# -*- coding: utf-8 -*-
"""
fv_new_1.py —— 「完整片从 14 扩到 100」的第一批七层数据（8 部）。

## 为什么分批、为什么先不与 fv_data 合并

七层是**人写的分析**，不依赖网络；但 `filmgrab` URL 必须解析得到
（读导演分类页），不能手写 —— 实测手写 10 个里 8 个 404。
下载剧照更依赖网络。

所以流程拆成三步，数据先落在这些 `fv_new_*.py` 里：

    1. 写七层（本文件，**离线可做**）
    2. fv_resolve.py 解析出真实 URL → 注入
    3. fv_fetch.py 抓班底 + 剧照 → fv_build.py 出卡

跑 `fv_merge.py` 校验全部字段齐全后才合并进 `fv_data.FILMS` ——
半成品不混进主数据，否则电影卡会生成出没有画廊页链接的空壳。

## 字段与 fv_data.FILMS 完全一致

`filmgrab` / `crew` / `filmgrab_director` 留空，由第 2、3 步填。
`source` 一律 `curated`（七层是手写解读，不是从有限信息推断）。
"""

BATCH = [
    {
        "slug": "kon-paprika",
        "director_zh": "今敏",
        "director_en": "Satoshi Kon",
        "director_slug": "satoshi-kon",
        "title_zh": "红辣椒",
        "title_en": "Paprika",
        "title_original": "パプリカ",
        "year": 2006,
        "filmgrab": "https://film-grab.com/2021/01/11/paprika/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/satoshi-kon/",
        "one_liner": "**把梦做成游行**——物体、角色与场景在同一个镜头里不停置换，剪辑就是视觉奇观本身。",
        "core": [
            "场景无缝置换：前一个镜头的物件变成下一个镜头的场景，中间不切",
            "游行队伍是全片色彩的爆发点：家电、招财猫、鸟居、玩偶挤在同一条街上",
            "饱和撞色但**分区分布**，每个梦一个主色系，靠色彩区分叙事层",
            "现实段用低饱和冷色、平光，梦段用高饱和与强烈方向光"
        ],
        "visual": {
            "色彩": "梦段：正红、品红、橙黄、青绿大面积撞色；现实段：灰蓝、米白、低饱和。两套色板切换即叙事切换",
            "光影": "赛璐珞平光；梦段用大块单色光（舞台灯般的品红与青），现实段用日光灯的平淡白",
            "笔触": "（动画媒介）手绘赛璐珞，硬边高光，阴影分层清楚；数字合成段落密度远高于普通 TV 动画",
            "构图": "极端视角切换与广角变形；游行用横向长卷式铺陈，现实用规整的室内透视",
            "材质": "反光塑料、玩偶织物、纸、镜面、玻璃；质感靠高光位置区分",
            "情绪": "癫狂、欢愉里带恐惧、身份溶解的眩晕"
        },
        "layers": {
            "style": "hand-drawn cel animation, Satoshi Kon dream logic, saturated parade palette, seamless scene transformation, 2000s Japanese feature animation",
            "lighting": "flat cel lighting with hard-edged shadow shapes; dream sequences use large single-color light blocks (magenta, cyan, orange) like stage lighting; reality uses flat neutral fluorescent white",
            "color": "dream: saturated vermilion, magenta, orange-yellow, cyan clashing in blocks; reality: grey-blue, off-white, low saturation; the switch between the two palettes IS the storytelling device",
            "composition": "extreme angle changes and wide-angle distortion; parades staged as horizontal scroll-like spreads; reality staged in tidy interior perspective",
            "medium": "hand-painted cel animation, hard-edged highlights, layered shading, dense digital compositing",
            "mood": "manic, joyful with dread, identity dissolving, vertiginous",
            "camera": "sudden overhead and worm's-eye, wide-angle close-ups, match-cut driven camera movement"
        },
        "negative": "photorealistic 3d render, soft airbrush shading, flat even lighting, pastel palette, desaturated grey, static wide establishing shot",
        "palette": [
            [
                "#C4203C",
                "游行正红"
            ],
            [
                "#D6338F",
                "品红"
            ],
            [
                "#E08A2B",
                "橙黄"
            ],
            [
                "#2B8C8C",
                "青绿"
            ],
            [
                "#3A4550",
                "现实灰蓝"
            ],
            [
                "#EDE6DA",
                "日光灯白"
            ]
        ],
        "video": {
            "运动": "游行队伍向前涌、玩偶与家电一起晃动、人物在场景间被吞没",
            "运镜": "大幅度的快速横移与俯冲；可用无缝场景置换的推镜",
            "时长": "10 秒",
            "关键": "**必须有「置换」**——一个物体的形状变成另一个场景的轮廓；只写 colourful 会得到普通的彩色动画"
        },
        "pitfalls": [
            "写 anime 会得到现代数字动画 → 要写 hand-drawn cel / 2000s Japanese feature animation",
            "3D 渲染与柔和喷枪阴影是这部片的反面，必须进负向词",
            "不给「两套色板」规则，梦与现实会糊成同一个调子，叙事层就没了",
            "游行段落的密度是刻意的：写 minimal 会把最有辨识度的场面杀掉"
        ],
        "see_also": [
            "anime-cel",
            "surrealism",
            "pop-art"
        ],
        "source": "curated"
    },
    {
        "slug": "kon-millennium-actress",
        "director_zh": "今敏",
        "director_en": "Satoshi Kon",
        "director_slug": "satoshi-kon",
        "title_zh": "千年女优",
        "title_en": "Millennium Actress",
        "title_original": "千年女優",
        "year": 2001,
        "filmgrab": "https://film-grab.com/2021/01/25/millenium-actress/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/satoshi-kon/",
        "one_liner": "**用色彩跳时间**——同一个奔跑动作穿过江户、战国、昭和与未来，每个时代一套色板。",
        "core": [
            "一个动作跨时代的连续转场：跑、回头、开门，背景换掉而人物不变",
            "每个时代一套色板与质感：和服的朱与金、战后的灰、现代的冷白",
            "把「回忆」拍成可进入的空间，人物在记忆布景里穿行",
            "光线用戏剧性的舞台感（追光、雪、火）撑住情绪，而非写实光源"
        ],
        "visual": {
            "色彩": "朱红、金、靛蓝、雪白按时代分区；同一画面里最多两个主色，靠色相区分时间层",
            "光影": "舞台式打光：追光、火光、雪面反光；暗部平涂不追求层次，高光集中",
            "笔触": "（动画媒介）手绘赛璐珞，线条比《未麻的部屋》更柔和；背景是水彩感的绘景",
            "构图": "人物居中或偏侧，背景做大幅时代置换；奔跑用横向长卷式构图",
            "材质": "和服织物、木构建筑、雪、纸门、胶片噪点",
            "情绪": "怀旧、执着、跨越时间的怅惘"
        },
        "layers": {
            "style": "hand-drawn cel animation, Satoshi Kon time-travel montage, watercolour painted backgrounds, era-coded palettes, 2000s Japanese feature animation",
            "lighting": "theatrical stagelight: follow spot, firelight, snow bounce; flat painted shadows, concentrated highlights, no naturalistic falloff",
            "color": "vermilion and gold for the Edo/kimono eras, grey for postwar, cool white for the present; at most two dominant hues per frame, hue codes the era",
            "composition": "subject centred or off-centre against a fully replaced background; running staged as a horizontal scroll; era shifts inside one shot",
            "medium": "hand-painted cel animation, soft linework, watercolour-painted backgrounds, film grain overlay",
            "mood": "nostalgic, obsessive, wistful across time",
            "camera": "lateral tracking with continuous background change, long dissolves replaced by match cuts, static medium shots"
        },
        "negative": "photorealistic 3d, soft airbrush, desaturated modern anime, static interior dialogue scene, pastel uniform palette",
        "palette": [
            [
                "#B03026",
                "和服朱红"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#2E4A6B",
                "靛蓝"
            ],
            [
                "#E8E4DC",
                "雪白"
            ],
            [
                "#6E6A63",
                "战后灰"
            ],
            [
                "#8FA3B8",
                "现代冷白"
            ]
        ],
        "video": {
            "运动": "奔跑、回头、开门；背景在运动中整体置换",
            "运镜": "横向跟拍 + 背景连续置换；可用极慢推近",
            "时长": "10 秒",
            "关键": "**必须让背景换掉而主体保持** —— 那是这部片的全部手法；只写「一个人跑」就退化成普通动画"
        },
        "pitfalls": [
            "不写 era-coded palette，时间层会糊在一起，转场失去意义",
            "写 realistic lighting 会杀死舞台感的追光",
            "背景要「绘景感」（水彩），写 photoreal background 会变成数字绘景产品"
        ],
        "see_also": [
            "anime-cel",
            "ukiyo-e",
            "impressionism"
        ],
        "source": "curated"
    },
    {
        "slug": "anime-akira",
        "director_zh": "大友克洋",
        "director_en": "Katsuhiro Otomo",
        "director_slug": "katsuhiro-otomo",
        "title_zh": "阿基拉",
        "title_en": "Akira",
        "title_original": "アキラ",
        "year": 1988,
        "filmgrab": "https://film-grab.com/2020/03/03/akira/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/katsuhiro-otomo/",
        "one_liner": "**霓虹红与工业灰**——新东京的夜被招牌和工地灯照亮，赛璐珞时代密度最高的城市。",
        "core": [
            "红色是城市的主色：招牌、机车尾灯、爆炸、血，全部同一族红",
            "夜景不靠天空照明，靠密集的人造光源；光是点状的、数量极多",
            "工业灰与混凝土构成白天，红与黑构成夜晚，两套色板交替",
            "高密度作画：一个镜头里同时有几十个运动元素（人群、车、招牌）"
        ],
        "visual": {
            "色彩": "正红、橙红、工业灰、沥青黑、霓虹青作点缀；红色面积最大且最饱和",
            "光影": "夜景为多光源点状照明（招牌、车灯、施工灯），不设主光；白天是平光的阴天灰",
            "笔触": "（动画媒介）赛璐珞手绘，线条极硬且细，机械细节刻意密集",
            "构图": "城市全景与贴地视角交替；广角拉伸街道纵深，爆炸段落用对称构图",
            "材质": "混凝土、金属、玻璃幕墙、霓虹灯管、蒸汽、碎石",
            "情绪": "压迫、躁动、末世感、少年的失控"
        },
        "layers": {
            "style": "1980s Japanese cel animation, Katsuhiro Otomo, cyberpunk city, extremely dense hand-drawn detail, 2.35:1 widescreen",
            "lighting": "night lit by many small practical sources (signage, headlights, construction lamps) with no single key; day is flat overcast grey; explosions as the only large light source",
            "color": "dominant vermilion and orange-red against industrial grey and asphalt black, neon cyan as accent; the red is the highest-chroma element in frame",
            "composition": "city panoramas alternating with ground-level shots; wide-angle stretched street depth; symmetrical staging for the destruction set pieces",
            "medium": "hand-painted cel animation, very hard thin linework, dense mechanical detail, optical compositing",
            "mood": "oppressive, restless, apocalyptic, adolescent loss of control",
            "camera": "low ground-level wide angle, fast lateral tracking, slow crane over the city"
        },
        "negative": "modern digital anime, soft shading, clean minimal composition, pastel palette, sparse background, 3d cgi",
        "palette": [
            [
                "#B01F1F",
                "正红"
            ],
            [
                "#D95B1E",
                "橙红"
            ],
            [
                "#4A4E52",
                "工业灰"
            ],
            [
                "#121316",
                "沥青黑"
            ],
            [
                "#2E8C8C",
                "霓虹青"
            ],
            [
                "#C9C4BA",
                "混凝土白"
            ]
        ],
        "video": {
            "运动": "车流、招牌闪烁、蒸汽喷出、爆炸冲击波推动碎石",
            "运镜": "贴地广角横移、快速摇镜、缓慢的城市俯瞰",
            "时长": "10 秒",
            "关键": "**红光面积要最大**且要有大量点状光源；只写 cyberpunk 会得到通用的蓝色未来都市"
        },
        "pitfalls": [
            "cyberpunk 默认会被渲染成蓝紫 → 必须写 red-dominant, vermilion",
            "写 modern anime / clean 会丢掉 80 年代赛璐珞的线路与噪点",
            "背景密度是这部片的签名，写 minimal 就把新东京拆了"
        ],
        "see_also": [
            "cyberpunk",
            "anime-cel",
            "retro-anime"
        ],
        "source": "curated"
    },
    {
        "slug": "anime-ghost-in-the-shell",
        "director_zh": "押井守",
        "director_en": "Mamoru Oshii",
        "director_slug": "mamoru-oshii",
        "title_zh": "攻壳机动队",
        "title_en": "Ghost in the Shell",
        "title_original": "攻殻機動隊",
        "year": 1995,
        "filmgrab": "https://film-grab.com/2022/02/10/ghost-in-the-shell-1995/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/mamoru-oshii/",
        "one_liner": "**把赛博朋克拍成安静的城市观察**——香港式招牌与冷绿水面，人物沉默地漂在运河上。",
        "core": [
            "城市取材自香港：密集招牌、狭窄街道、临水而建的老楼",
            "色温以冷绿与青灰为主，暖色只出现在招牌与室内灯光上，面积小",
            "大量静止镜头与长镜；动作段落的安静与爆发对比极强",
            "水面反光与玻璃反射是常用介质：把城市折进画面里"
        ],
        "visual": {
            "色彩": "青绿、灰蓝、暗绿为主；霓虹招牌的橙与红作小面积点缀",
            "光影": "阴天散射光 + 人工光源；水面与玻璃的反射承担一半照明，暗部偏绿",
            "笔触": "（动画媒介）赛璐珞手绘 + 早期数字合成，线条干净，阴影分层明确",
            "构图": "城市纵深与水面倒影并置；人物常被建筑压在一角，留大量环境",
            "材质": "水、玻璃、混凝土、招牌灯管、纸伞、电缆",
            "情绪": "冷静、忧郁、身份悬置、城市的疏离感"
        },
        "layers": {
            "style": "1990s Japanese cel animation, Mamoru Oshii, Hong Kong-inspired cyberpunk city, quiet observational staging, optical compositing",
            "lighting": "overcast diffuse daylight mixed with practical signage; reflections on water and glass provide half the illumination; green-tinted shadows, no dramatic key light",
            "color": "cyan-green, grey-blue and dark green dominate; orange and red neon as small accents only; cool overall with low saturation",
            "composition": "deep city canyons beside water reflections; subject pushed to one corner with large areas of environment; long static holds",
            "medium": "hand-painted cel animation with early digital compositing, clean linework, clearly layered shading",
            "mood": "calm, melancholic, suspended identity, urban alienation",
            "camera": "long static holds, slow lateral drift, occasional sudden close-up"
        },
        "negative": "bright saturated neon, fast cutting, handheld, warm cozy interior, modern digital anime, lens flare",
        "palette": [
            [
                "#2B5E5A",
                "青绿"
            ],
            [
                "#3C5566",
                "灰蓝"
            ],
            [
                "#1E3A32",
                "暗绿"
            ],
            [
                "#D97A2B",
                "招牌橙"
            ],
            [
                "#B03030",
                "招牌红"
            ],
            [
                "#C4CFC9",
                "阴天白"
            ]
        ],
        "video": {
            "运动": "水面波纹、雨、招牌闪烁、电缆与纸伞轻晃",
            "运镜": "长时间静止，偶尔极慢横移；可用缓慢推近到面部",
            "时长": "10 秒",
            "关键": "**冷绿 + 水面反射 + 静止机位**三件套；写 neon cyberpunk 会得到热闹的蓝紫都市，那是反的"
        },
        "pitfalls": [
            "cyberpunk 会被默认渲染成高饱和霓虹 → 必须写 cool cyan-green, low saturation, small neon accents",
            "快速剪辑与这部片的静止语法相反，要进负向词",
            "水面/玻璃反射是它的主要介质，不写 reflection 会丢掉一半气质"
        ],
        "see_also": [
            "cyberpunk",
            "anime-cel",
            "minimalism-art"
        ],
        "source": "curated"
    },
    {
        "slug": "miyazaki-spirited-away",
        "director_zh": "宫崎骏",
        "director_en": "Hayao Miyazaki",
        "director_slug": "hayao-miyazaki",
        "title_zh": "千与千寻",
        "title_en": "Spirited Away",
        "title_original": "千と千尋の神隠し",
        "year": 2001,
        "filmgrab": "https://film-grab.com/2020/04/27/spirited-away/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/hayao-miyazaki/",
        "one_liner": "**灯笼的暖光与深绿植被**——手绘背景的密度本身即风格，妖怪世界有明确的昼夜与湿度。",
        "core": [
            "暖色人工光（灯笼、油屋窗火）与冷绿自然（森林、水）对峙",
            "手绘背景密度极高：每个画面都有可读的纹理与层次",
            "夜间段落用大面积深蓝绿 + 点状暖光；白天用高调绿与天空蓝",
            "建筑是木构的、有湿度的；材质反光弱、以哑光为主"
        ],
        "visual": {
            "色彩": "深绿、青蓝、朱红（灯笼与鸟居）、暖金（窗户）；夜色偏蓝绿，白昼偏黄绿",
            "光影": "夜间为多点暖光源（灯笼）+ 大面积冷暗部；白天为高调日光，阴影是冷色",
            "笔触": "（动画媒介）手绘赛璐珞角色 + 水粉/水彩绘景；背景笔触可见",
            "构图": "水平铺陈的建筑全景与中景人物；水的横向流动常占画面下三分之一",
            "材质": "木、纸障子、灯笼纸、苔藓、蕨类、水、蒸汽",
            "情绪": "神秘、温暖里带不安、童年视角的惊奇"
        },
        "layers": {
            "style": "Studio Ghibli hand-drawn animation, Hayao Miyazaki, dense watercolour painted backgrounds, Japanese yokai world, cel characters on painted plates",
            "lighting": "night: many warm paper-lantern sources against large cool dark areas; day: high-key sunlight with cool-tinted shadows; strong indoor-outdoor temperature contrast",
            "color": "deep green, teal, vermilion lanterns and torii, warm gold window light; night leans blue-green, day leans yellow-green",
            "composition": "horizontally spread architectural wide shots with mid-scale figures; water often occupies the lower third; layered foreground foliage",
            "medium": "hand-painted cel animation over watercolour/gouache backgrounds, visible background brushwork",
            "mood": "mysterious, warmly unsettling, childlike wonder",
            "camera": "gentle lateral pans, static wides, occasional slow push into a doorway"
        },
        "negative": "3d cgi, photoreal, flat digital gradient background, sparse composition, harsh neon, modern anime sheen",
        "palette": [
            [
                "#20462E",
                "深绿"
            ],
            [
                "#2E6B6B",
                "青蓝"
            ],
            [
                "#B03026",
                "灯笼朱红"
            ],
            [
                "#C9A227",
                "窗火暖金"
            ],
            [
                "#1B2A3A",
                "夜蓝绿"
            ],
            [
                "#8FA34A",
                "黄绿日光"
            ]
        ],
        "video": {
            "运动": "灯笼轻晃、水流动、蒸汽升起、草木在风里晃",
            "运镜": "缓慢横移与静止全景；可用极慢推近到门内",
            "时长": "10 秒",
            "关键": "**背景密度 + 暖灯笼对冷暗部**；写 anime 会得到干净的数字动画，那是反的"
        },
        "pitfalls": [
            "写 anime / 现代动画会丢掉手绘绘景的笔触密度",
            "3D 与 photoreal 必须进负向词",
            "只写 warm 会得到统一暖调；这部片的关键是暖光与冷暗部的对峙"
        ],
        "see_also": [
            "ukiyo-e",
            "zen-art",
            "romanticism"
        ],
        "source": "curated"
    },
    {
        "slug": "takahata-kaguya",
        "director_zh": "高畑勋",
        "director_en": "Isao Takahata",
        "director_slug": "isao-takahata",
        "title_zh": "辉夜姬物语",
        "title_en": "The Tale of Princess Kaguya",
        "title_original": "かぐや姫の物語",
        "year": 2013,
        "filmgrab": "https://film-grab.com/2026/08/13/the-tale-of-princess-kaguya/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/isao-takahata/",
        "one_liner": "**留白的水墨动画**——炭笔线条与淡彩在纸上呼吸，动作被画成笔势而不是形。",
        "core": [
            "线条是炭笔/毛笔的笔势，故意保留抖动与不闭合",
            "大面积纸白留白，颜色以淡彩薄涂，不用饱和填充",
            "背景是水彩与素描的混合，可见纸纹",
            "情绪强烈时线条变粗变乱、颜色溢出——用笔触当表演"
        ],
        "visual": {
            "色彩": "淡墨、赭石、浅绿、樱粉、纸白；整体低饱和且薄，颜色常不上满",
            "光影": "几乎没有方向性光源；明暗靠线的疏密与薄涂层次表达",
            "笔触": "（动画媒介）炭笔与毛笔线条，保留手绘抖动与断笔；上色是水彩薄涂",
            "构图": "大量留白，主体常偏于一角；横幅式风景铺陈；镜头运动极少",
            "材质": "纸、炭、水墨、淡彩、竹、织物",
            "情绪": "质朴、天真、悲悯、时间流逝的怅惘"
        },
        "layers": {
            "style": "charcoal and ink line animation, watercolour wash on paper, Isao Takahata, extreme negative space, sketch-like unfinished linework",
            "lighting": "no directional light source; value built from line density and thin wash layers; high-key paper white dominates",
            "color": "dilute ink, ochre, pale green, cherry pink, paper white; low saturation, colour often does not fill the shape",
            "composition": "large negative space with subject pushed to a corner; horizontal landscape spreads; almost no camera movement",
            "medium": "charcoal and brush line on paper, watercolour wash, visible paper grain",
            "mood": "artless, innocent, compassionate, elegiac",
            "camera": "near-static, occasional slow lateral drift, long holds"
        },
        "negative": "cel animation, saturated flat fill, 3d cgi, clean vector line, photoreal texture, busy detailed background",
        "palette": [
            [
                "#3A3A38",
                "淡墨"
            ],
            [
                "#8A6A3C",
                "赭石"
            ],
            [
                "#9CAE8A",
                "浅绿"
            ],
            [
                "#E8C4C4",
                "樱粉"
            ],
            [
                "#F5F2EA",
                "纸白"
            ],
            [
                "#6B7A8C",
                "远山灰蓝"
            ]
        ],
        "video": {
            "运动": "极小的动作：走动、风吹草、花瓣落；笔触本身在变",
            "运镜": "几乎静止；可极慢横移",
            "时长": "10 秒",
            "关键": "**留白 + 不闭合的炭笔线 + 薄涂**；写 anime 会得到完整填充的赛璐珞，与这部片完全相反"
        },
        "pitfalls": [
            "任何「完整填充」的写法都会毁掉这部片 —— 要写 colour does not fill the shape / outline unclosed",
            "写 cel animation 或 vector line 是反的",
            "方向性光源与这部片的无光源语法冲突"
        ],
        "see_also": [
            "zen-art",
            "ukiyo-e",
            "minimalism-art"
        ],
        "source": "curated"
    },
    {
        "slug": "tarkovsky-solaris",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "飞向太空",
        "title_en": "Solaris",
        "title_original": "Солярис",
        "year": 1972,
        "filmgrab": "https://film-grab.com/2012/12/14/solaris-2/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/andrei-tarkovsky/",
        "one_liner": "**把科幻拍成水草与记忆**——空间站里长出水生植物，失重段落用极慢环绕代替特效。",
        "core": [
            "科幻外壳装的是记忆与愧疚：所谓「外星」其实是自己最不愿见的人",
            "失重段落靠极慢的环绕与漂浮的道具实现，不用快切制造动感",
            "色温两分：地球段是湿绿与琥珀，空间站是冷白与金属灰",
            "水面、雨、水草反复出现，把「流体」作为跨空间的连接物"
        ],
        "visual": {
            "色彩": "地球：湿绿、琥珀、锈褐；空间站：冷白、钢灰、暗绿。两套色温把「家」与「太空」分开",
            "光影": "地球段自然散射光与水下反光；空间站冷白均匀照明 + 单个暖点光源作情绪锚",
            "笔触": "（电影媒介）35mm 胶片，颗粒细；水下与失重段落有柔和的曝光呼吸",
            "构图": "缓慢环绕与纵深构图；人物常被设备或水草遮挡，画面里有第二层",
            "材质": "水、水草、金属舱壁、玻璃、湿混凝土、雨、旧家具",
            "情绪": "乡愁、愧疚、缓慢的绝望、几乎宗教的静"
        },
        "layers": {
            "style": "Tarkovsky science fiction, 35mm film, slow orbital camera, damp organic textures against cold machinery, poetic long take",
            "lighting": "Earth: soft diffused daylight with underwater bounce; station: even cold white ambient with a single warm practical as emotional anchor; no dramatic key light, shadows detailed",
            "color": "wet green and amber for Earth, cold white and steel grey with dark green for the station; low saturation, separation by temperature",
            "composition": "slow circular camera moves, deep staging, subject partially occluded by equipment or aquatic plants, off-centre figures",
            "medium": "35mm film, fine grain, soft edges, gentle exposure breathing in water and zero-gravity sequences",
            "mood": "nostalgic, guilty, slowly despairing, almost religious stillness",
            "camera": "very slow orbit and lateral drift, long unbroken takes, 40mm-ish wide, deep focus"
        },
        "negative": "fast cutting, cgi spectacle, saturated colors, lens flare, teal-and-orange grade, clean digital look, handheld shake",
        "palette": [
            [
                "#4E5B3C",
                "湿绿"
            ],
            [
                "#8A6A3C",
                "琥珀"
            ],
            [
                "#7A3B2E",
                "锈褐"
            ],
            [
                "#D8DCDD",
                "舱壁冷白"
            ],
            [
                "#5A6B78",
                "钢灰"
            ],
            [
                "#B8B0A0",
                "雾米"
            ]
        ],
        "video": {
            "运动": "水草摇动、水面波纹、失重物体缓慢漂浮、尘埃在光柱里移动",
            "运镜": "极慢的环绕与横移；避免快速运镜",
            "时长": "10–15 秒",
            "关键": "**流体必须是运动的唯一来源**（水、草、漂浮物），机位本身几乎不动；快切会立刻杀死它"
        },
        "pitfalls": [
            "写 sci-fi 会得到金属科幻 → 要写 damp organic, underwater plants, wet surfaces",
            "cgi 与高饱和是这部片的反面，负向词要明确",
            "空间站的冷白需要**一个暖点光源**作锚，否则变成无情绪的工业片"
        ],
        "see_also": [
            "realism",
            "surrealism"
        ],
        "source": "curated"
    },
    {
        "slug": "tarkovsky-nostalghia",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "乡愁",
        "title_en": "Nostalghia",
        "title_original": "Ностальгия",
        "year": 1983,
        "filmgrab": "https://film-grab.com/2025/04/21/nostalghia/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/andrei-tarkovsky/",
        "one_liner": "**举烛横穿水池**——一个动作撑满一个镜头的时间，宗教仪式被拍成物理过程。",
        "core": [
            "举着蜡烛走过温泉池：一次不剪断的行走，是全片的精神核心",
            "湿石墙、绿苔、蒸汽与雾构成几乎单色的环境",
            "构图被门槛、窗框、拱门切成多层，人物在不同层之间移动",
            "狗、水、火作为反复出现的元素，替代对白承担情绪"
        ],
        "visual": {
            "色彩": "湿灰绿、石褐、暗金；整体近乎单色，色彩只在火焰与水面上出现",
            "光影": "低照度自然光，蒸汽散射出体积光；烛光是唯一暖点光源",
            "笔触": "（电影媒介）35mm 胶片，柔焦，颗粒可见，暗部有细节",
            "构图": "拱门与窗框分层、纵深极深；人物很小，常背对镜头",
            "材质": "湿石、苔藓、铁、水、蒸汽、烛蜡、旧布",
            "情绪": "肃穆、孤独、仪式感、乡愁的钝痛"
        },
        "layers": {
            "style": "Tarkovsky late period, 35mm film, near-monochrome damp stone interiors, ritual long take, poetic slow cinema",
            "lighting": "very low key available light, volumetric shafts through steam, candle as the only warm source, deep shadows with retained detail",
            "color": "wet grey-green, stone brown, dark gold; almost monochrome with colour reserved for flame and water surfaces",
            "composition": "layered framing through arches, thresholds and windows, extreme depth, small distant figures often seen from behind",
            "medium": "35mm film, soft focus, visible grain, detailed shadows, aged tonality",
            "mood": "solemn, lonely, ritualistic, dull homesickness",
            "camera": "very slow forward dolly, long unbroken take, low eye-level, 35–50mm"
        },
        "negative": "fast cutting, saturated colors, handheld, lens flare, modern digital sharpness, cgi, bright even exposure",
        "palette": [
            [
                "#4A5A50",
                "湿灰绿"
            ],
            [
                "#6B5B45",
                "石褐"
            ],
            [
                "#A8843C",
                "暗金"
            ],
            [
                "#2A2E2C",
                "暗部墨绿"
            ],
            [
                "#C97B3C",
                "烛火橙"
            ],
            [
                "#B8B4A8",
                "蒸汽灰白"
            ]
        ],
        "video": {
            "运动": "烛火摇曳、蒸汽上升、水面微皱、人物极缓慢地行走",
            "运镜": "极慢推进或完全静止；一个镜头只做一件事",
            "时长": "15 秒以上（短了就变成普通阴天画面）",
            "关键": "**蜡烛必须是小面积暖光源、周围是大面积湿冷暗部**；它一旦变大就变成温馨场景"
        },
        "pitfalls": [
            "「举烛过水池」这个动作是识别特征，不写就会退化成普通欧洲文艺片",
            "写 warm 会跑偏；要写 candle against wet grey-green stone",
            "蒸汽与雾是体积光的载体，去掉就没有塔可夫斯基的纵深"
        ],
        "see_also": [
            "baroque",
            "realism"
        ],
        "source": "curated"
    },
    {
        "slug": "tarkovsky-ivan",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "伊万的童年",
        "title_en": "Ivan's Childhood",
        "title_original": "Иваново детство",
        "year": 1962,
        "filmgrab": "https://film-grab.com/2016/03/30/ivans-childhood/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/andrei-tarkovsky/",
        "one_liner": "**黑白里的水面与白桦**——梦境过曝发白，现实压成深灰，两个世界靠亮度分开。",
        "core": [
            "梦境是过曝的高调（井、白桦、雨、母亲），现实是深压暗的低调（战壕、废墟）",
            "水面与倒影反复出现：井、水桶、积水 —— 把记忆拍成会反光的介质",
            "竖直构图：白桦林、井壁、梯子，把画面切成纵向的条",
            "孩子的视点被抬高或压低，用非成人机位看战争"
        ],
        "visual": {
            "色彩": "黑白；梦境段接近纯白与浅灰，现实段为中深灰到黑，中间调窄",
            "光影": "梦境为过曝散射光（几乎无阴影）；现实为低照度硬光与深黑",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，高光有溢出",
            "构图": "垂直线条主导（白桦、井、梯）、纵深穿透；人物常置于画面下缘",
            "材质": "水、木、泥、铁、破布、雨、白桦树皮",
            "情绪": "童年被战争夺走的哀伤、梦与醒的落差"
        },
        "layers": {
            "style": "Tarkovsky debut, 35mm black and white, dream sequences overexposed, poetic war film, vertical composition",
            "lighting": "dreams: blown-out diffuse light with almost no shadow; reality: very low key hard light with deep black; two registers separated by exposure",
            "color": "black and white; near-white and pale grey for dreams, mid-to-deep grey and black for reality, narrow midtones",
            "composition": "vertical lines dominate (birches, well shaft, ladders), deep penetration, small figures low in frame, reflections on water",
            "medium": "35mm black-and-white film, pronounced grain, clipped highlights",
            "mood": "grief for a stolen childhood, the drop between dream and waking",
            "camera": "slow dolly through verticals, low and high non-adult angles, long take"
        },
        "negative": "saturated color, even lighting, modern clean look, handheld action, cgi explosions, bright midtones",
        "palette": [
            [
                "#0F0F0F",
                "战壕黑"
            ],
            [
                "#3A3A3A",
                "深灰"
            ],
            [
                "#6E6E6E",
                "中灰"
            ],
            [
                "#A8A8A8",
                "浅灰"
            ],
            [
                "#E8E8E8",
                "梦境过曝白"
            ],
            [
                "#555555",
                "泥水灰"
            ]
        ],
        "video": {
            "运动": "雨落、水面涟漪、白桦叶动、尘埃在光里飘",
            "运镜": "缓慢的纵向推进（穿过井/林）；可完全静止",
            "时长": "10 秒",
            "关键": "**梦境必须过曝、现实必须压暗**，两者的亮度差是这部片的结构；统一曝光就没了"
        },
        "pitfalls": [
            "写 black and white 不够 → 要写 blown-out highlights for dreams, crushed blacks for reality",
            "垂直构图（白桦/井）是它的语法，不写会变成横向的普通战争片",
            "水面倒影承担「记忆」的意义，缺了就只剩战壕"
        ],
        "see_also": [
            "realism",
            "expressionism"
        ],
        "source": "curated"
    },
    {
        "slug": "tarkovsky-andrei-rublev",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "安德烈·卢布廖夫",
        "title_en": "Andrei Rublev",
        "title_original": "Андрей Рублёв",
        "year": 1966,
        "filmgrab": "https://film-grab.com/2025/06/04/andrei-rublev/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/andrei-tarkovsky/",
        "one_liner": "**黑白里的泥、火与钟**——中世纪被拍成质感而非布景，最后一段突然转彩色壁画。",
        "core": [
            "全片黑白，唯独结尾的壁画段落转为彩色 —— 颜色是全片唯一一次「升华」",
            "泥、雨、火、烟是主要材质，衣服永远是脏的",
            "长镜横移穿过人群与工地，把时代拍成劳作现场",
            "门洞与矮墙把人物框住，空间总是拥挤而低矮"
        ],
        "visual": {
            "色彩": "黑白（大量中深灰），仅结尾壁画段为彩色的赭、朱、金、青",
            "光影": "低照度自然光；火与熔炉提供大面积暖光，室外是阴天散射",
            "笔触": "（电影媒介）35mm 黑白胶片，粗颗粒，高光有轻微溢出",
            "构图": "横移长镜穿行、门洞框景、低矮拥挤的空间；人群是主要构图元素",
            "材质": "泥、稻草、木、火、铁、粗布、烟、钟铜",
            "情绪": "沉重、苦难、粗粝里的信仰"
        },
        "layers": {
            "style": "Tarkovsky historical epic, 35mm black and white, medieval Russian textures, crowd-staged long take, final sequence in colour",
            "lighting": "low key available light; furnaces and fire as large warm sources, overcast diffuse outdoors, deep shadow indoors",
            "color": "black and white for most of the film with a wide grey range; the closing fresco sequence is the only colour: ochre, vermilion, gold, teal",
            "composition": "lateral tracking through crowds and construction sites, framing through doorways and walls, low cramped spaces",
            "medium": "35mm black-and-white film, coarse grain, slight highlight bloom",
            "mood": "heavy, suffering, faith inside coarseness",
            "camera": "long lateral tracking shots, low eye-level, wide framing of crowds"
        },
        "negative": "saturated color throughout, clean period costumes, symmetrical formal staging, modern digital look, handheld",
        "palette": [
            [
                "#121212",
                "熔炉黑"
            ],
            [
                "#3E3A34",
                "泥褐灰"
            ],
            [
                "#6E6A60",
                "湿泥灰"
            ],
            [
                "#B0722B",
                "火橙"
            ],
            [
                "#8C8C86",
                "阴天灰"
            ],
            [
                "#C9A227",
                "壁画金"
            ]
        ],
        "video": {
            "运动": "火焰、烟、雨、泥浆溅起、人群走动、钟摆晃动",
            "运镜": "缓慢横移穿过场景；镜头本身稳定不晃",
            "时长": "10–15 秒",
            "关键": "**材质要脏、光要靠火**；把画面拍干净就等于把中世纪换成了博物馆"
        },
        "pitfalls": [
            "写 medieval 会得到干净的骑士片 → 要写 mud, soot, wet wool, fire-lit",
            "结尾转彩色是结构性的，别把它当通用调色写进正向词",
            "拥挤与低矮是构图特征，写 spacious 就跑偏"
        ],
        "see_also": [
            "baroque",
            "realism"
        ],
        "source": "curated"
    },
]
