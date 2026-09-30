# -*- coding: utf-8 -*-
"""fv_new_3.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "fincher-fight-club",
        "director_zh": "大卫·芬奇",
        "director_en": "David Fincher",
        "director_slug": "fincher",
        "title_zh": "搏击俱乐部",
        "title_en": "Fight Club",
        "year": 1999,
        "one_liner": "**冷绿与脏黄**——现代办公与地下空间的两种脏被分得很清，漂白般的低饱和把一切压扁。",
        "core": [
            "闪银漂白式的冷绿与脏黄，中间调被抽走，高光发白",
            "办公/公寓是冷绿荧光，地下空间是脏黄钨丝，两种脏度泾渭分明",
            "低照度与大量暗部，但光源永远「不够用」，人物半张脸在暗处",
            "手持与斯坦尼康混合，镜头不安分但始终精准"
        ],
        "visual": {
            "色彩": "冷绿、脏黄、灰白、沥青黑；几乎无饱和，整体病态",
            "光影": "荧光灯与钨丝灯为仅有的光源；大面积暗部，高光发白过曝，几乎无补光",
            "笔触": "（电影媒介）35mm 胶片 + 漂白工艺，粗颗粒，高对比",
            "构图": "偏心构图、被前景遮挡的取景、低角度压迫；不追求对称",
            "材质": "水泥、金属、塑料、废纸、油烟、旧家具、湿墙",
            "情绪": "躁狂、虚无、消耗感、暴力的疲惫"
        },
        "layers": {
            "style": "David Fincher Fight Club, bleach-bypass look, 1990s grime, cold green against dirty yellow, gritty low-key realism",
            "lighting": "fluorescent and tungsten only, extremely low key, large dead blacks, blown-out white highlights, no fill light, practical sources in frame",
            "color": "cold green, dirty yellow, soiled white, asphalt black; almost no saturation, sickly overall",
            "composition": "off-centre imbalance, framing obstructed by foreground, low angle with oppressive ceiling, cramped interiors",
            "medium": "35mm film with bleach bypass, coarse grain, high contrast, silver retained in highlights",
            "mood": "manic, nihilistic, depleted, weary violence",
            "camera": "handheld and steadicam mix, 35mm-ish, low and high angles, restless but precise"
        },
        "negative": "bright daylight, saturated colors, clean modern interior, warm cozy light, tripod stillness, lens flare, teal-orange grade",
        "palette": [
            [
                "#4A5240",
                "冷绿"
            ],
            [
                "#6B5E3A",
                "脏黄"
            ],
            [
                "#D8D4C4",
                "污白"
            ],
            [
                "#141511",
                "沥青黑"
            ],
            [
                "#8A7A5C",
                "旧家具褐"
            ],
            [
                "#9AA38C",
                "湿墙灰绿"
            ]
        ],
        "video": {
            "运动": "烟、雨、拳头与身体的冲击、荧光灯轻闪",
            "运镜": "手持跟拍、低角度推进、快速摇镜",
            "时长": "10 秒",
            "关键": "**漂白感（发白高光 + 死黑暗部 + 病态冷绿）**是命门；只写 dark 会得到普通暗调画面"
        },
        "pitfalls": [
            "只写 dark 不够 → 要写 bleach bypass / crushed blacks / blown highlights",
            "补光会把这部片变成普通室内剧，必须写 no fill light",
            "两组脏度（冷绿办公 / 脏黄地下）不能混成一个调子"
        ],
        "see_also": [
            "film-noir",
            "realism"
        ],
        "title_original": "Fight Club",
        "filmgrab": "https://film-grab.com/2010/11/14/fight-club/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/david-fincher/",
        "source": "curated"
    },
    {
        "slug": "fincher-zodiac",
        "director_zh": "大卫·芬奇",
        "director_en": "David Fincher",
        "director_slug": "fincher",
        "title_zh": "十二宫",
        "title_en": "Zodiac",
        "year": 2007,
        "one_liner": "**数字摄影的极干净冷调**——70 年代加州被拍成无光泽的灰，暗部干净得像被擦过。",
        "core": [
            "数字摄影的洁净感：无颗粒、无光晕，暗部极其干净",
            "整体冷灰偏绿，阳光段落也不温暖，只增加明度不增加暖度",
            "大量固定机位与大景别，信息靠构图而非剪辑给出",
            "夜间段落光源稀少，大片黑色里只有几个精确的亮点"
        ],
        "visual": {
            "色彩": "冷灰、青灰、米灰、暗绿；极低饱和，几乎无暖色",
            "光影": "日光被压成中性灰；夜间极少光源，大面积黑，高光克制不过曝",
            "笔触": "（电影媒介）数字摄影，无颗粒，锐利，柔和的高光滚降",
            "构图": "固定的宽景与对称的室内；人物常被放在画面深处",
            "材质": "旧车漆、报纸、办公家具、玻璃、木、地毯、雨",
            "情绪": "偏执、冷静、时间的消耗、不可解"
        },
        "layers": {
            "style": "David Fincher Zodiac, clean digital cinematography, 1970s California in flat grey, restrained procedural realism",
            "lighting": "daylight rendered neutral grey with no warmth, minimal night sources, huge black areas with a few precise points of light, restrained highlights",
            "color": "cool grey, slate, beige-grey, dark green; very low saturation with almost no warm tones",
            "composition": "locked-off wide shots, symmetrical interiors, figures deep in frame, information carried by staging not cutting",
            "medium": "digital cinema, no visible grain, sharp rendition, smooth highlight rolloff",
            "mood": "obsessive, clinical, time draining away, unsolvable",
            "camera": "locked-off wide, slow creep, deep focus, minimal handheld"
        },
        "negative": "film grain, warm golden hour, handheld chaos, saturated colors, lens flare, close-up shot-reverse-shot",
        "palette": [
            [
                "#5A6360",
                "冷灰"
            ],
            [
                "#6E7A78",
                "青灰"
            ],
            [
                "#A8A79E",
                "米灰"
            ],
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#14161A",
                "夜黑"
            ],
            [
                "#C4C0B4",
                "纸白"
            ]
        ],
        "video": {
            "运动": "雨、车流、人物在办公室里缓慢翻页、烟",
            "运镜": "固定机位为主，极慢的推近",
            "时长": "10 秒",
            "关键": "**必须干净**（无颗粒、暗部无噪）；加颗粒或暖调就变成了另一部芬奇片"
        },
        "pitfalls": [
            "写 70s vintage 会引入暖调与颗粒 → 这部片刻意反其道",
            "手持与快速剪辑是反的",
            "不加「无颗粒」会丢掉数字洁净感"
        ],
        "see_also": [
            "photorealism",
            "realism"
        ],
        "title_original": "Zodiac",
        "filmgrab": "https://film-grab.com/2010/06/23/zodiac/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/david-fincher/",
        "source": "curated"
    },
    {
        "slug": "fincher-the-social-network",
        "director_zh": "大卫·芬奇",
        "director_en": "David Fincher",
        "director_slug": "fincher",
        "title_zh": "社交网络",
        "title_en": "The Social Network",
        "year": 2010,
        "one_liner": "**冷绿与琥珀两种室内**——用极低照度的数字摄影把对话拍成暗调，桌面像舞台。",
        "core": [
            "两种室内色温：律所/宿舍的冷绿与餐厅/俱乐部的琥珀暖",
            "极低照度拍摄，人物脸上保留大片暗部，只有轮廓与眼窝被照到",
            "固定的中景与桌面俯拍交替，把对话戏拍成棋局",
            "数字摄影的干净暗部，噪点极少，黑色纯净"
        ],
        "visual": {
            "色彩": "冷绿（荧光）与琥珀（钨丝）两套；低饱和，暗部偏绿或偏褐",
            "光影": "极低照度，侧光切出轮廓；背景常完全黑，人脸半明半暗",
            "笔触": "（电影媒介）数字摄影，锐利干净，无颗粒",
            "构图": "固定中景、桌面俯拍、偏心构图；人物常背对或侧对镜头",
            "材质": "玻璃、金属、酒液、纸、屏幕光、木桌、雨夜玻璃",
            "情绪": "冷峻、机敏、孤独、聪明带来的孤立"
        },
        "layers": {
            "style": "David Fincher The Social Network, low-light digital, cold green versus amber interiors, dialogue staged as chess",
            "lighting": "extremely low key with side light carving profiles, backgrounds falling to pure black, faces half in shadow, no fill",
            "color": "cold green fluorescent and amber tungsten as two separate registers; low saturation with shadows tinted green or brown",
            "composition": "locked-off medium shots alternating with overhead desk framings, off-centre figures, subjects often in profile or from behind",
            "medium": "digital cinema, sharp and clean, minimal noise, pure blacks",
            "mood": "cold, sharp, lonely, isolated by intelligence",
            "camera": "locked-off medium, slow push, overhead desk shot, no handheld"
        },
        "negative": "flat even lighting, warm cozy ambience, handheld, saturated colors, bright backgrounds, film grain",
        "palette": [
            [
                "#2E4A3E",
                "冷绿"
            ],
            [
                "#8A5A2B",
                "琥珀"
            ],
            [
                "#141618",
                "纯黑"
            ],
            [
                "#6E7A72",
                "灰绿"
            ],
            [
                "#C4A87A",
                "酒液金"
            ],
            [
                "#3A4550",
                "雨夜蓝灰"
            ]
        ],
        "video": {
            "运动": "极少：手指敲键盘、酒杯轻晃、雨打在玻璃上、人物微微前倾",
            "运镜": "固定机位、极慢推近",
            "时长": "10 秒",
            "关键": "**背景要黑、脸要半明半暗**；把光补平就变成了普通的律政剧"
        },
        "pitfalls": [
            "写 warm 会丢掉冷绿那一半",
            "补光与提亮背景是反的（这部片靠黑背景造孤岛）",
            "手持不适合它的固定机位语法"
        ],
        "see_also": [
            "precisionism",
            "minimalism-art"
        ],
        "title_original": "The Social Network",
        "filmgrab": "https://film-grab.com/2013/10/28/the-social-network/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/david-fincher/",
        "source": "curated"
    },
    {
        "slug": "villeneuve-arrival",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "降临",
        "title_en": "Arrival",
        "year": 2016,
        "one_liner": "**把外星接触拍成天气**——雾、灰绿与竖构图，巨物沉默地悬在低云下。",
        "core": [
            "竖构图与仰视：飞船与雾墙被拍成垂直的体量，人站在下方",
            "整体灰绿低饱和，光线永远是阴天的散射",
            "雾与潮湿空气承担体积感，光没有明确来源",
            "室内是冷白荧光与灰绿墙面，室外是灰绿天光"
        ],
        "visual": {
            "色彩": "灰绿、青灰、米白、暗褐；极低饱和，几乎无暖色",
            "光影": "阴天散射光；雾中无明确光源方向，光从四面八方来",
            "笔触": "（电影媒介）数字摄影，柔和的暗部，轻微颗粒",
            "构图": "竖构图与仰视、大面积天空与雾、人物在画面下缘",
            "材质": "雾、湿草、混凝土、玻璃、金属、雨、羊毛",
            "情绪": "肃穆、哀伤、宿命、理解的重量"
        },
        "layers": {
            "style": "Denis Villeneuve Arrival, volumetric fog and overcast grey-green, monumental vertical scale, quiet science fiction",
            "lighting": "diffuse overcast light with no defined direction, fog acting as the light diffuser, soft shadowless volume, low contrast",
            "color": "grey-green, slate, off-white, dark brown; extremely low saturation with almost no warm tones",
            "composition": "vertical framing and upward angles, large sky and fog masses, small figures low in frame, monolithic silhouettes",
            "medium": "digital cinema, soft shadows, subtle grain, muted tonality",
            "mood": "solemn, mournful, fated, the weight of understanding",
            "camera": "slow push in, low angle looking up, static wide, no handheld"
        },
        "negative": "lens flare, saturated colors, warm sunlight, handheld, cgi spectacle, bright blue sky, fast cutting",
        "palette": [
            [
                "#6E7A6E",
                "雾灰绿"
            ],
            [
                "#8C9490",
                "青灰"
            ],
            [
                "#C4C0B4",
                "米白"
            ],
            [
                "#4A4238",
                "暗褐"
            ],
            [
                "#2E3634",
                "暗墨绿"
            ],
            [
                "#A8AEA4",
                "湿草灰"
            ]
        ],
        "video": {
            "运动": "雾缓慢流动、草被风压弯、雨丝、飞船表面无动",
            "运镜": "极慢推进或静止；仰视固定",
            "时长": "10 秒",
            "关键": "**雾必须占大面积且光无方向**；加光束或阳光就变成了普通科幻片"
        },
        "pitfalls": [
            "写 sci-fi 会得到飞船特效片 → 要写 fog, overcast, no defined light source",
            "仰视竖构图是它的语法，横构图会失去巨物感",
            "高饱和与暖光是反的"
        ],
        "see_also": [
            "surrealism",
            "minimalism-art"
        ],
        "title_original": "Arrival",
        "filmgrab": "https://film-grab.com/2019/06/28/arrival/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/denis-villeneuve/",
        "source": "curated"
    },
    {
        "slug": "villeneuve-sicario",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "边境杀手",
        "title_en": "Sicario",
        "year": 2015,
        "one_liner": "**黄昏的热噪声与夜视绿**——Deakins 用两种色温各承担一半的紧张。",
        "core": [
            "黄昏段落被橙金与热噪声统治，天空占大面积",
            "夜视段落是单色绿 + 白色热点，画面颗粒粗糙，质感与前面完全不同",
            "大量航拍与高位俯视，把人物压成地貌上的小点",
            "剪影与逆光：人物常背光成黑色轮廓贴在亮背景前"
        ],
        "visual": {
            "色彩": "黄昏橙金与土褐；夜视段为单色荧光绿",
            "光影": "黄昏逆光与低角度阳光；夜视段为红外绿 + 高光溢出，几乎无中间调",
            "笔触": "（电影媒介）数字摄影；夜视段有强烈的噪点与扫描感",
            "构图": "航拍高位俯视、宽银幕横向、人物小且偏置；剪影构图",
            "材质": "沙、尘、混凝土、铁网、车漆、夜视设备、烟雾",
            "情绪": "冷硬、紧张、道德沉没、无力"
        },
        "layers": {
            "style": "Denis Villeneuve Sicario, Roger Deakins, dusk thermal haze, monochrome night-vision green, wide aerial surveillance",
            "lighting": "dusk backlight with low sun and atmospheric haze; night-vision sequences in single-channel green with blown highlights and no midtones",
            "color": "orange-gold and earth brown at dusk, monochrome phosphor green at night; low saturation in daylight, zero colour in night vision",
            "composition": "high aerial wide shots, widescreen horizontals, small off-centre figures, silhouettes against bright sky",
            "medium": "digital cinema; heavy grain and scan texture in the night-vision passages",
            "mood": "hard, tense, moral sinking, powerless",
            "camera": "aerial high wide, slow push, static surveillance framing"
        },
        "negative": "saturated colors, warm cozy interior, handheld intimacy, lens flare, bright flat daylight, teal-orange grade",
        "palette": [
            [
                "#C97A2B",
                "黄昏橙"
            ],
            [
                "#8A6A3E",
                "土褐"
            ],
            [
                "#3E5A3A",
                "夜视绿"
            ],
            [
                "#B8E0A8",
                "夜视高光"
            ],
            [
                "#4A4E52",
                "混凝土灰"
            ],
            [
                "#1A1E20",
                "暗部黑"
            ]
        ],
        "video": {
            "运动": "尘土在光里飘、车队行进、夜视中的缓慢移动光点",
            "运镜": "航拍高位、缓慢横移、监视式固定",
            "时长": "10 秒",
            "关键": "**两种色温必须分镜使用**（黄昏橙 / 夜视绿），混在一起就丢了结构；夜视段要有噪点"
        },
        "pitfalls": [
            "写 thriller 会得到普通犯罪片 → 要写 dusk backlight, thermal haze",
            "夜视绿是单色的，不是「绿色调的白昼」",
            "低角度亲密手持是反的（这部片是俯视与监视感）"
        ],
        "see_also": [
            "photorealism",
            "realism"
        ],
        "title_original": "Sicario",
        "filmgrab": "https://film-grab.com/2016/04/22/sicario/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/denis-villeneuve/",
        "source": "curated"
    },
    {
        "slug": "villeneuve-prisoners",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "囚徒",
        "title_en": "Prisoners",
        "year": 2013,
        "one_liner": "**永不停雨的灰绿小镇**——Deakins 用大头灯和雨把中景压成暗调。",
        "core": [
            "持续的雨与湿表面，光源永远被雨幕散射",
            "灰绿与蓝灰为底，暖色只在室内钨丝灯与车灯上出现，面积极小",
            "大面积暗部，人物常只有轮廓与一侧脸被照亮",
            "中景与固定机位为主，情绪靠等待与雨的持续"
        ],
        "visual": {
            "色彩": "灰绿、蓝灰、湿黑；低饱和，暖色仅点状",
            "光影": "雨天散射 + 车灯与大头灯；低照度，高光在湿面上碎开",
            "笔触": "（电影媒介）数字摄影，柔和暗部，雨幕颗粒",
            "构图": "固定中景、前景遮挡（树、车、雨帘）；对称的室内框景",
            "材质": "雨、湿沥青、树皮、铁、玻璃、泥、旧木",
            "情绪": "压抑、焦虑、道德困境、漫长的等待"
        },
        "layers": {
            "style": "Denis Villeneuve Prisoners, Roger Deakins, perpetual rain, grey-green suburban dread, low-key naturalism",
            "lighting": "rain-diffused daylight with headlight and flashlight accents, very low key, highlights shattering on wet surfaces, no fill",
            "color": "grey-green, blue-grey, wet black; low saturation with only point warm accents from tungsten and car lights",
            "composition": "locked-off medium shots, foreground occlusion by trees, cars and rain, symmetrical interior framings",
            "medium": "digital cinema, soft shadows, rain-textured grain",
            "mood": "oppressive, anxious, moral quagmire, long waiting",
            "camera": "locked-off medium, slow creep, occasional low angle, no handheld"
        },
        "negative": "dry sunny weather, saturated colors, handheld vérité, warm cozy lighting, bright flat exposure, lens flare",
        "palette": [
            [
                "#3E4A42",
                "灰绿"
            ],
            [
                "#4A5560",
                "蓝灰"
            ],
            [
                "#141618",
                "湿黑"
            ],
            [
                "#8A7A5C",
                "钨丝褐"
            ],
            [
                "#C4C8C0",
                "雨幕灰白"
            ],
            [
                "#2E3A32",
                "树影暗绿"
            ]
        ],
        "video": {
            "运动": "雨持续下落、水洼涟漪、车灯扫过、人物缓慢移动",
            "运镜": "固定机位、极慢推进",
            "时长": "10 秒",
            "关键": "**雨必须持续且湿面反光**；把雨去掉就变成一个普通的阴天小镇"
        },
        "pitfalls": [
            "写 thriller 不够 → 要写 perpetual rain, wet surface reflections",
            "晴天与高饱和是反的",
            "手持不适合它的固定机位语法"
        ],
        "see_also": [
            "realism",
            "film-noir"
        ],
        "title_original": "Prisoners",
        "filmgrab": "https://film-grab.com/2014/04/14/prisoners/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/denis-villeneuve/",
        "source": "curated"
    },
    {
        "slug": "bong-memories-of-murder",
        "director_zh": "奉俊昊",
        "director_en": "Bong Joon-ho",
        "director_slug": "bong-joon-ho",
        "title_zh": "杀人回忆",
        "title_en": "Memories of Murder",
        "year": 2003,
        "one_liner": "**土黄稻田与灰天**——韩国乡野被拍成压抑的色谱，尾声那次直视镜头是构图名场面。",
        "core": [
            "土黄、灰绿、泥褐构成乡野的色谱，天空永远阴沉",
            "田间、水渠、排水管是主要场景，泥与水反复出现",
            "构图常让大片空田占画面下半，人物被压在画面边缘",
            "尾声：人物正面直视镜头 —— 全片唯一一次打破第四面墙的构图"
        ],
        "visual": {
            "色彩": "土黄、灰绿、泥褐、阴天灰；低饱和，无鲜艳色",
            "光影": "阴天散射为主；夜间用单一手电或路灯，暗部大",
            "笔触": "（电影媒介）35mm 胶片，颗粒可见，色调偏脏",
            "构图": "大片空田与低地平线、排水管内的框中框、人物偏置于画面一缘",
            "材质": "泥、稻草、水、铁管、旧制服、塑料棚、雨",
            "情绪": "无解、疲惫、乡野的沉默、时代性的无能"
        },
        "layers": {
            "style": "Bong Joon-ho Memories of Murder, 35mm film, Korean rural palette, overcast procedural, muddy fields and drains",
            "lighting": "overcast diffuse daylight, single flashlight or street lamp at night, large dark areas, no fill, dirty tonality",
            "color": "earth yellow, grey-green, mud brown, overcast grey; low saturation with no bright accents",
            "composition": "wide empty fields with a low horizon, framing inside drainage pipes, figures pushed to the edge of frame, ",
            "medium": "35mm film, visible grain, dirty tonal rendition",
            "mood": "unsolved, exhausted, rural silence, generational impotence",
            "camera": "static wide, slow creep, occasional handheld in the chase, frontal direct address for the final shot"
        },
        "negative": "saturated colors, clean urban environment, bright sunny field, handheld chaos, modern digital sharpness",
        "palette": [
            [
                "#8A7A3C",
                "土黄"
            ],
            [
                "#5E6B4A",
                "灰绿"
            ],
            [
                "#6B4A32",
                "泥褐"
            ],
            [
                "#9AA3A0",
                "阴天灰"
            ],
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#C4BCA0",
                "干草米"
            ]
        ],
        "video": {
            "运动": "雨、泥水流动、稻穗被风压、人物在田埂上行走",
            "运镜": "固定宽景、缓慢横移；结尾可用正面直视",
            "时长": "10 秒",
            "关键": "**低地平线 + 大片空田 + 阴天散射**；写 clean 或 bright 会丢掉乡野的脏"
        },
        "pitfalls": [
            "写 crime thriller 会得到都市刑侦 → 这部片的特征是乡野的土黄",
            "高饱和与晴天是反的",
            "排水管/水渠的框中框是它的构图语法，不写会丢一半"
        ],
        "see_also": [
            "realism",
            "photorealism"
        ],
        "title_original": "Memories of Murder",
        "filmgrab": "https://film-grab.com/2025/06/05/memories-of-murder/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/joon-ho-bong/",
        "source": "curated"
    },
    {
        "slug": "bong-snowpiercer",
        "director_zh": "奉俊昊",
        "director_en": "Bong Joon-ho",
        "director_slug": "bong-joon-ho",
        "title_zh": "雪国列车",
        "title_en": "Snowpiercer",
        "year": 2013,
        "one_liner": "**一节车厢一套色彩系统**——横向推进的空间即阶级叙事，越往前越冷、越亮。",
        "core": [
            "每节车厢一套独立的色彩与材质系统：脏绿、橙黄、冷白、温室绿、蓝黑、纯白",
            "横向推进的镜头语言：人物始终从画面右向左或左向右穿行",
            "色温与照度沿车厢递变，用视觉直接编码阶级",
            "车厢内的对称纵深与窄画幅压迫感"
        ],
        "visual": {
            "色彩": "按车厢分区：尾车厢脏褐绿、中间橙黄与冷白、温室翠绿、车头纯白与冰蓝",
            "光影": "尾车厢低照度脏光；中间均匀实用光；车头高调纯白无影",
            "笔触": "（电影媒介）数字摄影，锐利，轻微颗粒；不同车厢质感有意不同",
            "构图": "车厢内的纵深透视、对称走道、横向推进；人物被窄画幅挤压",
            "材质": "锈铁、水泥、玻璃、植物、钢、塑料、雪、冰",
            "情绪": "暴烈的阶级愤怒、封闭的绝望、冷到骨头的秩序"
        },
        "layers": {
            "style": "Bong Joon-ho Snowpiercer, colour-coded train carriages, lateral forward staging, dystopian production design",
            "lighting": "registers change per carriage: low dirty light at the tail, even practical mid-train, high-key shadowless white at the front",
            "color": "tail: dirty brown-green; middle: orange-yellow and cool white; greenhouse: chlorophyll green; front: pure white and ice blue",
            "composition": "deep one-point perspective down the carriage, symmetrical aisles, lateral forward movement, cramped vertical confinement",
            "medium": "digital cinema, sharp, subtle grain varying by carriage",
            "mood": "violent class rage, sealed despair, order frozen to the bone",
            "camera": "lateral tracking down the carriage, one-point forward dolly, static symmetry"
        },
        "negative": "uniform colour grade, outdoor landscape, handheld chaos, pastel palette, naturalistic daylight",
        "palette": [
            [
                "#5E4A32",
                "尾车厢脏褐"
            ],
            [
                "#C97A2B",
                "中间橙黄"
            ],
            [
                "#D8DCDD",
                "冷白"
            ],
            [
                "#3E8C4A",
                "温室翠绿"
            ],
            [
                "#1E2A3A",
                "冰蓝黑"
            ],
            [
                "#F2F2F0",
                "车头纯白"
            ]
        ],
        "video": {
            "运动": "列车晃动、蒸汽喷出、人物横向穿行、雪花在车外飞过",
            "运镜": "横向跟拍、正面纵深推进",
            "时长": "10 秒",
            "关键": "**一个镜头一套色彩系统**（车厢即色板）；统一调色会把阶级编码抹平"
        },
        "pitfalls": [
            "写 sci-fi 会得到统一的冷蓝未来感 → 这部片是**多套**色彩系统",
            "横向推进是空间语法，静态构图会丢失运动感",
            "统一调色是最大的错"
        ],
        "see_also": [
            "cyberpunk",
            "precisionism"
        ],
        "title_original": "Snowpiercer",
        "filmgrab": "https://film-grab.com/2020/01/08/snowpiercer/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/joon-ho-bong/",
        "source": "curated"
    },
    {
        "slug": "park-chan-wook-oldboy",
        "director_zh": "朴赞郁",
        "director_en": "Park Chan-wook",
        "director_slug": "park-chan-wook",
        "title_zh": "老男孩",
        "title_en": "Oldboy",
        "year": 2003,
        "one_liner": "**高饱和绿与紫的对撞**——长镜横移的走廊打斗，韩式暴力美学的高峰。",
        "core": [
            "绿与紫的病态对撞，配合橙黄的钨丝，饱和度被刻意推高",
            "走廊打斗：一条横向长镜，人物在画面里横向流动，不切",
            "对称构图与正面机位频繁出现，暴力被摆在画面正中",
            "室内狭窄、光源杂乱但有方向，暗部保留饱和色"
        ],
        "visual": {
            "色彩": "荧光绿、紫、橙黄、暗红；高饱和，色相对撞明显",
            "光影": "实用光源（荧光管、钨丝、霓虹）；中低照度，高光偏色",
            "笔触": "（电影媒介）35mm 胶片，色彩浓烈，颗粒可见",
            "构图": "横向长镜、对称正面、狭窄室内的框景；人物居中",
            "材质": "瓷砖、荧光管、金属、血、旧墙纸、水、木",
            "情绪": "暴烈、荒诞、黑色幽默、被设计好的宿命"
        },
        "layers": {
            "style": "Park Chan-wook Oldboy, saturated green and violet clash, lateral single-take corridor fight, Korean revenge aesthetic",
            "lighting": "practical fluorescent, tungsten and neon, medium-low key with colour-cast highlights, no clean white",
            "color": "fluorescent green, violet, orange-yellow, dark red; deliberately high saturation with clashing hues",
            "composition": "lateral long take across the frame, symmetrical frontal staging, cramped interior framing, centred figures",
            "medium": "35mm film, rich colour, visible grain",
            "mood": "violent, absurd, blackly comic, a designed fate",
            "camera": "lateral tracking single take, frontal symmetry, static medium, no handheld shake"
        },
        "negative": "low saturation, naturalistic daylight, handheld chaos, clean modern interior, teal-orange grade, desaturated earth tones",
        "palette": [
            [
                "#3EA84A",
                "荧光绿"
            ],
            [
                "#6B3A8C",
                "紫"
            ],
            [
                "#D98A2B",
                "橙黄"
            ],
            [
                "#8C1F1F",
                "暗红"
            ],
            [
                "#1A1E1A",
                "暗部黑"
            ],
            [
                "#C4BCA8",
                "旧墙米"
            ]
        ],
        "video": {
            "运动": "人物横向移动、血溅、荧光管轻闪、水滴",
            "运镜": "横向长镜跟拍、正面固定",
            "时长": "10 秒",
            "关键": "**绿与紫必须对撞且高饱和**；降饱和会把它变成普通犯罪片"
        },
        "pitfalls": [
            "写 revenge thriller 会得到低饱和冷调 → 这部片的签名是**高饱和撞色**",
            "走廊打斗是一条长镜，写 fast cutting 是反的",
            "自然光是反的"
        ],
        "see_also": [
            "pop-art",
            "expressionism"
        ],
        "title_original": "Oldboy",
        "filmgrab": "https://film-grab.com/2014/02/28/oldboy/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/chan-wook-park/",
        "source": "curated"
    },
    {
        "slug": "park-chan-wook-the-handmaiden",
        "director_zh": "朴赞郁",
        "director_en": "Park Chan-wook",
        "director_slug": "park-chan-wook",
        "title_zh": "小姐",
        "title_en": "The Handmaiden",
        "year": 2016,
        "one_liner": "**深绿与金的对峙**——日据宅邸的对称构图与镜面分割讲双重叙事。",
        "core": [
            "宅邸的深绿、赭金、暗红构成等级化的色彩系统",
            "对称构图与镜面/门窗分割：同一画面里两个叙事层并存",
            "室内以窗光与烛光为主，暗部保留饱和的绿与红",
            "室外是雾、苔、雨与深绿植被，与室内的金红形成内外对峙"
        ],
        "visual": {
            "色彩": "深绿、赭金、暗红、墨黑；高饱和但压暗，色相精致",
            "光影": "窗光与烛光的暖点光源；大面积暗部，绿调阴影",
            "笔触": "（电影媒介）数字摄影，柔和高光，轻微颗粒；布料的柔边",
            "构图": "严格对称、镜面与门窗分割、框中框；人物居中",
            "材质": "丝绸、纸门、木、铜器、烛蜡、雨、苔藓、玻璃",
            "情绪": "情欲的张力、欺瞒、冷艳、被困住"
        },
        "layers": {
            "style": "Park Chan-wook The Handmaiden, symmetrical period interiors, mirror and doorframe division, deep green and gold, Japanese-occupied Korea",
            "lighting": "window light and candle warm points, large dark areas, green-tinted shadows, soft veil of light through screens",
            "color": "deep green, ochre gold, dark crimson, ink black; high saturation but low brightness with refined hues",
            "composition": "strict symmetry, division by mirror and doorframe, frame within frame, centred figures, layered planes",
            "medium": "digital cinema, soft highlights, subtle grain, soft textile edges",
            "mood": "erotic tension, deception, cold elegance, entrapment",
            "camera": "static symmetrical wide, slow push, mirror framing, no handheld"
        },
        "negative": "handheld, desaturated palette, modern interior, harsh daylight, asymmetric chaos, cgi spectacle",
        "palette": [
            [
                "#1F3B2C",
                "深绿"
            ],
            [
                "#A8843C",
                "赭金"
            ],
            [
                "#6B1F1A",
                "暗红"
            ],
            [
                "#141210",
                "墨黑"
            ],
            [
                "#8A9A7A",
                "苔绿"
            ],
            [
                "#E0D2B4",
                "纸门米"
            ]
        ],
        "video": {
            "运动": "烛火摇曳、帘幕轻动、雨落、人物极缓慢的动作",
            "运镜": "固定对称、极慢推进、镜面构图",
            "时长": "10 秒",
            "关键": "**对称 + 深绿对赭金 + 镜面分割**；手持或降饱和都会破坏它的骨架"
        },
        "pitfalls": [
            "写 period drama 会得到普通年代剧 → 对称与镜面分割是它的叙事装置",
            "自然光与手持是反的",
            "深绿不能写成亮绿：它是压暗的"
        ],
        "see_also": [
            "baroque",
            "precisionism"
        ],
        "title_original": "The Handmaiden",
        "filmgrab": "https://film-grab.com/2020/01/28/the-handmaiden/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/chan-wook-park/",
        "source": "curated"
    },
]
