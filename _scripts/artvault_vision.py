#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
artvault_vision.py —— 图像语义相似度检索（T3）。

用 macOS 自带 Vision 框架算 768 维特征向量，回答两类问题：

    以图搜图   这张参考图最像库里哪些图
    相近流派   浮世绘在**画面上**最接近哪些流派（不是靠文字，是靠像素）
    近重复     两张图是不是同一张（换个来源重抓时会遇到）

和 `image_analysis.py` 的分工：
    那个测的是**可解释的客观维度**（明度/对比/色彩/构图…），每一项都能
    翻译成提示词，向量本身人看得懂。
    这个测的是**不可解释的语义相似度**，只知道「像/不像」，不知道为什么。

两者互补：拆解用前者，找参考图用后者。

为什么用 Vision 而不是 CLIP：CLIP 要 PyTorch（约 2.5GB）且模型要联网下，
实测这台机器上 PyTorch / onnxruntime / tensorflow **全部装不上**（PyPI 读超时），
HuggingFace 也被挡（http=000）。Vision 是系统自带、完全离线。

为什么用 Objective-C 而不是 Swift：本机 `xcrun swiftc` 坏了
（`redefinition of module 'SwiftBridging'`），clang + Objective-C 走同一套框架。

用法：
    python3 artvault_vision.py features <图>          # 单张特征向量（768 维）
    python3 artvault_vision.py build [--force]        # 建/更新索引
    python3 artvault_vision.py query <图> [-n 10]     # 以图搜图
    python3 artvault_vision.py similar <流派> [-n 10]  # 画面最接近的流派
    python3 artvault_vision.py dups [--thresh 0.3]    # 近重复检测

非 macOS 或编译失败时**所有功能优雅降级**：CLI 给出明确原因，不抛栈。
索引是生成物，已 gitignore（`_scripts/_data/vision_index.json`）。
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
VISION_DIR = os.path.join(HERE, "vision")
SOURCE = os.path.join(VISION_DIR, "vision_feat.m")
BINARY = os.path.join(VISION_DIR, "vision_feat")
IMAGES = os.path.join(VAULT, "99-附件", "images")
INDEX = os.path.join(HERE, "_data", "vision_index.json")

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp")
EXPECTED_DIM = 768


# ------------------------------------------------------------ 可用性
def unavailable_reason():
    """返回不可用的原因；可用则返回 None。"""
    if platform.system() != "Darwin":
        return "图像语义检索依赖 macOS 自带的 Vision 框架，当前系统是 %s" % platform.system()
    if not os.path.exists(SOURCE):
        return "缺少源码 %s" % SOURCE
    return None


def ensure_binary(verbose=False):
    """按需编译 .m。二进制架构相关，不入库；.m 更新了会自动重编。"""
    reason = unavailable_reason()
    if reason:
        return None
    if os.path.exists(BINARY):
        if os.path.getmtime(BINARY) >= os.path.getmtime(SOURCE):
            return BINARY
    cmd = ["clang", "-O2", "-fobjc-arc", "-framework", "Foundation",
           "-framework", "AppKit", "-framework", "Vision", SOURCE, "-o", BINARY]
    if verbose:
        print("编译 Vision 特征提取器…")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except Exception as e:
        if verbose:
            print("  编译失败: %s" % e)
        return None
    if p.returncode != 0 or not os.path.exists(BINARY):
        if verbose:
            print("  编译失败:\n%s" % (p.stderr or "")[:500])
        return None
    if verbose:
        print("  ✓ %s" % BINARY)
    return BINARY


# ------------------------------------------------------------ 特征提取
def _parse(text):
    """解析 .m 的输出。返回 {path: [float,...]} 和错误列表。"""
    out, errs, cur, dim, vec = {}, [], None, None, None
    for line in text.split("\n"):
        if line.startswith("=== "):
            if cur and vec is not None:
                out[cur] = vec
            cur, dim, vec = line[4:].strip(), None, None
        elif line.startswith("DIM "):
            try:
                dim = int(line[4:])
            except ValueError:
                dim = None
        elif line.startswith("VEC"):
            vec = [float(x) for x in line[3:].split()]
        elif line.startswith("ERROR "):
            errs.append(line[6:].strip())
    if cur and vec is not None:
        out[cur] = vec
    return out, errs


def features_batch(paths, verbose=False):
    """一次进程算多张图的特征。372 张逐个起进程约 19 秒，批量约 8 秒。"""
    b = ensure_binary(verbose=verbose)
    if not b or not paths:
        return {}, []
    stdin = "\n".join(paths) + "\n"
    try:
        p = subprocess.run([b, "-"], input=stdin, capture_output=True,
                           text=True, timeout=60 * max(5, len(paths) // 20))
    except Exception as e:
        return {}, ["批量提取失败: %s" % e]
    return _parse(p.stdout)


def features(path, verbose=False):
    """单张图的 768 维特征向量。不可用时返回 None。"""
    r, _ = features_batch([path], verbose=verbose)
    return r.get(path)


# ------------------------------------------------------------ 距离
def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def _dist_np(a, b):
    import numpy as np
    return float(np.linalg.norm(np.asarray(a, dtype="f4") - np.asarray(b, dtype="f4")))


_NUMPY = None


def _have_numpy():
    """numpy 可用性。缓存结果 —— 这个函数会改 sys.path 并尝试 import，
    放在双层循环里每对比一次跑一遍是纯浪费（cmd_similar 要跑几万次）。"""
    global _NUMPY
    if _NUMPY is None:
        for c in (os.path.join(HERE, "vendor", "libs"),
                  os.environ.get("ARTVAULT_DEPS", ""),
                  os.path.expanduser("~/.artvault/deps")):
            if c and os.path.isdir(c) and c not in sys.path:
                sys.path.insert(0, c)
        try:
            import numpy  # noqa: F401
            _NUMPY = True
        except Exception:
            _NUMPY = False
    return _NUMPY


# ------------------------------------------------------------ 索引
def iter_images():
    """遍历库里所有图，返回 vault 相对路径（用 / 分隔，跨平台且可入库）。"""
    for root, _dirs, files in os.walk(IMAGES):
        for fn in sorted(files):
            if fn.lower().endswith(EXTS):
                yield os.path.relpath(os.path.join(root, fn), VAULT).replace(os.sep, "/")


def load_index():
    if not os.path.exists(INDEX):
        return None
    try:
        return json.load(open(INDEX, encoding="utf-8"))
    except Exception:
        return None


def build_index(force=False, verbose=True):
    """建/更新索引。已算过的图直接复用，只补新增的，`--force` 才全量重算。"""
    reason = unavailable_reason()
    if reason:
        if verbose:
            print("无法建立索引：%s" % reason)
        return None

    files = list(iter_images())
    if not files:
        if verbose:
            print("库里没找到图（%s）" % IMAGES)
        return None

    old = (load_index() or {}) if not force else {}
    known = old.get("vectors", {}) if isinstance(old, dict) else {}
    todo = [f for f in files if f not in known]

    if verbose:
        print("库中图片 %d 张；已有特征 %d 张，需要计算 %d 张"
              % (len(files), len(known), len(todo)))

    vecs = dict(known)
    if todo:
        abs_paths = [os.path.join(VAULT, f) for f in todo]
        got, errs = features_batch(abs_paths, verbose=verbose)
        # .m 输出的是绝对路径，换回 vault 相对路径
        for ap, v in got.items():
            rel = os.path.relpath(ap, VAULT).replace(os.sep, "/")
            vecs[rel] = v
        if errs and verbose:
            print("  %d 张读取失败（前面几条）：" % len(errs))
            for e in errs[:3]:
                print("    %s" % e[:100])

    dims = set(len(v) for v in vecs.values())
    if dims and dims != {EXPECTED_DIM}:
        if verbose:
            print("  ⚠ 特征维度异常: %s（预期 %d）" % (sorted(dims), EXPECTED_DIM))

    # 清掉索引里已经不存在的图
    live = set(files)
    dropped = [k for k in vecs if k not in live]
    for k in dropped:
        del vecs[k]

    os.makedirs(os.path.dirname(INDEX), exist_ok=True)
    json.dump({"built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "dim": EXPECTED_DIM, "count": len(vecs), "vectors": vecs},
              open(INDEX, "w", encoding="utf-8"), ensure_ascii=False)
    if verbose:
        print("✓ 索引已写入 %s（%d 张%s）"
              % (os.path.relpath(INDEX, VAULT), len(vecs),
                 "，清理了 %d 张已删除的图" % len(dropped) if dropped else ""))
    return vecs


def slug_of(relpath):
    """从图库相对路径取出流派 slug：99-附件/images/<slug>/<file>"""
    parts = relpath.split("/")
    return parts[2] if len(parts) >= 4 and parts[0] == "99-附件" else "?"


def require_index(verbose=True):
    idx = load_index()
    if not idx or not idx.get("vectors"):
        if verbose:
            print("还没有索引。先跑：python3 artvault_vision.py build")
        return None
    return idx


# ------------------------------------------------------------ 检索
def rank(query_vec, vectors, topn=10, exclude=None):
    """按 L2 距离升序返回 [(relpath, distance)]。距离越小越像。"""
    use_np = _have_numpy()
    scored = []
    for rel, v in vectors.items():
        if exclude and rel == exclude:
            continue
        if len(v) != len(query_vec):
            continue
        try:
            d = _dist_np(query_vec, v) if use_np else _dist(query_vec, v)
        except Exception:
            d = _dist(query_vec, v)
        scored.append((rel, d))
    scored.sort(key=lambda x: x[1])
    return scored[:topn]


def interpret(d):
    """距离 → 可读判读。阈值由本库实测分布标定（见 vision/README.md）。

    **一个必须记住的坑**：曾经把「最近邻同流派的命中率」和 50% 比，得出
    「只有 44%，近乎随机」的结论 —— 基准就错了。随机的正确基准是
    「随便挑另一张图恰好同流派」；本库 78 个流派、每流派约 5 张，所以约 1%。
    而且那个 44% 还是被 pinterest 投递箱（212 张混杂图互相成为最近邻）抬高的。

    按正确口径重算（400+ 张、78 个流派、排除 pinterest）：

        最近邻同流派   27.6%   随机 1.1%   → 随机的 25 倍
        78 选 1 Top-1  29.7%   随机 1.3%   → 随机的 23 倍

    所以这个特征**含有真实信号**，不是噪声。但 Top-1 约 30% 也意味着
    十次里错七次 —— 它是**建议**工具，不是分类器。

    阈值按「是不是同一张 / 同一构图」标定（这部分一直可靠）：

        <0.10  几乎同一张（真重复，实测 17 对全是这样找出来的）
        <0.35  高度相似（同题材、同构图）
        <0.60  明显相似
        <0.85  有一定共同点
        其余   不构成相似
    """
    if d < 0.10:
        return "几乎同一张（重复图）"
    if d < 0.35:
        return "高度相似（同题材/同构图）"
    if d < 0.60:
        return "明显相似"
    if d < 0.85:
        return "有一定共同点"
    return "不构成相似"


def cmd_query(target, topn, show_all=False):
    idx = require_index()
    if not idx:
        return 1
    vectors = idx["vectors"]
    rel_target = None
    try:
        rel_target = os.path.relpath(os.path.abspath(target), VAULT).replace(os.sep, "/")
    except Exception:
        pass
    qv = vectors.get(rel_target)
    if qv is None:
        qv = features(target, verbose=True)
        if qv is None:
            print("提取特征失败（文件不存在，或 Vision 不可用）")
            return 1
    res = rank(qv, vectors, topn=topn + (1 if rel_target in vectors else 0),
               exclude=rel_target if not show_all else None)
    print("查询：%s" % (rel_target or target))
    print("%-52s %8s  %s" % ("最相似的图", "距离", "判读"))
    print("-" * 92)
    for rel, d in res[:topn]:
        print("%-52s %8.3f  %s" % (rel[:52], d, interpret(d)))
    return 0


def cmd_similar(slug, topn):
    """某个流派在**画面上**最接近的其他流派。

    不是靠文字标签，是靠像素 —— 所以它可能给出文字上看不出来的关联
    （比如两个从没被归到一类的流派其实色调和构图同源）。
    """
    idx = require_index()
    if not idx:
        return 1
    vectors = idx["vectors"]
    mine = {k: v for k, v in vectors.items() if slug_of(k) == slug}
    if not mine:
        slugs = sorted(set(slug_of(k) for k in vectors))
        print("库里没有流派 %r。可用流派 %d 个，例如：%s"
              % (slug, len(slugs), ", ".join(slugs[:8])))
        return 1

    # 对每个其他流派，取「与我方任一图最接近」的那张作为该流派的代表分
    use_np = _have_numpy()          # 循环外取一次，别在几万次对比里反复探测
    best = {}
    for rel_q, vq in mine.items():
        for rel_o, vo in vectors.items():
            s = slug_of(rel_o)
            if s == slug or len(vo) != len(vq):
                continue
            d = _dist_np(vq, vo) if use_np else _dist(vq, vo)
            if s not in best or d < best[s][0]:
                best[s] = (d, rel_o)

    ranked = sorted(best.items(), key=lambda kv: kv[1][0])[:topn]
    print("「%s」在**画面内容**上最接近的流派（%d 张图参与对比）" % (slug, len(mine)))
    print("%-22s %8s  %-40s %s" % ("流派", "最近距离", "最像的那张图", "判读"))
    print("-" * 100)
    for s, (d, rel) in ranked:
        print("%-22s %8.3f  %-40s %s" % (s[:22], d, rel.split("/")[-1][:40], interpret(d)))
    print()
    print("· 这个排序是**建议**不是结论：实测最近邻同流派的命中率 27.6%，")
    print("  随机基准 1.1% —— 是随机的 25 倍，含真实信号；但 Top-1 也只有约三成，")
    print("  十次里错七次。要更确定的风格关联，配合 `artvault.py related` 一起看。")
    return 0


def cmd_dups(thresh):
    idx = require_index()
    if not idx:
        return 1
    vectors = idx["vectors"]
    items = sorted(vectors.items())
    pairs = []
    use_np = _have_numpy()
    for i in range(len(items)):
        ri, vi = items[i]
        for j in range(i + 1, len(items)):
            rj, vj = items[j]
            if len(vi) != len(vj):
                continue
            d = _dist_np(vi, vj) if use_np else _dist(vi, vj)
            if d < thresh:
                pairs.append((d, ri, rj))
    pairs.sort()
    if not pairs:
        print("阈值 %.2f 下没有发现近重复（共比对 %d 张）" % (thresh, len(items)))
        return 0
    print("阈值 %.2f 下的近重复（共比对 %d 张，发现 %d 对）" % (thresh, len(items), len(pairs)))
    print("%8s  %s" % ("距离", "图片对"))
    print("-" * 96)
    for d, a, b in pairs[:40]:
        cross = "" if slug_of(a) == slug_of(b) else "   ← 跨流派！"
        print("%8.3f  %s\n         %s%s" % (d, a, b, cross))
    if len(pairs) > 40:
        print("… 另有 %d 对未显示" % (len(pairs) - 40))
    return 0


def main():
    ap = argparse.ArgumentParser(description="图像语义相似度检索（macOS Vision）")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("features", help="单张图的 768 维特征")
    p.add_argument("target")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("build", help="建/更新索引")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("query", help="以图搜图")
    p.add_argument("target")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--all", action="store_true", help="结果里也包含查询图自己")

    p = sub.add_parser("similar", help="画面最接近的流派")
    p.add_argument("slug")
    p.add_argument("-n", type=int, default=10)

    p = sub.add_parser("dups", help="近重复检测")
    p.add_argument("--thresh", type=float, default=0.3)

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return 0

    reason = unavailable_reason()
    if reason:
        print("✗ %s" % reason)
        print("  这个功能是可选增强：库本身的查询、拆解、构建都不依赖它。")
        return 3

    if a.cmd == "features":
        v = features(a.target, verbose=True)
        if v is None:
            print("提取失败"); return 1
        if a.json:
            print(json.dumps({"path": a.target, "dim": len(v), "vector": v}))
        else:
            print("维度 %d" % len(v))
            print("前 12 维：%s" % " ".join("%.5f" % x for x in v[:12]))
        return 0
    if a.cmd == "build":
        return 0 if build_index(force=a.force) else 1
    if a.cmd == "query":
        return cmd_query(a.target, a.n, show_all=a.all)
    if a.cmd == "similar":
        return cmd_similar(a.slug, a.n)
    if a.cmd == "dups":
        return cmd_dups(a.thresh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
