# -*- coding: utf-8 -*-
"""
多数据源提供器 —— 每个函数返回统一结构的作品列表。

已实测可用的免密钥源：
  · 克利夫兰艺术博物馆  CC0       openaccess-api.clevelandart.org
  · 大都会艺术博物馆    CC0       collectionapi.metmuseum.org
  · 维基共享资源        逐条标注   commons.wikimedia.org

统一返回字段：
  title / artist / date / medium / image_url / image_url_hi /
  page_url / source / license / license_url
"""

import json
import re
import ssl
import time
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
        # 标题里带作者是最可靠的署名来源，优先用它
        out.append({
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
        })
        if len(out) >= want * 2:
            break
    return out


PROVIDERS = {
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


def is_flat_work(w):
    m = (w.get("medium") or "").lower()
    if not m:
        return True
    return any(k in m for k in MEDIUM_OK)


def artist_matches(w, keys, exclude=None):
    """判断一件作品是否属于某个流派。

    关键区别：博物馆 API 的 artist 字段是**画家本人**；
    维基共享资源的 Artist 字段常常是**拍这张照片的上传者**
    （实测：罗马式壁画条目的 artist 是 "Joe Mabel"）。
    所以来自共享资源的作品只按文件名判断——文件名里通常带画家名或作品名。

    排除词同样重要：名字片段会误命中，比如 "henri" 会命中 Henri Fantin-Latour，
    "delaunay" 会命中 17 世纪的 Nicolas Delaunay。流派用 exclude_keys 挡掉。
    """
    if w.get("raw_title"):
        hay = w["raw_title"].lower()
    else:
        hay = ((w.get("artist") or "") + " " + (w.get("title") or "")).lower()
    if exclude and any(x.lower() in hay for x in exclude):
        return False
    if not keys:
        return False
    return any(k.lower() in hay for k in keys)
