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


def load_analyzer():
    """把 image_analysis 的七个客观维度接进来。找不到就跳过，不影响扫描。"""
    try:
        import image_analysis
        return image_analysis
    except Exception:
        return None


_CLIP_MATCH = None


def load_clip_match():
    """把 CLIP 的「最像哪个流派」接进来。

    模型没下（clip_embed.available() 返回原因字符串）就返回 None，
    扫描照常进行 —— 这一项是增强，不是必需。
    """
    global _CLIP_MATCH
    if _CLIP_MATCH is None:
        try:
            import clip_embed
            import clip_match
            _CLIP_MATCH = clip_match if clip_embed.available() is None else False
        except Exception:
            _CLIP_MATCH = False
    return _CLIP_MATCH or None


_ANALYZER = None


def render_analysis(r):
    """渲染单个分析结果（省掉调用方已经印过的头行和主色行）。"""
    global _ANALYZER
    if _ANALYZER is None:
        _ANALYZER = load_analyzer()
    return _ANALYZER.render(r, compact=True) if _ANALYZER else ""


# ------------------------------------------------------------------ 扫描
def scan_new(analyze=True):
    if not os.path.isdir(INBOX):
        return []
    analyzer = load_analyzer() if analyze else None
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
            if analyzer and not rec.get("error"):
                try:
                    rec["analysis"] = analyzer.analyze(p)
                except Exception as e:
                    rec["analysis_error"] = str(e)[:80]
        else:
            rec["error"] = "未安装 Pillow，只能列出文件"
        out.append(rec)

    # CLIP 建议流派：一次算好文本矩阵与质心，再批量编码所有新图。
    # 这是投递箱工作流里最有用的信号 —— 但它只有约四成准确率
    # （实测 Top-1 39.1%，随机基准 1.4%），所以输出里标成「建议」。
    # 空投递箱不必加载 CLIP —— 文本矩阵要 5.8 秒，没图可匹配就是白等
    cm = load_clip_match() if (analyze and out) else None
    if cm:
        try:
            sug = cm.suggest([r["path"] for r in out if not r.get("error")])
            for r in out:
                if r["path"] in sug:
                    r["suggested"] = [{"slug": s_, "name": n, "score": round(sc, 3)}
                                      for s_, n, sc in sug[r["path"]]]
        except Exception as e:
            for r in out:
                r["suggest_error"] = str(e)[:70]
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


def archive(recs, verbose=True):
    """把处理完的图从投递箱移走，**并记进本地图库的待归档清单**。

    原来的做法是移到 pinterest/_已归档/ —— 结果图仍留在投递箱区域，
    而投递箱是刻意排除在图谱外的，于是「处理完了」等于「从图谱里消失了」。
    现在改为移进 99-附件/images-local/<流派>/，并写进 local_library.json，
    跑一次 build_vault.py 就会生成 15-我的图库/ 的笔记、链回流派卡 ——
    这些图从此和权威库挂在同一张图谱上。

    没指定流派的图进 99-附件/images-local/_未归类/，在总览页里能看到、等着归。
    """
    # 取 CLIP 建议：优先读 --scan 写下的清单（不必重跑一遍分析）
    sug_by_file = {}
    if os.path.exists(MANIFEST):
        try:
            for it in (json.load(open(MANIFEST, encoding="utf-8")).get("items") or []):
                if it.get("suggested"):
                    sug_by_file[it["file"]] = it["suggested"]
        except Exception:
            pass

    man_path = os.path.join(HERE, "_data", "local_library.json")
    man = {"items": {}}
    if os.path.exists(man_path):
        try:
            man = json.load(open(man_path, encoding="utf-8"))
            man.setdefault("items", {})
        except Exception:
            pass
    moved, unmoved = 0, 0
    for r in recs:
        src = r["path"]
        if not os.path.exists(src):
            continue
        # 用 CLIP 的第一建议作为去处；没有建议就进 _未归类
        sug = r.get("suggested") or sug_by_file.get(r["file"]) or []
        slug = (sug[0].get("slug") if sug else None) or "_未归类"
        dest_dir = os.path.join(VAULT, "99-附件", "images-local", slug)
        os.makedirs(dest_dir, exist_ok=True)
        dst = os.path.join(dest_dir, r["file"])
        base, ext = os.path.splitext(r["file"])
        k = 1
        while os.path.exists(dst):
            dst = os.path.join(dest_dir, "%s-%d%s" % (base, k, ext)); k += 1
        try:
            shutil.move(src, dst)
        except Exception:
            continue
        rel = os.path.relpath(dst, VAULT).replace(os.sep, "/")
        man["items"][rel] = {
            "movement": slug,
            "title": base,
            "source": "pinterest 投递箱",
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": (r.get("analysis") and {
                "明度": (r["analysis"].get("luminance") or {}).get("key"),
                "饱和度": (r["analysis"].get("color") or {}).get("saturation"),
                "繁杂度": (r["analysis"].get("texture") or {}).get("busyness"),
            }) or None,
        }
        moved += 1
        if slug == "_未归类":
            unmoved += 1

    # 清掉已经空掉的投递箱目录
    os.makedirs(ARCHIVE, exist_ok=True)
    try:
        json.dump(man, open(man_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    except Exception:
        pass
    if verbose:
        print("已归档 %d 张 → 99-附件/images-local/（按 CLIP 建议分流派）" % moved)
        if unmoved:
            print("  其中 %d 张进了 _未归类/ —— 建议没把握，等着你归" % unmoved)
        print("  下一步：python3 build_vault.py   （生成 15-我的图库/ 的笔记并链回流派卡）")
        print("  要改归类：python3 scan_local.py --list  然后 --file <编号> --to <流派>")
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
        if r.get("analysis"):
            # 客观测量，供拆解时参考 —— 数字是信号不是结论，最终判断靠看图
            for ln in render_analysis(r["analysis"]).split("\n"):
                L.append("   " + ln)
        elif r.get("analysis_error"):
            L.append("   ⚠ 维度分析失败: %s" % r["analysis_error"])
        if r.get("suggested"):
            L.append("   CLIP 建议流派：")
            for m in r["suggested"]:
                L.append("      %-16s %-18s 融合分 %.2f" % (m["slug"], m["name"], m["score"]))
        elif r.get("suggest_error"):
            L.append("   ⚠ CLIP 建议失败: %s" % r["suggest_error"])
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
    ap.add_argument("--no-analysis", action="store_true",
                    help="跳过七维度客观测量（只想快速列文件时用）")
    a = ap.parse_args()

    if a.archive:
        recs = scan_new(analyze=False)
        if not recs:
            print("投递箱是空的，没有要归档的。"); return 0
        archive(recs)          # archive() 自己会说明去了哪
        return 0

    recs = scan_new(analyze=not a.no_analysis)
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
