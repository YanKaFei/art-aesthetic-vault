#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contact_sheet.py —— 把一部片的关键帧拼成一张接触印相图，供**人眼精读**。

## 为什么需要它（而且不该省这一步）

实测页给出了数字：明度 65.9、饱和 0.31、暗部溢出 9%。这些**如实但冷**，
而「这部片到底长什么样」是眼睛的事 —— 数字能告诉你「偏暗」，
告诉不了你「暗得脏还是暗得神圣」。

所以流程是：**先量全部帧（客观）→ 选出代表帧 → 拼成一张印相图 → 人看图
→ 把看到的写回卡上的解读**。少了最后一步，交付的是一堆没人看过的数字。

一次能看 9 张（3×3）而不是一张一张读，是为了让**对比**发生 ——
风格恰恰在并置里才看得出来。

## 产物放哪

写到系统临时目录（不进仓库）。本地剧照本身已 gitignore，
印相图是**一次性的审查工具**，没有留在库里的必要。
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for _c in (os.environ.get("ARTVAULT_DEPS", ""),
           os.path.join(HERE, "vendor", "libs"),
           os.path.expanduser("~/.artvault/deps")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

TILE_W, TILE_H = 480, 270


def sheet(paths, out_path, cols=3, caption=None):
    """把若干张图拼成一张。失败返回 (None, 原因)。"""
    try:
        from PIL import Image, ImageDraw
    except Exception as e:
        return None, "需要 Pillow：%s" % str(e)[:60]
    if not paths:
        return None, "没有可用的图"
    rows = (len(paths) + cols - 1) // cols
    pad, cap_h = 6, (22 if caption else 0)
    W = cols * TILE_W + (cols + 1) * pad
    H = rows * (TILE_H + cap_h) + (rows + 1) * pad
    canvas = Image.new("RGB", (W, H), (18, 18, 20))
    draw = ImageDraw.Draw(canvas)
    for i, p in enumerate(paths):
        r, c = divmod(i, cols)
        x = pad + c * (TILE_W + pad)
        y = pad + r * (TILE_H + cap_h + pad)
        try:
            im = Image.open(p).convert("RGB")
        except Exception:
            continue
        # 等比缩放进格子（不裁切，保留原画幅比例）
        im.thumbnail((TILE_W, TILE_H))
        ox = x + (TILE_W - im.width) // 2
        oy = y + (TILE_H - im.height) // 2
        canvas.paste(im, (ox, oy))
        if caption:
            name = caption[i] if i < len(caption) else ""
            draw.text((x + 4, y + TILE_H + 4), name, fill=(200, 200, 200))
    canvas.save(out_path, quality=88)
    return out_path, None


def film_sheet(slug, out_path=None, k=9, which="representative"):
    """给一部片出一张印相图。`which` 可选 representative / first。"""
    import fv_core
    import still_analysis as SA
    f, _ = fv_core.resolve(slug)
    if not f:
        return None, "没找到片子：%s" % slug
    r = SA.load_measurements(f["slug"])
    if not r:
        r = SA.analyse_film(f)
    stills = r.get("stills") or []
    # ⚠ 缓存里**不存** path（写盘前剥离绝对路径，防泄漏到仓库）。
    # 所以这里必须自己补回来 —— 实测直接从缓存出图会 `s["path"]` KeyError，
    # 而缓存本身完好，没有任何检查会报错，只有出图时才炸。
    img_dir = os.path.join(SA.STILLS_DIR, f["slug"])
    for s in stills:
        if not s.get("path"):
            s["path"] = os.path.join(img_dir, s["file"])
    if not stills:
        return None, "这部片本地没有剧照"
    if which == "first":
        sel = stills[:k]
    else:
        idx = {x["index"] for x in (r.get("representative") or [])}
        sel = [s for s in stills if s["index"] in idx][:k] or stills[:k]
    tmpdir = tempfile.mkdtemp(prefix="artvault-sheet-")
    if not out_path:
        out_path = os.path.join(tmpdir, "%s-%s.jpg" % (f["slug"], which))
    caps = ["%02d 明%s 饱%.2f %s" % (s["index"], s["luminance"], s["saturation"],
                                    (s.get("framing") or "")[:6]) for s in sel]
    return sheet([s["path"] for s in sel], out_path, cols=3, caption=caps)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="拼接触印相图供人眼精读")
    ap.add_argument("slug", help="电影 slug 或中文名")
    ap.add_argument("--k", type=int, default=9)
    ap.add_argument("--first", action="store_true", help="取前 N 张而不是代表帧")
    ap.add_argument("--out", help="输出路径（默认写到系统临时目录）")
    a = ap.parse_args()
    p, why = film_sheet(a.slug, a.out, k=a.k,
                        which="first" if a.first else "representative")
    if not p:
        print("出图失败：%s" % why)
        return 1
    print(p)
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 contact_sheet.py villeneuve-dune",
          ["把一部片的关键帧拼成 3×3 接触印相图，供人眼精读。",
           "  slug          电影 slug 或中文名",
           "  --k N         拼几张，默认 9",
           "  --first       取前 N 张而不是代表帧",
           "  --out PATH    输出路径（默认写到系统临时目录）",
           "",
           "印相图是一次性的审查工具，不留在仓库里（剧照本身也已 gitignore）。"])
    sys.exit(main())
