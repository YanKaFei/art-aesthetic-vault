# -*- coding: utf-8 -*-
"""
artvault_core.py —— 仓库的「可被调用的那一层」。

把 141 张流派卡从 Markdown 变成**结构化、可检索、可组合**的数据，
让 AI（或你自己）能：
  · search()    按任意词找到相关流派
  · show()      取一张卡的完整提示词层
  · compose()   把一个创意想法拆成层级，再从多张卡里各取一层拼成提示词
  · palette()   取配色
  · related()   找关联流派

只依赖标准库。CLI 在 artvault.py，MCP 服务在 mcp_server.py，都调用这里。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

LAYERS = ["style", "lighting", "color", "composition", "medium", "mood", "camera"]

# 这些负向词意味着「画面里不要有人」，一旦你给了主体就冲突
HUMAN_WORDS = ("people", "person", "figures", "human", "crowd", "portrait", "face",
               "no people", "figures,", "有人")
LAYER_ZH = {"style": "风格", "lighting": "光照", "color": "色彩",
            "composition": "构图", "medium": "媒介", "mood": "情绪", "camera": "镜头"}

# 意图词 → 该意图通常由哪一层承担。用于 compose() 自动分层。
INTENT_LAYERS = {
    "style": ["风格", "画风", "感觉像", "看起来像", "style", "look like", "in the style of", "质感像"],
    "lighting": ["光照", "光", "打光", "灯光", "lighting", "light", "布光", "照明"],
    "color": ["配色", "色彩", "颜色", "色调", "color", "palette", "colour"],
    "composition": ["构图", "视角", "镜头感", "composition", "framing", "angle", "布局"],
    "medium": ["媒介", "材质", "媒介感", "medium", "material", "画在", "印在"],
    "mood": ["情绪", "氛围", "感觉", "mood", "atmosphere", "vibe", "气氛"],
    "camera": ["镜头", "焦段", "景别", "机位", "运镜", "camera", "lens", "shot"],
}


# --------------------------------------------------------------------- 加载
def load():
    """从 movements.py 直接读定义（不依赖生成的 Markdown，保证始终最新）"""
    from movements import MOVEMENTS, CATEGORIES, by_category, build_positive
    cards = []
    for m in MOVEMENTS:
        cards.append({
            "slug": m["slug"],
            "name_zh": m["name_zh"],
            "name_en": m["name_en"],
            "period": m["period"],
            "region": m["region"],
            "category": m["category"],
            "tier": m.get("tier", "B"),
            "one_liner": m["one_liner"],
            "core": m.get("core", []),
            "visual": m.get("visual", {}),
            "palette": m.get("palette", []),
            "artists": m.get("artists", []),
            "prompt": m.get("prompt", {}),
            "positive": build_positive(m),
            "negative": m.get("negative", ""),
            "video": m.get("video", {}),
            "pitfalls": m.get("pitfalls", []),
            "see_also": m.get("see_also", []),
            "artist_keys": m.get("artist_keys", []),
            "has_images": False,
        })
    # 标注哪些有实图
    d = os.path.join(HERE, "_data")
    for c in cards:
        p = os.path.join(d, c["slug"] + ".json")
        if os.path.exists(p):
            try:
                c["has_images"] = len(json.load(open(p, encoding="utf-8"))) > 0
            except Exception:
                pass
    return cards, CATEGORIES, by_category


_CACHE = {}


def cards():
    if "cards" not in _CACHE:
        cs, cats, bycat = load()
        _CACHE["cards"] = cs
        _CACHE["cats"] = cats
        # by_category() 返回 {分类: [movement 定义]}，这里换成卡片对象
        m = {c["slug"]: c for c in cs}
        _CACHE["bycat"] = {k: [m[x["slug"]] for x in v if x["slug"] in m]
                           for k, v in bycat().items()}
    return _CACHE["cards"]


def video_prompts(mv):
    """取某个流派的两块可粘贴中文视频提示词（Seedance 2.5 / MiniMax H3）。

    实现在 video_prompt.py，这里只做转发 —— 卡片和 CLI 共用同一份生成逻辑，
    避免两边各写一套后漂移。
    """
    import video_prompt
    return video_prompt.build(mv)


def by_slug():
    if "byslug" not in _CACHE:
        _CACHE["byslug"] = {c["slug"]: c for c in cards()}
    return _CACHE["byslug"]


def lookup(ident):
    """按**标识符**精确查找一个流派：slug / 中文名 / 英文名 / 别名。

    找不到返回 None。**不要用 search() 代替这个** —— search 是全文模糊检索，
    卡片正文里的词也算命中，所以拿它做标识符查找会静默返回错误的流派。

    踩过的坑：`artvault.py show 不存在` 会返回「原生艺术 Art Brut」，
    因为那张卡片的描述里恰好有「不存在」这个词（原生艺术「不存在于
    主流艺术史」）。同理 `get_movement("不存在")` 也返回它。
    问一个流派却得到另一个流派，比明确报错糟得多。
    """
    q = (ident or "").strip().lower()
    if not q:
        return None
    for c in cards():
        if q in (c["slug"].lower(), c["name_zh"].lower(), c["name_en"].lower()):
            return c
    s = _aliases().get(q)
    if s:
        return by_slug().get(s)
    return None


def name_matches(ident, limit=5):
    """只在**名字**里找近似项，用于「你是不是想找…」提示（绝不用于取值）。

    和 search() 的区别：search 会命中正文，这里只看名字，所以不会有
    「正文里碰巧有这个词」的假命中。
    """
    q = (ident or "").strip().lower()
    if not q:
        return []
    out = []
    for c in cards():
        for field in (c["slug"].lower(), c["name_zh"].lower(), c["name_en"].lower()):
            if q in field or field in q:
                out.append(c)
                break
    return out[:limit]


def resolve(ident):
    """标识符解析：先精确，再在**名字**里找近似。

    返回 (card, hint)。card 为 None 时 hint 是「你是不是想找」的候选列表；
    这样调用方可以明确报错并给出建议，而不是随便挑一个用。
    """
    c = lookup(ident)
    if c:
        return c, []
    cands = name_matches(ident)
    return (cands[0], []) if len(cands) == 1 else (None, cands)


# --------------------------------------------------------------------- 检索
def _aliases():
    """关键词 → slug 的别名表（含 WikiArt 映射 + 四个核心词的同义簇）"""
    if "aliases" in _CACHE:
        return _CACHE["aliases"]
    al = {}
    try:
        import keyword_map
        for cl in keyword_map.CLUSTERS:
            for s in cl["synonyms"]:
                al[s.lower()] = cl["card"]
            al[cl["key"].lower()] = cl["card"]
            al[cl["en"].lower()] = cl["card"]
    except Exception:
        pass
    _CACHE["aliases"] = al
    return al


def _haystack(c):
    parts = [c["slug"], c["name_zh"], c["name_en"], c["category"], c["one_liner"],
             c["period"], c["region"], c["negative"]]
    parts += c["core"] + list(c["visual"].values()) + c["pitfalls"]
    parts += [a for a, _ in c["artists"]]
    parts += list(c["prompt"].values())
    parts += c["artist_keys"]
    parts += [h for h, _ in [(x, None) for x in []]]
    parts += [x[0] for x in c["palette"]]
    return " ".join(str(p) for p in parts).lower()


_HAY = {}


def search(query, limit=8, category=None, semantic=False):
    """模糊检索：精确名 > 别名 > 子串命中数。返回按相关度排序的卡。

    semantic=True 时叠加 CLIP 语义检索（需要模型；不可用就自动退回纯关键词）。
    规则是**分档接管**而不是分数融合：关键词搜得到就不动它，搜不到才让语义上。
    阈值 SEM_TAKEOVER 是实测扫出来的，复跑：`python3 eval_search.py`。
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    al = _aliases()
    scored = {}
    for c in cards():
        if category and c["category"] != category:
            continue
        score = 0.0
        if q == c["name_zh"].lower() or q == c["name_en"].lower() or q == c["slug"]:
            score += 100
        if al.get(q) == c["slug"]:
            score += 80
        if q in c["name_zh"].lower() or q in c["name_en"].lower():
            score += 40
        if q in c["slug"]:
            score += 25
        for term in re.split(r"[\s,，、]+", q):
            if len(term) < 2:
                continue
            if term in c["name_zh"].lower() or term in c["name_en"].lower():
                score += 12
            if _HAY.setdefault(c["slug"], _haystack(c)).count(term):
                score += 2
        if score:
            scored[c["slug"]] = score

    if semantic:
        # 语义检索**不是一个再加权的排序器**，而是关键词接不住时的接管者。
        #
        # 为什么不融合分数：试过三种关键词归一（除以最大值 / 开方 / 饱和曲线）
        # × 两种语义归一（min-max / 固定标定），**A 组全部摔到 78.7%**
        # （基准 99.3%）。原因是语义分是余弦相似度，任意查询的 top40 都落在
        # 0.80–0.90 这条窄带里、跨度只有 0.03 —— 无论怎么归一，都是在把一条
        # 本来没有区分度的分布拉成满量程，噪声于是变成信号：art-informel /
        # outsider-art 这类「谁的英文描述都沾一点」的流派抢走了几乎所有查询，
        # 而正确答案在关键词里明明排第 0。
        #
        # 所以改成**分档**，阈值同样是实测扫出来的（见 eval_search.py）：
        #   关键词命中任何东西（最高分 ≥ SEM_TAKEOVER）→ 原样返回，语义不插手
        #   关键词什么都没找到                        → 语义接管
        # T=2 处 A 组**零损失**（99.3% / 100%），B 组 Top-3 从 26.7% 翻到 53.3%。
        # 规则一句话说得清，用户也能预期：**搜得到就不动它，搜不到才让语义上。**
        top_kw = max(scored.values()) if scored else 0.0
        if top_kw < SEM_TAKEOVER:
            sem = _semantic_scores(query)
            if sem:
                bs = by_slug()
                order = [s for s, _ in sorted(sem.items(), key=lambda x: -x[1])]
                # 关键词那点弱命中垫在语义结果后面，别丢
                order += [s for s, _ in sorted(scored.items(), key=lambda x: -x[1])
                          if s not in order]
                out = []
                for s in order:
                    c = bs.get(s)
                    if not c or (category and c["category"] != category):
                        continue
                    out.append(c)
                    if len(out) >= limit:
                        break
                return out

    ranked = sorted(scored.items(), key=lambda x: -x[1])[:limit]
    bs = by_slug()
    return [bs[s] for s, _ in ranked if s in bs]


# 关键词最高分低于这个值（=什么都没命中）时才让语义检索接管。
# 实测扫描见 eval_search.py：T=2 处 A 组零损失、B 组 Top-3 翻倍；
# T=5 起 A 组明显掉（82.3%），因为连「单个词面命中」都被判成不可信。
SEM_TAKEOVER = 2


def _semantic_scores(query):
    """CLIP 语义分 {slug: 相似度}；不可用时返回 None。

    **绝不抛异常** —— 语义检索是可选的增量能力，它坏了不该把 `search` 也带坏。
    """
    try:
        import clip_match as CM
        res = CM.semantic_search(query, topn=40)
    except Exception:
        return None
    if not res:
        return None
    return {slug: score for slug, score in res}


def detect(text):
    """从一段自然语言里找出提到的流派（用于 compose 的自动分层）"""
    t = (text or "").lower()
    found = []
    for c in cards():
        for key in {c["name_zh"].lower(), c["name_en"].lower(), c["slug"]}:
            if key and key in t:
                found.append(c)
                break
    for alias, slug in _aliases().items():
        if alias in t:
            c = by_slug().get(slug)
            if c and c not in found:
                found.append(c)
    return found


# --------------------------------------------------------------------- 组合
def compose(brief="", style=None, lighting=None, color=None, composition=None,
            medium=None, mood=None, camera=None, subject=None, extra_layers=None,
            resolve_conflicts=True):
    """把创意想法 → 分层提示词。

    两种用法：
      1) 显式：compose(style="baroque", lighting="caravaggisti", composition="cyberpunk")
      2) 自然语言：compose("雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图")
         —— 会先 detect() 出提到的流派，再按 brief 里的意图词决定各占哪一层。

    resolve_conflicts=True（默认）时，与正向要求打架的负向词会被**自动丢掉**，
    丢掉的记在返回值的 `dropped` 里。设 False 则只报告不处理（旧行为）。
    为什么默认丢掉：跨流派混搭实测 68% 会撞（抽 300 组风格×光照），平均 1.7 处；
    把「删哪几个词」丢给用户，等于让每个用混搭的人都手工收拾一遍。
    规则只有一条 —— **正向是意图，负向是护栏，护栏让位于意图**：
      · 你说要巴洛克的光照 → 浮世绘的「no cast shadows」必须让路
      · 你给的主体是个人 → 精确主义的「no people」必须让路
    """
    assigned = {k: v for k, v in dict(
        style=style, lighting=lighting, color=color, composition=composition,
        medium=medium, mood=mood, camera=camera).items() if v}
    notes = []

    if brief:
        hits = detect(brief)
        if hits:
            # 看 brief 里每个流派附近有没有意图词，决定它占哪一层
            low = brief.lower()
            for c in hits:
                pos = min([low.find(k) for k in
                           [c["name_zh"].lower(), c["name_en"].lower(), c["slug"]] if low.find(k) >= 0] or [0])
                window = low[max(0, pos - 14): pos + len(c["name_zh"]) + 14]
                layer = None
                for lname, words in INTENT_LAYERS.items():
                    if any(w in window for w in words):
                        layer = lname
                        break
                if layer and layer not in assigned:
                    assigned[layer] = c["slug"]
                    notes.append("%s → %s 层（按 brief 里的意图词判断）" % (c["name_zh"], LAYER_ZH[layer]))
                elif "style" not in assigned:
                    assigned["style"] = c["slug"]
                    notes.append("%s → 风格层（默认）" % c["name_zh"])
        else:
            notes.append("brief 里没识别出具体流派，只用你显式指定的层")

    for k, v in (extra_layers or {}).items():
        assigned.setdefault(k, v)

    bs = by_slug()
    out_layers = {}
    for layer, slug in assigned.items():
        c = bs.get(slug) or (search(slug, 1) or [None])[0]
        if not c:
            notes.append("未找到：%s" % slug)
            continue
        out_layers[layer] = {"slug": c["slug"], "name": c["name_zh"],
                             "text": c["prompt"].get(layer, "")}

    # 组装
    body = []
    if subject:
        body.append(subject.strip())
    for layer in LAYERS:
        if layer in out_layers and out_layers[layer]["text"]:
            body.append(out_layers[layer]["text"])
    positive = ", ".join(x.strip().rstrip(",") for x in body if x)

    # 负向：合并各层的 negative，并检出互相矛盾的部分
    # （跨时代混搭时这是真实存在的坑：浮世绘说 no cast shadows，
    #   而巴洛克的光照层恰恰要求 deep crushed shadows）
    subject_tokens = set(re.findall(r"[a-z]{4,}", (subject or "").lower()))
    pos_tokens = set()
    for layer, info in out_layers.items():
        for tok in re.split(r"[,，]", info["text"]):
            for w in re.findall(r"[a-z]{5,}", tok.lower()):
                pos_tokens.add(w)
    neg, seen, conflicts, dropped = [], set(), [], []
    for layer, info in out_layers.items():
        c = bs.get(info["slug"])
        if not c:
            continue
        for term in re.split(r"[,，]", c.get("negative", "")):
            t = term.strip()
            if not t or t.lower() in seen:
                continue
            # 这个词是否与另一层的要求冲突？
            clash = [w for w in re.findall(r"[a-z]{5,}", t.lower()) if w in pos_tokens]
            hit, why = None, ""
            if clash:
                hit, why = clash[0], "另一层要求 `%s`" % clash[0]
            elif subject and any(w in t.lower() for w in HUMAN_WORDS):
                # 语义冲突没法靠词面匹配发现：精确主义的负向词里有 people/figures，
                # 而主体是个人。这类「空场景禁令 vs 有人物主体」用规则直接拦。
                hit, why = "主体（有人物/生物）", "你给的主体是人/生物"
            elif subject_tokens and any(w in subject_tokens for w in re.findall(r"[a-z]{4,}", t.lower())):
                sw = [w for w in re.findall(r"[a-z]{4,}", t.lower()) if w in subject_tokens][0]
                hit, why = sw, "主体里有 `%s`" % sw
            if hit:
                conflicts.append((LAYER_ZH.get(layer, layer), t, hit))
                if resolve_conflicts:
                    dropped.append({"layer": LAYER_ZH.get(layer, layer),
                                    "term": t, "reason": why})
                    seen.add(t.lower())
                    continue                      # 不进 neg —— 护栏让位于意图
            seen.add(t.lower()); neg.append(t)

    # 配色：取风格层的卡，没有就取光照层
    pc = bs.get(out_layers.get("style", {}).get("slug", "")) or \
         bs.get(out_layers.get("lighting", {}).get("slug", ""))
    palette = pc["palette"] if pc else []

    # 视频层：取风格层的卡
    video = (bs.get(out_layers.get("style", {}).get("slug", "")) or {}).get("video", {})

    if conflicts:
        if dropped:
            notes.append("⚠️ 检出 %d 处负向词冲突，已自动丢掉 %d 个让位于正向要求"
                         "（要看原样加 --keep-conflicts）" % (len(conflicts), len(dropped)))
        else:
            notes.append("⚠️ 检出 %d 处负向词冲突（--keep-conflicts 模式下未处理），"
                         "见 conflicts 字段" % len(conflicts))

    return {
        "layers": out_layers,
        "conflicts": conflicts,
        "dropped": dropped,
        "positive": positive,
        "negative": ", ".join(neg),
        "palette": palette,
        "video": video,
        "notes": notes,
    }


def render(result, subject=None):
    """把 compose() 的结果渲染成可读文本（也是给 AI 看的格式）"""
    L = []
    L.append("【分层】")
    for layer in LAYERS:
        if layer in result["layers"]:
            i = result["layers"][layer]
            L.append("  %-4s ← %s" % (LAYER_ZH[layer], i["name"]))
    if not result["layers"]:
        L.append("  （没有分配到任何层）")
    L.append("")
    L.append("【正向提示词】")
    L.append(result["positive"])
    L.append("")
    if result["negative"]:
        L.append("【负向提示词】")
        L.append(result["negative"])
        L.append("")
    if result["palette"]:
        L.append("【配色】")
        L.append("  " + "  ".join("%s %s" % (h, n) for h, n in result["palette"]))
        L.append("")
    if result["video"]:
        L.append("【视频层】")
        L.append("  运动：%s" % result["video"].get("motion", ""))
        L.append("  运镜：%s" % result["video"].get("camera", ""))
        L.append("")
    if result.get("dropped"):
        L.append("【✓ 已自动消解的冲突】")
        L.append("  这些负向词和你另一层的要求打架，已从上面的负向提示词里拿掉：")
        for d in result["dropped"]:
            L.append("    · %s 层原本禁止 `%s` —— 让位于%s" % (d["layer"], d["term"], d["reason"]))
        L.append("  （想要原样的负向词合集：加 --keep-conflicts）")
        L.append("")
    elif result.get("conflicts"):
        L.append("【⚠️ 层级冲突（未消解）】")
        L.append("  下面这些负向词和你另一层的要求打架，用之前先删掉：")
        for lay, term, pos in result["conflicts"]:
            L.append("    · %s 层禁止 `%s`，但另一层要求 `%s`" % (lay, term, pos))
        L.append("")
    if result["notes"]:
        L.append("【分层依据】")
        for n in result["notes"]:
            L.append("  · %s" % n)
    return "\n".join(L)


def format_card(c, full=True):
    L = ["# %s · %s" % (c["name_zh"], c["name_en"]),
         "分类：%s ｜ 时期：%s ｜ 地区：%s" % (c["category"], c["period"], c["region"]),
         "一句话：%s" % c["one_liner"], ""]
    L.append("## 视觉语言拆解")
    for k, v in c["visual"].items():
        L.append("- %s：%s" % (k, v))
    L.append("")
    L.append("## 提示词层（可单独复用）")
    for layer in LAYERS:
        if c["prompt"].get(layer):
            L.append("- %s：%s" % (LAYER_ZH[layer], c["prompt"][layer]))
    L.append("")
    L.append("## 整段正向")
    L.append(c["positive"].strip())
    L.append("")
    L.append("## 负向")
    L.append(c["negative"])
    L.append("")
    L.append("## 配色")
    L.append("  ".join("%s %s" % (h, n) for h, n in c["palette"]))
    L.append("")
    if full:
        L.append("## 视频层")
        L.append("运动：%s" % c["video"].get("motion", ""))
        L.append("运镜：%s" % c["video"].get("camera", ""))
        L.append("要诀：%s" % c["video"].get("note", ""))
        L.append("")
        L.append("## 常见翻车点")
        for p in c["pitfalls"]:
            L.append("- %s" % p)
        L.append("")
        L.append("## 关联流派： " + "、".join(c["see_also"]))
    return "\n".join(L)


if __name__ == "__main__":
    cs = cards()
    print("流派卡 %d 张，分类 %d 个" % (len(cs), len(_CACHE["cats"])))
    print("有实图的 %d 张" % sum(1 for c in cs if c["has_images"]))
