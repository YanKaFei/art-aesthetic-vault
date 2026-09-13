#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""visual_lexicon.py —— 中文视觉词 → 英文 CLIP 短语的桥。

## 为什么需要这座桥

本库的卡片是**中文写的**，而 CLIP 的文本塔是**纯英文**训练的
（`Xenova/clip-vit-base-patch32`）。实测：

    查询「a serene Japanese woodblock print of a wave」
      → 创作版画 / 浮世绘 / 日本水墨画 / 新版画 / 琳派        ✓ 全对

    查询「赛博朋克 霓虹 雨夜」
      → 工笔重彩 / 宋代院体画 / 新客观主义 / 无形式艺术        ✗ 全错
        （而且分数挤在 0.837—0.843，没有任何区分度）

也就是说，**中文查询直接喂给文本塔等于随机**。而本库的使用者是用中文提问的
（「压抑但华丽的光」这种表达里甚至没有流派名），所以他们恰好拿不到这个能力。

## 这座桥怎么建

词表是**按键写的**，不是从语料里对齐出来的：中文视觉词的英文对应没有捷径，
自动对齐在几百条数据的规模上噪声大于信号。词条来源是**本库自己的词汇表** ——
把 141 张卡 `visual` 字段里出现 ≥4 个流派的高频词抽出来（60 个），
再补上光照/色彩/构图/媒介/情绪五类里常用的说法。

所以这个词表描述的是**本库使用的术语体系**，不是通用中文。这是对的：
库的卖点就是「以库里的术语为准」，那么检索也该在库的术语空间里做。

## 它有多准

`self_retrieval()` 可以量：拿每个流派自己的中文描述过一遍桥，
看它能不能被检索回自己。数字在测试里打印，**不写死在文档里** ——
写死的数字会烂掉（这个仓库已经因为写死统计数字吃过一次亏）。
"""

import re

# ---------------------------------------------------------------- 词表
# 键是中文（库里的说法），值是英文 CLIP 短语。
# 值刻意写成**短语而不是单词**：CLIP 的文本塔对短语的语义更稳定
# （单字词的嵌入噪声大，实测 "warm" 单独用不如 "warm colour palette"）。
LEXICON = {
    # ---- 光影 / 光照 ----
    "明暗对照": "chiaroscuro, dramatic light and dark contrast",
    "强光": "strong single light source, hard light",
    "柔光": "soft diffused light, gentle gradation",
    "逆光": "backlit, rim light, silhouette against light",
    "侧光": "side lighting, raking light across the surface",
    "顶光": "overhead light, top-down illumination",
    "烛光": "candlelight, warm flickering single flame",
    "体积光": "volumetric light, visible light shafts",
    "硬阴影": "hard cast shadows, sharp shadow edges",
    "深阴影": "deep crushed shadows, heavy darkness",
    "无阴影": "no shadows, shadowless flat lighting",
    "高对比": "high contrast, strong tonal separation",
    "低对比": "low contrast, narrow tonal range",
    "无光源": "flat ambient illumination, no discernible light source",
    "均匀光": "even flat lighting, no directional light",
    "舞台光": "theatrical spotlight, staged illumination",
    "天光": "natural daylight from above",
    "氛围光": "atmospheric glow, hazy ambient light",
    "明暗渐变": "gradual tonal transition, soft shading",
    "暗部溢出": "crushed blacks, deep shadow areas",
    "高光": "specular highlights, bright accents",
    "光晕": "soft glow, halation around light sources",

    # ---- 色彩 ----
    "暖调": "warm colour palette, warm tones",
    "冷调": "cool colour palette, cool blue tones",
    "高饱和": "highly saturated vivid colours",
    "低饱和": "desaturated muted colours",
    "单色": "monochrome, single hue",
    "中性色": "neutral greys and earth tones",
    "互补色": "complementary colour contrast",
    "邻近色": "analogous colour harmony",
    "土色": "earth pigments, ochre and umber",
    "霓虹": "neon colours, glowing electric hues",
    "粉彩": "pastel palette, soft light tints",
    "金箔": "gold leaf, gilded surface",
    "朱红": "vermilion red",
    "胭脂红": "crimson, deep red",
    "靛蓝": "indigo blue",
    "钴蓝": "cobalt blue",
    "群青": "ultramarine blue",
    "普鲁士蓝": "prussian blue",
    "翠绿": "emerald green",
    "草绿": "grass green, olive green",
    "土黄": "yellow ochre",
    "赭石": "raw sienna, red ochre",
    "墨黑": "ink black",
    "灰白": "grey-white, silvery pale tone",
    "渐变": "colour gradient, smooth transition",

    # ---- 构图 ----
    "对称": "symmetrical composition, balanced axis",
    "不对称": "asymmetrical composition, dynamic imbalance",
    "对角线": "diagonal composition, dynamic diagonal",
    "中心构图": "centred composition, focal subject in the middle",
    "三分法": "rule of thirds placement",
    "留白": "large negative space, empty void",
    "满构图": "all-over composition, edge-to-edge density",
    "平面化": "flattened picture plane, no depth recession",
    "纵深": "deep perspective recession, spatial depth",
    "透视": "linear perspective, vanishing point",
    "特写": "close-up, tight framing on the subject",
    "全景": "wide establishing view",
    "俯视": "high angle, bird's eye view",
    "仰视": "low angle, looking up",
    "装饰性边框": "decorative border, ornamental frame",
    "重复": "repeating motif, pattern repetition",
    "几何": "geometric abstraction, hard-edged shapes",
    "有机形状": "organic flowing shapes",

    # ---- 媒介 / 材质 ----
    "布面油画": "oil on canvas painting",
    "木板油画": "oil painting on wood panel",
    "丙烯": "acrylic paint",
    "水彩": "watercolour on paper",
    "水墨": "ink wash painting",
    "版画": "woodblock print",
    "木刻": "woodcut print",
    "石版画": "lithograph",
    "湿壁画": "fresco mural",
    "蛋彩": "tempera painting",
    "镶嵌": "mosaic, tessellated surface",
    "拼贴": "collage, pasted paper elements",
    "厚涂": "thick impasto brushwork, heavy paint texture",
    "平涂": "flat even colour fields, no visible brushwork",
    "零笔触": "no visible brushstrokes, smooth surface",
    "可见笔触": "visible expressive brushstrokes",
    "纸本": "work on paper",
    "织物": "textile, woven fabric surface",
    "玻璃": "glass, translucent surface",
    "皮革": "leather surface",
    "矿物颜料": "mineral pigments, matte granular surface",
    "雕塑感": "sculptural volume, modelled form",
    "粗粝": "rough gritty texture",
    "细腻": "fine delicate finish",

    # ---- 情绪 / 气质 ----
    "压抑": "oppressive, claustrophobic, heavy atmosphere",
    "华丽": "ornate, opulent, lavishly decorated",
    "宁静": "serene, tranquil, calm",
    "戏剧性": "dramatic, theatrical intensity",
    "忧郁": "melancholic, sorrowful",
    "神秘": "mysterious, enigmatic, veiled",
    "梦幻": "dreamlike, surreal, hazy",
    "冷峻": "cold, austere, severe",
    "温柔": "gentle, tender, soft",
    "荒诞": "absurd, unsettling, irrational",
    "庄严": "solemn, dignified, ceremonial",
    "优雅": "elegant, refined, graceful",
    "感伤": "sentimental, nostalgic longing",
    "怀旧": "nostalgic, retrospective",
    "孤独": "lonely, isolated, solitary",
    "疏离": "alienated, detached, distant",
    "不安": "anxious, uneasy, disquieting",
    "愤怒": "angry, confrontational",
    "挑衅": "provocative, transgressive",
    "沉重": "heavy, weighty, grave",
    "轻快": "light, buoyant, cheerful",
    "理性": "rational, measured, intellectual",
    "冷静": "detached, cool, unemotional",
    "感官": "sensual, tactile, bodily",
    "亲密": "intimate, close, private",
    "有力": "forceful, powerful, assertive",
    "克制": "restrained, understated",
    "精确": "precise, exacting, meticulous",
    "快速": "rapid, spontaneous, gestural",
    "怪诞": "grotesque, bizarre",
    "崇高": "sublime, awe-inspiring vastness",
    "日常": "everyday, ordinary, vernacular",
    "工业化": "industrial, machine-made",
    "未来感": "futuristic, sci-fi",
    "复古": "retro, vintage",
    "童趣": "childlike, playful",
    "宗教": "religious, devotional subject",
    "神话": "mythological, legendary subject",
    "政治": "political, propagandistic",

    # ---- 题材 / 场景 ----
    # 这一类是实测补的：第一版只有光影色彩构图，于是「宁静的水墨风景」
    # 里的「风景」、「赛博朋克霓虹雨夜」里的「雨夜」都没被覆盖。
    "风景": "landscape scenery",
    "山水": "mountain and water landscape",
    "人物": "human figure",
    "肖像": "portrait of a person",
    "群像": "group of figures",
    "裸体": "nude figure",
    "静物": "still life objects",
    "室内": "interior scene",
    "城市": "cityscape, urban scene",
    "街景": "street scene",
    "夜景": "night scene, nocturnal",
    "雨夜": "rainy night",
    "海": "sea, ocean",
    "山": "mountains",
    "森林": "forest, trees",
    "天空": "sky",
    "云": "clouds",
    "花卉": "flowers, floral",
    "动物": "animal",
    "战争": "battle scene, warfare",
    "仪式": "ceremony, ritual",
    "劳动": "labour, working figures",
    "室内景": "indoor setting",
    "剪影": "silhouette",

    # ---- 程度副词（中文查询里几乎一定会带）----
    "强烈": "intense, powerful",
    "柔和": "soft, gentle",
    "极其": "extremely",
    "非常": "very",
    "略带": "slightly",

    # ---- 时代 / 风格坐标（不出流派名，只给坐标）----
    "古典": "classical antique style",
    "中世纪": "medieval style",
    "文艺复兴": "renaissance style",
    "巴洛克式": "baroque style",
    "浪漫主义式": "romantic style",
    "写实": "realistic representation",
    "抽象": "abstract, non-representational",
    "极简": "minimalist, reduced to essentials",
    "装饰艺术": "art deco decorative style",
    "手绘": "hand-drawn illustration",
}

# 长词优先匹配：不然「不对称」会被「对称」先吃掉、「无阴影」会被「阴影」吃掉。
_KEYS_BY_LEN = sorted(LEXICON, key=len, reverse=True)


def to_english(query):
    """把中文查询过桥成英文短语。

    返回 (english, matched, misses)：
      english  拼好的英文查询；一个词都没命中时是空串
      matched  命中的中文词，按出现顺序
      misses   看起来是视觉词、但词表里没有的片段（供补词表用）
    """
    if not query:
        return "", [], []
    text = query
    matched, parts = [], []
    for key in _KEYS_BY_LEN:
        if key in text:
            matched.append(key)
            parts.append(LEXICON[key])
            text = text.replace(key, " ")      # 吃掉，避免嵌套重复命中
    english = ", ".join(parts)

    # 挑出「没被吃掉的实词」当作候选缺口。只保留 2–4 字的中文片段，
    # 且必须是汉字 —— 数字、标点、英文都不要（英文本来就能直接编码）。
    # 另外滤掉「的光」「题材」这种虚词残渣：以助词/量词开头或结尾的短片段
    # 基本都是长词被吃掉后的边角，不是缺词。
    _NOISE = ("的", "了", "很", "非", "超", "是", "和", "与", "在", "有",
              "个", "种", "类", "感", "化", "性")
    misses = []
    for seg in re.split(r"[\s,，、。；;：:()（）/]+", text):
        seg = seg.strip()
        if not (2 <= len(seg) <= 4) or not re.fullmatch(r"[\u4e00-\u9fff]+", seg):
            continue
        if seg[0] in _NOISE or seg[-1] in _NOISE:
            continue
        if any(seg in k for k in LEXICON):
            continue
        misses.append(seg)
    return english, matched, misses


def coverage(query):
    """查询被词表覆盖的比例 —— 用来决定「要不要相信这次语义检索」。

    返回 0.0–1.0。全是中文却一个词都没命中时是 0，此时语义检索没有意义，
    应当退回关键词检索并如实说明。
    """
    if not query:
        return 0.0
    cjk = re.findall(r"[\u4e00-\u9fff]", query)
    has_latin = bool(re.search(r"[a-zA-Z]{3,}", query))
    if not cjk:
        return 1.0 if has_latin else 0.0      # 纯英文：管道直接可用
    _, matched, _ = to_english(query)
    if not matched:
        return 0.0
    covered = sum(len(m) for m in matched)
    return min(1.0, float(covered) / float(len(cjk)))
