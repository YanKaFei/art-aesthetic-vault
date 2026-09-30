# -*- coding: utf-8 -*-
"""fv_new_9.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "tsai-ming-liang-goodbye-dragon-inn",
        "director_zh": "蔡明亮",
        "director_en": "Tsai Ming-liang",
        "director_slug": "tsai-ming-liang",
        "title_zh": "不散",
        "title_en": "Goodbye Dragon Inn",
        "year": 2003,
        "one_liner": "**一座将拆的电影院，一场没几个人看的电影**——固定机位与屋外大雨，时间被拉成空间的面积。",
        "core": [
            "全片几乎都在影院内：固定机位、极长镜头，动作被压到最少",
            "室内是影院特有的混合光：银幕的反射光 + 出口指示灯 + 走廊日光灯",
            "屋外大雨是唯一持续的运动，雨声替代对白",
            "大量空座位与走廊的空镜，人物常只作为剪影出现"
        ],
        "visual": {
            "色彩": "暗绿、褐红、屏幕冷白、出口灯的绿；低饱和且压暗",
            "光影": "银幕反射光为周期性主光（随画面变化）；出口指示灯与走廊日光灯为固定冷光",
            "笔触": "（电影媒介）35mm/数字胶片感，颗粒明显，暗部偏绿",
            "构图": "固定宽景、影厅的对称纵深、走廊与门的框中框；人物小且偏置",
            "材质": "绒布座椅、木地板、瓷砖、雨、玻璃、旧墙、水渍",
            "情绪": "孤独、衰败、对电影本身的告别"
        },
        "layers": {
            "style": "Tsai Ming-liang Goodbye Dragon Inn, fixed camera inside a decaying cinema, extreme long take, rain outside, minimal action",
            "lighting": "screen glow as a flickering key, green exit signs and corridor fluorescents as fixed cool fill, very low key with green shadows",
            "color": "dark green, brown-red, cold screen white, exit-sign green; low saturation and underexposed",
            "composition": "locked-off wide shot, symmetrical auditorium depth, framing through corridors and doors, small off-centre figures",
            "medium": "film-look digital, pronounced grain, green-leaning shadows",
            "mood": "lonely, decaying, a farewell to cinema itself",
            "camera": "completely static long take, no movement, wide framing of the auditorium"
        },
        "negative": "moving camera, handheld, close-up coverage, fast cutting, saturated colors, daylight, dialogue-driven staging",
        "palette": [
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#6B1F1A",
                "褐红"
            ],
            [
                "#C4CFD4",
                "屏幕冷白"
            ],
            [
                "#3E7A4A",
                "出口灯绿"
            ],
            [
                "#0F1210",
                "暗部黑"
            ],
            [
                "#8C8880",
                "旧墙灰"
            ]
        ],
        "video": {
            "运动": "屋外大雨、银幕上光影变化、出口灯恒亮、人物极小地移动",
            "运镜": "完全固定；不要任何运镜",
            "时长": "15 秒以上",
            "关键": "**固定机位 + 影厅纵深 + 持续大雨**；加运镜或揭示对白就丢掉了它的空"
        },
        "pitfalls": [
            "写 drama 会得到有对白与运镜的剧情片 → 这部片是**固定、空、几乎无对白**的",
            "任何镜头运动都反",
            "光要暗且偏绿（出口灯与银幕），明亮均匀会毁掉影院感"
        ],
        "see_also": [
            "minimalism-art",
            "realism"
        ],
        "title_original": "Goodbye Dragon Inn",
        "filmgrab": "https://film-grab.com/2025/07/17/goodbye-dragon-inn/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/tsai-ming-liang/",
        "source": "curated"
    },
    {
        "slug": "refn-the-neon-demon",
        "director_zh": "尼古拉斯·温丁·雷弗恩",
        "director_en": "Nicolas Winding Refn",
        "director_slug": "nicolas-winding-refn",
        "title_zh": "霓虹恶魔",
        "title_en": "The Neon Demon",
        "year": 2016,
        "one_liner": "**把品红与青推成唯一光源**——对称构图与慢速推镜，当代霓虹美学的极端样本。",
        "core": [
            "品红与青是唯一的光源颜色，环境完全被这两色统治",
            "严格对称构图与极慢的推镜/横移，镜头像在催眠",
            "大量反光材质（镜面、玻璃、亮片、血）制造对称倒影",
            "构图把人物放在正中，两侧光源对称打出轮廓光"
        ],
        "visual": {
            "色彩": "品红、青蓝、正红、金、纯黑；高饱和且双色主导",
            "光影": "霓虹/有色光作主光，人物轮廓被品红与青从两侧勾出；大面积纯黑",
            "笔触": "（电影媒介）数字摄影，锐利，高光溢出，色彩极纯",
            "构图": "严格对称、中心构图、极慢推镜；镜面与倒影制造几何",
            "材质": "镜面、玻璃、亮片、丝绒、金属、血、霓虹灯管",
            "情绪": "冷艳、欲望与暴力、审美化的恐怖"
        },
        "layers": {
            "style": "Nicolas Winding Refn The Neon Demon, magenta and cyan as the only light sources, strict symmetry, hypnotic slow push, fashion-world horror",
            "lighting": "coloured neon as key from both sides rimming the figure in magenta and cyan, large pure black areas, no white light",
            "color": "magenta, cyan, primary red, gold, pure black; high saturation with two hues dominating",
            "composition": "strict symmetry, centred subject, extremely slow push in, mirrors and reflections building geometry",
            "medium": "digital cinema, sharp, blown highlights, extremely pure colour",
            "mood": "cold glamour, desire and violence, aestheticised horror",
            "camera": "very slow push in, symmetrical locked-off wide, slow lateral drift"
        },
        "negative": "naturalistic white light, handheld, desaturated palette, asymmetric framing, documentary realism",
        "palette": [
            [
                "#C42B72",
                "品红"
            ],
            [
                "#1E8C9A",
                "青"
            ],
            [
                "#B0241F",
                "正红"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#0A0A0A",
                "纯黑"
            ],
            [
                "#E0C4D4",
                "亮片粉白"
            ]
        ],
        "video": {
            "运动": "极缓的推镜、烟雾、反光流动、人物缓慢转身",
            "运镜": "极慢对称推镜、缓慢横移；绝不手持",
            "时长": "10 秒",
            "关键": "**品红与青是唯一光源 + 严格对称**；引入白光或手持就完全不是这部片"
        },
        "pitfalls": [
            "写 neon 会得到蓝紫都市夜景 → 这里是**品红/青双色**且人物被两侧打光",
            "白光与自然光是反的",
            "对称与极慢推镜是签名，手持会毁掉"
        ],
        "see_also": [
            "neo-pop",
            "pop-art"
        ],
        "title_original": "The Neon Demon",
        "filmgrab": "https://film-grab.com/2016/11/25/the-neon-demon/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/nicolas-winding-refn/",
        "source": "curated"
    },
    {
        "slug": "malick-days-of-heaven",
        "director_zh": "泰伦斯·马力克",
        "director_en": "Terrence Malick",
        "director_slug": "terrence-malick",
        "title_zh": "天堂之日",
        "title_en": "Days of Heaven",
        "year": 1978,
        "one_liner": "**全片在魔幻时刻实拍**——麦田的金、天空的橙紫与逆光剪影，自然光摄影的公共标杆。",
        "core": [
            "几乎全片在日出后/日落前的魔幻时刻实拍：光极低、极暖、方向性极强",
            "人物常成逆光剪影，被天空与麦田的亮背景包围",
            "麦田、天空、水面构成横向的层次，地平线低",
            "构图开阔，人物在风景里很小；镜头缓慢漂移像在观察"
        ],
        "visual": {
            "色彩": "麦金、橙、紫、暗绿、天蓝；暖调且层次连续，暗部偏紫",
            "光影": "魔幻时刻的低角度逆光：长影、轮廓光、天空过曝；室内用窗光与油灯",
            "笔触": "（电影媒介）35mm 胶片，柔焦，颗粒细，高光有光晕",
            "构图": "低地平线、横向风景层次、人物剪影偏置；缓慢漂移与航拍",
            "材质": "麦秆、土、水、棉布、木、火、天空",
            "情绪": "田园的诗意、宿命的哀伤、时间流逝"
        },
        "layers": {
            "style": "Terrence Malick Days of Heaven, magic-hour natural light, wheat-field horizontals, backlit silhouettes, lyrical landscape",
            "lighting": "low-angle magic-hour backlight with long shadows and rim light, blown sky, interiors lit by window and oil lamp only",
            "color": "wheat gold, orange, violet, dark green, sky blue; warm with continuous gradation and violet-leaning darks",
            "composition": "low horizon, horizontal layers of field and sky, silhouetted off-centre figures, slow drifting and aerial camera",
            "medium": "35mm film, soft focus, fine grain, glowing highlights",
            "mood": "pastoral poetry, fated sorrow, passing time",
            "camera": "slow drifting track, aerial sweep over fields, static wide at dusk"
        },
        "negative": "harsh midday sun, flat even lighting, handheld chaos, desaturated grey, close-up driven coverage, artificial key light",
        "palette": [
            [
                "#C9A227",
                "麦金"
            ],
            [
                "#D97426",
                "橙"
            ],
            [
                "#6B4A8C",
                "紫"
            ],
            [
                "#4E6B3A",
                "暗绿"
            ],
            [
                "#3E7A9A",
                "天蓝"
            ],
            [
                "#8C6A3C",
                "土褐"
            ]
        ],
        "video": {
            "运动": "麦浪起伏、云层、尘埃在逆光里飘、衣服被风掀起",
            "运镜": "缓慢漂移横移、航拍掠过田野；可静止",
            "时长": "10 秒",
            "关键": "**光必须是魔幻时刻的低角度逆光**（长影 + 过曝天空 + 轮廓光）；正午硬光完全反"
        },
        "pitfalls": [
            "写 farm drama 会得到正午平光的乡村片 → 这部片的光**只在日出日落前后**",
            "人工补光会杀死自然光的层次",
            "高饱和正午调色是反的"
        ],
        "see_also": [
            "romanticism",
            "impressionism"
        ],
        "title_original": "Days of Heaven",
        "filmgrab": "https://film-grab.com/2010/07/21/days-of-heaven/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/terrence-malick/",
        "source": "curated"
    },
]
