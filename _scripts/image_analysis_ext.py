#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
image_analysis_ext.py —— 图片测量的**可选增强**维度。

为什么单独一个文件：`image_analysis.py` 是**纯 Pillow、零依赖**的，
那个文件里的七个维度永远可用。这里的三项需要 numpy / opencv，
不是每个用户都会装，所以分开放、**优雅降级**：

    装了 → 多三个维度
    没装 → 主脚本照常跑，只是没有这三项

三项各自独立（opencv 没装但 numpy 装了，显著性照样能算）。

维度
    人脸  检出的人脸数、最大脸占比、画面位置、景别推断（特写/半身/全身/群像）
    直线  霍夫变换检出的**真实直线**（已做共线合并去重），按方向分类
    显著性 谱残差法（Hou & Zhang, CVPR 2007）算视觉重心、集中度

和主脚本 `lines` 维度的区别：
    主脚本的 `lines` 用梯度方向直方图，测**整体的纹理走向趋势**
    （笔触方向、画面大势），不需要真的存在一条直线。
    这里的 `hough` 测**确实存在的线段**。印象派碎笔触会拉高主脚本的
    `lines`，但霍夫直线可能一条都检不出 —— 这正是两者的用处差异。

依赖直接用主脚本那套查找（vendor/libs / ARTVAULT_DEPS / ~/.artvault/deps）。
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FACE_SIZE = 800         # 人脸检测的长边尺寸，见下面「为什么不能缩到 256」
HOUGH_SIZE = 512        # 霍夫变换的工作尺寸

# 全局关掉增强维度（想看纯 Pillow 的结果、或想跑快一点时用）。
# 设了 ARTVAULT_NO_EXT=1 后，即使装了 numpy/opencv 也不加载。
_DISABLED = bool(os.environ.get("ARTVAULT_NO_EXT"))

for _c in (os.environ.get("ARTVAULT_DEPS", ""), os.path.join(HERE, "vendor", "libs"),
           os.path.join(HERE, "..", "..", ".artvault-deps"),
           os.path.expanduser("~/.artvault/deps")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

try:
    import numpy as np
except Exception:
    np = None

try:
    import cv2
except Exception:
    cv2 = None

if _DISABLED:
    np = None
    cv2 = None


def available():
    """返回可用的增强维度名。"""
    out = []
    if np is not None:
        out.append("saliency")
    if cv2 is not None:
        out += ["faces", "hough"]
    return out


# ------------------------------------------------------------ 人脸 / 景别
_CASCADE = None


def _cascade():
    global _CASCADE
    if _CASCADE is not None:
        return _CASCADE or None
    if cv2 is None:
        return None
    d = os.path.join(os.path.dirname(cv2.__file__), "data")
    for fn in ("haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_default.xml",
               "haarcascade_frontalface_alt.xml"):
        p = os.path.join(d, fn)
        if os.path.exists(p):
            c = cv2.CascadeClassifier(p)
            if not c.empty():
                _CASCADE = c
                return c
    _CASCADE = False
    return None


def analyze_faces(orig_im):
    """人脸检测 + 景别推断。

    景别对提示词是硬信息：`close-up portrait` / `half body` / `full body`
    / `group shot` 出图差别极大，而「画面里有几张脸」人眼容易数漏
    （群像里的侧脸、远景小脸）。

    **为什么不能缩到 256**：Haar 级联的基特征是 24x24，脸缩到 40px 就基本检不出。
    实测同一张 900px 肖像 —— 缩到 256/512 都是 0 张，用长边 800 才检出。
    人脸这一项必须在大图上跑，所以单独读原图，不复用主脚本的 256px 版本。

    **局限性要说清**：Haar 只认正面、且对绘画/风格化的脸不敏感。
    实测 8 张明确的人像里检出 6 张；漏掉的是侧面和光照怪异的那两张。
    所以这里是「检出 N 张」而不是「有 N 个人」。
    """
    if cv2 is None or np is None:
        return None
    casc = _cascade()
    if not casc:
        return None

    W, H = orig_im.size
    sc = FACE_SIZE / float(max(W, H))
    im = orig_im.convert("L")
    if sc < 1:
        im = im.resize((max(1, int(W * sc)), max(1, int(H * sc))))
    arr = np.array(im)
    h, w = arr.shape[:2]

    faces = casc.detectMultiScale(arr, scaleFactor=1.08, minNeighbors=5,
                                  minSize=(28, 28))
    note = "Haar 只认正面，绘画风格化人脸可能漏检"
    if len(faces) == 0:
        return {"count": 0, "framing": "未检出面部", "largest_face_pct": 0.0,
                "positions": [], "note": note}

    boxes = sorted(faces, key=lambda b: -(b[2] * b[3]))
    lx, ly, lw, lh = boxes[0]
    ratio = lh / float(h)

    if len(boxes) >= 3 and ratio < 0.18:
        framing = "群像 / 人群（多张较小的脸）"
    elif ratio > 0.45:
        framing = "特写（脸部占画面主体）"
    elif ratio > 0.22:
        framing = "半身 / 近景"
    elif ratio > 0.09:
        framing = "大半身 / 中景（可见到腰或膝）"
    else:
        framing = "远景 / 全身（人物很小）"

    pos = []
    for (x, y, fw, fh) in boxes[:6]:
        cx, cy = (x + fw / 2.0) / w, (y + fh / 2.0) / h
        pos.append({"x": round(cx, 2), "y": round(cy, 2),
                    "where": "%s%s" % ("左" if cx < 0.4 else ("右" if cx > 0.6 else "中"),
                                       "上" if cy < 0.4 else ("下" if cy > 0.6 else "中"))})
    return {"count": int(len(boxes)), "framing": framing,
            "largest_face_pct": round(ratio * 100, 1), "positions": pos, "note": note}


# ------------------------------------------------------------ 霍夫直线
def analyze_hough(orig_im):
    """霍夫变换检出**真实直线**，共线合并后按方向分类。

    踩过的坑：`threshold=45` 太低，HoughLinesP 会把同一条边反复检出，
    一张色调主义风景报出 112 段「斜线」，全是噪声。改成：

        threshold=80, minLineLength=0.25×短边, maxLineGap=3

    再做**共线合并**（角度差 <6° 且 rho 差 <10px 算同一条线）。
    实测结果语义正确：

        蒙德里安式构图  11 条，全是水平/垂直，斜向 0
        精确主义摩天楼  10 条，9 条垂直
        色调主义园林     2 条
        大津绘画卷      15 条，11 条水平（画卷格纹边框 + 接缝，真实存在）
    """
    if cv2 is None or np is None:
        return None
    im = orig_im.convert("L").resize((HOUGH_SIZE, HOUGH_SIZE))
    arr = np.array(im)
    edges = cv2.Canny(arr, 60, 160)
    min_len = int(HOUGH_SIZE * 0.25)
    segs = cv2.HoughLinesP(edges, 1, math.pi / 180.0, threshold=80,
                           minLineLength=min_len, maxLineGap=3)
    if segs is None or len(segs) == 0:
        return {"count": 0, "horizontal": 0, "vertical": 0, "diagonal": 0,
                "raw_segments": 0,
                "hint": "无明显直线（笔触型 / 有机形状）"}

    # 共线合并
    clusters = []
    for seg in segs:
        x1, y1, x2, y2 = seg[0]
        ang = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
        if ang > 90:
            ang -= 180                       # 归一到 (-90, 90]
        rho = x1 * math.cos(math.radians(ang)) + y1 * math.sin(math.radians(ang))
        for c in clusters:
            if min(abs(ang - c[0]), 180 - abs(ang - c[0])) < 6 and abs(rho - c[1]) < 10:
                c[2] += 1
                break
        else:
            clusters.append([ang, rho, 1])

    b = {"horizontal": 0, "vertical": 0, "diagonal": 0}
    for ang, _rho, _n in clusters:
        a = abs(ang)
        if a < 20:
            b["horizontal"] += 1
        elif a > 70:
            b["vertical"] += 1
        else:
            b["diagonal"] += 1

    top = max(b, key=b.get)
    zh = {"horizontal": "水平", "vertical": "垂直", "diagonal": "斜向"}[top]
    hint = "以%s直线为主（建筑感 / 透视 / 几何构图）" % zh
    return {"count": len(clusters), "raw_segments": int(len(segs)),
            "horizontal": b["horizontal"], "vertical": b["vertical"],
            "diagonal": b["diagonal"], "hint": hint}


# ------------------------------------------------------------ 显著性
def analyze_saliency(rgb_pil):
    """谱残差显著性（Hou & Zhang, CVPR 2007）—— 视觉重心与集中度。

    原理：自然图像的对数幅度谱大致平滑，减去平滑部分后剩下的「残差」
    对应视觉上意外/突出的区域。只需 numpy FFT，不需要 opencv。

    踩过的坑：最初用「显著分布的方差半径」当集中度，结果四张图全在
    0.67~0.83 —— 因为谱残差图是**边缘型**的，全图各处都有小峰，方差被
    它们撑满，没有区分度。改用两个真能量集中度的量：

      top5_mass   最显著的 5% 像素占了多少显著质量
      main_region 最大连通显著区占显著总面积的比例（需要 opencv 做连通域）

    实测 main_region：单人肖像 47.6%，繁杂版画 8.2%，均匀风景 5.4%。
    """
    if np is None:
        return None
    n = 128
    g = np.array(rgb_pil.convert("L").resize((n, n)), dtype=np.float64)
    F = np.fft.fft2(g)
    amp, phase = np.abs(F), np.angle(F)
    log_amp = np.log(amp + 1e-8)

    # 3x3 均值滤波平滑对数幅度谱（在频域直接做，不引入 scipy）
    pad = np.pad(log_amp, 1, mode="wrap")
    smooth = np.zeros_like(log_amp)
    for dy in range(3):
        for dx in range(3):
            smooth += pad[dy:dy + n, dx:dx + n] / 9.0

    sal = np.abs(np.fft.ifft2(np.exp(log_amp - smooth + 1j * phase))) ** 2
    for _ in range(2):                       # 两次 5 点模糊近似高斯
        sp = np.pad(sal, 1, mode="edge")
        sal = (sp[:-2, 1:-1] + sp[2:, 1:-1] + sp[1:-1, :-2] + sp[1:-1, 2:] + 4 * sal) / 8.0

    tot = float(sal.sum()) or 1.0
    flat = np.sort(sal.ravel())[::-1]
    top5 = float(flat[:max(1, int(len(flat) * 0.05))].sum()) / tot

    ys, xs = np.mgrid[0:n, 0:n]
    cx = float((sal * xs).sum() / tot) / n
    cy = float((sal * ys).sum() / tot) / n

    pk = int(np.argmax(sal))
    py, px = divmod(pk, n)
    px_n, py_n = px / float(n), py / float(n)
    thirds = [(1 / 3., 1 / 3.), (2 / 3., 1 / 3.), (1 / 3., 2 / 3.), (2 / 3., 2 / 3.)]
    on_thirds = min(math.hypot(px_n - tx, py_n - ty) for tx, ty in thirds) < 0.10

    main_region = None
    if cv2 is not None:
        m = (sal > sal.mean() * 3).astype(np.uint8)
        ncc, _lab, stats, _c = cv2.connectedComponentsWithStats(m, 8)
        if ncc > 1:
            areas = stats[1:, cv2.CC_STAT_AREA]
            if areas.sum() > 0:
                main_region = float(areas.max()) / float(areas.sum())

    if main_region is None:
        focus = "集中（无法算连通区，看 top5 质量）" if top5 > 0.45 else "较分散"
    elif main_region > 0.30:
        focus = "单一主体，重心明确"
    elif main_region > 0.15:
        focus = "主体较明确，但有次要元素"
    else:
        focus = "注意力分散（群像 / 满构图 / 装饰性图案）"

    return {"center_x": round(cx, 2), "center_y": round(cy, 2),
            "top5_mass": round(top5, 3),
            "main_region": round(main_region, 3) if main_region is not None else None,
            "focus": focus, "peak_on_thirds": bool(on_thirds),
            "peak": [round(px_n, 2), round(py_n, 2)]}


# ------------------------------------------------------------ 汇总
def analyze_extended(orig_im, rgb_pil, gray_pil):
    """跑所有可用的增强维度。任何一项失败都不影响其他项和主脚本。"""
    out = {}
    for key, fn, arg in (("faces", analyze_faces, orig_im),
                         ("hough", analyze_hough, orig_im),
                         ("saliency", analyze_saliency, rgb_pil)):
        try:
            v = fn(arg)
            if v is not None:
                out[key] = v
        except Exception as e:
            out[key] = {"error": str(e)[:70]}
    return out or None


def render_extended(ext, indent="  "):
    """渲染增强维度为可读文本行。"""
    L = []
    if not ext:
        return L
    f = ext.get("faces")
    if isinstance(f, dict) and "error" not in f:
        if f["count"] == 0:
            L.append("%s人脸  未检出面部" % indent)
        else:
            L.append("%s人脸  检出 %d 张，最大占画面高 %.1f%% ｜ %s"
                     % (indent, f["count"], f["largest_face_pct"], f["framing"]))
            if f.get("positions"):
                L.append("%s      位置 %s" % (indent, "  ".join(
                    "%s(%.2f,%.2f)" % (p["where"], p["x"], p["y"]) for p in f["positions"][:4])))
    h = ext.get("hough")
    if isinstance(h, dict) and "error" not in h:
        L.append("%s直线  霍夫检出 %d 条 (水平 %d / 垂直 %d / 斜向 %d) ｜ %s"
                 % (indent, h["count"], h["horizontal"], h["vertical"], h["diagonal"], h["hint"]))
    s = ext.get("saliency")
    if isinstance(s, dict) and "error" not in s:
        mr = s.get("main_region")
        L.append("%s显著  重心 (%.2f, %.2f) ｜ 最大显著区 %s ｜ %s%s"
                 % (indent, s["center_x"], s["center_y"],
                    ("%.0f%%" % (mr * 100)) if mr is not None else "n/a",
                    s["focus"],
                    "  ｜ 峰值在三分交点" if s["peak_on_thirds"] else ""))
    for k, v in ext.items():
        if isinstance(v, dict) and "error" in v:
            L.append("%s⚠ %s 失败: %s" % (indent, k, v["error"]))
    return L


def missing_hint():
    """增强维度不可用时给一句提示。全部可用则返回空串。"""
    if _DISABLED:
        return "增强维度已被 ARTVAULT_NO_EXT 主动关闭（不是缺依赖）"
    miss = []
    if np is None:
        miss.append("numpy")
    if cv2 is None:
        miss.append("opencv-python-headless")
    if not miss:
        return ""
    return "增强维度（人脸/直线/显著性）需要 %s，未安装则自动跳过" % " 和 ".join(miss)


if __name__ == "__main__":
    import argparse
    import json as _json
    from PIL import Image
    ap = argparse.ArgumentParser(description="可选增强维度（numpy / opencv）")
    ap.add_argument("target", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    have = available()
    print("可用增强维度:", ", ".join(have) or "无")
    if missing_hint():
        print("提示:", missing_hint())
    for t in a.target:
        im = Image.open(t)
        rgb = im.convert("RGB").resize((256, 256))
        ext = analyze_extended(im, rgb, rgb.convert("L"))
        if a.json:
            print(_json.dumps({os.path.basename(t): ext}, ensure_ascii=False, indent=1))
        else:
            print("📷 %s" % os.path.basename(t))
            for ln in render_extended(ext):
                print(ln)
