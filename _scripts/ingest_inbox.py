#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ingest_inbox.py —— 处理 pinterest/ 投递箱里的图。

工作方式：**你丢图，我（AI）拆解**。
脚本负责所有客观测量（尺寸、主色、感知哈希去重、配色匹配），
语义拆解（这张图是什么风格、像哪个流派）由看图的那个 AI 来做。

用法：
    python3 ingest_inbox.py --scan          # 扫描投递箱，输出清单 + 客观属性
    python3 ingest_inbox.py --scan --json   # 机器可读
    python3 ingest_inbox.py --archive       # 把已处理的图移到 _已归档/
    python3 ingest_inbox.py --palette-match 3   # 每张图给出配色最接近的 3 个流派

依赖（requests / Pillow）会自动在多个位置查找，见 _deps.py。
"""

import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
INBOX = os.path.join(VAULT, "pinterest")
ARCHIVE = os.path.join(INBOX, "_已归档")
MANIFEST = os.path.join(HERE, "_data", "inbox_manifest.json")

sys.path.insert(0, HERE)

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".tif", ".heic")


# ------------------------------------------------------------------ 依赖
def load_image_libs():
    """在多个位置找 Pillow。找不到就降级为「只列文件、不做图像分析」。"""
    candidates = [
        os.environ.get("ARTVAULT_DEPS", ""),
        os.path.join(HERE, "vendor", "libs"),
        os.path.join(HERE, "..", "..", ".artvault-deps"),
        os.path.expanduser("~/.artvault/deps"),
    ]
    for c in candidates:
        if c and os.path.isdir(c) and c not in sys.path:
            sys.path.insert(0, c)
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None


Image = load_image_libs()


# ------------------------------------------------------------------ 感知哈希
def dhash(img, size=8):
    """差分哈希：抗缩放、抗轻微调色，用于去重。返回 16 位十六进制串。"""
    g = img.convert("L").resize((size + 1, size), 1)
    px = list(g.getdata())
    bits = []
    for r in range(size):
        for c in range(size):
            left = px[r * (size + 1) + c]
            right = px[r * (size + 1) + c + 1]
            bits.append("1" if left > right else "0")
    return "%016x" % int("".join(bits), 2)


def hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


# ------------------------------------------------------------------ 主色
def dominant_colors(img, n=6):
    """量化到 4 级/通道后取频次最高的 n 色。够稳，也够快。"""
    small = img.convert("RGB").resize((160, 160))
    q = small.quantize(colors=n, method=2).convert("RGB")
    counts = {}
    for p in q.getdata():
        counts[p] = counts.get(p, 0) + 1
    total = sum(counts.values()) or 1
    top = sorted(counts.items(), key=lambda x: -x[1])[:n]
    return [{"hex": "#%02X%02X%02X" % c, "rgb": list(c),
             "pct": round(v * 100.0 / total, 1)} for c, v in top]


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _as_hex(x):
    """调色板元素的形态有三种：{'hex':...} / '#RRGGBB' / ('#RRGGBB', '名字')"""
    if isinstance(x, dict):
        return x["hex"]
    if isinstance(x, (tuple, list)):
        return x[0]
    return x


def palette_distance(pal_a, pal_b):
    """两个调色板之间的距离：对每个色取到对方最近色的距离，再平均。"""
    if not pal_a or not pal_b:
        return 1e9
    a = [hex_to_rgb(_as_hex(x)) for x in pal_a]
    b = [hex_to_rgb(_as_hex(x)) for x in pal_b]

    def nearest(c, pool):
        return min(sum((ci - pi) ** 2 for ci, pi in zip(c, p)) ** 0.5 for p in pool)

    d1 = sum(nearest(c, b) for c in a) / len(a)
    d2 = sum(nearest(c, a) for c in b) / len(b)
    return (d1 + d2) / 2


# ------------------------------------------------------------------ 扫描
def scan_new():
    if not os.path.isdir(INBOX):
        return []
    out = []
    for fn in sorted(os.listdir(INBOX)):
        p = os.path.join(INBOX, fn)
        if not os.path.isfile(p) or fn.startswith("."):
            continue
        if not fn.lower().endswith(EXTS):
            continue
        rec = {"file": fn, "path": p, "size_kb": round(os.path.getsize(p) / 1024, 1),
               "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(p)))}
        if Image:
            try:
                im = Image.open(p)
                w, h = im.size
                rec.update({"width": w, "height": h,
                            "ratio": round(w / h, 3) if h else 0,
                            "orientation": ("横构图" if w / h > 1.15 else
                                            "竖构图" if h / w > 1.15 else "方构图"),
                            "mode": im.mode, "format": im.format,
                            "dhash": dhash(im),
                            "colors": dominant_colors(im)})
                im.close()
            except Exception as e:
                rec["error"] = "读取失败: %s" % str(e)[:60]
        else:
            rec["error"] = "未安装 Pillow，只能列出文件"
        out.append(rec)
    return out


def find_duplicates(recs):
    dups = []
    for i in range(len(recs)):
        for j in range(i + 1, len(recs)):
            a, b = recs[i].get("dhash"), recs[j].get("dhash")
            if a and b and hamming(a, b) <= 6:
                dups.append((recs[i]["file"], recs[j]["file"], hamming(a, b)))
    return dups


def match_palette(recs, topn=3):
    """给每张图找出配色最接近的流派卡（客观信号，供 AI 参考）"""
    try:
        import artvault_core as A
    except Exception:
        return {}
    cards = A.cards()
    res = {}
    for r in recs:
        if not r.get("colors"):
            continue
        scored = []
        for c in cards:
            d = palette_distance(r["colors"], c["palette"])
            scored.append((d, c))
        scored.sort(key=lambda x: x[0])
        res[r["file"]] = [{"slug": c["slug"], "name": c["name_zh"],
                           "distance": round(d, 1), "category": c["category"]}
                          for d, c in scored[:topn]]
    return res


def archive(recs):
    os.makedirs(ARCHIVE, exist_ok=True)
    moved = 0
    for r in recs:
        src, dst = r["path"], os.path.join(ARCHIVE, r["file"])
        if os.path.exists(src):
            base, ext = os.path.splitext(r["file"])
            k = 1
            while os.path.exists(dst):
                dst = os.path.join(ARCHIVE, "%s-%d%s" % (base, k, ext)); k += 1
            shutil.move(src, dst)
            moved += 1
    return moved


def render(recs, dups, matches):
    L = ["投递箱：共 %d 张待处理" % len(recs), ""]
    for r in recs:
        L.append("─" * 62)
        L.append("📷 %s   (%.0f KB, %s)" % (r["file"], r["size_kb"], r["mtime"]))
        if r.get("error"):
            L.append("   ⚠ %s" % r["error"]); continue
        L.append("   尺寸 %dx%d  %s  比例 %.2f" % (r["width"], r["height"], r["orientation"], r["ratio"]))
        L.append("   主色 " + "  ".join("%s %.0f%%" % (c["hex"], c["pct"]) for c in r["colors"]))
        L.append("   感知哈希 %s" % r["dhash"])
        if r["file"] in matches:
            L.append("   配色最近的流派：")
            for m in matches[r["file"]]:
                L.append("      %-10s %-8s 距离 %.1f  (%s)" % (m["slug"], m["name"], m["distance"], m["category"]))
    if dups:
        L.append(""); L.append("可能的重复（汉明距离 ≤6）：")
        for a, b, d in dups:
            L.append("   %s  ≈  %s   (距离 %d)" % (a, b, d))
    L.append("")
    L.append("下一步：让 AI 逐张看图（read_image），按七层拆解，写入 20-我的提示词/。")
    L.append("拆完执行：python3 ingest_inbox.py --archive")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--palette-match", type=int, default=3, metavar="N")
    a = ap.parse_args()

    if a.archive:
        recs = scan_new()
        if not recs:
            print("投递箱是空的，没有要归档的。"); return 0
        n = archive(recs)
        print("已归档 %d 张 → pinterest/_已归档/" % n)
        return 0

    recs = scan_new()
    if not recs:
        print("投递箱是空的。把图片放进 pinterest/ 再来。")
        return 0
    dups = find_duplicates(recs)
    matches = match_palette(recs, a.palette_match) if a.palette_match else {}

    os.makedirs(os.path.dirname(MANIFEST), exist_ok=True)
    json.dump({"scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
               "count": len(recs), "items": recs,
               "duplicates": dups, "palette_matches": matches},
              open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.json:
        print(json.dumps({"items": recs, "duplicates": dups, "palette_matches": matches},
                         ensure_ascii=False, indent=1))
    else:
        print(render(recs, dups, matches))
        if not Image:
            print("\n⚠ 没有 Pillow，只能列文件。安装：pip3 install --user Pillow")
        print("\n清单已写入 _scripts/_data/inbox_manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
