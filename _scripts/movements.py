# -*- coding: utf-8 -*-
"""
movements.py —— 聚合所有流派定义，供 fetch_art.py / build_vault.py 使用。

要加新流派：在对应的 mv_*.py 里加一条，然后重跑 fetch_art.py 和 build_vault.py。
"""

import mv_core
import mv_west
import mv_asia
import mv_asia2
import mv_modern
import mv_gaps
import mv_contemporary
import mv_visual
import mv_photo

MODULES = [mv_core, mv_west, mv_asia, mv_asia2, mv_modern, mv_gaps,
           mv_contemporary, mv_visual, mv_photo]

# 让 mv_core 里的现代流派归到正确的分类下
CATEGORY_OVERRIDE = {
    "expressionism": "现代主义与战后",
    "cubism": "现代主义与战后",
    "surrealism": "现代主义与战后",
    "bauhaus": "现代主义与战后",
    "art-deco": "现代主义与战后",
    "cyberpunk": "数字·亚文化·摄影美学",
    "ukiyo-e": "东亚·南亚·伊斯兰",
    "zen-art": "东亚·南亚·伊斯兰",
}

MOVEMENTS = []
for _mod in MODULES:
    for _m in _mod.MOVEMENTS:
        _m["category"] = CATEGORY_OVERRIDE.get(_m["slug"], _mod.CATEGORY)
        _m["artist_keys"] = _mod.ARTIST_KEYS.get(_m["slug"], [])
        _m.setdefault("tier", "B")
        MOVEMENTS.append(_m)

BY_SLUG = {m["slug"]: m for m in MOVEMENTS}

CATEGORIES = []
for _m in MOVEMENTS:
    if _m["category"] not in CATEGORIES:
        CATEGORIES.append(_m["category"])


def build_positive(mv):
    """没有手写 positive 时，用七层里的六层自动拼一段。"""
    if mv.get("positive"):
        return mv["positive"].strip()
    p = mv["prompt"]
    parts = [p["style"], p["lighting"], p["color"], p["composition"], p["medium"], p["mood"]]
    return " " + ", ".join(x.strip().rstrip(",") for x in parts if x)


def by_category():
    out = {}
    for m in MOVEMENTS:
        out.setdefault(m["category"], []).append(m)
    return out


if __name__ == "__main__":
    print("合计 %d 个流派，%d 个分类" % (len(MOVEMENTS), len(CATEGORIES)))
    for c in CATEGORIES:
        print("  %-18s %2d 个" % (c, len(by_category()[c])))
    print("有配图来源声明的: %d" % sum(1 for m in MOVEMENTS if m.get("sources")))
    print("有艺术家过滤词的: %d" % sum(1 for m in MOVEMENTS if m.get("artist_keys")))
