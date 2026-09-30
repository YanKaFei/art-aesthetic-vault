#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
still_analysis.py —— 剧照全量实测：把每一张画面量成数字，聚合成全片图景。

## 这一层回答什么问题

`40-films/` 的电影卡上写的是**「这部片的画面长什么样」**——那是手写的解读
（基于公认的摄影特征）。这一层回答的是另一个问题：

    **「这 1001 张画面，实测下来到底是什么样？」**

每张量七维（明度/对比/色彩/和谐/构图/质感/线条）+ 景别（人脸尺寸）+
构图线（霍夫直线）+ 显著性（视觉重心），然后：
  · 全片聚合：均值、分位数、帧幅分布
  · 实测主色：全片最常出现的六个颜色
  · 代表帧：k-medoids 从全片挑出「最像整体」的 8–12 张
  · 与手写配色的差异比对

## 铁律：实测**不得**改写手写描述

这是本库的既有规矩 —— **数字是信号不是结论**。实测一张油画的土色系
曾被配色匹配误判成「现实主义」，而它其实毫不相干。所以：

    palette_diff() 只**报告**差异，没有修改权。
    analyse_film() 只**返回**数字，不写回 fv_data.py。

`tests/still_test.py` 里有一条测试守着「本模块不得对 fv_data 有写操作」。
改不改、怎么改，由人看过两边之后决定。

## 诚实覆盖 > 结论精确

实测页必须写明「已量 N / 共 M 张」。用 176 张样本冒充 1001 张的全片均值
是**最能骗人的一种错** —— 它算出来的数字全都对，只有样本不对。
所以 `analyse_film()` 返回的 `measured` / `total_linked` 会被渲染到页面上。

## 缓存

1001 张 × 0.19s ≈ 3 分钟，重复跑没有意义。缓存落在 `_data/stills/<slug>.json`，
按**源文件大小 + 修改时间**校验 —— 图被换过就重算，绝不返回陈旧数字。
缓存只存测量结果，不存任何「结论」。
"""

import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# 可选依赖装在 vendor/libs（本库的约定）
for _c in (os.environ.get("ARTVAULT_DEPS", ""),
           os.path.join(HERE, "vendor", "libs"),
           os.path.expanduser("~/.artvault/deps")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

STILLS_DIR = os.path.join(VAULT, "99-attachments", "images-films")
DATA_DIR = os.path.join(HERE, "_data", "stills")

# 色相 × 饱和度 的直方图。形状固定是代表帧选择可复现的前提。
HUE_BINS, SAT_BINS = 8, 4
FEATURE_LEN = HUE_BINS * SAT_BINS

# 缓存结构版本。**改了卡上会出现的字段就要 +1** —— 指纹只能判断「图变了没」，
# 判断不了「代码变了没」，所以升级后旧缓存必须被判为过期重算。
# 实测踩到：加了 stability 之后，`analyse_film` 把旧缓存原样取出，
# 于是 `r["stability"]` 直接 KeyError，而缓存看着「有效」。
SCHEMA = 3

# 比对阈值：手写色与最近的实测色之间的 Lab 距离（0–100 量级）。
# 80 是「肉眼明显是两个颜色」的量级；60 是「同色系但有偏差」。
FAR_DIST = 60.0
CLOSE_DIST = 32.0


# ------------------------------------------------------------------ 颜色工具
def hex_to_rgb(h):
    h = (h or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return (0, 0, 0)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _srgb_to_lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb_to_lab(rgb):
    """sRGB → CIELAB。用 Lab 而不是 RGB 距离，因为 RGB 距离会把
    「深蓝 vs 深棕」判得比「浅蓝 vs 中蓝」更远 —— 那是亮度差在捣鬼，
    不是色相差。"""
    r, g, b = (_srgb_to_lin(x) for x in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722)
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else (7.787 * t + 16 / 116)

    fx, fy, fz = f(x), f(y), f(z)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def lab_distance(h1, h2):
    a, b = rgb_to_lab(hex_to_rgb(h1)), rgb_to_lab(hex_to_rgb(h2))
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


# ------------------------------------------------------------------ 特征
def feature(path):
    """色相-饱和度直方图（归一化）。用于代表帧选择。"""
    import numpy as np
    from PIL import Image

    im = Image.open(path).convert("RGB")
    im.thumbnail((256, 256))
    a = np.asarray(im, dtype=np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)

    h = np.zeros_like(mx)
    d = np.maximum(mx - mn, 1e-6)
    m = (mx == r)
    h[m] = ((g - b) / d)[m] % 6
    m = (mx == g) & (mx != r)
    h[m] = ((b - r) / d)[m] + 2
    m = (mx == b) & (mx != r) & (mx != g)
    h[m] = ((r - g) / d)[m] + 4
    h = h / 6.0                                  # 0–1

    # 只统计「有色」像素（饱和度够高）；无彩像素进最后一个亮度桶
    colored = s > 0.12
    hist = np.zeros(FEATURE_LEN, dtype=np.float64)
    if colored.any():
        hi = np.clip((h[colored] * HUE_BINS).astype(int), 0, HUE_BINS - 1)
        si = np.clip((s[colored] * SAT_BINS).astype(int), 0, SAT_BINS - 1)
        np.add.at(hist, hi * SAT_BINS + si, 1)
    grey = (~colored).sum()
    if grey:
        hist[-1] += grey
    tot = hist.sum()
    if tot <= 0:
        hist[-1] = 1.0
        tot = 1.0
    hist /= tot
    return [round(float(x), 6) for x in hist]


# ------------------------------------------------------------------ 单张测量
def analyse_still(path):
    """量一张。返回扁平的关键数字（原始报告太啰嗦，卡片上放不下）。

    缺 Pillow 时抛异常，由调用方决定怎么降级 —— 这里不吞。
    """
    import image_analysis as IA

    r = IA.analyze(path)
    if r.get("error"):
        raise RuntimeError(r["error"])
    lu, co, cl = r["luminance"], r["contrast"], r["color"]
    hm, cp, tx, ln = r["harmony"], r["composition"], r["texture"], r["lines"]
    ex = r.get("extended") or {}
    faces, sal = ex.get("faces") or {}, ex.get("saliency") or {}
    return {
        "file": os.path.basename(path),
        "width": r["size"][0],
        "height": r["size"][1],
        "ratio": round(float(r["ratio"]), 3),
        "orientation": r["orientation"],
        "luminance": round(float(lu["mean"]), 1),
        "luminance_median": round(float(lu["median"]), 1),
        "dynamic_range": round(float(lu.get("dynamic_range", 0)), 1),
        "shadow_clip_pct": round(float(lu.get("shadow_clip_pct", 0)), 2),
        "highlight_clip_pct": round(float(lu.get("highlight_clip_pct", 0)), 2),
        "key": lu.get("key", ""),
        "contrast": round(float(co["rms"]), 1),
        "contrast_level": co.get("level", ""),
        "saturation": round(float(cl["saturation"]), 3),
        "temperature": cl.get("temperature", ""),
        "warm_score": round(float(cl.get("warm_score", 0)), 1),
        "dominant": [(d["hex"], round(float(d["pct"]), 1)) for d in cl.get("dominant", [])],
        "harmony": hm.get("scheme", ""),
        "colored_ratio": round(float(hm.get("colored_ratio", 0)), 3),
        "mean_hue_name": hm.get("mean_hue_name", ""),
        "symmetry_hint": cp.get("symmetry_hint", ""),
        "symmetry_h": round(float(cp.get("symmetry_h", 0)), 1),
        "edge_density": round(float(tx.get("edge_density", 0)), 2),
        "busyness": tx.get("busyness", ""),
        "entropy": round(float(tx.get("entropy", 0)), 2),
        "line_orientation": ln.get("orientation", ""),
        "framing": faces.get("framing", "未检出面部"),
        "face_count": int(faces.get("count", 0)),
        "face_pct": round(float(faces.get("largest_face_pct", 0)), 2),
        "saliency_focus": sal.get("focus", ""),
        "saliency_x": round(float(sal.get("center_x", 0)), 3),
        "saliency_y": round(float(sal.get("center_y", 0)), 3),
        "features_available": not r.get("extended_disabled"),
    }


# ------------------------------------------------------------------ 聚合
def _q(vals, p):
    """分位数（线性插值），确定性实现 —— 不依赖 numpy 版本。"""
    if not vals:
        return None
    v = sorted(vals)
    if len(v) == 1:
        return v[0]
    k = (len(v) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(v) - 1)
    return round(v[lo] + (v[hi] - v[lo]) * (k - lo), 2)


def _mean(vals):
    return round(sum(vals) / len(vals), 2) if vals else None


def _top(counter, n=None):
    items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    return items[:n] if n else items


def _collect(counter, val):
    counter[val] = counter.get(val, 0) + 1


def _dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def k_medoids(feats, k):
    """k-medoids（PAM 思路，确定性）。

    为什么不用 k-means：k-means 的中心是**算出来的平均向量**，不是一个真实
    画面。而我们要的是「用哪几张图代表全片」—— 必须是真实存在的帧。
    为什么确定性很重要：生成物进版本库，选择一漂移，diff 就永远在抖。
    """
    n = len(feats)
    if k >= n:
        return list(range(n))
    if k <= 1:
        # 中位向量最近的那个点，稳且不随机
        med = [sorted(f[i] for f in feats)[n // 2] for i in range(len(feats[0]))]
        return [min(range(n), key=lambda i: (_dist(feats[i], med), i))]

    # 用最远点采样（FPS）播种：起点固定取 0 号，结果可复现
    sel = [0]
    while len(sel) < k:
        far, fd = None, -1.0
        for i in range(n):
            if i in sel:
                continue
            d = min(_dist(feats[i], feats[j]) for j in sel)
            if d > fd or (d == fd and far is not None and i < far):
                far, fd = i, d
        sel.append(far)

    def cost(meds):
        return sum(min(_dist(feats[i], feats[m]) for m in meds) for i in range(n))

    # 迭代改进：依次尝试把每个 medoid 换成能让总代价下降的点
    improved = True
    rounds = 0
    while improved and rounds < 12:
        improved, rounds = False, rounds + 1
        for mi in range(len(sel)):
            best, best_cost = sel[mi], cost(sel)
            for cand in range(n):
                if cand in sel:
                    continue
                trial = list(sel)
                trial[mi] = cand
                c = cost(trial)
                if c < best_cost - 1e-12:
                    best, best_cost = cand, c
            if best != sel[mi]:
                sel[mi] = best
                improved = True
    return sorted(set(sel))


# ------------------------------------------------------------------ 全片
def _img_dir(slug):
    return os.path.join(STILLS_DIR, slug)


def local_stills(slug):
    """本地已下载的剧照文件（按序号排序）。"""
    d = _img_dir(slug)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in sorted(os.listdir(d)):
        if re.match(r"^\d{2,}\.(jpe?g|png|webp)$", fn, re.I):
            out.append(os.path.join(d, fn))
    return out


_ABS_PATH = re.compile(r"['\"]?/(?:Users|home|Volumes|private|tmp|var)/[^'\"]*")


def _why(e):
    """把异常压成**不含绝对路径**的短原因。

    缓存（`.repo/_data/stills/*.json`）是要提交的，而 Pillow 的报错原文会把
    整个路径写进去：

        cannot identify image file '/Users/<某人>/Desktop/.../38.jpg'

    结果就是把作者的家目录带进了公开仓库 —— 实测被 CI 的「发布卫生」抓出来。
    这里只压掉**看起来像绝对路径**的片段，不依赖「路径恰好等于 VAULT」。
    """
    msg = _ABS_PATH.sub("<file>", str(e))
    return " ".join(msg.split())[:80]


def _sig(path):
    """源文件指纹：大小 + mtime。图被换过 → 缓存失效。"""
    try:
        st = os.stat(path)
        return "%d:%d" % (st.st_size, int(st.st_mtime))
    except OSError:
        return ""


def analyse_film(film, k=10, use_cache=True, progress=None):
    """量一部片的全部本地剧照。返回结构化结果（不写回任何手写数据）。"""
    slug = film["slug"]
    paths = local_stills(slug)
    cached = load_measurements(slug) if use_cache else None
    if cached and cached.get("schema") != SCHEMA:
        cached = None                     # 旧结构 → 整体重算，别复用半成品

    got = {}
    if cached and cached.get("stills"):
        for s in cached["stills"]:
            # 缓存里**不存** path（含机器特定的绝对路径，进仓库就成泄漏）。
            # 从 slug + 文件名推回来，结果一模一样。
            s["path"] = os.path.join(_img_dir(slug), s["file"])
            got[s["file"]] = s

    stills, skipped = [], []
    for p in paths:
        fn = os.path.basename(p)
        sig = _sig(p)
        if fn in got and got[fn].get("_sig") == sig:
            stills.append(got[fn])
            continue
        try:
            r = analyse_still(p)
            r["_sig"] = sig
            r["index"] = int(re.match(r"^(\d+)", fn).group(1))
            r["path"] = p
            stills.append(r)
            if progress:
                progress(slug, fn)
        except Exception as e:
            skipped.append((fn, _why(e)))
    stills.sort(key=lambda x: x["index"])

    res = {
        "schema": SCHEMA,
        "slug": slug,
        "title_zh": film["title_zh"],
        "director_zh": film["director_zh"],
        "measured": len(stills),
        "total_linked": len(film.get("stills") or []),
        "local_files": len(paths),
        "skipped": skipped,
        "stills": stills,
        "aggregate": _aggregate(stills),
        "representative": [],
        "palette_written": [h for h, _ in film["palette"]],
        "palette_written_named": list(film["palette"]),
        "palette_measured": _measured_palette(stills),
        # 覆盖度之后紧接着回答「那已量的这部分算得准吗」
        "stability": sample_stability(stills),
    }
    res["palette_diff"] = palette_diff(list(film["palette"]), res["palette_measured"])

    feats = []
    for s in stills:
        try:
            feats.append(feature(s["path"]))
        except Exception:
            feats.append([0.0] * FEATURE_LEN)
    if stills and len(feats) == len(stills):
        for idx in k_medoids(feats, min(k, len(stills))):
            s = dict(stills[idx])
            res["representative"].append({
                "index": s["index"], "file": s["file"], "path": s["path"],
                "luminance": s["luminance"], "saturation": s["saturation"],
                "temperature": s["temperature"], "framing": s["framing"],
                "key": s["key"], "ratio": s["ratio"],
            })
    save_measurements(slug, _strip_paths(res))
    return res


def _strip_paths(res):
    """写盘前剥掉绝对路径。

    实测踩到：缓存把每张图的 `/Users/<用户名>/…/13.jpg` 也存了，被
    smoke 的「已跟踪文件不得含个人绝对路径」抓住。那个检查是防
    「别人 clone 后看到你的私有目录结构」，而缓存正是最容易漏的一处。
    路径本来就能从 slug 推出来，存它零收益、只剩风险。
    """
    out = dict(res)
    out["stills"] = []
    for s in res.get("stills") or []:
        t = dict(s)
        t.pop("path", None)
        out["stills"].append(t)
    if res.get("representative"):
        out["representative"] = [{k: v for k, v in x.items() if k != "path"}
                                 for x in res["representative"]]
    return out


def _aggregate(stills):
    if not stills:
        return {}
    def col(key):
        return [s[key] for s in stills if isinstance(s.get(key), (int, float))]
    keys = [("luminance", "明度"), ("contrast", "对比"), ("saturation", "饱和度"),
            ("warm_score", "暖度"), ("entropy", "信息熵"),
            ("edge_density", "边缘密度"), ("shadow_clip_pct", "暗部溢出"),
            ("highlight_clip_pct", "高光溢出")]
    metrics = {}
    for key, zh in keys:
        v = col(key)
        if not v:
            continue
        metrics[key] = {"zh": zh, "mean": _mean(v), "p10": _q(v, .1), "p50": _q(v, .5),
                        "p90": _q(v, .9), "min": round(min(v), 2), "max": round(max(v), 2)}
    ratios = {}
    for s in stills:
        r = s.get("ratio")
        if r:
            ratios[r] = ratios.get(r, 0) + 1
    frames, keys_, temps, orients, harmonies = {}, {}, {}, {}, {}
    for s in stills:
        _collect(frames, s.get("framing") or "未检出面部")
        _collect(keys_, s.get("key") or "—")
        _collect(temps, s.get("temperature") or "—")
        _collect(orients, s.get("orientation") or "—")
        _collect(harmonies, s.get("harmony") or "—")
    # 近全黑的帧（明度 < 15）单列出来：它们的主色接近纯黑，
    # 会把「饱和度均值」和「实测主色」往上带 —— 实测《潜行者》有一帧
    # 明度 6.2 却算出饱和度 0.78，主色 97.7% 是 #050202。那不是风格，
    # 是几乎全黑的画面里几个噪点像素的色相被放大。不标出来的话，
    # 读者会把被污染的均值当成风格特征。
    low = [{"file": s["file"], "index": s.get("index"), "luminance": s["luminance"],
            "saturation": s["saturation"]} for s in stills
           if isinstance(s.get("luminance"), (int, float)) and s["luminance"] < 15]
    return {
        "n": len(stills),
        "lowlight": low,
        "lowlight_note": ("以下 %d 张近全黑（明度 < 15）。它们的主色接近纯黑，"
                          "会**污染**饱和度均值与实测主色 —— 别把这些帧的色彩"
                          "当成风格特征。" % len(low)) if low else "",
        "metrics": metrics,
        "ratios": _top(ratios),
        "framing": _top(frames),
        "keys": _top(keys_),
        "temperatures": _top(temps),
        "orientations": _top(orients),
        "harmonies": _top(harmonies),
        "framing_note": ("人脸检测是 Haar，只认正面；风格化人脸会漏检，"
                         "「未检出面部」不等于没有脸"),
    }


def sample_stability(stills):
    """抽样稳定性：已量的那部分能不能代表全片？

    ## 为什么需要这个

    实测页上写着「已量 8 / 共 65 张」，读者接着就会问：**那这 8 张算得准吗**。
    与其让人猜，不如算给他看 —— 拿前 1/4 与全量的均值比。

    这不是形式主义：实测发现 film-grab 的画廊排列**没有强时间偏**
    （三部已下齐的片，前 8 张与全量的明度差 ≤4.5、饱和差 ≤0.03），
    所以「先下前 N 张」的抽样是可用的。但那是个**要验证的经验事实**，
    不是可以假设的东西 —— 样本一偏，页上所有数字都会跟着偏。
    """
    n = len(stills)
    if n < 10:
        return {"n": n, "verdict": "样本还太少，别下结论",
                "first_quarter_mean": None, "all_mean": None,
                "delta_luminance": None, "delta_saturation": None}
    k = max(1, n // 4)
    head, allv = stills[:k], stills
    fl = sum(s["luminance"] for s in head) / len(head)
    al = sum(s["luminance"] for s in allv) / len(allv)
    fs = sum(s["saturation"] for s in head) / len(head)
    as_ = sum(s["saturation"] for s in allv) / len(allv)
    dl, ds = fl - al, fs - as_
    # 阈值：明度差 15（0–255 量级）或饱和度差 0.08 就算有偏
    if abs(dl) > 15 or abs(ds) > 0.08:
        verdict = "有偏"
    else:
        verdict = "稳定"
    return {"n": n, "k": k, "verdict": verdict,
            "first_quarter_mean": round(fl, 1), "all_mean": round(al, 1),
            "delta_luminance": round(dl, 1), "delta_saturation": round(ds, 3),
            "note": ("前 %d 张与全量的对比。**稳定**说明「先下前 N 张」的抽样可用；"
                     "**有偏**说明画廊开头与整体差异明显，此时全片均值不可外推。"
                     "阈值：明度差 15 或饱和度差 0.08。" % k)}


def _measured_palette(stills, n=6):
    """全片实测主色：把每张的主色按面积加权合并，取前 n。

    这是「这部片实际用的是什么颜色」，与卡上**手写**的六色并列展示。
    """
    if not stills:
        return []
    from collections import defaultdict
    acc = defaultdict(float)
    for s in stills:
        for hx, pct in (s.get("dominant") or []):
            acc[hx.upper()] += float(pct)
    tot = sum(acc.values()) or 1.0
    # 先按面积排序取候选，再做一次贪心去重（避免六个色都是同一个色系）
    cand = sorted(acc.items(), key=lambda x: (-x[1], x[0]))[:40]
    out = []
    for hx, w in cand:
        if len(out) >= n:
            break
        if all(lab_distance(hx, o[0]) >= 12 for o in out):
            out.append((hx, round(100.0 * w / tot, 1)))
    for hx, w in cand:                       # 色相太单一凑不满时放宽要求
        if len(out) >= n:
            break
        if all(hx != o[0] for o in out):
            out.append((hx, round(100.0 * w / tot, 1)))
    return out[:n]


# ------------------------------------------------------------------ 比对
def palette_diff(written, measured):
    """手写配色 vs 实测配色：**只报告差异**。

    本库的规矩（AGENTS.md 里写着的）：数字是信号不是结论。实测一张油画的
    土色系会被配色匹配误判成「现实主义」，而它其实毫不相干。所以这个函数
    的全部职责是算出「差多远」并给一句判断，**没有修改权**。

    `written` / `measured` 都是 [(hex, name_or_pct), ...]。
    """
    w = [h for h, _ in written if h]
    m = [h for h, _ in measured if h]
    if not w or not m:
        return {"pairs": [], "距离": None, "distance": None,
                "verdict": "无法比对（缺一侧）"}
    pairs = []
    for hx in w:
        best, bd = None, 1e9
        for mx in m:
            d = lab_distance(hx, mx)
            if d < bd:
                best, bd = mx, d
        pairs.append({"written": hx, "nearest_measured": best,
                      "distance": round(bd, 1)})
    avg = sum(p["distance"] for p in pairs) / len(pairs)
    if avg <= CLOSE_DIST:
        verdict = "基本一致（实测色都在手写色附近）"
    elif avg >= FAR_DIST:
        verdict = "明显不一致（手写色与实测主色差得较远，值得回看两边）"
    else:
        verdict = "部分一致（同色系但有偏差）"
    # 同时给「距离」与「distance」两个键：中文键与库内页面的用词一致，
    # 英文键给程序用。重复一个键比让调用方猜哪个存在好。
    return {"pairs": pairs, "距离": round(avg, 1), "distance": round(avg, 1),
            "verdict": verdict}


# ------------------------------------------------------------------ 缓存
def _cache_path(slug):
    return os.path.join(DATA_DIR, "%s.json" % slug)


def save_measurements(slug, payload):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_cache_path(slug), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    return _cache_path(slug)


def load_measurements(slug):
    p = _cache_path(slug)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


# ------------------------------------------------------------------ CLI
def _main():
    import argparse
    ap = argparse.ArgumentParser(description="剧照全量实测")
    ap.add_argument("--slug", help="只量某一部片")
    ap.add_argument("--k", type=int, default=10, help="代表帧张数，默认 10")
    ap.add_argument("--no-cache", action="store_true", help="忽略缓存重算")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    import fv_core
    films = [f for f in fv_core.films() if not a.slug or f["slug"] == a.slug]
    if not films:
        print("没找到片子：%s" % a.slug)
        return 1

    def prog(slug, fn):
        sys.stderr.write(".")
        sys.stderr.flush()

    out = []
    for f in films:
        r = analyse_film(f, k=a.k, use_cache=not a.no_cache, progress=prog)
        out.append(r)
        print("\n%-38s 已量 %d / 共 %d 张（本地 %d，跳过 %d）"
              % (f["slug"], r["measured"], r["total_linked"],
                 r["local_files"], len(r["skipped"])), file=sys.stderr)
        if r["skipped"]:
            print("   跳过的：%s" % r["skipped"][:3], file=sys.stderr)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for r in out:
            ag = r["aggregate"]
            if not ag:
                print("%s：没有本地剧照，未测量" % r["slug"])
                continue
            print("\n%s · %s（已量 %d/%d）"
                  % (r["director_zh"], r["title_zh"], r["measured"], r["total_linked"]))
            print("  明度 %.1f（p10 %.1f – p90 %.1f）  饱和度 %.3f  对比 %.1f"
                  % (ag["metrics"]["luminance"]["mean"], ag["metrics"]["luminance"]["p10"],
                     ag["metrics"]["luminance"]["p90"], ag["metrics"]["saturation"]["mean"],
                     ag["metrics"]["contrast"]["mean"]))
            print("  实测主色：%s" % "、".join(h for h, _ in r["palette_measured"]))
            print("  手写配色：%s" % "、".join(r["palette_written"]))
            print("  比对：%s（平均 Lab 距离 %.1f）"
                  % (r["palette_diff"]["verdict"], r["palette_diff"]["distance"] or -1))
            print("  景别分布：%s" % "，".join("%s %d" % (k, v) for k, v in ag["framing"]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 still_analysis.py --slug villeneuve-dune",
          ["对本地剧照做客观测量，聚合成全片图景（不改写任何手写描述）。",
           "  --slug SLUG   只量某一部片",
           "  --k N         代表帧张数，默认 10",
           "  --no-cache    忽略缓存重算",
           "  --json        机器可读输出",
           "",
           "先跑 python3 fv_fetch.py --download --per 0 把剧照下到本地。"])
    sys.exit(_main())
