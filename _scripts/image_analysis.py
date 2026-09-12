#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_analysis.py —— 图片的客观测量（T1：只用 Pillow，零额外依赖）。

设计原则
    脚本做**确定性测量**，AI 做**语义判断**。
    这里算出来的都是可以复现的数字（明度、对比、色温、构图能量……），
    至于「这是哪个流派」交给看图的那个。

    实测过：配色距离算出一张油画调色板最接近「现实主义」，
    但那只是土色系重合，风格毫不相干。**数字只能当参考信号，不能当结论。**

维度
    明度  均值/标准差/中位/动态范围/高光暗部溢出/明暗基调
    对比  RMS 对比、Michelson 对比
    色彩  均值 RGB、色温倾向、平均饱和度、主色
    和谐  色相集中度 + 有效色相数 → 单色调/邻近/互补/多色相
    构图  三分法能量、水平/垂直对称性、中心 vs 边缘、地平线位置
    质感  边缘密度、局部方差、直方图熵（繁杂度）
    线条  梯度方向直方图 → 主导线条方向

用法
    python3 image_analysis.py <图片>              # 可读报告
    python3 image_analysis.py <图片> --json       # 机器可读
    python3 image_analysis.py <目录> --json       # 批量
"""

import argparse
import colorsys
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _pil():
    """在多个位置找 Pillow（与其他脚本一致的依赖发现逻辑）。"""
    for c in (os.environ.get("ARTVAULT_DEPS", ""),
              os.path.join(HERE, "vendor", "libs"),
              os.path.expanduser("~/.artvault/deps")):
        if c and os.path.isdir(c) and c not in sys.path:
            sys.path.insert(0, c)
    try:
        from PIL import Image, ImageFilter, ImageStat
        return Image, ImageFilter, ImageStat
    except ImportError:
        return None, None, None


Image, ImageFilter, ImageStat = _pil()

ANALYZE_SIZE = 256      # 分析用的缩放尺寸；再大只是变慢，指标几乎不变


# ------------------------------------------------------------------ 基础工具
def _hist_percentile(hist, total, frac):
    """从灰度直方图取分位数。"""
    target = total * frac
    acc = 0
    for i, n in enumerate(hist):
        acc += n
        if acc >= target:
            return i
    return 255


def _entropy(hist, total):
    """直方图熵：衡量画面的「繁杂度」。全平 = 0，满噪点 ≈ 8。"""
    h = 0.0
    for n in hist:
        if n:
            p = n / total
            h -= p * math.log2(p)
    return h


def _saturation(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return s, h * 360.0, v


# ------------------------------------------------------------------ 各维度
def _luminance(gray):
    st = ImageStat.Stat(gray)
    hist = gray.histogram()
    total = sum(hist)
    mean = st.mean[0]
    std = st.stddev[0]
    p05 = _hist_percentile(hist, total, 0.05)
    p50 = _hist_percentile(hist, total, 0.50)
    p95 = _hist_percentile(hist, total, 0.95)
    shadow_clip = sum(hist[:6]) / total * 100.0
    high_clip = sum(hist[250:]) / total * 100.0
    key = "低明调（暗）" if mean < 95 else ("高明调（亮）" if mean > 165 else "中间调")
    return {
        "mean": round(mean, 1), "std": round(std, 1), "median": p50,
        "p05": p05, "p95": p95,
        "dynamic_range": p95 - p05,
        "shadow_clip_pct": round(shadow_clip, 2),
        "highlight_clip_pct": round(high_clip, 2),
        "key": key,
    }


def _contrast(gray):
    st = ImageStat.Stat(gray)
    hist = gray.histogram()
    total = sum(hist)
    lo = _hist_percentile(hist, total, 0.02)
    hi = _hist_percentile(hist, total, 0.98)
    michelson = (hi - lo) / (hi + lo) if (hi + lo) else 0
    rms = st.stddev[0]
    level = "低对比" if rms < 35 else ("高对比" if rms > 70 else "中等对比")
    return {"rms": round(rms, 1), "michelson": round(michelson, 3), "level": level}


def _color(rgb):
    st = ImageStat.Stat(rgb)
    r, g, b = st.mean
    sat, _, _ = _saturation(r, g, b)
    # 色温倾向：暖色通道 vs 冷色通道。经验阈值 ±8 以内算中性
    warm = r - b
    temp = "暖" if warm > 8 else ("冷" if warm < -8 else "中性")
    # 平均饱和度用抽样算（比逐像素快，且更稳）
    small = rgb.resize((64, 64))
    sats = [_saturation(*px)[0] for px in small.getdata()]
    # 主色（量化到 4 级/通道）
    q = rgb.quantize(colors=6, method=2).convert("RGB")
    counts = {}
    for px in q.getdata():
        counts[px] = counts.get(px, 0) + 1
    total = sum(counts.values()) or 1
    dom = [{"hex": "#%02X%02X%02X" % c, "pct": round(v * 100.0 / total, 1)}
           for c, v in sorted(counts.items(), key=lambda x: -x[1])[:6]]
    return {
        "mean_rgb": [round(x) for x in (r, g, b)],
        "temperature": temp, "warm_score": round(warm, 1),
        "saturation": round(sum(sats) / len(sats), 3),
        "dominant": dom,
    }


def _harmony(rgb):
    """色彩和谐：用色相直方图上的圆统计量，不做峰值猜测定阈。

    踩过的坑：最早用量化主色算色相距离 —— 那几个色都接近画面均值色，
    于是任何图都被判成「邻近色」。改成「找色相峰 + 固定阈值」也不行：
    面积和饱和度互相打架（大津绘的米黄纸底压掉蓝和服，抬高饱和度地板
    又让色调主义整张归零）。最终改用两个稳的统计量：

      R   色相向量的圆集中度，0=色相均匀散布，1=单一色相
      eff 色相直方图的 exp(熵)，即「真正参与画面的色相个数」

    R 低而 eff 不高 = 两组色相对峙（互补），这是峰值法抓不到的情况。
    """
    small = rgb.resize((96, 96))
    N = 36                                  # 每 10° 一档
    hist = [0.0] * N
    n_sat = 0
    for r, g, b in small.getdata():
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        if s < 0.15 or v < 0.12:            # 忽略接近灰/黑的像素
            continue
        hist[int(h * N) % N] += s * s       # 按饱和度平方加权，压制低饱和底子
        n_sat += 1

    if n_sat < 60:
        return {"scheme": "单色 / 中性（画面几乎无色相）", "concentration": 0.0,
                "effective_hues": 0.0, "mean_hue": None, "mean_hue_name": "—",
                "colored_ratio": round(n_sat / float(96 * 96), 3)}

    tot = sum(hist) or 1.0
    sx = sum(hist[i] * math.cos(2 * math.pi * i / N) for i in range(N))
    sy = sum(hist[i] * math.sin(2 * math.pi * i / N) for i in range(N))
    R = math.hypot(sx, sy) / tot

    ent = 0.0
    for c in hist:
        if c > 0:
            pr = c / tot
            ent -= pr * math.log(pr)
    eff = math.exp(ent)

    mean_hue = (math.degrees(math.atan2(sy, sx)) % 360) if (sx or sy) else 0.0

    if eff < 2.5:
        scheme = "单色调（一个色相贯穿）"
    elif R < 0.45 and eff < 6.0:
        scheme = "互补 / 两组色相对峙"
    elif eff < 4.5:
        scheme = "邻近色（有限调色板）"
    elif eff < 9.0:
        scheme = "中等多色"
    else:
        scheme = "多色相（丰富或杂乱）"

    return {"scheme": scheme, "concentration": round(R, 2),
            "effective_hues": round(eff, 2), "mean_hue": round(mean_hue),
            "mean_hue_name": hue_name(mean_hue),
            "colored_ratio": round(n_sat / float(96 * 96), 3)}


HUE_NAMES = [(15, "红"), (45, "橙"), (70, "黄"), (95, "黄绿"), (150, "绿"),
             (190, "青"), (225, "蓝"), (260, "蓝紫"), (290, "紫"),
             (330, "品红"), (360, "红")]


def hue_name(h):
    for bound, name in HUE_NAMES:
        if h < bound:
            return name
    return "红"


def _composition(rgb, gray):
    w, h = gray.size
    st = ImageStat.Stat(gray)
    full = st.stddev[0] or 1

    # 三分法：四个交点的局部对比是否高于全图
    def energy(box):
        return ImageStat.Stat(gray.crop(box)).stddev[0]
    pts = [energy((0, 0, w // 3, h // 3)), energy((2 * w // 3, 0, w, h // 3)),
           energy((0, 2 * h // 3, w // 3, h)), energy((2 * w // 3, 2 * h // 3, w, h))]
    thirds = sum(pts) / 4

    # 对称性：与镜像混合后的标准差越小越对称
    def sym(transpose):
        m = rgb.transpose(transpose)
        return ImageStat.Stat(Image.blend(rgb, m, 0.5)).stddev
    sym_h = sum(sym(Image.FLIP_LEFT_RIGHT)) / 3
    sym_v = sum(sym(Image.FLIP_TOP_BOTTOM)) / 3

    # 中心 vs 边缘密度
    cx0, cy0, cx1, cy1 = w // 4, h // 4, 3 * w // 4, 3 * h // 4
    center = energy((cx0, cy0, cx1, cy1))
    edge_all = energy((0, 0, w, h))
    # 边缘带（去掉中心后剩下的一圈）
    return {
        "thirds_energy": round(thirds, 1),
        "thirds_vs_full": round(thirds / full, 2),
        "subject_on_thirds": thirds > full,
        "symmetry_h": round(sym_h, 1),
        "symmetry_v": round(sym_v, 1),
        "symmetry_hint": ("横向对称" if sym_h < 20 else ("纵向对称" if sym_v < 20 else "非对称")),
        "center_energy": round(center, 1),
        "overall_energy": round(edge_all, 1),
        "center_weight": round(center / (edge_all or 1), 2),
    }


def _texture(gray):
    edges = gray.filter(ImageFilter.FIND_EDGES)
    est = ImageStat.Stat(edges)
    hist = gray.histogram()
    total = sum(hist)
    # 局部方差：与 3x3 均值滤波的差
    blurred = gray.filter(ImageFilter.BoxBlur(1))
    diff = ImageStat.Stat(Image.blend(gray, blurred, 0.5)).stddev[0]
    ent = _entropy(hist, total)
    return {
        "edge_density": round(est.mean[0], 1),
        "local_variance": round(diff, 1),
        "entropy": round(ent, 2),
        "busyness": ("繁杂" if ent > 7.0 else ("适中" if ent > 5.5 else "简洁")),
    }


# Sobel 算子（PIL 自定义 kernel，零依赖做梯度方向）
_SOBEL_X = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
_SOBEL_Y = [-1, -2, -1, 0, 0, 0, 1, 2, 1]


def _lines(gray):
    """梯度方向直方图 → 主导线条方向。

    边缘的梯度方向垂直于线条走向，所以线条角度 = 梯度角 + 90°。
    """
    small = gray.resize((160, 160))
    kx = ImageFilter.Kernel((3, 3), _SOBEL_X, scale=1, offset=128)
    ky = ImageFilter.Kernel((3, 3), _SOBEL_Y, scale=1, offset=128)
    gx_img = small.filter(kx)
    gy_img = small.filter(ky)
    gx = list(gx_img.getdata())
    gy = list(gy_img.getdata())

    bins = [0] * 6                      # 0°,30°,60°,90°,120°,150°
    strong = 0
    for x, y in zip(gx, gy):
        dx, dy = x - 128, y - 128
        mag = math.hypot(dx, dy)
        if mag < 40:                    # 只统计强梯度
            continue
        strong += 1
        line_angle = (math.degrees(math.atan2(dy, dx)) + 90) % 180
        bins[min(int(line_angle // 30), 5)] += 1
    if not strong:
        return {"dominant_angle": None, "orientation": "无明显线条", "distribution": bins}
    peak = bins.index(max(bins))
    ang = peak * 30 + 15
    if ang < 30 or ang >= 150:
        ori = "以横线为主"
    elif 60 <= ang < 120:
        ori = "以竖线为主"
    else:
        ori = "以对角线为主"
    return {
        "dominant_angle": ang,
        "orientation": ori,
        "distribution": bins,
        "strong_edge_pct": round(strong / (160 * 160) * 100, 1),
    }


# ------------------------------------------------------------------ 主入口
def analyze(path):
    if Image is None:
        return {"file": path, "error": "未安装 Pillow（pip3 install --user Pillow）"}
    try:
        im = Image.open(path)
        w, h = im.size
        rgb = im.convert("RGB").resize((ANALYZE_SIZE, ANALYZE_SIZE))
    except Exception as e:
        return {"file": path, "error": "读取失败: %s" % str(e)[:60]}

    gray = rgb.convert("L")
    c = _color(rgb)
    r = {
        "file": os.path.basename(path),
        "path": path,
        "size": [w, h],
        "ratio": round(w / h, 3) if h else 0,
        "orientation": ("横构图" if w / h > 1.15 else ("竖构图" if h / w > 1.15 else "方构图")),
        "luminance": _luminance(gray),
        "contrast": _contrast(gray),
        "color": c,
        "harmony": _harmony(rgb),
        "composition": _composition(rgb, gray),
        "texture": _texture(gray),
        "lines": _lines(gray),
    }
    # 可选增强（人脸/直线/显著性）—— 需要 numpy + opencv，缺了就静默跳过。
    # 人脸必须在大图上跑，所以把原图 im 也传进去。
    try:
        import image_analysis_ext as _ext
        e = _ext.analyze_extended(im, rgb, gray)
        if e:
            r["extended"] = e
        r["extended_missing"] = _ext.missing_hint()
        r["extended_disabled"] = bool(getattr(_ext, "_DISABLED", False))
    except Exception as e:
        r["extended_error"] = str(e)[:80]
    try:
        im.close()
    except Exception:
        pass
    return r


def render(r, compact=False):
    """compact=True 时省掉 📷 头行和主色行，供调用方（如投递箱扫描）自己印这两项。"""
    if r.get("error"):
        return "  ✗ %s —— %s" % (r["file"], r["error"])
    L = []
    if not compact:
        L.append("📷 %s  %dx%d  %s  比例 %.2f" % (r["file"], r["size"][0], r["size"][1],
                                                 r["orientation"], r["ratio"]))
    lu, co, cl = r["luminance"], r["contrast"], r["color"]
    L.append("  明度  均值 %.1f 标准差 %.1f 中位 %d ｜ 动态范围 %d ｜ %s"
             % (lu["mean"], lu["std"], lu["median"], lu["dynamic_range"], lu["key"]))
    L.append("        高光溢出 %.2f%%  暗部溢出 %.2f%%" % (lu["highlight_clip_pct"], lu["shadow_clip_pct"]))
    L.append("  对比  RMS %.1f  Michelson %.3f  ｜ %s" % (co["rms"], co["michelson"], co["level"]))
    # 两个对比度打架时是个有意义的信号，不是 bug：
    # RMS 测整体明暗铺开程度，Michelson 测最亮/最暗的极差。
    # RMS 低而 Michelson 高 = 大面积暗调里只有小面积高光 —— 明暗对照法的签名。
    if co["rms"] < 45 and co["michelson"] > 0.85:
        L.append("        ↑ RMS 低但 Michelson 高 ＝ 大面积暗调 + 小面积高光，典型明暗对照（chiaroscuro）")
    L.append("  色彩  RGB %s  ｜ 色温 %s (%.0f) ｜ 饱和度 %.3f"
             % (cl["mean_rgb"], cl["temperature"], cl["warm_score"], cl["saturation"]))
    if not compact:
        L.append("        主色 " + "  ".join("%s %.0f%%" % (d["hex"], d["pct"]) for d in cl["dominant"]))
    hm = r["harmony"]
    L.append("  和谐  %s  (集中度 %.2f, 有效色相 %.2f, 主色相 %s %s°)"
             % (hm["scheme"], hm["concentration"], hm["effective_hues"],
                hm["mean_hue_name"], hm["mean_hue"]))
    cp = r["composition"]
    L.append("  构图  三分交点能量 %.1f (全图 %.1f) %s ｜ %s"
             % (cp["thirds_energy"], cp["overall_energy"],
                "✓ 主体偏交点" if cp["subject_on_thirds"] else "· 居中/均衡",
                cp["symmetry_hint"]))
    L.append("        中心/全图能量比 %.2f" % cp["center_weight"])
    tx = r["texture"]
    L.append("  质感  边缘密度 %.1f ｜ 局部方差 %.1f ｜ 熵 %.2f (%s)"
             % (tx["edge_density"], tx["local_variance"], tx["entropy"], tx["busyness"]))
    ln = r["lines"]
    L.append("  线条  %s%s  ｜ 强边缘占比 %.1f%%"
             % (ln["orientation"],
                ("  主导角 %d°" % ln["dominant_angle"]) if ln["dominant_angle"] is not None else "",
                ln.get("strong_edge_pct", 0)))
    if r.get("extended"):
        try:
            import image_analysis_ext as _ext
            L.extend(_ext.render_extended(r["extended"]))
        except Exception:
            pass
    elif r.get("extended_error"):
        L.append("  ⚠ 增强维度失败: %s" % r["extended_error"])
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="图片客观测量（零依赖）")
    ap.add_argument("target", nargs="+", help="图片或目录（可给多个）")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if Image is None:
        print("需要 Pillow：pip3 install --user Pillow")
        return 1

    targets = []
    for t in a.target:
        if os.path.isdir(t):
            for dp, _, fn in os.walk(t):
                for f in sorted(fn):
                    if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif")):
                        targets.append(os.path.join(dp, f))
        else:
            targets.append(t)

    results = [analyze(t) for t in targets]
    if a.json:
        print(json.dumps(results if len(results) > 1 else results[0],
                         ensure_ascii=False, indent=1))
    else:
        for r in results:
            print(render(r))
            print()
        # 增强维度缺失时明确说一声，别让用户以为「就这些」
        miss = results[0].get("extended_missing") if results else ""
        if miss:
            print("提示：%s" % miss)
            if not results[0].get("extended_disabled"):
                print("      装：pip3 install --target ./vendor/libs "
                      "numpy opencv-python-headless")
    return 0


if __name__ == "__main__":
    sys.exit(main())
