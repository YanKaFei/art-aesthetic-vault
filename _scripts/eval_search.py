#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_search.py —— 量一下检索到底行不行，顺便把融合权重 W_SEM 选出来。

    python3 eval_search.py              # 全部
    python3 eval_search.py --weights    # 只扫权重

## 为什么要有这个脚本

`artvault_core.W_SEM = 0.45` 这个数字如果只是拍脑袋写的，那它和「把统计数字
写死在 README 里」是同一类问题 —— 会烂掉，而且没人知道它当初为什么是 0.45。
这个脚本就是那个数字的出处：**可复跑、有对照、结果打印出来**。

## 两组评测，各管一件事

**A 组 · 精确度守卫（自动，141 条）**
    查询 = 该流派自己的中文一句简介。正确结果就是它自己。
    这组**不测语义增益** —— 简介原文本就在卡里，关键词检索当然找得到。
    它守的是反面：语义分会不会**把本来对的挤下去**（稀释）。所以这组要求
    加语义之后命中率不能掉 —— 掉了就说明 W_SEM 太高。

**B 组 · 语义增益（人工标注，见 CASES）**
    查询是**描述性说法**，刻意不用流派名、也不用卡里现成的句子
    （「霓虹雨夜的城市」而不是「赛博朋克」）。
    这组测的是关键词检索**根本接不住**的那类问题 —— 语义检索的存在理由。
    标注是我写的，所以它会带入我的判断；但每条都写明期望流派，
    你可以直接改 CASES 重新跑。
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


# ---------------------------------------------------------------- B 组标注
# (查询, 期望流派 slug 集合)  —— 命中集合里任意一个就算对
CASES = [
    ("霓虹雨夜的城市，巨型广告和湿漉漉的街道", {"cyberpunk", "synthwave"}),
    ("宁静的水墨风景，大量留白", {"suiboku-ga", "ink-wash-xieyi", "song-academic"}),
    ("金色背景的宗教圣像，平面化，正面构图", {"byzantine", "russian-icon"}),
    ("厚重的笔触，强烈的明暗对照，戏剧性的光", {"baroque", "caravaggisti"}),
    ("分解成几何切面的静物，同时看到好几个角度", {"cubism"}),
    ("点彩的小笔触拼出光感", {"neo-impressionism", "pointillism"}),
    ("梦一样的超现实场景，不合理的并置", {"surrealism"}),
    ("废土之后的荒芜景象，锈迹与废墟", {"wasteland", "dieselpunk"}),
    ("浮世绘风格的海浪与富士山", {"ukiyo-e"}),
    ("战后抽象的色块，情绪压倒形状", {"abstract-expressionism", "color-field"}),
    ("极简的几何形状，原色，去掉一切装饰", {"bauhaus", "minimalism-design", "de-stijl"}),
    ("粉彩、曲线、享乐气息的宫廷场景", {"rococo"}),
    ("把光照当成主角，暗部大面积吞没", {"baroque", "caravaggisti", "tenebrism"}),
    ("工业化流水线般的精确与重复", {"precisionism", "constructivism"}),
    ("安静的黄昏雾气，边界模糊的风景", {"tonalism"}),
]


def _name(slug):
    from movements import MOVEMENTS
    for m in MOVEMENTS:
        if m["slug"] == slug:
            return m["name_zh"]
    return slug


def _self_queries():
    """A 组：每个流派用自己的中文简介当查询。"""
    import artvault_core as A
    out = []
    for c in A.cards():
        q = (c.get("one_liner") or "").strip()
        if len(q) >= 6:
            out.append((q, {c["slug"]}))
    return out


def run_set(cases, limit, semantic):
    """返回 (top1 命中数, top3 命中数, 总数)。"""
    import artvault_core as A
    t1 = t3 = 0
    for q, want in cases:
        got = [c["slug"] for c in A.search(q, limit=limit, semantic=semantic)]
        if got[:1] and got[0] in want:
            t1 += 1
        if want & set(got[:3]):
            t3 += 1
    return t1, t3, len(cases)


def fmt(t1, t3, n):
    return "Top-1 %5.1f%%   Top-3 %5.1f%%   (n=%d)" % (
        100.0 * t1 / max(n, 1), 100.0 * t3 / max(n, 1), n)


def semantic_available():
    try:
        import clip_embed as C
        if C.available():
            return False, C.available()
        import clip_match as CM
        if CM.text_matrix() is None:
            return False, "文本矩阵不可用"
        return True, ""
    except Exception as e:
        return False, "%s: %s" % (type(e).__name__, e)


def sweep_threshold(limit=8):
    """扫 SEM_TAKEOVER：A 组（精确守卫）不能掉，B 组（语义增益）越高越好。

    这个扫描就是 `artvault_core.SEM_TAKEOVER` 的出处。别改代码里的值而不跑它。
    """
    import artvault_core as A
    a_cases = _self_queries()
    base_a = run_set(a_cases, limit, semantic=False)
    base_b = run_set(CASES, limit, semantic=False)
    print("  %-10s %-30s %s" % ("阈值", "A组(精确守卫)", "B组(语义增益)"))
    print("  " + "-" * 72)
    print("  %-10s %s   %s   ← 纯关键词" % ("—", fmt(*base_a), fmt(*base_b)))
    rows = []
    for t in (1, 2, 3, 4, 5, 8):
        A.SEM_TAKEOVER = t
        ra = run_set(a_cases, limit, semantic=True)
        rb = run_set(CASES, limit, semantic=True)
        rows.append((t, ra, rb))
        mark = ""
        if ra[0] >= base_a[0]:
            mark = "   ← A 组零损失"
        print("  T=%-8s %s   %s%s" % (t, fmt(*ra), fmt(*rb), mark))
    return base_a, base_b, rows


def main(argv):
    ap = argparse.ArgumentParser(description="检索评测：把 W_SEM 从拍脑袋变成实测")
    ap.add_argument("--weights", action="store_true", help="只扫权重")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args(argv)

    ok, why = semantic_available()
    if not ok:
        print("语义检索不可用：%s" % why)
        print("（需要先跑 python3 clip_embed.py download && clip_embed.py build，"
              "以及装 numpy）")
        print()
        print("只跑关键词基线：")
        print("  A 组 %s" % fmt(*run_set(_self_queries(), a.limit, semantic=False)))
        print("  B 组 %s" % fmt(*run_set(CASES, a.limit, semantic=False)))
        return 1

    print("=" * 70)
    print("A 组 · 精确度守卫：查询=流派自己的简介，看会不会被语义分挤下去")
    print("B 组 · 语义增益：描述性查询（不含流派名），关键词接不住的那类")
    print("=" * 70)
    sweep_threshold(a.limit)

    import artvault_core as A
    print()
    print("取法：**A 组零损失**里 T 最大的那个（保住精确匹配的前提下，")
    print("让语义尽量多接管）。T 再往上 A 组就开始掉，说明连词面命中都被判成不可信。")
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 eval_search.py [--weights] [--limit N]",
          ["量检索效果并把融合权重 W_SEM 选出来。",
           "A 组守卫精确度、B 组测语义增益，两组都打印完整数字。",
           "需要先下 CLIP 模型，否则只打关键词基线。"])
    sys.exit(main(sys.argv[1:]))
