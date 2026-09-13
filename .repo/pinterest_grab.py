#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pinterest_grab.py —— 从 Pinterest 抓取公开的 /ideas/ 分类图，存进仓库。

【重要发现】本机环境下 curl 连不上 Pinterest（TLS 被代理拦截，http=000），
但 **Python requests 可以正常访问**。所以这个脚本用 requests 而不是 curl。

实测可用的路径（2026-09）：
  https://www.pinterest.com/ideas/                      → 10 个顶层分类 + 数字 ID
  https://www.pinterest.com/ideas/<分类>/<数字ID>/       → 服务端渲染，约 20 张原图 + 子分类
  https://i.pinimg.com/originals/...                    → 原图可直接下载

实测**不可用**的路径：
  /resource/BaseSearchResource/get/  → 403 Invalid Resource Request（需要合法 app version）
  /ideas/<任意关键词>/                → 200 但无图（必须带数字 ID）
  /search/pins/?q=X                  → 页面是 JS 渲染，HTML 里没有 pin 数据

所以：**按分类抓可以，按关键词搜不行**。关键词检索请用官方的
在你自己的浏览器里做。

用法：
    python3 pinterest_grab.py --discover              # 列出所有分类与子分类
    python3 pinterest_grab.py --crawl art             # 抓 art 分类（含子分类）
    python3 pinterest_grab.py --crawl art design --max-per 25
    python3 pinterest_grab.py --url /ideas/oil-painting/907077517247/
    python3 pinterest_grab.py --crawl-all --max-per 20

产出：
    99-附件/images/pinterest/<分类>/<hash>.jpg
    20-我的提示词/Pinterest-<分类>.md     每张图带来源链接与反推提示
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse

# 帮助闸门放在 requests 的检查**之前**：缺 requests 时 `--help` 应该照样能看，
# 而不是把人挡在「先装依赖」那句话上（他可能只是想先读一下用法再决定装不装）。
from clihelp import guard  # noqa: E402

guard(sys.argv[1:], "python3 pinterest_grab.py <选项>",
      ["--discover              列出所有分类与子分类",
       "--crawl <分类…>         抓指定分类（含子分类）",
       "--crawl-all             抓所有分类",
       "--url /ideas/…/         只抓一个板子",
       "--max-per N             每个板最多抓几张",
       "--analyze [分类…]       给已抓的图补反推（提示词 + 视频）",
       "--no-analyze            抓完不自动补反推"])

try:
    import requests
except ImportError:
    sys.exit("需要 requests：pip3 install --target ./vendor/libs --upgrade requests\n"
             "然后用 PYTHONPATH=./vendor/libs 运行")

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMG_ROOT = os.path.join(VAULT, "99-附件", "images", "pinterest")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
BASE = "https://www.pinterest.com"
IMG_RE = re.compile(r'https://i\.pinimg\.com/originals/[^"\\\s]+?\.(?:jpg|jpeg|png|webp)', re.I)

# Pinterest 每个页面都带自己的 logo 图，必须排除，否则每个板第一张都是它
LOGO_HASHES = ("d53b014d86a6b6761bf649a0ed81", "d5/3b/01/d53b014d86a6b6761bf649a0ed813c2b")


def is_logo(u):
    return any(h in u for h in LOGO_HASHES)
SUB_RE = re.compile(r'href="/ideas/([a-z0-9\-]+)/(\d+)/?"')
THROTTLE = 1.5           # 秒／请求，礼貌抓取


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                      "Referer": BASE + "/"})
    return s


def get(s, path, tries=3):
    url = path if path.startswith("http") else BASE + path
    for i in range(tries):
        try:
            r = s.get(url, timeout=35)
            if r.status_code == 200:
                return r.text
            if r.status_code in (429, 500, 502, 503) and i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            print("    ! http=%s %s" % (r.status_code, url[-56:]))
            return None
        except Exception as e:
            if i == tries - 1:
                print("    ! %s -> %s" % (url[-56:], str(e)[:60])); return None
            time.sleep(3 * (i + 1))
    return None


def images_in(html):
    seen, out = set(), []
    for u in IMG_RE.findall(html or ""):
        if is_logo(u):
            continue
        if u not in seen:
            seen.add(u); out.append(u)
    return out


def discover(s):
    """返回 {分类 slug: {'id':..., 'subs': [...]}}"""
    html = get(s, "/ideas/")
    if not html:
        return {}
    cats = {}
    for m in re.finditer(r'href="/ideas/([a-z0-9\-]+)/(\d+)/?"', html):
        cats.setdefault(m.group(1), {"id": m.group(2), "subs": []})
    print("顶层分类 %d 个：%s" % (len(cats), "、".join(cats)))
    # 展开一层子分类
    for slug, info in cats.items():
        html2 = get(s, "/ideas/%s/%s/" % (slug, info["id"]))
        time.sleep(THROTTLE)
        if html2:
            for m in SUB_RE.finditer(html2):
                sub = "/ideas/%s/%s/" % (m.group(1), m.group(2))
                if sub.rstrip("/").split("/")[2] != slug or sub not in info["subs"]:
                    info["subs"].append(sub)
    return cats


def slugify(s, n=40):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower(), flags=re.UNICODE)
    return (re.sub(r"[\s_]+", "-", s).strip("-")[:n] or "board")


def grab_board(s, path, max_n=25, download=True, label=None):
    """抓一个 /ideas/ 页面，返回作品列表"""
    html = get(s, path)
    time.sleep(THROTTLE)
    if not html:
        return []
    urls = images_in(html)[:max_n]
    name = label or slugify(path.strip("/").split("/")[-2] if path.count("/") > 3
                            else path.strip("/").split("/")[-1])
    out = []
    imgdir = os.path.join(IMG_ROOT, name)
    if download and urls:
        os.makedirs(imgdir, exist_ok=True)
    for i, u in enumerate(urls, 1):
        w = {"title": "%s #%02d" % (name, i), "artist": "Pinterest 用户（见来源页）",
             "date": "", "medium": "", "image_url": u, "image_url_hi": u,
             "page_url": BASE + path, "source": "Pinterest",
             "license": "版权归原作者，仅个人参考，不可再分发",
             "license_url": "https://policy.pinterest.com/terms-of-service",
             "local_image": ""}
        if download:
            fn = "%02d-%s.jpg" % (i, u.rsplit("/", 1)[-1].rsplit(".", 1)[0][:28])
            dest = os.path.join(imgdir, fn)
            if not os.path.exists(dest):
                try:
                    rr = s.get(u, timeout=45)
                    if rr.status_code == 200 and len(rr.content) > 3000:
                        open(dest, "wb").write(rr.content)
                    time.sleep(0.4)
                except Exception as e:
                    print("      ! 下载失败 %s" % str(e)[:50])
            if os.path.exists(dest):
                w["local_image"] = "99-附件/images/pinterest/%s/%s" % (name, fn)
        out.append(w)
        print("    %s %s" % ("✓" if w["local_image"] else "✗", u.rsplit("/", 1)[-1][:40]))
    return out, name


def write_note(name, works, board_path, analysis=None):
    """写一块板子的笔记。

    analysis: {图片文件名: reverse_prompt 记录} —— 有的话就在每张图下面
    补上反推（提示词 + 两块视频提示词）。回填时由 --analyze 传进来。
    """
    L = ["---", "# auto-generated by pinterest_grab.py", "type: Pinterest抓取",
         "分类: %s" % name, "张数: %d" % len(works), "标签:", "  - pinterest", "---", ""]
    L += ["# Pinterest · %s" % name, "",
          "← 回到 [[Pinterest]]", "",
          "> [!warning] 版权",
          "> 图片版权归各自原作者，**没有统一授权**，只供个人审美参考、不要再分发。",
          "> 完整说明见 [[Pinterest]]。", "",
          "> [!tip] 下一步",
          "> 挑出真正有用的丢进投递箱（`pinterest/`），反推会自动跑完。",
          "> 流程见 [[Pinterest]]。", "",
          "来源页：<%s>" % (BASE + board_path), ""]
    for i, w in enumerate(works, 1):
        L += ["### %d. %s" % (i, w["title"]), ""]
        fn = os.path.basename(w["local_image"]) if w.get("local_image") else None
        if fn:
            L += ["![[%s]]" % fn, ""]
        # 反推结果放在图片**下面** —— 用户要的就是「图下面有提示词分析和视频分析」
        if analysis and fn and fn in analysis:
            rec = analysis[fn]
            slug = ((rec.get("suggest") or [{}])[0].get("slug"))
            mv = _mv_by_slug(slug) if slug else None
            import reverse_prompt as RP
            L += [RP.compose_compact(rec, mv, fn), ""]
        L += ["[原图直链](%s)" % w["image_url_hi"], "", "---", ""]
    p = os.path.join(VAULT, "20-我的提示词", "Pinterest-%s.md" % name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")
    return p



def _mv_by_slug(slug):
    try:
        from movements import MOVEMENTS
        return next((m for m in MOVEMENTS if m["slug"] == slug), None)
    except Exception:
        return None


def analyze_boards(only=None, verbose=True):
    """给已经下载到本地的板子图补反推，并重写板子笔记。

    为什么要单独一个模式：抓取和**分析**是两件事。
    抓的时候要联网、慢；分析是纯本地计算，可以反复跑。
    实测过的坑：抓取脚本原来只写图片和原图直链，图下面是空的 ——
    用户看到 212 张 Pinterest 图却一点分析都没有。
    """
    import reverse_prompt as RP
    from movements import MOVEMENTS
    root = os.path.join(VAULT, "99-附件", "images", "pinterest")
    if not os.path.isdir(root):
        print("还没有抓过图：%s 不存在" % root)
        return 0
    boards = sorted(d for d in os.listdir(root)
                    if os.path.isdir(os.path.join(root, d)) and (not only or d in only))
    total = 0
    for board in boards:
        d = os.path.join(root, board)
        imgs = sorted(f for f in os.listdir(d)
                      if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        if not imgs:
            continue
        if verbose:
            print("· %s（%d 张）" % (board, len(imgs)))
        recs = RP.analyze_images([os.path.join(d, f) for f in imgs], verbose=verbose)
        analysis = {os.path.basename(k): v for k, v in recs.items()}
        # 原图直链在本地文件名里是找不回来的（文件名只有序号和 hash），
        # 所以从**已有笔记里解析出来复用** —— 否则回填一次就把原始出处丢了。
        old_note = os.path.join(VAULT, "20-我的提示词", "Pinterest-%s.md" % board)
        links, board_path = [], "/ideas/"
        if os.path.exists(old_note):
            old_txt = open(old_note, encoding="utf-8").read()
            links = re.findall(r"\[原图直链\]\((https?://[^)]+)\)", old_txt)
            # 板子来源页同样从旧笔记里取回来（本地文件里没有它）
            m = re.search(r"来源页：<(https?://[^>]+)>", old_txt)
            if m:
                board_path = m.group(1).replace(BASE, "")
        works = []
        for k, f in enumerate(imgs):
            works.append({
                "title": f, "local_image": "99-附件/images/pinterest/%s/%s" % (board, f),
                "image_url_hi": links[k] if k < len(links) else (BASE + "/ideas/"),
                "artist": "Pinterest 用户（见来源页）", "page_url": BASE,
            })
        p = write_note(board, works, board_path, analysis=analysis)
        total += len(imgs)
        if verbose:
            print("   → %s" % os.path.relpath(p, VAULT))
    print("\n完成：%d 个板子、%d 张图已补上反推" % (len(boards), total))
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discover", action="store_true")
    ap.add_argument("--crawl", nargs="*", metavar="分类")
    ap.add_argument("--crawl-all", action="store_true")
    ap.add_argument("--url", nargs="*", metavar="/ideas/...")
    ap.add_argument("--max-per", type=int, default=25)
    ap.add_argument("--no-download", action="store_true")
    ap.add_argument("--analyze", nargs="*", metavar="板子",
                    help="给已下载的板子图补反推（提示词+视频），重写板子笔记")
    ap.add_argument("--no-analyze", action="store_true",
                    help="抓完不做反推（默认会做）")
    a = ap.parse_args()

    if a.analyze is not None:
        return 0 if analyze_boards(only=a.analyze or None) else 1

    s = session()

    if a.discover:
        cats = discover(s)
        for slug, info in cats.items():
            print("%-20s id=%-14s 子分类 %d" % (slug, info["id"], len(info["subs"])))
            for sub in info["subs"][:6]:
                print("     ", sub)
        return 0

    targets = []
    if a.url:
        targets = [(u, u.strip("/").split("/")[-2] if u.count("/") > 3 else u.strip("/").split("/")[-1]) for u in a.url]
    else:
        cats = discover(s)
        want = a.crawl or (list(cats) if a.crawl_all else None)
        if not want:
            ap.print_help(); return 0
        for slug in want:
            if slug not in cats:
                print("跳过未知分类：%s" % slug); continue
            info = cats[slug]
            targets.append(("/ideas/%s/%s/" % (slug, info["id"]), slug))
            targets += [(x, x.strip("/").split("/")[-2]) for x in info["subs"]]

    total = 0
    grabbed = []
    for path, label in targets:
        print("· %s" % path)
        res = grab_board(s, path, a.max_per, not a.no_download, label)
        if not res:
            continue
        works, name = res
        if works:
            p = write_note(name, works, path)
            total += len(works)
            grabbed.append(name)
            print("    → %s（%d 张）" % (os.path.basename(p), len(works)))
    print("\n完成，共 %d 张。" % total)

    # 抓完**立刻补上反推** —— 否则图下面又是空的，就是用户报的那个问题。
    # 抓取要联网、分析是纯本地计算，两件事分开，但默认串起来跑。
    if grabbed and not a.no_analyze:
        print("\n给新抓的图补反推（提示词 + 视频）…")
        analyze_boards(only=grabbed)
    elif grabbed:
        print("\n（跳过了反推。要补上：python3 pinterest_grab.py --analyze %s）"
              % " ".join(grabbed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
