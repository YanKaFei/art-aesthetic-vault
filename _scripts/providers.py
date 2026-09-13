# -*- coding: utf-8 -*-
"""
多数据源提供器 —— 每个函数返回统一结构的作品列表。

已实测可用的免密钥源：
  · 克利夫兰艺术博物馆  CC0       openaccess-api.clevelandart.org
  · 芝加哥艺术博物馆    CC0       api.artic.edu            ← 复测后加入
  · 大都会艺术博物馆    CC0       collectionapi.metmuseum.org
  · 维基共享资源        逐条标注   commons.wikimedia.org

⚠️ 芝加哥这个源曾经被 curl 测出 403 而误判为「图片有 Cloudflare 保护」。
   用 Python requests 复测是 200 —— 出口代理会拦 curl 的 TLS 指纹但放过 Python。
   **判断可达性必须用最终要用的客户端。**

统一返回字段：
  title / artist / date / medium / image_url / image_url_hi /
  page_url / source / license / license_url
"""

import json
import re
import ssl
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

UA = "ArtAestheticVault/1.0 (personal Obsidian reference library; non-commercial)"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CLE_API = "https://openaccess-api.clevelandart.org/api/artworks/"
MET_SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1/search"
MET_OBJECT = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
ARTIC_SEARCH = "https://api.artic.edu/api/v1/artworks/search"
ARTIC_IIIF = "https://www.artic.edu/iiif/2"


def get_json(url, tries=3, timeout=45):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                return None                     # 大都会的失效条目，静默跳过
            if i < tries - 1:
                time.sleep(1.5 * (i + 1))
    print("    ! %s -> %s" % (url[:88], last))
    return None


# Wikimedia 对 upload.wikimedia.org 的原始文件限流很严（HTTP 429），
# 官方要求改用缩略图。这里做两件事：统一走缩略图 URL，并对 429 退避重试。
_wm_last = [0.0]


def _is_wikimedia(url):
    return "wikimedia.org" in (url or "")


def download(url, dest, tries=4):
    if not url:
        return False
    for i in range(tries):
        try:
            if _is_wikimedia(url):
                # 同一域名下至少间隔 1.2 秒，避免触发 429
                gap = time.time() - _wm_last[0]
                if gap < 1.2:
                    time.sleep(1.2 - gap)
                # 有些文件只预渲染了部分宽度，请求别的宽度会 400。
                # 先按需缩小，再真正发请求。
                url = _fit_width(url)
            req = urllib.request.Request(url, headers={
                "User-Agent": UA, "Referer": "https://commons.wikimedia.org/"})
            with urllib.request.urlopen(req, timeout=90, context=CTX) as r:
                blob = r.read()
                ctype = r.headers.get("Content-Type", "")
            _wm_last[0] = time.time()
            if len(blob) < 2048:
                raise ValueError("too small: %d bytes" % len(blob))
            if "image" not in ctype:
                raise ValueError("not an image: %s" % ctype)
            with open(dest, "wb") as f:
                f.write(blob)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 400 and _is_wikimedia(url):
                nxt = _shrink(url)
                if nxt:
                    url = nxt
                    time.sleep(1.0)
                    continue
                if i == tries - 1:
                    print("    ! 该文件无可用的预渲染尺寸，跳过 %s" % url[:60])
                    return False
                continue
            if e.code == 429:
                if i == tries - 1:
                    print("    ! 被 Wikimedia 限流，跳过 %s" % url[:60])
                    return False
                time.sleep(4.0 * (i + 1))          # 429 要等久一点
                continue
            if i == tries - 1:
                print("    ! download failed %s -> %s" % (url[:70], e))
                return False
            time.sleep(1.5 * (i + 1))
        except Exception as e:
            if i == tries - 1:
                print("    ! download failed %s -> %s" % (url[:70], e))
                return False
            time.sleep(1.5 * (i + 1))
    return False


def _shrink(url):
    """把缩略图 URL 里的宽度换成下一个更小的标准宽度；没有更小的就返回 None。"""
    m = re.search(r"/(\d+)px-", url or "")
    if not m:
        return None
    cur = int(m.group(1))
    smaller = [w for w in reversed(ALLOWED_W) if w < cur]
    if not smaller:
        return None
    return url[:m.start(1)] + str(smaller[0]) + url[m.end(1):]


def _fit_width(url):
    """把任意宽度吸附到能命中的标准宽度（默认取 1024 以下的最大值）。"""
    return re.sub(r"/\d+px-", "/%dpx-" % snap_width(1024), url or "")


# Wikimedia 现在只对「预渲染的标准宽度」提供缩略图，其它宽度会返回
# HTTP 400「Use thumbnail sizes listed on ...」。所以必须吸附到白名单。
ALLOWED_W = (320, 640, 800, 1024, 1280, 1920, 2560)


def snap_width(w):
    cand = [x for x in ALLOWED_W if x <= (w or 0)]
    return cand[-1] if cand else ALLOWED_W[0]


def thumb_url(orig, width=1024):
    """把 Commons 的原始文件 URL 转成缩略图 URL。
    原文件 URL 会被 Wikimedia 严格限流，缩略图则宽松得多。"""
    if not orig or "/commons/" not in orig or "/thumb/" in orig:
        return orig
    name = orig.rsplit("/", 1)[-1]
    return orig.replace("/commons/", "/commons/thumb/", 1) + "/%dpx-%s" % (width, name)


# ------------------------------------------------------------------ 授权过滤
PD_MARKERS = ("public domain", "pd-", "cc0", "pdm", "no restrictions", "pd self")
CCBY_MARKERS = ("cc by", "cc-by", "cc by-sa", "cc-by-sa")


def license_ok(short_name, allow_ccby=False):
    """只接受公共领域 / CC0；allow_ccby=True 时额外接受 CC BY 系列（需署名）。"""
    s = (short_name or "").lower()
    if any(m in s for m in PD_MARKERS):
        return True
    if allow_ccby and any(m in s for m in CCBY_MARKERS):
        return True
    return False


# ------------------------------------------------------------------ 克利夫兰
def from_cleveland(query, want):
    url = CLE_API + "?" + urllib.parse.urlencode({
        "q": query, "cc0": 1, "has_image": 1, "limit": max(want * 3, 12),
    })
    js = get_json(url)
    out = []
    for a in (js or {}).get("data", []):
        imgs = a.get("images") or {}
        pick = imgs.get("web") or imgs.get("print") or imgs.get("full") or {}
        src = pick.get("url")
        if not src:
            continue
        hi = (imgs.get("print") or imgs.get("full") or {}).get("url") or src
        creators = a.get("creators") or []
        artist = creators[0].get("description", "") if creators else "佚名"
        artist = re.sub(r"\s*\(.*?\)\s*", " ", artist).strip() or "佚名"
        out.append({
            "title": (a.get("title") or "无题").strip(),
            "artist": artist,
            "date": (a.get("creation_date") or "").strip(),
            "medium": (a.get("technique") or "").strip(),
            "image_url": src, "image_url_hi": hi,
            "page_url": "https://www.clevelandart.org/art/%s" % a.get("accession_number", ""),
            "source": "克利夫兰艺术博物馆",
            "license": "CC0 1.0 公共领域奉献",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        })
    return out


# ------------------------------------------------------------------ 芝加哥
# 公共领域作品的 IIIF 图片按 CC0 发布（官方声明见 license_url）。
# 用 IIIF 分级取图：843px 约 225KB 做笔记嵌图，1686px 约 950KB 作高清链接。
# 注意 "full" 尺寸会返回 403，必须用带数字的尺寸。
def from_artic(query, want):
    js = get_json(ARTIC_SEARCH + "?" + urllib.parse.urlencode({
        "q": query, "limit": min(want * 4, 60),
        "fields": "id,title,artist_title,date_display,medium_display,image_id,"
                  "is_public_domain,department_title,classification_title,place_of_origin",
    }))
    out = []
    for a in (js or {}).get("data", []):
        # 只要公共领域 + 有图。AIC 的 bool 查询参数格式特殊，
        # 客户端过滤比构造查询更稳。
        if not a.get("is_public_domain") or not a.get("image_id"):
            continue
        iid = a["image_id"]
        out.append({
            "title": (a.get("title") or "无题").strip(),
            "artist": (a.get("artist_title") or "佚名").strip(),
            "date": (a.get("date_display") or "").strip(),
            "medium": (a.get("medium_display") or "").strip(),
            "image_url": "%s/%s/full/843,/0/default.jpg" % (ARTIC_IIIF, iid),
            "image_url_hi": "%s/%s/full/1686,/0/default.jpg" % (ARTIC_IIIF, iid),
            "page_url": "https://www.artic.edu/artworks/%s" % a.get("id"),
            "source": "芝加哥艺术博物馆",
            "license": "CC0 1.0 公共领域奉献",
            "license_url": "https://www.artic.edu/open-access/open-access-images",
        })
    return out


# ------------------------------------------------------------------ 大都会
def from_met(query, want):
    js = get_json(MET_SEARCH + "?" + urllib.parse.urlencode({
        "q": query, "hasImages": "true", "isPublicDomain": "true",
    }))
    ids = (js or {}).get("objectIDs") or []
    out = []
    for oid in ids[: min(want * 2, 18)]:
        if len(out) >= want:
            break
        o = get_json(MET_OBJECT + str(oid))
        if not o or not o.get("isPublicDomain"):
            continue
        nm = (o.get("objectName") or "").lower()
        if nm and not any(k in nm for k in ("painting", "drawing", "print", "photograph",
                                            "manuscript", "album", "miniature", "scroll",
                                            "woodblock", "calligraphy", "textile")):
            continue
        src = o.get("primaryImageSmall") or o.get("primaryImage")
        if not src:
            continue
        out.append({
            "title": (o.get("title") or "无题").strip(),
            "artist": (o.get("artistDisplayName") or "佚名").strip(),
            "date": (o.get("objectDate") or "").strip(),
            "medium": (o.get("medium") or "").strip(),
            "image_url": src, "image_url_hi": o.get("primaryImage") or src,
            "page_url": o.get("objectURL") or "",
            "source": "大都会艺术博物馆",
            "license": "CC0 1.0（Open Access 公共领域）",
            "license_url": "https://www.metmuseum.org/about-the-met/policies-and-documents/open-access",
        })
        time.sleep(0.2)
    return out


# ------------------------------------------------------------------ 维基共享
def _strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def from_commons(query, want, allow_ccby=False, width=1024):
    """在 Commons 的 File 命名空间搜索，逐条读 extmetadata 判断授权。
    只收 Public domain / CC0（可选 CC BY），其余一律丢弃。"""
    url = COMMONS_API + "?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": "filetype:bitmap " + query,
        "gsrnamespace": 6, "gsrlimit": min(want * 5, 50),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
        "iiurlwidth": snap_width(width),
    })
    js = get_json(url, timeout=50)
    pages = ((js or {}).get("query") or {}).get("pages") or {}
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        lic = _strip_html(em.get("LicenseShortName", {}).get("value"))
        if not license_ok(lic, allow_ccby):
            continue
        # 直接用 API 返回的 thumburl 并不可靠：有些文件只预渲染了部分宽度，
        # 构造出来的 /NNNpx- 链接会返回 400。Special:FilePath 由服务端负责
        # 选尺寸并 302 到合法缩略图，是唯一稳定的下载入口。
        title = p.get("title", "")[5:]                     # 去掉 "File:"
        if re.search(r"\.(svg|pdf|tif|tiff|webm|ogv)$", title, re.I):
            continue
        orig_w = ii.get("width") or 0
        if orig_w and orig_w < 500:
            continue                      # 太小的图做参考没意义
        fname = title.replace(" ", "_")
        thumb = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
                 + urllib.parse.quote(fname, safe=",_-()!'.~")
                 + "?width=%d" % snap_width(min(width, orig_w) if orig_w else width))
        artist = _strip_html(em.get("Artist", {}).get("value")) or "佚名"
        artist = re.sub(r"\s+", " ", artist)[:80]
        # extmetadata 里 Artist 常是上传者、DateTimeOriginal 常是拍摄时间、
        # ObjectName 就是文件名 —— 先原样收下，紧接着交给 clean_attribution
        # 洗一遍再入库，避免脏值进 JSON（渲染时还会再洗一次兜底）。
        out.append(clean_attribution({
            "title": re.sub(r"\.(jpe?g|png|gif)$", "", title, flags=re.I).replace("_", " ").strip(),
            "artist": artist,
            "date": _strip_html(em.get("DateTimeOriginal", {}).get("value"))[:40],
            "medium": _strip_html(em.get("ObjectName", {}).get("value"))[:60],
            "image_url": thumb,
            "image_url_hi": ii.get("url") or ii.get("thumburl") or thumb,
            "page_url": "https://commons.wikimedia.org/wiki/File:%s" % urllib.parse.quote(title.replace(" ", "_")),
            "source": "维基共享资源",
            "license": lic or "见文件页",
            "license_url": "https://commons.wikimedia.org/wiki/Commons:Licensing",
            "raw_title": title,
        }))
        if len(out) >= want * 2:
            break
    return out


# ---------------------------------------------------------------- 署名清洗
# 维基共享资源的 extmetadata 有三个字段名不副实，直接采信会产出
#   **Daderot · 2016-12-01 15:50:04 · John the Baptist, Crete, Late Byzantine, 1600s**
# 这种卡片 —— 把上传者当画家、把拍摄时间当作品年代、把文件名当材质。
# 一个标着「公共领域、可自由使用」的参考库出现这种署名，比图少更伤可信度。
#
# 下面这份逻辑在**两处**使用，保持单一实现：
#   1. from_commons 抓取时清洗 —— 存进 JSON 的就是干净数据
#   2. build_vault.py 渲染时再洗一遍 —— 防止历史 JSON 里的脏值漏到卡片上
_NON_PERSON = {
    "late", "early", "high", "middle", "northern", "southern", "italian", "french",
    "dutch", "spanish", "german", "english", "british", "american", "chinese",
    "japanese", "persian", "mughal", "byzantine", "romanesque", "gothic",
    "renaissance", "baroque", "rococo", "neoclassical", "romantic", "realist",
    "impressionist", "modern", "contemporary", "school", "style", "art", "artist",
    "painting", "mural", "fresco", "mosaic", "icon", "manuscript", "print",
    "crete", "cretan", "sinai", "athens", "rome", "paris", "london",
    "cyanotype", "albumen", "daguerreotype", "photograph", "photographer",
    "attributed", "unknown", "anonymous", "master", "workshop", "follower",
    "dynasty", "period", "era", "century", "c.", "ca.", "circa",
    "song", "tang", "yuan", "ming", "qing", "edo", "meiji", "heian",
    "album", "leaf", "scroll", "handscroll", "screen", "panel", "wood",
}

UPLOADER_HINT = (
    "daderot", "didier descouens", "egorovasvetlana", "gary todd", "cbl62",
    "gryffindor", "hiart", "paradise chronicle", "rijksmuseum", "library of congress",
    "christies", "sotheby", "bonhams", "museum ", "museo ", "gallery",
    "from xinzheng", "unknown author", "anonymous", "未署名", "uploaded by",
    "wikimedia", "wikipedia", "user:", "digital id",
)
# 带时分秒的一定是拍摄/上传时间 —— 作品年代不会精确到秒
# 拍摄/上传时间：带时分秒的、或只有年-月/年-月-日的，都不是作品年代
_TIMESTAMP_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}")
_PHOTO_DATE_RE = re.compile(r"^\d{4}(-\d{2}){0,2}$")
# 标题里可用的年份/年代片段，如 "1600s"、"c. 1500"、"1934"、"1852-54"
_YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-2][0-9])\s*(?:s\b|–|-)?(?:\s*(\d{2,4}))?")
# 材质词：从标题里捞，捞不到就留空（不要拿文件名冒充材质）
_MEDIUM_WORDS = ("oil on canvas", "tempera", "gold leaf", "watercolor", "watercolour",
                 "gouache", "ink on paper", "ink and", "woodblock", "wood engraving",
                 "etching", "engraving", "lithograph", "aquatint", "cyanotype",
                 "albumen", "gelatin silver", "collodion", "fresco", "mural",
                 "opaque watercolor", "album leaf", "handscroll", "hanging scroll",
                 "screen", "tapestry", "mosaic", "stained glass", "ivory")


# Commons 的字段里会混进 Wikidata 机器语法和编目口癖，实测这些形态：
#   medium: "… title QS:P1476,en:\"The Pink Candle\" label QS:Lfr,…"
#   artist: "Designed by William Morris, British" / "Theo van Doesburg AB4075"
#   date:   "circa 1883 date QS:P571,+1883-00-00T00:00:00Z/7"
# 直接渲染就是把机器语法摆给用户看。
_WIKI_QS_RE = re.compile(r"\s*(?:title|label|date|object name)\s+QS:.*$", re.I)
_ARTIST_PREFIX_RE = re.compile(r"^(designed by|made by|after|attributed to|circle of|"
                               r"follower of|manner of|workshop of|school of)\s+", re.I)
_ARTIST_CATALOG_RE = re.compile(r"\s+[A-Z]{1,4}[- ]?\d{3,}\s*$")
# 共享资源里常见的前缀噪音："Digital ID- 419707. Atkins, Anna"
_ARTIST_DIGITALID_RE = re.compile(r"^digital\s*id[-–: ]*[\w.\-]*\s*", re.I)


def strip_wiki_junk(t):
    """清掉 Wikidata 机器语法与编目口癖，返回干净文本。"""
    t = _WIKI_QS_RE.sub("", t or "").strip(" ,;")
    return re.sub(r"\s{2,}", " ", t).strip()


def clean_artist_name(a):
    """把「Designed by X, British」「X AB4075」这类整成 X。"""
    a = strip_wiki_junk(a)
    a = _ARTIST_PREFIX_RE.sub("", a).strip()
    a = _ARTIST_DIGITALID_RE.sub("", a).strip()
    a = _ARTIST_CATALOG_RE.sub("", a).strip(" ,;")
    # 去掉末尾的国籍/身份词（"William Morris, British" → "William Morris"）
    parts = [x.strip() for x in a.split(",")]
    while len(parts) > 1 and parts[-1].lower() in _NON_PERSON:
        parts.pop()
    return ", ".join(parts).strip(" ,;")


def clean_attribution(w):
    """把 artist / date / medium 三个字段里的脏值换成得体内容，就地修改并返回 w。"""
    artist = clean_artist_name(w.get("artist"))
    date = strip_wiki_junk(w.get("date"))
    medium = strip_wiki_junk(w.get("medium"))
    title = (w.get("title") or "").strip() or (w.get("raw_title") or "").strip()

    al = artist.lower()
    _words = [x.strip(",.()") for x in al.split() if x.strip(",.()")]
    _all_non_person = bool(_words) and all(x in _NON_PERSON for x in _words)
    if ((not artist) or any(h in al for h in UPLOADER_HINT)
            or _TIMESTAMP_RE.search(artist) or _all_non_person):
        # 认不出真作者就写「佚名」—— **绝不把上传者当画家**，
        # 也不把 "song dynasty" 这种时期标签当画家
        artist = "佚名"

    # 维基共享的 DateTimeOriginal 有时是 **Wikidata 快速陈述**：
    #   "circa 1883 date QS:P571,+1883-00-00T00:00:00Z/7"
    #   直接渲染出来就是机器语法，实测全库 13 处。
    if "QS:" in date:
        ym = re.search(r",\s*([+-]?\d{3,4})", date)
        head = date.split("date QS:")[0].strip(" ,;")
        date = head or (ym.group(1).lstrip("+-") if ym else "")
    date = re.sub(r"(\d+)\s+th\b", r"\1th", date)      # "17 th century" → "17th century"
    if _TIMESTAMP_RE.search(date) or _PHOTO_DATE_RE.match(date.strip()):
        # 带时分秒 / 纯日期的都当拍摄时间，改从标题里找作品年代
        date = ""
    if not date:
        m = _YEAR_RE.search(title)
        if m:
            date = m.group(0).strip()

    # 材质：等于标题、包含标题、或被标题包含 —— 都说明它不是材质
    if medium and (medium == title or medium in title or title in medium or len(medium) > 70):
        medium = ""
    if not medium:
        tl = title.lower()
        for mw in _MEDIUM_WORDS:
            if mw in tl:
                i = tl.index(mw)
                medium = title[i:i + 42].split(" - ")[0].strip(" ,.;")
                break

    w["artist"], w["date"], w["medium"] = artist, date, medium
    return w


def is_uploader_like(name):
    """判断一个「作者」是不是上传者/机构/时间戳，而不是画家。

    黑名单永远列不全（实测 Daderot、Gary Todd、Cbl62、Joaquín Martínez Rosado…
    一个接一个冒出来），所以这里只作为**辅助信号**；真正的判据是
    display_artist() 里的正向校验：作者必须对得上该流派自己的艺术家。
    """
    n = _norm(name or "")
    if not n:
        return True
    if any(h in n for h in UPLOADER_HINT):
        return True
    if _TIMESTAMP_RE.search(n):
        return True
    if re.search(r"\b(from|via|uploaded|photo(graph)? by|digital id|cc-by|unknown)\b", n):
        return True
    # 「姓, 名, 1799-1871」是**正常的署名格式**，别被数字规则误杀
    if re.match(r"^[\w'’\-]+\s*,\s*[\w'’\-]+(?:\s*,\s*\d{4})?$", n):
        return False
    if re.search(r"\d{3,}", n):          # 带长串数字的多半是文件名/编号
        return True
    return len(n) < 3


# 这些词是风格/时期/地名/材质，不是人名。恢复作者时若命中它们，
# 宁可写「佚名」—— 把 "Late Byzantine" 当成画家比留空更糟。



def _looks_like_person(name):
    """这个名字像不像人名。用来挡住 "song dynasty"、"Late Byzantine" 这类。"""
    words = [x.strip(",.;:()").lower() for x in (name or "").split() if x.strip(",.;:()")]
    if not words or len(words) > 3:
        return False
    if any(w in _NON_PERSON for w in words):
        return False
    return not re.search(r"\d", name or "")


def display_artist(w, keys, exclude=None, title_keys=None):
    """决定卡片上该显示谁为作者。**绝不把上传者当画家。**

    判据是正向的：作者必须能对上该流派自己的艺术家关键词
    （artist_matches）。对不上就试着从标题里**恢复**真作者，再不行写「佚名」。

    实测效果：
      "Diego Rivera Mural of Mexican History" + artist="Gary Todd from Xinzheng"
        → 标题开头就是 diego rivera → 恢复为 "Diego Rivera"
      "John the Baptist, Crete, Late Byzantine, 1600s…" + artist="Daderot"
        → 匿名圣像，恢复不出人 → "佚名"
    """
    a = (w.get("artist") or "").strip()
    # 1) 作者能对上该流派的艺术家 —— 直接用
    if a and not is_uploader_like(a) and artist_matches(w, keys, exclude, title_keys):
        return a
    raw = w.get("raw_title") or w.get("title") or ""
    # 2) 「画家名 - 作品名」/「作品名 by 画家名」这类明确格式
    rec = extract_artist_from_title(raw, keys)
    if rec:
        return rec
    # 3) 标题**靠前**位置出现某位艺术家的名字（"Diego Rivera Mural of…"）
    #    三个收紧点，都是实测踩出来的：
    #      · 取**最早**出现的 key —— 否则 "Anna Atkins algae cyanotype" 会被
    #        更靠后的 key "cyanotype" 匹配，返回整串标题
    #      · 剥掉开头的 "by" —— "Landscape …, by Paul Nash, 1934" 会得到 "by Paul Nash"
    #      · 非人名停用词 —— 否则匿名圣像的标题会返回 "Late Byzantine"（地名/风格词）
    low = raw.lower()
    best = None
    for k in (keys or []):
        if len(k) < 5:
            continue
        i = low.find(k.lower())
        if i < 0:
            i = _norm(raw).find(_norm(k))
        if 0 <= i <= 48 and (best is None or i < best[0]):
            best = (i, k)
    if best:
        i, k = best
        start = 0
        for c in ",;(":
            j = low.rfind(c, 0, i)
            if j + 1 > start:
                start = j + 1
        name = raw[start:i + len(k)].strip(" ,;.-·")
        name = re.sub(r"^(by|after|attributed to)\s+", "", name, flags=re.I).strip()
        if _looks_like_person(name) and len(name) > 3:
            return name
        kn = k.strip()
        if _looks_like_person(kn) and len(kn) > 3:
            return kn
    # 4) 「姓, 名, 生卒年」→「名 姓」（Anna Atkins 这类）
    m = re.match(r"^([A-Z][\w'’\-]+)\s*,\s*([A-Z][\w'’\-]+)(?:\s*,\s*\d{4})?\s*$", a)
    if m:
        return "%s %s" % (m.group(2), m.group(1))
    return "佚名"


PROVIDERS = {
    "artic": from_artic,
    "cleveland": from_cleveland,
    "met": from_met,
    "commons": from_commons,
}


# ------------------------------------------------------------------ 平面作品
MEDIUM_OK = ("paint", "oil", "canvas", "panel", "watercolor", "water-colour", "watercolour",
             "tempera", "gouache", "paper", "drawing", "ink", "chalk", "lithograph",
             "woodcut", "print", "pastel", "charcoal", "graphite", "fresco", "mural",
             "crayon", "wash", "cartoon", "scroll", "sketch",
             "etching", "drypoint", "engraving", "aquatint", "mezzotint", "linocut",
             "serigraph", "screenprint", "monotype", "wood engraving", "poster",
             # 摄影与版画类风格需要
             "albumen", "gelatin", "photograph", "cyanotype", "daguerreotype",
             "collodion", "platinum print", "silver print", "bromide",
             # 东亚与伊斯兰
             "silk", "hanging scroll", "handscroll", "thangka", "pigment",
             "miniat", "illuminat", "calligraph", "gilt", "gold on")


# 维基共享资源上有大量 AI 生成图（标注 CC0），文件名常带这些标记。
# 一个「给 AI 生成做参考」的仓库里混进 AI 生成的图是致命的——
# 那等于用模型的输出当模型的参考。一律排除。
AI_MARKERS = ("dall-e", "dalle", "dall·e", "stable diffusion", "stablediffusion",
              "midjourney", "fooocus", "ai art", "ai-art", "aiart", "ai generated",
              "ai-generated", "aigenerated", "generated by", "text-to-image",
              "text to image", "novelai", "comfyui", "deepai", "craiyon",
              "artbreeder", "albedo", "nightcafe", "leonardo.ai", "firefly",
              "imagen", "flux.1", "sdxl", "checkpoint model", "diffusion model")


def is_ai_generated(w):
    hay = " ".join([(w.get("raw_title") or ""), (w.get("title") or ""),
                    (w.get("artist") or "")]).lower()
    return any(m in hay for m in AI_MARKERS)


def extract_artist_from_title(raw_title, keys):
    """共享资源的 Artist 字段常是上传者。文件名通常写成
    「画家名 - 作品名」或「作品名 by 画家名」，从中还原真正的作者。"""
    if not raw_title:
        return None
    t = raw_title.rsplit(".", 1)[0]
    cands = []
    if " - " in t:
        cands.append(t.split(" - ")[0])
    if " by " in t.lower():
        i = t.lower().rindex(" by ")
        cands.append(t[i + 4:])
    for c in cands:
        c = c.strip()
        if 3 < len(c) < 60 and any(k.lower() in c.lower() for k in (keys or [])):
            return c
    return None



# ---------------------------------------------------------------- 复制品 / 机构署名
# 这两个名单是**一次失败的批量补图**逼出来的。为了让 57 个 20 世纪流派有图，
# 我对它们跑了一遍重抓，结果混进来三类错误：
#
#   秘鲁邮票（图案是 Sabogal 的画）        → 是印刷品，不是画作本身
#   华纳兄弟的电影宣传剧照                 → 机构署名，且不是艺术作品
#   「Edward Payson Weston, 1839-1929」   → 人名撞车：照片拍的是**同名的一个人**，
#                                          不是摄影家 Edward Weston
#
# 这三类都不会被原有的「AI 生成 / 平面作品 / 作者匹配」挡住。
REPRO_WORDS = (
    "stamp", "postage", "postcard", "banknote", "bank note", "coin", "medal",
    "book cover", "album cover", "promotional", "publicity", "press photo",
    "press photograph", "film still", "movie still", "advertis", "poster",
    "matchbox", "cigarette card", "trade card", "lobby card", "screenshot",
    "logo", "letterhead", "currency", "reproduction of a stamp",
)

# 只收**明确不是艺术家**的机构名。
# 第一版把 museum / gallery / collection / library / institute 也写进来了，
# 结果把梵高的《L'Arlésienne》当成「机构署名」拒掉 —— 因为公共领域记录的
# author 字段常常填的是**收藏机构**而不是画家。名单宁窄勿宽：
# 漏掉一个机构，代价是少一张图；多写一个词，代价是误杀真作品。
CORPORATE_WORDS = (
    "bros", "brothers", "studios", "pictures", "inc", "ltd", "corp",
    "company", "co.", "agency", "news service", "post of", "post office",
)


def is_artifact_reproduction(w):
    """标题里出现「邮票 / 明信片 / 宣传剧照」这类词 → 不是艺术作品本身。

    刻意不收录裸的 "still" —— 那会把 still life（静物）整类误杀。
    """
    t = _norm(w.get("raw_title") or w.get("title"))
    return any(_norm(k) in t for k in REPRO_WORDS)


def is_corporate_artist(w):
    """作者字段是机构（华纳兄弟、秘鲁邮政、Bain News Service）→ 不是艺术家署名。"""
    a = _norm(w.get("artist") or "")
    if not a:
        return False
    return any(_norm(k) in a for k in CORPORATE_WORDS)


def looks_like_person_subject(w, keys):
    """匿名作品里，标题在讲**一个同名的人** → 人名撞车，不是这位艺术家的作品。

    实测：找 Edward Weston（摄影家）时抓到「Edward Payson Weston, 1839-1929」
    —— 那是一位同名的竞走名人，照片拍的是他。判据是标题里带生卒年
    （`1839-1929` 这种跨度），而且命中的关键词出现在标题里。
    生卒年是一个很强的人物传记信号，正常作品标题很少带。
    """
    if not keys:
        return False
    artist = _norm(w.get("artist") or "")
    # 只有当作者字段不可信（空 / 匿名 / 像上传者）时才启用这条
    if artist and not any(x in artist for x in ANON_ARTIST):
        return False
    t = _norm(w.get("raw_title") or w.get("title"))
    if not re.search(r"\b1[5-9]\d\d\s*[-–—]\s*(1[5-9]|20)\d\d\b", t):
        return False
    return any(_norm(k) in t for k in keys)

def is_flat_work(w):
    m = (w.get("medium") or "").lower()
    if not m:
        return True
    return any(k in m for k in MEDIUM_OK)


def _norm(s):
    """归一化：小写 + 去掉变音符号。

    必须做这一步 —— 实测 "Sesshū Tōyō" 因为 ū 和关键词 "sesshu" 的 u
    不是同一个字符而漏掉。同类问题还有 é / ñ / ō / ü 等一大类。
    """
    s = unicodedata.normalize("NFKD", (s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# 作者字段是这些时，说明没有具体作者，才允许退回用标题兜底匹配
ANON_ARTIST = ("佚名", "unknown", "anonymous", "unidentified", "unattributed",
               "attributed to", "artist(s)", "workshop", "follower of",
               "circle of", "school of", "manner of", "formerly", "workshop of")


def artist_matches(w, keys, exclude=None, title_keys=None):
    """判断一件作品是否属于某个流派。按可信度从高到低：

    1. **维基共享资源**：Artist 字段常是上传者不是画家（实测罗马式壁画
       条目的作者写着 "Joe Mabel"），只看文件名。
    2. **博物馆 API 且作者是真人**：只看作者，**绝不看标题**。
       标题里出现风格词会造成严重误判 —— 实测一幅 19 世纪东方主义油画
       《Circassian Cavalry ... at the Door of a Byzantine Monument》
       因为标题含 "Byzantine" 被收进了拜占庭。
    3. **作者匿名/不确定**：退回用标题匹配。敦煌、唐卡、伊斯兰瓷砖
       这类无名氏传统需要这条退路。
    4. **title_keys**：有些流派的身份在「作品/主题」而不是「作者」
       （禅艺术、壁画运动），这些流派显式声明 title_keys，总是匹配标题。

    排除词同样重要：名字片段会误命中（"henri" 命中 Henri Fantin-Latour、
    "delaunay" 命中 17 世纪的 Nicolas Delaunay、"lange" 命中 michelangelo）。
    所有比较都先过 _norm()。
    """
    hay_title = _norm(w.get("raw_title") or w.get("title"))
    hay_artist = _norm(w.get("artist"))
    hay = (hay_artist + " " + hay_title) if w.get("raw_title") else hay_artist

    if exclude and any(_norm(x) in hay or _norm(x) in hay_title for x in exclude):
        return False

    # title_keys 单独判定，不受「真人作者只看作者」的限制
    if title_keys and any(_norm(k) in hay_title for k in title_keys):
        return True
    if not keys:
        return False

    if not w.get("raw_title"):
        if hay_artist and not any(x in hay_artist for x in ANON_ARTIST):
            hay = hay_artist                    # 真人作者：只看作者
        else:
            hay = hay_artist + " " + hay_title  # 匿名：作者 + 标题
    return any(_norm(k) in hay for k in keys)
