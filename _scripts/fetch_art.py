#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_art.py —— 从开放授权美术馆 / 维基共享资源抓取公共领域作品图与元数据。

只使用 Python 标准库，不需要 pip install。

数据源：
  · 克利夫兰艺术博物馆  CC0        https://openaccess-api.clevelandart.org
  · 大都会艺术博物馆    CC0        https://collectionapi.metmuseum.org
  · 维基共享资源        Public domain / CC0（逐条判定）

用法：
    python3 fetch_art.py                      # 抓全部流派
    python3 fetch_art.py impressionism        # 只抓指定流派（可给多个）
    python3 fetch_art.py --per 8              # 每个流派抓 8 件
    python3 fetch_art.py --refresh            # 忽略已有数据重抓
    python3 fetch_art.py --include-ccby       # 额外接受 CC BY 系列（需署名）
    python3 fetch_art.py --only-tier A        # 只抓 A 类（有可靠公共领域图的）
    python3 fetch_art.py --list               # 只列出流派，不抓取
"""

import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMG_DIR = os.path.join(VAULT, "99-附件", "images")
DATA_DIR = os.path.join(HERE, "_data")

sys.path.insert(0, HERE)
from movements import MOVEMENTS, BY_SLUG                     # noqa: E402
from providers import (PROVIDERS, download, is_flat_work,  # noqa: E402
                       artist_matches, is_ai_generated, extract_artist_from_title)


def ext_of(url):
    m = re.search(r"\.(jpe?g|png|tiff?|webp|gif)(?:$|\?)", url or "", re.I)
    if not m:
        return ".jpg"
    e = m.group(1).lower()
    return ".jpg" if e in ("jpeg", "jpg") else "." + e


def slugify(s, n=44):
    s = re.sub(r"[^\w\s-]", "", (s or "").lower(), flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return (s[:n] or "untitled").strip("-")


def fetch_one(provider, query, want, allow_ccby):
    fn = PROVIDERS[provider]
    if provider == "commons":
        return fn(query, want, allow_ccby=allow_ccby)
    return fn(query, want)


def collect(mv, per, allow_ccby=False):
    """按 sources 里声明的顺序、逐个查询词抓取，并做两层过滤：

       1) 艺术家必须命中该流派的关联艺术家关键词（保证语义相关）
       2) 必须是平面作品（排除汤盆、沙发、花瓶之类的三维藏品）

    刻意不做「放宽补充」：宁可某个流派只有 2 张图，也不要混进无关作品。
    一个参考库最怕的不是图少，是图错——错的参考会污染你的提示词直觉。
    """
    seen, works = set(), []
    keys = mv.get("artist_keys") or []
    excl = mv.get("exclude_keys") or []
    plan = []
    for provider in ("cleveland", "met", "commons"):
        for q in (mv.get("sources") or {}).get(provider, []) or []:
            plan.append((provider, q))
    if not plan or not keys:
        return []

    for provider, query in plan:
        print("    [%s] q=%s" % (provider, query))
        try:
            pool = fetch_one(provider, query, per * 3, allow_ccby)
        except Exception as e:
            print("    ! provider error: %s" % e)
            pool = []
        for w in pool:
            # 大多数流派只要平面作品；但侘寂（茶碗）、伊斯兰几何（瓷砖）
            # 这类流派的主角就是器物，用 allow_3d 关掉平面过滤
            if is_ai_generated(w):
                print("    ✗ 排除 AI 生成图: %s" % w["title"][:48])
                continue
            if not mv.get("allow_3d") and not is_flat_work(w):
                continue
            if not artist_matches(w, keys, excl):
                continue
            if w.get("raw_title"):
                real = extract_artist_from_title(w["raw_title"], keys)
                if real:
                    w["artist"] = real
            key = (w["title"].lower()[:40], (w.get("raw_title") or w["artist"]).lower()[:40])
            if key in seen:
                continue
            seen.add(key)
            works.append(w)
        time.sleep(0.5)
        if len(works) >= per:
            break
    return works[:per]


def run(only=None, per=6, refresh=False, allow_ccby=False, tier=None):
    os.makedirs(DATA_DIR, exist_ok=True)
    if only:
        targets = [BY_SLUG[s] for s in only if s in BY_SLUG]
        for s in only:
            if s not in BY_SLUG:
                print("!! 未知流派 slug: %s" % s)
    else:
        targets = [m for m in MOVEMENTS if (tier is None or m.get("tier") == tier)]

    done = skipped = total_imgs = 0
    for mv in targets:
        slug = mv["slug"]
        out_json = os.path.join(DATA_DIR, slug + ".json")
        if os.path.exists(out_json) and not refresh:
            skipped += 1
            continue
        print("· %s (%s)" % (mv["name_zh"], slug))
        works = collect(mv, per, allow_ccby)
        if not works:
            print("    (无可用公共领域图片 —— 生成纯提示词卡)")
            json.dump([], open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            done += 1
            continue
        d = os.path.join(IMG_DIR, slug)
        os.makedirs(d, exist_ok=True)
        for i, w in enumerate(works, 1):
            # 文件名必须带 slug：不同流派可能收录同一件作品，
            # 而 Obsidian 的 ![[文件名]] 是按 basename 解析的，重名会撞车。
            fn = "%02d-%s-%s%s" % (i, slug, slugify(w["title"]), ext_of(w["image_url"]))
            dest = os.path.join(d, fn)
            if not os.path.exists(dest):
                download(w["image_url"], dest)
            w["local_image"] = ("99-附件/images/%s/%s" % (slug, fn)) if os.path.exists(dest) else ""
            w["image_url_hi"] = w.get("image_url_hi") or w["image_url"]
            w.pop("raw_title", None)
            print("    %s %s — %s" % ("✓" if w["local_image"] else "✗",
                                      w["title"][:42], w["artist"][:24]))
        json.dump(works, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        total_imgs += len(works)
        done += 1
        print("    → %d 件" % len(works))
        time.sleep(0.4)
    print("\n完成：处理 %d 个流派，跳过 %d 个（已有数据），本次入库 %d 件。"
          % (done, skipped, total_imgs))


if __name__ == "__main__":
    argv = sys.argv[1:]
    per = 6
    if "--per" in argv:
        i = argv.index("--per")
        per = int(argv[i + 1])
        del argv[i:i + 2]
    tier = None
    if "--only-tier" in argv:
        i = argv.index("--only-tier")
        tier = argv[i + 1]
        del argv[i:i + 2]
    if "--list" in argv:
        cats = {}
        for m in MOVEMENTS:
            cats.setdefault(m["category"], []).append(m)
        for c, ms in cats.items():
            print("\n【%s】%d 个" % (c, len(ms)))
            for m in ms:
                print("   %-24s %-16s %s" % (m["slug"], m["name_zh"], m["name_en"]))
        print("\n合计 %d 个流派" % len(MOVEMENTS))
        sys.exit(0)
    args = [a for a in argv if not a.startswith("--")]
    run(only=args or None, per=per, refresh="--refresh" in argv,
        allow_ccby="--include-ccby" in argv, tier=tier)
