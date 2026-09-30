# -*- coding: utf-8 -*-
"""
fv_new_2.py —— 第 2 批：库布里克 / 黑泽明 / 小林正树 / 沟口健二（10 部）。

数据性质与字段说明见 `fv_new_1.py` 顶部。
"""

BATCH = [
    {
        "slug": "kubrick-2001",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "2001 太空漫游",
        "title_en": "2001: A Space Odyssey",
        "title_original": "2001: A Space Odyssey",
        "year": 1968,
        "filmgrab": "https://film-grab.com/2010/07/06/2001-a-space-odyssey/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/stanley-kubrick/",
        "one_liner": "**一点透视与纯色块**——对称舱室、白墙、红椅，后世科幻构图的公共祖先。",
        "core": [
            "一点透视：走廊、舱室、隧道全部收向画面正中灭点",
            "纯色块与硬边几何：白、红、黑构成干净的平面分割",
            "光是无源的均匀白光，不存在可见灯具也不存在阴影方向",
            "真空段落完全无声，用沉默而非音效制造尺度感"
        ],
        "visual": {
            "色彩": "纯白、正红、黑、冷灰；高对比但面积干净，几乎不用中间色",
            "光影": "无源的均匀高照度白光；阴影被压扁、几乎不可见，暗部也干净",
            "笔触": "（电影媒介）70mm 胶片，极高清晰度，无颗粒感，色温偏冷",
            "构图": "严格一点透视、绝对对称、大量负空间；人物常被放在正中或画面下缘",
            "材质": "抛光塑料、白色面板、红色织物座椅、金属、玻璃",
            "情绪": "冷峻、崇高、秩序里的不安、宇宙尺度下的渺小"
        },
        "layers": {
            "style": "Kubrick 2001, one-point perspective, symmetrical hard-edged geometry, 70mm large format, pristine retro-futurist interior, pure colour blocks",
            "lighting": "sourceless even high-key white light, flat invisible shadows, cool colour temperature, no visible fixtures, no rim light",
            "color": "pure white, primary red, black and cool grey; high contrast with clean flat areas and almost no midtones",
            "composition": "strict one-point perspective, dead-centre symmetry, large negative space, subject centred or low in frame, long receding corridors",
            "medium": "70mm film, extreme resolution, no visible grain, cool hard tonality",
            "mood": "cold, sublime, unease inside order, cosmic insignificance",
            "camera": "perfectly level tracking, slow forward dolly, static symmetry, no handheld"
        },
        "negative": "cluttered detail, warm cozy lighting, handheld, dutch angle, lens flare, film grain, organic textures, saturated secondary colours",
        "palette": [
            [
                "#F2F2F0",
                "纯白"
            ],
            [
                "#B0241F",
                "正红"
            ],
            [
                "#121316",
                "黑"
            ],
            [
                "#8C9296",
                "冷灰"
            ],
            [
                "#2E4A6B",
                "深蓝"
            ],
            [
                "#D8D2C4",
                "米白"
            ]
        ],
        "video": {
            "运动": "极缓慢的物体漂浮、旋转的站体、人物的慢速步行",
            "运镜": "水平匀速推进、缓慢环绕；绝不手持",
            "时长": "10 秒",
            "关键": "**对称与一点透视**是唯一命门，角度一歪就全丢；光必须是无源的均匀白光"
        },
        "pitfalls": [
            "有源光与可见灯具会立刻破坏它的「无源白光」语法",
            "写 warm 或 cozy 是反的；这部片是冷的",
            "杂乱细节会杀死纯色块的构图"
        ],
        "see_also": [
            "precisionism",
            "minimalism-art"
        ],
        "source": "curated"
    },
    {
        "slug": "kubrick-clockwork-orange",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "发条橙",
        "title_en": "A Clockwork Orange",
        "title_original": "A Clockwork Orange",
        "year": 1971,
        "filmgrab": "https://film-grab.com/2010/07/07/a-clockwork-orange/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/stanley-kubrick/",
        "one_liner": "**广角畸变 + 对称 + 撞色**——把暴力拍成装饰艺术，白色与橙红在同一个画面里对峙。",
        "core": [
            "广角镜头贴近人物，空间被拉伸到轻微畸形，产生压迫感",
            "对称构图与正面机位，人物正对镜头（有时直视观众）",
            "高饱和撞色：纯白、橙、红、蓝、绿，色块干净且面积大",
            "室内是装饰艺术的几何（条纹、圆环、镜面），表面全是塑料与漆"
        ],
        "visual": {
            "色彩": "纯白、橙红、钴蓝、草绿、黑；高饱和，色相之间不加过渡",
            "光影": "均匀高照度的室内光，阴影浅而硬；部分段落用彩色光（舞台式）",
            "笔触": "（电影媒介）35mm 胶片，色彩还原浓烈，低畸变但广角拉伸明显",
            "构图": "正面/对称构图、广角贴近、框中框；墙面装饰与人物构成图形对位",
            "材质": "塑料、镜面、漆、瓷、钢、人造毛、镀铬",
            "情绪": "玩世不恭、暴力被审美化、机械的欢愉"
        },
        "layers": {
            "style": "Kubrick A Clockwork Orange, wide-angle distortion, symmetrical frontal staging, high-chroma 1970s decor, art-deco graphic interiors",
            "lighting": "even high-key interior light with hard shallow shadows; some scenes lit with coloured stage light; no naturalistic falloff",
            "color": "pure white, orange-red, cobalt blue, grass green, black; high saturation with hard edges between hues and no gradient",
            "composition": "frontal symmetry, wide-angle close-up, frame within frame, decor pattern and figure aligned as graphic shapes",
            "medium": "35mm film, rich colour rendition, visible wide-angle stretch",
            "mood": "sardonic, violence made decorative, mechanical pleasure",
            "camera": "wide-angle close-up, dead-on frontal, slow forward dolly, occasional handheld"
        },
        "negative": "naturalistic lighting, desaturated palette, handheld vérité, documentary realism, muted earth tones, soft focus",
        "palette": [
            [
                "#F2F2F0",
                "纯白"
            ],
            [
                "#D97426",
                "橙红"
            ],
            [
                "#1F3A6E",
                "钴蓝"
            ],
            [
                "#4E8C3A",
                "草绿"
            ],
            [
                "#121212",
                "黑"
            ],
            [
                "#B0241F",
                "正红"
            ]
        ],
        "video": {
            "运动": "人物正面走近镜头、缓慢的机械动作、镜头微微后拉",
            "运镜": "正面广角推进、极慢后拉；对称的横移",
            "时长": "10 秒",
            "关键": "**正面广角 + 纯白与橙红的大色块**；拍侧脸或降低饱和就退化成普通 70 年代片"
        },
        "pitfalls": [
            "写 naturalistic 或 documentary 是反的",
            "广角畸变是特征，长焦会把这部片变成普通室内剧",
            "低饱和会杀掉它的撞色语法"
        ],
        "see_also": [
            "pop-art",
            "art-deco"
        ],
        "source": "curated"
    },
    {
        "slug": "kubrick-paths-of-glory",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "光荣之路",
        "title_en": "Paths of Glory",
        "title_original": "Paths of Glory",
        "year": 1957,
        "filmgrab": "https://film-grab.com/2015/02/06/paths-of-glory/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/stanley-kubrick/",
        "one_liner": "**战壕横移长镜与对称法庭**——黑白里的空间即权力，人被走廊和队列吞掉。",
        "core": [
            "战壕里的横移跟拍长镜：摄影机贴着士兵行进，空间狭窄到窒息",
            "军事法庭的对称构图：高窗、长桌、队列，权力被摆成几何",
            "黑白高对比，但室内保留丰富的灰阶层次，不是硬调",
            "面部特写与大全景交替，比例差制造无助感"
        ],
        "visual": {
            "色彩": "黑白；灰阶丰富，暗部有细节，高光克制",
            "光影": "战壕用侧逆光切出轮廓与泥；室内用高窗的顶光与侧光，人物常半脸在暗处",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，画面稳定",
            "构图": "横移长镜、对称正面、极深的纵深；队列与走廊把人物压成小点",
            "材质": "泥、沙袋、木、钢盔、石阶、大理石、制服呢",
            "情绪": "荒诞、愤怒、制度的冷、个体被碾碎"
        },
        "layers": {
            "style": "Kubrick Paths of Glory, 35mm black and white, tracking trench cinematography, symmetrical military interiors, stark realism",
            "lighting": "trenches: side-backlight carving silhouettes out of mud; interiors: high-window top and side light with faces half in shadow; restrained highlights, detailed blacks",
            "color": "black and white with a wide grey range; blacks retain detail, highlights never clip",
            "composition": "tracking lateral shot at soldier height, symmetrical frontal courtroom, extreme depth, queues and corridors reducing figures to small marks",
            "medium": "35mm black-and-white film, fine grain, steady frame",
            "mood": "absurdist, angry, institutional coldness, the individual ground down",
            "camera": "long lateral tracking at chest height, dead-on frontal wide, static symmetry"
        },
        "negative": "handheld shake, saturated color, close-up shot-reverse-shot, warm lighting, cgi battlefield, dutch angle",
        "palette": [
            [
                "#0F0F0F",
                "战壕黑"
            ],
            [
                "#3E3A34",
                "泥褐"
            ],
            [
                "#6E6E6E",
                "中灰"
            ],
            [
                "#A8A8A8",
                "石膏灰"
            ],
            [
                "#E0E0DC",
                "高窗白"
            ],
            [
                "#8C7A5C",
                "制服褐灰"
            ]
        ],
        "video": {
            "运动": "士兵在战壕里行进、泥浆溅起、法庭上人物端坐不动",
            "运镜": "贴地横移跟拍、正面固定；镜头稳定",
            "时长": "10 秒",
            "关键": "**横移长镜要贴着人走**（观众也在战壕里）；高机位俯瞰会丢掉压迫感"
        },
        "pitfalls": [
            "写 war film 会得到普通战争片 → 要写 trench-level tracking, symmetrical courtroom",
            "手持晃动与这部片的稳定机位相反",
            "黑白不是硬调：它保留大量灰阶，写 high contrast 会压掉层次"
        ],
        "see_also": [
            "realism",
            "precisionism"
        ],
        "source": "curated"
    },
    {
        "slug": "kubrick-dr-strangelove",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "奇爱博士",
        "title_en": "Dr. Strangelove",
        "title_original": "Dr. Strangelove",
        "year": 1964,
        "filmgrab": "https://film-grab.com/2014/08/01/dr-strangelove-or-how-i-learned-to-stop-worrying-and-love-the-bomb/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/stanley-kubrick/",
        "one_liner": "**作战室的顶光与环形桌**——黑白高对比的几何，把冷战拍成一场台球局。",
        "core": [
            "作战室：巨大的环形桌 + 顶部大面积光源，人物被低压在光下",
            "机舱段落：狭窄、多光源、金属反光，与作战室的空旷形成对照",
            "黑白高对比，室内用硬质光源把墙面切成几何块",
            "构图常把人物放在对称的图形中心，或让天花板占据画面上半"
        ],
        "visual": {
            "色彩": "黑白；作战室偏硬调高对比，机舱段落灰阶更连续",
            "光影": "作战室为顶部大面积光源（灯具可见），人物面部有硬阴影；机舱用多点实用光",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，画面锐利",
            "构图": "环形/对称构图、低角度仰拍带天花板、纵深排列的座位；广角贴近",
            "材质": "金属、混凝土地图台、皮革椅、仪表、荧光灯、钢",
            "情绪": "黑色幽默、荒诞、制度性疯狂、末日前的冷静"
        },
        "layers": {
            "style": "Kubrick Dr. Strangelove, 35mm black and white, war-room geometry, low-angle wide with ceiling, hard-edged institutional lighting",
            "lighting": "war room: large visible overhead source producing hard facial shadows; cockpit: multiple small practicals with metal bounce; high contrast in the war room, softer grey range in the aircraft",
            "color": "black and white; hard high contrast in the war room, continuous grey range in the cockpit",
            "composition": "circular and symmetrical staging, low angle including the ceiling, depth rows of seating, wide-angle close-up",
            "medium": "35mm black-and-white film, fine grain, sharp rendition",
            "mood": "black comedy, absurdity, institutional madness, pre-apocalyptic calm",
            "camera": "wide-angle low angle with ceiling, slow dolly around the table, static symmetry"
        },
        "negative": "saturated color, naturalistic soft lighting, handheld, shallow depth of field, intimate close-ups, warm tones",
        "palette": [
            [
                "#0F0F0F",
                "暗部黑"
            ],
            [
                "#3A3E42",
                "钢板灰"
            ],
            [
                "#6E7276",
                "混凝土灰"
            ],
            [
                "#A8ACB0",
                "仪表浅灰"
            ],
            [
                "#E8E8E4",
                "顶灯白"
            ],
            [
                "#8C7A5C",
                "皮革褐"
            ]
        ],
        "video": {
            "运动": "人物在桌边转身、手部动作、烟雾在顶光下升起",
            "运镜": "低角度广角推进、环绕缓慢横移",
            "时长": "10 秒",
            "关键": "**顶光必须可见且是大面积**，构图要带上天花板；柔光会把它变成普通黑白剧"
        },
        "pitfalls": [
            "把光柔化是这个片子的反面：硬阴影是它的喜剧语言",
            "不带天花板就丢掉了作战室的压迫感",
            "写 color 或 warm 直接跑偏"
        ],
        "see_also": [
            "precisionism",
            "pop-art"
        ],
        "source": "curated"
    },
    {
        "slug": "kubrick-killers-kiss",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "杀手之吻",
        "title_en": "Killer's Kiss",
        "title_original": "Killer's Kiss",
        "year": 1955,
        "filmgrab": "https://film-grab.com/2014/08/13/killers-kiss/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/stanley-kubrick/",
        "one_liner": "**黑白里的低照度工厂与屋顶**——库布里克最早的明暗对照实验，纽约被拍成一座废厂。",
        "core": [
            "实景拍摄的纽约：仓库、屋顶、拳击馆，场地本身就是压迫来源",
            "低照度黑白，大面积深黑，人物只有局部被照亮",
            "倾斜与非常规机位在天台段频繁出现，制造失衡",
            "拳击馆的顶光与烟雾构成硬质的光柱"
        ],
        "visual": {
            "色彩": "黑白；硬调高对比，暗部面积大，中间调窄",
            "光影": "低照度实用光源；顶光与侧光硬切面部，天台段落用城市环境光作剪影",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，略有粗糙感",
            "构图": "低角度与倾斜构图、天台纵深、狭长的仓库走廊；人物常被前景遮挡",
            "材质": "砖、铁、木箱、绳索、湿沥青、玻璃、拳台帆布",
            "情绪": "孤独、暴力、疲惫、城市的敌意"
        },
        "layers": {
            "style": "early Kubrick, 35mm black and white, location-shot New York, low-key chiaroscuro, noir warehouse geometry",
            "lighting": "low-key practical light, hard top and side light carving faces, large dead blacks, silhouettes against the skyline, visible smoke shafts",
            "color": "black and white, hard contrast, narrow midtones, large dark areas",
            "composition": "low and tilted angles, deep rooftop staging, long narrow warehouse corridors, figures blocked by foreground",
            "medium": "35mm black-and-white film, pronounced grain, slightly raw look",
            "mood": "lonely, violent, weary, the city as adversary",
            "camera": "handheld tilt, low angle, slow creep through corridors, static wide"
        },
        "negative": "bright even lighting, saturated color, studio polish, symmetrical calm composition, modern digital clean",
        "palette": [
            [
                "#0A0A0A",
                "死黑"
            ],
            [
                "#2E2A26",
                "仓库褐黑"
            ],
            [
                "#5E5A54",
                "水泥灰"
            ],
            [
                "#8C8C88",
                "灰白"
            ],
            [
                "#C4C0B8",
                "灯罩米"
            ],
            [
                "#4A4238",
                "木箱褐"
            ]
        ],
        "video": {
            "运动": "人物在仓库里移动、烟升起、拳击动作、天台的风",
            "运镜": "缓慢推进、低角度倾斜、横移",
            "时长": "10 秒",
            "关键": "**光要硬、暗部要大、机位要低或歪**；打平光就变成普通黑白片"
        },
        "pitfalls": [
            "这是库布里克最早的作品，风格尚未「对称克制」，别把《闪灵》的语法套过来",
            "实景粗糙感是它的特征，写 studio polish 是反的",
            "倾斜机位在这里是常态，写 level camera 会削弱失衡感"
        ],
        "see_also": [
            "film-noir",
            "expressionism"
        ],
        "source": "curated"
    },
    {
        "slug": "kurosawa-rashomon",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "罗生门",
        "title_en": "Rashomon",
        "title_original": "羅生門",
        "year": 1950,
        "filmgrab": "https://film-grab.com/2016/07/09/rashomon/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/akira-kurosawa/",
        "one_liner": "**让阳光穿过树叶进镜头**——第一次把自然光当戏剧主角，林间光斑是道德暧昧的隐喻。",
        "core": [
            "镜头直接对着太阳拍：光斑、眩光与树影成为画面主体",
            "森林段落用大量横移与仰拍，枝叶把画面切碎",
            "光斑的移动与闪烁替代剪辑制造节奏",
            "审判段落回到静止的正面构图，与森林的运动形成对照"
        ],
        "visual": {
            "色彩": "黑白；森林段高对比、光斑密布，审判段灰阶平缓",
            "光影": "直射阳光穿过滤叶，形成密集移动光斑与镜头眩光（当年被视为技术冒险）",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显，眩光与过曝高光可见",
            "构图": "仰拍与横移穿过树林、枝条切割画面；审判段为静态正面中景",
            "材质": "树叶、树皮、泥地、麻布、木、雨、石",
            "情绪": "暧昧、焦躁、道德的不可知、夏日的闷热"
        },
        "layers": {
            "style": "Kurosawa Rashomon, 35mm black and white, direct sun through foliage, lens flare and dappled light, forest tracking shots",
            "lighting": "direct sunlight through leaves producing dense moving dapples and visible lens flare, blown highlights, hard shadows; the light itself is the subject",
            "color": "black and white, high contrast in the forest, softer grey range in the courtroom, clipped highlights where the sun enters frame",
            "composition": "upward camera through branches, lateral tracking in the woods, foliage fracturing the frame; static frontal medium shots in court",
            "medium": "35mm black-and-white film, pronounced grain, visible flare and bloom",
            "mood": "ambiguous, agitated, moral unknowability, humid heat",
            "camera": "lateral tracking through trees, upward angle, static frontal in court"
        },
        "negative": "controlled studio lighting, no flare, symmetrical calm, saturated color, clean modern look, handheld",
        "palette": [
            [
                "#0F0F0F",
                "树影黑"
            ],
            [
                "#3E3E38",
                "林间灰"
            ],
            [
                "#6E6E64",
                "土灰"
            ],
            [
                "#A8A89C",
                "麻布米"
            ],
            [
                "#E8E8E0",
                "过曝天光"
            ],
            [
                "#55503E",
                "树皮褐"
            ]
        ],
        "video": {
            "运动": "树叶晃动使光斑游走、人物在林中穿行、雨落",
            "运镜": "仰拍横移、穿过枝叶的推进",
            "时长": "10 秒",
            "关键": "**必须让阳光直接进镜头**（眩光 + 移动光斑）；把光控干净就杀死了这部片的核心"
        },
        "pitfalls": [
            "写 controlled lighting / no flare 是反的 —— 眩光是它的历史性突破",
            "森林段的高对比与审判段的平缓是两套光，别统一",
            "仰拍与枝叶切割是构图语法，不写会变成普通古装片"
        ],
        "see_also": [
            "impressionism",
            "romanticism"
        ],
        "source": "curated"
    },
    {
        "slug": "kurosawa-seven-samurai",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "七武士",
        "title_en": "Seven Samurai",
        "title_original": "七人の侍",
        "year": 1954,
        "filmgrab": "https://film-grab.com/2016/09/03/seven-samurai/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/akira-kurosawa/",
        "one_liner": "**长焦压缩的雨与泥**——多机位拍出的横幅群像，把动作拍成天气。",
        "core": [
            "长焦镜头压缩前后景，人群与山峦被叠在一起",
            "雨、泥、风是主要元素：终场战斗在暴雨泥地里，动作变成挣扎",
            "多机位同时拍摄，剪辑点密集但空间关系始终清楚",
            "横幅式群像构图，人物被安排在画面的横向带里"
        ],
        "visual": {
            "色彩": "黑白；雨段深灰到黑，日间段灰阶开阔",
            "光影": "阴天散射为主，雨段用逆光让雨丝可见；室内低照度，火把作光源",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显；长焦段落景深压缩",
            "构图": "长焦压缩、横幅群像、低角度地平线；雨中段落人物半身陷在泥里",
            "材质": "泥、雨、稻草、竹、麻、铁、火把、马",
            "情绪": "壮阔、悲壮、劳作式的战斗、底层的尊严"
        },
        "layers": {
            "style": "Kurosawa Seven Samurai, 35mm black and white, telephoto compression, rain-soaked battle, horizontal group staging, multi-camera action",
            "lighting": "overcast diffuse for exteriors, backlight making rain streaks visible, low-key interiors lit by torches and hearth, hard contrast in the final battle",
            "color": "black and white; deep grey to black in the rain, wider grey range in daylight, mud midtones",
            "composition": "telephoto-compressed layers, horizontal bands of figures, low horizon, figures half-buried in mud, deep staging",
            "medium": "35mm black-and-white film, pronounced grain, compressed perspective from long lenses",
            "mood": "epic, tragic, labour-like combat, dignity of the lower class",
            "camera": "long lens medium wide, low angle, rapid multi-camera cutting within a clear space"
        },
        "negative": "clean dry ground, saturated color, handheld chaos without geography, close-up only coverage, modern digital sharpness",
        "palette": [
            [
                "#0F0F0F",
                "暴雨黑"
            ],
            [
                "#3A3A34",
                "泥灰"
            ],
            [
                "#5E5A4E",
                "泥褐"
            ],
            [
                "#8C8C84",
                "雨幕灰"
            ],
            [
                "#C4C0B4",
                "稻草米"
            ],
            [
                "#6E5A3E",
                "竹木褐"
            ]
        ],
        "video": {
            "运动": "暴雨、泥浆飞溅、人群冲撞、旗帜与竹枪晃动",
            "运镜": "长焦固定或缓慢横移；多机位但每镜稳定",
            "时长": "10 秒",
            "关键": "**雨与泥必须同时在场**，且要用长焦压人群；干净地面会让它变成普通古装打斗"
        },
        "pitfalls": [
            "写 samurai 会得到干净的古装剑戟片 → 要写 rain, mud, telephoto compression",
            "手持晃动不是黑泽明的语法（他用多机位但每台都稳）",
            "群像要横向铺陈，写 single hero close-up 就跑偏"
        ],
        "see_also": [
            "realism",
            "ukiyo-e"
        ],
        "source": "curated"
    },
    {
        "slug": "kurosawa-throne-of-blood",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "蜘蛛巢城",
        "title_en": "Throne of Blood",
        "title_original": "蜘蛛巣城",
        "year": 1957,
        "filmgrab": "https://film-grab.com/2016/09/24/throne-of-blood/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/akira-kurosawa/",
        "one_liner": "**能剧式静止与雾中森林**——把麦克白做成浮世绘般的构图，动作被压成仪式。",
        "core": [
            "能剧式的表演与构图：人物静止、姿态极端克制、情绪靠造型传达",
            "雾与森林是主要环境：雾中骑马、雾中行军，轮廓被雾吃掉",
            "室内用极简的几何（障子、柱子、地面）构成平面化的构图",
            "前景枝条与雾气作为遮挡层，纵深被压成几片平面"
        ],
        "visual": {
            "色彩": "黑白；雾段浅灰为主，室内深灰到黑，层次少而硬",
            "光影": "阴天散射与雾气；室内低照度，靠障子透光形成平面亮块",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒明显；雾中轮廓柔和",
            "构图": "平面化构图（浮世绘式）、前景枝叶遮挡、人物在画面中央静止",
            "材质": "雾、枯枝、竹、纸障子、木、甲胄、马",
            "情绪": "宿命、阴冷、仪式化的恐惧、被预言推着走"
        },
        "layers": {
            "style": "Kurosawa Throne of Blood, 35mm black and white, Noh-influenced stillness, fog-shrouded forest, flat ukiyo-e-like composition",
            "lighting": "overcast diffuse light diffused further by fog, paper-screen transmission indoors, low key with limited tonal steps, silhouettes dissolving into mist",
            "color": "black and white; pale grey dominates the fog, deep grey to black indoors, few intermediate steps",
            "composition": "flat graphic staging like a woodblock print, foreground branches as occlusion, figures centred and motionless, compressed depth",
            "medium": "35mm black-and-white film, pronounced grain, soft edges in fog",
            "mood": "fatalistic, cold, ritualised dread, driven by prophecy",
            "camera": "static centred framing, slow creep through fog, no handheld"
        },
        "negative": "saturated color, fast cutting, handheld, naturalistic depth, bright even lighting, modern clean digital",
        "palette": [
            [
                "#0F0F0F",
                "甲胄黑"
            ],
            [
                "#3A3A38",
                "室内深灰"
            ],
            [
                "#6E6E6A",
                "石墙灰"
            ],
            [
                "#A8A8A2",
                "雾灰"
            ],
            [
                "#D8D8D2",
                "障子白"
            ],
            [
                "#4A4438",
                "枯枝褐"
            ]
        ],
        "video": {
            "运动": "雾缓慢流动、枯枝轻晃、人物极缓慢地移动、马匹静止",
            "运镜": "固定机位或极慢推进；雾气承担运动",
            "时长": "10 秒",
            "关键": "**雾与静止**是这部片的一切；加快速动作或清晰轮廓就变成普通时代剧"
        },
        "pitfalls": [
            "能剧式的静止是核心，写 dynamic action 是反的",
            "浮世绘式平面构图 ≠ 一般对称构图，要写 flat graphic staging",
            "雾必须参与构图（吃轮廓），只当气氛不够"
        ],
        "see_also": [
            "ukiyo-e",
            "expressionism"
        ],
        "source": "curated"
    },
    {
        "slug": "kobayashi-harakiri",
        "director_zh": "小林正树",
        "director_en": "Masaki Kobayashi",
        "director_slug": "masaki-kobayashi",
        "title_zh": "切腹",
        "title_en": "Harakiri",
        "title_original": "切腹",
        "year": 1962,
        "filmgrab": "https://film-grab.com/2025/09/23/harakiri/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/masaki-kobayashi/",
        "one_liner": "**宽银幕黑白里的极简几何**——武家秩序被拍成冷峻的平面设计，静到能听见呼吸。",
        "core": [
            "宽银幕黑白，室内构图对称且极简，墙面与地面切成大块",
            "极长的静止镜头，等待本身是压迫",
            "深焦与平面化并存：人物站在几何正中，背景是规整的木构",
            "闪回段落用不同的构图与光线，与现实段落区分"
        ],
        "visual": {
            "色彩": "黑白；灰阶层次极丰富，中间调为主，黑不过死白不过曝",
            "光影": "室内以窗光与障子透光为主，人物脸上是柔和的侧光；庭院段用阴天散射",
            "笔触": "（电影媒介）35mm 黑白胶片（宽银幕），颗粒细，画面极干净",
            "构图": "宽银幕横幅、严格对称、深焦平面化、大量留白；人物常居中静止",
            "材质": "木、纸障子、榻榻米、刀、麻布、石、竹",
            "情绪": "冷峻、压抑、尊严与荒诞并存、制度的重量"
        },
        "layers": {
            "style": "Kobayashi Harakiri, 2.35:1 black and white, minimal symmetrical interiors, deep-focus flat staging, prolonged stillness",
            "lighting": "window and paper-screen transmission indoors with soft side light on faces; overcast diffuse in the courtyard; restrained highlights, rich midtones",
            "color": "black and white with an unusually wide grey range; midtones dominate, blacks and whites both restrained",
            "composition": "widescreen horizontal, strict symmetry, deep-focus flat staging, large empty areas, figures centred and motionless",
            "medium": "35mm black-and-white film in widescreen, fine grain, very clean frame",
            "mood": "cold, oppressive, dignity and absurdity together, institutional weight",
            "camera": "static wide hold, very slow lateral drift, deep focus, no handheld"
        },
        "negative": "handheld, close-up coverage, saturated color, fast cutting, asymmetrical handheld framing, warm cozy lighting",
        "palette": [
            [
                "#0F0F0F",
                "墨黑"
            ],
            [
                "#3E3E3A",
                "木褐灰"
            ],
            [
                "#6E6E68",
                "石墙灰"
            ],
            [
                "#A8A8A0",
                "庭石灰"
            ],
            [
                "#DCDCD4",
                "障子白"
            ],
            [
                "#55503E",
                "榻榻米褐"
            ]
        ],
        "video": {
            "运动": "几乎不动：布帘轻晃、烟升起、人物极缓慢地举手",
            "运镜": "固定机位，极慢横移；**不要快速运镜**",
            "时长": "10–15 秒",
            "关键": "**对称 + 极长的静止 + 宽银幕留白**；加动作与特写就退化成普通时代剧"
        },
        "pitfalls": [
            "写 jidaigeki 会得到带打斗的时代剧 → 这部片的特征是**静止**",
            "特写不是它的语法，要写 widescreen static wide",
            "黑白灰阶要丰富，写 high contrast 会压掉它的细腻"
        ],
        "see_also": [
            "precisionism",
            "zen-art"
        ],
        "source": "curated"
    },
    {
        "slug": "mizoguchi-ugetsu",
        "director_zh": "沟口健二",
        "director_en": "Kenji Mizoguchi",
        "director_slug": "mizoguchi",
        "title_zh": "雨月物语",
        "title_en": "Ugetsu",
        "title_original": "雨月物語",
        "year": 1953,
        "filmgrab": "https://film-grab.com/2022/11/02/ugetsu/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/kenji-mizoguchi/",
        "one_liner": "**一卷式长镜横移**——雾与湖面把志怪拍成水墨，镜头从不切而是滑过去。",
        "core": [
            "「一卷式」长镜：镜头缓慢横移并跟随，几乎不切，把空间连成一张卷轴",
            "雾、湖、芦苇是主要环境，人物像从水墨里浮出来",
            "构图留有大量「空」，人物常偏于一侧，视线引向画外",
            "室内段落用障子与帘幕切分，光从纸后透出"
        ],
        "visual": {
            "色彩": "黑白；雾段浅灰大面积，室内深灰，水面高光成片",
            "光影": "雾天散射光与水面反光；室内靠纸障子的透射光，柔和无影",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，柔和的层次过渡",
            "构图": "横向卷轴式长镜、人物偏置、大面积雾气留白；门框与帘幕分层",
            "材质": "雾、水、芦苇、纸障子、陶器、丝绸、船",
            "情绪": "幽玄、怅惘、物哀、人世无常"
        },
        "layers": {
            "style": "Mizoguchi Ugetsu, 35mm black and white, scrolling long take, mist-shrouded lake, Japanese ghost tale, painterly composition",
            "lighting": "diffuse fog daylight with water bounce; interiors lit through paper screens, soft and shadowless; pale highlights on water",
            "color": "black and white; large pale grey areas in the mist, deep grey interiors, broad specular sheets on the lake",
            "composition": "horizontal scroll-like tracking, subject placed to one side, generous mist negative space, layering through screens and curtains",
            "medium": "35mm black-and-white film, fine grain, soft tonal transitions",
            "mood": "ethereal, wistful, mono no aware, impermanence",
            "camera": "very slow lateral tracking in long unbroken takes, eye-level, no cutting within the move"
        },
        "negative": "fast cutting, handheld, close-up coverage, saturated color, hard directional light, modern digital sharpness",
        "palette": [
            [
                "#0F0F0F",
                "室内墨黑"
            ],
            [
                "#3E3E3C",
                "深灰"
            ],
            [
                "#6E6E6A",
                "石阶灰"
            ],
            [
                "#A8A8A2",
                "雾灰"
            ],
            [
                "#DCDCD6",
                "水面亮灰"
            ],
            [
                "#4E4A3E",
                "芦苇褐"
            ]
        ],
        "video": {
            "运动": "雾流动、芦苇摇、水面波纹、船缓慢移动",
            "运镜": "一卷式横移，长时间不切；可极慢推进",
            "时长": "10–15 秒",
            "关键": "**一个镜头完成一段位移（不切）** + 大面积雾；剪辑一多就失去了「卷轴」的语法"
        },
        "pitfalls": [
            "写 ghost story 会得到恐怖片 → 这部片是幽玄，不是惊吓",
            "频繁剪辑与一卷式长镜相反",
            "雾必须占大面积并承担留白，只当氛围用不够"
        ],
        "see_also": [
            "zen-art",
            "ukiyo-e"
        ],
        "source": "curated"
    },
]
