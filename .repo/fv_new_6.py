# -*- coding: utf-8 -*-
"""fv_new_6.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "wenders-paris-texas",
        "director_zh": "维姆·文德斯",
        "director_en": "Wim Wenders",
        "director_slug": "wenders",
        "title_zh": "德州巴黎",
        "title_en": "Paris, Texas",
        "year": 1984,
        "one_liner": "**霓虹与沙漠的撞色**——Robby Müller 把美国拍成荧光色，红帽与绿衬衫是唯一的暖点。",
        "core": [
            "沙漠段是土黄与天蓝的横向色带；城市段是霓虹的品红青绿",
            "Robby Müller 的高饱和撞色：红帽、绿衬衫、青绿霓虹共存于同一画面",
            "大量横向构图与静止的车窗视角，公路与天际线构成带状画面",
            "夜间段落用霓虹作主光，人物被品红与青绿切分"
        ],
        "visual": {
            "色彩": "沙漠土黄与天蓝；城市品红、青绿、橙红；高饱和撞色",
            "光影": "沙漠硬日光与长影；夜间霓虹作主光源，高饱和色打在人物脸上",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩浓烈，颗粒细",
            "构图": "横向带状构图、车窗视角、空旷公路与天际线；大量负空间",
            "材质": "沙、公路、霓虹灯管、玻璃、旧车、牛仔布、湿沥青",
            "情绪": "漂泊、孤独、寻找、被色彩照亮的虚无"
        },
        "layers": {
            "style": "Wim Wenders Paris, Texas, Robby Müller, saturated neon and desert colour, American road movie, wide horizontal compositions",
            "lighting": "hard desert sun with long shadows; neon as the key source at night with saturated magenta and cyan washing faces",
            "color": "desert earth yellow and sky blue; city magenta, cyan, orange-red; high saturation with deliberate clashes",
            "composition": "wide horizontal bands, framing through car windows, empty highways and skylines, generous negative space",
            "medium": "35mm colour film, rich saturation, fine grain",
            "mood": "drifting, lonely, searching, emptiness lit in colour",
            "camera": "static wide, slow lateral drive, long holds through windows"
        },
        "negative": "desaturated palette, handheld, cluttered foreground, European grey light, narrow framing",
        "palette": [
            [
                "#C9A227",
                "沙漠土黄"
            ],
            [
                "#3E7A9A",
                "天蓝"
            ],
            [
                "#C42B72",
                "霓虹品红"
            ],
            [
                "#2B8C8C",
                "霓虹青绿"
            ],
            [
                "#B03A2B",
                "红帽"
            ],
            [
                "#2E4A3A",
                "绿衬衫"
            ]
        ],
        "video": {
            "运动": "霓虹闪烁、车流、沙尘被风扬起、人物静止凝视",
            "运镜": "缓慢的车窗视角横移、固定宽景",
            "时长": "10 秒",
            "关键": "**霓虹要作主光并打在脸上**（不是背景装饰）；只当背景就失去了 Müller 的撞色"
        },
        "pitfalls": [
            "写 road movie 会得到普通公路片 → 要写 saturated neon as key light",
            "低饱和与手持是反的",
            "横向带状构图是它的语法"
        ],
        "see_also": [
            "pop-art",
            "photorealism"
        ],
        "title_original": "Paris, Texas",
        "filmgrab": "https://film-grab.com/2010/06/19/paris-texas/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/wim-wenders/",
        "source": "curated"
    },
    {
        "slug": "welles-citizen-kane",
        "director_zh": "奥逊·威尔斯",
        "director_en": "Orson Welles",
        "director_slug": "welles",
        "title_zh": "公民凯恩",
        "title_en": "Citizen Kane",
        "year": 1941,
        "one_liner": "**深焦与低角度天花板**——把明暗对照搬进现代室内，天花板第一次出现在画面里。",
        "core": [
            "极低角度仰拍，天花板明确出现在画框内，人物被压低或放大",
            "深焦：前后景同时清晰，观众自己选择看哪里",
            "明暗对照的室内：光从窗外/顶部来，人物常成剪影",
            "大量长镜与复杂的场面调度，剪辑点刻意减少"
        ],
        "visual": {
            "色彩": "黑白；深黑与亮白并存，灰阶层次丰富",
            "光影": "硬质方向光（窗、顶灯），大面积深黑，人物轮廓被切出",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，景深极深",
            "构图": "低角度仰拍带天花板、深焦前后景、纵深场面调度；大景别为主",
            "材质": "石、木、报纸、玻璃、金属、旧家具、雪",
            "情绪": "权力、孤独、浮士德式的代价、被围困的巨人"
        },
        "layers": {
            "style": "Orson Welles Citizen Kane, deep focus, low-angle with visible ceilings, 1940s chiaroscuro interiors, long take staging",
            "lighting": "hard directional light from windows and overheads, large deep blacks, silhouetted figures, strong value contrast indoors",
            "color": "black and white; deep blacks and bright whites with a rich grey range",
            "composition": "low angle including the ceiling, deep focus with foreground and background both sharp, staged depth, wide framing",
            "medium": "35mm black-and-white film, fine grain, extreme depth of field",
            "mood": "power, loneliness, Faustian cost, a giant under siege",
            "camera": "low angle, long take with complex blocking, slow crane, deep focus"
        },
        "negative": "flat even lighting, shallow depth of field, eye-level only, handheld, saturated color",
        "palette": [
            [
                "#0A0A0A",
                "深黑"
            ],
            [
                "#3E3A34",
                "暗褐"
            ],
            [
                "#8C8C86",
                "中灰"
            ],
            [
                "#E8E8E4",
                "窗光白"
            ],
            [
                "#5E5A54",
                "石墙灰"
            ],
            [
                "#6B5B45",
                "木褐"
            ]
        ],
        "video": {
            "运动": "人物在深焦中走动、雪、烟、报纸翻动",
            "运镜": "低角度固定、长镜内的调度移动",
            "时长": "10 秒",
            "关键": "**必须带天花板且前后景同时清晰**；平视+浅景深就完全反了"
        },
        "pitfalls": [
            "写 classic Hollywood 会得到平坦的棚内打光 → 这部片是深焦+低角度+强明暗",
            "浅景深与它相反",
            "彩色不成立"
        ],
        "see_also": [
            "baroque",
            "film-noir"
        ],
        "title_original": "Citizen Kane",
        "filmgrab": "https://film-grab.com/2013/02/07/citizen-kane/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/orson-welles/",
        "source": "curated"
    },
    {
        "slug": "welles-touch-of-evil",
        "director_zh": "奥逊·威尔斯",
        "director_en": "Orson Welles",
        "director_slug": "welles",
        "title_zh": "历劫佳人",
        "title_en": "Touch of Evil",
        "year": 1958,
        "one_liner": "**开场三分钟长镜**——高对比黑白与广角畸变，黑色电影的最后一次狂欢。",
        "core": [
            "开场三分钟不剪断的长镜：镜头穿过街区、车辆与人群",
            "广角镜头贴近人物，空间被拉伸畸变，产生压迫与不安",
            "高对比黑白：夜间只有霓虹与车灯，大面积死黑",
            "构图常把人物压在画框边缘或被前景遮挡"
        ],
        "visual": {
            "色彩": "黑白；硬调高对比，夜间大面积死黑，高光溢出",
            "光影": "夜间实用光源（霓虹、车灯、灯泡）+ 大面积黑；硬光在脸上切出强影",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，广角畸变明显",
            "构图": "广角畸变、低角度与倾斜、人物被边缘化或被前景遮挡；复杂的长镜场面调度",
            "材质": "霓虹灯管、湿沥青、旧车、铁、木、玻璃、烟",
            "情绪": "腐败、紧张、道德泥沼、边境的失序"
        },
        "layers": {
            "style": "Orson Welles Touch of Evil, 35mm black and white, famous opening long take, wide-angle distortion, late film noir",
            "lighting": "practical neon and car lights at night against large dead black, hard light cutting deep shadows on faces, blown highlights",
            "color": "black and white, hard high contrast, large black areas, clipping highlights",
            "composition": "wide-angle distortion, low and tilted angles, figures pushed to the frame edge or blocked by foreground, elaborate long-take staging",
            "medium": "35mm black-and-white film, pronounced grain, visible wide-angle stretch",
            "mood": "corrupt, tense, moral quagmire, disorder at the border",
            "camera": "long unbroken take with complex movement, wide-angle close-up, tilted low angle"
        },
        "negative": "flat lighting, telephoto compression, symmetrical calm, saturated color, static coverage",
        "palette": [
            [
                "#0A0A0A",
                "死黑"
            ],
            [
                "#3E3A34",
                "暗褐"
            ],
            [
                "#8C8C86",
                "中灰"
            ],
            [
                "#E8E8E4",
                "霓虹白"
            ],
            [
                "#5E5A54",
                "湿沥青灰"
            ],
            [
                "#6B1F1A",
                "暗红"
            ]
        ],
        "video": {
            "运动": "车流、霓虹闪烁、行人穿过街道、烟雾",
            "运镜": "长镜横移穿过街区、广角贴近、倾斜低角度",
            "时长": "10 秒",
            "关键": "**广角畸变 + 大面积死黑 + 复杂长镜调度**；平视和补光都会杀掉它"
        },
        "pitfalls": [
            "写 noir 会得到普通的暗调犯罪片 → 广角畸变与长镜调度是它的签名",
            "彩色与浅景深是反的",
            "补光会毁掉大面积黑"
        ],
        "see_also": [
            "film-noir",
            "expressionism"
        ],
        "title_original": "Touch of Evil",
        "filmgrab": "https://film-grab.com/2015/05/06/touch-of-evil/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/orson-welles/",
        "source": "curated"
    },
    {
        "slug": "welles-the-trial",
        "director_zh": "奥逊·威尔斯",
        "director_en": "Orson Welles",
        "director_slug": "welles",
        "title_zh": "审判",
        "title_en": "The Trial",
        "year": 1962,
        "one_liner": "**空旷到扭曲的黑白空间**——废弃车站被拍成卡夫卡的迷宫，广角把人压扁。",
        "core": [
            "实景拍摄于废弃的巴黎火车站：巨大、空旷、几何化的空间",
            "极广角镜头让墙壁与柱子在画面边缘弯曲，产生压迫",
            "高对比黑白，大面积深黑与孤立的亮区",
            "人物在巨大的空间中很小，或被迫贴着墙与门"
        ],
        "visual": {
            "色彩": "黑白；硬调高对比，深黑多，高光集中",
            "光影": "顶光与局部灯源，制造头顶的压迫阴影；大面积黑",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，广角畸变强",
            "构图": "极广角、巨大空间的纵深、人物被压在边缘；天花板频繁入画",
            "材质": "石柱、铁架、混凝土、木门、旧文件、玻璃、尘埃",
            "情绪": "荒诞、噩梦、官僚的窒息、无出路的恐惧"
        },
        "layers": {
            "style": "Orson Welles The Trial, 35mm black and white, cavernous real locations, extreme wide angle, Kafkaesque geometry",
            "lighting": "overhead and isolated practical sources casting oppressive top shadows, large black areas with concentrated highlights",
            "color": "black and white, hard contrast, deep black dominant, contained highlights",
            "composition": "extreme wide angle, vast receding spaces, figures pressed to the edge, ceilings frequently in frame",
            "medium": "35mm black-and-white film, pronounced grain, strong wide-angle distortion",
            "mood": "absurd, nightmarish, bureaucratic suffocation, inescapable dread",
            "camera": "wide-angle low and high angle, slow dolly through vast spaces, no handheld"
        },
        "negative": "normal lens, cosy interiors, flat lighting, saturated color, symmetrical calm",
        "palette": [
            [
                "#0A0A0A",
                "深黑"
            ],
            [
                "#3E3A34",
                "暗褐"
            ],
            [
                "#8C8C86",
                "石柱灰"
            ],
            [
                "#E8E8E4",
                "孤立高光白"
            ],
            [
                "#5E5A54",
                "混凝土灰"
            ],
            [
                "#6B5B45",
                "旧木褐"
            ]
        ],
        "video": {
            "运动": "尘埃在光柱里飘、纸页翻动、人物在巨大空间里缓慢移动",
            "运镜": "广角缓慢推进、高空俯视",
            "时长": "10 秒",
            "关键": "**极广角 + 巨大空旷空间 + 天花板**；正常焦段会让卡夫卡的空间感消失"
        },
        "pitfalls": [
            "写 Kafka 会得到普通的荒诞剧 → 空间必须巨大且用极广角畸变",
            "温馨室内与它完全相反",
            "彩色不成立"
        ],
        "see_also": [
            "expressionism",
            "surrealism"
        ],
        "title_original": "The Trial",
        "filmgrab": "https://film-grab.com/2015/05/13/the-trial/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/orson-welles/",
        "source": "curated"
    },
    {
        "slug": "hitchcock-vertigo",
        "director_zh": "阿尔弗雷德·希区柯克",
        "director_en": "Alfred Hitchcock",
        "director_slug": "hitchcock",
        "title_zh": "迷魂记",
        "title_en": "Vertigo",
        "year": 1958,
        "one_liner": "**绿与红的病态对撞**——滤镜化的旧金山，彩色黑色电影从此有了样板。",
        "core": [
            "病态的绿与红对撞：绿色霓虹、红色室内、灰蓝雾",
            "大量滤镜与柔光，把旧金山变成梦境般的雾色",
            "构图强调垂直与眩晕：楼梯、塔楼、纵深下望",
            "人物常被放在画面正中，然后被空间吞掉"
        ],
        "visual": {
            "色彩": "病态绿、暗红、灰蓝、雾灰；高饱和但整体偏冷",
            "光影": "雾中的散射光与霓虹；柔焦与滤镜让画面失去锐度",
            "笔触": "（电影媒介）35mm 彩色胶片，柔焦与滤镜效果明显，颗粒细",
            "构图": "垂直纵深（楼梯、塔）与俯视；人物居中；薄雾遮挡远景",
            "材质": "雾、霓虹灯管、木楼梯、红墙、玻璃、旧车、花束",
            "情绪": "痴迷、眩晕、幻觉、被过去缠住"
        },
        "layers": {
            "style": "Hitchcock Vertigo, filtered San Francisco, sickly green and red, soft focus, colour noir",
            "lighting": "fog-diffused light with neon accents, soft and hazy, filters softening the whole image, cool overall",
            "color": "sickly green, dark red, blue-grey, mist grey; saturated but cold overall",
            "composition": "vertical depth down stairwells and towers, overhead looking down, subject centred, fog veiling the background",
            "medium": "35mm colour film, heavy soft focus and filtration, fine grain",
            "mood": "obsessive, vertiginous, hallucinatory, haunted by the past",
            "camera": "slow dolly with zoom (vertigo effect), overhead down-shot, static centred"
        },
        "negative": "sharp un-filtered image, warm golden palette, flat lighting, handheld, desaturated grey",
        "palette": [
            [
                "#3E6B4A",
                "病态绿"
            ],
            [
                "#6B1F1A",
                "暗红"
            ],
            [
                "#4A5A6B",
                "灰蓝"
            ],
            [
                "#B8BCB4",
                "雾灰"
            ],
            [
                "#1F3A2E",
                "深绿"
            ],
            [
                "#E0D2B4",
                "柔光米"
            ]
        ],
        "video": {
            "运动": "雾流动、霓虹闪烁、人物缓慢走向纵深、眩晕的变焦",
            "运镜": "希区柯克变焦（推轨+变焦）、俯视下望",
            "时长": "10 秒",
            "关键": "**病态绿 + 雾 + 柔焦滤镜**；把画面拍清晰就变成了普通彩色片"
        },
        "pitfalls": [
            "写 colour noir 会得到常规黑色电影 → 这部片的特征是绿与雾与柔焦",
            "锐利无滤镜的画面是反的",
            "暖金色调完全跑偏"
        ],
        "see_also": [
            "film-noir",
            "surrealism"
        ],
        "title_original": "Vertigo",
        "filmgrab": "https://film-grab.com/2013/02/28/vertigo/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/alfred-hitchcock/",
        "source": "curated"
    },
    {
        "slug": "hitchcock-rear-window",
        "director_zh": "阿尔弗雷德·希区柯克",
        "director_en": "Alfred Hitchcock",
        "director_slug": "hitchcock",
        "title_zh": "后窗",
        "title_en": "Rear Window",
        "year": 1954,
        "one_liner": "**单场景 + 长焦窥视**——把「看」这件事本身做成构图结构，一整个街区摊在窗前。",
        "core": [
            "单一场景（公寓）内的多窗口窥视构图：对面楼被切成一个个画框",
            "长焦镜头压缩空间，把对面楼拉近但保持距离",
            "室内是暖调钨丝与霓虹混合，对面楼是各种不同的窗光",
            "视线引导：从室内到窗外，构图始终带框"
        ],
        "visual": {
            "色彩": "暖褐、霓虹品红与绿、夜蓝；高饱和的彩色片，色彩浓艳",
            "光影": "室内钨丝灯 + 窗外霓虹与路灯；夜晚多光源，光从下方与侧面来",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩浓烈，颗粒细",
            "构图": "多窗口的框中框、长焦压缩、室内外视线关系；人物常在前景剪影",
            "材质": "窗帘、玻璃、砖墙、金属栏杆、水泥、霓虹灯、雨",
            "情绪": "窥视的不安、闷热、被围困的好奇"
        },
        "layers": {
            "style": "Hitchcock Rear Window, single-set voyeurism, long-lens compression, multi-window framing, saturated 1950s colour",
            "lighting": "interior tungsten mixed with exterior neon and street lights, multi-source at night, light coming from below and the side",
            "color": "warm brown, neon magenta and green, night blue; saturated colour with rich contrast",
            "composition": "grid of windows as frames within frames, long-lens compression, sightlines between interior and courtyard, foreground silhouettes",
            "medium": "35mm colour film, rich saturation, fine grain",
            "mood": "voyeuristic unease, heat, trapped curiosity",
            "camera": "long lens framing from one position, slow pan across windows, static interior wide"
        },
        "negative": "handheld, multi-location coverage, desaturated palette, wide-angle establishing, modern digital clean",
        "palette": [
            [
                "#6B4A32",
                "暖褐"
            ],
            [
                "#C42B72",
                "霓虹品红"
            ],
            [
                "#3E7A4A",
                "霓虹绿"
            ],
            [
                "#1E2A4A",
                "夜蓝"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#C4C0B4",
                "窗帘米"
            ]
        ],
        "video": {
            "运动": "窗帘被风掀起、雨落、邻居窗口的微小活动、霓虹闪烁",
            "运镜": "长焦缓慢横摇过窗口、固定室内宽景",
            "时长": "10 秒",
            "关键": "**必须保持单一视点 + 长焦压缩 + 多窗口框**；切换机位或多角度会破坏它的结构"
        },
        "pitfalls": [
            "写 thriller 会得到多机位犯罪片 → 这部片的语法是单一视点的长焦窥视",
            "手持是反的",
            "低饱和会失去 50 年代彩色片的浓艳"
        ],
        "see_also": [
            "photorealism",
            "pop-art"
        ],
        "title_original": "Rear Window",
        "filmgrab": "https://film-grab.com/2012/12/08/rear-window/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/alfred-hitchcock/",
        "source": "curated"
    },
    {
        "slug": "lynch-blue-velvet",
        "director_zh": "大卫·林奇",
        "director_en": "David Lynch",
        "director_slug": "lynch",
        "title_zh": "蓝丝绒",
        "title_en": "Blue Velvet",
        "year": 1986,
        "one_liner": "**艳红窗帘与暗绿草坪**——把美国小镇拍成夜里的高饱和噩梦，白天越干净越可怕。",
        "core": [
            "极端撞色：艳红、宝蓝（丝绒）、暗绿草坪、白栅栏",
            "白天是高饱和的干净小镇；夜里是深黑里的单点色光（红、蓝）",
            "构图常把人物放在对称的干净构图里，然后让不洁的东西进入画框",
            "光源刻意戏剧化：从门缝、车灯、舞台灯来"
        ],
        "visual": {
            "色彩": "艳红、宝蓝、暗绿、纯白栅栏；高饱和且刻意刺眼",
            "光影": "夜间单点有色光源（红/蓝）+ 大面积黑；白天高调干净日光",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩浓烈，颗粒细",
            "构图": "对称的干净构图、框中框（门缝、衣柜、车窗）、人物居中",
            "材质": "丝绒、栅栏、草地、汽车、皮革、金属、雨",
            "情绪": "甜美表面下的暴力、被窥视的欲望、梦魇"
        },
        "layers": {
            "style": "David Lynch Blue Velvet, saturated red and blue against dark green suburbia, ironic clean compositions, American nightmare",
            "lighting": "night: single coloured source against large black; day: high-key clean daylight; dramatic sources through doors and car lights",
            "color": "vivid crimson, royal blue velvet, dark lawn green, pure white fence; high saturation used aggressively",
            "composition": "symmetrical clean staging, framing through door cracks and wardrobes, centred figures, intrusion into tidy frames",
            "medium": "35mm colour film, rich saturation, fine grain",
            "mood": "violence under sweetness, voyeuristic desire, nightmare",
            "camera": "static symmetrical wide, slow push through doors, occasional dream-like drift"
        },
        "negative": "naturalistic muted palette, documentary light, handheld vérité, desaturated grey, sparse composition",
        "palette": [
            [
                "#B01F1F",
                "艳红"
            ],
            [
                "#1F3A8C",
                "宝蓝"
            ],
            [
                "#2E4A2E",
                "暗绿草坪"
            ],
            [
                "#F2F2F0",
                "白栅栏"
            ],
            [
                "#141618",
                "夜黑"
            ],
            [
                "#6B4A2B",
                "木褐"
            ]
        ],
        "video": {
            "运动": "窗帘飘动、雨落、丝绒的微动、车灯扫过",
            "运镜": "缓慢推进、对称固定、穿过门缝",
            "时长": "10 秒",
            "关键": "**高饱和撞色（红/蓝）+ 干净对称构图**；写 subdued 或 handheld 就完全跑偏"
        },
        "pitfalls": [
            "写 suburban drama 会得到平淡的家庭剧 → 这部片的颜色是刻意刺眼的",
            "低饱和与写实光是反的",
            "对称的干净构图是它的反讽装置"
        ],
        "see_also": [
            "pop-art",
            "surrealism"
        ],
        "title_original": "Blue Velvet",
        "filmgrab": "https://film-grab.com/2010/06/17/blue-velvet/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/david-lynch/",
        "source": "curated"
    },
    {
        "slug": "lynch-mulholland-drive",
        "director_zh": "大卫·林奇",
        "director_en": "David Lynch",
        "director_slug": "lynch",
        "title_zh": "穆赫兰道",
        "title_en": "Mulholland Drive",
        "year": 2001,
        "one_liner": "**暖琥珀的夜与冷蓝的幻**——同一场戏换一套色温就是另一层现实。",
        "core": [
            "两套色温对应两层现实：暖琥珀（好莱坞白日梦）与冷蓝（真相/夜）",
            "夜间段落用深黑 + 暖点光源（台灯、车灯）",
            "构图在「正常」与「诡异」之间摇摆：干净对称的画面里出现不该有的东西",
            "暖色段落刻意柔焦美化，冷色段落更硬更脏"
        ],
        "visual": {
            "色彩": "暖琥珀、蜜色（梦）对冷蓝、钢灰（真相）；两套并列",
            "光影": "暖段：柔和钨丝与金色日光；冷段：冷蓝荧光与深黑",
            "笔触": "（电影媒介）35mm 胶片，柔焦与颗粒，暖段更柔",
            "构图": "对称与框中框；暖段规整，冷段失衡",
            "材质": "丝绒、木、玻璃、霓虹、旧车、胶片、蓝钥匙、雨",
            "情绪": "欲望的幻觉、身份的错位、梦与真相的裂缝"
        },
        "layers": {
            "style": "David Lynch Mulholland Drive, two colour-temperature registers for dream and truth, Hollywood reverie turning cold, surreal staging",
            "lighting": "warm register: soft tungsten and golden daylight; cold register: cool blue fluorescent and deep black; sources often visible",
            "color": "warm amber and honey for the dream, cold blue and steel grey for the truth; the two are never mixed",
            "composition": "symmetry and frame within frame in the warm register, imbalance and unease in the cold one",
            "medium": "35mm film, soft focus and grain, softer in the warm passages",
            "mood": "hallucinated desire, displaced identity, a crack between dream and truth",
            "camera": "slow push, static symmetrical wide, dreamlike drift, occasional handheld unease"
        },
        "negative": "single consistent grade, naturalistic documentary light, handheld chaos, desaturated grey, flat composition",
        "palette": [
            [
                "#C9A227",
                "暖琥珀"
            ],
            [
                "#8A5A2B",
                "蜜色"
            ],
            [
                "#1F3A6E",
                "冷蓝"
            ],
            [
                "#4A5560",
                "钢灰"
            ],
            [
                "#141618",
                "深黑"
            ],
            [
                "#C42B72",
                "霓虹粉"
            ]
        ],
        "video": {
            "运动": "烟雾、车灯扫过、缓慢的门开合、人物静止凝视",
            "运镜": "缓慢推进、对称固定、梦游式漂移",
            "时长": "10 秒",
            "关键": "**两套色温必须分得清**（暖梦 / 冷真相）；混成一个调子就失去了叙事层"
        },
        "pitfalls": [
            "写 neo-noir 会得到统一的冷调 → 这部片是暖冷两套对撞",
            "单一调色会把两层现实拍平",
            "手持混乱不是它的语法"
        ],
        "see_also": [
            "surrealism",
            "film-noir"
        ],
        "title_original": "Mulholland Drive",
        "filmgrab": "https://film-grab.com/2014/09/23/mulholland-drive/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/david-lynch/",
        "source": "curated"
    },
    {
        "slug": "michael-mann-heat",
        "director_zh": "迈克尔·曼",
        "director_en": "Michael Mann",
        "director_slug": "michael-mann",
        "title_zh": "盗火线",
        "title_en": "Heat",
        "year": 1995,
        "one_liner": "**洛杉矶的蓝灰夜景被拍成冷金属**——枪战段落没有配乐，只有空间与回声。",
        "core": [
            "夜景以青蓝与灰为主，冷金属质感，几乎无暖色",
            "大量广角与静止构图，城市空间被拍得空旷而精确",
            "枪战段落在白天的灰蓝都市里，无配乐，靠枪声在楼宇间的回声制造空间",
            "人物常被放在大面积的玻璃、混凝土与车流之中"
        ],
        "visual": {
            "色彩": "青蓝、钢灰、混凝土白、少量钠灯橙；低饱和偏冷",
            "光影": "夜景为钠灯与霓虹的混合但被压成冷调；白天为阴天散射与玻璃反射",
            "笔触": "（电影媒介）35mm 胶片，颗粒细，色调冷硬",
            "构图": "静止宽景、玻璃反光、空旷的城市纵深；人物在画面中偏小",
            "材质": "玻璃幕墙、混凝土、车漆、钢、沥青、雨、霓虹",
            "情绪": "冷静、职业化、孤独、宿命的对峙"
        },
        "layers": {
            "style": "Michael Mann Heat, cool blue-grey Los Angeles, architectural emptiness, professional crime drama, un-scored action",
            "lighting": "night sodium and neon mixed but graded cool, day overcast diffuse with glass bounce, controlled and undramatic",
            "color": "cyan blue, steel grey, concrete white with sparse sodium orange; low saturation leaning cool",
            "composition": "static wide shots, glass reflections, empty urban depth, small figures in large spaces",
            "medium": "35mm film, fine grain, hard cool tonality",
            "mood": "cold, professional, lonely, fated confrontation",
            "camera": "static wide, slow dolly, long lens across streets, no handheld"
        },
        "negative": "warm orange night grade, handheld chaos, close-up shot-reverse-shot, saturated colours, teal-orange stylisation",
        "palette": [
            [
                "#2E4A5A",
                "青蓝"
            ],
            [
                "#5A6570",
                "钢灰"
            ],
            [
                "#C4C8C9",
                "混凝土白"
            ],
            [
                "#C97A2B",
                "钠灯橙"
            ],
            [
                "#141618",
                "夜黑"
            ],
            [
                "#8C9490",
                "玻璃灰"
            ]
        ],
        "video": {
            "运动": "车流、玻璃反射中的人影、雨、枪火闪动",
            "运镜": "静止宽景、缓慢横移、长焦",
            "时长": "10 秒",
            "关键": "**冷调 + 空旷城市 + 静止机位**；手持与暖调会把它变成普通警匪片"
        },
        "pitfalls": [
            "写 action film 会得到手持快剪的枪战片 → 这部片的枪战是**安静而空旷**的",
            "暖橙夜景调色是反的",
            "玻璃反射是它的构图装置"
        ],
        "see_also": [
            "photorealism",
            "precisionism"
        ],
        "title_original": "Heat",
        "filmgrab": "https://film-grab.com/2013/03/27/heat/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/michael-mann/",
        "source": "curated"
    },
    {
        "slug": "coppola-apocalypse-now",
        "director_zh": "弗朗西斯·福特·科波拉",
        "director_en": "Francis Ford Coppola",
        "director_slug": "coppola",
        "title_zh": "现代启示录",
        "title_en": "Apocalypse Now",
        "year": 1979,
        "one_liner": "**橙色的火与烟**——直升机剪影对着天空，把战争拍成色温的轰炸。",
        "core": [
            "橙色的火、烟与夕阳统治画面，人物成黑色剪影",
            "大量烟雾与逆光，空间被体积光填满",
            "构图把直升机、船、人物压在画面的下三分之一，天空占大面积",
            "夜间段落是深黑 + 火焰的单一暖光源"
        ],
        "visual": {
            "色彩": "橙色火与烟、暗绿丛林、深黑、天光白；高对比，暖冷分区",
            "光影": "逆光与火光；烟雾散射出体积光，人物成剪影，暗部深",
            "笔触": "（电影媒介）35mm 胶片，颗粒明显，高光溢出",
            "构图": "低地平线、大面积天空与烟、人物剪影贴在下三分之一；纵深烟雾",
            "材质": "烟、火、直升机、水、泥、丛林、尼龙、橙剂雾",
            "情绪": "迷狂、暴力、末日感、逐渐失控"
        },
        "layers": {
            "style": "Coppola Apocalypse Now, orange fire and smoke, helicopter silhouettes against sky, Vietnam war as sensory overload",
            "lighting": "backlight and firelight, volumetric shafts through smoke, silhouetted figures, deep shadows, blown highlights",
            "color": "orange fire and smoke, dark jungle green, deep black, sky white; high contrast with warm and cool zones",
            "composition": "low horizon with huge sky and smoke, figures silhouetted in the lower third, smoke layering depth",
            "medium": "35mm film, pronounced grain, clipping highlights",
            "mood": "manic, violent, apocalyptic, spiralling out of control",
            "camera": "slow aerial drift, lateral tracking, static wide, occasional handheld"
        },
        "negative": "clean air, desaturated palette, flat lighting, tight interior framing, modern digital sharpness",
        "palette": [
            [
                "#D97426",
                "火橙"
            ],
            [
                "#8A6A3E",
                "烟褐"
            ],
            [
                "#2E4A32",
                "丛林暗绿"
            ],
            [
                "#141618",
                "深黑"
            ],
            [
                "#E8E8E4",
                "天光白"
            ],
            [
                "#B0722B",
                "夕阳金"
            ]
        ],
        "video": {
            "运动": "烟雾翻滚、火焰、直升机旋翼、水花",
            "运镜": "缓慢航拍横移、低空推进",
            "时长": "10 秒",
            "关键": "**烟与火造体积光，人物成剪影**；把光打平或减少烟就变成了普通战争片"
        },
        "pitfalls": [
            "写 war movie 会得到战场写实片 → 这部片是**感官过载**",
            "烟是体积光的载体，不能省",
            "低饱和与平光是反的"
        ],
        "see_also": [
            "romanticism",
            "baroque"
        ],
        "title_original": "Apocalypse Now",
        "filmgrab": "https://film-grab.com/2012/11/10/apocalypse-now/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/francis-ford-coppola/",
        "source": "curated"
    },
    {
        "slug": "coppola-godfather",
        "director_zh": "弗朗西斯·福特·科波拉",
        "director_en": "Francis Ford Coppola",
        "director_slug": "coppola",
        "title_zh": "教父",
        "title_en": "The Godfather",
        "year": 1972,
        "one_liner": "**黑里还有黑**——Gordon Willis 的顶光让眼窝永远在阴影里，室内几乎没有补光。",
        "core": [
            "「黑里还有黑」：暗部层次极多，最深的黑仍保留细节",
            "室内只用顶光（吊灯），眼窝与颊下永远在阴影里",
            "暖褐与暗金为主，室内像被旧木头与酒浸过",
            "构图以中景与群像为主，人物常被安排在暗部的正中央"
        ],
        "visual": {
            "色彩": "暖褐、暗金、酒红、深黑；低照度暖调，饱和度中低",
            "光影": "顶光为主（吊灯/桌灯），无补光；脸的上半亮、眼窝黑，大面积暗部有层次",
            "笔触": "（电影媒介）35mm 胶片，颗粒可见，色调如旧照片",
            "构图": "中景与群像、对称的室内、人物被暗部包围；桌面与手部特写",
            "材质": "木、皮革、酒、纸、丝绸、铁、旧墙纸、雪茄烟",
            "情绪": "沉重、家族宿命、权力的仪式感"
        },
        "layers": {
            "style": "Coppola The Godfather, Gordon Willis top light, blacks within blacks, 1940s-50s period interiors, operatic family drama",
            "lighting": "overhead light only with no fill, eyes and cheeks permanently in shadow, deep blacks that retain detail, warm and dim",
            "color": "warm brown, dark gold, wine red, deep black; low key warm with moderate saturation",
            "composition": "medium shots and group staging, symmetrical interiors, figures enveloped in darkness, close-ups of hands and desks",
            "medium": "35mm film, visible grain, sepia-like aged tonality",
            "mood": "heavy, dynastic fate, the ritual of power",
            "camera": "slow push, static medium, eye level, occasional slow dolly"
        },
        "negative": "flat even lighting, fill light on faces, bright daylight interior, saturated colours, handheld",
        "palette": [
            [
                "#6B4A2B",
                "暖褐"
            ],
            [
                "#A8843C",
                "暗金"
            ],
            [
                "#6B1F1A",
                "酒红"
            ],
            [
                "#0F0F0F",
                "深黑"
            ],
            [
                "#C4B49A",
                "旧纸米"
            ],
            [
                "#3E3A34",
                "暗部褐灰"
            ]
        ],
        "video": {
            "运动": "雪茄烟上升、手部动作、门开合、人物静坐",
            "运镜": "缓慢推进、固定中景",
            "时长": "10 秒",
            "关键": "**顶光 + 眼窝的黑 + 无补光**；把脸照亮就毁掉了 Willis 的全部设计"
        },
        "pitfalls": [
            "补光是这部片的死敌 → 必须在负向词里写 no fill light",
            "写 period drama 会得到明亮的年代剧 → 它近乎全暗",
            "平光会失去「黑里还有黑」的层次"
        ],
        "see_also": [
            "baroque",
            "film-noir"
        ],
        "title_original": "The Godfather",
        "filmgrab": "https://film-grab.com/2010/07/27/the-godfather/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/francis-ford-coppola/",
        "source": "curated"
    },
    {
        "slug": "scorsese-taxi-driver",
        "director_zh": "马丁·斯科塞斯",
        "director_en": "Martin Scorsese",
        "director_slug": "scorsese",
        "title_zh": "出租车司机",
        "title_en": "Taxi Driver",
        "year": 1976,
        "one_liner": "**钠灯的黄绿把纽约夜色染成病态**——红色在灰里只出现一次，那一处就是全片的爆点。",
        "core": [
            "钠灯的黄绿统治夜景，湿沥青反光把颜色拉长",
            "红色被严格节制：只在关键一处出现，形成全片色彩爆点",
            "大量车内/车外视点与后视镜构图，人物被玻璃隔着",
            "白天是灰扑扑的中性色，夜里的黄绿与之对立"
        ],
        "visual": {
            "色彩": "钠灯黄绿、湿沥青灰、暗红（节制使用）、污白",
            "光影": "夜间钠灯与车灯作主光，大面积暗部带黄绿偏色；白天中性平光",
            "笔触": "（电影媒介）35mm 彩色胶片，颗粒明显，色彩脏",
            "构图": "后视镜与车窗构图、街景纵深、人物被玻璃隔开；低角度街道",
            "材质": "湿沥青、玻璃、铁、霓虹、雨、蒸汽、旧车",
            "情绪": "失眠、愤怒、孤独、被城市浸透的暴力"
        },
        "layers": {
            "style": "Scorsese Taxi Driver, sodium-yellow-green night New York, wet street reflections, restrained use of red, 1970s grime",
            "lighting": "sodium street lamps and headlights as key at night with large yellow-green shadows, wet asphalt stretching reflections, neutral flat daylight",
            "color": "sodium yellow-green, wet asphalt grey, dark red used sparingly, soiled white; dirty low saturation",
            "composition": "framing through windscreens and mirrors, deep street perspective, figures separated by glass, low street angles",
            "medium": "35mm colour film, pronounced grain, dirty tonality",
            "mood": "insomniac, angry, lonely, violence soaked into the city",
            "camera": "slow street-level dolly, static wide, framing through glass, occasional handheld"
        },
        "negative": "clean digital look, saturated colours, bright daylight, warm cozy interior, symmetrical formal composition",
        "palette": [
            [
                "#8A9A3C",
                "钠灯黄绿"
            ],
            [
                "#3E4245",
                "湿沥青灰"
            ],
            [
                "#6B1F1A",
                "节制的暗红"
            ],
            [
                "#C4C0B4",
                "污白"
            ],
            [
                "#141618",
                "夜黑"
            ],
            [
                "#6B6459",
                "旧车褐"
            ]
        ],
        "video": {
            "运动": "雨刷摆动、蒸汽从井盖升起、街灯下的雨水、车流",
            "运镜": "贴地缓慢横移、车内固定视角",
            "时长": "10 秒",
            "关键": "**钠灯黄绿 + 湿沥青反射**，红色要**节制**；把红色用满就丢掉了那个爆点"
        },
        "pitfalls": [
            "写 crime drama 会得到干净的都市犯罪片 → 这部片的颜色是**脏的黄绿**",
            "红色用多了就没有爆点",
            "干净数字质感是反的"
        ],
        "see_also": [
            "film-noir",
            "photorealism"
        ],
        "title_original": "Taxi Driver",
        "filmgrab": "https://film-grab.com/2010/07/29/taxi-driver/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/martin-scorsese/",
        "source": "curated"
    },
]
