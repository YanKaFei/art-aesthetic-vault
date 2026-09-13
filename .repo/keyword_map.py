# -*- coding: utf-8 -*-
"""keyword_map.py —— 关键词辨析的数据层。

同一个视觉概念常有多个叫法（先锋 / 前卫 / avant-garde；超现实 /
超现实主义 / surrealism）。这里把它们聚成簇，说清彼此的差别，
让「搜任何一说都能找到同一张卡」这件事成立。

`CLUSTERS` 同时供两处使用：
  · `artvault_core.search` 的别名表（同义词 → slug）
  · 笔记 [[关键词图谱]] 的正文
"""
# ---------------------------------------------------------------------------
# 四个核心关键词的语义簇
# ---------------------------------------------------------------------------
CLUSTERS = [
{
 "key": "先锋艺术",
 "en": "Avant-Garde",
 "card": "avant-garde",
 "define": "不是一个风格，而是一个「位置」：主动站在体制与观众前面，"
           "以打破既有规则为目的。所以同一个词下可以同时容纳达达、构成主义、"
           "未来主义——它们画法完全不同，但姿态一致。",
 "boundary": [
   ("不等于「现代艺术」", "现代艺术是时间段（约1860–1970），先锋是态度。19世纪也有先锋，21世纪也有。"),
   ("不等于「前卫」吗？", "中文的「前卫艺术」和「先锋艺术」一般可互换；「先锋派」偏文学与戏剧语境。"),
   ("不等于「当代艺术」", "当代艺术是时间段（约1970至今）；先锋可以发生在任何时代。"),
 ],
 "synonyms": ["前卫艺术", "先锋派", "前卫派", "avant-garde", "avantgarde",
              "新先锋", "neo-avant-garde", "实验艺术", "反艺术", "anti-art"],
 "related_cards": ["dada", "constructivism", "suprematism", "futurism",
                   "surrealism", "conceptual-art", "situationist"],
 "prompt_use": "单独写 avant-garde 几乎没用——模型不知道你要什么画面。"
               "必须叠加一个具体流派：`avant-garde constructivist poster` / "
               "`avant-garde dada collage`。",
},
{
 "key": "当代艺术",
 "en": "Contemporary Art",
 "card": "contemporary-art",
 "define": "一个时间段（约1970年至今），不是一个风格。它的特征是「没有统一风格」："
           "装置、影像、行为、社会参与、数字艺术同时并存，靠双年展体系与理论话语组织。",
 "boundary": [
   ("不等于「现代艺术」", "现代艺术有统一的形式追求（抽象、原创、进步）；当代艺术放弃了这些共识。"),
   ("不等于「后现代」", "后现代是一种对现代主义的批判立场；当代艺术是它之后的时间容器，包含但不限于后现代。"),
   ("不是一种可画的风格", "写提示词时必须叠加具体形式：installation / video art / performance。"),
 ],
 "synonyms": ["当代", "contemporary", "当代艺术", "全球艺术",
              "双年展艺术", "biennale art", "后观念艺术", "post-conceptual"],
 "related_cards": ["postmodernism", "conceptual-art", "installation-art",
                   "digital-art", "feminist-art", "street-art"],
 "prompt_use": "`contemporary art installation` 或 `contemporary art gallery`，"
               "不要单独用。想画面感强就用具体媒介词。",
},
{
 "key": "后现代艺术",
 "en": "Postmodern Art",
 "card": "postmodernism",
 "define": "对现代主义「宏大叙事」的怀疑：不再相信原创、进步与唯一真理，"
           "转而使用拼贴（pastiche）、引用、戏仿，把一切历史风格当成可用符号。",
 "boundary": [
   ("和当代艺术的差别", "后现代是立场（反元叙事），当代是时间段。多数后现代作品属于当代艺术，反之不然。"),
   ("和波普的差别", "波普挪用商业图像，仍有批判距离；后现代把挪用本身当成方法，不一定要批判。"),
   ("建筑上更典型", "文丘里、格雷夫斯的后现代建筑比绘画更能说明这个立场。"),
 ],
 "synonyms": ["后现代", "postmodern", "postmodernism", "后现代主义",
              "拼贴艺术", "pastiche", "戏仿", "parody", "挪用艺术", "appropriation art",
              "元叙事", "meta-narrative", "解构", "deconstruction"],
 "related_cards": ["pop-art", "neo-dada", "conceptual-art", "kitsch", "neo-pop"],
 "prompt_use": "`postmodern pastiche, ironic quotation of baroque and neon signage` —— "
               "关键词是「并置两种不相容的符号」。",
},
{
 "key": "超现实主义",
 "en": "Surrealism",
 "card": "surrealism",
 "define": "用最写实的手法画最不可能的事：让梦看起来像照片。"
           "建立在弗洛伊德的无意识理论上，1924年由布勒东宣言确立。",
 "boundary": [
   ("和魔幻现实主义的差别", "超现实有荒诞并置与变形；魔幻现实主义只把现实画得过度清晰，不加荒诞元素。"),
   ("和形而上绘画的差别", "形而上绘画更早、更克制、更建筑化（德·基里科的空广场）。"),
   ("和奇幻艺术的差别", "奇幻艺术是类型文学插图；超现实主义是反理性的思想运动。"),
 ],
 "synonyms": ["超现实", "surrealism", "surrealist", "超现实派", "梦的超现实",
              "自动主义", "automatism", "无意识", "uncanny", "不可思议",
              "达利式", "dali-esque", "马格利特式", "magritte-like"],
 "related_cards": ["dada", "metaphysical-art", "magic-realism", "symbolism",
                   "surrealist-photography", "dreamcore"],
 "prompt_use": "必须写 `hyper-realistic rendering of impossible scenes`——"
               "超现实主义的力量来自「画得极真 + 内容极不合理」的组合，"
               "只写 surreal 会得到泛泛的奇幻画。",
},
]


# ---------------------------------------------------------------------------
# 关键词 → 流派卡 的显式近义映射（网站命名 → 本库 slug）
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 索引
# ---------------------------------------------------------------------------
def by_slug_map(cards):
    """cards: [{'slug', 'name_zh', ...}] → {slug: card}。

    原来这里还有一张 175 条的 WikiArt 风格名映射表和一份兜底表 ——
    它们的唯一用途是生成「关键词图谱」里那几张跨界对照表，而那些表已经
    不发布了（讲的是数据从哪来，不是知识）。表留着没人用，删掉。
    """
    return {c["slug"]: c for c in cards}
