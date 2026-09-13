#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""refs.py —— 流派卡各层提示词的**艺术史出处**。

## 为什么要有这个

在此之前，卡上每一层（光照、色彩、构图、媒介…）的说法都是**我们写的**。
「巴洛克的光照 = 明暗对照法 + 深压暗调」这句话是对的，但读者没有任何办法
去核对，也没法往下追。加上出处之后同一句话变成三件事：

  1. 可核对 —— 点开就能看权威机构怎么定义
  2. 可追溯 —— 术语有官方译名与定义，做多语言时不用自己造词
  3. 可审计 —— 别人能指出「你这条引用不成立」

## 出处怎么选（以及为什么没有 Britannica）

只收**能程序化验证**的来源。实测：

    Britannica   全线 403（挡爬虫）—— 搜索能搜到，但脚本打不开，
                 也就是**无法验证**。无法验证的 URL 我不写进仓库：
                 一旦写错，读者点开是 404，比没有出处更糟。
    Tate         可用。`tate.org.uk/art/art-terms/<字母>/<词条>` 这个模式
                 可批量探测，且**能通过**（40 条 200、8 条 404）——
                 有区分度才说明验证是真的在验。
    Met          429 限流，暂缓。

所以目前唯一来源是 Tate 的艺术术语词典（Art terms）。它是英中艺术教育里
最常被引用的公开术语表之一，词条短、定义清楚、链接稳定。

## 覆盖率是诚实的

`ASSIGN` 只覆盖了**一部分**流派，而且是逐条判断「这个概念确实适用于这张卡」
之后才写的。没写的不是遗漏，是**还没做**——`coverage()` 会报出当前比例，
验收第 21 项也会打印。不为了让数字好看而给不相干的卡硬塞引用。

## 结构

    CONCEPTS  概念 → (中文名, 出处机构, URL)
    ASSIGN    流派 slug → {层名: [概念…]}

「层名」用库里七层的说法（风格/光照/色彩/构图/媒介/情绪/镜头），
这样卡上能逐层列出「这一层的说法从哪来」。
"""

# --------------------------------------------------------------- 概念表
TATE = "Tate 艺术术语词典（Art terms）"
_T = "https://www.tate.org.uk/art/art-terms/%s/%s"

CONCEPTS = {
    # 风格 / 流派本身
    "baroque":        ("巴洛克（Baroque）", TATE, _T % ("b", "baroque")),
    "impressionism":  ("印象派（Impressionism）", TATE, _T % ("i", "impressionism")),
    "neo-impressionism": ("新印象派（Neo-Impressionism）", TATE, _T % ("n", "neo-impressionism")),
    "cubism":         ("立体主义（Cubism）", TATE, _T % ("c", "cubism")),
    "surrealism":     ("超现实主义（Surrealism）", TATE, _T % ("s", "surrealism")),
    "romanticism":    ("浪漫主义（Romanticism）", TATE, _T % ("r", "romanticism")),
    "realism":        ("现实主义（Realism）", TATE, _T % ("r", "realism")),
    "fauvism":        ("野兽派（Fauvism）", TATE, _T % ("f", "fauvism")),
    "expressionism":  ("表现主义（Expressionism）", TATE, _T % ("e", "expressionism")),
    "symbolism":      ("象征主义（Symbolism）", TATE, _T % ("s", "symbolism")),
    "dada":           ("达达（Dada）", TATE, _T % ("d", "dada")),
    "futurism":       ("未来主义（Futurism）", TATE, _T % ("f", "futurism")),
    "constructivism": ("构成主义（Constructivism）", TATE, _T % ("c", "constructivism")),
    "bauhaus":        ("包豪斯（Bauhaus）", TATE, _T % ("b", "bauhaus")),
    "pop-art":        ("波普艺术（Pop art）", TATE, _T % ("p", "pop-art")),
    "photorealism":   ("照相写实主义（Photorealism）", TATE, _T % ("p", "photorealism")),
    "land-art":       ("大地艺术（Land art）", TATE, _T % ("l", "land-art")),
    "minimalism":     ("极简主义（Minimalism）", TATE, _T % ("m", "minimalism")),
    "conceptual-art": ("观念艺术（Conceptual art）", TATE, _T % ("c", "conceptual-art")),
    "abstract-expressionism": ("抽象表现主义（Abstract expressionism）", TATE,
                               _T % ("a", "abstract-expressionism")),
    "modernism":      ("现代主义（Modernism）", TATE, _T % ("m", "modernism")),
    "postmodernism":  ("后现代主义（Postmodernism）", TATE, _T % ("p", "postmodernism")),
    "art-nouveau":    ("新艺术运动（Art nouveau）", TATE, _T % ("a", "art-nouveau")),
    "avant-garde":    ("先锋派（Avant-garde）", TATE, _T % ("a", "avant-garde")),
    "abstract-art":   ("抽象艺术（Abstract art）", TATE, _T % ("a", "abstract-art")),
    "figurative-art": ("具象艺术（Figurative art）", TATE, _T % ("f", "figurative-art")),
    "performance-art": ("行为艺术（Performance art）", TATE, _T % ("p", "performance-art")),

    # 光照 / 手法
    "chiaroscuro":    ("明暗对照法（chiaroscuro）", TATE, _T % ("c", "chiaroscuro")),
    "sublime":        ("崇高（the sublime）", TATE, _T % ("s", "sublime")),
    "picturesque":    ("如画（picturesque）", TATE, _T % ("p", "picturesque")),
    "perspective":    ("透视法（perspective）", TATE, _T % ("p", "perspective")),

    # 媒介 / 材质
    "impasto":        ("厚涂（impasto）", TATE, _T % ("i", "impasto")),
    "fresco":         ("湿壁画（fresco）", TATE, _T % ("f", "fresco")),
    "tempera":        ("蛋彩（tempera）", TATE, _T % ("t", "tempera")),
    "watercolour":    ("水彩（watercolour）", TATE, _T % ("w", "watercolour")),
    "woodcut":        ("木刻版画（woodcut）", TATE, _T % ("w", "woodcut")),
    "lithography":    ("石版画（lithography）", TATE, _T % ("l", "lithography")),
    "collage":        ("拼贴（collage）", TATE, _T % ("c", "collage")),
    "assemblage":     ("集合艺术（assemblage）", TATE, _T % ("a", "assemblage")),
    "readymade":      ("现成品（readymade）", TATE, _T % ("r", "readymade")),

    # 题材
    "still-life":     ("静物（still life）", TATE, _T % ("s", "still-life")),
    "portrait":       ("肖像（portrait）", TATE, _T % ("p", "portrait")),
    "landscape":      ("风景（landscape）", TATE, _T % ("l", "landscape")),
    "history-painting": ("历史画（history painting）", TATE, _T % ("h", "history-painting")),
}

# --------------------------------------------------------------- 挂载表
# 只写「这个概念确实适用于这张卡的这一层」的组合。
# 拿不准的宁可不写 —— 硬塞一条不相干的引用，比没有引用更坏。
ASSIGN = {
    "baroque":          {"风格": ["baroque"], "光照": ["chiaroscuro"],
                         "媒介": ["impasto"], "构图": ["history-painting"]},
    "caravaggisti":     {"风格": ["baroque"], "光照": ["chiaroscuro"]},
    "rococo":           {"风格": ["baroque"]},
    "romanticism":      {"风格": ["romanticism"], "情绪": ["sublime"],
                         "构图": ["landscape"]},
    "neo-romanticism":  {"风格": ["romanticism"], "情绪": ["sublime"]},
    "realism":          {"风格": ["realism"], "构图": ["genre" if False else "figurative-art"]},
    "naturalism":       {"风格": ["realism"], "构图": ["figurative-art"]},
    "social-realism":   {"风格": ["realism"], "构图": ["figurative-art"]},
    "impressionism":    {"风格": ["impressionism"], "媒介": ["impasto"],
                         "构图": ["landscape"]},
    "post-impressionism": {"风格": ["impressionism"], "媒介": ["impasto"]},
    "neo-impressionism": {"风格": ["neo-impressionism"]},
        "tonalism":         {"风格": ["landscape"], "情绪": ["sublime"]},
    "symbolism":        {"风格": ["symbolism"]},
    "cubism":           {"风格": ["cubism"], "媒介": ["collage"]},
    "orphism":          {"风格": ["cubism"]},
    "futurism":         {"风格": ["futurism"]},
    "constructivism":   {"风格": ["constructivism"]},
    "bauhaus":          {"风格": ["bauhaus"], "构图": ["abstract-art"]},
    "dada":             {"风格": ["dada"], "媒介": ["readymade", "collage"]},
    "surrealism":       {"风格": ["surrealism"]},
    "fauvism":          {"风格": ["fauvism"]},
    "expressionism":    {"风格": ["expressionism"], "媒介": ["woodcut"]},
    "der-blaue-reiter": {"风格": ["expressionism"]},
    "abstract-expressionism": {"风格": ["abstract-expressionism"],
                               "构图": ["abstract-art"]},
    "color-field":      {"风格": ["abstract-expressionism"], "构图": ["abstract-art"]},
    "pop-art":          {"风格": ["pop-art"]},
    "photorealism":     {"风格": ["photorealism"], "构图": ["figurative-art"]},
    "land-art":         {"风格": ["land-art"], "构图": ["landscape"]},
    "minimalism-art":   {"风格": ["minimalism"], "构图": ["abstract-art"]},
    "conceptual-art":   {"风格": ["conceptual-art"], "媒介": ["readymade"]},
    "postmodernism":    {"风格": ["postmodernism"]},
    "art-nouveau":      {"风格": ["art-nouveau"]},
    "avant-garde":      {"风格": ["avant-garde"]},
    "early-renaissance": {"构图": ["perspective"], "媒介": ["tempera", "fresco"]},
        "international-gothic": {"媒介": ["tempera"]},
        "venetian-school":  {"媒介": ["impasto"]},
    "renaissance":      {"构图": ["perspective", "history-painting"],
                         "媒介": ["fresco", "tempera"]},
    "byzantine":        {"媒介": ["fresco"]},
    "romanesque":       {"媒介": ["fresco"]},
    "gothic":           {"媒介": ["fresco"]},
        "cubo-futurism":    {"风格": ["cubism", "futurism"], "媒介": ["collage"]},
    "neo-geo":          {"构图": ["abstract-art"]},
    "post-minimalism":  {"风格": ["minimalism"], "媒介": ["assemblage"]},
    "spatialism":       {"媒介": ["assemblage"], "构图": ["abstract-art"]},
        "dutch-golden-age": {"构图": ["still-life", "landscape"]},
        "pictorialism":     {"构图": ["portrait", "landscape"]},
    "documentary-photography": {"构图": ["figurative-art"]},
            "wabi-sabi":        {"构图": ["still-life"]},
    "ukiyo-e":          {"媒介": ["woodcut"]},
    "shin-hanga":       {"媒介": ["woodcut"]},
    "sosaku-hanga":     {"媒介": ["woodcut"]},
}


def _layer_order():
    """层的库内顺序 + 中文名→英文键的对照，都取自 artvault_core（单一来源）。

    不在这里另写一份：层顺序改了两处就会漂（本仓库为这类事吃过亏）。
    ASSIGN 里写中文层名是为了可读（「光照」比 "lighting" 好核对），
    所以这里要反查一次。延迟导入避免 refs ← artvault_core ← movements 的循环。
    """
    import artvault_core as A
    return A.LAYERS, dict(A.LAYER_ZH)          # 英文键 → 中文名


def refs_for(slug):
    """返回 [(层, 概念中文名, 出处机构, URL), ...]，按层的库内顺序排。"""
    plan = ASSIGN.get(slug) or {}
    LAYERS, EN2ZH = _layer_order()
    out = []
    for layer in LAYERS:
        for key in plan.get(EN2ZH.get(layer, layer), []):
            c = CONCEPTS.get(key)
            if not c:
                continue
            out.append((layer, c[0], c[1], c[2]))
    return out


def coverage():
    """(有出处的流派数, 有出处的层数, 总层数, 卡片总数)。

    这个数字是要**报出来**的，不是拿来好看的 —— 没覆盖的部分就是还没做。
    """
    from movements import MOVEMENTS
    LAYERS, _en2zh = _layer_order()
    cards = 0
    layers = 0
    for m in MOVEMENTS:
        r = refs_for(m["slug"])
        if r:
            cards += 1
            layers += len({x[0] for x in r})
    return cards, layers, len(MOVEMENTS) * len(LAYERS), len(MOVEMENTS)


def unknown_concepts():
    """ASSIGN 里引用了、但 CONCEPTS 里没有的概念名（拼错会静默少一条引用）。"""
    bad = set()
    for plan in ASSIGN.values():
        for keys in plan.values():
            for k in keys:
                if k not in CONCEPTS:
                    bad.add(k)
    return sorted(bad)


def unknown_slugs():
    """ASSIGN 里写了、但库里没有的流派 slug。"""
    try:
        from movements import MOVEMENTS
    except Exception:
        return []
    slugs = {m["slug"] for m in MOVEMENTS}
    return sorted(s for s in ASSIGN if s not in slugs)


def check_urls(timeout=25, workers=6):
    """联网复验所有出处 URL 是否还打得开。返回 [(概念, URL, 状态), ...]。

    **故意不做进验收**：验收要能在没有网络的 CI 上跑，而网络检查会引入
    假失败（网站临时 429/503 就红一片）。所以这里做成手动命令：
        python3 refs.py --check-urls
    写词条时跑一次，日后怀疑链接烂了再跑一次。
    """
    import urllib.request
    import concurrent.futures
    ua = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/135.0 Safari/537.36")

    def one(item):
        key, (topic, src, url) = item
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return key, url, r.status
        except Exception as e:
            return key, url, getattr(e, "code", "ERR:%s" % type(e).__name__)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, sorted(CONCEPTS.items())))


if __name__ == "__main__":
    from clihelp import guard
    import sys
    guard(sys.argv[1:], "python3 refs.py",
          ["打印出处覆盖率与完整性自检。",
           "ASSIGN 里引用不存在的概念 / 不存在的流派 slug 都会报出来。",
           "--check-urls  联网复验所有出处链接（手动跑，不进 CI）"])
    if "--check-urls" in sys.argv[1:]:
        res = check_urls()
        bad = [(k, u, s) for k, u, s in res if s != 200]
        print("出处链接复验：%d / %d 可达" % (len(res) - len(bad), len(res)))
        for k, u, st in bad:
            print("  ✗ %-34s %s  %s" % (k, st, u))
        sys.exit(1 if bad else 0)
    cards, layers, total, n = coverage()
    print("出处覆盖：%d / %d 张卡（%.0f%%）" % (cards, n, 100.0 * cards / max(n, 1)))
    print("逐层覆盖：%d / %d 层（%.0f%%）" % (layers, total, 100.0 * layers / max(total, 1)))
    print("概念表：%d 条，来源：Tate 艺术术语词典" % len(CONCEPTS))
    bad = unknown_concepts()
    print("引用了不存在概念：%s" % (bad or "无"))
    bad2 = unknown_slugs()
    print("引用了不存在流派：%s" % (bad2 or "无"))
