#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_assets.py —— 生成 README 的配图（头图 / 七层示意 / 四条轴 / 总览网格）。

用法
    python3 readme_assets.py            # 全部重建，并写 MANIFEST.txt
    python3 readme_assets.py --list     # 只列出用了哪些源图，不写文件
    python3 readme_assets.py --check    # 只核对：磁盘上的图与清单是否一致

产物落在 99-attachments/readme/，四份 README（中/英/日/法）共用同一批图。

## 为什么图里没有中文

README 有四份，图只有一份。图里写中文，英日法三份就得各配一套图 —— 四套图
迟早会漂移，而「四份 README 说的是同一件事」正是这个仓库要守的东西。
所以图只承担**语言无关**的信息：画面的样子、层的结构、流派的英文名
（英文名本来就是库里卡片的 slug，中文名只是它的译名）。
正文里该说的话，交给四份 README 各自的文字。

## 为什么是脚本而不是手工拼图

和库里其它生成物同一条理由：手工拼出来的图，换台机器就重建不出来，
下次改版还得再拼一遍，而「重建不出来」的图没人敢删、也没人敢改。
这个脚本只依赖 Pillow，输出确定 —— 同样输入永远同样字节（tests/readme_i18n_test.py
里有一步会真的重画一遍逐字节比）。

## 只用品库里的图

源图一律走 `only_tracked()`：发布出去的配图必须来自**别人 clone 也拿得到**的
文件。这条纪律在 README 的统计数字上已经吃过一次亏（写了 654 张，克隆下来
只有 442 张），配图同理 —— 引用一张只在作者机上的图，读者看到的就是破图。
"""

import argparse
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)

for _c in (os.environ.get("ARTVAULT_DEPS", ""),
           os.path.join(HERE, "vendor", "libs"),
           os.path.expanduser("~/.artvault/deps")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)

# Pillow 是**可选**的，而且这个 import 必须在 argparse 之后才发作。
#
# 第一版在这里 `sys.exit(1)`，于是没装 Pillow 的机器上连 `--help` 都退出 1 ——
# 实测被 CI 的「每个入口的 --help 必须是安全的」抓住（同 image_analysis_ext.py
# 当年那个 traceback 是同一类问题）。读者拿到陌生仓库第一个试的就是 `--help`。
#
# 而且 `--list` 与 `--check` 本来就不需要 Pillow：前者只列源图路径，后者只比
# sha256。把 import 挪到真正要画图的那一步，这两条路在没 Pillow 的机器上照常可用。
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:                                    # pragma: no cover
    Image = ImageDraw = ImageFont = None
    _PIL_ERR = str(e)
else:
    _PIL_ERR = None


def need_pil():
    """要画图了才检查 Pillow。缺就说明白，并指出哪两条路照样能走。"""
    if _PIL_ERR is None:
        return
    print("需要 Pillow：%s" % _PIL_ERR)
    print("  pip3 install Pillow    或   ARTVAULT_DEPS=<含有 Pillow 的目录>")
    print("  （--list 与 --check 不需要 Pillow，可以照常跑）")
    sys.exit(1)

OUT_DIR = os.path.join(VAULT, "99-attachments", "readme")
IMAGES = os.path.join(VAULT, "99-attachments", "images")
STILLS = os.path.join(VAULT, "99-attachments", "images-films")
MANIFEST = "MANIFEST.txt"

# ---------------------------------------------------------------- 配色
# 深色是为了「放哪都对」：GitHub 亮色与暗色主题下，深色横幅都读得清，
# 而浅色横幅在暗色主题里会变成一块刺眼的白。
BG = (11, 11, 15)
PANEL = (21, 21, 27)
PANEL2 = (16, 16, 21)
LINE = (40, 40, 50)
INK = (244, 241, 234)
DIM = (146, 142, 134)
FAINT = (92, 89, 84)
GOLD = (201, 166, 79)
GOLD_DIM = (128, 106, 52)
COOL = (110, 139, 181)

# ---------------------------------------------------------------- 字体
_FONTS = (
    ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "serif_bold"),
    ("/System/Library/Fonts/Supplemental/Georgia.ttf", "serif"),
    ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "sans_bold"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "sans"),
    ("/System/Library/Fonts/HelveticaNeue.ttc", "sans"),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", "cjk"),
    ("/Library/Fonts/Arial Unicode.ttf", "cjk"),
)
_CACHE = {}


def font(role, size):
    """取字体。**一台机器上缺字体就报错，不退回默认位图字体。**

    这里原来最后会 `ImageFont.load_default()` 兜底 —— 听起来是「优雅降级」，
    实际是把一个必须被发现的错误变成了看不见的错误：

      · 图的**字节取决于字体**，「同一份源码重建出同一张图」这条承诺，
        在缺字体的机器上会静默失效；
      · 而校验只在装了 Pillow 的机器上跑 —— 恰好就是字体齐全的那一台，
        所以谁也不会发现，直到有人在别处重建出一套不一样的图并提交上去。

    候选字体都是 macOS 自带的。在没有它们的机器上，正确的行为是**停下来说明**，
    而不是画一张看起来没问题的图。
    """
    key = (role, size)
    if key in _CACHE:
        return _CACHE[key]
    order = [p for p, r in _FONTS if r == role] + [p for p, r in _FONTS if r != role]
    for p in order:
        if not os.path.exists(p):
            continue
        try:
            f = ImageFont.truetype(p, size)
            _CACHE[key] = f
            return f
        except Exception:
            continue
    raise RuntimeError(
        "找不到可用的字体，拒绝生成配图 —— 图的字节取决于字体，"
        "退回 Pillow 默认位图字体会让「配图可复现」静默失效。\n"
        "需要下面任一个（本脚本的选图与排版按它们的度量调过）：\n  %s\n"
        "如果只是想核对已有配图，用 `python3 readme_assets.py --check`，它不需要字体。"
        % "\n  ".join(p for p, _r in _FONTS))


# ---------------------------------------------------------------- 绘制小工具
def tracked_text(draw, xy, s, f, fill, tracking=0.0):
    """带字距的文本。PIL 没有 letter-spacing，而「高级感」有一半来自字距。"""
    x, y = xy
    for ch in s:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def rounded(im, radius):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, im.size[0] - 1, im.size[1] - 1], radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def cover(im, w, h):
    """等比缩放并居中裁切到 w×h（cover 语义）。"""
    im = im.convert("RGB")
    iw, ih = im.size
    s = max(w / float(iw), h / float(ih))
    nw, nh = max(w, int(iw * s + 0.5)), max(h, int(ih * s + 0.5))
    im = im.resize((nw, nh), Image.LANCZOS)
    l, t = (nw - w) // 2, (nh - h) // 2
    return im.crop((l, t, l + w, t + h))


def load(path, w, h):
    if not path or not os.path.isfile(path):
        return None
    try:
        with Image.open(path) as im:
            return cover(im, w, h)
    except Exception:
        return None


IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")
_TRACKED = None


def tracked_set():
    """`99-attachments/` 下被 git 跟踪的文件（一次问完，别每张图问一遍 git）。"""
    global _TRACKED
    if _TRACKED is None:
        try:
            r = subprocess.run(["git", "-C", VAULT, "ls-files", "-z", "--",
                                "99-attachments"],
                               capture_output=True, text=True, timeout=60)
            _TRACKED = set(p for p in r.stdout.split("\0") if p)
        except Exception:
            _TRACKED = set()             # 不是 git 仓库 → 退化为「不做跟踪检查」
    return _TRACKED


def pick(dirpath, index=1):
    """取目录里第 index 张**被 git 跟踪的**图（按文件名排序，1 起）。

    只从被跟踪的文件里挑，是因为剧照目录里同时躺着两批东西：随仓库发布的
    代表帧，和只留本地的全量语料（约 160 MB，gitignore 掉了）。按文件名
    取第 1 张，取到的正是**没发布**的那一张 —— README 上就会出现一张
    只有作者看得见的破图。这个坑第一次跑就踩到了，所以在这里堵住。
    """
    if not os.path.isdir(dirpath):
        return None
    rel_dir = os.path.relpath(dirpath, VAULT).replace(os.sep, "/")
    fs = sorted(f for f in os.listdir(dirpath) if f.lower().endswith(IMG_EXT))
    have = tracked_set()
    ok = [f for f in fs if not have or ("%s/%s" % (rel_dir, f)) in have]
    if not ok:
        return None
    return os.path.join(dirpath, ok[min(index, len(ok)) - 1])


# ---------------------------------------------------------------- 内容清单
AXIS_OF = {"mv": "ART MOVEMENT", "hw": "HAND-DRAWN", "fm": "FILM"}


def movement(slug, index=1):
    """流派图：按文件名排序取第 index 张（`01-...`、`02-...`）。"""
    return pick(os.path.join(IMAGES, slug), index)


def handraw(n):
    """手绘风格没有 slug 目录，直接点编号。"""
    return named(os.path.join(IMAGES, "handraw"), "handraw-%03d.webp" % n)


def still(slug, frame):
    """电影剧照：按**帧号**取（`47` → `47.jpg`）。

    这里原来复用了「第 N 张」的序号语义，于是 `still(slug, 47)` 在只有 6 张
    已发布剧照的目录里被 `min()` 悄悄夹到第 6 张 —— 我要的是 47.jpg，拿到的
    是 50.jpg，而且不报错。**默默换一张图比报错难查得多**（你只会觉得「这张
    好像不太对」）。所以改成按帧号取，取不到就返回 None，缺口在图上直接看得见。
    """
    return named(os.path.join(STILLS, slug), "%02d.jpg" % int(frame))


def named(dirpath, name):
    """取目录里指定文件名的那一张，且必须已被 git 跟踪。"""
    p = os.path.join(dirpath, name)
    if not os.path.exists(p):
        return None
    rel = os.path.relpath(p, VAULT).replace(os.sep, "/")
    have = tracked_set()
    return p if (not have or rel in have) else None


def hero_items():
    """头图：6 格，画派 / 手绘 / 电影各占两格 —— 一眼就是「这库不止有画」。

    选图有两条硬要求，都是跑完看图才发现的：
      · **不能带大字水印**（有些手绘参考图上印着风格名的大标题，缩到头图尺寸
        只剩几个被切断的字）；
      · **裁成竖幅之后还认得出**（居中裁切会切掉两侧，中心是空的图会变成一片灰）。
    """
    return [movement("baroque", 1), movement("ukiyo-e", 2),
            still("kurosawa-ran", 38), still("villeneuve-blade-runner-2049", 47),
            handraw(243), handraw(247)]


AXIS_STRIPS = {
    "axis-1-movements": [movement("baroque", 1), movement("ukiyo-e", 2),
                         movement("renaissance", 3)],
    "axis-2-handraw": [handraw(26), handraw(243), handraw(256)],
    "axis-3-films": [still("villeneuve-blade-runner-2049", 47),
                     still("kurosawa-ran", 38),
                     still("wong-kar-wai-in-the-mood-for-love", 34)],
}


GALLERY = [
    (movement("baroque", 3), "Baroque", "mv"),
    (movement("renaissance", 3), "Renaissance", "mv"),
    (movement("romanticism", 4), "Romanticism", "mv"),
    (movement("impressionism", 2), "Impressionism", "mv"),
    (movement("ukiyo-e", 2), "Ukiyo-e", "mv"),
    (movement("persian-miniature", 1), "Persian Miniature", "mv"),
    (movement("dunhuang-murals", 1), "Dunhuang Murals", "mv"),
    (movement("constructivism", 1), "Constructivism", "mv"),
    (handraw(26), "Pen & Wash Narrative", "hw"),
    (handraw(223), "Flat Editorial Portrait", "hw"),
    (handraw(243), "Painterly Animal Study", "hw"),
    (handraw(247), "Flat Character Portrait", "hw"),
    (handraw(252), "Flat Colour Storybook", "hw"),
    (handraw(256), "Soft Landscape Illustration", "hw"),
    (still("villeneuve-blade-runner-2049", 47), "Blade Runner 2049", "fm"),
    (still("wong-kar-wai-in-the-mood-for-love", 34), "In the Mood for Love", "fm"),
    (still("kurosawa-ran", 38), "Ran", "fm"),
    (still("miyazaki-spirited-away", 4), "Spirited Away", "fm"),
    (still("kon-paprika", 5), "Paprika", "fm"),
    (still("bong-parasite", 13), "Parasite", "fm"),
    (still("anime-akira", 19), "Akira", "fm"),
    (still("anime-ghost-in-the-shell", 3), "Ghost in the Shell", "fm"),
    (still("fincher-se7en", 24), "Se7en", "fm"),
    (still("park-chan-wook-oldboy", 21), "Oldboy", "fm"),
]


# ---------------------------------------------------------------- 1. 头图
def draw_hero(out):
    W, H, N, GAP = 2080, 520, 6, 6
    tw = (W - GAP * (N - 1)) // N
    im = Image.new("RGB", (W, H), BG)
    tips = hero_items()
    d = ImageDraw.Draw(im)
    x = 0
    for i in range(N):
        p = tips[i] if i < len(tips) else None
        tile = load(p, tw, H) if p else None
        if tile is None:
            tile = Image.new("RGB", (tw, H), PANEL)
            ImageDraw.Draw(tile).line([(0, 0), (tw, H)], fill=LINE, width=1)
        im.paste(tile, (x, 0))
        if i:
            d.line([(x - GAP // 2, 0), (x - GAP // 2, H)], fill=BG, width=GAP)
        x += tw + GAP
    # 上下各压一道渐隐，让照片带「被设计过」的收边，而不是一沓图直接摆着
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dv = ImageDraw.Draw(veil)
    band = 96
    for i in range(band):
        a = int(46 * (1 - i / float(band)))
        dv.line([(0, i), (W, i)], fill=(BG[0], BG[1], BG[2], a))
        dv.line([(0, H - 1 - i), (W, H - 1 - i)], fill=(BG[0], BG[1], BG[2], a))
    im = Image.alpha_composite(im.convert("RGBA"), veil).convert("RGB")
    ImageDraw.Draw(im).rectangle([0, 0, W - 1, H - 1], outline=(32, 32, 40), width=2)
    im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return im.size


# ---------------------------------------------------------------- 2. 七层示意
LAYER_ROWS = (
    ("01", "STYLE", "The movement's own vocabulary - what makes it look like itself."),
    ("02", "LIGHTING", "Source, direction, contrast, shadow. The highest-leverage layer."),
    ("03", "COLOR", "The palette, named as hex. What dominates, what accents."),
    ("04", "COMPOSITION", "Camera position, framing, geometry, symmetry."),
    ("05", "MEDIUM", "Surface and material - oil on canvas, ink on paper, celluloid."),
    ("06", "MOOD", "The emotional register the image should land in."),
    ("07", "CAMERA", "Lens, angle, shot size, depth of field."),
)


def draw_layers(out):
    W = 2080
    pad = 72
    head_h = 250
    row_h = 118
    foot_h = 104
    H = head_h + row_h * len(LAYER_ROWS) + foot_h
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    f_kick = font("sans_bold", 24)
    f_title = font("serif_bold", 62)
    f_sub = font("sans", 27)
    tracked_text(d, (pad, 54), "THE PROMPT LAYERS", f_kick, GOLD, 6.0)
    d.text((pad - 3, 92), "Seven swappable layers", font=f_title, fill=INK)
    d.text((pad, 176), "subject (yours)  +  style + lighting + color + composition "
                       "+ medium + mood + camera", font=f_sub, fill=DIM)

    y = head_h
    f_idx = font("serif", 34)
    f_name = font("sans_bold", 30)
    f_desc = font("sans", 24)
    for i, (idx, name, desc) in enumerate(LAYER_ROWS):
        d.rectangle([0, y, W, y + row_h - 1], fill=PANEL if i % 2 == 0 else PANEL2)
        d.line([(0, y + row_h - 1), (W, y + row_h - 1)], fill=LINE, width=1)
        d.rectangle([pad, y + 34, pad + 4, y + 82], fill=GOLD if i in (0, 1) else GOLD_DIM)
        d.text((pad + 34, y + 38), idx, font=f_idx, fill=GOLD_DIM)
        tracked_text(d, (pad + 118, y + 44), name, f_name, INK, 3.6)
        d.text((pad + 470, y + 46), desc, font=f_desc, fill=DIM)
        y += row_h

    d.text((pad, y + 34), "Every layer is independently replaceable: swap the lighting "
                          "of one style onto the subject of another.",
           font=f_desc, fill=FAINT)
    im.save(out, "PNG", optimize=True)
    return im.size


# ---------------------------------------------------------------- 3. 四条轴
def strip(out, paths, W=1024, H=364, radius=10):
    pad, gap = 14, 12
    tw = (W - pad * 2 - gap * 2) // 3
    th = H - pad * 2
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for i in range(3):
        x = pad + i * (tw + gap)
        p = paths[i] if i < len(paths) else None
        tile = load(p, tw, th)
        if tile is None:
            tile = Image.new("RGB", (tw, th), PANEL)
        rt = rounded(tile.convert("RGBA"), radius)
        im.paste(rt, (x, pad), rt)
        d.rounded_rectangle([x, pad, x + tw - 1, pad + th - 1], radius,
                            outline=LINE, width=1)
    im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return im.size


def easing(d, x, y, w, h, kind="ease_in"):
    """一条缓动曲线 —— 镜头卡里真正被写下来的东西就是它。"""
    d.line([(x, y + h), (x + w, y + h)], fill=LINE, width=1)
    d.line([(x, y), (x, y + h)], fill=LINE, width=1)
    pts = []
    for i in range(0, 41):
        t = i / 40.0
        if kind == "ease_in":
            v = t * t
        elif kind == "ease_out":
            v = 1 - (1 - t) ** 2
        else:
            v = 1 - (1 - t) ** 3
        pts.append((x + t * w, y + h - v * h))
    d.line(pts, fill=GOLD, width=2, joint="curve")


def draw_shots(out, W=1024, H=364):
    """镜头轴的示意图。

    这一轴**故意没有照片** —— 157 张镜头卡讲的是帧数与缓动，一张图都不该有
    （库里有测试守着这条边界）。所以这里画的是招式本身：起点、终点、中间那条
    运动轨迹，以及底下的缓动曲线。
    """
    pad, gap = 14, 12
    tw = (W - pad * 2 - gap * 2) // 3
    th = H - pad * 2
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    f_lab = font("sans_bold", 15)
    titles = ("CRASH ZOOM", "WHIP PAN", "IMPACT SHAKE")
    for i in range(3):
        x0, y0 = pad + i * (tw + gap), pad
        d.rounded_rectangle([x0, y0, x0 + tw - 1, y0 + th - 1], 10,
                            fill=PANEL, outline=LINE, width=1)
        cx, cy = x0 + tw // 2, y0 + th // 2 - 16
        fw, fh = 150, 92
        fx, fy = cx - fw // 2, cy - fh // 2
        d.rectangle([fx, fy, fx + fw, fy + fh], outline=LINE, width=2)

        if i == 0:                            # 推近：虚线起点 → 实线终点
            d.rectangle([fx + 34, fy + 22, fx + fw - 34, fy + fh - 22],
                        outline=FAINT, width=1)
            d.rectangle([fx + 14, fy + 10, fx + fw - 14, fy + fh - 10],
                        outline=GOLD, width=2)
            d.line([(cx - 16, cy + 2), (cx + 16, cy + 2)], fill=GOLD, width=2)
            d.polygon([(cx + 16, cy - 4), (cx + 24, cy + 2), (cx + 16, cy + 8)], fill=GOLD)
            easing(d, x0 + 46, y0 + th - 74, tw - 92, 40, kind="ease_in")
        elif i == 1:                          # 横摇：起点框 + 弧线 + 终点箭头
            d.rectangle([fx - 30, fy + 24, fx + 34, fy + fh - 24], outline=FAINT, width=1)
            d.arc([fx + 30, fy + 6, fx + fw + 34, fy + fh - 6], 250, 110, fill=GOLD, width=2)
            d.polygon([(fx + fw + 34, fy + fh // 2 - 8), (fx + fw + 44, fy + fh // 2),
                       (fx + fw + 34, fy + fh // 2 + 8)], fill=GOLD)
            easing(d, x0 + 46, y0 + th - 74, tw - 92, 40, kind="ease_out")
        else:                                 # 震屏：残影 + 放射
            for k, a in ((14, FAINT), (8, GOLD_DIM)):
                d.rectangle([fx - k, fy + k, fx + fw - k, fy + fh + k],
                            outline=a, width=1)
            d.rectangle([fx, fy, fx + fw, fy + fh], outline=GOLD, width=2)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                d.line([(cx + dx * 92, cy + dy * 58), (cx + dx * 106, cy + dy * 68)],
                       fill=FAINT, width=2)
            easing(d, x0 + 46, y0 + th - 74, tw - 92, 40, kind="decay")

        tracked_text(d, (x0 + 22, y0 + th - 30), titles[i], f_lab, DIM, 2.4)
    im.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return im.size


# ---------------------------------------------------------------- 4. 总览网格
def draw_gallery(out, cols=6, tile_w=314, img_h=196):
    items = [(p, n, a) for (p, n, a) in GALLERY if p]
    rows = (len(items) + cols - 1) // cols
    pad, gx, gy = 56, 16, 34
    cap_h = 52
    W = pad * 2 + cols * tile_w + (cols - 1) * gx
    H = pad * 2 + rows * (img_h + cap_h) + (rows - 1) * gy
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    f_name = font("sans_bold", 21)
    f_tag = font("sans_bold", 13)
    for i, (p, name, axis) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (tile_w + gx)
        y = pad + r * (img_h + cap_h + gy)
        tile = load(p, tile_w, img_h) or Image.new("RGB", (tile_w, img_h), PANEL)
        rt = rounded(tile.convert("RGBA"), 8)
        im.paste(rt, (x, y), rt)
        d.rounded_rectangle([x, y, x + tile_w - 1, y + img_h - 1], 8,
                            outline=LINE, width=1)
        d.text((x, y + img_h + 10), name, font=f_name, fill=INK)
        tracked_text(d, (x + 1, y + img_h + 36), AXIS_OF[axis], f_tag,
                     GOLD if axis != "fm" else COOL, 1.8)
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    return im.size


# ---------------------------------------------------------------- main
JOBS = (
    ("hero.jpg", draw_hero),
    ("layers.png", draw_layers),
    ("axis-1-movements.jpg", lambda p: strip(p, AXIS_STRIPS["axis-1-movements"])),
    ("axis-2-handraw.jpg", lambda p: strip(p, AXIS_STRIPS["axis-2-handraw"])),
    ("axis-3-films.jpg", lambda p: strip(p, AXIS_STRIPS["axis-3-films"])),
    ("axis-4-shots.jpg", draw_shots),
    ("gallery.jpg", draw_gallery),
)
JOBS = dict(JOBS)


def write_manifest():
    lines = [
        "# README 配图的清单。由 readme_assets.py 生成，不要手改。",
        "# sha256  size  file  sources...",
        "#",
        "# 每一行末尾列出这张图用到的库内源图。测试会核对源图存在、且被 git 跟踪 ——",
        "# 配图必须能在别人 clone 下来的仓库里重建，否则它只是一张作者机上的私有图。",
    ]
    for name in JOBS:
        p = os.path.join(OUT_DIR, name)
        with open(p, "rb") as f:
            data = f.read()
        srcs = sorted({os.path.relpath(s, VAULT) for s in sources_of(name) if s})
        lines.append("%s  %d  %s  %s" % (hashlib.sha256(data).hexdigest(),
                                         len(data), name, " ".join(srcs)))
    path = os.path.join(OUT_DIR, MANIFEST)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def sources_of(name):
    if name == "hero.jpg":
        return hero_items()
    if name == "axis-1-movements.jpg":
        return AXIS_STRIPS["axis-1-movements"]
    if name == "axis-2-handraw.jpg":
        return AXIS_STRIPS["axis-2-handraw"]
    if name == "axis-3-films.jpg":
        return AXIS_STRIPS["axis-3-films"]
    if name == "gallery.jpg":
        return [p for p, _n, _a in GALLERY]
    return []                             # layers / shots 是画出来的，没有源图


def cmd_check():
    path = os.path.join(OUT_DIR, MANIFEST)
    if not os.path.exists(path):
        print("  ✗ 缺清单 %s（跑 python3 readme_assets.py）" % MANIFEST)
        return 1
    bad = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            sha, size, name = line.split()[:3]
            p = os.path.join(OUT_DIR, name)
            if not os.path.exists(p):
                print("  ✗ %s 不在磁盘上" % name)
                bad += 1
                continue
            with open(p, "rb") as fh:
                data = fh.read()
            if hashlib.sha256(data).hexdigest() != sha or len(data) != int(size):
                print("  ✗ %s 与清单不符" % name)
                bad += 1
    if bad:
        print("  重跑 python3 readme_assets.py 重建")
        return 1
    print("  ✓ 配图与清单一致")
    return 0


def main():
    ap = argparse.ArgumentParser(description="生成 README 配图")
    ap.add_argument("--list", action="store_true", help="只列出源图，不写文件")
    ap.add_argument("--check", action="store_true", help="只核对清单，不写文件")
    a = ap.parse_args()

    if a.check:
        return cmd_check()

    if a.list:
        print("头图：")
        for p in hero_items():
            print("   %s" % (os.path.relpath(p, VAULT) if p else "（缺）"))
        print("四条轴：")
        for k in ("axis-1-movements", "axis-2-handraw", "axis-3-films"):
            for p in AXIS_STRIPS[k]:
                print("   %-22s %s" % (k, os.path.relpath(p, VAULT) if p else "（缺）"))
        print("   axis-4-shots          画出来的示意图（这一轴没有照片，是有意的）")
        print("总览网格：%d 格，缺 %d 张"
              % (len(GALLERY), sum(1 for p, _n, _a in GALLERY if not p)))
        return 0

    need_pil()                      # 只有走到「真画图」这一步才要求 Pillow

    os.makedirs(OUT_DIR, exist_ok=True)
    for name, fn in JOBS.items():
        out = os.path.join(OUT_DIR, name)
        size = fn(out)
        print("  ✓ %-22s %5d×%-5d %7.0f KB"
              % (name, size[0], size[1], os.path.getsize(out) / 1024.0))
    write_manifest()
    print("清单 %s" % os.path.relpath(os.path.join(OUT_DIR, MANIFEST), VAULT))
    print("写到 %s" % os.path.relpath(OUT_DIR, VAULT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
