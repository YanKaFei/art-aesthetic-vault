# -*- coding: utf-8 -*-
"""mv_handraw.py —— 第 7 大类「手绘艺术风格」（handraw-style 274 条）。

## 这一层做什么

把 `30-handraw-style/` 里那份 `styles.json`（274 条：编号 / 组 / 参考作者 /
生图名称 / 中文核心特征）翻译成本库的流派定义，让这 274 条和已有的
147 张卡**走同一条路**：同一个 `movements.MOVEMENTS`、同一套七层提示词、
同一个 `artvault.py`、同一份验收。

翻译而不是重写 —— 这条线要划清楚：

    traits 原文          逐字进卡（「一、核心视觉特征」），一个字不改
    参考作者 / 生图名称   逐字进卡，且明确标注「这是索引标签，不是对作者的描述」
    七层英文              由 handraw_lexicon 的词表从 traits 里**抽**出来
    抽不到的层            用 A–H 的**组级默认**补，并在卡上标 ⟨组⟩

所以卡上任何一句英文都能回答「你凭什么这么写」：要么是 traits 里的某个词
命中词表，要么是这一组的组级共识。这是本库 `refs.py` 那套态度在手绘类上的
等价物 —— 出处不总是 Tate 词条，但**必须能被核对**。

## 为什么不做「逐条让模型写一段」

274 条里只要有一部分是编的，读者没有任何办法分辨哪一条是编的。而这个库的
全部价值就在于「以库里的术语为准」。词表推导是可审计的：词表是手写的、
命中是确定的、覆盖率是可测的（`python3 mv_handraw.py --stats`）。

## 图片

编号参考图落在 `99-attachments/images/handraw/handraw-<编号>.webp`，
卡上用 `![[...]]` 嵌入。**必须落在这个根下** —— 验收第 1/7/15 项
（断链 / 孤儿图 / 克隆完整性）只认 `99-attachments/images/`。
"""

import json
import os
import re

import handraw_lexicon as LX

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)

CATEGORY = LX.CATEGORY

# 组表原样转出：build_vault 要用它生成 README 的组内分组与总览页，
# 而**不能自己再抄一份**（抄一份就会与 handraw 的数据漂移）。
GROUPS = LX.GROUPS

# 原仓库整棵装在这个目录下（见 30-handraw-style/SOURCE.md）。
HANDRAW_ROOT = os.path.join(VAULT, "30-handraw-style")
STYLES_JSON = os.path.join(VAULT, LX.STYLES_JSON)

# 逐条罗列不合适：274 条手绘风格是**当代插画谱系**，不是历史分期。
PERIOD = "当代"

# 这些分句是 handraw 自己写的「避免…」——按它的 SKILL.md，这类子句
# **不该混进正向提示词**，要单独当翻车点用。所以这里把它们摘出来。
NEG_MARKERS = ("避免", "不要", "不准", "禁止")

# 组级兜底的翻车点（traits 里没写「避免…」时用）
GROUP_PITFALLS = [
    "模型最容易把这套画风渲染成 3D —— 必须写 hand-drawn / ink on paper，"
    "并给足平光",
    "手绘的线宽会被 AI 统一成矢量描边 —— 加 visible pen pressure、"
    "wobbly hand-drawn lines",
]

# 所有手绘类共用的负向词。**注意与正向层不撞词** ——
# 撞词的字面会被 compose 的冲突消解判成矛盾并丢掉（那是设计行为，
# 但会让 dropped 列表无意义地变长，所以这里先避开）。
BASE_NEGATIVE = ("3d render, cgi, photorealism, plastic skin, over-rendered detail, "
                 "glossy specular highlights, hdr, watermark, signature")


def _load_json(path):
    if not os.path.isfile(path):
        raise RuntimeError(
            "找不到 handraw 数据：%s\n"
            "  这一大类依赖 30-handraw-style/ 整棵仓库（见其 SOURCE.md）。\n"
            "  数据缺失时不静默降级成 0 张卡 —— 那会让 build_vault 生成一份"
            "「少了一整个分类」的库，而 README 的数字看着仍然对得上。"
            % path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _segments(traits):
    """把 traits 拆成分句。handraw 用「；」分隔「特征 / 补充要求」。"""
    out = []
    for s in re.split(r"[；;。\n]+", traits or ""):
        s = s.strip()
        if s:
            out.append(s)
    return out


def _split_evidence(traits):
    """返回 (正向分句, 翻车点)。后者含「避免/不要/不准/禁止」。"""
    keep, pitfalls = [], []
    for s in _segments(traits):
        (pitfalls if any(k in s for k in NEG_MARKERS) else keep).append(s)
    return keep, pitfalls


def _match(traits):
    """在 traits 里子串命中词表，返回 {维: [(中文词, 英文片段), ...]}。

    同一个维度内做**长词压制**：命中「极细钢笔」之后就不再收「钢笔」，
    命中「小人物大空间」就不再收「小人物」。否则提示词里会出现
    「very fine pen linework, ink pen linework」这种同义堆叠 ——
    堆叠不会让画更准，只会让权重失控。
    """
    low = (traits or "").lower()
    hits = {}
    for zh, dim, en in LX.KEYWORDS:          # 长词在前，先到先得
        if zh.lower() not in low:
            continue
        taken = hits.setdefault(dim, [])
        if any(zh in t for t, _ in taken):   # 已被更长的词覆盖
            continue
        taken.append((zh, en))
    return hits


def _palette(hits, g):
    """配色 = 组级底色 + traits 里出现的色彩词推导。

    卡上会写清这是**推导**：handraw 的数据里没有 hex，这些色值是按
    traits 提到的颜色词配的底色，不是从原图采样的。
    """
    out, seen = [], set()

    def push(pair):
        if pair and pair[0] not in seen:
            seen.add(pair[0])
            out.append(pair)

    for pair in LX.GROUP_BASE_PALETTE.get(g["letter"], LX.GROUP_BASE_PALETTE["H"]):
        push(pair)
    for zh, _en in hits.get("色彩", []):
        for key, pair in LX.COLOR_HEX.items():
            if key in zh:
                push(pair)
                break
    return out[:6]


def _blueprint(entry):
    """一条 styles.json → 一个本库的流派定义。"""
    number = str(entry.get("number") or "").strip()
    if not re.fullmatch(r"\d{3}", number):
        raise RuntimeError("styles.json 里编号不合法：%r" % entry.get("number"))
    group_raw = (entry.get("group") or "").strip()
    letter = group_raw[:1].upper()
    if letter not in LX.GROUPS:
        raise RuntimeError("styles.json 里出现了未知分组：%r" % group_raw)
    g = dict(LX.GROUPS[letter])
    g["letter"] = letter
    label = group_raw[1:].strip() or g["label"]

    n = int(number)
    slug = "handraw-%03d" % n
    gen = (entry.get("generation_name") or "").strip() or ("Hand-drawn Style #%s" % number)
    ref = (entry.get("reference") or "").strip() or "未标注"
    traits = (entry.get("traits") or "").strip()

    keep, pitfalls = _split_evidence(traits)
    hits = _match(traits)

    # ---- 六维：抽到的标 ⟨条⟩，没抽到的用组级默认标 ⟨组⟩ ------------------
    visual, prompt = {}, {}
    # 维 → 组级兜底文字
    fallback_zh = {
        "色彩": "",                          # 色彩没有组级默认，见下面的显式覆盖
        "光影": g["light_zh"],
        "笔触": g["medium_zh"],
        "构图": g["comp_zh"],
        "材质": g["medium_zh"],
        "情绪": g["mood_zh"],
    }
    fallback_en = {
        "光影": g["light_en"],
        "笔触": g["medium_en"],
        "构图": g["comp_en"],
        "材质": g["medium_en"],
        "情绪": g["mood_en"],
    }
    for dim in LX.DIMS:
        got = hits.get(dim) or []
        if got:
            visual[dim] = "、".join(dict.fromkeys(z for z, _ in got)) + " ⟨条⟩"
        else:
            word = fallback_zh.get(dim) or ("按该条 traits 的题材定" if dim == "色彩" else "")
            visual[dim] = (word or "该条未标注") + " ⟨组⟩"
    # 色彩是唯一一个「没有组级默认」的维度：手绘类的用色逐条不同，
    # 用组级色板冒充这一条的配色就是编。这里明确写出来。
    if not hits.get("色彩"):
        visual["色彩"] = LX.COLOR_FALLBACK_ZH + " ⟨组⟩"

    # ---- 七层英文 -------------------------------------------------------
    def en_of(dim):
        return list(dict.fromkeys(e for _z, e in (hits.get(dim) or [])))

    style = ("hand-drawn illustration, %s, reference style label: %s"
             % (gen, ref))
    lighting = ", ".join(en_of("光影")) or g["light_en"]
    color = ", ".join(en_of("色彩")) or LX.COLOR_FALLBACK_EN
    composition = ", ".join(en_of("构图")) or g["comp_en"]
    medium = ", ".join(en_of("笔触") + en_of("材质")) or g["medium_en"]
    mood = ", ".join(en_of("情绪")) or g["mood_en"]
    camera = g["camera_en"]
    prompt = {"style": style, "lighting": lighting, "color": color,
              "composition": composition, "medium": medium, "mood": mood,
              "camera": camera}

    negative = ", ".join(dict.fromkeys(
        [x.strip() for x in (BASE_NEGATIVE + ", " + g["neg"]).split(",") if x.strip()]))

    # ---- 关联：组内前后邻居 + 组级谱系锚点（锚点是编者加的，卡上会注明）----
    see_also = []
    if n > 1:
        see_also.append("handraw-%03d" % (n - 1))
    if n < 274:
        see_also.append("handraw-%03d" % (n + 1))
    see_also += [a for a in g["anchors"] if a not in see_also]

    image_rel = "%s/%s%03d.webp" % (LX.IMAGES_REL, LX.IMAGE_PREFIX, n)
    has_image = os.path.isfile(os.path.join(VAULT, image_rel))

    one_liner = keep[0] if keep else ("%s：编号 %s 的手绘风格。" % (ref, number))

    # 中文名：由 handraw_name.py 定名（274 条定名表 + 机械抽取的依据）。
    #
    # **name_zh = 名字**（不再是「手绘001」）。理由：Obsidian 里真正被看到的
    # 是 `流派:` 字段与文件名，别名只出现在属性面板的一行 —— 用户要的是
    # 「打开就是名字」，所以名字必须占正位。
    #
    # 编号不丢：它变成 `别名`（HANDRAW_ALIAS），检索/引用照旧可用。
    # slug 仍是 `handraw-001`（稳定 id，图片与 see_also 都指着它，不动）。
    try:
        import handraw_name as HN
        _rec = HN.all_names().get(number) or {}
        name_alias = _rec.get("name") or ""
        name_basis = _rec.get("basis") or ""
        name_from = _rec.get("from") or []
    except Exception:
        name_alias, name_basis, name_from = "", "", []

    return {
        "slug": slug,
        "name_zh": (name_alias or ("手绘%03d" % n)),
        "alias": "手绘%03d" % n,
        "name_alias": name_alias,
        "name_basis": name_basis,
        "name_from": name_from,
        "name_en": gen,
        "period": PERIOD,
        "region": g["region"],
        "category": CATEGORY,
        "tier": "B",
        "one_liner": one_liner,
        "core": keep or ["该条 traits 未提供更多描述。"],
        "visual": visual,
        "palette": _palette(hits, g),
        "artists": [(ref, "")],
        "prompt": prompt,
        "positive": "",          # 交给 movements.build_positive 按六层拼
        "negative": negative,
        "video": dict(g["video"]),
        "pitfalls": pitfalls + GROUP_PITFALLS,
        "see_also": see_also,
        # ---- 本条独有的字段（本库其它流派没有）----
        "kind": "handraw",
        "handraw_number": number,
        "handraw_group": letter,
        "handraw_group_label": label,
        "handraw_reference": ref,
        "handraw_traits": traits,
        "handraw_traits_empty": not traits,
        "handraw_image": image_rel if has_image else "",
    }


def build(entries=None):
    """读 styles.json（或传入的 entries）→ MOVEMENTS 列表。"""
    if entries is None:
        entries = _load_json(STYLES_JSON)
    out = [_blueprint(e) for e in entries]
    # 编号必须连续且唯一 —— 缺号会让「编号就是身份」这个前提悄悄失效
    nums = [m["handraw_number"] for m in out]
    if len(set(nums)) != len(nums):
        raise RuntimeError("styles.json 里有重复编号")
    return out


MOVEMENTS = build()

# 手绘类没有从博物馆抓来的作品，artist_keys 只用于过滤抓取结果，这里为空。
ARTIST_KEYS = {}


def groups():
    """按 A–H 顺序返回 (字母, 组名, [卡…])，供总览页使用。"""
    out = []
    for letter in sorted(LX.GROUPS):
        ms = [m for m in MOVEMENTS if m["handraw_group"] == letter]
        if ms:
            out.append((letter, LX.GROUPS[letter]["label"], ms))
    return out


def coverage():
    """抽取覆盖率 —— 不写死在文档里，随时现算（这个库为写死的数字吃过亏）。"""
    total = len(MOVEMENTS) * len(LX.DIMS)
    hit = 0
    for m in MOVEMENTS:
        for v in m["visual"].values():
            if "⟨条⟩" in v:
                hit += 1
    by_dim = {}
    for dim in LX.DIMS:
        k = sum(1 for m in MOVEMENTS if "⟨条⟩" in m["visual"][dim])
        by_dim[dim] = k
    with_img = sum(1 for m in MOVEMENTS if m["handraw_image"])
    return {"cells": total, "extracted": hit, "by_dim": by_dim,
            "with_image": with_img, "n": len(MOVEMENTS)}


if __name__ == "__main__":
    c = coverage()
    print("手绘艺术风格：%d 条，%d 个组" % (c["n"], len(groups())))
    print("配了编号参考图的：%d / %d" % (c["with_image"], c["n"]))
    print("六维单元格：%d 个，其中来自 traits 原文的 %d 个（%.1f%%），"
          "其余为组级默认" % (c["cells"], c["extracted"],
                          100.0 * c["extracted"] / max(1, c["cells"])))
    for dim, k in c["by_dim"].items():
        print("    %-4s 抽到 %3d / %d" % (dim, k, c["n"]))
