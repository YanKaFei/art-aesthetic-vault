#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visual_signature.py —— 从实图反推每个流派的**可测量区间**。

## 它做的是「描述区间」，不是「分类」

曾经还有一个脚本（`movement_fingerprint.py`）用客观维度算**质心**来做
「这张图像哪个流派」的匹配 —— 实测那条路最弱（最近邻同流派 13.4%，
随机基准 1.4%），已经删掉，只留下结论。

这个模块做的是另一件事：**描述区间**。回答的不是「这是哪个流派」，
而是「这张图真的像它声称的那个流派吗」。

    匹配（fingerprint）  给一张图猜流派      → 弱，别当结论
    签名（这里）        给定流派查区间      → 用途是**验收**，不是分类

区别很重要：分类要求跨流派可比，物理测量做不到；而验收只要求**同一流派内部
自洽**，这就宽松得多，也可解释得多 —— 能直接说「你这张熵 7.2，而这个流派的
实图集中在 4.1–5.6，所以它不太像该流派」。

## 为什么要挑「有区分度」的维度

不是所有测量都有信息。画面比例（ratio）几乎不区分流派，各流派的 6 张图之间
差异比流派之间还大。所以这里算一个类间/类内方差比（类似 F 统计量），
把「流派之间差得开、流派内部又稳定」的维度排前面，并在文档里如实标出
哪些维度**没有区分度** —— 硬拿噪声维度去判「像不像」是自欺。

## 样本量的诚实交代

每流派中位 6 张图，p10/p90 区间会很宽。所以 `min_n` 以下的流派不出签名
（区间宽到没有约束力，写出来只是好看）。
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "_data")
CACHE = os.path.join(DATA, "signatures.json")
IMAGES = os.path.join(VAULT, "99-attachments", "images")

# 参与签名的数值维度。刻意剔掉几类：
#   ratio / orientation        画面比例受题材支配，跨流派几乎不区分
#   harmony.mean_hue           色相是环形的，取平均没有意义（红+青平均成灰）
#   composition.*_energy       和 luminance 高度共线，留着只是重复计权
#   luminance.p05/p95/median   与 mean/std/dynamic_range 重复
DIMS = [
    ("luminance.mean", "明度均值"),
    ("luminance.std", "明度离散"),
    ("luminance.dynamic_range", "动态范围"),
    ("luminance.shadow_clip_pct", "暗部溢出%"),
    ("luminance.highlight_clip_pct", "高光溢出%"),
    ("contrast.rms", "对比 RMS"),
    ("contrast.michelson", "Michelson 对比"),
    ("color.saturation", "饱和度"),
    ("color.warm_score", "暖度"),
    ("harmony.concentration", "主色集中度"),
    ("harmony.effective_hues", "有效色相数"),
    ("harmony.colored_ratio", "有色面积比"),
    ("composition.thirds_energy", "三分点能量"),
    ("composition.center_weight", "中心权重"),
    ("composition.symmetry_h", "水平对称"),
    ("texture.edge_density", "边缘密度"),
    ("texture.local_variance", "局部方差"),
    ("texture.entropy", "熵"),
    ("lines.strong_edge_pct", "强边缘%"),
]

# 少于这么多张图的流派不出签名 —— 区间宽到没有约束力
MIN_N = 4


def _get(d, path):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
        if cur is None:
            return None
    return cur if isinstance(cur, (int, float)) else None


def _pct(vals, q):
    """线性插值分位数（不引 numpy —— 这个模块要能在纯标准库下跑）。"""
    if not vals:
        return None
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def images_by_movement():
    """{slug: [图片路径…]}，按流派目录分组。"""
    out = {}
    if not os.path.isdir(IMAGES):
        return out
    for d in sorted(os.listdir(IMAGES)):
        p = os.path.join(IMAGES, d)
        if not os.path.isdir(p):
            continue
        fs = [os.path.join(p, f) for f in sorted(os.listdir(p))
              if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
        if fs:
            out[d] = fs
    return out


def compute(verbose=False):
    """扫描所有实图，返回 (signatures, meta)。不写盘。"""
    try:
        import image_analysis as IA
    except Exception as e:
        return None, {"error": "image_analysis 不可用：%s" % e}

    by_mv = images_by_movement()
    if not by_mv:
        return None, {"error": "没有找到任何流派图片目录"}

    raw = {}          # slug -> {dim: [值…]}
    skipped = 0
    for slug, files in sorted(by_mv.items()):
        per = {k: [] for k, _ in DIMS}
        for f in files:
            a = IA.analyze(f)
            if a.get("error"):
                skipped += 1
                continue
            for k, _zh in DIMS:
                v = _get(a, k)
                if v is not None:
                    per[k].append(float(v))
        # 只保留够了样本量的维度
        keep = {k: v for k, v in per.items() if len(v) >= MIN_N}
        if keep:
            raw[slug] = keep
        if verbose:
            print("  %s: %d 张" % (slug, len(files)))

    if not raw:
        return None, {"error": "没有任何流派达到 %d 张的样本量" % MIN_N,
                      "skipped": skipped}

    # 签名：中位数 + p10/p90
    sigs = {}
    for slug, per in raw.items():
        entry = {}
        for k, vals in per.items():
            entry[k] = {"p10": round(_pct(vals, 0.10), 2),
                        "median": round(_pct(vals, 0.50), 2),
                        "p90": round(_pct(vals, 0.90), 2),
                        "n": len(vals)}
        sigs[slug] = {"dims": entry, "n_img": max(len(v) for v in per.values())}

    # 区分度：类间方差 / 类内方差（越大越能区分流派）
    disc = []
    for k, zh in DIMS:
        groups = [s["dims"][k]["median"] for s in sigs.values() if k in s["dims"]]
        if len(groups) < 3:
            continue
        grand = sum(groups) / len(groups)
        between = sum((g - grand) ** 2 for g in groups) / len(groups)
        # 类内：用 (p90-p10)/2.56 近似标准差
        within = []
        for s in sigs.values():
            d = s["dims"].get(k)
            if d:
                within.append(((d["p90"] - d["p10"]) / 2.56) ** 2)
        w = sum(within) / len(within) if within else 0.0
        disc.append({"dim": k, "zh": zh,
                     "between": round(between, 3), "within": round(w, 3),
                     "ratio": round(between / w, 3) if w > 1e-9 else None})
    disc.sort(key=lambda x: -(x["ratio"] or 0))

    meta = {"n_movements": len(sigs), "n_images": sum(s["n_img"] for s in sigs.values()),
            "min_n": MIN_N, "skipped_errors": skipped,
            "discriminative": disc,
            "no_signal": [d["dim"] for d in disc if not d["ratio"] or d["ratio"] < 0.25]}
    return sigs, meta


def build(force=False, verbose=False):
    """算并写盘。已有缓存且非 force 时直接读。"""
    if not force and os.path.exists(CACHE):
        d = json.load(open(CACHE, encoding="utf-8"))
        if d.get("signatures"):
            return d["signatures"], d.get("meta") or {}
    sigs, meta = compute(verbose=verbose)
    if sigs is None:
        return None, meta
    if not os.path.isdir(DATA):
        os.makedirs(DATA, exist_ok=True)
    json.dump({"signatures": sigs, "meta": meta},
              open(CACHE, "w", encoding="utf-8"), ensure_ascii=False)
    return sigs, meta


def load():
    if not os.path.exists(CACHE):
        return None, {}
    try:
        d = json.load(open(CACHE, encoding="utf-8"))
        return d.get("signatures"), d.get("meta") or {}
    except Exception:
        return None, {}


# ------------------------------------------------------------------ 校验
def check(path, slug):
    """一张图对某个流派的签名。返回 dict（verdict / 越界维度 / 依据）。

    verdict 取值：fit（落在区间内）/ partial（部分越界）/ off（明显不像）/
    unknown（该流派没有签名，或图读不出来）。
    """
    sigs, _meta = load()
    if not sigs or slug not in sigs:
        return {"verdict": "unknown", "reason": "该流派还没有签名（样本不足或无图）"}
    try:
        import image_analysis as IA
    except Exception as e:
        return {"verdict": "unknown", "reason": "image_analysis 不可用：%s" % e}
    a = IA.analyze(path)
    if a.get("error"):
        return {"verdict": "unknown", "reason": a["error"]}

    inside, outside = [], []
    for k, zh in DIMS:
        d = sigs[slug]["dims"].get(k)
        if not d:
            continue
        v = _get(a, k)
        if v is None:
            continue
        if d["p10"] <= v <= d["p90"]:
            inside.append((zh, v, d))
        else:
            # 越界程度：相对区间宽度。区间宽为 0（该维度在这个流派里几乎恒定，
            # 比如「暗部溢出%」样本全是 0）时**不能拿它当分母** —— 第一版没防，
            # 输出成了「偏离 2200000.0 个区间宽」。改成报绝对偏离并标注。
            width = d["p90"] - d["p10"]
            dist = (d["p10"] - v) if v < d["p10"] else (v - d["p90"])
            rel = round(dist / width, 2) if width > 0.05 else None
            outside.append((zh, round(v, 2), d, rel, round(dist, 2)))
    # 排序：能算相对偏离的按相对值，算不了的排后面
    outside.sort(key=lambda x: -(x[3] if x[3] is not None else -1))
    n_all = len(inside) + len(outside)
    if n_all == 0:
        return {"verdict": "unknown", "reason": "没有可比对的维度"}
    # 分档要记住签名是 p10–p90 构造的：**样本内**的图天然就有约 20% 的维度
    # 落在区间外（分位数的定义如此）。所以「同流派的图」正常结果就是 partial，
    # fit 只留给非常居中那些；跨流派的图会到 40–50% 以上。
    ratio = len(outside) / float(n_all)
    if ratio <= 0.10:
        verdict = "fit"
    elif ratio <= 0.30:
        verdict = "partial"
    else:
        verdict = "off"
    return {"verdict": verdict, "inside": len(inside), "outside": outside,
            "n_dims": n_all, "n_img": sigs[slug]["n_img"]}


def describe(slug, top=4):
    """卡片上的一行紧凑描述：只列该流派**最有信息**的几个维度。

    「有信息」按全局区分度排 —— 拿没有区分度的维度写签名等于写噪声。
    """
    sigs, meta = load()
    if not sigs or slug not in sigs:
        return ""
    rank = {d["dim"]: i for i, d in enumerate(meta.get("discriminative") or [])}
    dims = sigs[slug]["dims"]
    order = sorted(dims, key=lambda k: rank.get(k, 999))[:top]
    zh = dict(DIMS)
    parts = []
    for k in order:
        d = dims[k]
        parts.append("%s %.1f–%.1f" % (zh.get(k, k), d["p10"], d["p90"]))
    return " ｜ ".join(parts)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="流派的可测量视觉签名")
    ap.add_argument("cmd", nargs="?", default="report",
                    choices=["report", "build", "check", "dims"])
    ap.add_argument("target", nargs="?", help="check 时是图片路径")
    ap.add_argument("--slug", help="check 时要比对的流派")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)

    if a.cmd == "dims":
        for k, zh in DIMS:
            print("  %-28s %s" % (k, zh))
        return 0
    if a.cmd == "build":
        sigs, meta = build(force=True, verbose=True)
        if sigs is None:
            print("构建失败：%s" % meta.get("error"))
            return 1
        print("已算 %d 个流派的签名 → %s" % (len(sigs), os.path.relpath(CACHE, VAULT)))
        return 0
    if a.cmd == "check":
        if not a.target or not a.slug:
            print("用法：python3 visual_signature.py check <图片> --slug <流派>")
            return 2
        r = check(a.target, a.slug)
        if r["verdict"] == "unknown":
            print("无法判断：%s" % r["reason"])
            return 1
        print("结论：%s（%d/%d 个维度落在区间内，签名取自 %d 张实图）"
              % ({"fit": "像", "partial": "大体像但有偏差", "off": "不太像"}[r["verdict"]],
                 r["inside"], r["n_dims"], r["n_img"]))
        for zh, v, d, rel, dist in r["outside"][:8]:
            arrow = "低于" if v < d["p10"] else "高于"
            how = ("偏离 %.1f 个区间宽" % rel) if rel is not None else \
                  ("偏离 %.2f（该流派这个维度几乎恒定）" % dist)
            print("   · %s %s：这张 %.2f，该流派集中在 %.2f–%.2f（%s）"
                  % (zh, arrow, v, d["p10"], d["p90"], how))
        if r["outside"]:
            print("   ↑ 这些是「哪里不像」。物理测量会有题材带来的噪声，"
                  "当线索用，别当判决。")
        return 0

    sigs, meta = build()
    if sigs is None:
        print("还没有签名：%s" % meta.get("error"))
        print("先跑：python3 visual_signature.py build")
        return 1
    print("流派 %d 个，覆盖 %d 张实图（每流派至少 %d 张）"
          % (meta["n_movements"], meta["n_images"], meta["min_n"]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 visual_signature.py [report|build|check|dims]",
          ["report  打印覆盖情况（默认）",
           "build   重算并写 _data/signatures.json",
           "check <图片> --slug <流派>   看这张图像不像该流派",
           "dims    列出参与签名的测量维度"])
    sys.exit(main(sys.argv[1:]))
