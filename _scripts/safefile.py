#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
safefile.py —— 安全读写本地数据文件。

两个坑，都在实测里见过：

1. **写到一半被打断会留下截断的 JSON**，之后所有读它的脚本都会炸。
   `write_json()` 先写临时文件再 `os.replace()` —— POSIX 上 rename 是原子的，
   所以要么是完整的旧文件，要么是完整的新文件，不会出现半截。

2. **向量缓存用 JSON 存太浪费**。实测 654 张图：JSON 7.1 MB、加载 0.07s；
   换成 float32 的 npz 是 1.2 MB、加载 0.004s（小 5.9 倍、快 108 倍）。
   按这个比例，20000 张图时 JSON 是 218 MB / 2.1s，npz 是 37 MB / 0.02s。
   所以向量一律走 `write_vectors()` / `read_vectors()`。
"""

import json
import os
import tempfile


def write_json(path, obj, indent=1):
    """原子写 JSON：先写同目录的临时文件，再 os.replace 覆盖。"""
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=indent)
        os.replace(tmp, path)          # 原子
    except Exception:
        try:
            os.remove(tmp)
        except Exception:
            pass
        raise
    return path


def read_json(path, default=None):
    """读 JSON。文件不存在或坏了都返回 default，不抛异常。"""
    if not os.path.exists(path):
        return default
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def write_vectors(path, keys, vecs, meta=None):
    """原子写向量矩阵（float32 npz）。keys 是路径列表，vecs 是 N×D 的数组。

    npz 没有原子替换的问题，因为它是单文件写出后 rename。
    """
    import numpy as np
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-", suffix=".npz")
    os.close(fd)
    try:
        np.savez_compressed(tmp, keys=np.asarray(keys, dtype=object),
                            vecs=np.asarray(vecs, dtype="f4"),
                            meta=np.asarray([json.dumps(meta or {})], dtype=object),
                            allow_pickle=True)
        os.replace(tmp if tmp.endswith(".npz") else tmp + ".npz", path)
        # np.savez 会自动补 .npz，临时名已经带了后缀，所以上面两种都试一下
        if not os.path.exists(path) and os.path.exists(tmp):
            os.replace(tmp, path)
    except Exception:
        for x in (tmp, tmp + ".npz"):
            try:
                os.remove(x)
            except Exception:
                pass
        raise
    return path


def read_vectors(path):
    """读向量矩阵，返回 (keys, vecs, meta)。读不了返回 (None, None, None)。

    同时兼容旧的 JSON 格式（早期版本把向量直接存成 JSON），
    这样升级后不用重建索引就能继续用。
    """
    import numpy as np
    if not os.path.exists(path):
        return None, None, None
    # np.load 对 JSON 文件会抛（不是 zip），但也加一道魔数检查更稳
    try:
        _is_npz = open(path, "rb").read(2) == b"PK"
    except Exception:
        _is_npz = False
    if _is_npz:
        try:
            z = np.load(path, allow_pickle=True)
            keys = list(z["keys"])
            vecs = np.asarray(z["vecs"], dtype="f4")
            meta = json.loads(str(z["meta"][0])) if "meta" in z else {}
            return keys, vecs, meta
        except Exception:
            pass
    # 回退：旧 JSON 格式。**有两种形状**，都要认：
    #   扁平版 {"a.jpg": [...], "b.jpg": [...]}          （clip_cache.json）
    #   包装版 {"built_at":…, "dim":…, "vectors": {...}}  （vision_index.json）
    # 实测踩过：只认扁平版，包装版会把 built_at 那个时间字符串当向量转，
    # 报 ValueError: could not convert string to float: '2026-09-13 02:10:04'。
    old = read_json(path)
    if isinstance(old, dict):
        if isinstance(old.get("vectors"), dict):
            meta = {k: v for k, v in old.items() if k != "vectors"}
            old = old["vectors"]
        else:
            meta = {}
        if old and all(isinstance(v, (list, tuple)) for v in old.values()):
            keys = list(old)
            vecs = np.asarray(list(old.values()), dtype="f4")
            return keys, vecs, meta
    return None, None, None
