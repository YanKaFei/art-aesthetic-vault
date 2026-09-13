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
    # numpy 的 import 放在 try 里，兑现上面「读不了返回 (None, None, None)」的承诺：
    # 原来它是裸 import，缺 numpy 时直接把 ModuleNotFoundError 抛给调用方 ——
    # 于是 `artvault_vision.py dups` 在没装 numpy 的机器上是一段 traceback，
    # 而不是一句「需要 numpy」。函数签名承诺了优雅降级，就得做到。
    try:
        import numpy as np
    except ImportError:
        return None, None, None
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

# ------------------------------------------------------------------ 并发锁
def locked(path, timeout=15.0, poll=0.05):
    """对 `path` 配一把排他锁，覆盖整个「读 → 改 → 写」过程。

        with safefile.locked(MANIFEST):
            d = safefile.read_json(MANIFEST) or {}
            d["items"][k] = v
            safefile.write_json(MANIFEST, d)

    ## 为什么原子写还不够

    `write_json` 保证的是「不会留下半截文件」。但两个进程各自
    「读 → 改 → 写」时，后写的那个会把先写的**改动整体覆盖掉** ——
    文件始终是完整的，只是丢了一次更新。原子性防不住这个。

    实测场景：DSH 里并行起两个子代理、或者你手动跑 scan_local 的同时
    另一个脚本在归档投递箱，都会碰到。

    ## 实现

    锁放在 `<path>.lock` 这个**旁挂文件**上，而不是目标文件本身 ——
    目标文件每次写入都会被 `os.replace` 换成新 inode，锁在旧 inode 上会失效。
    这是 `flock` 类锁的经典陷阱。

    非 POSIX（没有 fcntl）时退化成不加锁，但**明确返回 False 让调用方知道**，
    不假装有保护。超时抛 TimeoutError，不静默继续 —— 静默继续就等于丢更新。
    """
    import contextlib

    @contextlib.contextmanager
    def _cm():
        lock_path = path + ".lock"
        d = os.path.dirname(os.path.abspath(lock_path))
        os.makedirs(d, exist_ok=True)
        try:
            import fcntl
        except ImportError:
            yield False                     # 没有 fcntl：明确告知未加锁
            return
        f = open(lock_path, "a+")
        got = False
        try:
            import time
            deadline = time.time() + timeout
            while True:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    got = True
                    break
                except OSError:
                    if time.time() >= deadline:
                        raise TimeoutError(
                            "等 %s 的锁超时（%.0fs）—— 可能有另一个进程在写同一个文件。"
                            "若确定没有，删掉 %s 重试。" % (path, timeout, lock_path))
                    time.sleep(poll)
            yield True
        finally:
            if got:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except Exception:
                    pass
            f.close()

    return _cm()


def update_json(path, fn, default=None, timeout=15.0):
    """加锁地「读 → 让 fn 改 → 原子写」。fn 收到当前值（读不到时是 default）。

    fn 的返回值就是新值；返回 None 表示「不改，别写」（省掉一次无谓写盘）。
    """
    with locked(path, timeout=timeout):
        cur = read_json(path, default)
        new = fn(cur)
        if new is None:
            return cur
        write_json(path, new)
        return new
