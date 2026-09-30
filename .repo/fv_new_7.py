# -*- coding: utf-8 -*-
"""fv_new_7.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "carpenter-halloween",
        "director_zh": "约翰·卡朋特",
        "director_en": "John Carpenter",
        "director_slug": "carpenter",
        "title_zh": "月光光心慌慌",
        "title_en": "Halloween",
        "year": 1978,
        "one_liner": "**宽银幕里的蓝色夜与空街**——把「画框边缘」变成恐怖装置，白天越像日常越可怕。",
        "core": [
            "宽银幕（2.35:1）里的蓝色夜景与空旷街道，人物常被放在画框一侧",
            "恐怖来自画框边缘与景深深处，不来自光",
            "白天是明媚的郊区日常（绿草坪、白墙），与夜里形成反差",
            "大量主观/长焦视点，观众被迫成为窥视者"
        ],
        "visual": {
            "色彩": "夜：蓝、灰蓝、暗绿；白天：饱和的草坪绿与白墙；两极对照",
            "光影": "夜间蓝色环境光 + 单点暖灯；白天为高调日光，平而亮",
            "笔触": "（电影媒介）35mm 宽银幕彩色胶片，颗粒可见",
            "构图": "宽银幕横向、人物偏置于画框一侧、长焦压缩的纵深；空街与门口",
            "材质": "草地、白墙、树叶、玻璃、旧车、万圣节装饰、雨",
            "情绪": "被窥视的不安、郊区日常里的空洞、缓慢逼近的恐惧"
        },
        "layers": {
            "style": "John Carpenter Halloween, 2.35:1 widescreen, blue suburban night, empty streets, dread from the frame edge",
            "lighting": "blue ambient night light with isolated warm lamps, high-key flat daylight for the day scenes, no dramatic horror lighting",
            "color": "night: blue, grey-blue, dark green; day: saturated lawn green and white walls; the two poles contrast sharply",
            "composition": "widescreen horizontals, subject pushed to one side, telephoto depth compression, empty streets and doorways, negative space at the frame edge",
            "medium": "35mm widescreen colour film, visible grain",
            "mood": "voyeuristic unease, suburban emptiness, slow approaching dread",
            "camera": "steadicam long take, telephoto observation, static wide, POV framing"
        },
        "negative": "gore close-ups, jump-cut scares, saturated red lighting, handheld chaos, cgi, cluttered composition",
        "palette": [
            [
                "#2E4A6B",
                "夜蓝"
            ],
            [
                "#5A6B7A",
                "灰蓝"
            ],
            [
                "#2E5A32",
                "草坪绿"
            ],
            [
                "#F2F2F0",
                "白墙"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#C97A2B",
                "单点暖灯"
            ]
        ],
        "video": {
            "运动": "树影晃动、窗帘轻动、人物在空街上缓慢行走、落叶",
            "运镜": "斯坦尼康长镜跟随、长焦远观、固定宽景",
            "时长": "10 秒",
            "关键": "**蓝色夜 + 宽银幕空街 + 画框边缘的空**；用红光或血浆特写就不是卡朋特"
        },
        "pitfalls": [
            "写 slasher 会得到血浆恐怖片 → 这部片的恐怖是**空间的空与画框的边缘**",
            "红光与特写吓人法是反的",
            "白天的郊区日常必须明亮，否则失去反差"
        ],
        "see_also": [
            "photorealism",
            "minimalism-art"
        ],
        "title_original": "Halloween",
        "filmgrab": "https://film-grab.com/2010/09/01/halloween/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/john-carpenter/",
        "source": "curated"
    },
    {
        "slug": "friedkin-the-exorcist",
        "director_zh": "威廉·弗莱德金",
        "director_en": "William Friedkin",
        "director_slug": "friedkin",
        "title_zh": "驱魔人",
        "title_en": "The Exorcist",
        "year": 1973,
        "one_liner": "**冷灰蓝的卧室与单一光源**——恐怖发生在最普通的居室照明下，越平常越致命。",
        "core": [
            "卧室是全片的主场景：冷灰蓝墙面 + 单只台灯/窗光",
            "光刻意平常：日光灯、台灯、窗外灰光，没有恐怖片式的打光",
            "构图规整，人物常被放在床边、门口等日常位置",
            "冷暖两套：室内冷灰蓝，室外阴天灰褐"
        ],
        "visual": {
            "色彩": "冷灰蓝、米灰、暗褐、污白；低饱和，几乎无暖色",
            "光影": "单一光源（台灯、窗、走廊灯），大面积暗部但保留细节；无戏剧性打光",
            "笔触": "（电影媒介）35mm 胶片，颗粒可见，色调平实",
            "构图": "规整的室内中景、门口与床边的框中框；固定机位为主",
            "材质": "木床、墙纸、地毯、玻璃、金属医疗器具、布、雪花",
            "情绪": "日常里的邪恶、寒冷、医疗式的冷静、缓慢逼近"
        },
        "layers": {
            "style": "William Friedkin The Exorcist, 1970s naturalistic horror, cold grey-blue bedroom interiors, ordinary domestic light",
            "lighting": "single practical source (bedside lamp, window, hall light) with large but detailed shadows, deliberately un-stylised and everyday",
            "color": "cold grey-blue, beige grey, dark brown, soiled white; low saturation with almost no warm tones",
            "composition": "tidy interior medium shots, framing at doorways and bedside, mostly locked-off camera",
            "medium": "35mm film, visible grain, plain tonality",
            "mood": "evil inside the everyday, cold, clinical, slow approach",
            "camera": "locked-off medium, slow push, static wide, no handheld"
        },
        "negative": "dramatic horror lighting, saturated red, handheld chaos, jump cuts, cgi, gothic sets",
        "palette": [
            [
                "#3E4A56",
                "冷灰蓝"
            ],
            [
                "#8C8C86",
                "米灰"
            ],
            [
                "#4A4238",
                "暗褐"
            ],
            [
                "#C4C0B4",
                "污白"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#6B6459",
                "墙纸褐灰"
            ]
        ],
        "video": {
            "运动": "窗帘轻动、台灯微闪、雪花飘落、人物静卧",
            "运镜": "固定机位、极慢推进",
            "时长": "10 秒",
            "关键": "**光要平常到没有风格**（台灯/窗光）；加戏剧打光就变成普通恐怖片"
        },
        "pitfalls": [
            "写 horror 会得到哥特式打光 → 这部片的恐怖恰恰来自**日常照明**",
            "红光与烟雾吓人法是反的",
            "低饱和冷灰蓝是它的底色"
        ],
        "see_also": [
            "realism",
            "photorealism"
        ],
        "title_original": "The Exorcist",
        "filmgrab": "https://film-grab.com/2013/08/19/the-exorcist/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/william-friedkin/",
        "source": "curated"
    },
    {
        "slug": "ridley-scott-alien",
        "director_zh": "雷德利·斯科特",
        "director_en": "Ridley Scott",
        "director_slug": "ridley-scott",
        "title_zh": "异形",
        "title_en": "Alien",
        "year": 1979,
        "one_liner": "**工业蒸汽与频闪**——把飞船内部拍成有湿度的厂房，光永远不够用。",
        "core": [
            "飞船内部是工业化的：管道、格栅、蒸汽、冷凝水，没有一块光滑面板",
            "光源是频闪灯、手电、屏幕与警示灯，永远不足且闪烁",
            "大量暗部与烟雾，人物常只剩轮廓",
            "构图用窄长走廊与管道纵深，压迫感来自空间的拥挤而非空旷"
        ],
        "visual": {
            "色彩": "暗绿、钢灰、琥珀警示灯、冷白屏幕光；低饱和且脏",
            "光影": "多光源但都弱：频闪、手电、屏幕、警示灯；烟雾与蒸汽散射，大面积暗部",
            "笔触": "（电影媒介）35mm 胶片，颗粒明显，暗部有噪",
            "构图": "窄长走廊纵深、管道框景、人物被结构遮挡；低角度仰视管道",
            "材质": "金属格栅、管道、冷凝水、蒸汽、塑料、皮革、玻璃",
            "情绪": "幽闭、工业化寒冷、未知逼近的恐惧"
        },
        "layers": {
            "style": "Ridley Scott Alien, industrial sci-fi interior, wet pipes and steam, flashing practical lights, claustrophobic corridor depth",
            "lighting": "multiple weak practical sources (strobes, torches, screens, warning lamps) scattered through smoke and steam, huge dark areas, nothing evenly lit",
            "color": "dark green, steel grey, amber warning light, cold screen white; low saturation and dirty",
            "composition": "narrow corridor depth, framing through pipes and grating, figures blocked by structure, low upward angles",
            "medium": "35mm film, pronounced grain, noisy shadows",
            "mood": "claustrophobic, industrial cold, dread of the unknown",
            "camera": "slow creep through corridors, low angle, handheld accents, static wide"
        },
        "negative": "clean sci-fi surfaces, even bright lighting, saturated colours, wide open spaces, modern minimal future",
        "palette": [
            [
                "#2E4A3A",
                "暗绿"
            ],
            [
                "#5A6570",
                "钢灰"
            ],
            [
                "#C97A2B",
                "警示琥珀"
            ],
            [
                "#C4C8C9",
                "屏幕冷白"
            ],
            [
                "#0F1210",
                "暗部黑"
            ],
            [
                "#6B6459",
                "锈褐"
            ]
        ],
        "video": {
            "运动": "蒸汽喷出、水滴、频闪灯闪、人物在走廊里缓慢移动",
            "运镜": "缓慢推进穿过走廊、低角度仰视",
            "时长": "10 秒",
            "关键": "**湿的工业表面 + 微弱多源灯 + 蒸汽**；干净明亮的未来感是完全反的"
        },
        "pitfalls": [
            "写 sci-fi 会得到干净明亮的未来舱 → 这部片的飞船是**湿的厂房**",
            "均匀照明是反的",
            "高饱和与光滑面板会毁掉它"
        ],
        "see_also": [
            "cyberpunk",
            "minimalism-art"
        ],
        "title_original": "Alien",
        "filmgrab": "https://film-grab.com/2013/07/24/alien/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ridley-scott/",
        "source": "curated"
    },
    {
        "slug": "ridley-scott-blade-runner",
        "director_zh": "雷德利·斯科特",
        "director_en": "Ridley Scott",
        "director_slug": "ridley-scott",
        "title_zh": "银翼杀手",
        "title_en": "Blade Runner",
        "year": 1982,
        "one_liner": "**烟、雨、霓虹与金字塔光束**——赛博朋克视觉的定义者，光从巨构建筑里倾泻下来。",
        "core": [
            "巨型建筑的侧面射出的巨大光束（金字塔式），照亮烟雾与雨",
            "永不停雨的夜城：湿面反射 + 霓虹招牌 + 烟雾",
            "内部空间是装饰艺术与未来主义的混合：暖金、木、几何装饰",
            "冷暖两套：街道冷蓝青绿，室内暖金褐"
        ],
        "visual": {
            "色彩": "冷蓝、青绿（街）对暖金、褐、红（室内）；高饱和但压暗",
            "光影": "巨大侧向光束穿过烟雾（体积光）；霓虹作实用光源；湿面反射提亮暗部",
            "笔触": "（电影媒介）35mm 胶片，颗粒明显，光晕与雾气重",
            "构图": "巨物与极小人物并列、纵向光束、纵深街道；大量烟雾遮挡远景",
            "材质": "雨、湿沥青、霓虹、金属、木材、玻璃、烟、塑料",
            "情绪": "孤独、末世都市、人造生命的哀伤"
        },
        "layers": {
            "style": "Ridley Scott Blade Runner, cyberpunk definition, enormous light shafts through smoke, perpetual rain, art-deco futurism",
            "lighting": "huge lateral light beams cutting through smoke and rain producing volumetric shafts, neon practicals, wet surfaces bouncing light into shadows",
            "color": "cool blue and cyan-green for the streets against warm gold, brown and red for the interiors; saturated but dark",
            "composition": "monumental architecture with tiny figures, vertical light shafts, deep street perspective, heavy smoke veiling the distance",
            "medium": "35mm film, pronounced grain, heavy halation and atmospheric haze",
            "mood": "lonely, end-of-world urban, grief of artificial life",
            "camera": "slow lateral drift, low angle up into light shafts, static monumental wide"
        },
        "negative": "clear dry air, daylight, clean modern surfaces, sparse composition, no atmosphere, flat lighting",
        "palette": [
            [
                "#1E3A4C",
                "夜街冷蓝"
            ],
            [
                "#2B6B6B",
                "青绿"
            ],
            [
                "#A8843C",
                "室内暖金"
            ],
            [
                "#6B4A2B",
                "木褐"
            ],
            [
                "#B03A2B",
                "霓虹红"
            ],
            [
                "#8C9490",
                "烟雾灰"
            ]
        ],
        "video": {
            "运动": "雨落、烟雾翻滚、霓虹闪烁、光束里的尘埃",
            "运镜": "缓慢横移、低角度仰拍光束、纵深推进",
            "时长": "10 秒",
            "关键": "**巨大光束 + 烟雨 + 湿面反射**三件套；去掉烟雾就没有体积光"
        },
        "pitfalls": [
            "写 cyberpunk 会得到蓝紫霓虹 + 无烟的都市 → 体积光靠烟雾实现，不能省",
            "干燥清洁的环境是反的",
            "室内外两套色温（冷街 / 暖室内）别混"
        ],
        "see_also": [
            "cyberpunk",
            "art-deco"
        ],
        "title_original": "Blade Runner",
        "filmgrab": "https://film-grab.com/2010/06/23/blade-runner/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ridley-scott/",
        "source": "curated"
    },
    {
        "slug": "ridley-scott-legend",
        "director_zh": "雷德利·斯科特",
        "director_en": "Ridley Scott",
        "director_slug": "ridley-scott",
        "title_zh": "诡秘怪谈",
        "title_en": "Legend",
        "year": 1985,
        "one_liner": "**雾、金粉与森林绿**——童话布景的密度与光斑，每一帧都像被撒了金粉。",
        "core": [
            "森林与洞穴的手工布景：苔藓、树根、水池，密度极高",
            "大量雾、金粉、光斑与逆光；光源常被雾散射成光晕",
            "色彩是高饱和的童话色：翠绿、金、深红、白",
            "构图为古典童话式：人物在布景中居中，周围是装饰性的自然细节"
        ],
        "visual": {
            "色彩": "翠绿、金、深红、白、暗褐；高饱和的童话色板",
            "光影": "雾中散射光 + 逆光光斑；金粉与尘埃在光里可见，暗部偏暖",
            "笔触": "（电影媒介）35mm 胶片，柔焦与光晕，颗粒细",
            "构图": "中心构图、装饰性的自然细节包围主体；纵深由雾与树根制造",
            "材质": "苔藓、树根、水、羽毛、丝绒、金粉、蜡、冰",
            "情绪": "童话的惊奇、光明对黑暗、被金粉笼罩的梦幻"
        },
        "layers": {
            "style": "Ridley Scott Legend, hand-built fairy-tale forest, drifting mist and gold dust, high-saturation storybook palette",
            "lighting": "mist-diffused light with strong backlight and bokeh, visible gold dust and motes in the beams, warm-tinted shadows",
            "color": "emerald green, gold, deep crimson, white, dark brown; saturated storybook palette",
            "composition": "centred subjects surrounded by dense decorative natural detail, depth built from mist and roots",
            "medium": "35mm film, soft focus and halation, fine grain",
            "mood": "fairy-tale wonder, light against dark, dreamlike gold haze",
            "camera": "slow push through foliage, static centred wide, gentle crane"
        },
        "negative": "sparse composition, desaturated palette, modern surfaces, handheld, documentary light, clean digital",
        "palette": [
            [
                "#2E7A3A",
                "翠绿"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#8C1F1F",
                "深红"
            ],
            [
                "#F2F2F0",
                "白"
            ],
            [
                "#4A3A2A",
                "暗褐"
            ],
            [
                "#8FA35A",
                "苔绿"
            ]
        ],
        "video": {
            "运动": "雾流动、金粉飘落、树叶微动、水面反光",
            "运镜": "缓慢穿过枝叶推进、中心静止、轻微升降",
            "时长": "10 秒",
            "关键": "**雾 + 逆光金粉 + 高饱和童话色**；把布景拍稀或降饱和就变成普通奇幻片"
        },
        "pitfalls": [
            "写 fantasy 会得到现代 CG 奇幻 → 这部片是**手工布景 + 雾 + 金粉**",
            "稀疏构图与它相反",
            "低饱和会杀死童话色板"
        ],
        "see_also": [
            "romanticism",
            "surrealism"
        ],
        "title_original": "Legend",
        "filmgrab": "https://film-grab.com/2023/11/21/legend/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ridley-scott/",
        "source": "curated"
    },
    {
        "slug": "ridley-scott-thelma-and-louise",
        "director_zh": "雷德利·斯科特",
        "director_en": "Ridley Scott",
        "director_slug": "ridley-scott",
        "title_zh": "末路狂花",
        "title_en": "Thelma & Louise",
        "year": 1991,
        "one_liner": "**沙漠的橙与天空的蓝切成横向色带**——末帧的过曝是全片唯一的高调。",
        "core": [
            "公路与沙漠被切成横向色带：橙土、蓝空、灰路",
            "整体高调明亮，阳光充足，与通常的公路犯罪片不同",
            "人物与车在宽广的风景里很小，构图开阔",
            "末帧突然过曝发白，是全片唯一的高调极端，作为情绪高潮"
        ],
        "visual": {
            "色彩": "沙漠橙、天蓝、路面灰、车漆色；高调明快，饱和度中高",
            "光影": "正午硬日光与长影；开阔无遮挡，人物脸上有硬阴影",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩明快，颗粒细",
            "构图": "横向色带（土/路/天）、大远景、人物与车在画面下三分之一",
            "材质": "沙、沥青、金属车漆、牛仔布、尘土、天空",
            "情绪": "自由、辽阔、逃逸的亢奋、注定的悲壮"
        },
        "layers": {
            "style": "Ridley Scott Thelma & Louise, sunlit desert road movie, horizontal colour bands, high-key American landscape",
            "lighting": "hard midday sun with long shadows, open unshaded landscape, hard facial shadows, bright and saturated",
            "color": "desert orange, sky blue, road grey, car paint; high key with moderate-to-high saturation",
            "composition": "horizontal bands of earth, road and sky, very wide establishing shots, figures and car in the lower third",
            "medium": "35mm colour film, bright tonality, fine grain",
            "mood": "free, vast, exhilarated escape, fated tragedy",
            "camera": "aerial wide, lateral tracking with the car, static monumental landscape"
        },
        "negative": "dark low-key grade, claustrophobic framing, handheld shake, desaturated palette, night interiors",
        "palette": [
            [
                "#C97A2B",
                "沙漠橙"
            ],
            [
                "#3E7A9A",
                "天蓝"
            ],
            [
                "#8C8C86",
                "路面灰"
            ],
            [
                "#B03A2B",
                "车漆红"
            ],
            [
                "#E8E0CC",
                "尘土白"
            ],
            [
                "#2E4A5A",
                "远景蓝灰"
            ]
        ],
        "video": {
            "运动": "车在公路上行驶、尘土飞扬、风吹头发、云的阴影掠过地面",
            "运镜": "航拍远景、横向跟车、固定大远景",
            "时长": "10 秒",
            "关键": "**高调明亮的横向色带**；把它拍暗就变成了普通的黑色公路片"
        },
        "pitfalls": [
            "写 crime road movie 会得到暗调犯罪片 → 这部片是**明亮高调**的",
            "窄构图会失去沙漠的辽阔",
            "手持摇晃不是它的语法"
        ],
        "see_also": [
            "photorealism",
            "romanticism"
        ],
        "title_original": "Thelma & Louise",
        "filmgrab": "https://film-grab.com/2023/11/22/thelma-louise/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ridley-scott/",
        "source": "curated"
    },
    {
        "slug": "villeneuve-enemy",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "宿敌",
        "title_en": "Enemy",
        "year": 2013,
        "one_liner": "**整片琥珀黄滤镜**——把多伦多拍成一个没有蓝色的城市，黄得像被泡过。",
        "core": [
            "整片被琥珀/芥末黄滤镜覆盖，几乎不出现蓝色",
            "城市被拍成低对比的黄褐色调，人物与建筑同色",
            "构图常把巨大的建筑或雕塑压在画面上方，人物很小",
            "室内也是同一套黄调，色温统一得近乎病态"
        ],
        "visual": {
            "色彩": "琥珀、芥末黄、土褐、暗黄绿；整体单色化，无蓝色",
            "光影": "低对比散射光；无明确方向，影子浅，黄调均匀",
            "笔触": "（电影媒介）数字摄影，柔和的暗部，轻微颗粒",
            "构图": "巨物（高楼、蜘蛛雕塑）压在上方，人物小且偏置；对称的室内",
            "材质": "混凝土、玻璃幕墙、旧墙纸、金属、玻璃、灰尘、黄雾",
            "情绪": "身份的重影、压抑、被同一性吞没的不安"
        },
        "layers": {
            "style": "Denis Villeneuve Enemy, monochrome amber-yellow grade, oppressive urban sameness, doppelganger unease",
            "lighting": "low-contrast diffuse light with no defined direction, shallow shadows, the amber cast applied uniformly",
            "color": "amber, mustard yellow, earth brown, dark yellow-green; effectively monochrome with no blue anywhere",
            "composition": "monumental structures looming overhead with tiny figures, off-centre subjects, symmetrical interiors",
            "medium": "digital cinema, soft shadows, subtle grain",
            "mood": "doubled identity, oppression, unease of sameness",
            "camera": "static wide with looming architecture, slow push, symmetrical framing"
        },
        "negative": "blue tones, cool colour grade, high contrast dramatic lighting, handheld, saturated multi-hue palette",
        "palette": [
            [
                "#C9A227",
                "琥珀"
            ],
            [
                "#A8843C",
                "芥末黄"
            ],
            [
                "#6B5B45",
                "土褐"
            ],
            [
                "#4A4A2E",
                "暗黄绿"
            ],
            [
                "#141410",
                "暗部黑"
            ],
            [
                "#C4B48C",
                "黄雾米"
            ]
        ],
        "video": {
            "运动": "黄雾缓慢移动、灰尘浮动、人物静止凝视、窗帘轻动",
            "运镜": "固定宽景、缓慢推进",
            "时长": "10 秒",
            "关键": "**整片单一琥珀调、不许出现蓝色**；一旦加入冷色就失去了它的压迫感"
        },
        "pitfalls": [
            "写 thriller 会得到普通冷调悬疑片 → 这部片是**单色琥珀**",
            "蓝色与冷调是反的",
            "巨物压顶的构图是它的语法"
        ],
        "see_also": [
            "surrealism",
            "precisionism"
        ],
        "title_original": "Enemy",
        "filmgrab": "https://film-grab.com/2015/06/24/enemy/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/denis-villeneuve/",
        "source": "curated"
    },
    {
        "slug": "satoshi-kon-tokyo-godfathers",
        "director_zh": "今敏",
        "director_en": "Satoshi Kon",
        "director_slug": "satoshi-kon",
        "title_zh": "东京教父",
        "title_en": "Tokyo Godfathers",
        "year": 2003,
        "one_liner": "**冬夜东京的冷蓝与暖灯**——今敏最写实的一部，暖光只出现在人情处。",
        "core": [
            "冬夜东京的冷蓝灰与便利店/居酒屋的暖灯形成分区",
            "背景是写实的城市细节（招牌、垃圾堆、地铁），密度极高",
            "构图把三个主角常常并列在画面里，形成横向的群像",
            "光线平实，接近实景，少见今敏惯用的超现实调度"
        ],
        "visual": {
            "色彩": "冬夜冷蓝灰、暖灯橙黄、霓虹杂色；对比明确",
            "光影": "夜间实用光源（路灯、招牌、店内灯）；暗部偏冷，暖调集中在室内",
            "笔触": "（动画媒介）赛璐珞 + 数字绘景，背景写实细节密集",
            "构图": "横向群像、城市街景纵深；人物常被环境包围",
            "材质": "雪、垃圾袋、玻璃、金属、纸张、霓虹、旧衣",
            "情绪": "寒冷中的温情、偶然的善意、城市边缘的孤独"
        },
        "layers": {
            "style": "Satoshi Kon Tokyo Godfathers, realistic winter Tokyo, dense painted city detail, warm light against cold night, cel animation",
            "lighting": "night practical sources (street lamps, signage, shop interiors), cold blue-grey shadows with warm pools indoors, naturalistic",
            "color": "winter blue-grey night, warm lamp orange-yellow, mixed neon; clear contrast between registers",
            "composition": "horizontal group staging, deep city streets, figures surrounded by environment detail",
            "medium": "cel animation with digital compositing, densely detailed painted backgrounds",
            "mood": "warmth inside cold, accidental kindness, marginal urban loneliness",
            "camera": "static wide, lateral tracking through streets, occasional overhead"
        },
        "negative": "surreal scene transformation, flat sparse background, 3d cgi, saturated fantasy palette, abstract staging",
        "palette": [
            [
                "#2E4A6B",
                "冬夜冷蓝"
            ],
            [
                "#C97A2B",
                "暖灯橙"
            ],
            [
                "#5A6570",
                "灰蓝"
            ],
            [
                "#C42B72",
                "霓虹粉"
            ],
            [
                "#E8E0CC",
                "雪光米"
            ],
            [
                "#141618",
                "暗部黑"
            ]
        ],
        "video": {
            "运动": "雪落、霓虹闪烁、垃圾被风吹动、人物在街上缓慢行走",
            "运镜": "横向跟拍、固定宽景、缓慢推进",
            "时长": "10 秒",
            "关键": "**冷蓝冬夜 + 暖灯分区 + 写实的城市密度**；今敏在这部片里刻意不玩场景置换"
        },
        "pitfalls": [
            "别把《红辣椒》的超现实置换套到这部片 —— 它是**写实**的",
            "背景要密（城市细节），写 sparse 就跑偏",
            "冷暖分区（室内暖 / 室外冷）是它的语法"
        ],
        "see_also": [
            "anime-cel",
            "realism"
        ],
        "title_original": "Tokyo Godfathers",
        "filmgrab": "https://film-grab.com/2024/05/19/tokyo-godfathers/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/satoshi-kon/",
        "source": "curated"
    },
    {
        "slug": "kurosawa-ikiru",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "生之欲",
        "title_en": "Ikiru",
        "year": 1952,
        "one_liner": "**官僚办公室的灰与雨夜的霓虹**——黑白里的空间把「活着」拍成一个公文堆。",
        "core": [
            "办公室是文件堆与低矮天花板构成的灰色迷宫，人物被文件埋住",
            "雨夜段落是霓虹与湿街的高对比，与白日的灰成对照",
            "构图常把人物压在文件/楼梯/人群的几何里",
            "秋千与雪等意象段落刻意简化背景，近乎舞台"
        ],
        "visual": {
            "色彩": "黑白；白日为平坦的灰，雨夜为高对比的黑与霓虹亮斑",
            "光影": "白日为均匀的顶光（办公室荧光感）；雨夜为霓虹与湿面反射",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒可见，层次丰富",
            "构图": "文件堆的框中框、楼梯纵深的对称、人群横向铺陈；静物段落近舞台",
            "材质": "纸、木桌、玻璃、雨、霓虹、雪、秋千铁链、布",
            "情绪": "官僚的麻木、迟来的觉醒、雨夜的孤独、雪中的宁静"
        },
        "layers": {
            "style": "Kurosawa Ikiru, 35mm black and white, bureaucratic grey interiors, neon rain, late-life awakening, expressionist staging",
            "lighting": "flat even overhead light for the office scenes; high-contrast neon and wet reflection for the rain night; minimalist staged light for the snow scenes",
            "color": "black and white; flat grey by day, hard black and bright neon pools at night",
            "composition": "framing through stacks of paper, symmetrical staircase depth, crowds staged horizontally, near-theatrical simplicity in the snowy section",
            "medium": "35mm black-and-white film, visible grain, rich tonal range",
            "mood": "bureaucratic numbness, belated awakening, rain-night loneliness, snow-lit calm",
            "camera": "static wide, slow dolly, symmetrical depth, no handheld"
        },
        "negative": "saturated colour, handheld, close-up only coverage, modern clean interiors, flat uniform exposure",
        "palette": [
            [
                "#3E3A34",
                "办公室灰"
            ],
            [
                "#8C8C86",
                "纸灰"
            ],
            [
                "#0A0A0A",
                "夜黑"
            ],
            [
                "#E8E8E4",
                "霓虹白"
            ],
            [
                "#5E5A54",
                "湿街灰"
            ],
            [
                "#B8B4A8",
                "雪白"
            ]
        ],
        "video": {
            "运动": "雨落、文件翻动、秋千轻晃、雪花飘落",
            "运镜": "固定对称、缓慢横移",
            "时长": "10 秒",
            "关键": "**办公室的平灰与雨夜的高对比并置**；把两段统一曝光就丢掉了对照"
        },
        "pitfalls": [
            "写 drama 会得到常规的社会剧 → 这部片的两段光是刻意对撞的",
            "手持与特写式覆盖不适合它的对称语法",
            "文件堆的框中框是构图语法"
        ],
        "see_also": [
            "realism",
            "expressionism"
        ],
        "title_original": "Ikiru",
        "filmgrab": "https://film-grab.com/2016/07/30/ikiru/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/akira-kurosawa/",
        "source": "curated"
    },
    {
        "slug": "kurosawa-high-and-low",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "天国与地狱",
        "title_en": "High and Low",
        "year": 1963,
        "one_liner": "**一间客厅里的一群人 vs 一整个城市**——宽银幕黑白把阶级拍成两种构图密度。",
        "core": [
            "前半段几乎全在一间客厅内：横向群像、对称、宽银幕压缩",
            "后半段是城市追踪：拥挤的街道、列车、夜总会，密度骤增",
            "黑白高对比，室内用大量暗部，室外用阳光的硬影",
            "构图中「高低」是字面的：高处的宅邸与低处的坡下街区"
        ],
        "visual": {
            "色彩": "黑白；室内深灰到黑，室外硬日光与深影",
            "光影": "室内侧窗光与大面积暗部；室外正午硬光与浓黑阴影",
            "笔触": "（电影媒介）35mm 黑白宽银幕胶片，颗粒明显",
            "构图": "宽银幕横向群像、对称室内、拥挤的街道纵深；构图密度前后对比强烈",
            "材质": "皮革、木、玻璃、列车、金属、布、烟、旧墙",
            "情绪": "阶级的对峙、紧张、道德压力、都市的窒息"
        },
        "layers": {
            "style": "Kurosawa High and Low, 2.35:1 black and white, single-room group staging then city-density tracking, hard midday shadows",
            "lighting": "interior side window light with large dark areas; exterior hard midday sun with deep black shadows; no diffusion",
            "color": "black and white; deep grey to black indoors, hard sun and black shadow outdoors",
            "composition": "widescreen horizontal group staging, symmetrical interiors, crowded city depth, dramatic change in composition density between halves",
            "medium": "35mm black-and-white widescreen film, pronounced grain",
            "mood": "class confrontation, tension, moral pressure, urban suffocation",
            "camera": "static wide, tight horizontal group shot, tracking through crowds, no handheld"
        },
        "negative": "flat even lighting, soft diffusion, handheld, narrow framing, modern digital clean",
        "palette": [
            [
                "#0A0A0A",
                "室内黑"
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
                "日光白"
            ],
            [
                "#5E5A54",
                "街道灰"
            ],
            [
                "#6B5B45",
                "皮革褐"
            ]
        ],
        "video": {
            "运动": "列车呼啸、人群流动、烟升起、人物在客厅里静坐",
            "运镜": "固定横向群像、跟拍穿过街道",
            "时长": "10 秒",
            "关键": "**前半一间房、后半一座城**；两段的构图密度差是这部片的结构"
        },
        "pitfalls": [
            "写 crime thriller 会得到常规警匪片 → 它的结构是**构图密度对撞**",
            "柔光与手持是反的",
            "窄画幅会失去横向群像的意义"
        ],
        "see_also": [
            "realism",
            "precisionism"
        ],
        "title_original": "High and Low",
        "filmgrab": "https://film-grab.com/2017/02/04/high-and-low/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/akira-kurosawa/",
        "source": "curated"
    },
    {
        "slug": "kobayashi-kwaidan",
        "director_zh": "小林正树",
        "director_en": "Masaki Kobayashi",
        "director_slug": "masaki-kobayashi",
        "title_zh": "怪谈",
        "title_en": "Kwaidan",
        "year": 1964,
        "one_liner": "**绘景式的舞台感**——雾、血红的天空与平涂背景，把怪谈拍成会动的浮世绘。",
        "core": [
            "背景是刻意的人造绘景（平涂天空、画出来的雾），舞台感明确",
            "宽银幕里做平面化构图，像卷轴画或绘马",
            "色彩浓烈且不自然：血红、漆黑、金、雪白，色块面积大",
            "构图常把人物放在画面正中或一角，周围是大面积色块"
        ],
        "visual": {
            "色彩": "血红、漆黑、金、雪白、靛蓝；高饱和且刻意不真实",
            "光影": "舞台式平光与光源明确的局部光；无自然衰减，暗部平涂",
            "笔触": "（电影媒介）35mm 彩色宽银幕胶片，色彩极浓，颗粒可见",
            "构图": "宽银幕平面化构图、绘景背景、中心或偏置人物；对称与仪式感",
            "材质": "纸门、雪、血、木、丝、绘景布、水、雾",
            "情绪": "幽玄、恐怖的诗意、宿命、被绘景包围的奇异"
        },
        "layers": {
            "style": "Kobayashi Kwaidan, 2.35:1 colour, painted studio backdrops, flat graphic staging, saturated Japanese ghost-tale palette",
            "lighting": "theatrical flat light with deliberate local sources, no natural falloff, flat painted shadows",
            "color": "blood red, lacquer black, gold, snow white, indigo; highly saturated and intentionally unreal",
            "composition": "widescreen flat graphic staging against painted backdrops, centred or offset figures, symmetry and ritual arrangement",
            "medium": "35mm colour widescreen film, extremely saturated, visible grain",
            "mood": "ethereal, poetic horror, fatalism, strangeness enclosed by painted worlds",
            "camera": "static flat wide, slow lateral drift, occasional sudden scale shift"
        },
        "negative": "naturalistic location shooting, documentary light, handheld, desaturated palette, realistic depth",
        "palette": [
            [
                "#8C1F1F",
                "血红"
            ],
            [
                "#0A0A0A",
                "漆黑"
            ],
            [
                "#C9A227",
                "金"
            ],
            [
                "#F2F2F0",
                "雪白"
            ],
            [
                "#1F3A6E",
                "靛蓝"
            ],
            [
                "#6B1F1A",
                "暗红"
            ]
        ],
        "video": {
            "运动": "雪落、烟升起、水面波纹、人物极缓慢地移动",
            "运镜": "固定平面宽景、缓慢横移",
            "时长": "10 秒",
            "关键": "**背景必须是绘景（平涂、不真实）+ 大面积纯色块**；写实外景会毁掉它的舞台感"
        },
        "pitfalls": [
            "写 horror 会得到写实恐怖片 → 这部片的背景是**人造绘景**",
            "自然光与写实深度是反的",
            "低饱和会丢掉血红的冲击"
        ],
        "see_also": [
            "ukiyo-e",
            "expressionism"
        ],
        "title_original": "Kwaidan",
        "filmgrab": "https://film-grab.com/2016/10/05/kwaidan/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/masaki-kobayashi/",
        "source": "curated"
    },
    {
        "slug": "bong-the-host",
        "director_zh": "奉俊昊",
        "director_en": "Bong Joon-ho",
        "director_slug": "bong-joon-ho",
        "title_zh": "汉江怪物",
        "title_en": "The Host",
        "year": 2006,
        "one_liner": "**汉江边的阴天绿与黄色小吃摊**——怪物出现在最平常的日光下，恐怖不靠黑暗。",
        "core": [
            "怪物在明亮的白天出现：阴天散射光下的河滩与人群",
            "汉江边的绿灰与小吃摊的黄是主色，日常感极强",
            "家庭成员的横向群像构图，人物常被放在拥挤的环境里",
            "室内（小吃摊、医院）用荧光灯与暖灯混合，空间狭窄"
        ],
        "visual": {
            "色彩": "河滩绿灰、芥末黄（帐篷）、冷白荧光、浑浊的江水褐绿",
            "光影": "阴天散射为主；室内荧光与暖灯混合；无恐怖片的暗调打光",
            "笔触": "（电影媒介）数字摄影，锐利，轻微颗粒",
            "构图": "横向群像、拥挤的河滩、狭窄室内的框中框；家庭成员的并列",
            "材质": "江水、泥、塑料帐篷、金属、玻璃、荧光灯、旧家具",
            "情绪": "失控的日常、家庭的笨拙、荒诞里的悲怆"
        },
        "layers": {
            "style": "Bong Joon-ho The Host, daylight creature feature, Han river green-grey, family group staging, mundane horror",
            "lighting": "overcast diffuse daylight for the riverbank; mixed fluorescent and warm practicals indoors; deliberately no horror-style darkness",
            "color": "riverbank grey-green, mustard tent yellow, cool fluorescent white, muddy brown-green water",
            "composition": "horizontal family group staging, crowded riverbank, cramped interior framing, figures side by side",
            "medium": "digital cinema, sharp, subtle grain",
            "mood": "runaway everyday life, clumsy family, absurdity inside grief",
            "camera": "static wide, lateral tracking with the crowd, occasional handheld panic"
        },
        "negative": "dark horror lighting, night-only setting, saturated red gore, cgi spectacle showcase, desaturated palette",
        "palette": [
            [
                "#5E6B4A",
                "河滩绿灰"
            ],
            [
                "#C9A227",
                "帐篷芥末黄"
            ],
            [
                "#DCE0D8",
                "荧光冷白"
            ],
            [
                "#6B5B45",
                "江水褐"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#8C9490",
                "阴天灰"
            ]
        ],
        "video": {
            "运动": "江水翻涌、人群奔逃、雨、怪物甩动",
            "运镜": "横向跟拍、固定宽景、拥挤中的手持",
            "时长": "10 秒",
            "关键": "**怪物出现在明亮的白天**；把它放进黑暗就变成普通怪兽片"
        },
        "pitfalls": [
            "写 monster movie 会得到暗调怪兽片 → 这部片的恐怖发生在**日光下的日常**",
            "高饱和红血与暗调打光是反的",
            "家庭横向群像是它的构图语法"
        ],
        "see_also": [
            "realism",
            "photorealism"
        ],
        "title_original": "The Host",
        "filmgrab": "https://film-grab.com/2026/07/10/the-host/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/joon-ho-bong/",
        "source": "curated"
    },
    {
        "slug": "bong-mother",
        "director_zh": "奉俊昊",
        "director_en": "Bong Joon-ho",
        "director_slug": "bong-joon-ho",
        "title_zh": "母亲",
        "title_en": "Mother",
        "year": 2009,
        "one_liner": "**草药的绿与大地的黄**——奉俊昊把田野拍成一种药理般的颜色，光总在人物的背后。",
        "core": [
            "田野的草绿与土地的黄褐是主色，与小镇的灰构成对照",
            "光常从人物背后或侧后来，脸部半明半暗",
            "构图把母亲与儿子放在画面的两端或对角，制造距离",
            "大量静止的中远景，情绪靠等待与剪草药的动作"
        ],
        "visual": {
            "色彩": "草药绿、土黄、灰蓝、暗褐；低饱和自然调",
            "光影": "自然侧逆光与阴天散射；暗部保留细节，无明显戏剧光",
            "笔触": "（电影媒介）数字摄影，柔和，轻微颗粒",
            "构图": "静止中远景、人物分列画面两端、田野的横向铺陈",
            "材质": "草药、土、镰刀、旧衣、金属、玻璃、雨、血",
            "情绪": "偏执的母爱、压抑、田野里的黑暗、宿命"
        },
        "layers": {
            "style": "Bong Joon-ho Mother, herb-green fields and earth yellow, backlit naturalism, quiet rural thriller",
            "lighting": "natural side and back light with overcast diffusion, detailed shadows, no dramatic key",
            "color": "herb green, earth yellow, grey-blue, dark brown; low saturation and natural",
            "composition": "static medium-long shots, mother and son at opposite ends of frame, wide horizontal fields",
            "medium": "digital cinema, soft, subtle grain",
            "mood": "obsessive mother love, repression, darkness in the fields, fatalism",
            "camera": "static medium-long, slow push, occasional handheld in the panic beats"
        },
        "negative": "dramatic lighting, saturated colours, cluttered urban scene, cgi, flat even exposure",
        "palette": [
            [
                "#4E6B3A",
                "草药绿"
            ],
            [
                "#A8843C",
                "土黄"
            ],
            [
                "#5A6B78",
                "灰蓝"
            ],
            [
                "#3E3A34",
                "暗褐"
            ],
            [
                "#C4C0B4",
                "干草米"
            ],
            [
                "#141618",
                "暗部黑"
            ]
        ],
        "video": {
            "运动": "草药被割、风穿过田野、雨、人物静止凝视",
            "运镜": "固定中远景、缓慢推进",
            "时长": "10 秒",
            "关键": "**自然侧逆光 + 低饱和草药绿/土黄**；把它拍成暗调惊悚就丢掉了田野的日常感"
        },
        "pitfalls": [
            "写 thriller 会得到暗调犯罪片 → 这部片的底色是**自然、明亮、低饱和**的田野",
            "戏剧打光是反的",
            "母亲与儿子分列画面两端的构图是它的语法"
        ],
        "see_also": [
            "realism",
            "photorealism"
        ],
        "title_original": "Mother",
        "filmgrab": "https://film-grab.com/2020/08/06/mother-2/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/joon-ho-bong/",
        "source": "curated"
    },
]
