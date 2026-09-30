#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_fetch.py —— 从 film-grab 抽一部片的**可核对事实**：班底、年份、剧照外链。

## 只用标准库，且为什么不用 requests

本仓库的核心原则是「clone 下来不用装任何东西」。抓取这条路上
`urllib.request` 就够用，没有 cookie/会话/重定向的复杂度。

⚠ 一个实测到的坑：**`curl` 在本机连不上 film-grab（LibreSSL
SSL_ERROR_SYSCALL），但 Python 的 urllib 能连**。所以「用 curl 先试一下」
得到的结论是错的 —— 这不是站点封禁，是 curl 那条 TLS 路径的问题。
本脚本因此不依赖任何外部命令行工具。

## 抓什么、不抓什么

**抓**（这些是事实，可回查画廊页）：
    Director / Director of Photography / Production Design / Costume Design / Year
    以及全部剧照的原图 URL

**不抓**：影片的风格描述。风格拆解在 fv_data.py 里手写 —— 那是「解读」，
不是「抓取」，把它自动化只会得到一段谁都能说的废话。

## 版权

film-grab 每页都写着「Images are not permitted for commercial use」。
剧照是版权作品，所以：

  · 卡片正文**只记外链**，不嵌本地图（别人 clone 后有网就能看）
  · 本地副本进 99-attachments/images-films/，该目录已 gitignore，
    纯个人研究参考，不随仓库分发
  · 默认只下前 N 张（够做视觉参考），不做整站镜像

## 用法

    python3 fv_fetch.py --check              # 只验证 14 个画廊页还通不通
    python3 fv_fetch.py --fetch              # 抓元数据 + 剧照清单（不下图）
    python3 fv_fetch.py --download           # 上面 + 下载本地参考图
    python3 fv_fetch.py --download --per 6   # 每部片只下 6 张
    python3 fv_fetch.py --slug villeneuve-dune
"""

import argparse
import html as htmllib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fv_data  # noqa: E402
import fv_core  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
# 每张图之间的间隔。实测 0.35s 连续下 14 部片会被限流断连；
# 放慢到 1.2s 后稳定。这不是效率问题，是别把别人的站点当 CDN 薅。
FETCH_PAUSE = 1.2
DATA_DIR = os.path.join(HERE, "_data", "films")
IMG_DIR = fv_core.STILLS_DIR          # 99-attachments/images-films/（gitignore）
CORPUS_DIR = os.path.join(VAULT, "40-films", "_剧照语料")   # 剧照索引页（进版本库）

# 页面上的字段名 → 我们内部统一的 key。
# 为什么要有这张表而不是直接字符串匹配：film-grab 的写法有过变动，
# 「Director of Photography」和「Directors of Photography」都出现过，
# 「:」有时在 <span> 里有时在外面。统一在这里收敛。
FIELD_KEYS = [
    ("director", ("director",)),
    ("cinematography", ("director of photography", "directors of photography", "cinematography")),
    ("production_design", ("production design", "production designer", "production designers")),
    ("costume_design", ("costume design", "costume designer", "costume designers")),
    ("year", ("year",)),
]


# ------------------------------------------------------------------ 解析
def _text(s):
    """去标签 + 解实体 + 压空白。"""
    s = re.sub(r"<[^>]+>", "", s or "")
    s = htmllib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def _label_and_value(p_html):
    """从一段 <p> 里取出 (字段名, 值)。

    写法在不同页面上不一样，两种都见过：
        <p><span ...>Director</span>: <a>Andrei Tarkovsky</a></p>
        <p><span ...>Director: <a>Satoshi Kon</a></span></p>
    所以先把整个 <p> 拍平成纯文本、按第一个「:」切，标签名小写比对。
    值的取法要特别处理**多值**：摄影指导常常是两个人用 & 连接，
    拍平会丢掉分隔，于是这里改成收集冒号之后的全部 <a> 文本。
    """
    flat = _text(p_html)
    if ":" not in flat:
        return None, None
    label = flat.split(":", 1)[0].strip().lower()
    label = re.sub(r"\s+", " ", label)
    # 值优先从冒号之后的 <a> 里取（保留多值与顺序）
    tail_html = p_html
    m = re.search(r":", _text_only_positions(p_html, flat))
    anchors = re.findall(r"<a\b[^>]*>(.*?)</a>", tail_html, re.S | re.I)
    anchors = [_text(a) for a in anchors if _text(a)]
    if anchors:
        val = " & ".join(anchors)
    else:
        val = flat.split(":", 1)[1].strip()
    return label, val


def _text_only_positions(_html, flat):
    """占位：值的锚点提取已由 anchors 分支处理，这里只需返回 flat 供冒号定位。"""
    return flat


def parse_movie(page_html):
    """把一页画廊 HTML 解析成结构化的 {title, director, year, crew, stills}。

    缺字段是常态（有的片没写美术指导），一律留空而不是抛异常 ——
    抓取器的职责是把**能拿到的**拿到，缺失由上层标出来。
    """
    m = {"title": "", "director": "", "year": None, "crew": {}, "stills": [],
         "director_key": ""}

    t = re.search(r"<title>(.*?)</title>", page_html, re.S | re.I)
    if t:
        title = _text(t.group(1))
        # 「Stalker – [FILMGRAB]」→「Stalker」
        title = re.sub(r"\s*[–—-]\s*\[?FILMGRAB\]?\s*$", "", title, flags=re.I)
        title = re.sub(r"\s*\[FILMGRAB\]\s*$", "", title, flags=re.I).strip()
        m["title"] = title

    # 元数据：只扫正文段，避免命中导航/侧栏里的同名文字
    body = page_html
    em = re.search(r'<div class="entry-content">', page_html)
    if em:
        body = page_html[em.start():em.start() + 20000]

    for p in re.findall(r"<p\b[^>]*>(?:(?!</p>).)*?</p>", body, re.S | re.I):
        label, val = _label_and_value(p)
        if not label or not val:
            continue
        for key, names in FIELD_KEYS:
            if label not in names:
                continue
            if key == "year":
                ym = re.search(r"\d{4}", val)
                if ym:
                    m["year"] = int(ym.group(0))
            elif key == "director":
                m["director"] = val
                dm = re.search(r'/category/(?:directors/)?([a-z0-9\-]+)/', p, re.I)
                if dm:
                    m["director_key"] = dm.group(1)
            else:
                m["crew"][key] = val
            break

    # 剧照：只要原图。thumb 缩略图是另一种尺寸的同一张图，混进来会让每张重复一遍。
    #
    # ⚠ 实测坑：**一部分老页面（2014 年前后那批）的图片 URL 里是裸空格**，
    # 写作 `photo-gallery/01 (494).jpg`；新页面则是 `%20` 编码。
    # 早先的正则排除了空白字符，于是 Stalker / 花样年华 / 闪灵 这批
    # 一律产出 0 张剧照 —— 而且看起来像「这些页面恰好没有图」。
    # 所以这里允许空格，把终止条件交给引号与标签边界；
    # 同时在输出侧统一编码成 %20，让「同一个 URL」只有一种写法，
    # 否则本地缓存键和卡片外链会随页面写法漂移。
    seen = []
    raw = re.findall(
        r'https://film-grab\.com/wp-content/uploads/photo-gallery/'
        r'([^"\'>]+?\.(?:jpe?g|png))',
        page_html, re.I)
    for u in raw:
        u = u.strip()
        u = html_quote(u, safe="/()!~*'_-.,%")
        # ⚠ 排除缩略图**不能只写 `(?!thumb/)`**：那个只挡紧跟
        # `photo-gallery/` 的缩略图。真实页面上还有嵌套一层路径的写法 ——
        #   …/photo-gallery/imported_from_media_libray/ran001.jpg      （原图）
        #   …/photo-gallery/imported_from_media_libray/thumb/ran001.jpg （缩略图）
        # 实测《乱》因此把每张画面记了两遍：报 130 张，实际 65 张；
        # 全库报 1001 张，实际 501 张。这个错会一路传到卡片的「共链接」上。
        if "/thumb/" in u or u.startswith("thumb/"):
            continue
        if u not in seen:
            seen.append(u)
    m["stills"] = ["https://film-grab.com/wp-content/uploads/photo-gallery/" + u
                   for u in seen]
    return m


def html_quote(s, safe="/"):
    """把裸空格等字符编码掉，但**不动已经编码的部分**（% 放行）。

    直接用 urllib.parse.quote 会把已有的 `%20` 二次编码成 `%2520`，
    所以先把 % 放进 safe 里。
    """
    return urllib.parse.quote(s, safe=safe)


def looks_ok(parsed):
    """判断这次解析是不是「真的拿到东西了」。

    这一条是为失败模式①服务的：站点改版后，解析器会安静地返回
    「0 张剧照」，如果把它当成成功，生成出来的就是一堆没有剧照的卡，
    而且没有任何报警。宁可在这里判定失败。
    """
    if not parsed:
        return False
    if not parsed.get("title"):
        return False
    if not parsed.get("stills"):
        return False
    if not (parsed.get("year") or parsed.get("director")):
        return False
    return True


# ------------------------------------------------------------------ 网络
def get_url(url, timeout=40, binary=False, opener=None, retries=4, backoff=2.0):
    """抓一个 URL。**瞬时错误要重试**，内容错误（4xx）不重试。

    ## 为什么要重试

    实测：以 0.35s 间隔连续下载 14 部片的剧照时，站点开始返回
    `URLError: EOF occurred in violation of protocol (_ssl.c:1129)` ——
    那是**限流**（连接被中途断开），不是内容问题。第一版没有重试，
    结果是 12/14 部片直接判定失败、一张都下不来。

    所以这里对瞬时错误做指数退避重试；而 404/403 这类是**内容问题**，
    重试既没用又白占站点配额，立刻抛出去。

    `opener` 只为测试注入（不联网），生产走 urllib。
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
    })
    _open = opener or (lambda u, timeout=timeout: urllib.request.urlopen(u, timeout=timeout))
    last = None
    for attempt in range(max(1, retries)):
        try:
            with _open(req, timeout=timeout) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError:
            # 4xx/5xx：内容或权限问题，重试没有意义
            raise
        except Exception as e:                      # 瞬时网络错误 → 退避重试
            last = e
            if attempt < retries - 1 and backoff:
                time.sleep(backoff * (2 ** attempt))
    # 全失败时把「很可能是限流」这层判断讲出来 —— 否则使用者只会看到
    # 一串 SSL 报错，不知道等一会儿再跑就好
    raise RuntimeError("%s（连续 %d 次失败；若为 EOF/SSL 断连，通常是站点限流，"
                       "等几分钟再跑，已下好的会跳过）" % (last, retries))


def fetch_one(film):
    """抓一部片。失败时返回 (None, 原因)，**不静默返回空**。"""
    url = film["filmgrab"]
    try:
        page = get_url(url)
    except urllib.error.HTTPError as e:
        return None, "HTTP %s" % e.code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, str(e)[:80])
    m = parse_movie(page)
    if not looks_ok(m):
        return None, "结构不匹配（拿到 %d 张剧照）" % len(m.get("stills") or [])
    m["slug"] = film["slug"]
    m["filmgrab"] = url
    return m, None


def load_saved(slug):
    """读已缓存的元数据；没有则 None。"""
    p = os.path.join(DATA_DIR, slug + ".json")
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            m = json.load(f)
        return m if m.get("stills") else None
    except Exception:
        return None


def metadata_for(film, use_cache=True):
    """取一部片的元数据：**优先读缓存**，缓存缺失才联网。

    ## 为什么要这条路径

    `--download` 原来对每部片都先联网抓一遍画廊页。而元数据一旦抓全，
    再抓就是白烧请求 —— 站点正在限流时，这等于自己把自己推向更难的境地。
    更糟的是**耦合**：元数据抓失败就 `continue`，那部片的图片一张都不下。
    实测一轮下来 55/100 部被整体跳过，尽管它们的元数据就在缓存里。

    返回 (metadata, 原因)。缓存命中时原因里写明「缓存」，便于分辨。
    """
    if use_cache:
        m = load_saved(film["slug"])
        if m:
            # 补齐可能缺的字段（老缓存可能没有 slug/filmgrab）
            m.setdefault("slug", film["slug"])
            m.setdefault("filmgrab", film["filmgrab"])
            return m, "缓存"
    return fetch_one(film)


def save(m):
    os.makedirs(DATA_DIR, exist_ok=True)
    p = os.path.join(DATA_DIR, m["slug"] + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, sort_keys=True)
    return p


# 每下这么多张就长歇一次。实测连续下会被限流断连；
# 分批 + 长歇比「失败重试」稳，也更不像在薅别人的站点。
BATCH = 25
BATCH_PAUSE = 20.0


def download_stills(film, m, per=8, quiet=False):
    """下载本地私有参考图。返回 (下载数, 跳过数)。

    `per=0` 表示全量。文件名带序号 —— 与卡片里的编号一一对应，方便对着看。
    已存在且 >4KB 的直接跳过（断点续下）。
    """
    d = os.path.join(IMG_DIR, film["slug"])
    os.makedirs(d, exist_ok=True)
    got, skipped = 0, 0
    done = 0
    sel = m["stills"] if per in (0, None) else m["stills"][:per]
    for i, u in enumerate(sel, 1):
        ext = os.path.splitext(urllib.parse.urlparse(u).path)[1] or ".jpg"
        p = os.path.join(d, "%02d%s" % (i, ext))
        if os.path.exists(p) and os.path.getsize(p) > 4096:
            skipped += 1
            continue
        try:
            with open(p, "wb") as f:
                f.write(get_url(u, binary=True))
            got += 1
            done += 1
            if done % BATCH == 0:
                time.sleep(BATCH_PAUSE)
            else:
                time.sleep(FETCH_PAUSE)   # 对站点客气一点，别把它当 CDN 薅
        except Exception as e:
            if os.path.exists(p):
                os.remove(p)        # 半张图比没有更糟：会让「本地有图」的判断说谎
            # **一张失败不要中断整片**：记下来继续，最后如实报告
            skipped += 1
            if not quiet:
                sys.stderr.write("\n    ! %s 失败：%s\n" % (os.path.basename(p), str(e)[:70]))
    return got, skipped


# ------------------------------------------------------------------ 语料索引页
def corpus_note(by_director, crawled):
    """40-films/_剧照语料/README.md —— 剧照索引（进版本库，只含外链）。

    为什么要有这一页：卡片正文只放少量剧照（保持可读），
    完整的剧照清单（几十张）放这里，想挑参考图时一次看全。
    """
    L = ["---", "type: 剧照语料", "标签:", "  - 电影", "  - 剧照", "---", "",
         "# 剧照语料索引", "",
         "> [!warning] 版权",
         "> 这些剧照的版权属于原片方。**本页只索引 film-grab 的原图外链**，",
         "> 不转载图片本身。个人研究参考可以点开看；商用请自行取得授权",
         "> （film-grab 页面写明 *Images are not permitted for commercial use*）。",
         "",
         "> [!info] 本地私有副本",
         "> 跑 `python3 .repo/fv_fetch.py --download` 会把前若干张存到",
         "> `99-attachments/images-films/`（已 gitignore，不随仓库发布）供离线看。",
         "> 卡片正文**只记外链**，所以你 clone 之后有网就能看到图。",
         "",
         "| 导演 | 电影 | 年份 | 剧照数 | 画廊 |", "|---|---|---|---|---|"]
    n = 0
    for d in by_director:
        for f in d["films"]:
            c = crawled.get(f["slug"]) or {}
            cnt = len(c.get("stills") or [])
            n += cnt
            L.append("| %s | %s | %s | %d | [film-grab](%s) |"
                     % (f["director_zh"], f["title_zh"], f["year"], cnt, f["filmgrab"]))
    L += ["", "合计 **%d** 张剧照外链。抓取时间见 `.repo/_data/films/*.json`。" % n, ""]
    return "\n".join(L)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="从 film-grab 抓电影班底与剧照外链")
    ap.add_argument("--check", action="store_true", help="只验证画廊页可达、结构仍匹配")
    ap.add_argument("--fetch", action="store_true", help="抓元数据与剧照清单（不下载图片）")
    ap.add_argument("--refresh-meta", action="store_true",
                    help="即使有缓存也重新抓画廊页元数据（默认下载时复用缓存）")
    ap.add_argument("--download", action="store_true", help="抓取并下载前若干张本地参考图")
    ap.add_argument("--per", type=int, default=8,
                    help="每部片下载张数上限，默认 8；**0 表示全量下载**"
                         "（1001 张约 133MB，是本地私有参考，gitignore）")
    ap.add_argument("--slug", help="只处理某一部片")
    a = ap.parse_args()

    if not (a.check or a.fetch or a.download):
        ap.print_help()
        print("\n至少给一个动作：--check / --fetch / --download")
        return 0

    films = [f for f in fv_data.FILMS if not a.slug or f["slug"] == a.slug]
    if not films:
        print("没找到片子：%s" % a.slug)
        return 1

    # `--download` 默认**复用缓存的元数据**，不再逐片联网抓画廊页。
    #
    # 元数据抓一次就够了（抓全后存在 _data/films/<slug>.json）。每次下载都
    # 重抓会白烧请求、把自己推向更重的限流；更糟的是元数据失败会连累图片
    # 下载（实测一轮 55/100 部因此被整体跳过）。要强制重抓用 --refresh-meta。
    use_cache = bool(a.download) and not a.refresh_meta
    reused = 0
    ok, failed = [], []
    for f in films:
        m, why = metadata_for(f, use_cache=use_cache)
        if m and why == "缓存":
            reused += 1
        if not m:
            failed.append((f["slug"], why))
            print("  ✗ %-38s %s" % (f["slug"], why))
            continue
        ok.append((f, m))
        print("  %s %-38s %s 年，%d 张剧照，班底 %d 项"
              % ("·" if why == "缓存" else "✓", f["slug"], m["year"],
                 len(m["stills"]), len(m["crew"])))
        if (a.fetch or a.download) and why != "缓存":
            save(m)
        if a.download:
            got, sk = download_stills(f, m, per=a.per)
            print("      下载 %d 张，已有 %d 张 → %s"
                  % (got, sk, os.path.join("99-attachments/images-films", f["slug"])))

    if reused:
        print("\n（其中 %d 部复用了缓存元数据，未联网抓画廊页）" % reused)
    print("\n成功 %d / 失败 %d" % (len(ok), len(failed)))
    if failed:
        print("\n失败的片子（**必须处理，不能当成空结果放过**）：")
        for s, w in failed:
            print("  · %-38s %s" % (s, w))
        return 1
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 fv_fetch.py --fetch",
          ["从 film-grab 抓电影班底（导演/摄影/美术/服装/年份）与剧照外链。",
           "  --check     只验证画廊页可达、结构仍匹配",
           "  --fetch     抓元数据与剧照清单（不下载图片）",
           "  --download  抓取并下载前若干张本地参考图（--per N 控制张数）",
           "",
           "剧照版权属原片方（film-grab 写明 non-commercial）。",
           "卡片会**本地嵌入**每部 6 张代表帧（约 15 MB 随仓库走）；",
           "其余语料留在本地做分析，由 build_vault.py 逐文件忽略。"])
    sys.exit(main())
