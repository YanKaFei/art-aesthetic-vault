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
import shutil
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
    """收集某个流派的作品。

    两层过滤（这是整个库最关键的逻辑）：
      1) 作者必须命中该流派的关联关键词 —— 否则泛化查询会混进大量无关作品
      2) 必须是平面作品 —— 排除硬币、玻璃器、家具之类的三维藏品

    抓取策略：**按来源轮流取**，而不是「第一个源凑够就停」。
    后者会让排在前面的源垄断结果，后面的源永远轮不到。
    不同馆的强项不同（AIC 印象派强、克利夫兰亚洲强、大都会最广），
    轮转能让结果有来源与风格上的广度。

    刻意不做「放宽补充」：宁可某个流派只有 2 张图，也不要混进无关作品。
    一个参考库最怕的不是图少，是图错——错的参考会污染提示词直觉。
    """
    keys = mv.get("artist_keys") or []
    excl = mv.get("exclude_keys") or []
    tkeys = mv.get("title_keys") or []
    if not keys and not tkeys:
        return []

    src = mv.get("sources") or {}
    # 芝加哥艺术博物馆是后加的源。为了不用改 141 份流派定义，
    # 没显式声明 artic 查询词时复用 cleveland 的——两者都是同类检索词。
    if "artic" not in src and src.get("cleveland"):
        src = dict(src, artic=list(src["cleveland"]))

    def keep(w):
        if is_ai_generated(w):
            print("    ✗ 排除 AI 生成图: %s" % w["title"][:48])
            return False
        if not mv.get("allow_3d") and not is_flat_work(w):
            return False
        if not artist_matches(w, keys, excl, tkeys):
            return False
        if w.get("raw_title"):
            real = extract_artist_from_title(w["raw_title"], keys)
            if real:
                w["artist"] = real
        return True

    # ---- 逐个来源收集候选池 ----
    pools = []          # [(来源名, [作品])]
    seen = set()
    for provider in ("cleveland", "artic", "met", "commons"):
        queries = src.get(provider) or []
        if not queries:
            continue
        mine = []
        for query in queries:
            if len(mine) >= per:      # 这个来源够了，不用再问它的后续查询词
                break
            print("    [%s] q=%s" % (provider, query))
            try:
                pool = fetch_one(provider, query, per * 3, allow_ccby)
            except Exception as e:
                print("    ! provider error: %s" % e)
                pool = []
            for w in pool:
                if len(mine) >= per:
                    break
                dedup = (w["title"].lower()[:40], (w.get("raw_title") or w.get("artist") or "").lower()[:40])
                if dedup in seen or not keep(w):
                    continue
                seen.add(dedup)
                mine.append(w)
            time.sleep(0.5)
        if mine:
            pools.append((provider, mine))

    # ---- 轮流取，保证来源分散 ----
    works, round_no = [], 0
    while len(works) < per and round_no < per * 2:
        progressed = False
        for _prov, pool in pools:
            if round_no < len(pool):
                progressed = True
                works.append(pool[round_no])
                if len(works) >= per:
                    break
        if not progressed:
            break
        round_no += 1
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
        # --refresh 时必须先清空这个流派的图片目录。
        # 否则换了数据源之后，旧图还在、新图又进来，会留下一堆
        # 没有任何笔记引用的孤儿文件（它们照样占体积、照样被 clone）。
        if refresh:
            shutil.rmtree(d, ignore_errors=True)
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
    from clihelp import guard
    guard(argv, "python3 fetch_art.py [流派…] [选项]",
          ["不给流派名就补抓所有还没有图的流派。",
           "--per N          每个流派抓几张（默认 6）",
           "--refresh        先删掉该流派的图目录再重抓",
           "--only-tier T    只处理某一层",
           "--include-ccby   连同 CC-BY 一起收（默认只收 CC0 / 公共领域）",
           "--list           列出全部流派，不抓图"])
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
