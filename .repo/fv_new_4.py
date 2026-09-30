# -*- coding: utf-8 -*-
"""fv_new_4.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "lee-chang-dong-burning",
        "director_zh": "李沧东",
        "director_en": "Lee Chang-dong",
        "director_slug": "lee-chang-dong",
        "title_zh": "燃烧",
        "title_en": "Burning",
        "year": 2018,
        "one_liner": "**黄昏的橙与夜的黑**——把「不安」拍成一种持续的暮色，光在人物背后慢慢消失。",
        "core": [
            "黄昏的橙金与夜的黑是两套色板，切换跟着叙事的不安推进",
            "大面积暗部，人物常只剩轮廓，脸在暮色里难以辨认",
            "长焦与远距离观察，人物被隔在环境的另一边",
            "构图常把大片空景（田野、湖、温室）留在画面里，人物很小"
        ],
        "visual": {
            "色彩": "黄昏橙金、暗绿、灰蓝、深黑；低饱和，暖色随时间退去",
            "光影": "自然黄昏光与极少的实用光源；夜段大面积黑，只有一点远处的灯",
            "笔触": "（电影媒介）数字摄影，柔和暗部，轻微噪点",
            "构图": "长焦远观、大片空景留白、人物偏置或背对镜头",
            "材质": "草地、塑料大棚、金属、玻璃、烟、夕阳、旧墙",
            "情绪": "悬而未决、阶级的疏离、缓慢蔓延的不安"
        },
        "layers": {
            "style": "Lee Chang-dong Burning, dusky orange to black, long-lens observation, ambiguous slow-burn mystery",
            "lighting": "natural dusk light fading to near darkness, minimal practical sources at night, large black areas with a single distant light, silhouettes",
            "color": "dusk orange-gold, dark green, slate blue, deep black; low saturation with warmth draining out of the frame",
            "composition": "telephoto distant framing, large empty fields and lakes, subject off-centre or turned away, small figures",
            "medium": "digital cinema, soft shadow rolloff, subtle noise",
            "mood": "unresolved, class alienation, slowly spreading unease",
            "camera": "distant long lens, slow pan, static observation, occasional handheld follow"
        },
        "negative": "saturated colors, bright flat daylight, close-up intimate framing, fast cutting, lens flare, warm cozy light",
        "palette": [
            [
                "#C97A2B",
                "黄昏橙"
            ],
            [
                "#3E5A3A",
                "暗绿"
            ],
            [
                "#4A5A6B",
                "暮蓝"
            ],
            [
                "#12140F",
                "夜黑"
            ],
            [
                "#8A7A5C",
                "干草褐"
            ],
            [
                "#A8B0A0",
                "雾白"
            ]
        ],
        "video": {
            "运动": "夕阳下沉、草被风压、烟升起、远处一点光缓慢移动",
            "运镜": "长焦远观、缓慢横移",
            "时长": "10 秒",
            "关键": "**暖色要随时间退去**（黄昏→黑）；保持明亮的暖调会丢掉这部片的不安"
        },
        "pitfalls": [
            "写 mystery thriller 会得到类型片的快节奏 → 这部片是**缓慢的观察**",
            "长焦远观是语法，特写会杀死疏离感",
            "高饱和是反的"
        ],
        "see_also": [
            "realism",
            "photorealism"
        ],
        "title_original": "Burning",
        "filmgrab": "https://film-grab.com/2019/12/10/burning/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/chang-dong-lee/",
        "source": "curated"
    },
    {
        "slug": "yang-edward-yi-yi",
        "director_zh": "杨德昌",
        "director_en": "Edward Yang",
        "director_slug": "edward-yang",
        "title_zh": "一一",
        "title_en": "Yi Yi",
        "year": 2000,
        "one_liner": "**玻璃反射构图**——城市中产的冷白日光与办公室荧光，人总被映在另一层空间里。",
        "core": [
            "大量隔着玻璃拍摄：反射把人物与城市叠在同一平面",
            "冷白日光与荧光灯为主，色温偏冷，几乎无暖色",
            "静止的中远景与对称的室内，人物被安排在几何里",
            "夜间段落是玻璃幕墙的蓝绿反光，不是暖色灯光"
        ],
        "visual": {
            "色彩": "冷白、灰蓝、玻璃绿、米灰；低饱和，绿色调明显",
            "光影": "日光灯与办公室荧光；均匀但偏冷，阴影浅而硬",
            "笔触": "（电影媒介）35mm 胶片，颗粒细，色调干净",
            "构图": "玻璃反射、框中框、对称室内、静止中远景",
            "材质": "玻璃幕墙、金属、办公家具、雨、电梯、城市夜景",
            "情绪": "疏离、理性、城市中产的疲惫、温和的绝望"
        },
        "layers": {
            "style": "Edward Yang Yi Yi, glass reflection composition, cold fluorescent urban interiors, static symmetrical staging, Taipei middle class",
            "lighting": "fluorescent and cool daylight, even but cold, shallow hard shadows, no warm sources",
            "color": "cool white, grey-blue, glass green, beige grey; low saturation with a distinct green cast",
            "composition": "shooting through glass so reflections layer figures onto the city, frame within frame, symmetrical interiors, static medium-long",
            "medium": "35mm film, fine grain, clean tonality",
            "mood": "alienated, rational, middle-class exhaustion, gentle despair",
            "camera": "locked-off medium-long, slow pan, shooting through glass and windows"
        },
        "negative": "warm cozy light, handheld, saturated colors, close-up intimacy, natural golden hour, film grain heavy",
        "palette": [
            [
                "#C4CCD0",
                "冷白"
            ],
            [
                "#5A6B78",
                "灰蓝"
            ],
            [
                "#7A9A8C",
                "玻璃绿"
            ],
            [
                "#A8A79E",
                "米灰"
            ],
            [
                "#1E2A32",
                "夜蓝黑"
            ],
            [
                "#D8DCDD",
                "荧光白"
            ]
        ],
        "video": {
            "运动": "玻璃上雨痕、电梯升降、人物在反射里移动、城市灯光闪烁",
            "运镜": "固定、极慢横移；隔着玻璃拍",
            "时长": "10 秒",
            "关键": "**要隔着玻璃拍出反射叠影**；直接拍人会丢掉这部片一半的语法"
        },
        "pitfalls": [
            "暖色与手持是反的",
            "不给玻璃反射就变成普通的都市家庭剧",
            "写 natural light 会丢掉荧光的冷"
        ],
        "see_also": [
            "photorealism",
            "precisionism"
        ],
        "title_original": "Yi Yi",
        "filmgrab": "https://film-grab.com/2018/05/29/yi-yi-a-one-and-a-two/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/edward-yang/",
        "source": "curated"
    },
    {
        "slug": "zhang-yimou-hero",
        "director_zh": "张艺谋",
        "director_en": "Zhang Yimou",
        "director_slug": "zhang",
        "title_zh": "英雄",
        "title_en": "Hero",
        "year": 2002,
        "one_liner": "**每个叙事层一种主色**——红、蓝、白、绿各管一段，把色彩当叙事结构的极端案例。",
        "core": [
            "每个叙事层被一种主色统治：红、蓝、白、绿，颜色即「谁在讲这个故事」",
            "大面积单色块 + 极小面积对比色，画面像被平涂过",
            "人物服装与场景同色系，人几乎融进环境",
            "打斗段用慢镜、飘动的布料与落叶/水花，把动作拍成舞蹈"
        ],
        "visual": {
            "色彩": "每段单色统治（正红/靛蓝/纯白/翠绿），配极小面积对比点缀",
            "光影": "硬质方向光与逆光，人物常成剪影；色彩不靠光而靠物料",
            "笔触": "（电影媒介）35mm 胶片，色彩极浓，颗粒可见",
            "构图": "对称、正面、大面积色块；人物在画面中被色块包围",
            "材质": "丝绸、纱、竹、水、落叶、雪、沙漠、朱漆",
            "情绪": "壮阔、凄美、浪漫化的牺牲"
        },
        "layers": {
            "style": "Zhang Yimou Hero, one dominant hue per narrative layer, wuxia colour-coding, flowing fabric and slow motion combat",
            "lighting": "hard directional and backlight making silhouettes; colour carried by materials and set rather than by light",
            "color": "each segment ruled by a single hue - vermilion, indigo, pure white, jade green - with tiny complementary accents",
            "composition": "symmetry, frontal staging, large flat colour blocks, figures embedded in the colour field",
            "medium": "35mm film, extremely saturated colour, visible grain",
            "mood": "vast, elegiac, romanticised sacrifice",
            "camera": "slow motion, sweeping lateral movement, static symmetry, floating camera"
        },
        "negative": "multi-hue palettes, naturalistic documentary light, handheld, desaturated tones, modern digital look",
        "palette": [
            [
                "#B01F1F",
                "正红"
            ],
            [
                "#1F3A6E",
                "靛蓝"
            ],
            [
                "#F2F2F0",
                "纯白"
            ],
            [
                "#2E7A4A",
                "翠绿"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#141210",
                "暗部黑"
            ]
        ],
        "video": {
            "运动": "布料飘动、落叶/水花飞散、慢镜中的动作、纱帘被风掀起",
            "运镜": "缓慢横移、环绕、慢镜推进",
            "时长": "10 秒",
            "关键": "**一个镜头一种主色**；多色混用会把「色彩即叙事层」这个结构抹掉"
        },
        "pitfalls": [
            "这是刻意的单色结构，不是通用调色板 —— 一张卡里不要混四色",
            "写 wuxia 会得到普通武侠 → 要写 one dominant hue, colour-coded narrative",
            "自然光与低饱和是反的"
        ],
        "see_also": [
            "pop-art",
            "ukiyo-e"
        ],
        "title_original": "Hero",
        "filmgrab": "https://film-grab.com/2013/12/19/hero/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/zhang-yimou/",
        "source": "curated"
    },
    {
        "slug": "zhang-yimou-raise-the-red-lantern",
        "director_zh": "张艺谋",
        "director_en": "Zhang Yimou",
        "director_slug": "zhang",
        "title_zh": "大红灯笼高高挂",
        "title_en": "Raise the Red Lantern",
        "year": 1991,
        "one_liner": "**红灯笼与灰墙的四合院对称**——构图本身就是制度的形状，人被院子框死。",
        "core": [
            "四合院的严格对称与纵深透视：院墙把人框在几何里",
            "大红灯笼是画面里唯一的高饱和色，其余是灰砖、青瓦、雪",
            "大量俯视与正面构图，把庭院拍成平面图案",
            "人物服装素净，与环境同调，只有灯笼红得刺眼"
        ],
        "visual": {
            "色彩": "正红（灯笼）、灰砖、青瓦、雪白、暗褐；低饱和环境 + 极高饱和的单一红",
            "光影": "阴天散射与室内侧光；柔和但有明确方向，影子不长",
            "笔触": "（电影媒介）35mm 胶片，色彩浓烈，颗粒可见",
            "构图": "严格对称、正面纵深、俯视平面化；院墙框中框",
            "材质": "砖、瓦、木、纸灯笼、雪、棉布、石板",
            "情绪": "压抑、规训、女性被制度吞没"
        },
        "layers": {
            "style": "Zhang Yimou Raise the Red Lantern, symmetrical courtyard geometry, single saturated red against grey brick, overhead flattening",
            "lighting": "overcast diffuse with directional interior side light, soft but defined, short shadows, no warmth in the environment",
            "color": "vermilion lanterns against grey brick, slate tile, snow white and dark brown; desaturated environment with one hyper-saturated hue",
            "composition": "strict symmetry, frontal deep staging, overhead shots flattening the courtyard into pattern, frame within frame by walls",
            "medium": "35mm film, rich colour, visible grain",
            "mood": "oppressive, disciplinary, women swallowed by the system",
            "camera": "static frontal wide, slow overhead descent, symmetrical symmetry, no handheld"
        },
        "negative": "handheld, multi-colour palette, warm cozy interior, modern architecture, desaturated dull grade",
        "palette": [
            [
                "#B0241F",
                "灯笼正红"
            ],
            [
                "#6E6A63",
                "灰砖"
            ],
            [
                "#3E4A52",
                "青瓦"
            ],
            [
                "#F2F2F0",
                "雪白"
            ],
            [
                "#4A3A2A",
                "暗褐"
            ],
            [
                "#C4BCA8",
                "棉布米"
            ]
        ],
        "video": {
            "运动": "灯笼在风里轻晃、雪落、人物缓慢穿过庭院",
            "运镜": "固定对称、俯视缓慢下降、正面纵深推进",
            "时长": "10 秒",
            "关键": "**对称庭院 + 唯一的高饱和红**；加第二个饱和色就毁掉了「一点红」的结构"
        },
        "pitfalls": [
            "加别的饱和色会稀释红灯笼的唯一性",
            "手持与俯视扁平化的语法冲突",
            "写 warm 会丢掉砖墙的冷灰"
        ],
        "see_also": [
            "precisionism",
            "baroque"
        ],
        "title_original": "Raise the Red Lantern",
        "filmgrab": "https://film-grab.com/2013/08/05/raise-the-red-lantern/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/zhang-yimou/",
        "source": "curated"
    },
    {
        "slug": "miike-audition",
        "director_zh": "三池崇史",
        "director_en": "Takashi Miike",
        "director_slug": "miike",
        "title_zh": "切肤之爱",
        "title_en": "Audition",
        "year": 1999,
        "one_liner": "**前段的电视质感与后段的过曝白**——用画质切换做恐怖转场，温和与残酷之间没有过渡。",
        "core": [
            "前段刻意用平淡的电视电影质感：均匀光、干净构图，像家庭剧",
            "后段切换为过曝白 + 高对比硬光，画面变脏变刺",
            "两段的画质反差本身就是恐怖装置，不靠特效",
            "后半段的空房间与单一光源（台灯）构成极简的舞台"
        ],
        "visual": {
            "色彩": "前段：米白、浅褐、柔和米调；后段：过曝白、暗红、脏褐",
            "光影": "前段均匀柔和（电视感）；后段单个硬光源 + 大面积深黑",
            "笔触": "（电影媒介）35mm 胶片；前段干净，后段有强对比与过曝颗粒",
            "构图": "前段规整的中景与对称；后段极简空房间、正面对称、单一焦点",
            "材质": "榻榻米、纸门、木、麻绳、金属针、白墙、血迹",
            "情绪": "从温和到残酷的断裂、被甜美掩盖的暴力"
        },
        "layers": {
            "style": "Takashi Miike Audition, two-register image quality, bland TV-like first half, blown-out hard-light second half, minimal stage",
            "lighting": "first half: even soft television lighting; second half: single hard source with blown white highlights and large dead blacks",
            "color": "first half: off-white, pale brown, soft beige; second half: overexposed white, dark red, dirty brown",
            "composition": "first half: tidy medium shots and symmetry; second half: bare room, frontal symmetry, single focal point",
            "medium": "35mm film; clean early, harsh contrast and blown grain late",
            "mood": "rupture from gentle to cruel, violence under sweetness",
            "camera": "static medium, slow zoom, locked-off frontal in the final act"
        },
        "negative": "uniform grade across the whole film, soft even lighting, handheld action, cgi gore, warm cozy light",
        "palette": [
            [
                "#E8E0D0",
                "前段米白"
            ],
            [
                "#A89478",
                "浅褐"
            ],
            [
                "#F2F2F0",
                "过曝白"
            ],
            [
                "#6B1F1A",
                "暗红"
            ],
            [
                "#3E3A34",
                "脏褐"
            ],
            [
                "#121212",
                "深黑"
            ]
        ],
        "video": {
            "运动": "极少的动作：手指轻动、水滴、针具的反光、人物静止",
            "运镜": "固定机位、极慢变焦",
            "时长": "10 秒",
            "关键": "**画质两段要能一眼分辨**（温和均匀 vs 过曝硬光）；统一质感就丢掉了它的恐怖装置"
        },
        "pitfalls": [
            "全片统一调色是反的：它的结构就是两段质感对撞",
            "写 gore / splatter 会得到血腥特效片",
            "柔和均匀的光是第一段的特征，第二段必须硬"
        ],
        "see_also": [
            "expressionism",
            "photorealism"
        ],
        "title_original": "Audition",
        "filmgrab": "https://film-grab.com/2019/07/09/audition/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/takashi-miike/",
        "source": "curated"
    },
    {
        "slug": "shinkai-your-name",
        "director_zh": "新海诚",
        "director_en": "Makoto Shinkai",
        "director_slug": "shinkai",
        "title_zh": "你的名字",
        "title_en": "Your Name",
        "year": 2016,
        "one_liner": "**逆光与镜头的黄昏**——把黄昏拍成动画里的独立色温层，光晕是画面的主角。",
        "core": [
            "逆光与镜头光晕被推到极致：光源常在画面里，光斑与光晕覆盖构图",
            "黄昏被做成独立的色温层（橙紫渐变 + 高光溢出），与白天/夜晚并列第三套色板",
            "背景是照片级的写实绘景，细节密度极高；人物线条简洁",
            "天空占画面大面积，云层与光斑是构图主体"
        ],
        "visual": {
            "色彩": "黄昏：橙、紫、金；白天：青蓝、白、绿；夜：深蓝、霓虹。三套色板随叙事切换",
            "光影": "强逆光与镜头光晕；光源常入画，人物成剪影；高光刻意溢出",
            "笔触": "（动画媒介）数字 2D，背景照片级细节，人物线条干净；光晕与光斑是合成出来的",
            "构图": "大面积天空与云、低角度、人物在画面下缘或侧边；光斑进入画框",
            "材质": "云、天空、雨、玻璃、电线、校舍、绳结、水",
            "情绪": "青春、怅惘、时间与距离、被光浸泡的怀念"
        },
        "layers": {
            "style": "Makoto Shinkai Your Name, photoreal painted backgrounds, extreme backlight and lens flare, dusk as a separate colour register, 2010s Japanese digital animation",
            "lighting": "strong backlight with the light source inside frame, heavy lens flare and bloom, silhouetted figures, deliberately blown highlights",
            "color": "three registers: dusk orange-purple-gold, daytime cyan-blue-white-green, night deep blue with neon; each carries a time of day",
            "composition": "large sky and cloud masses, low angle, figures low or to the side, lens flare entering the frame, dense background detail",
            "medium": "digital 2D animation, photoreal painted plates, clean character lines, composed flare and bloom",
            "mood": "youthful, wistful, time and distance, nostalgia soaked in light",
            "camera": "low angle toward sky, slow pan across clouds, static with flare drift, wide establishing"
        },
        "negative": "flat even lighting, no flare, sparse background, cel flat colour, muted palette, 3d cgi",
        "palette": [
            [
                "#E08A2B",
                "黄昏橙"
            ],
            [
                "#6B4A8C",
                "黄昏紫"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#3E7A9A",
                "白天青蓝"
            ],
            [
                "#1E2A4A",
                "夜深蓝"
            ],
            [
                "#F2F2F0",
                "高光白"
            ]
        ],
        "video": {
            "运动": "云层流动、光斑在画面里漂移、雨落、光影掠过人物",
            "运镜": "低角度缓慢横移、拉远露出天空",
            "时长": "10 秒",
            "关键": "**光源要进画面 + 光斑要覆盖构图**；把光藏起来就变成普通动画"
        },
        "pitfalls": [
            "写 anime 会得到平涂赛璐珞 → 这部片的背景是**照片级细节**",
            "不给光斑与逆光就丢掉了签名",
            "灰调低饱和是反的"
        ],
        "see_also": [
            "impressionism",
            "romanticism"
        ],
        "title_original": "Your Name",
        "filmgrab": "https://film-grab.com/2026/07/13/your-name/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/makoto-shinkai/",
        "source": "curated"
    },
]
