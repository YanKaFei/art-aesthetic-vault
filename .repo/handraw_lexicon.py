# -*- coding: utf-8 -*-
"""handraw_lexicon.py —— 第 7 大类「手绘艺术风格」的词表层。

## 这一层解决什么问题

handraw-style 的 274 个风格，每条只有四样东西：编号、组（A–H）、
参考作者、生图名称、以及一段**中文核心视觉特征**（`traits`）。
它没有本库要求的「七层英文提示词」，也没有配色、光照、媒介这些字段。

所以融合的关键问题是：**这七层从哪来？**

三条路，只有一条是对的：

    1. 让模型看着编号编七层      → 编出来的东西没有出处，读者无法核对，
                                  而且 274 条里错的比例没人知道。不做。
    2. 干脆不写七层，只搬 traits  → 「融合」退化成「复制一份文件进来」，
                                  检索、compose、视频层全都用不了。也不做。
    3. **从 traits 里抽**          → 词表是手写的（下面这些），命中与否由
                                  traits 原文决定，卡上标出这个词是哪来的。
                                  抽不到的层**明确标成组级默认**，不假装是
                                  这个风格自己的特征。

本模块就是第 3 条路的那张词表。

## 卡上的两个标记

    ⟨条⟩  这个词来自该风格自己的 traits 原文（逐字命中，可核对）
    ⟨组⟩  这个词是 A–H 该组的**组级共识**（组名本身就说明了媒介与谱系），
          不是这一条独有的特征

两个标记都会印在卡的六维表里。读者一眼能看出哪句话是 handraw 说的、
哪句话是我们按组推的 —— 这正是本库 `refs.py` 那句「没写的不是遗漏，
是还没做」的同一种态度：**不确定的部分要显形，不要伪装成确定。**

## 词表怎么来的

把 274 条 traits 拆成 516 个分句，统计高频词与共现，再按库里六维的
说法（色彩/光影/笔触/构图/材质/情绪）归类。只有**确实在手绘语境里有
英文对应说法**的词才收 —— 「脸型」「衣褶」这类词收进来只会污染提示词，
它们留在 traits 原文里就够了。

## 与 visual_lexicon 的关系

`EXTRA_LEXICON` 会被 `visual_lexicon` 合并进它的中文过桥词表 ——
这样 `artvault.py search "钢笔速写 留白"` 的语义检索也能命中这一大类。
合并方向是单向的（visual_lexicon 读本模块），避免循环导入。
"""

# 大类名：与另外 6 个分类同级，出现在 CATEGORIES 里、生成分类索引页。
CATEGORY = "手绘艺术风格"

# 编号参考图的落位。**必须落在 99-attachments/images/ 下** ——
# 验收第 1/7/15 项（断链/孤儿图/克隆完整性）只认这个根，
# 放别处会让 274 张卡在「别人 clone 下来」时全部断图。
IMAGES_REL = "99-attachments/images/handraw"
IMAGE_PREFIX = "handraw-"

# 原始数据的位置（30-handraw-style/ 是整棵装进来的仓库，见其 SOURCE.md）
STYLES_JSON = ("30-handraw-style/skills/handdraw-style-prompter/"
               "references/styles.json")


# --------------------------------------------------------------- 组级默认
# A–H 是 handraw-style 自己的分组，逐字沿用，不改写、不重排。
#   region   从组名读出，填 frontmatter 的「地区」
#   *_zh     Chinese side of the six-dimension table（组级默认，卡上标 ⟨组⟩）
#   *_en     English side（同一件事的提示词写法）
#   neg      组级追加的负向词
#   video    三行视频层（运动 / 运镜 / 这个组的视频关键）
#   anchors  与本库既有流派卡的谱系关联（**编者加的**，不是 handraw 的数据，
#            卡上会注明）。每个 slug 都在 movements.py 里真实存在。
GROUPS = {
    "A": {
        "label": "国际社论漫画 / 幽默手绘",
        "label_en": "International Editorial Cartoon / Humour",
        "region": "国际",
        "medium_zh": "钢笔 / 墨水线稿，纸面",
        "medium_en": "ink pen linework on paper",
        "light_zh": "平光，没有方向性阴影（漫画是纸面印刷媒介）",
        "light_en": "flat even lighting, no cast shadows",
        "comp_zh": "单人或极简场景，主体小、白底留白大",
        "comp_en": "single figure, generous white space, uncluttered frame",
        "mood_zh": "冷面、尴尬或荒诞的幽默",
        "mood_en": "deadpan, awkward, absurd humour",
        "neg": "sweet cutesy smile, generic chibi face, airbrushed finish",
        "camera_en": "eye-level, medium shot, static camera, flat perspective",
        "video": {
            "motion": "线条基本不动；人物眨眼、嘴角抽动、手里的小物件轻晃",
            "camera": "固定机位；最多极缓推近",
            "note": "手绘漫画一动起来最容易变成 3D —— 全片保持二维平涂与纸面质感，"
                    "线条粗细不能忽大忽小",
        },
        "anchors": ["pop-art", "street-art"],
    },
    "B": {
        "label": "国际绘本 / 叙事型手绘",
        "label_en": "International Picture Book / Narrative",
        "region": "国际",
        "medium_zh": "绘本插图，墨水配水彩或水粉，纸面",
        "medium_en": "picture-book illustration, ink with watercolour or gouache on paper",
        "light_zh": "柔和环境光，轻微体积阴影",
        "light_en": "soft ambient light with gentle shading",
        "comp_zh": "叙事性场景，圆润造型，角色与环境同框",
        "comp_en": "narrative scene, rounded shapes, character within an environment",
        "mood_zh": "温暖、童话、有叙述感",
        "mood_en": "warm, storybook, narrative",
        "neg": "harsh chiaroscuro, photorealistic rendering, vector-flat edges",
        "camera_en": "eye-level, wide establishing shot, gentle flat perspective",
        "video": {
            "motion": "角色轻微呼吸起伏；环境里的小物件轻晃；景别像翻页一样推进",
            "camera": "固定机位或极缓平移，像翻绘本",
            "note": "不要加立体光照；色块边缘要保持手绘的不齐整，别磨成矢量",
        },
        "anchors": ["naive-art", "magic-realism"],
    },
    "C": {
        "label": "现代平面 / 艺术化人物体系",
        "label_en": "Modern Graphic / Stylised Figures",
        "region": "国际",
        "medium_zh": "现代平面插画，平涂色块 + 手绘边缘，带孔版印刷感",
        "medium_en": "modern graphic illustration, flat colour blocks with hand-drawn edges, screen-print feel",
        "light_zh": "平光、图形化，几乎不做体积塑造",
        "light_en": "flat graphic lighting, minimal modelling",
        "comp_zh": "海报式平衡，外轮廓清楚，大形优先",
        "comp_en": "poster-like balance, bold readable silhouette, big shapes first",
        "mood_zh": "冷静、时尚、疏离",
        "mood_en": "cool, fashionable, detached",
        "neg": "intricate detail, muddy colour mixing, harsh 3d volume",
        "camera_en": "eye-level, full-body shot, flat graphic perspective",
        "video": {
            "motion": "图形元素依次出现；色块轻微位移；线条本身不动",
            "camera": "固定机位；可做小幅横移",
            "note": "平面插画动起来最容易变成动效广告 —— 保持手绘边缘与有限色板",
        },
        "anchors": ["art-deco", "bauhaus"],
    },
    "D": {
        "label": "日本作者 / 当代插画体系",
        "label_en": "Japanese Authors / Contemporary Illustration",
        "region": "日本",
        "medium_zh": "日系数码插画，干净线稿 + 柔和的赛璐璐或水彩上色",
        "medium_en": "Japanese digital illustration, clean line art with soft cel or watercolour shading",
        "light_zh": "柔和漫射光，轻微轮廓光",
        "light_en": "soft diffused light with a gentle rim",
        "comp_zh": "角色优先的构图，背景干净",
        "comp_en": "character-focused composition, clean background",
        "mood_zh": "纤细、情绪化、空气感",
        "mood_en": "delicate, emotional, airy",
        "neg": "3d anime render, plastic skin, over-sharpened line art",
        "camera_en": "eye-level, medium close-up, shallow depth of field",
        "video": {
            "motion": "发丝与衣角轻摆；表情细节变化；光斑缓慢移动",
            "camera": "极缓推近或轻微环绕；不要快切",
            "note": "线稿粗细要全片一致，上色保留透明叠染，别渲染成 3D 卡通",
        },
        "anchors": ["superflat", "ukiyo-e"],
    },
    "E": {
        "label": "中国作者 / 当代插画体系",
        "label_en": "Chinese Authors / Contemporary Illustration",
        "region": "中国",
        "medium_zh": "中国当代插画，墨线 + 数码上色，宣纸或国画纸质感",
        "medium_en": "Chinese contemporary illustration, ink line with digital colour, xuan-paper texture",
        "light_zh": "柔和均匀光，带淡墨晕染",
        "light_en": "soft even light with a light ink-wash bleed",
        "comp_zh": "人物居中，留白多，画面轻",
        "comp_en": "figure-centred composition with generous negative space",
        "mood_zh": "含蓄、诗性、有东方气息",
        "mood_en": "understated, poetic, East-Asian in feel",
        "neg": "3d render, plastic skin, western oil-painting glazing",
        "camera_en": "eye-level, medium shot, flat perspective with generous space",
        "video": {
            "motion": "衣袂与发丝轻摆；墨色缓慢晕开；尘埃或花瓣飘过",
            "camera": "极缓推近或轻微横移",
            "note": "别把墨线渲染成均匀矢量描边；留白要留住，不要填满背景",
        },
        "anchors": ["ink-wash-xieyi", "gongbi"],
    },
    "F": {
        "label": "通用网感 / 媒介 / 地域手绘",
        "label_en": "General Web / Medium / Regional",
        "region": "通用 / 地域",
        "medium_zh": "混合手绘媒介：马克笔、彩铅、数码涂鸦，带颗粒或纸纹",
        "medium_en": "mixed hand-drawn medium, marker and coloured pencil and digital doodle, grainy texture",
        "light_zh": "平光到轻微塑形",
        "light_en": "flat to lightly modelled lighting",
        "comp_zh": "适合屏幕观看的构图，外轮廓强，一眼能读懂",
        "comp_en": "web-friendly framing, strong silhouette, instantly readable",
        "mood_zh": "轻松、网感、当下",
        "mood_en": "casual, internet-native, of-the-moment",
        "neg": "corporate vector flatness, airbrushed gradients, 3d render",
        "camera_en": "eye-level, medium shot, flat perspective",
        "video": {
            "motion": "轻微循环动作：点头、晃动、贴纸式抖动",
            "camera": "以固定机位为主",
            "note": "网感手绘要留住颗粒与纸纹，最容易被磨皮成矢量",
        },
        "anchors": ["street-art", "y2k"],
    },
    "G": {
        "label": "附件新增 / 中国当代插画补充",
        "label_en": "New Additions / Chinese Contemporary",
        "region": "中国",
        "medium_zh": "中国当代插画，墨线 + 数码上色，纸面质感",
        "medium_en": "Chinese contemporary illustration, ink line with digital colour, paper texture",
        "light_zh": "柔和均匀光",
        "light_en": "soft even light",
        "comp_zh": "人物或小场景居中，留白克制",
        "comp_en": "centred figure or small scene, restrained negative space",
        "mood_zh": "当代、克制、带东方气味",
        "mood_en": "contemporary, restrained, East-Asian in feel",
        "neg": "3d render, plastic skin, western oil glazing",
        "camera_en": "eye-level, medium shot, flat perspective",
        "video": {
            "motion": "衣角与发丝轻摆；背景元素缓慢浮现",
            "camera": "极缓推近",
            "note": "沿用 E 组的注意事项：留白要留住，墨线不能变成均匀矢量描边",
        },
        "anchors": ["gongbi"],
    },
    "H": {
        "label": "其他",
        "label_en": "Others",
        "region": "其他",
        "medium_zh": "手绘插画，墨水与颜料在纸上",
        "medium_en": "hand-drawn illustration, ink and colour on paper",
        "light_zh": "平光、无明显方向性",
        "light_en": "flat even lighting, no strong direction",
        "comp_zh": "外轮廓清楚、画面不拥挤",
        "comp_en": "clear silhouette, uncluttered",
        "mood_zh": "该组不共用统一情绪，以该条 traits 为准",
        "mood_en": "as described by the individual entry",
        "neg": "3d render, photorealistic finish, over-painted look",
        "camera_en": "eye-level, medium shot, flat perspective",
        "video": {
            "motion": "画面内的小幅动作，一次只动一个元素",
            "camera": "固定机位",
            "note": "保持手绘媒介的原始质感，不要中途漂移成另一种画风",
        },
        "anchors": [],
    },
}


# --------------------------------------------------------------- 层词表
# (中文子串, 六维, 英文提示词片段)
# 匹配是**子串匹配**，长的先匹配（避免「冷幽默」被「幽默」吃掉、
# 「低饱和」被「饱和」吃掉）。命中即写进对应的层，卡上标 ⟨条⟩。
KEYWORDS = [
    # ---- 笔触：线条与用笔 ----------------------------------------------
    ("极细钢笔", "笔触", "very fine pen linework"),
    ("钢笔速写", "笔触", "pen sketch lines"),
    ("钢笔", "笔触", "ink pen linework"),
    ("墨线", "笔触", "inked contour lines"),
    ("毛笔", "笔触", "brush and ink strokes"),
    ("连续线", "笔触", "continuous single-line drawing"),
    ("密集排线", "笔触", "dense cross-hatching"),
    ("排线", "笔触", "cross-hatching"),
    ("交叉线", "笔触", "cross-hatched shading"),
    ("粗黑轮廓", "笔触", "thick black outlines"),
    ("粗黑线", "笔触", "bold black linework"),
    ("粗轮廓", "笔触", "bold outline"),
    ("粗线", "笔触", "thick lines"),
    ("细黑线", "笔触", "fine black linework"),
    ("细线", "笔触", "thin linework"),
    ("黑线", "笔触", "black linework"),
    ("极简黑线", "笔触", "minimal black linework"),
    ("歪斜线条", "笔触", "wobbly hand-drawn lines"),
    ("断裂墨线", "笔触", "broken scratchy ink lines"),
    ("极少线条", "笔触", "extremely sparse lines"),
    ("线描", "笔触", "line drawing"),
    ("线稿", "笔触", "clean line art"),
    ("轮廓清楚", "笔触", "clear readable contour"),
    ("轮廓", "笔触", "defined contour"),
    ("厚涂", "笔触", "thick impasto strokes"),
    ("笔压", "笔触", "visible pen pressure variation"),
    ("手绘笔压", "笔触", "visible hand-drawn pen pressure"),
    ("速写", "笔触", "sketchy gestural linework"),
    ("鼠绘", "笔触", "crude mouse-drawn digital linework"),
    ("涂鸦", "笔触", "doodle linework"),
    ("平涂", "笔触", "flat colour fills"),
    ("扁平色块", "笔触", "flat colour blocks"),
    ("色块", "笔触", "solid colour blocks"),
    ("几何", "笔触", "geometric simplification"),
    ("图标化", "笔触", "icon-like simplification"),
    ("高度概括", "笔触", "highly simplified shapes"),
    ("做减法", "笔触", "reduced to essential shapes"),
    ("大形", "笔触", "readable shapes built from big forms"),
    ("手写字", "笔触", "handwritten lettering"),
    ("手写文字", "笔触", "handwritten lettering"),
    ("手写", "笔触", "handwritten elements"),

    # ---- 材质：媒介与纸面 ----------------------------------------------
    ("水彩", "材质", "watercolour wash"),
    ("透明叠染", "材质", "transparent layered washes"),
    ("柔和水彩", "材质", "soft watercolour washes"),
    ("彩铅", "材质", "coloured pencil texture"),
    ("蜡笔", "材质", "wax crayon texture"),
    ("油画棒", "材质", "oil pastel texture"),
    ("马克笔", "材质", "marker strokes"),
    ("版画", "材质", "printmaking texture"),
    ("丝网", "材质", "screen-print texture"),
    ("孔版", "材质", "risograph misregistration and grain"),
    ("riso", "材质", "risograph misregistration and grain"),
    ("拼贴", "材质", "paper collage"),
    ("纸纹", "材质", "visible paper grain"),
    ("纸张质感", "材质", "paper surface"),
    ("粗糙", "材质", "rough textured surface"),
    ("颗粒", "材质", "grainy texture"),
    ("粗颗粒", "材质", "coarse grain"),
    ("手帐", "材质", "notebook / zine feel"),
    ("zine", "材质", "zine-printed feel"),
    ("反精致", "材质", "deliberately unpolished surface"),
    ("贴纸", "材质", "sticker-like flat shapes"),
    ("数码", "材质", "digital drawing"),
    ("数位", "材质", "digital tablet drawing"),
    ("水墨", "材质", "ink wash"),

    # ---- 色彩 ----------------------------------------------------------
    ("黑白", "色彩", "black and white"),
    ("单色", "色彩", "monochrome"),
    ("低饱和", "色彩", "desaturated muted colours"),
    ("高饱和", "色彩", "highly saturated colours"),
    ("有限色", "色彩", "limited colour palette"),
    ("粉彩", "色彩", "pastel palette"),
    ("柔和色", "色彩", "soft restrained colours"),
    ("荧光", "色彩", "fluorescent accents"),
    ("撞色", "色彩", "bold clashing colour pairing"),
    ("暖色", "色彩", "warm palette"),
    ("冷色", "色彩", "cool palette"),
    ("白底", "色彩", "plain white background"),
    ("米色", "色彩", "beige and off-white"),
    ("灰蓝", "色彩", "grey-blue"),
    ("灰绿", "色彩", "grey-green"),
    ("点色", "色彩", "small accent colour dots"),
    ("金色", "色彩", "gold accents"),
    ("泥土色", "色彩", "earth pigments"),
    ("蓝", "色彩", "blue accents"),
    ("粉", "色彩", "pink accents"),
    ("黄", "色彩", "yellow accents"),
    ("红", "色彩", "red accents"),

    # ---- 光影 ----------------------------------------------------------
    ("平光", "光影", "flat even lighting"),
    ("无阴影", "光影", "no cast shadows"),
    ("无光影", "光影", "no modelled lighting"),
    ("强烈光影", "光影", "strong directional light and shadow"),
    ("强光", "光影", "strong light source"),
    ("高对比", "光影", "high contrast"),
    ("逆光", "光影", "backlit"),
    ("柔和光", "光影", "soft diffused light"),
    ("柔和阴影", "光影", "soft shadows"),
    ("阴影", "光影", "soft shading"),
    ("光斑", "光影", "dappled light spots"),

    # ---- 构图 ----------------------------------------------------------
    ("大面积留白", "构图", "generous negative space"),
    ("大留白", "构图", "large areas of negative space"),
    ("大量留白", "构图", "lots of negative space"),
    ("留白", "构图", "negative space"),
    ("满版", "构图", "edge-to-edge composition"),
    ("满构图", "构图", "full-bleed composition"),
    ("全身", "构图", "full-body framing"),
    ("特写", "构图", "close-up framing"),
    ("小人物大空间", "构图", "tiny figure in a vast space"),
    ("小人物", "构图", "small figures"),
    ("单人", "构图", "single-figure focus"),
    ("居中", "构图", "centred composition"),
    ("对称", "构图", "symmetrical composition"),
    ("俯视", "构图", "high-angle view"),
    ("仰视", "构图", "low-angle view"),
    ("比例失衡", "构图", "deliberately off-balance proportions"),
    ("比例夸张", "构图", "exaggerated proportions"),
    ("比例偏修长", "构图", "elongated proportions"),
    ("错透视", "构图", "intentionally skewed perspective"),
    ("贴纸式", "构图", "sticker-style placement"),
    ("四宫格", "构图", "four-panel grid"),
    ("分镜", "构图", "comic-panel layout"),
    ("单格", "构图", "single-panel framing"),

    # ---- 情绪 ----------------------------------------------------------
    ("冷幽默", "情绪", "deadpan humour"),
    ("英式反鸡汤", "情绪", "dry British anti-inspirational humour"),
    ("黑色幽默", "情绪", "dark humour"),
    ("幽默", "情绪", "humorous"),
    ("冷面", "情绪", "deadpan"),
    ("冷脸", "情绪", "deadpan expression"),
    ("荒诞", "情绪", "absurd"),
    ("尴尬", "情绪", "awkward, cringe comedy"),
    ("神经质", "情绪", "nervous and jittery"),
    ("焦虑", "情绪", "anxious, urban neurosis"),
    ("讽刺", "情绪", "satirical"),
    ("恶趣味", "情绪", "off-colour humour"),
    ("meme", "情绪", "internet-meme energy"),
    ("童趣", "情绪", "childlike and playful"),
    ("儿童", "情绪", "childlike"),
    ("幼稚", "情绪", "childish and crude on purpose"),
    ("治愈", "情绪", "soothing and comforting"),
    ("温柔", "情绪", "gentle and tender"),
    ("诗性", "情绪", "poetic"),
    ("低调", "情绪", "understated"),
    ("潮流", "情绪", "trendy and fashionable"),
    ("时尚", "情绪", "fashionable"),
    ("青春", "情绪", "youthful"),
    ("怀旧", "情绪", "nostalgic"),
    ("复古", "情绪", "retro"),
    ("阴郁", "情绪", "gloomy"),
    ("黑暗", "情绪", "dark"),
    ("幻想", "情绪", "fantasy"),
    ("日常", "情绪", "everyday slice-of-life"),
    ("生活记录", "情绪", "diary-like slice-of-life"),
    ("平静", "情绪", "calm and quiet"),
    ("动态极强", "情绪", "highly dynamic"),
    ("强动作", "情绪", "strong physical action"),
    ("智性", "情绪", "intellectual wit"),
    ("亲密", "情绪", "intimate"),
    ("松弛", "情绪", "relaxed and casual"),
    ("安静", "情绪", "quiet"),
]

# 长的先匹配：「冷幽默」要在「幽默」之前命中
KEYWORDS.sort(key=lambda x: -len(x[0]))

# 色彩是唯一一个**故意不给组级默认**的维度：手绘类的用色逐条不同，
# 用一组色板冒充 274 条的配色就是编。抽不到时卡上明说「未标注」。
COLOR_FALLBACK_ZH = "组级底色（该条 traits 未标注具体用色）"
COLOR_FALLBACK_EN = "colour follows the group's base palette"

# 抽不到任何词时，用组级默认兜底 —— 这两个表只用于**判断是否命中**，
# 真正的文字来自 GROUPS。
DIM_FALLBACK = {
    "色彩": ("色彩", "colour"),
    "光影": ("光影", "lighting"),
    "笔触": ("笔触", "medium"),
    "构图": ("构图", "composition"),
    "材质": ("材质", "medium"),
    "情绪": ("情绪", "mood"),
}

# 六维 → 七层里的层名。笔触与材质都并进 medium 层。
DIM_TO_LAYER = {
    "色彩": "color",
    "光影": "lighting",
    "笔触": "medium",
    "构图": "composition",
    "材质": "medium",
    "情绪": "mood",
}

DIMS = ["色彩", "光影", "笔触", "构图", "材质", "情绪"]


# --------------------------------------------------------------- 配色
# 从 traits 里的色彩词推到 hex。**这是推导，不是引用** —— 卡上会写明
# 「配色由 traits 的色彩词推导 + 组级底色」。推不出来时用组级底色。
PAPER = ("#FAF7F0", "纸白")
INK = ("#1A1A1A", "墨黑")

# 值统一是 (hex, 中文色名) 二元组。
COLOR_HEX = {
    "黑白": ("#1A1A1A", "墨黑"),
    "单色": ("#1A1A1A", "墨黑"),
    "白底": ("#FAF7F0", "纸白"),
    "米色": ("#E8DFC8", "米色"),
    "米黄": ("#E8DFC8", "米色"),
    "粉彩": ("#F0D3C0", "粉彩"),
    "粉": ("#F2C6C2", "肉粉"),
    "红": ("#B4574A", "砖红"),
    "黄": ("#E8C46A", "暖黄"),
    "橙": ("#D98A3D", "暖橙"),
    "灰蓝": ("#8FA3B8", "灰蓝"),
    "蓝": ("#3B4E6B", "靛蓝"),
    "灰绿": ("#9AA98F", "灰绿"),
    "绿": ("#7C8F6A", "灰绿"),
    "荧光": ("#FF5FA2", "荧光粉"),
    "金": ("#C9A227", "金"),
    "紫": ("#6E5A8C", "紫"),
    "泥土": ("#8C6A3F", "赭土"),
    "暖色": ("#E8C46A", "暖黄"),
    "冷色": ("#8FA3B8", "灰蓝"),
    "低饱和": ("#9AA98F", "灰绿"),
    "高饱和": ("#FF5FA2", "荧光粉"),
}

GROUP_BASE_PALETTE = {
    "A": [INK, PAPER, ("#8FA3B8", "灰蓝")],
    "B": [INK, PAPER, ("#E8C46A", "暖黄"), ("#9AA98F", "灰绿")],
    "C": [INK, PAPER, ("#B4574A", "砖红"), ("#3B4E6B", "靛蓝")],
    "D": [INK, PAPER, ("#F2C6C2", "肉粉"), ("#8FA3B8", "灰蓝")],
    "E": [INK, PAPER, ("#D9C7A3", "宣纸黄"), ("#7C8F6A", "灰绿")],
    "F": [INK, PAPER, ("#FF5FA2", "荧光粉"), ("#E8C46A", "暖黄")],
    "G": [INK, PAPER, ("#D9C7A3", "宣纸黄"), ("#6E5A8C", "紫")],
    "H": [INK, PAPER, ("#E8DFC8", "米色"), ("#9AA98F", "灰绿")],
}


# --------------------------------------------------------------- 过桥词表
# 合并进 visual_lexicon.LEXICON，让中文语义检索也能命中这一大类。
# 只放**库里其它地方没有的**手绘说法；重复键会覆盖同义项，不会冲突。
EXTRA_LEXICON = {
    "手绘": "hand-drawn illustration",
    "线稿": "clean line art illustration",
    "线描": "line drawing",
    "黑线": "black linework",
    "粗黑线": "bold black linework",
    "钢笔": "ink pen linework",
    "钢笔速写": "pen sketch",
    "毛笔": "brush and ink",
    "排线": "cross-hatching",
    "密集排线": "dense cross-hatching",
    "留白": "negative space, uncluttered composition",
    "大留白": "large areas of negative space",
    "纸纹": "visible paper grain",
    "颗粒": "grainy texture",
    "水彩": "watercolour wash",
    "彩铅": "coloured pencil",
    "蜡笔": "wax crayon",
    "马克笔": "marker drawing",
    "涂鸦": "doodle",
    "鼠绘": "crude mouse-drawn digital linework",
    "手写": "handwritten lettering",
    "拼贴": "paper collage",
    "版画": "printmaking",
    "孔版": "risograph",
    "贴纸": "sticker-like flat shapes",
    "扁平色块": "flat colour blocks",
    "色块": "solid colour blocks",
    "平涂": "flat colour fills",
    "厚涂": "thick impasto",
    "撞色": "bold clashing colours",
    "有限色": "limited colour palette",
    "荧光": "fluorescent accents",
    "冷幽默": "deadpan humour",
    "荒诞": "absurd",
    "尴尬": "awkward cringe comedy",
    "治愈": "soothing and comforting",
    "童趣": "childlike and playful",
    "网感": "internet-native visual slang",
    "绘本": "picture-book illustration",
    "社论漫画": "editorial cartoon",
    "鼠绘感": "low-fidelity crude digital drawing",
}
