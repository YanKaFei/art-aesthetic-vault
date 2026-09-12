#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clip_match.py —— 用 CLIP 做「图像 → 流派」匹配（零样本为主）。

## 这是目前最好的一条路

同一个留一法框架下的实测（396 张、72 个有 ≥3 张图的流派、
排除 pinterest 投递箱，随机基准约 1.4%）：

| 做法 | 最近邻同流派 | Top-1 | Top-3 |
|---|---|---|---|
| **CLIP + 融合（零样本权重 0.15）** | — | **39.1%** | **61.4%** |
| CLIP 图像质心 | 33.1% | 37.6% | 59.8% |
| CLIP 零样本（图 vs 流派文字） | — | 21.5% | 36.6% |
| Vision featureprint（768 维） | 27.6% | 30.6% | 50.8% |
| T1 客观维度（31 维） | 13.4% | 13.2% | 25.3% |

CLIP 是**图文对比学习**出来的，训练目标就是「让描述和图像对上」，
所以它比「认物体的」Vision featureprint 和「只测亮度的」T1 客观维度都更贴近这件事：
Top-1 比 Vision 高 8.5 个百分点，比 T1 高 26 个百分点。

（注意 Vision 那 27.6%/30.6% 是**修正后**的数字。曾有一版把它的命中率和 50%
比、说成「近乎随机」，那是基准错了 —— 随机的正确基准是「随便挑另一张图
恰好同流派」，本库约 1%，所以 30.6% 其实是随机水平的二十多倍。）

## 零样本：不需要任何参考图

CLIP 有一个前两条路都没有的能力 —— **文本和图像在同一个向量空间里**。
所以可以直接拿流派卡的英文描述当类别，用文字去匹配图像：

    1. 每个流派的 prompt.style 等字段拼成几句英文描述
    2. 用 CLIP 文本塔编码成 512 维
    3. 图像的 512 维直接和它们点积，取最大

好处是这个库**141 个流派全都有英文 prompt 字段**，所以连那些
一张 CC0 图都没有的流派（如赛博朋克、蒸汽朋克）也能被匹配到 ——
而基于图像质心的做法对它们无能为力。

用法
    python3 clip_match.py prompts             # 看每个流派用的文本提示
    python3 clip_match.py eval                # 评测：零样本 / 质心 / 融合
    python3 clip_match.py match <图片> [-n 5]  # 给一张图找最像的流派
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "_data", "clip_cache.json")

sys.path.insert(0, HERE)
for _c in (os.path.join(HERE, "vendor", "libs"), os.path.expanduser("~/.artvault/deps"),
           os.environ.get("ARTVAULT_DEPS", "")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

# 不是流派的目录（用户投递箱）
NOT_MOVEMENTS = {"pinterest"}

# 融合权重：score = W_ZERO * 零样本z + (1-W_ZERO) * 质心z
#
# **这个值不能拍脑袋，也不能追噪声里的 argmax。**
# 最初用等权 0.5，融合比纯质心还差 —— 零样本较弱（21.5%），
# 等权等于让弱信号压过强信号。
#
# 在**正确的**留一法下扫权重（396 张图、72 个流派、随机 1.4%）：
#
#     w=0.00（纯质心） 37.6 / 59.8      w=0.25  38.6 / 61.4
#     w=0.05          38.4 / 60.1      w=0.50  33.1 / 57.1
#     w=0.10          39.6 / 60.9      w=1.00  21.5 / 36.6（纯零样本）
#     w=0.15          39.1 / 61.4
#     w=0.20          39.1 / 61.6
#
# 0.10–0.20 是个**平台**（39.1~39.6%），两端差异落在 396 样本的噪声范围内
# （±2.5pp @95%）。所以取平台中值 0.15，而不是去追 0.10 那个高 0.5pp 的
# argmax —— 那是在拟合噪声。
W_ZERO = 0.15

# CLIP 官方推荐的 prompt ensemble 做法：一个类别配多句模板、取平均。
# 单句模板对措辞很敏感，平均几句能明显稳住。
TEMPLATES = [
    "{style}",
    "a painting in the style of {name}: {style}",
    "{style}, {mood}",
    "{name} art, {style}, {composition}",
]


def slug_of(relpath):
    parts = relpath.split("/")
    return parts[2] if len(parts) >= 4 and parts[0] == "99-附件" else "?"


# ------------------------------------------------------------ 文本侧
def movement_prompts(movements=None):
    """给每个流派拼出几句英文描述，用于 CLIP 文本塔。"""
    if movements is None:
        from movements import MOVEMENTS
        movements = MOVEMENTS
    out = {}
    for m in movements:
        p = m.get("prompt") or {}
        name = m.get("name_en") or m.get("name_zh") or m["slug"]
        style = (p.get("style") or "").strip()
        if not style:
            style = "%s style" % name
        ctx = {"style": style.rstrip(" ,"),
               "name": name,
               "mood": (p.get("mood") or "characteristic mood").rstrip(" ,"),
               "composition": (p.get("composition") or "characteristic composition").rstrip(" ,")}
        texts = []
        for t in TEMPLATES:
            try:
                s = t.format(**ctx).strip()
            except Exception:
                continue
            if s and s not in texts:
                texts.append(s)
        out[m["slug"]] = {"name": name, "texts": texts}
    return out


_TEXT_CACHE = None


def text_matrix():
    """返回 (slugs, 矩阵[N,512])。每个流派的模板取平均后重新归一化。"""
    global _TEXT_CACHE
    if _TEXT_CACHE is not None:
        return _TEXT_CACHE
    import numpy as np
    import clip_embed as C
    mp = movement_prompts()
    slugs = sorted(mp)
    flat, owner = [], []
    for s in slugs:
        for t in mp[s]["texts"]:
            flat.append(t)
            owner.append(s)
    E = C.text_embed(flat)
    if E is None:
        return None
    M = np.zeros((len(slugs), E.shape[1]), dtype="f4")
    idx = {s: i for i, s in enumerate(slugs)}
    for j, s in enumerate(owner):
        M[idx[s]] += E[j]
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    M = M / n
    _TEXT_CACHE = (slugs, M)
    return _TEXT_CACHE


# ------------------------------------------------------------ 图像侧
def load_cache():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _np_matrix(cache, slugs=None):
    import numpy as np
    items = [(k, v) for k, v in cache.items() if slug_of(k) not in NOT_MOVEMENTS]
    if slugs is not None:
        items = [(k, v) for k, v in items if slug_of(k) in slugs]
    keys = [k for k, _v in items]
    if not keys:
        return [], None
    X = np.asarray([v for _k, v in items], dtype="f4")
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-8)
    return keys, X


def _label_index(keys):
    labels = {}
    for k in keys:
        labels.setdefault(slug_of(k), []).append(k)
    return labels


# ------------------------------------------------------------ 评测
def evaluate(min_samples=3, verbose=True):
    """三种做法在同一批图上比。

    零样本不需要留一法（它完全不用参考图），质心法用留一法。
    两者都是「在候选流派里选一个」，所以数字可以并排看。
    """
    import numpy as np
    cache = load_cache()
    if not cache:
        print("没有 CLIP 缓存。先跑：python3 clip_embed.py build")
        return None
    tm = text_matrix()
    if tm is None:
        print("CLIP 文本塔不可用。先跑：python3 clip_embed.py download")
        return None
    slugs, M = tm
    keys, X = _np_matrix(cache, slugs)
    if not keys:
        print("缓存里没有可用图像")
        return None

    labels = _label_index(keys)
    # 候选：有 >= min_samples 张图的流派（与另两条路同口径）
    cands = sorted([s for s, v in labels.items() if len(v) >= min_samples])
    cidx = {s: i for i, s in enumerate(cands)}
    Mc = M[[slugs.index(s) for s in cands]]
    rows = [i for i, k in enumerate(keys) if slug_of(k) in cidx]

    # 精确留一法：预存每个流派的向量**和**与计数，查询时现算
    # 「排除这张图之后」的质心。
    #
    # 踩过的坑：最初在循环里直接改写 cents[cidx[truth]]，看着像留一法，
    # 其实只排除了该流派的**第一张**图 —— 之后每张图用的都是那个旧质心。
    # 这种状态泄漏会让数字不可复现（同一份数据两次跑出 41.2% 和 40.4%）。
    sums = {s: X[[i for i, k in enumerate(keys) if slug_of(k) == s]].sum(axis=0)
            for s in cands}
    cnts = {s: sum(1 for k in keys if slug_of(k) == s) for s in cands}

    zs_ok = ct_ok = fu_ok = zs3 = ct3 = fu3 = 0
    for i in rows:
        truth = slug_of(keys[i])
        q = X[i]
        zs = Mc @ q                                   # 零样本：图 vs 文本
        # 质心：精确留一（把自己从所属流派的核心里去掉）
        ct = np.empty(len(cands), dtype="f4")
        for s in cands:
            k = cidx[s]
            if s == truth and cnts[s] > 1:
                c = (sums[s] - q) / float(cnts[s] - 1)
            else:
                c = sums[s] / float(cnts[s])
            nrm = float(np.linalg.norm(c))
            ct[k] = float((c / nrm) @ q) if nrm > 0 else 0.0
        # 融合：两条分数各自 z 归一化后按实测权重相加（量纲不同，必须先归一化）
        z1 = (zs - zs.mean()) / (zs.std() + 1e-8)
        z2 = (ct - ct.mean()) / (ct.std() + 1e-8)
        fu = W_ZERO * z1 + (1.0 - W_ZERO) * z2
        if cands[int(np.argmax(zs))] == truth:
            zs_ok += 1
        if cands[int(np.argmax(ct))] == truth:
            ct_ok += 1
        if cands[int(np.argmax(fu))] == truth:
            fu_ok += 1
        for arr, bump in ((zs, "zs"), (ct, "ct"), (fu, "fu")):
            top = set(cands[j] for j in np.argsort(-arr)[:3])
            if truth in top:
                if bump == "zs": zs3 += 1
                elif bump == "ct": ct3 += 1
                else: fu3 += 1

    n = len(rows)
    chance = 1.0 / len(cands)
    res = {"n": n, "movements": len(cands), "chance": chance,
           "zeroshot_top1": zs_ok / n, "zeroshot_top3": zs3 / n,
           "centroid_top1": ct_ok / n, "centroid_top3": ct3 / n,
           "fusion_top1": fu_ok / n, "fusion_top3": fu3 / n}
    if verbose:
        print("CLIP 图像→流派评测：%d 张图，%d 个候选流派，随机基准 %.1f%%"
              % (n, len(cands), chance * 100))
        print()
        print("%-26s %10s %10s" % ("做法", "Top-1", "Top-3"))
        print("-" * 48)
        print("%-26s %9.1f%% %9.1f%%" % ("零样本（图 vs 流派文本）",
                                         res["zeroshot_top1"] * 100, res["zeroshot_top3"] * 100))
        print("%-26s %9.1f%% %9.1f%%" % ("图像质心（留一法）",
                                         res["centroid_top1"] * 100, res["centroid_top3"] * 100))
        print("%-26s %9.1f%% %9.1f%%" % ("融合（零样本权重 %.2f）" % W_ZERO,
                                         res["fusion_top1"] * 100, res["fusion_top3"] * 100))
        print()
        print("对照（同口径）：Vision featureprint 30.6%% / 50.8%%，"
              "T1 客观维度 13.2%% / 25.3%%.")
    return res


# ------------------------------------------------------------ 匹配
def match(path, topn=5):
    """给一张图找最像的流派。

    **按融合分排序**，不是按零样本排 —— 实测零样本单独只有 21.5%，
    质心 37.6%，融合 39.1%。只用零样本排等于扔掉最强信号。
    """
    import numpy as np
    import clip_embed as C
    tm = text_matrix()
    if tm is None:
        print("CLIP 不可用。先跑：python3 clip_embed.py download")
        return 1
    slugs, M = tm
    emb = C.embed_batch([path])
    if not emb:
        print("图像编码失败")
        return 1
    q = np.asarray(list(emb.values())[0], dtype="f4")
    q = q / max(float(np.linalg.norm(q)), 1e-8)

    zs = M @ q                       # 零样本：与流派文字描述的相似度

    # 图像质心：只对有 >=3 张实图的流派算（样本太少的质心噪声大）
    cache = load_cache()
    keys, X = _np_matrix(cache, set(slugs))
    ct = {}
    if keys:
        for s in slugs:
            sel = [i for i, k in enumerate(keys) if slug_of(k) == s]
            if len(sel) < 3:
                continue
            c = X[sel].mean(axis=0)
            n = float(np.linalg.norm(c))
            if n > 0:
                ct[s] = float((c / n) @ q)

    # 在「两个分数都有」的流派上做 z 归一化再融合
    have = [s for s in slugs if s in ct]
    if have:
        a = np.array([zs[slugs.index(s)] for s in have], dtype="f4")
        b = np.array([ct[s] for s in have], dtype="f4")
        z1 = (a - a.mean()) / (a.std() + 1e-8)
        z2 = (b - b.mean()) / (b.std() + 1e-8)
        fused = W_ZERO * z1 + (1.0 - W_ZERO) * z2
        order = np.argsort(-fused)
    else:
        have, fused, order = [], np.array([]), []

    mp = movement_prompts()
    print("查询：%s" % os.path.basename(path))
    print("按融合分排序（零样本权重 %.2f）—— 融合实测 Top-1 39.1%%，" % W_ZERO)
    print("高于单用质心的 37.6% 和单用零样本的 21.5%。")
    print()
    print("%-24s %-24s %9s %9s" % ("slug", "流派", "零样本", "图像质心"))
    print("-" * 72)
    for j in order[:topn]:
        s = have[int(j)]
        print("%-24s %-24s %9.3f %9.3f"
              % (s[:24], str(mp[s]["name"])[:24], zs[slugs.index(s)], ct[s]))

    # 库里没有（或不足 3 张）参考图的流派，只能靠零样本 —— 这是 CLIP 独有的能力
    only_zs = sorted([s for s in slugs if s not in ct], key=lambda s: -zs[slugs.index(s)])[:3]
    if only_zs:
        print()
        print("另：以下流派库里没有足够实图，只能靠文字匹配（CLIP 独有的能力）")
        for s in only_zs:
            print("      %-24s %-24s 零样本 %.3f"
                  % (s[:24], str(mp[s]["name"])[:24], zs[slugs.index(s)]))
    print()
    print("「零样本」= 图像向量与流派**文字描述**的余弦相似度；")
    print("「图像质心」= 与库里该流派实图平均向量的相似度（样本 <3 张时不给）。")
    r = evaluate(verbose=False)
    if r:
        print()
        print("排序有信息量（随机基准 %.1f%%），但 Top-1 约四成意味着十次错六次 ——"
              % (r["chance"] * 100))
        print("当**建议**用。判风格请以流派卡为准：python3 artvault.py layers <流派>")
    return 0


def main():
    ap = argparse.ArgumentParser(description="CLIP 图像→流派匹配（零样本）")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("eval", help="评测：零样本 / 质心 / 融合")
    p = sub.add_parser("match", help="给一张图找最像的流派")
    p.add_argument("target")
    p.add_argument("-n", type=int, default=5)
    sub.add_parser("prompts", help="查看每个流派用的文本提示")
    a = ap.parse_args()

    if a.cmd == "eval":
        return 0 if evaluate() else 1
    if a.cmd == "match":
        return match(a.target, a.n)
    if a.cmd == "prompts":
        mp = movement_prompts()
        print("共 %d 个流派，每个用 %d 句模板" % (len(mp), len(TEMPLATES)))
        for s in ["baroque", "ukiyo-e", "tonalism"]:
            if s in mp:
                print("\n[%s] %s" % (s, mp[s]["name"]))
                for t in mp[s]["texts"]:
                    print("   · %s" % t[:110])
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
