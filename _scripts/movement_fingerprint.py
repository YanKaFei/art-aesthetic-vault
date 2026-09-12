#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
movement_fingerprint.py —— 用客观维度做「图像 → 流派」匹配。

## 它是怎么来的

T3 的 Vision 特征能做语义匹配，于是想试试「用可解释的客观维度会不会更好」——
毕竟明度、饱和、笔触、线条这些**正是艺术史划分流派的依据**。

**结论：不会。而且在三条路里它是最弱的 —— 最好的是 CLIP。**

同一留一法框架下（396 张、72 个有 ≥3 张图的流派、随机基准约 1.4%）：

| 做法 | 最近邻同流派 | Top-1 | Top-3 |
|---|---|---|---|
| **CLIP + 融合（零样本权重 0.15）** | — | **39.1%** | **61.4%** |
| CLIP 图像质心 | 33.1% | 37.6% | 59.8% |
| CLIP 零样本（图 vs 流派文字） | — | 21.5% | 36.6% |
| Vision featureprint（768 维） | 27.6% | 30.6% | 50.8% |
| T1 客观维度（31 维） | 13.4% | 13.2% | 25.3% |

可能的原因：T1 的 31 维里含大量与流派无关的信息（画面比例、对称性、
边缘密度更多受题材和构图支配），而 CLIP 是图文对比学习、Vision 是物体识别，
都比纯物理测量更贴近「这张图属于哪个流派」。

**但这个模块仍然留着**，因为它有一个另外两条路都给不了的东西：**可解释**。
它能说清「你这张图暗、低饱和、笔触碎，所以最像色调主义」，以及**哪里不像**。
CLIP 和 Vision 只给一个黑箱分数。

## 原理

    1. 用 image_analysis 的客观维度（明度/对比/色彩/和谐/构图/质感/线条）
       给每张图算一个数值向量
    2. 按流派把向量平均，得到该流派的「视觉指纹」（质心）
    3. 新图算完向量，找最近的质心

## 怎么知道它行不行

不靠感觉，跑留一法（leave-one-out）：

    取出某张图，把**它自己**从所属流派的质心里剔除，再问「最像哪个流派」，
    看答对没有。对 400+ 张全跑一遍，得到命中率。

**基准必须算对**（我自己在这里栽过）：随机基准不是 50%，而是
「随便挑另一张图恰好同流派」—— 本库 78 个流派、每流派约 5 张，所以约 1%。
用 50% 当基准会得出完全相反的结论。

`eval` 会同时跑 T1 和 Vision 两组特征、两种口径，差值由数据算出而不是写死。

用法
    python3 movement_fingerprint.py build          # 算全库维度并缓存
    python3 movement_fingerprint.py eval           # 留一法评估，与 Vision 对等对比
    python3 movement_fingerprint.py match <图>      # 给一张图找最像的流派（带解释）
"""

import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMAGES = os.path.join(VAULT, "99-附件", "images")
CACHE = os.path.join(HERE, "_data", "feature_cache.json")

sys.path.insert(0, HERE)
for _c in (os.path.join(HERE, "vendor", "libs"), os.path.expanduser("~/.artvault/deps"),
           os.environ.get("ARTVAULT_DEPS", "")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp")


# ------------------------------------------------------------ 特征向量
def vector(r):
    """把 analyze() 的结果拍平成一个数值向量。

    两个循环量（色相、线条主方向）必须转成 sin/cos 再放进去 ——
    直接放角度会出错：色相 350° 和 10° 只差 20°，数值上却差 340。
    线条方向是 180° 周期的，所以用 2θ。
    """
    if r.get("error"):
        return None
    lu, co, cl = r["luminance"], r["contrast"], r["color"]
    hm, cp, tx, ln = r["harmony"], r["composition"], r["texture"], r["lines"]

    hue = math.radians(hm.get("mean_hue") or 0)
    ang = math.radians((ln.get("dominant_angle") or 0) * 2)

    dist = ln.get("distribution") or [0] * 6
    dtot = float(sum(dist)) or 1.0

    v = [
        lu["mean"], lu["std"], lu["dynamic_range"],
        lu["shadow_clip_pct"], lu["highlight_clip_pct"],
        co["rms"], co["michelson"],
        cl["warm_score"], cl["saturation"],
        hm["concentration"], hm["effective_hues"], hm["colored_ratio"],
        math.sin(hue), math.cos(hue),
        cp["thirds_vs_full"], cp["symmetry_h"], cp["symmetry_v"], cp["center_weight"],
        tx["edge_density"], tx["local_variance"], tx["entropy"],
        ln["strong_edge_pct"],
        math.sin(ang), math.cos(ang),
        r.get("ratio") or 1.0,
    ]
    v += [d / dtot for d in dist]           # 6 个方向分布，已归一化
    return v


FEATURE_NAMES = [
    "明度均值", "明度标准差", "动态范围", "暗部溢出", "高光溢出",
    "RMS对比", "Michelson对比",
    "色温", "饱和度",
    "色相集中度", "有效色相数", "有色像素比",
    "色相sin", "色相cos",
    "三分法能量比", "水平对称", "垂直对称", "中心权重",
    "边缘密度", "局部方差", "熵",
    "强边缘占比",
    "方向sin", "方向cos",
    "画面比例",
] + ["方向分布%d" % i for i in range(6)]


def slug_of(relpath):
    parts = relpath.split("/")
    return parts[2] if len(parts) >= 4 and parts[0] == "99-附件" else "?"


def iter_images():
    for root, _d, files in os.walk(IMAGES):
        for fn in sorted(files):
            if fn.lower().endswith(EXTS):
                yield os.path.relpath(os.path.join(root, fn), VAULT).replace(os.sep, "/")


# ------------------------------------------------------------ 缓存
def load_cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(c, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)


def build(verbose=True, force=False):
    """算全库的维度向量并缓存。已算过的复用，只补新增的。"""
    import image_analysis as A
    if A.Image is None:
        if verbose:
            print("需要 Pillow")
        return None
    files = list(iter_images())
    cache = {} if force else load_cache()
    todo = [f for f in files if f not in cache]
    if verbose:
        print("库中图片 %d 张；已缓存 %d 张，需计算 %d 张"
              % (len(files), len(cache), len(todo)))
    t0 = time.time()
    for i, rel in enumerate(todo, 1):
        r = A.analyze(os.path.join(VAULT, rel))
        v = vector(r)
        if v:
            cache[rel] = v
        if verbose and (i % 50 == 0 or i == len(todo)):
            el = time.time() - t0
            print("  %d/%d  (%.0fs，预计还需 %.0fs)"
                  % (i, len(todo), el, el / i * (len(todo) - i)))
    # 清掉已删除的图
    live = set(files)
    dropped = [k for k in cache if k not in live]
    for k in dropped:
        del cache[k]
    save_cache(cache)
    if verbose:
        print("✓ 缓存 %d 张%s → %s"
              % (len(cache), ("，清理 %d 张" % len(dropped)) if dropped else "",
                 os.path.relpath(CACHE, VAULT)))
    return cache


# ------------------------------------------------------------ 质心与评估
def _stats(vectors):
    """按维度求均值与标准差，用于 z 归一化（各维度量纲差很大）。"""
    n = len(vectors[0])
    mean = [0.0] * n
    for v in vectors:
        for i, x in enumerate(v):
            mean[i] += x
    mean = [m / len(vectors) for m in mean]
    var = [0.0] * n
    for v in vectors:
        for i, x in enumerate(v):
            var[i] += (x - mean[i]) ** 2
    std = [math.sqrt(x / len(vectors)) or 1e-6 for x in var]
    return mean, std


def _norm(v, mean, std):
    return [(x - mean[i]) / std[i] for i, x in enumerate(v)]


def _dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def centroids(cache):
    """按流派求质心（未归一化的原始和，便于做留一法剔除）。"""
    groups = {}
    for rel, v in cache.items():
        groups.setdefault(slug_of(rel), []).append((rel, v))
    return groups


# 不是流派的目录：pinterest/ 是用户的投递箱（混杂参考图），
# 拿它参与评估会同时污染准确率和混淆榜 —— 它本来就不属于任何流派。
NOT_MOVEMENTS = {"pinterest"}


def evaluate(cache, exclude=NOT_MOVEMENTS, min_samples=3, verbose=True):
    """留一法：取出某张图，把它自己从所属流派的质心里剔除，再问最像哪个流派。

    min_samples 控制哪些流派能当候选：1 张图的流派质心就是那一张图本身，
    噪声极大，会把结果带偏（实测色调主义的花园被单图流派 bauhaus 抢走）。
    """
    cache = {k: v for k, v in cache.items() if slug_of(k) not in exclude}
    # 先按 min_samples 过滤候选流派，再参与评估
    sizes = {}
    for rel in cache:
        sizes[slug_of(rel)] = sizes.get(slug_of(rel), 0) + 1
    cache = {k: v for k, v in cache.items() if sizes[slug_of(k)] >= min_samples}
    groups = centroids(cache)
    all_v = [v for _r, v in cache.items()]
    if not all_v:
        return None
    mean, std = _stats(all_v)
    norm = {rel: _norm(v, mean, std) for rel, v in cache.items()}

    # 每个流派的归一化向量和
    sums = {}
    for s, items in groups.items():
        acc = [0.0] * len(all_v[0])
        for _rel, v in items:
            nv = norm[_rel]
            for i, x in enumerate(nv):
                acc[i] += x
        sums[s] = (acc, len(items))

    ok = 0
    tot = 0
    top3 = 0
    confusion = {}
    for s, items in groups.items():
        if len(items) < 2:
            continue
        for rel, _v in items:
            if len(items) < 2:
                continue
            q = norm[rel]
            scored = []
            for s2, (acc, n) in sums.items():
                cnt = n - 1 if s2 == s else n
                if cnt <= 0:
                    continue
                cen = [(acc[i] - (q[i] if s2 == s else 0.0)) / cnt
                       for i in range(len(q))]
                scored.append((_dist2(q, cen), s2))
            scored.sort()
            tot += 1
            if scored and scored[0][1] == s:
                ok += 1
            if any(s2 == s for _d, s2 in scored[:3]):
                top3 += 1
            elif scored:
                confusion[(s, scored[0][1])] = confusion.get((s, scored[0][1]), 0) + 1

    if not tot:
        if verbose:
            print("可用样本不足（需要 ≥2 张图的流派）")
        return None
    cands = [s for s, i in groups.items() if len(i) >= min_samples]
    return {"n": tot, "top1": ok / float(tot), "top3": top3 / float(tot),
            "chance": 1.0 / max(1, len(cands)),
            "confusion": sorted(confusion.items(), key=lambda kv: -kv[1])[:10],
            "movements": len(cands), "min_samples": min_samples}


def describe_match(cache, target_vec, topn=5, min_samples=3):
    """给一张新图找最像的流派，并给出**为什么**（哪些维度贡献最大）。

    min_samples 默认 3：1 张图的流派质心就是那张图本身，会把结果带偏
    （实测把色调主义的花园判给了只有一个样本的 bauhaus）。
    """
    cache = {k: v for k, v in cache.items() if slug_of(k) not in NOT_MOVEMENTS}
    sizes = {}
    for rel in cache:
        sizes[slug_of(rel)] = sizes.get(slug_of(rel), 0) + 1
    cache = {k: v for k, v in cache.items() if sizes[slug_of(k)] >= min_samples}
    if not cache:
        return []
    groups = centroids(cache)
    mean, std = _stats([v for _r, v in cache.items()])
    q = _norm(target_vec, mean, std)
    scored = []
    for s, items in groups.items():
        acc = [0.0] * len(q)
        for _rel, v in items:
            nv = _norm(v, mean, std)
            for i, x in enumerate(nv):
                acc[i] += x
        cen = [a / len(items) for a in acc]
        d = _dist2(q, cen)
        # 逐维贡献，用于解释
        contrib = sorted(((q[i] - cen[i]) ** 2, FEATURE_NAMES[i]) for i in range(len(q)))
        scored.append((d, s, len(items), contrib[-3:]))
    scored.sort()
    return scored[:topn]


# ------------------------------------------------------------ CLI
def evaluate_nn(cache, exclude=NOT_MOVEMENTS):
    """最近邻口径：最近的那张图是否同流派。

    这个口径是为了和 T3 的 Vision 特征**对等比较** —— Vision 那组数字就是
    按「最近邻是否同流派」算的。

    **基准要算对**（这里踩过一个大坑）：随机基准不是 50%，而是
    「随便挑另一张图，它恰好属于同一流派」的概率 —— 本库 78 个流派、
    每流派约 5 张图，所以约 1%。曾经误把 50% 当基准，得出「Vision 只有
    44%，近乎随机」的相反结论；实际上 44% 是随机水平的 30 多倍。
    """
    cache = {k: v for k, v in cache.items() if slug_of(k) not in exclude}
    all_v = [v for _r, v in cache.items()]
    if len(all_v) < 2:
        return None
    mean, std = _stats(all_v)
    norm = {rel: _norm(v, mean, std) for rel, v in cache.items()}
    items = sorted(norm.items())

    # 每个流派有多少张图，用于算随机基准
    sizes = {}
    for rel, _v in items:
        sizes[slug_of(rel)] = sizes.get(slug_of(rel), 0) + 1

    ok = tot = 0
    chance_acc = 0.0
    for i, (ri, vi) in enumerate(items):
        best = None
        for j, (rj, vj) in enumerate(items):
            if i == j:
                continue
            d = _dist2(vi, vj)
            if best is None or d < best[0]:
                best = (d, rj)
        if not best:
            continue
        tot += 1
        chance_acc += (sizes.get(slug_of(ri), 1) - 1) / float(len(items) - 1)
        if slug_of(best[1]) == slug_of(ri):
            ok += 1
    if not tot:
        return None
    hit = ok / float(tot)
    chance = chance_acc / tot
    return {"n": tot, "same_movement": hit, "chance": chance,
            "lift": (hit / chance) if chance else 0.0}


def vision_cache():
    """把 T3 的 Vision 特征索引读成同一格式，用于对等比较。"""
    p = os.path.join(HERE, "_data", "vision_index.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
        return d.get("vectors") or None
    except Exception:
        return None


def _need_cache(verbose=True):
    c = load_cache()
    if not c:
        if verbose:
            print("还没有缓存。先跑：python3 movement_fingerprint.py build")
        return None
    return c


def _report(name, cache):
    """对一个特征集跑两种口径，返回结果字典。"""
    print("── %s ──" % name)
    if not cache:
        print("  （无数据）")
        return None
    loo = evaluate(cache)
    nn = evaluate_nn(cache)
    if not loo or not nn:
        print("  （样本不足）")
        return None
    print("  样本 %d 张 / %d 个流派有 ≥%d 张图（已排除 pinterest 投递箱）"
          % (loo["n"], loo["movements"], loo.get("min_samples", 2)))
    print("  ［口径 A］质心分类（%d 选 1）  随机 %5.1f%%   Top-1 %5.1f%% (×%.0f)   Top-3 %5.1f%%"
          % (loo["movements"], loo["chance"] * 100, loo["top1"] * 100,
             loo["top1"] / loo["chance"] if loo["chance"] else 0, loo["top3"] * 100))
    print("  ［口径 B］最近邻是否同流派      随机 %5.1f%%   命中 %5.1f%% (×%.0f)"
          % (nn["chance"] * 100, nn["same_movement"] * 100, nn["lift"]))
    return {"loo": loo, "nn": nn}


def cmd_eval(a):
    t1 = load_cache()
    vis = vision_cache()

    r1 = _report("T1 客观维度（本模块，31 维）", t1)
    r2 = None
    if vis:
        r2 = _report("T3 Vision 特征（768 维，macOS）", vis)
    else:
        print("── T3 Vision 特征 ──")
        print("  （没有索引；跑 python3 artvault_vision.py build）")
    print()

    if r1 and r2:
        # 结论**由数据算出**，不写死。这里曾经写过一段硬编码的叙述，
        # 断言「T1 更好」，而实测两个口径都是 Vision 反超 —— 代码照着一个
        # 错误假设打印了与数据相反的结论。叙述必须从数字来。
        print("结论（同一口径下直接对比，差值为正表示 T1 更好）：")
        for label, key, fmt in (("口径 A（Top-1）", "top1", "%.1f 个百分点"),
                                ("口径 B（最近邻同流派）", "same_movement", "%.1f 个百分点")):
            d = (r1["loo" if key == "top1" else "nn"][key]
                 - r2["loo" if key == "top1" else "nn"][key]) * 100
            print("  %-24s T1 − Vision = %s" % (label, fmt % d))
        wins = sum([
            r1["loo"]["top1"] > r2["loo"]["top1"],
            r1["nn"]["same_movement"] > r2["nn"]["same_movement"]])
        print()
        if wins == 2:
            print("  → 两个口径上 T1 客观维度都更好。")
        elif wins == 0:
            print("  → 两个口径上 Vision 都更好。**这与「客观维度更懂风格」的直觉相反**，")
            print("    可能的原因：T1 的 31 维里含大量与流派无关的信息（画面比例、")
            print("    对称性、边缘密度受构图和题材支配），而 Vision 的 768 维虽然为物体")
            print("    识别训练，却隐含编码了笔触、材质、色调这些风格线索。")
            print("    另一个可能：78 个流派里每个只有约 5 张样本，31 维质心估计比")
            print("    768 维更容易被离群图带偏。要下确定结论需要更大的样本。")
        else:
            print("  → 两个口径结论不一致，说明两者的排序能力各有偏重，")
            print("    不能简单说谁更好；建议按具体用途选。")
        print()
        print("  **但两者都远超随机**：随机基准约 1%（78 个流派、每流派约 5 张），")
        print("  所以即使较弱的一方也是随机水平的十倍以上 —— 都含有真实信号。")
    elif r1:
        print("（未与 Vision 对比：缺索引）")

    if r1 and r1["loo"]["confusion"]:
        print()
        print("T1 最常见的混淆（真实流派 → 被判成）：")
        for (x, y), n in r1["loo"]["confusion"][:8]:
            print("    %-26s → %-26s %d 次" % (x, y, n))
    return 0


def main():
    ap = argparse.ArgumentParser(description="用客观维度做图像→流派匹配")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("build", help="算全库维度并缓存")
    p.add_argument("--force", action="store_true")
    sub.add_parser("eval", help="留一法评估；同时跑 T3 Vision 做对等对比")
    p = sub.add_parser("match", help="给一张图找最像的流派")
    p.add_argument("target")
    p.add_argument("-n", type=int, default=5)
    a = ap.parse_args()

    if a.cmd == "build":
        return 0 if build(force=a.force) else 1

    if a.cmd == "eval":
        return cmd_eval(a)

    if a.cmd == "match":
        c = _need_cache()
        if not c:
            return 1
        import image_analysis as A
        r = A.analyze(a.target)
        v = vector(r)
        if not v:
            print("分析失败：%s" % r.get("error"))
            return 1
        print("查询：%s" % os.path.basename(a.target))
        print("%-24s %8s %6s   %s" % ("最像的流派", "距离", "样本", "主要差异维度"))
        print("-" * 88)
        for d, s, n, contrib in describe_match(c, v, a.n):
            why = "、".join("%s" % name for _c2, name in reversed(contrib))
            print("%-24s %8.2f %6d   %s" % (s, d, n, why))
        print()
        print("「主要差异维度」是这张图和该流派指纹差得最多的三项 —— 它同时告诉你")
        print("为什么像、以及哪里不像，不是一个黑箱分数。")
        print()
        print("⚠ 准确率要给准：留一法实测 Top-1 只有 13.2%（随机基准 1.4%，即 ×9），")
        print("  **比 macOS Vision 特征的 30.6% 差**。这是弱参考 ——")
        print("  它的价值在可解释，不在准。判风格请以流派卡为准。")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
