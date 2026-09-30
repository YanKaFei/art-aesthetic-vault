#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_resolve.py —— 把「片名」解析成**真实存在的** film-grab 画廊页 URL。

## 为什么必须解析而不能写 URL

加片子时最容易犯的错是猜 URL。本项目实测：手写的 10 个 film-grab URL 里
**8 个是 404** —— 因为 URL 里的日期是画廊**发布时间**，不是上映年份，
猜不出来。例如：

    ✗ https://film-grab.com/2014/03/30/stalker/     （猜的，404）
    ✓ https://film-grab.com/2012/07/31/stalker/     （读导演页拿到的）

所以加新片的流程是：**读导演分类页 → 按片名匹配 → 拿真实链接**，
匹配不到就明确报告，**绝不猜一个**。

## 数据从哪来

film-grab 的导演分类页 `/category/directors/<slug>/` 列出该导演的全部片目，
每条是 `https://film-grab.com/YYYY/MM/DD/<film-slug>/`。
导演索引在 `/browse-by-artist/directors-a-z/`（实测 1,709 个导演页）。

## 离线可测

`parse_director_page` / `match_film` 是纯函数，用夹具测（`tests/resolve_test.py`）。
联网只发生在 `fetch_*` 三个函数里。
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

BASE = "https://film-grab.com"
DIRECTORS_AZ = BASE + "/browse-by-artist/directors-a-z/"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
# 对站点客气：实测 0.35s 连续抓会被限流断连，1.2s 稳定
PAUSE = 1.2
CACHE = os.path.join(HERE, "_data", "filmgrab_pages")

FILM_URL_RE = re.compile(
    r'https://film-grab\.com/(\d{4}/\d{2}/\d{2})/([a-z0-9%\-\u4e00-\u9fff]+)/', re.I)


def get_html(url, retries=4, backoff=3.0, cache=True):
    """抓一页（带退避重试 + 本地缓存）。

    缓存让「同一批候选反复核对」只抓一次 —— 既快，也少打扰站点。
    """
    if cache:
        os.makedirs(CACHE, exist_ok=True)
        fn = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:120] + ".html"
        p = os.path.join(CACHE, fn)
        if os.path.exists(p) and os.path.getsize(p) > 500:
            return open(p, encoding="utf-8").read()
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Language": "en-US,en;q=0.9"})
    last = None
    for i in range(retries):
        try:
            data = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "replace")
            if cache:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(data)
            return data
        except urllib.error.HTTPError:
            raise
        except Exception as e:
            last = e
            if i < retries - 1:
                time.sleep(backoff * (2 ** i))
    raise RuntimeError("%s（连续 %d 次失败；EOF/SSL 断连通常是限流，"
                       "等十几分钟再跑，已缓存的会跳过）" % (last, retries))


# ------------------------------------------------------------------ 解析
def parse_director_page(html):
    """从导演分类页抽出 [(film-slug, url)]。

    只认 `/YYYY/MM/DD/<slug>/` 形态的链接 —— `/category/...`、`/type/...`
    这些不是片目，混进来会让匹配命中错的东西。
    """
    out, seen = [], set()
    for m in FILM_URL_RE.finditer(html or ""):
        slug = m.group(2).strip("/").lower()
        url = "https://film-grab.com/%s/%s/" % (m.group(1), m.group(2))
        if slug in seen:
            continue
        seen.add(slug)
        out.append((slug, url))
    return out


def _norm(s):
    """归一化：小写 + 去掉所有非字母数字（含中日韩字符保留）。

    `In The Mood For Love` / `in-the-mood-for-love` / `IntheMoodforLove`
    是同一个片名 —— 标点与空格不该决定查找成败。
    """
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", (s or "").lower())


def _edit1(a, b):
    """a 与 b 是否**恰好**相差一个字符（增/删/改各算一种）。

    只判「是不是 1」，不返回距离 —— 我们只需要这个布尔。比完整编辑距离
    便宜，而且意图更清楚：容错**只放开一个字符**。
    """
    if a == b:
        return False                      # 相等不算「近似」，精确匹配已处理
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:                          # 替换
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb:                           # a 多一个字符
        a, b = b, a
    # b 比 a 多一个字符：试着跳过一处
    i = 0
    while i < len(a) and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


def match_film(films, title):
    """在 [(slug, url)] 里找片名。返回 (url|None, 说明)。

    三级匹配：① slug 原样相等 → ② 归一化相等 → ③ 归一化后唯一子串。
    **都不中就返回 None**，绝不猜。
    """
    t = (title or "").strip()
    if not t or not films:
        return None, "片名为空或该导演没有片目"
    tl, tn = t.lower(), _norm(t)
    # ① 原样 slug
    for slug, url in films:
        if slug == tl:
            return url, "slug 精确匹配"
    # ② 归一化相等（处理标点/空格/年份括号）
    for slug, url in films:
        if _norm(slug) == tn:
            return url, "归一化匹配"
    # ③ 唯一子串（`Dune (2021)` 对 `dune-2021`）
    hits = [(s, u) for s, u in films if tn and (tn in _norm(s) or _norm(s) in tn)]
    if len(hits) == 1:
        return hits[0][1], "唯一子串匹配"
    if len(hits) > 1:
        return None, "匹配到 %d 条，歧义：%s" % (len(hits), [s for s, _ in hits][:4])
    # ④ 站点拼错一个字符时的近似匹配（**收紧**：距离恰为 1 且候选唯一）
    #
    # 实测踩到：film-grab 把《千年女优》写成 `millenium-actress`（少一个 n），
    # 于是那部片被误判成「站上没有」—— 与事实相反。
    # 但错配比漏配更糟，所以只放开一个字符，且必须唯一；多个候选就报歧义。
    near = [(s, u) for s, u in films if tn and _edit1(tn, _norm(s))]
    if len(near) == 1:
        return near[0][1], "近似匹配（差 1 个字符，站点可能拼错）"
    if len(near) > 1:
        return None, "近似匹配到 %d 条，歧义：%s" % (len(near), [s for s, _ in near][:4])
    return None, "没匹配到（该导演页里没有这个片名）"


def director_pages(html=None):
    """从 A–Z 索引页抽 [(导演名, 分类页 url)]。"""
    if html is None:
        html = get_html(DIRECTORS_AZ)
    out, seen = [], set()
    for m in re.finditer(r'href="(https?://film-grab\.com/category/directors/[^"]+)"[^>]*>([^<]{2,60})<',
                         html):
        url, name = m.group(1), m.group(2).strip()
        if url in seen:
            continue
        seen.add(url)
        out.append((name, url))
    return out


def resolve(title, director_slug=None, director_url=None):
    """解析一部片。给 director_slug 或 director_url 直接查那个导演页。

    返回 {url, how, films_seen} 或 {url: None, why}。
    """
    if not director_url and director_slug:
        director_url = "%s/category/directors/%s/" % (BASE, director_slug)
    if not director_url:
        return {"url": None, "why": "缺少导演分类页（director_slug 或 director_url）"}
    try:
        html = get_html(director_url)
    except Exception as e:
        return {"url": None, "why": "抓导演页失败：%s" % str(e)[:90]}
    films = parse_director_page(html)
    if not films:
        return {"url": None, "why": "导演页里没解析出片目（%s）" % director_url}
    url, how = match_film(films, title)
    # ⚠ 这里必须把**失败原因**也放进 `why`。原先只放 `how`，而 CLI 读的是
    # `why` —— 于是 18 条解析失败的原因全被显示成 `None`，等于把诊断信息
    # 静默丢掉（实测踩到）。成功时 how 记录匹配方式，失败时 why 记录原因。
    if url:
        return {"url": url, "how": how, "films_seen": len(films)}
    return {"url": None, "why": how, "films_seen": len(films)}


# ------------------------------------------------------------------ CLI
def main():
    import argparse
    ap = argparse.ArgumentParser(description="把片名解析成真实 film-grab URL")
    ap.add_argument("title", nargs="?", help="片名（英文）")
    ap.add_argument("--director", help="导演分类页 slug，如 wong-kar-wai")
    ap.add_argument("--list-directors", action="store_true", help="列出全部导演页")
    ap.add_argument("--check-candidates", action="store_true",
                    help="把 fv_candidates 里的候选逐条解析（慢，会打扰站点）")
    a = ap.parse_args()

    if a.list_directors:
        ds = director_pages()
        print("导演分类页：%d 个" % len(ds))
        for n, u in ds[:20]:
            print("  %-30s %s" % (n, u))
        return 0

    if a.check_candidates:
        import fv_candidates as C
        ok = bad = 0
        for c in C.CANDIDATES:
            r = resolve(c["title_en"], director_slug=c.get("director_slug"),
                        director_url=c.get("filmgrab_director"))
            if r.get("url"):
                ok += 1
                print("  ✓ %-34s %s" % (c["slug"], r["url"]))
            else:
                bad += 1
                print("  ✗ %-34s %s" % (c["slug"], r.get("why")))
            time.sleep(PAUSE)
        print("\n解析成功 %d / 失败 %d" % (ok, bad))
        return 0 if bad == 0 else 1

    if not a.title:
        ap.print_help()
        return 0
    r = resolve(a.title, director_slug=a.director)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0 if r.get("url") else 1


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 fv_resolve.py 2046 --director wong-kar-wai",
          ["把片名解析成**真实存在**的 film-grab 画廊页 URL。",
           "  <title>            片名（英文）",
           "  --director SLUG    导演分类页 slug，如 wong-kar-wai",
           "  --list-directors   列出全部导演分类页（1,709 个）",
           "  --check-candidates 逐条解析 fv_candidates 的候选（慢）",
           "",
           "⚠ 不要手写 film-grab URL：URL 里的日期是画廊发布时间，猜不出来。",
           "实测手写 10 个里 8 个 404。"])
    sys.exit(main())
