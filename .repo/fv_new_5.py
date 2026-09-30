# -*- coding: utf-8 -*-
"""fv_new_5.py —— 新增完整片的七层数据。

数据性质与字段说明见 `fv_new_1.py` 顶部。
由 /tmp/mkbatch.py 生成，字段经 full() 校验（缺项会报错）。
"""

BATCH = [
    {
        "slug": "bergman-the-seventh-seal",
        "director_zh": "英格玛·伯格曼",
        "director_en": "Ingmar Bergman",
        "director_slug": "bergman",
        "title_zh": "第七封印",
        "title_en": "The Seventh Seal",
        "year": 1957,
        "one_liner": "**过曝天空下的高对比黑白**——把中世纪寓言拍成极简的明暗对照，死神是画面里的一个平面。",
        "core": [
            "过曝的天空（几乎纯白）与深黑的人物形成极简两级",
            "构图平面化：人物与死神并列站在空旷的海滩或林间空地",
            "黑白高对比但保留灰阶，云层是唯一的大面积中间调",
            "面孔特写频繁，脸被硬光切成明暗两半"
        ],
        "visual": {
            "色彩": "黑白；天空近纯白，暗部深黑，中间调集中在云与布料",
            "光影": "阴天散射与直射太阳混合；逆光让人物成剪影，面部特写用硬侧光",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，高光有溢出",
            "构图": "平面化构图、人物并列、空旷的海滩与林间空地；大量天空",
            "材质": "麻布、铁甲、木、沙、石、枯草、乌云、镰刀",
            "情绪": "肃穆、荒凉、宿命、寓言式的庄严"
        },
        "layers": {
            "style": "Ingmar Bergman The Seventh Seal, 35mm black and white, overexposed sky, planar staging, medieval allegory, hard chiaroscuro",
            "lighting": "blown-out sky against deep black figures, hard side light on faces splitting them into light and dark halves, overcast plus direct sun",
            "color": "black and white; near-white sky, deep black shadows, midtones concentrated in clouds and cloth",
            "composition": "flat planar staging, figures standing side by side in empty landscapes, low horizon with large sky, frequent face close-ups",
            "medium": "35mm black-and-white film, pronounced grain, clipping highlights",
            "mood": "solemn, desolate, fatalistic, allegorical grandeur",
            "camera": "static wide, slow track, direct close-up, no handheld"
        },
        "negative": "saturated color, soft even lighting, shallow depth of field, handheld, modern digital clean, warm tones",
        "palette": [
            [
                "#0A0A0A",
                "暗部黑"
            ],
            [
                "#E8E8E4",
                "过曝天空"
            ],
            [
                "#8C8C86",
                "云灰"
            ],
            [
                "#3E3A34",
                "麻布褐"
            ],
            [
                "#6E6E68",
                "石滩灰"
            ],
            [
                "#B8B4A8",
                "沙白"
            ]
        ],
        "video": {
            "运动": "云层流动、海浪、布袍被风掀起、人物静止不动",
            "运镜": "固定机位、缓慢横移；硬光不变",
            "时长": "10 秒",
            "关键": "**天空必须过曝发白**；把天空压暗就丢掉了这部片的极简两级"
        },
        "pitfalls": [
            "写 medieval 会得到暖调古装 → 它的天空是过曝的白",
            "柔和打光是反的（面部要硬侧光切半）",
            "彩色会直接毁掉它"
        ],
        "see_also": [
            "expressionism",
            "baroque"
        ],
        "title_original": "The Seventh Seal",
        "filmgrab": "https://film-grab.com/2013/02/26/the-seventh-seal/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ingmar-bergman/",
        "source": "curated"
    },
    {
        "slug": "bergman-persona",
        "director_zh": "英格玛·伯格曼",
        "director_en": "Ingmar Bergman",
        "director_slug": "bergman",
        "title_zh": "假面",
        "title_en": "Persona",
        "year": 1966,
        "one_liner": "**两张脸叠成一个**——Sven Nykvist 的柔光把皮肤拍成地形，脸是唯一的风景。",
        "core": [
            "极端正面特写：脸部充满画框，背景消失",
            "柔和的散射光让皮肤几乎没有硬阴影，明暗过渡极长",
            "两张脸的重叠/镜像构图（同一张脸的两半合成）",
            "高光的克制：脸是亮的，但绝不过曝；暗部干净"
        ],
        "visual": {
            "色彩": "黑白；脸部大片浅灰到中灰，背景压成深灰或纯黑",
            "光影": "Sven Nykvist 式柔散光：无方向感但有塑形，皮肤过渡极滑，无硬阴影",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，画面极其干净",
            "构图": "极端正面特写、面部对称、双脸叠合；背景消失或压黑",
            "材质": "皮肤、头发、亚麻、玻璃、水面、胶片本身",
            "情绪": "身份的溶解、内省、被观看、沉默的暴力"
        },
        "layers": {
            "style": "Ingmar Bergman Persona, Sven Nykvist soft light, extreme facial close-up, black and white, face as landscape",
            "lighting": "soft shadowless wrap light sculpting without direction, extremely smooth skin gradation, no hard shadows, clean deep backgrounds",
            "color": "black and white; face in broad pale to mid grey, background crushed to dark grey or black",
            "composition": "extreme frontal close-up filling the frame, facial symmetry, two faces fused or mirrored, no background",
            "medium": "35mm black-and-white film, fine grain, exceptionally clean image",
            "mood": "dissolving identity, introspection, being watched, silent violence",
            "camera": "static extreme close-up, no movement, occasional slow zoom"
        },
        "negative": "hard directional light, busy background, color, handheld, wide establishing shots, film grain heavy",
        "palette": [
            [
                "#E0DCD4",
                "肤色浅灰"
            ],
            [
                "#8C8880",
                "中灰"
            ],
            [
                "#3E3A38",
                "深灰"
            ],
            [
                "#0A0A0A",
                "背景黑"
            ],
            [
                "#B8B4AC",
                "亚麻浅灰"
            ],
            [
                "#5E5A56",
                "暗部灰"
            ]
        ],
        "video": {
            "运动": "几乎不动：眨眼、呼吸、发丝轻动、焦点的微小漂移",
            "运镜": "固定特写；不要移动",
            "时长": "10 秒",
            "关键": "**柔光无硬阴影 + 脸占满画框**；加硬光或拉远景就不是《假面》"
        },
        "pitfalls": [
            "硬方向光是反的（Nykvist 的柔光是这部片的签名）",
            "彩色或杂乱背景都不成立",
            "写 portrait 不够 → 要写 extreme close-up filling frame"
        ],
        "see_also": [
            "photorealism",
            "minimalism-art"
        ],
        "title_original": "Persona",
        "filmgrab": "https://film-grab.com/2014/04/22/persona/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ingmar-bergman/",
        "source": "curated"
    },
    {
        "slug": "bergman-wild-strawberries",
        "director_zh": "英格玛·伯格曼",
        "director_en": "Ingmar Bergman",
        "director_slug": "bergman",
        "title_zh": "野草莓",
        "title_en": "Wild Strawberries",
        "year": 1957,
        "one_liner": "**没有中间调的梦境**——过曝的白与深黑并置，回忆被拍成一种刺眼的亮。",
        "core": [
            "梦境段落过曝：天空与街道几乎全白，人物成黑色剪影",
            "现实段落灰阶平缓、柔和，与梦境的极简两级形成对照",
            "空街、无脸的行人、停摆的钟 —— 用构图与道具制造超现实",
            "面部特写用柔和侧光，保留皮肤层次"
        ],
        "visual": {
            "色彩": "黑白；梦境为过曝白 + 黑剪影，现实为丰富灰阶",
            "光影": "梦境：无方向的高强度散射（几乎无阴影）；现实：柔和侧光与窗光",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细；梦境段高光溢出明显",
            "构图": "空荡的街道纵深、正面特写、极简几何；梦境中人物成黑色块",
            "材质": "石街、木、帘、钟表、棺木、亚麻、旧家具",
            "情绪": "怀旧、恐惧、自省、时间的重量"
        },
        "layers": {
            "style": "Ingmar Bergman Wild Strawberries, black and white, overexposed dream sequences, empty streets, road-movie introspection",
            "lighting": "dreams: directionless high-intensity light with almost no shadow and clipped white; reality: soft side light and window light with full grey range",
            "color": "black and white; dreams are blown white with black silhouette forms, reality has a wide gentle grey scale",
            "composition": "empty receding streets, frontal close-up, minimal geometry, figures as black masses in the dream",
            "medium": "35mm black-and-white film, fine grain, strong highlight bloom in the dream",
            "mood": "nostalgic, fearful, self-examining, the weight of time",
            "camera": "static wide, slow dolly, direct close-up, no handheld"
        },
        "negative": "saturated color, uniform exposure across dream and reality, handheld, cluttered composition, modern digital look",
        "palette": [
            [
                "#E8E8E4",
                "梦境过曝白"
            ],
            [
                "#0A0A0A",
                "剪影黑"
            ],
            [
                "#8C8C86",
                "现实中灰"
            ],
            [
                "#3E3A34",
                "暗褐"
            ],
            [
                "#C4C0B4",
                "帘布米"
            ],
            [
                "#5E5A54",
                "石街灰"
            ]
        ],
        "video": {
            "运动": "极少的动作：钟摆停住、人物静止、烟升起",
            "运镜": "固定、缓慢推进",
            "时长": "10 秒",
            "关键": "**梦境要过曝、现实要有灰阶**，两段的曝光差是这部片的结构"
        },
        "pitfalls": [
            "把梦境与现实拍成同一个曝光就丢掉了对照",
            "写 surreal 会得到特效梦 → 它的超现实靠构图与过曝实现",
            "彩色是反的"
        ],
        "see_also": [
            "surrealism",
            "expressionism"
        ],
        "title_original": "Wild Strawberries",
        "filmgrab": "https://film-grab.com/2013/09/23/wild-strawberries/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/ingmar-bergman/",
        "source": "curated"
    },
    {
        "slug": "fellini-8-half",
        "director_zh": "费德里科·费里尼",
        "director_en": "Federico Fellini",
        "director_slug": "fellini",
        "title_zh": "八部半",
        "title_en": "8½",
        "year": 1963,
        "one_liner": "**黑白里的超现实群像**——梦境段过曝与深黑并置，现实段是明亮的平面灰。",
        "core": [
            "梦境/幻想段落：过曝高调 + 深黑剪影，人群被排成仪式化的队形",
            "现实段落：明亮的中灰调，构图开阔，人物在建筑与人群里穿行",
            "构图常把人物排成横向队列（浴场、车站、后宫幻想）",
            "光从上方或远处来，制造「被照亮的人群」效果"
        ],
        "visual": {
            "色彩": "黑白；幻想段近纯白 + 黑，现实段中灰为主",
            "光影": "幻想段无方向强光；现实段为日光与灯光的混合，柔和",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，层次丰富",
            "构图": "横向队列、开阔的平面构图、纵深人群；对称与仪式化排列",
            "材质": "白布、石阶、水、纸伞、旧衣、蒸汽、马戏道具",
            "情绪": "荒诞、自嘲、创作焦虑、梦与现实的滑动"
        },
        "layers": {
            "style": "Fellini 8½, 35mm black and white, surreal mass staging, overexposed fantasy sequences, Italian modernist cinema",
            "lighting": "fantasy: directionless intense light with blown whites and black silhouettes; reality: mixed daylight and practical with a broad grey range",
            "color": "black and white; near-white and black in the fantasies, mid-grey dominant in reality",
            "composition": "horizontal queues of people, wide flat staging, crowds receding in depth, symmetrical ritual arrangements",
            "medium": "35mm black-and-white film, pronounced grain, rich tonal range",
            "mood": "absurd, self-mocking, creative anxiety, sliding between dream and reality",
            "camera": "slow crane, lateral tracking across crowds, static wide, occasional handheld"
        },
        "negative": "saturated color, single-figure framing, tight close-up only, smooth even lighting, modern digital clean",
        "palette": [
            [
                "#E8E8E4",
                "幻想过曝白"
            ],
            [
                "#0A0A0A",
                "剪影黑"
            ],
            [
                "#8C8C86",
                "现实中灰"
            ],
            [
                "#4A4438",
                "旧衣褐"
            ],
            [
                "#C4C0B4",
                "石阶米"
            ],
            [
                "#5E5E58",
                "水汽灰"
            ]
        ],
        "video": {
            "运动": "人群缓慢移动、蒸汽上升、布幔被风掀起、纸伞旋转",
            "运镜": "缓慢横移、升镜、穿过人群的推进",
            "时长": "10 秒",
            "关键": "**人群要排成横向队列**（仪式化构图）；只拍单人特写就丢掉了费里尼"
        },
        "pitfalls": [
            "写 surreal 会堆特效 → 它的超现实来自构图与曝光",
            "特写不是它的语法，要写 crowds staged in rows",
            "彩色会直接破坏"
        ],
        "see_also": [
            "surrealism",
            "baroque"
        ],
        "title_original": "8½",
        "filmgrab": "https://film-grab.com/2014/10/10/8-12/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/federico-fellini/",
        "source": "curated"
    },
    {
        "slug": "fellini-la-dolce-vita",
        "director_zh": "费德里科·费里尼",
        "director_en": "Federico Fellini",
        "director_slug": "fellini",
        "title_zh": "甜蜜的生活",
        "title_en": "La Dolce Vita",
        "year": 1960,
        "one_liner": "**罗马夜里的强反差黑白**——喷泉与路灯把人物围在光环里，长夜是一串光斑。",
        "core": [
            "夜间段落用强反差黑白：路灯、车灯、喷泉成为高光孤岛",
            "大面积深黑中人物成剪影或被照亮一半",
            "白天的罗马是明亮的平面中灰，建筑与人群构成开阔构图",
            "镜头缓慢横移穿过夜club与广场，像一场不间断的巡游"
        ],
        "visual": {
            "色彩": "黑白；夜为深黑 + 强高光，白天为明亮中灰",
            "光影": "夜间单点强光（路灯/车灯）+ 大面积黑；白天为日光散射",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，高光有轻微溢出",
            "构图": "开阔的广场与街道、纵深人群、框中框（喷泉、车门、帽檐）",
            "材质": "石阶、水、喷泉、丝绸、旧车、报纸、灯罩",
            "情绪": "浮华、空虚、彻夜的无意义、被光照亮的孤独"
        },
        "layers": {
            "style": "Fellini La Dolce Vita, 35mm black and white, high-contrast Roman nights, long promenade camera, paparazzi-era glamour",
            "lighting": "night: single strong practical sources against large black; day: diffuse daylight with a flat mid-grey range",
            "color": "black and white; deep black with isolated highlights at night, bright mid-grey by day",
            "composition": "wide open squares and streets, crowds receding in depth, framing through fountains, car windows and hat brims",
            "medium": "35mm black-and-white film, fine grain, slight highlight bloom",
            "mood": "glamorous, hollow, all-night meaninglessness, loneliness lit up",
            "camera": "slow lateral promenade tracking, wide static, deep staging"
        },
        "negative": "saturated color, flat even night lighting, tight intimate framing, handheld, modern digital clean",
        "palette": [
            [
                "#0A0A0A",
                "夜黑"
            ],
            [
                "#E8E8E4",
                "路灯白"
            ],
            [
                "#8C8C86",
                "白天中灰"
            ],
            [
                "#C4C0B4",
                "石阶米"
            ],
            [
                "#5E5A54",
                "水光灰"
            ],
            [
                "#3E3A34",
                "暗褐"
            ]
        ],
        "video": {
            "运动": "喷泉水花、人群缓慢走动、车灯扫过、纸屑飘落",
            "运镜": "缓慢横移巡游、固定宽景",
            "时长": "10 秒",
            "关键": "**夜间孤立高光 + 大面积黑**；把夜景照亮就变成了普通的黑白都市片"
        },
        "pitfalls": [
            "夜间要敢于留黑（大面积死黑是特征）",
            "彩色与手持是反的",
            "特写不是它的语汇，广场与人群才是"
        ],
        "see_also": [
            "film-noir",
            "photorealism"
        ],
        "title_original": "La Dolce Vita",
        "filmgrab": "https://film-grab.com/2014/10/03/la-dolce-vita/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/federico-fellini/",
        "source": "curated"
    },
    {
        "slug": "antonioni-blow-up",
        "director_zh": "米开朗基罗·安东尼奥尼",
        "director_en": "Michelangelo Antonioni",
        "director_slug": "michelangelo-antonioni",
        "title_zh": "放大",
        "title_en": "Blow-Up",
        "year": 1966,
        "one_liner": "**60 年代伦敦的高调冷色**——草地绿与灰白建筑，构图里大量空与几何。",
        "core": [
            "高调冷色：白墙、灰混凝土、草地绿，几乎无暖色",
            "构图为几何化的空旷——大片空白与建筑边缘",
            "人物常被放在画面边缘或纵深里，与空间的面积不成比例",
            "公园段落是唯一的绿，与城市的灰白形成对照"
        ],
        "visual": {
            "色彩": "灰白、草绿、冷灰、少量红作点缀；高调低饱和偏冷",
            "光影": "阴天与建筑反射的散射光；均匀，影子浅",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩清淡，颗粒可见",
            "构图": "几何化的空旷构图、人物偏置、大面积建筑与空白",
            "材质": "混凝土、玻璃、草地、金属、印刷纸、胶片、螺旋桨",
            "情绪": "空洞、虚无、被放大的虚无、60 年代的倦怠"
        },
        "layers": {
            "style": "Antonioni Blow-Up, high-key cool 1960s London, geometric emptiness, muted modernist colour",
            "lighting": "overcast and architectural bounce giving even diffuse light with shallow shadows, no warm key",
            "color": "off-white, grass green, cool grey with small red accents; high key, low saturation, cool",
            "composition": "geometric emptiness, subject pushed to the edge or deep in frame, large areas of building and blank space",
            "medium": "35mm colour film, pale tonality, visible grain",
            "mood": "hollow, nihilistic, magnified meaninglessness, 1960s ennui",
            "camera": "static wide, slow zoom into grain, detached high angle"
        },
        "negative": "saturated warm colours, close intimate framing, handheld, dramatic lighting, cluttered composition",
        "palette": [
            [
                "#DCE0DC",
                "混凝土白"
            ],
            [
                "#6E8C5A",
                "草地绿"
            ],
            [
                "#A8AEA8",
                "冷灰"
            ],
            [
                "#B0241F",
                "点缀红"
            ],
            [
                "#C4C0B4",
                "纸米"
            ],
            [
                "#4A4E52",
                "金属灰"
            ]
        ],
        "video": {
            "运动": "树影晃动、草地起伏、放大机下的颗粒变化、螺旋桨旋转",
            "运镜": "缓慢变焦、固定宽景",
            "时长": "10 秒",
            "关键": "**高调冷色 + 几何化的空旷**；把画面塞满或加暖色都不成立"
        },
        "pitfalls": [
            "写 60s vintage 会引入暖黄滤镜，而它是冷的高调",
            "塞满构图与它的空旷语法相反",
            "手持是反的"
        ],
        "see_also": [
            "photorealism",
            "minimalism-art"
        ],
        "title_original": "Blow-Up",
        "filmgrab": "https://film-grab.com/2014/02/07/blow-up/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/michelangelo-antonioni/",
        "source": "curated"
    },
    {
        "slug": "antonioni-l-avventura",
        "director_zh": "米开朗基罗·安东尼奥尼",
        "director_en": "Michelangelo Antonioni",
        "director_slug": "michelangelo-antonioni",
        "title_zh": "奇遇",
        "title_en": "L'Avventura",
        "year": 1960,
        "one_liner": "**火山岩岛与灰海**——用大面积空白构图表现「人不见了」，消失比出现更有存在感。",
        "core": [
            "构图让「空」成为主角：人物消失后，镜头停在岩石与海面上",
            "黑白灰阶极丰富，海与天是连续的中灰，岩石是深灰",
            "火山岩岛与灰海构成荒凉的地形，人物在其中很小",
            "长镜与缓慢横移，视线在空间里游荡而非跟随人"
        ],
        "visual": {
            "色彩": "黑白；海天为中灰，岩石深灰，人物服装浅灰",
            "光影": "阴天散射与强烈的海面反射；无戏剧光，均匀且开阔",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，层次丰富",
            "构图": "大面积空白（海、天、岩）、人物小且偏置；全景为主",
            "材质": "火山岩、海、风、布、船、石墙、雾",
            "情绪": "虚空、焦虑的等待、被空间吞没的孤独"
        },
        "layers": {
            "style": "Antonioni L'Avventura, 35mm black and white, volcanic island and grey sea, composition of absence, modernist alienation",
            "lighting": "overcast diffuse with strong sea reflection, no dramatic source, even and wide, shallow shadows",
            "color": "black and white; sea and sky a continuous mid-grey, rock dark grey, clothing pale grey",
            "composition": "large empty areas of sea, sky and rock, small off-centre figures, wide establishing shots, camera lingering on absence",
            "medium": "35mm black-and-white film, fine grain, rich tonal range",
            "mood": "void, anxious waiting, loneliness swallowed by space",
            "camera": "slow pan across landscapes, long wide holds, no handheld"
        },
        "negative": "saturated color, close-up driven coverage, handheld, dramatic lighting, cluttered foreground",
        "palette": [
            [
                "#8C8C86",
                "海天中灰"
            ],
            [
                "#3E3E3A",
                "岩石深灰"
            ],
            [
                "#C4C0B4",
                "浅灰衣"
            ],
            [
                "#5E5E58",
                "石墙灰"
            ],
            [
                "#E8E8E4",
                "天光白"
            ],
            [
                "#6E6A60",
                "风蚀褐"
            ]
        ],
        "video": {
            "运动": "海浪、风、布被吹动、人物在岩石上缓慢移动",
            "运镜": "缓慢横移、固定全景",
            "时长": "10 秒",
            "关键": "**镜头要停在「人不在」的地方**；只跟人走会丢掉「消失」这个主题"
        },
        "pitfalls": [
            "写 mystery 会得到寻找失踪者的悬疑片 → 这部片的重点是空间本身",
            "彩色是反的",
            "特写与手持不适合它的宽阔语法"
        ],
        "see_also": [
            "minimalism-art",
            "realism"
        ],
        "title_original": "L'Avventura",
        "filmgrab": "https://film-grab.com/2014/03/25/lavventura/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/michelangelo-antonioni/",
        "source": "curated"
    },
    {
        "slug": "godard-contempt",
        "director_zh": "让-吕克·戈达尔",
        "director_en": "Jean-Luc Godard",
        "director_slug": "godard",
        "title_zh": "蔑视",
        "title_en": "Contempt",
        "year": 1963,
        "one_liner": "**红蓝黄原色块与地中海的蓝**——宽银幕被 Raoul Coutard 当成色板用。",
        "core": [
            "宽银幕（Franscope）被当成色板：红、蓝、黄的原色块大面积并置",
            "地中海蓝与白墙是环境的底色，红与黄在物件上爆发",
            "室内以白墙 + 单色家具构成平面色块，构图对称",
            "长镜与缓慢横移，把公寓、影院、海岛拍成舞台"
        ],
        "visual": {
            "色彩": "地中海蓝、白、正红、正黄、正蓝；高饱和，色块面积大且干净",
            "光影": "地中海硬日光与白墙反光；室内为均匀的散射光，影子短而硬",
            "笔触": "（电影媒介）35mm 彩色胶片（宽银幕），色彩浓烈，颗粒细",
            "构图": "对称的室内平面、宽银幕横向构图、色块分割画面",
            "材质": "白墙、红沙发、蓝海、黄椅、玻璃、石头、胶片设备",
            "情绪": "疲惫、疏离、创作的屈辱、美的重量"
        },
        "layers": {
            "style": "Godard Contempt, Raoul Coutard, Franscope widescreen, primary colour blocks, Mediterranean white and blue, modernist flat staging",
            "lighting": "hard Mediterranean sun with white-wall bounce, short hard shadows; interiors evenly diffuse with flat shadow",
            "color": "Mediterranean blue, white, primary red, primary yellow, primary blue; high saturation in large clean blocks",
            "composition": "symmetrical flat interiors, widescreen horizontals, the frame divided into colour blocks, slow staging",
            "medium": "35mm colour film in widescreen, rich saturation, fine grain",
            "mood": "weary, estranged, creative humiliation, the weight of beauty",
            "camera": "slow lateral tracking, static symmetrical wide, occasional slow zoom"
        },
        "negative": "desaturated palette, handheld, cluttered composition, naturalistic grey light, narrow framing",
        "palette": [
            [
                "#1F5A8C",
                "地中海蓝"
            ],
            [
                "#F2F2F0",
                "白墙"
            ],
            [
                "#B0241F",
                "正红"
            ],
            [
                "#D9A32B",
                "正黄"
            ],
            [
                "#1F3A6E",
                "正蓝"
            ],
            [
                "#C4BCA8",
                "石灰米"
            ]
        ],
        "video": {
            "运动": "海面波动、窗帘轻动、人物在色块间缓慢移动",
            "运镜": "缓慢横移、对称固定",
            "时长": "10 秒",
            "关键": "**原色块要大、要干净**（不混色）；把颜色调灰就变成普通 60 年代片"
        },
        "pitfalls": [
            "写 60s French film 会得到灰调新浪潮 → 这部片的颜色是高饱和原色块",
            "手持不适合它的对称舞台感",
            "窄画幅会失去色块分割的意义"
        ],
        "see_also": [
            "pop-art",
            "art-deco"
        ],
        "title_original": "Contempt",
        "filmgrab": "https://film-grab.com/2012/09/16/contempt-le-mepris/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/jean-luc-godard/",
        "source": "curated"
    },
    {
        "slug": "godard-pierrot-le-fou",
        "director_zh": "让-吕克·戈达尔",
        "director_en": "Jean-Luc Godard",
        "director_slug": "godard",
        "title_zh": "狂人皮埃罗",
        "title_en": "Pierrot le Fou",
        "year": 1965,
        "one_liner": "**原色当拼贴材料**——红蓝黄在宽银幕里被切成漫画分格，颜色自己会说话。",
        "core": [
            "原色（红、蓝、黄）大面积并置，像被剪贴上去的色纸",
            "构图常把人物与色块切成并列的平面，像漫画格或拼贴画",
            "南法的蓝与绿、室内的红与黄、夜里的蓝，色相按段落跳跃",
            "摄影机自由：横移、环形、突然的静止，运动带有游戏感"
        ],
        "visual": {
            "色彩": "正红、正蓝、正黄、南法蓝绿；高饱和，色相之间强对比",
            "光影": "日光硬光与室内均匀光；影子短，颜色不靠光影塑形",
            "笔触": "（电影媒介）35mm 彩色胶片（宽银幕），色彩浓烈刺眼",
            "构图": "平面化拼贴、漫画式分格、色块并列；人物常被放在色块边缘",
            "材质": "色纸、汽油桶、书、汽车、海、玻璃、布料",
            "情绪": "轻狂、暴力、游戏、浪漫的虚无"
        },
        "layers": {
            "style": "Godard Pierrot le Fou, primary colours as collage, widescreen flat planes, comic-strip framing, French New Wave",
            "lighting": "hard daylight and even interior light with short shadows; colour is carried by surfaces, not shaped by light",
            "color": "primary red, blue and yellow with southern French blue-green; high saturation with hard contrast between hues",
            "composition": "flat collage staging, comic-strip panels, colour blocks placed side by side, figures at the edge of colour fields",
            "medium": "35mm colour film in widescreen, harsh saturated colour",
            "mood": "flippant, violent, playful, romantic nihilism",
            "camera": "lateral tracking, sudden static holds, circular pans, handheld accents"
        },
        "negative": "desaturated palette, classical continuity coverage, static symmetrical staging, naturalistic soft light",
        "palette": [
            [
                "#B0241F",
                "正红"
            ],
            [
                "#1F3A6E",
                "正蓝"
            ],
            [
                "#D9A32B",
                "正黄"
            ],
            [
                "#1F6B7A",
                "南法蓝绿"
            ],
            [
                "#F2F2F0",
                "白"
            ],
            [
                "#141210",
                "暗部黑"
            ]
        ],
        "video": {
            "运动": "汽车行驶、海面、人物突然奔跑、色块在画框里跳动",
            "运镜": "横移、突然静止、环形摇镜",
            "时长": "10 秒",
            "关键": "**原色要像贴上去的纸**（平面、无渐变）；写 cinematic natural colour 就完全反了"
        },
        "pitfalls": [
            "自然写实的调色是反的",
            "古典连续性（正反打）不是它的语法",
            "低饱和会杀死拼贴感"
        ],
        "see_also": [
            "pop-art",
            "neo-pop"
        ],
        "title_original": "Pierrot le Fou",
        "filmgrab": "https://film-grab.com/2011/02/08/pierrot-le-fou-crazy-pete/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/jean-luc-godard/",
        "source": "curated"
    },
    {
        "slug": "melville-le-samourai",
        "director_zh": "让-皮埃尔·梅尔维尔",
        "director_en": "Jean-Pierre Melville",
        "director_slug": "melville",
        "title_zh": "独行杀手",
        "title_en": "Le Samouraï",
        "year": 1967,
        "one_liner": "**灰蓝与米色的极简冷调**——风衣与帽子的剪影配色，是黑色电影的现代版。",
        "core": [
            "极简冷调：灰蓝、米灰、浅褐，几乎没有饱和色",
            "风衣、帽子、室内墙面构成同色系的剪影色板",
            "构图静止且对称，人物像被摆在几何里（地铁、公寓、警局）",
            "光源极少且有方向：窗、灯管、车灯，暗部大面积"
        ],
        "visual": {
            "色彩": "灰蓝、米灰、浅褐、暗绿；极低饱和，几乎无暖色",
            "光影": "冷调低照度；单一光源（窗光、荧光管）配合大面积阴影",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩清淡，颗粒可见",
            "构图": "静止对称、几何化的室内、人物剪影；大量空镜（走廊、地铁）",
            "材质": "风衣呢、帽子毡、金属、玻璃、瓷砖、旧墙、雨",
            "情绪": "孤绝、冷静、程序化的宿命、极简的暴力"
        },
        "layers": {
            "style": "Melville Le Samouraï, minimalist cold colour, trench coat silhouette, silent procedural noir, geometric interiors",
            "lighting": "cool low key with a single directional source and large shadow areas, almost no warm light",
            "color": "blue-grey, beige grey, pale brown, dark green; extremely low saturation with virtually no warm tones",
            "composition": "static symmetry, geometric interiors, silhouette figures, long empty corridors and metro platforms",
            "medium": "35mm colour film, pale tonality, visible grain",
            "mood": "solitary, cold, procedural fatalism, minimalist violence",
            "camera": "locked-off symmetry, slow lateral drift, long static holds, no handheld"
        },
        "negative": "warm saturated colours, handheld, cluttered interiors, fast cutting, close-up shot-reverse-shot",
        "palette": [
            [
                "#3E4A56",
                "灰蓝"
            ],
            [
                "#A8A294",
                "米灰"
            ],
            [
                "#6B5B45",
                "浅褐"
            ],
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#C4C0B4",
                "瓷砖白"
            ]
        ],
        "video": {
            "运动": "极少：烟升起、雨落、人物缓慢走过走廊、地铁进站",
            "运镜": "固定机位、极慢横移",
            "时长": "10 秒",
            "关键": "**冷调 + 静止 + 剪影**；加暖色或手持就变成了普通犯罪片"
        },
        "pitfalls": [
            "写 neo-noir 会得到暖调+霓虹的现代犯罪片 → 这部片是冷、静、极简",
            "手持与快剪是反的",
            "饱和色会破坏它的同色系剪影"
        ],
        "see_also": [
            "film-noir",
            "minimalism-art"
        ],
        "title_original": "Le Samouraï",
        "filmgrab": "https://film-grab.com/2024/05/14/le-samourai/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/jean-pierre-melville/",
        "source": "curated"
    },
    {
        "slug": "melville-army-of-shadows",
        "director_zh": "让-皮埃尔·梅尔维尔",
        "director_en": "Jean-Pierre Melville",
        "director_slug": "melville",
        "title_zh": "影子部队",
        "title_en": "Army of Shadows",
        "year": 1969,
        "one_liner": "**冷蓝灰里的沉默抵抗**——色调被压成葬礼般的灰蓝，人物在空街与暗室里等待。",
        "core": [
            "整体压成冷蓝灰的丧葬调，几乎没有饱和色",
            "室内低照度 + 单光源；走廊、楼梯、暗室构成大量几何空镜",
            "人物静止且寡言，构图把孤独放进大面积的建筑空处",
            "外景多为阴天与雨，巴黎被拍成灰色"
        ],
        "visual": {
            "色彩": "冷蓝灰、暗绿、米灰、黑；极低饱和，整体近乎单色",
            "光影": "低照度方向光（窗、台灯、楼梯灯）；大面积阴影",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩清淡偏冷，颗粒可见",
            "构图": "几何化空镜（楼梯、走廊、暗室）、静止中景、人物剪影",
            "材质": "石灰墙、铁栏、木、雨、呢料大衣、旧车、石阶",
            "情绪": "沉默、坚忍、冷到骨头的孤独、注定的牺牲"
        },
        "layers": {
            "style": "Melville Army of Shadows, funereal blue-grey palette, silent resistance, geometric Paris interiors, procedural long takes",
            "lighting": "low key directional light with large shadow fields, cold and undramatic",
            "color": "cold blue-grey, dark green, beige grey, black; extremely low saturation, close to monochrome",
            "composition": "geometric empty shots of stairs and corridors, static medium shots, silhouette figures, lonely architecture",
            "medium": "35mm colour film, pale cool tonality, visible grain",
            "mood": "silent, stoic, cold to the bone, fated sacrifice",
            "camera": "static medium, slow lateral, long holds, no handheld"
        },
        "negative": "warm colours, saturated palette, handheld, fast cutting, battle spectacle",
        "palette": [
            [
                "#3E4A56",
                "冷蓝灰"
            ],
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#A8A294",
                "米灰"
            ],
            [
                "#141618",
                "暗部黑"
            ],
            [
                "#6B6459",
                "石灰灰"
            ],
            [
                "#C4C0B4",
                "雨幕白"
            ]
        ],
        "video": {
            "运动": "雨落、烟升起、人物缓慢走上楼梯、车驶过空街",
            "运镜": "固定机位、极慢横移",
            "时长": "10 秒",
            "关键": "**整体近乎单色的冷蓝灰**；加暖色或提高饱和就丢掉了葬礼调"
        },
        "pitfalls": [
            "写 war film 会得到战场大片 → 这部片是室内与等待，不是战斗",
            "暖色是反的",
            "手持与快剪不适合它的静止语法"
        ],
        "see_also": [
            "film-noir",
            "realism"
        ],
        "title_original": "Army of Shadows",
        "filmgrab": "https://film-grab.com/2017/11/25/the-army-of-shadows/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/jean-pierre-melville/",
        "source": "curated"
    },
]
