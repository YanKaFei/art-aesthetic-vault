# -*- coding: utf-8 -*-
"""
fv_data.py —— 电影风格库的数据层：导演-电影卡的定义。

## 为什么是独立的一层，而不是塞进 mv_*.py

`mv_*.py` 里的 421 张卡是**艺术流派**，它们的轴是「流派」——
七层拆的是「这个流派长什么样」。电影卡要回答的是另一个问题：
**「这部片子的画面是怎么拍出来的，我怎么让 AI 复现它」**。
轴是「导演-电影」，而且多两样艺术流派卡没有的东西：

  · 可核对的**拍摄班底**（摄影指导 / 美术指导 / 服装设计 / 年份）
  · 具体的**剧照索引**（哪几张、来自哪个画廊、外链在哪）

硬塞进 mv_core 会让两边都不干净。所以单独一层，但**共用同一套七层词表**
（LAYERS = style/lighting/color/composition/medium/mood/camera），
这样 artvault.py compose 的跨源混搭（「王家卫的光照 + 巴洛克的构图」）
才有统一的接口，不用为电影另写一套拼装逻辑。

## 证据强度要标清楚（本库的规矩）

艺术流派卡的七层是**手写的艺术史结论**，每层追得到 Tate 术语词条。
电影卡这一层不一样，所以 `source` 字段区分两种：

  · `"curated"` —— 导演/年份/班底来自 film-grab 画廊页（可回查 URL），
    七层拆解是**基于该片公认的摄影特征手写**的（如《花样年华》的
    step-printing 降格、杜可风的霓虹钨丝混合光）。
  · `"inferred"` —— 只从有限信息反推的（片名 + 导演 + 年份 + 剧照）。
    卡上会明确标注，不冒充「逐帧量出来的」。

**七层是「可复现的画面配方」，不是对原片的复述。**
剧照只用来校准描述，不要把图里的具体主体、构图、文字一起搬进提示词。

## 配色怎么来的

`palette` 六个色是这个片子**视觉签名**的锚色（手写近似值），
不是从剧照里逐张取样的结果——版权图不进 CI，取样结果不可复现。
想要实测值，用 `python3 image_analysis.py <本地剧照>`，
本地图在 99-attachments/images-films/（gitignore，不随仓库走）。
"""

# 每部片的字段说明（放在最前面，改数据前先看这里）
#
# slug            稳定标识符，全库唯一。约定 <导演>-<片名>，用于文件名/CLI/MCP
# director_zh     导演中文名（显示 + 检索）
# director_en     导演英文名（显示 + 检索）
# director_slug   英文短标识，用于「按导演分组」的目录名与索引页
# title_zh        片名中文
# title_en        片名英文（film-grab 的标题记法）
# title_original  原始片名（非英语片的原文，可空）
# year            年份
# filmgrab        画廊页 URL —— **可回查的证据来源**，不是装饰
# crew            拍摄班底，抓取脚本会用画廊页的真实值覆盖/校对
# one_liner       一句话：这部片的画面在做什么
# core            3–5 条核心主张（画面语法层面，不是剧情梗概）
# visual          六维拆解，键固定为 色彩/光影/笔触/构图/材质/情绪
# layers          七层提示词片段（英文，可直接拼）
# negative        负向提示词（这部片**不该有**什么）
# palette         六色 + 颜色名
# video           视频层的运动/运镜/时长/关键点
# pitfalls        常见翻车点：写提示词时最容易丢的东西
# see_also        关联的**艺术流派卡 slug**（跨库链接，artvault 那边有卡）
# source          "curated" | "inferred"
# stills          固定的剧照清单；留空则由 fv_fetch.py 从画廊页抓

FILMS = [

    # ------------------------------------------------------------------ 诗电影
    {
        "slug": "tarkovsky-stalker",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "潜行者",
        "title_en": "Stalker",
        "title_original": "Сталкер",
        "year": 1979,
        "filmgrab": "https://film-grab.com/2012/07/31/stalker/",
        "crew": {"摄影指导": "Aleksandr Knyazhinsky & Georgi Rerberg",
                 "美术指导": "Aleksandr Boym", "服装设计": "Nelli Fomina"},
        "one_liner": "**把时间本身拍成材质**——长镜头不推进剧情，只让湿气、锈迹和光慢慢渗进画面。",
        "core": [
            "长镜头是时间单位不是炫技：一个镜头里完成一个完整的时间体验",
            "低饱和的棕绿灰统一全片，颜色只在**水、火、沙**三种物质上出现",
            "前景障碍物（门框、管道、草丛）把人物压在画框深处",
            "声音先于画面：滴水、脚步、远处的火车，画面静止声音在动",
        ],
        "visual": {
            "色彩": "湿棕、苔绿、锈红、灰蓝；整体低饱和，靠**同一色族的明度层次**拉开空间，不用撞色",
            "光影": "全自然光/窗光为主；光被水汽和灰尘散射成体积光。雨夜段落改用**硬质点光源**（车灯、厂房灯）在湿地上拖出长条反光，反差陡然拉高",
            "笔触": "（电影媒介）颗粒感 35mm 胶片，柔边、无锐化，轻微曝光呼吸；雨夜的工业段落近乎**单色**（棕调黑白），与湿地的自然光段落形成两种质感",
            "构图": "极慢的横移与俯瞰；人物很小，环境是主角；画面里总有**第二层遮挡**",
            "材质": "积水、湿墙、锈铁、沙土、苔藓、破布；所有表面都是「被时间浸润过」的",
            "情绪": "肃穆、疲惫、时间凝滞、近乎宗教的静",
        },
        "layers": {
            "style": "slow cinema, poetic long take, 35mm film grain, Tarkovsky composition, "
                     "desaturated earth tones, no stylization",
            "lighting": "available light only; diffuse overcast daylight with volumetric light "
                        "through mist and dust, soft window light, deep but detailed shadows; in the "
                        "rain-night sequences, hard practical points (headlights, factory lamps) "
                        "streaking across wet ground, much higher contrast",
            "color": "wet brown, moss green, rust red, slate blue; uniformly desaturated, "
                     "tonal separation by value not hue, no saturated accents",
            "composition": "very slow lateral dolly, distant wide shot with small human figure, "
                            "foreground occlusion (doorway, pipes, grass), deep staging, eye-level",
            "medium": "35mm film, fine grain, soft edges, slight exposure breathing, no digital "
                      "sharpening; industrial rain sequences rendered near-monochrome (brown-tinted "
                      "black and white)",
            "mood": "solemn, weary, suspended time, contemplative, sacred stillness",
            "camera": "slow lateral tracking, 35mm-ish wide, deep focus, long unbroken takes",
        },
        "negative": "fast cutting, handheld shake, saturated colors, teal-and-orange grade, "
                    "lens flare, drone shot, cgi spectacle, clean digital look, hdr punch",
        "palette": [("#3A342A", "湿棕"), ("#4E5B3C", "苔绿"), ("#7A3B2E", "锈红"),
                    ("#5A6B78", "灰蓝"), ("#8C8577", "尘埃灰"), ("#D8D2C4", "散射天光")],
        "video": {
            "运动": "水面的细纹、飘落的尘埃、烟雾缓慢扩散、衣角轻动；动作幅度极小",
            "运镜": "极慢的横向移动（dolly/track）或完全静止；一个镜头里只做一件事",
            "时长": "15 秒以上才有意义；短于 8 秒会退化成「普通的阴天画面」",
            "关键": "画面必须几乎不动，靠**颗粒、雾气、光斑的呼吸**提供运动——一旦快切就杀死了诗电影",
        },
        "pitfalls": [
            "写「slow」不够 → 要写 slow lateral dolly / long unbroken take / minimal camera movement",
            "饱和度一高就变成普通风光片；必须写 desaturated earth tones，且**不要**写 vibrant",
            "缺少前景遮挡会让画面变成「空旷的大远景」，塔可夫斯基的纵深靠遮挡堆出来",
            "加 lens flare / 逆光光晕会立刻变成广告质感",
        ],
        "see_also": ["realism", "romanticism"],
        "source": "curated",
    },
    {
        "slug": "tarkovsky-mirror",
        "director_zh": "安德烈·塔可夫斯基",
        "director_en": "Andrei Tarkovsky",
        "director_slug": "tarkovsky",
        "title_zh": "镜子",
        "title_en": "The Mirror",
        "title_original": "Зеркало",
        "year": 1975,
        "filmgrab": "https://film-grab.com/2010/09/27/mirror-%d0%b7%d0%b5%d1%80%d0%ba%d0%b0%d0%bb%d0%be-zerkalo/",
        "crew": {"摄影指导": "Georgi Rerberg", "美术指导": "Nikolay Dvigubskiy",
                 "服装设计": "Nelli Fomina"},
        "one_liner": "**记忆的质感**——同一个空间在不同时间里反复出现，颜色随情绪漂移而不是随光源。",
        "core": [
            "色彩不服务真实，服务记忆：黑白与褐色调纪录片素材和彩色梦境片段交替",
            "室内戏靠**窗光 + 镜面**把空间切成多层，人物常常只出现一半",
            "物体特写（火、水、牛奶、荞麦）承担情绪，而不是演员的脸",
            "镜头缓慢漂移，像视线而不是摄影机",
        ],
        "visual": {
            "色彩": "**色温会漂**：室内记忆段落偏陈旧褐、奶白（实测暖度 +7～+33），外景与纪录片段落转向褪色橄榄、冷灰（测得 −6～−20）。全片低饱和，像不同年代的旧照片混在一本相册里 —— 这正是「记忆不可靠」的视觉手段",
            "光影": "单一窗光为主，室内暗部保留细节；烛火/油灯提供暖点光源。**冷暖对比是它的语法**：暖点光源总是小面积、被大片的冷环境包围",
            "笔触": "（电影媒介）胶片颗粒明显，镜头柔，轻微眩光但不做光斑特效",
            "构图": "对称的室内框景、镜中反射、缓慢横移；人物常被框在门/窗内",
            "材质": "木质地板、亚麻窗帘、旧墙纸、水汽、牛奶、火焰",
            "情绪": "怀旧、恍惚、私密、时间重叠的失重感",
        },
        "layers": {
            "style": "poetic memoir cinema, 35mm film, desaturated sepia-olive palette, "
                     "Tarkovsky slow drift, documentary texture",
            "lighting": "single window light, warm oil lamp interior, low-contrast soft shadows, "
                        "light through linen curtains, no artificial fill",
            "color": "temperature drifts across the film: aged sepia, milk white and muted "
                     "ochre in the warm interior-memory passages, fading into desaturated "
                     "olive and cold grey in the exterior and documentary passages; low "
                     "saturation throughout, like photographs from different decades",
            "composition": "symmetrical interior framing, mirror reflections, slow drifting camera, "
                            "subject framed inside doorways and windows, off-center half figures",
            "medium": "35mm film, visible grain, soft lens, slight veiling glare, no digital sharpening",
            "mood": "nostalgic, dreamlike, intimate, weightless overlapping time",
            "camera": "slow drifting eye-level camera, 40mm-ish, medium and long shots, few cuts",
        },
        "negative": "saturated colors, modern clean interior, handheld, fast cutting, "
                    "teal-and-orange grade, cgi, music-video pacing, hdr",
        "palette": [("#6B5B45", "陈旧褐"), ("#6E7A5A", "褪色橄榄"), ("#EFE9DC", "奶白"),
                    ("#A8894F", "暗赭黄"), ("#3B3830", "室内暗部"), ("#C97B3C", "油灯暖橙")],
        "video": {
            "运动": "窗帘被风吹动、火焰跳动、水面微皱、尘埃漂浮",
            "运镜": "极慢的横移或几乎静止；镜头像被风推动而不是被操作",
            "时长": "10–15 秒",
            "关键": "暖色点光源（油灯/烛火）必须有，但**面积要小**；大面积暖光会变成温馨家居广告",
        },
        "pitfalls": [
            "写 warm cozy 会跑成家居广告；要写 warm oil lamp against desaturated olive interior",
            "镜子反射是这部片的语法，不写 reflection 会丢掉一半特征",
            "过曝高光会杀死胶片感；要写 highlight detail retained",
        ],
        "see_also": ["impressionism", "realism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 港片霓虹
    {
        "slug": "wong-kar-wai-in-the-mood-for-love",
        "director_zh": "王家卫",
        "director_en": "Wong Kar Wai",
        "director_slug": "wong-kar-wai",
        "title_zh": "花样年华",
        "title_en": "In The Mood For Love",
        "title_original": "花樣年華",
        "year": 2000,
        "filmgrab": "https://film-grab.com/2013/03/09/in-the-mood-for-love/",
        "crew": {"摄影指导": "Christopher Doyle & Ping Bin Lee",
                 "美术指导": "William Chang", "服装设计": "William Chang"},
        "one_liner": "**用遮挡和色块谈恋爱**——人物永远被门框、窗帘、走廊切开，情绪全靠色彩和布料承载。",
        "core": [
            "前景遮挡构成偷窥感：镜头总在门框/栏杆/窗帘后面，观众像邻居",
            "饱和的暖红与暗绿对峙，颜色是情绪不是写实",
            "降格慢动作（step-printing）让日常动作变成回忆",
            "旗袍的图案与墙纸纹样互相呼应，布料即时间流逝的刻度",
        ],
        "visual": {
            "色彩": "深绛红、墨绿、琥珀金；饱和度高但**压暗**，不是明快的红绿",
            "光影": "钨丝灯与霓虹混合的暖光源，从画面外斜切进来；楼梯与走廊用整片暗部包围",
            "笔触": "（电影媒介）35mm 胶片，柔焦镜头，浅景深，轻微颗粒",
            "构图": "框中框、镜面反射、极窄的走廊纵深；人物常被切掉一部分（背影、手、侧脸）",
            "材质": "丝绸旗袍、印花墙纸、磨旧木扶手、雨、烟气、钨丝灯罩",
            "情绪": "隐忍、暧昧、克制、怀旧的惆怅",
        },
        "layers": {
            "style": "Wong Kar-wai romance, Christopher Doyle cinematography, 35mm film, "
                     "saturated deep red and jade green, step-printed slow motion",
            "lighting": "warm tungsten practical lamps, neon spill from off-frame, "
                        "single directional warm source, large areas of crushed shadow, "
                        "soft falloff on faces, smoky haze in the air",
            "color": "deep crimson, jade green, amber gold, lacquer black; high saturation "
                     "but low brightness, warm-cool opposition between red and green",
            "composition": "frame within frame, subject occluded by doorframe / railing / curtain, "
                            "mirror reflection, narrow corridor depth, partial figures (back, hand, profile)",
            "medium": "35mm film, soft focus lens, shallow depth of field, fine grain, slight halation",
            "mood": "repressed, ambiguous, restrained, nostalgic melancholy",
            "camera": "slow lateral tracking behind foreground, 50–85mm, medium and medium-close, "
                      "slightly off-speed slow motion",
        },
        "negative": "flat even lighting, modern clean digital look, daylight white balance, "
                    "wide empty space, saturated primary colors, fast cutting, handheld action",
        "palette": [("#5C1F1A", "深绛红"), ("#1F3B2C", "墨绿"), ("#B8863B", "琥珀金"),
                    ("#141210", "漆黑"), ("#8A6A55", "旧木褐"), ("#E3D6BC", "钨丝灯罩米白")],
        "video": {
            "运动": "人物缓慢走过前景、窗帘被风掀起、烟雾上升、雨丝斜落",
            "运镜": "缓慢横移跟随，前景遮挡物在镜头前滑过；可用极慢的 dolly in",
            "时长": "10 秒",
            "关键": "必须有**前景遮挡**和**暖光源从画外斜切**；去掉这两样就只剩「复古滤镜」，王家卫的味道全无",
        },
        "pitfalls": [
            "写 vintage filter 是错的 → 要写 frame within frame + tungsten practical + crushed shadows",
            "把红绿写得太亮会变成圣诞配色；必须压暗（low brightness, deep crimson）",
            "没有前景遮挡就失去了「偷窥感」这个核心语法",
            "写 slow motion 要指明是 off-speed/step-printed，否则模型给的是普通 24fps",
        ],
        "see_also": ["ukiyo-e", "art-deco"],
        "source": "curated",
    },
    {
        "slug": "wong-kar-wai-chungking-express",
        "director_zh": "王家卫",
        "director_en": "Wong Kar Wai",
        "director_slug": "wong-kar-wai",
        "title_zh": "重庆森林",
        "title_en": "Chungking Express",
        "title_original": "重慶森林",
        "year": 1994,
        "filmgrab": "https://film-grab.com/2014/10/20/chungking-express/",
        "crew": {"摄影指导": "Christopher Doyle & Lau Wai-Keung",
                 "美术指导": "William Chang", "服装设计": "William Chang"},
        "one_liner": "**手持、霓虹、降格**——城市的噪音感被拍成视觉，人物永远在拥挤里孤独。",
        "core": [
            "手持晃动 + 降格慢动作，制造「记忆中的城市」的不稳定感",
            "霓虹绿与钨丝黄撞色，光源密集在画面里（招牌、鱼缸、自动扶梯）",
            "广角近贴脸，人物变形、空间被拉伸",
            "罐头、鱼缸、快餐店灯管：日常物件被拍得像宗教圣物",
        ],
        "visual": {
            "色彩": "霓虹青绿、钨丝橙黄、荧光粉；高饱和撞色，暗部偏绿",
            "光影": "多光源现场光：霓虹招牌、鱼缸反光、荧光灯管；高光溢出（halation）明显",
            "笔触": "（电影媒介）16/35mm 胶片，粗颗粒，快镜头的运动模糊",
            "构图": "广角近景，人物在拥挤空间中被打断；倾斜构图、镜面反射、玻璃隔层",
            "材质": "玻璃、水族箱、塑料帘、湿沥青、金属扶梯、荧光灯管",
            "情绪": "躁动、孤独、轻盈、城市失眠感",
        },
        "layers": {
            "style": "Wong Kar-wai urban romance, Christopher Doyle handheld, 16mm film grain, "
                     "neon-green and tungsten-amber clash, step-printed slow motion",
            "lighting": "dense practical neon sources, fluorescent tube overhead, aquarium glow, "
                        "blown-out highlights with halation, green-tinted shadows, no clean key light",
            "color": "neon cyan-green, tungsten amber, fluorescent pink, wet asphalt black; "
                     "high saturation, cross-processed look, green in the shadows",
            "composition": "wide-angle close-up, slightly tilted frame, subject crowded by "
                            "foreground objects, reflections in glass and mirrors, layers of glass",
            "medium": "16mm film, coarse grain, motion blur from fast pans, halation on highlights",
            "mood": "restless, lonely, buoyant, urban insomnia",
            "camera": "handheld 24–28mm wide, close to face, fast pan, off-speed slow motion",
        },
        "negative": "static tripod shot, clean digital look, neutral white balance, "
                    "empty street, desaturated palette, symmetrical formal composition, tripod stillness",
        "palette": [("#1E7A63", "霓虹青绿"), ("#E39A2C", "钨丝橙黄"),
                    ("#D94F8A", "荧光粉"), ("#14201C", "湿沥青黑"),
                    ("#7FB8A8", "鱼缸冷光"), ("#F2E4C8", "灯管米白")],
        "video": {
            "运动": "人物穿过人群、扶梯移动、鱼缸水纹、烟雾在灯下翻滚",
            "运镜": "手持跟拍、快速摇镜（pan）、贴脸广角推进",
            "时长": "10 秒",
            "关键": "手持的**不稳定**和霓虹的**多光源高光溢出**是命门；稳如三脚架 = 立刻变成普通都市片",
        },
        "pitfalls": [
            "写 neon 不够 → 要写 dense practical neon sources + blown-out halation",
            "广角贴脸是关键，写 portrait lens / 85mm 会失去变形感",
            "画面太干净会失真；要写 crowded foreground, glass layers, wet surfaces",
        ],
        "see_also": ["ukiyo-e", "pop-art"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 冷面构成
    {
        "slug": "kubrick-the-shining",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "闪灵",
        "title_en": "The Shining",
        "year": 1980,
        "filmgrab": "https://film-grab.com/2010/07/09/the-shining/",
        "crew": {"摄影指导": "John Alcott", "美术指导": "Roy Walker"},
        "one_liner": "**一点透视的完美对称**——走廊永远对准灭点，安全感来自秩序，恐惧也来自秩序。",
        "core": [
            "严格的一点透视：所有线条收向画面正中的灭点",
            "对称构图 + 广角，空间被拉长到不自然",
            "饱和的红、橙、绿撞色（70 年代美式室内），颜色越欢快越不安",
            "斯坦尼康跟随长镜头：观众被牵着走，无法逃出画框",
        ],
        "visual": {
            "色彩": "正红、橘橙、芥末黄、钴蓝、薄荷绿；高饱和的室内装饰色，与冷白灯对峙",
            "光影": "均匀的高照度人工光（酒店没有真正的暗角），阴影被刻意压扁",
            "笔触": "（电影媒介）35mm 胶片，极低畸变，清晰度高，色温偏冷偏硬",
            "构图": "单点透视、绝对对称、走廊纵向深入；人物被放在正中或正中切开",
            "材质": "图案地毯、几何墙纸、抛光木地板、镜面、帘布",
            "情绪": "冷静、压抑、秩序中的暴力、令人不安的整洁",
        },
        "layers": {
            "style": "Kubrick symmetrical composition, one-point perspective, 35mm film, "
                     "saturated 1970s interior palette, steadicam long take",
            "lighting": "even high-key artificial interior light, cold white balance, "
                        "flat shadows, no darkness to hide in, practical lamps as visible sources",
            "color": "saturated primary red, orange, mustard, cobalt, mint; warm decor colors "
                     "against cold white light, high chroma but hard and flat",
            "composition": "perfect one-point perspective, dead-center symmetry, long corridor "
                            "receding to vanishing point, subject centered and isolated, wide angle",
            "medium": "35mm film, minimal distortion, high clarity, cool hard color temperature",
            "mood": "cold, oppressive, violent order, unsettling cleanliness",
            "camera": "steadicam tracking at eye level, 18–24mm wide, slow forward follow, "
                      "dead-on frontal, long take",
        },
        "negative": "handheld, tilted dutch angle, warm cozy lighting, natural window light, "
                    "cluttered composition, shallow depth of field, film grain heavy",
        "palette": [("#A8241F", "正红"), ("#D97426", "橘橙"), ("#C9A227", "芥末黄"),
                    ("#1F3A6E", "钴蓝"), ("#7FA88C", "薄荷绿"), ("#EDEDE6", "冷白灯")],
        "video": {
            "运动": "三脚架式稳定的前进、人物在走廊尽头静止等待",
            "运镜": "斯坦尼康匀速前进（steadicam）、水平横移、**绝不手持**",
            "时长": "10 秒",
            "关键": "对称和一点透视是**唯一命门**：角度一歪、镜头一歪，库布里克感立刻归零",
        },
        "pitfalls": [
            "写 symmetrical 必须同时写 one-point perspective，否则模型只给「左右对称」而非「纵深灭点」",
            "dutch angle / 倾斜构图是这部片的反面；要明确写进负向词",
            "写 warm cozy 会把 70 年代室内变成宜家广告；要写 cold white light over saturated decor",
        ],
        "see_also": ["precisionism", "art-deco"],
        "source": "curated",
    },
    {
        "slug": "kubrick-barry-lyndon",
        "director_zh": "斯坦利·库布里克",
        "director_en": "Stanley Kubrick",
        "director_slug": "kubrick",
        "title_zh": "巴里·林登",
        "title_en": "Barry Lyndon",
        "year": 1975,
        "filmgrab": "https://film-grab.com/2010/07/08/barry-lyndon/",
        "crew": {"摄影指导": "John Alcott", "美术指导": "Ken Adam"},
        "one_liner": "**用烛光拍夜景**——整部片像一幅会动的 18 世纪油画，每个定格都是绘画。",
        "core": [
            "NASA 定制的 f/0.7 镜头 + 纯烛光照明，暗部大面积但绝不糊",
            "构图直接引用 18 世纪绘画：人物居中、对称、画框内留白克制",
            "缓慢变焦（slow zoom out）代替剪辑，让观众意识到自己在看一幅画",
            "色彩是绘画性的：暖褐、暗金、灰蓝，层次靠颜料感而不是对比",
        ],
        "visual": {
            "色彩": "**两套色温**：烛光室内是暖褐、暗金、赭石；阴天外景是冷蓝紫、灰绿。低饱和但色域宽，像老油画的上光",
            "光影": "纯烛光/窗光的低照度照明，大面积深暗部，高光集中在脸与烛台",
            "笔触": "（电影媒介）35mm 胶片，极浅景深，柔焦边缘，轻微胶片颗粒",
            "构图": "绘画式构图：人物居中偏侧、前后景层次、对称的室内框景、缓慢拉开",
            "材质": "烛台、织锦、镀金框、亚麻、木质护墙板、雾气",
            "情绪": "冷峻、优雅、宿命、被观看的距离感（外景尤其冷，室内才暖）",
        },
        "layers": {
            "style": "18th century oil painting cinematography, Barry Lyndon candlelight, "
                     "35mm film, painterly composition, slow zoom",
            "lighting": "pure candlelight only, extremely low key, large deep shadow areas, "
                        "warm point sources with soft falloff, window light as fill, no electric light",
            "color": "two temperature registers: warm brown, dark gold and ochre in candlelit "
                     "interiors; cool blue-violet and muted green in overcast exteriors; low "
                     "saturation with wide gamut, varnished oil painting tonality",
            "composition": "painterly staging, subject off-center within symmetry, layered "
                            "foreground-midground-background, interior frame within frame, slow zoom out",
            "medium": "35mm film, very shallow depth of field, soft edges, fine grain, "
                      "candlelight halation",
            "mood": "cold, elegant, fatalistic, distanced",
            "camera": "slow zoom out, static eye-level, 50mm-ish, very shallow focus",
        },
        "negative": "modern lighting, bright even exposure, fluorescent, neon, handheld, "
                    "fast cutting, saturated colors, sharp digital look, hdr",
        "palette": [("#5A4632", "暖褐"), ("#B08A3E", "暗金"), ("#8A6A3C", "赭石"),
                    ("#4A5A6B", "灰蓝"), ("#3E4A38", "暗绿"), ("#E8D9B0", "烛光米")],
        "video": {
            "运动": "烛火摇曳、人物极缓慢的动作、织物的微小起伏",
            "运镜": "缓慢的 zoom out 或完全静止；**不要推拉摇移的炫技**",
            "时长": "10–15 秒",
            "关键": "光必须是**唯一的低照度烛光**且有大面积暗部；一旦补光变亮就成了普通古装剧",
        },
        "pitfalls": [
            "写 candlelight 但没写 low key / deep shadow 会让场景过亮，绘画感消失",
            "浅景深是这部片的签名（f/0.7），不写 shallow depth of field 会丢失",
            "快速剪辑与这部片完全相反；负向词里要写 fast cutting",
        ],
        "see_also": ["baroque", "rococo", "neoclassicism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 东方史诗
    {
        "slug": "kurosawa-ran",
        "director_zh": "黑泽明",
        "director_en": "Akira Kurosawa",
        "director_slug": "kurosawa",
        "title_zh": "乱",
        "title_en": "Ran",
        "title_original": "乱",
        "year": 1985,
        "filmgrab": "https://film-grab.com/2017/03/04/ran/",
        "crew": {"摄影指导": "Asakazu Nakai & Takao Saitô & Shôji Ueda",
                 "美术指导": "Shinobu Muraki & Yoshirô Muraki", "服装设计": "Emi Wada"},
        "one_liner": "**让天空成为主角**——横幅式构图把人压在地平线下，色彩像能剧面具一样分阵营。",
        "core": [
            "固定机位 + 长焦压缩，画面像横向展开的绘卷",
            "大面积的天空与云占据画面上半部，人在下三分之一行动",
            "色彩分阵营：一族的盔甲色就是它的身份，红黄蓝直接对立",
            "能剧式的表演与构图克制：极端场面也用静止的镜头呈现",
        ],
        "visual": {
            "色彩": "朱红、藤黄、靛蓝、灰白、烟灰；高饱和的军队色块 + 低饱和的环境色",
            "光影": "自然天光为主，阴天与逆光的天空是大光源；地面反光柔和",
            "笔触": "（电影媒介）35mm 胶片，长焦压缩，柔和的远景层次",
            "构图": "横幅式全景、人物在画面下方三分之一、地平线高；长焦压缩前后景",
            "材质": "盔甲、旗帜、尘土、枯草、云、雾气、燃烧的城",
            "情绪": "悲怆、宿命、壮阔、冷眼的残酷",
        },
        "layers": {
            "style": "Kurosawa epic, painterly widescreen tableau, long lens compression, "
                     "Noh-influenced stillness, 35mm film",
            "lighting": "natural overcast daylight, big bright sky as the key source, "
                        "soft ground bounce, silhouettes against sky, no artificial fill",
            "color": "vermilion red, gamboge yellow, indigo blue army blocks against muted "
                     "grey-green environment; high chroma only on figures and banners",
            "composition": "wide horizontal tableau, figures in the lower third, high horizon "
                            "line, large cloud-filled sky, long-lens compression, static camera",
            "medium": "35mm film, long telephoto compression, soft atmospheric haze, fine grain",
            "mood": "tragic, fated, vast, coldly cruel",
            "camera": "static long shot, telephoto 100mm+, high horizon, wide 2.35:1 framing",
        },
        "negative": "handheld, close-up portrait, cluttered foreground, modern digital grade, "
                    "night interior, desaturated grey palette, dutch angle",
        "palette": [("#B02A22", "朱红"), ("#D9A32B", "藤黄"), ("#274B7A", "靛蓝"),
                    ("#8C8C82", "烟灰"), ("#5E6B4A", "枯草绿"), ("#E4E1D6", "云白")],
        "video": {
            "运动": "旗帜与衣甲被风吹动、云层流动、尘土升起、火焰蔓延",
            "运镜": "固定机位为主；可用极慢的横摇展开全景",
            "时长": "10–15 秒",
            "关键": "**天空必须占画面一半以上**、人物在下三分之一；把地平线压低或天空填满就失去了绘卷感",
        },
        "pitfalls": [
            "写 epic 不够 → 要写 high horizon line + large sky + figures in lower third",
            "长焦压缩是这个片子的空间感，写 wide angle 会变成普通战场",
            "色彩分阵营（vermilion / indigo blocks）是它的语法，不能只写「 colourful 」",
        ],
        "see_also": ["ukiyo-e", "zen-art"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 韩国悬疑
    {
        "slug": "bong-parasite",
        "director_zh": "奉俊昊",
        "director_en": "Bong Joon-ho",
        "director_slug": "bong-joon-ho",
        "title_zh": "寄生虫",
        "title_en": "Parasite",
        "title_original": "기생충",
        "year": 2019,
        "filmgrab": "https://film-grab.com/2024/02/05/parasite/",
        "crew": {"摄影指导": "Hong Kyung-pyo", "美术指导": "Lee Ha-jun"},
        "one_liner": "**垂直的空间政治**——用楼梯和窗户讲阶级，光线的冷暖就是楼层。",
        "core": [
            "垂直调度：上楼＝阶级上升，下楼＝坠落；每个转场都是一次垂直移动",
            "半地下室的窗与豪宅的落地窗构成对照，取景框即社会位置",
            "光线分层：地下偏黄绿荧光、地上偏冷白日光",
            "对称的横向构图 + 突然的纵向爆发，克制与失控交替",
        ],
        "visual": {
            "色彩": "地下：黄绿荧光、灰褐；地上：冷白、米灰、木色；对比靠**色温**而不是饱和度",
            "光影": "**光就是空间的阶级标记**：半地下只有一扇贴着天花板的窄窗，光永远是「借来的」；豪宅是整面落地窗的漫射日光。地下用荧光灯管的绿黄，地上用冷白日光 —— 一眼就能看出人在哪一层",
            "笔触": "（电影媒介）数字摄影，干净锐利，轻微颗粒模拟，无风格化滤镜",
            "构图": "水平对称、框中框、窗户作为社会取景器；纵深的楼梯与走廊",
            "材质": "瓷砖、水泥、木饰面、玻璃、雨、石材、半地下铁窗",
            "情绪": "冷峻、阶级焦虑、幽默中的暴力、逐渐失控",
        },
        "layers": {
            "style": "modern Korean social thriller, clean digital cinematography, "
                     "vertical staging, symmetrical framing, Bong Joon-ho blocking",
            "lighting": "light itself marks the class of the space: the semi-basement has "
                        "only one narrow window near the ceiling so daylight always reads as "
                        "borrowed, while the mansion gets full-wall diffused daylight; "
                        "green-yellow fluorescent tubes below, cool white above, low key "
                        "with retained shadow detail, no stylized grade",
            "color": "split by level: yellow-green fluorescent and grey-brown below, cool white "
                     "and warm wood above; contrast by color temperature not saturation",
            "composition": "horizontal symmetry, frame within frame, window as social viewfinder, "
                            "vertical depth via staircases and corridors, characters placed by level",
            "medium": "digital cinema, clean and sharp, subtle grain overlay, no filter look",
            "mood": "cold, class anxiety, violence inside humor, escalating loss of control",
            "camera": "eye-level and slight high angle, 35–50mm, static symmetry, "
                      "vertical tracking on stairs",
        },
        "negative": "saturated colors, warm cozy lighting, handheld chaos, heavy film grain, "
                    "sepia vintage filter, lens flare, shaky cam",
        "palette": [("#8A9A5B", "荧光黄绿"), ("#6B6459", "水泥灰褐"), ("#DDE3E6", "冷白日光"),
                    ("#9C7B52", "木饰暖褐"), ("#2B2E2C", "暗部黑"), ("#B8C4C9", "雨天铅灰")],
        "video": {
            "运动": "雨落下、水沿台阶流下、人物上下楼梯、窗帘轻动",
            "运镜": "垂直移动（上/下楼梯的跟拍）、缓慢横移；克制不炫技",
            "时长": "10 秒",
            "关键": "**垂直方向**必须出现（楼梯/上下运动）；只有水平移动就丢掉了这部片的阶级语法",
        },
        "pitfalls": [
            "写 dark 不够 → 要写 split lighting by level（地下荧光 / 地上冷白日光）",
            "加 vintage 滤镜或重颗粒会立刻变成「廉价复古」，这部片是干净数字质感",
            "没有垂直移动就失去了楼梯这个核心符号",
        ],
        "see_also": ["realism", "precisionism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 数字科幻
    {
        "slug": "villeneuve-blade-runner-2049",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "银翼杀手 2049",
        "title_en": "Blade Runner 2049",
        "year": 2017,
        "filmgrab": "https://film-grab.com/2019/05/24/blade-runner-2049/",
        "crew": {"摄影指导": "Roger Deakins", "美术指导": "Dennis Gassner",
                 "服装设计": "Renée April"},
        "one_liner": "**用雾和硬光造体积**——橙色沙尘与青色雨夜两种世界，人物在巨物前渺小到失焦。",
        "core": [
            "两种极端环境配色：橙黄沙尘（废土）与青蓝雨夜（城市），几乎不用中间色",
            "硬光源 + 雾气/雨/尘，把光变成可见的体积",
            "巨大体量的建筑/雕塑与极小的人，比例即是主题",
            "Deakins 式的克制造型：几乎不用镜头光晕，靠**光源位置**而不是特效造气氛",
        ],
        "visual": {
            "色彩": "城市：青蓝、灰白、霓虹品红点缀；废土：橙黄、琥珀、烟褐；两端都极低饱和",
            "光影": "强方向性硬光穿过雾/雨/尘形成体积光；大面积暗部，光源本身常入画",
            "笔触": "（电影媒介）数字摄影，极高解析力，柔和的暗部过渡，无颗粒",
            "构图": "极端比例关系的远景、居中对称的正面构图、人物剪影贴在光幕前",
            "材质": "雨、雾、玻璃、混凝土、锈金属、全息投影、雪",
            "情绪": "孤寂、冷峻、崇高、宿命的沉重",
        },
        "layers": {
            "style": "Roger Deakins cinematography, Blade Runner 2049, brutalist sci-fi, "
                     "volumetric haze, extreme scale contrast, digital large format",
            "lighting": "single hard directional source through fog, rain or dust creating "
                        "visible beams, huge dark areas, source often inside frame, "
                        "backlit silhouettes, no lens flare",
            "color": "two worlds: cyan blue and cool grey with magenta neon accents / "
                     "orange ochre and amber dust; both severely desaturated, no midtones",
            "composition": "extreme scale contrast between giant structure and tiny figure, "
                            "dead-center frontal symmetry, silhouette against a wall of light, "
                            "huge negative space",
            "medium": "digital large format, extreme clarity, smooth shadow rolloff, no grain, "
                      "no filter",
            "mood": "lonely, austere, sublime, fatalistic weight",
            "camera": "very wide establishing with small subject, 40–75mm, slow push in, "
                      "static and monumental",
        },
        "negative": "lens flare, warm cozy interior, handheld, saturated colors, "
                    "cluttered detail, bright daylight, film grain, anamorphic bokeh",
        "palette": [("#1E3A4C", "雨夜青蓝"), ("#3E5A66", "冷灰"), ("#B0417A", "霓虹品红"),
                    ("#C97A2B", "沙尘橙"), ("#8A6A3E", "琥珀褐"), ("#D6D9D6", "雾白")],
        "video": {
            "运动": "雨丝、雾气缓慢流动、全息投影闪烁、衣摆被风掀起",
            "运镜": "缓慢推进（push in）、固定机位等主体入画；避免手持",
            "时长": "10 秒",
            "关键": "必须有**可见的光束**（雾/雨/尘 + 硬光）和**极端的体量对比**；去掉这两样就变成普通科幻概念图",
        },
        "pitfalls": [
            "写 fog 但没写 hard directional light 出不来体积光；两者缺一不可",
            "lens flare 是这部片的反面，要写进负向词（Deakins 刻意避免）",
            "不写 scale contrast 会失去「人在巨物前」的主题性构图",
        ],
        "see_also": ["cyberpunk", "minimalism-art", "precisionism"],
        "source": "curated",
    },
    {
        "slug": "villeneuve-dune",
        "director_zh": "丹尼斯·维伦纽瓦",
        "director_en": "Denis Villeneuve",
        "director_slug": "villeneuve",
        "title_zh": "沙丘",
        "title_en": "Dune",
        "year": 2021,
        "filmgrab": "https://film-grab.com/2022/06/24/dune-2021/",
        "crew": {"摄影指导": "Greig Fraser", "美术指导": "Patrice Vermette",
                 "服装设计": "Jacqueline West & Bob Morgan"},
        "one_liner": "**把画面压成色块**——极简的几何与单一色温，巨物慢慢从沙尘里浮出来。",
        "core": [
            "极端简化：每个场景基本只有一到两个色相，画面像被烧过",
            "低照度大反差，逆光剪影，人脸常常只有轮廓",
            "几何化的巨物（飞船、建筑）与无边际的自然（沙丘、海）并列",
            "运动极慢：镜头滑动像地质运动，不用快切推进",
        ],
        "visual": {
            "色彩": "沙黄、赭石、铁灰、沥青黑、冷蓝；单场景单色相，饱和极低",
            "光影": "强逆光与侧逆光，大面积剪影；室内用极窄的缝隙光制造神圣感",
            "笔触": "（电影媒介）数字摄影转胶片印制，柔和高光滚降，颗粒极细",
            "构图": "极简几何、大面积负空间、人物被巨物压成小点、正面对称",
            "材质": "沙、岩石、混凝土、金属、布幔、蒸汽、尘埃",
            "情绪": "庄严、神秘、压迫、近乎宗教的肃穆",
        },
        "layers": {
            "style": "Dune cinematography, Greig Fraser, monumental minimalism, brutalist sci-fi, "
                     "dusty desaturated palette, slow geological camera",
            "lighting": "strong backlight and side-backlight producing silhouettes, narrow slit "
                        "of light indoors, extremely low key, atmospheric dust diffusion, "
                        "no fill light",
            "color": "single dominant hue per scene: sand yellow, ochre, iron grey, pitch black, "
                     "cold blue; minimal saturation, almost no secondary colors",
            "composition": "radical minimalism, massive negative space, figure reduced to a speck "
                            "beside monumental geometry, frontal symmetry, horizon as a hard line",
            "medium": "digital large format printed to film, soft highlight rolloff, very fine grain",
            "mood": "solemn, mystical, oppressive, religious awe",
            "camera": "extremely slow tracking or static, wide anamorphic-ish framing, "
                      "long lens for compaction, no handheld",
        },
        "negative": "saturated colors, handheld, lens flare, cluttered composition, "
                    "warm cozy light, bright even daylight, fast cutting, cgi clutter",
        "palette": [("#C29A5B", "沙黄"), ("#8A6236", "赭石"), ("#4A4E52", "铁灰"),
                    ("#14161A", "沥青黑"), ("#3B5A75", "冷蓝"), ("#E2D3B4", "尘光米")],
        "video": {
            "运动": "沙粒被风推着走、尘埃在光里漂浮、布幔缓慢起伏、巨物缓缓升起",
            "运镜": "极慢的横移或推进，机位接近静止；可用缓慢上升（crane up）",
            "时长": "10–15 秒",
            "关键": "**单一色相 + 逆光剪影 + 极慢运动**三件套；任何一项丢了都会退化成普通科幻片",
        },
        "pitfalls": [
            "多色相会毁掉这部片的「被烧过」的观感；一场景一色相是硬约束",
            "正面打光会让人脸亮起来，剪影感全失；要写 backlight / silhouette",
            "快速剪辑与地质感的慢运动相反，负向词要写 fast cutting",
        ],
        "see_also": ["minimalism-art", "surrealism", "zen-art"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 黑色犯罪
    {
        "slug": "fincher-se7en",
        "director_zh": "大卫·芬奇",
        "director_en": "David Fincher",
        "director_slug": "fincher",
        "title_zh": "七宗罪",
        "title_en": "Se7en",
        "title_original": "Seven",
        "year": 1995,
        "filmgrab": "https://film-grab.com/2013/09/09/seven/",
        "crew": {"摄影指导": "Darius Khondji", "美术指导": "Arthur Max"},
        "one_liner": "**漂白与压暗**——永远在下雨的城市，光进不来，画面脏、绿、湿。",
        "core": [
            "闪银漂白（bleach bypass）：高光死白、暗部沉黑、中间调被抽走",
            "全片低照度 + 永不停雨的湿表面，光源永远是「不够用」的",
            "摄影机沉稳但**不安分**：微妙的不对称、被前景遮挡的取景",
            "手电筒/台灯作为唯一光源，把观众也拖进现场",
        ],
        "visual": {
            "色彩": "脏绿、褐黄、污白、沥青黑；几乎无饱和，整体偏黄绿病态",
            "光影": "极低照度，手电与台灯作主光，大面积死黑；高光过曝成纯白",
            "笔触": "（电影媒介）35mm 胶片 + bleach bypass，粗颗粒，高对比",
            "构图": "被前景遮挡的取景、微妙的偏心构图、低角度压迫",
            "材质": "湿沥青、纸、血、锈、瓷砖、雨水、旧木头",
            "情绪": "压抑、肮脏、疲惫、无可挽回",
        },
        "layers": {
            "style": "David Fincher, Darius Khondji, bleach bypass film look, "
                     "1990s crime thriller, grimy low-key realism",
            "lighting": "extremely low key, flashlight and desk lamp as only sources, "
                        "large dead-black areas, blown-out white highlights, "
                        "no fill light, practical rain-soaked ambience",
            "color": "dirty green, brownish yellow, soiled white, asphalt black; "
                     "almost no saturation, sickly yellow-green cast overall",
            "composition": "framing obstructed by foreground, off-center imbalance, "
                            "low angle with oppressive ceiling, cramped interior",
            "medium": "35mm film with bleach bypass, coarse grain, high contrast, "
                      "silver retained in highlights",
            "mood": "oppressive, filthy, weary, irredeemable",
            "camera": "steady but slightly unsettled, 35mm-ish, low and high angles, "
                      "static with slow creep",
        },
        "negative": "bright daylight, saturated colors, clean modern interior, "
                    "handheld shake, warm cozy light, lens flare, teal-orange grade",
        "palette": [("#4A5240", "脏绿"), ("#6B5E3A", "褐黄"), ("#D8D4C4", "污白"),
                    ("#141511", "沥青黑"), ("#8A7A5C", "旧木"), ("#9AA38C", "湿墙灰绿")],
        "video": {
            "运动": "雨水、水洼涟漪、烟、手电光柱缓慢扫过",
            "运镜": "固定或缓慢横移、手电扫光的视角移动",
            "时长": "10 秒",
            "关键": "**bleach bypass（死白高光 + 沉黑暗部 + 病态黄绿）**是命门；写「dark」不够，中间调不能被拉回来",
        },
        "pitfalls": [
            "只写 dark 会得到普通的暗调画面；必须写 bleach bypass / crushed blacks / blown highlights",
            "手电/台灯作为光源要写出来，否则模型自己补一个柔和的棚光，全毁",
            "加 teal-orange 调色（现代常见）会偏离这部片的黄绿病态",
        ],
        "see_also": ["film-noir", "realism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 台湾新电影
    {
        "slug": "hou-hsiao-hsien-the-assassin",
        "director_zh": "侯孝贤",
        "director_en": "Hou Hsiao-hsien",
        "director_slug": "hou-hsiao-hsien",
        "title_zh": "刺客聂隐娘",
        "title_en": "The Assassin",
        "title_original": "刺客聶隱娘",
        "year": 2015,
        "filmgrab": "https://film-grab.com/2017/02/24/the-assassin/",
        "crew": {"摄影指导": "Ping Bin Lee", "美术指导": "Hwarng Wern-ying",
                 "服装设计": "Hwarng Wern-ying"},
        "one_liner": "**隔着纱帘看唐朝**——大量前景遮挡与静止镜头，情绪不在脸上而在织物的透光里。",
        "core": [
            "层层纱帘/屏风/枝叶作前景，画面永远有「隔着什么在看」的距离",
            "极端静止的长镜头，动作被留在画外或省略",
            "自然光 + 织物透光，室内是暖金，室外是青绿",
            "构图把人物放在画面边缘或次要位置，空间与器物才是主角",
        ],
        "visual": {
            "色彩": "暖金、暗红、青绿、铅灰、墨黑；低饱和但色相精致，像旧绢本",
            "光影": "自然窗光透过纱帘/纸门形成柔散光；室内以油灯作暖点；大面积含蓄暗部",
            "笔触": "（电影媒介）35mm 胶片，极柔的光晕与轻微颗粒，布料的柔边",
            "构图": "多层前景遮挡（纱、屏、枝、柱）、人物偏置、静止的横向构图",
            "材质": "丝绸、纱、纸门、漆器、竹、烛火、雾",
            "情绪": "疏离、隐忍、含蓄、时间的静止",
        },
        "layers": {
            "style": "Hou Hsiao-hsien, Tang dynasty aesthetic, layered gauze foreground, "
                     "static long take, 35mm film, Chinese scroll painting composition",
            "lighting": "natural light diffused through gauze and paper screens, warm oil lamp "
                        "interior points, soft veiling glare, restrained shadow detail, no hard light",
            "color": "warm gold, dark crimson, jade green, lead grey, ink black; low saturation "
                     "with refined hues like aged silk",
            "composition": "multiple layers of foreground occlusion (gauze, screen, branch, pillar), "
                            "off-center subject, static horizontal framing, action off-screen",
            "medium": "35mm film, very soft halation, fine grain, textile softness",
            "mood": "detached, restrained, implicit, suspended time",
            "camera": "completely static long take, 40–50mm, medium-long shot, "
                      "camera as a distant observer",
        },
        "negative": "handheld, fast cutting, close-up face, saturated colors, hard directional light, "
                    "action choreography in frame, modern digital sharpness, lens flare",
        "palette": [("#A8843C", "暖金"), ("#6B2320", "暗红"), ("#4E6B54", "青绿"),
                    ("#5A5E63", "铅灰"), ("#1A1A18", "墨黑"), ("#E0D2B4", "纱透米")],
        "video": {
            "运动": "纱帘被风轻吹、烛火摇曳、衣料缓慢摆动、雾在远处移动",
            "运镜": "完全静止或极缓慢的横移；**不要有推拉**",
            "时长": "10–15 秒",
            "关键": "**至少两层前景遮挡**（纱/屏/枝）+ 静止机位；没有遮挡就变成普通的古装美人图",
        },
        "pitfalls": [
            "写 Chinese ancient style 会得到通用古装；必须写 Tang dynasty + layered gauze foreground",
            "把动作拍进画面会破坏侯孝贤的省略语法；要写 action off-screen",
            "硬光会杀死纱帘的透光感，负向词里要明确禁止 hard light",
        ],
        "see_also": ["ukiyo-e", "zen-art", "impressionism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 欧洲作者电影
    {
        "slug": "goddard-breathless",
        "director_zh": "让-吕克·戈达尔",
        "director_en": "Jean-Luc Godard",
        "director_slug": "godard",
        "title_zh": "精疲力尽",
        "title_en": "Breathless",
        "title_original": "À bout de souffle",
        "year": 1960,
        "filmgrab": "https://film-grab.com/2011/01/20/a-bout-de-souffle-breathless/",
        "crew": {"摄影指导": "Raoul Coutard", "美术指导": "Claude Chabrol"},
        "one_liner": "**粗糙即风格**——手持、跳切、自然光，把 B 级片的穷拍法变成现代电影的语言。",
        "core": [
            "跳切（jump cut）：同一动作被切断再接上，时间被故意打断",
            "手持摄影机在街头跟拍，自然光、胶片感粗糙",
            "打破轴线与连续性，观众始终意识到「这是电影」",
            "高对比的黑白，靠自然光与反射光，不走精致布光",
        ],
        "visual": {
            "色彩": "黑白；硬调高对比，中间调被拉窄，高光与暗部都敢过",
            "光影": "自然光/现场光，窗光作主光；脸上常有不对称的硬阴影",
            "笔触": "（电影媒介）35mm 胶片，粗颗粒，手持的轻微抖动与失焦",
            "构图": "街头的即兴取景、打破常规的偏心构图、跳切制造的不连续",
            "材质": "报纸、香烟、皮质座椅、玻璃、街道、汽车、金属",
            "情绪": "焦躁、轻盈、玩世不恭、青春的虚无",
        },
        "layers": {
            "style": "French New Wave, Godard Breathless, handheld 35mm, jump cut editing, "
                     "Raoul Coutard natural light, documentary roughness",
            "lighting": "available light only, window light as key, hard asymmetric shadows "
                        "on faces, no fill, natural contrast range, occasional overexposure",
            "color": "black and white, hard contrast, narrow midtones, both highlights and "
                     "shadows allowed to clip",
            "composition": "improvised street framing, off-center and rule-breaking, "
                            "jump-cut discontinuity, handheld drift",
            "medium": "35mm film, coarse grain, handheld softness, slight focus breathing",
            "mood": "restless, buoyant, cynical, youthful nihilism",
            "camera": "handheld, 35–50mm, street level, improvised pans, discontinuous cuts",
        },
        "negative": "tripod steadiness, symmetrical formal composition, studio lighting, "
                    "smooth gimbal move, saturated color, clean digital, classical continuity",
        "palette": [("#0F0F0F", "黑"), ("#3A3A3A", "暗灰"), ("#8C8C8C", "中灰"),
                    ("#C9C9C9", "浅灰"), ("#F2F2F0", "过曝白"), ("#5C5C5C", "阴天街灰")],
        "video": {
            "运动": "手持跟随人物穿过街道、人群移动、烟、汽车驶过",
            "运镜": "手持跟拍、突然的横摇；**可以有轻微失焦和抖动**",
            "时长": "10 秒",
            "关键": "**手持 + 自然光 + 高对比黑白**三件套；一旦上了三脚架、补了光，新浪潮的即时感就没了",
        },
        "pitfalls": [
            "写 black and white 不够 → 要写 hard contrast, clipped highlights, narrow midtones",
            "稳如三脚架会立刻变成「古典黑白片」；要明确写 handheld / improvised",
            "过度精致（打光、构图）与这部片的美学完全相反",
        ],
        "see_also": ["film-noir", "photorealism"],
        "source": "curated",
    },

    # ------------------------------------------------------------------ 日本动画
    {
        "slug": "kon-satoshi-perfect-blue",
        "director_zh": "今敏",
        "director_en": "Satoshi Kon",
        "director_slug": "satoshi-kon",
        "title_zh": "未麻的部屋",
        "title_en": "Perfect Blue",
        "title_original": "パーフェクトブルー",
        "year": 1997,
        "filmgrab": "https://film-grab.com/2020/01/23/perfect-blue/",
        "crew": {"摄影指导": "Hisao Shirai"},
        "one_liner": "**把镜子当剪辑台**——现实与幻觉在同一个镜头里交换，观众分不清哪一层是真的。",
        "core": [
            "镜面/反射承担叙事：同一个人在两块镜子里做不同的动作",
            "主体与背景的割裂：人物正常，背景在扭曲或错位",
            "色温分层：现实偏冷白，幻觉偏品红/橙暖，靠色温而不是特效区分层级",
            "构图突然的俯视/极近特写，制造心理压迫",
        ],
        "visual": {
            "色彩": "冷白、灰蓝（现实）对品红、橙黄（幻觉/舞台）；高饱和的局部跳色",
            "光影": "**两套打光系统对撞**：舞台/幻觉是品红与蓝的顶光，光源在画面里看得见；现实是冷白日光或荧光，平而冷。脸上用硬边阴影切分，不追求体积 —— 那是赛璐珞的语法",
            "笔触": "（动画媒介）赛璐璐手绘，硬边高光，色彩平涂但阴影分层精细",
            "构图": "镜面分割画面、突然的俯视、极近距离特写、背景与主体错位",
            "材质": "玻璃、镜子、霓虹、水面、舞台灯、胶片颗粒叠加",
            "情绪": "偏执、眩晕、身份崩解、被窥视的不安",
        },
        "layers": {
            "style": "1990s Japanese cel animation, Satoshi Kon psychological thriller, "
                     "hand-drawn cel look, mirror-split composition, film grain overlay",
            "lighting": "two lighting systems colliding: the stage / hallucination world is "
                        "lit by visible magenta and blue top light, while reality is flat cold "
                        "daylight or fluorescent; the split is the storytelling device. "
                        "Hard-edged shadow shapes on faces, no volumetric rendering - "
                        "that is the cel grammar",
            "color": "cool white and grey-blue (reality) against magenta and orange (stage / "
                     "hallucination); selectively high chroma accents, flat cel fills with "
                     "layered shading",
            "composition": "subject split by mirror or glass, sudden high-angle overhead, "
                            "extreme close-up, protagonist normal while background warps and "
                            "misaligns",
            "medium": "hand-painted cel animation, hard-edged highlights, flat color fills, "
                      "fine layered shading, film grain overlay",
            "mood": "paranoid, vertiginous, identity dissolving, voyeuristic dread",
            "camera": "sudden overhead, extreme close-up, mirror framing, disorienting angle shifts",
        },
        "negative": "photorealistic 3d render, soft airbrush shading, flat even lighting, "
                    "pastel palette, wide calm establishing shot, naturalistic lighting",
        "palette": [("#D8E2E8", "冷白"), ("#5A7086", "灰蓝"), ("#C42B72", "品红"),
                    ("#E08A2B", "舞台橙"), ("#1E2430", "夜蓝黑"), ("#8A9BA8", "玻璃反光灰")],
        "video": {
            "运动": "镜中影像的延迟动作、背景缓慢扭曲、灯光闪烁、人物突然转头",
            "运镜": "突然的俯视、快速变焦、镜面构图下的缓慢推进",
            "时长": "10 秒",
            "关键": "**色温分层**（现实冷 / 幻觉暖）和**镜面分割**是命门；只写「黑暗心理」会跑成普通恐怖动画",
        },
        "pitfalls": [
            "写 anime 会得到现代数字动画；要写 1990s cel animation / hand-painted cel / film grain",
            "3D 渲染和柔和喷枪阴影是这部片的反面，必须写进负向词",
            "不给色温分层规则，模型会把现实和幻觉拍成一个调子，叙事就没了",
        ],
        "see_also": ["anime-cel", "surrealism", "pop-art"],
        "source": "curated",
    },



    # >>> 新增完整片（fv_merge.py 生成，勿手改）BEGIN

    # ---------------------------------------------------- 今敏
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

    # ---------------------------------------------------- 大友克洋
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

    # ---------------------------------------------------- 押井守
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

    # ---------------------------------------------------- 宫崎骏
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

    # ---------------------------------------------------- 高畑勋
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

    # ---------------------------------------------------- 安德烈·塔可夫斯基
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

    # ---------------------------------------------------- 斯坦利·库布里克
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

    # ---------------------------------------------------- 黑泽明
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

    # ---------------------------------------------------- 小林正树
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

    # ---------------------------------------------------- 沟口健二
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

    # ---------------------------------------------------- 大卫·芬奇
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

    # ---------------------------------------------------- 丹尼斯·维伦纽瓦
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

    # ---------------------------------------------------- 奉俊昊
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

    # ---------------------------------------------------- 朴赞郁
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

    # ---------------------------------------------------- 李沧东
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

    # ---------------------------------------------------- 杨德昌
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

    # ---------------------------------------------------- 张艺谋
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

    # ---------------------------------------------------- 三池崇史
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

    # ---------------------------------------------------- 新海诚
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

    # ---------------------------------------------------- 英格玛·伯格曼
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

    # ---------------------------------------------------- 费德里科·费里尼
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

    # ---------------------------------------------------- 米开朗基罗·安东尼奥尼
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

    # ---------------------------------------------------- 让-吕克·戈达尔
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

    # ---------------------------------------------------- 让-皮埃尔·梅尔维尔
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

    # ---------------------------------------------------- 维姆·文德斯
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

    # ---------------------------------------------------- 奥逊·威尔斯
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

    # ---------------------------------------------------- 阿尔弗雷德·希区柯克
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

    # ---------------------------------------------------- 大卫·林奇
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

    # ---------------------------------------------------- 迈克尔·曼
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

    # ---------------------------------------------------- 弗朗西斯·福特·科波拉
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

    # ---------------------------------------------------- 马丁·斯科塞斯
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

    # ---------------------------------------------------- 约翰·卡朋特
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

    # ---------------------------------------------------- 威廉·弗莱德金
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

    # ---------------------------------------------------- 雷德利·斯科特
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

    # ---------------------------------------------------- 丹尼斯·维伦纽瓦
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

    # ---------------------------------------------------- 今敏
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

    # ---------------------------------------------------- 黑泽明
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

    # ---------------------------------------------------- 小林正树
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

    # ---------------------------------------------------- 奉俊昊
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

    # ---------------------------------------------------- 侯孝贤
    {
        "slug": "hou-hsiao-hsien-flowers-of-shanghai",
        "director_zh": "侯孝贤",
        "director_en": "Hou Hsiao-hsien",
        "director_slug": "hou-hsiao-hsien",
        "title_zh": "海上花",
        "title_en": "Flowers of Shanghai",
        "year": 1998,
        "one_liner": "**全片没有一场日光**——油灯、鸦片烟与一道道门，把长镜关进室内。",
        "core": [
            "全片室内、只用油灯与鸦片灯：**没有任何自然光**，光源永远在画面里且极小",
            "长镜穿过一道又一道门框，空间被门帘切成层层薄片",
            "鸦片烟把光变成雾，人物在烟雾里半隐半现",
            "构图静止且对称，人物坐在画面正中或两端，中间是空桌与烟灯"
        ],
        "visual": {
            "色彩": "暖琥珀、赭红、墨黑、烟灰；低照度暖调，几乎无冷色",
            "光影": "油灯与鸦片灯为唯一光源：小面积暖光 + 大面积深暗；烟散射出体积光",
            "笔触": "（电影媒介）35mm 胶片，柔焦，颗粒细，暗部有层次",
            "构图": "框中框（门帘层层套叠）、静止对称、纵深极深；人物小、坐姿固定",
            "材质": "丝绸、木、纸帘、瓷器、烟、油灯、鸦片烟具",
            "情绪": "昏沉、被围困的精致、时间的停滞"
        },
        "layers": {
            "style": "Hou Hsiao-hsien Flowers of Shanghai, entirely interior lamplit brothels, no daylight, long takes through layered doorways, opium haze",
            "lighting": "only oil lamps and opium lamps as sources, small warm pools against large deep dark, smoke scattering light into volume, no natural light anywhere",
            "color": "warm amber, ochre red, ink black, smoke grey; low-key warm with virtually no cool tones",
            "composition": "frame within frame through layered curtains, static symmetry, extreme depth, small seated figures with empty table between them",
            "medium": "35mm film, soft focus, fine grain, detailed shadows",
            "mood": "somnolent, gilded entrapment, stalled time",
            "camera": "very slow lateral tracking through doorways, static long takes, eye level"
        },
        "negative": "daylight, window light, handheld, fast cutting, saturated cool colours, modern interiors",
        "palette": [
            [
                "#8A5A2B",
                "油灯琥珀"
            ],
            [
                "#6B1F1A",
                "赭红"
            ],
            [
                "#141210",
                "墨黑"
            ],
            [
                "#8C8880",
                "烟灰"
            ],
            [
                "#C9A227",
                "灯焰金"
            ],
            [
                "#3E3A34",
                "木褐"
            ]
        ],
        "video": {
            "运动": "鸦片烟缓慢升起、灯焰轻晃、帘幕微动、人物极缓慢的动作",
            "运镜": "极慢横移穿门、静止长镜",
            "时长": "15 秒以上（短了就没有「时间停滞」）",
            "关键": "**光源必须只有油灯/鸦片灯，且画面里绝不见日光**；加窗光就毁掉整部片"
        },
        "pitfalls": [
            "写 period drama 会得到明亮的年代剧 → 这部片**没有自然光**，全靠油灯",
            "手持与快剪是反的",
            "门帘层层套叠的框中框是它的空间语法，不写会丢一半"
        ],
        "see_also": [
            "baroque",
            "zen-art"
        ],
        "title_original": "Flowers of Shanghai",
        "filmgrab": "https://film-grab.com/2025/08/31/flowers-of-shanghai/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/hsiao-hsien-hou/",
        "source": "curated"
    },
    {
        "slug": "hou-hsiao-hsien-millennium-mambo",
        "director_zh": "侯孝贤",
        "director_en": "Hou Hsiao-hsien",
        "director_slug": "hou-hsiao-hsien",
        "title_zh": "千禧曼波",
        "title_en": "Millennium Mambo",
        "year": 2001,
        "one_liner": "**霓虹、手持与台北夜店**——同一位导演最不「侯孝贤」的一部，却最合适做夜戏参考。",
        "core": [
            "大量手持跟拍（与他惯常的固定长镜相反），镜头贴着人物在人群里穿行",
            "霓虹色主导：青绿、品红、橙，高饱和且反射在湿面与玻璃上",
            "夜店段落用频闪与有色光，室外段落是冷蓝的街灯",
            "构图为贴近的肩后视角与不规则倾斜，而不是对称远景"
        ],
        "visual": {
            "色彩": "霓虹青绿、品红、橙、冷蓝；高饱和，暗部带色",
            "光影": "夜店频闪与有色舞台光；街头冷蓝街灯与湿面反射；大面积暗部有色偏",
            "笔触": "（电影媒介）35mm 胶片，颗粒明显，手持运动模糊",
            "构图": "肩后跟拍、不规则构图、人群遮挡；贴近而非远景",
            "材质": "玻璃、湿沥青、霓虹灯管、塑料、皮革、烟、酒",
            "情绪": "躁动、迷失、青春的消耗、夜里的不安"
        },
        "layers": {
            "style": "Hou Hsiao-hsien Millennium Mambo, hand-held neon Taipei nightlife, saturated club light, restless youth, shot on film",
            "lighting": "strobing coloured club light and cold blue street lamps, wet surfaces bouncing neon, large colour-cast shadows, no soft daylight",
            "color": "neon cyan-green, magenta, orange against cold blue; high saturation with colour in the shadows",
            "composition": "over-the-shoulder following shots, irregular tilted framing, crowd occlusion, close rather than distant",
            "medium": "35mm film, pronounced grain, hand-held motion blur",
            "mood": "restless, lost, youth burning away, nocturnal unease",
            "camera": "handheld following behind the subject, fast pan, strobing club interiors"
        },
        "negative": "static symmetrical long take, tripod stillness, natural light, desaturated palette, empty wide landscape",
        "palette": [
            [
                "#1E8C7A",
                "霓虹青绿"
            ],
            [
                "#C42B72",
                "霓虹品红"
            ],
            [
                "#D97426",
                "霓虹橙"
            ],
            [
                "#1E2A4A",
                "冷蓝街灯"
            ],
            [
                "#0F1210",
                "暗部黑"
            ],
            [
                "#8C9490",
                "湿沥青灰"
            ]
        ],
        "video": {
            "运动": "人群晃动、频闪、烟雾翻滚、雨水在霓虹下流动",
            "运镜": "手持贴身跟拍、快摇、穿过人群推进",
            "时长": "10 秒",
            "关键": "**手持 + 霓虹主光 + 高饱和**；写成固定长镜就变回他别的片子了"
        },
        "pitfalls": [
            "这是侯孝贤的**例外**，别套他惯常的固定长镜与低饱和",
            "冷蓝街灯与暖霓虹两套要并存，不要统一成一个调子",
            "手持不是失误，是这部片的语言"
        ],
        "see_also": [
            "cyberpunk",
            "pop-art"
        ],
        "title_original": "Millennium Mambo",
        "filmgrab": "https://film-grab.com/2023/04/05/millennium-mambo/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/hsiao-hsien-hou/",
        "source": "curated"
    },

    # ---------------------------------------------------- 杨德昌
    {
        "slug": "yang-edward-the-terrorizers",
        "director_zh": "杨德昌",
        "director_en": "Edward Yang",
        "director_slug": "edward-yang",
        "title_zh": "恐怖分子",
        "title_en": "The Terrorizers",
        "year": 1986,
        "one_liner": "**玻璃反射与冷调远景**——把暴力推到画外，用距离和静止说话。",
        "core": [
            "大量玻璃与镜面反射：人物被映在建筑与橱窗里，实体与影像叠在一起",
            "冷调低饱和：灰蓝、灰绿、白墙，几乎无暖色",
            "远景与静止机位为主，情绪靠距离而非特写",
            "结尾那场戏用静止与画外事件把暴力留在画框之外"
        ],
        "visual": {
            "色彩": "灰蓝、灰绿、白、水泥灰；极低饱和，冷调",
            "光影": "日光灯与阴天天光；均匀偏冷，阴影浅硬",
            "笔触": "（电影媒介）35mm 胶片，颗粒细，冷调干净",
            "构图": "玻璃反射叠影、框中框（窗、门、橱窗）、静止远景",
            "材质": "玻璃幕墙、混凝土、金属、旧公寓、电话、雨",
            "情绪": "疏离、冷硬、城市里的偶然与暴力"
        },
        "layers": {
            "style": "Edward Yang The Terrorizers, cold low-saturation urban alienation, glass reflection composition, distant static framing, 1980s Taipei",
            "lighting": "fluorescent and overcast cool daylight, even but hard and shallow, no warm sources",
            "color": "grey-blue, grey-green, white, cement grey; extremely low saturation and cool",
            "composition": "figures doubled in glass and shop windows, frame within frame, static distant shot, violence kept off-screen",
            "medium": "35mm film, fine grain, clean cool tonality",
            "mood": "alienated, cold, urban accident and violence",
            "camera": "locked-off distant shot, slow pan, framing through glass"
        },
        "negative": "warm cozy light, close-up intimacy, handheld, saturated colours, daylight golden hour",
        "palette": [
            [
                "#4A5A6B",
                "灰蓝"
            ],
            [
                "#5E6B5A",
                "灰绿"
            ],
            [
                "#C4C8C9",
                "白"
            ],
            [
                "#8C9490",
                "水泥灰"
            ],
            [
                "#1E2A32",
                "暗部黑"
            ],
            [
                "#2E4A5A",
                "玻璃青"
            ]
        ],
        "video": {
            "运动": "雨落、玻璃上的反光移动、车流、人物在远景里极少移动",
            "运镜": "固定远景、缓慢横移、隔着玻璃拍",
            "时长": "10 秒",
            "关键": "**必须隔着玻璃拍出叠影，且机位要远**；贴近的特写会毁掉它的疏离"
        },
        "pitfalls": [
            "写 crime 会得到紧张的犯罪片 → 这部片把暴力放在**画外**",
            "特写与手持是反的",
            "暖色与高饱和会破坏冷调"
        ],
        "see_also": [
            "photorealism",
            "precisionism"
        ],
        "title_original": "The Terrorizers",
        "filmgrab": "https://film-grab.com/2018/09/02/the-terrorizers/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/edward-yang/",
        "source": "curated"
    },

    # ---------------------------------------------------- 小津安二郎
    {
        "slug": "ozu-floating-weeds",
        "director_zh": "小津安二郎",
        "director_en": "Yasujiro Ozu",
        "director_slug": "yasujiro-ozu",
        "title_zh": "浮草",
        "title_en": "Floating Weeds",
        "year": 1959,
        "one_liner": "**小津罕见的彩色片**——饱和的红与彩绘布景，配上他标志性的低机位静止。",
        "core": [
            "小津少有的彩色作品：颜色被刻意夸张，红、黄、绿的色块面积大",
            "低机位固定构图与正面人物关系不变（他惯常的语法）",
            "布景有明显的**舞台感**：天空与远景是画出来的，颜色平涂",
            "室内用纸门透光，室外用硬日光，色彩不靠光影塑形"
        ],
        "visual": {
            "色彩": "正红、芥末黄、草绿、靛蓝；高饱和且平涂，舞台感强",
            "光影": "室内为纸门透射的柔光；室外为硬日光但阴影浅，颜色不靠光塑形",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩浓艳，颗粒细",
            "构图": "低机位固定、正面构图、并排而坐；彩绘背景把纵深压平",
            "材质": "纸障子、木、布、油纸伞、彩绘布景、榻榻米",
            "情绪": "温和里的失落、旧戏班的漂泊、克制的哀伤"
        },
        "layers": {
            "style": "Ozu Floating Weeds, rare colour Ozu, saturated painted backdrops, low static camera at tatami height, frontal staging",
            "lighting": "soft light through paper screens indoors, hard sunlight outdoors with shallow shadows, colour carried by surfaces not light",
            "color": "vermilion, mustard yellow, grass green, indigo; high saturation and flat, deliberately stage-like",
            "composition": "locked-off low camera, frontal staging, figures seated side by side, painted backdrop flattening the depth",
            "medium": "35mm colour film, rich saturated colour, fine grain",
            "mood": "gentle loss, a travelling troupe adrift, restrained grief",
            "camera": "locked-off low camera, no movement, pillow shots between scenes"
        },
        "negative": "handheld, moving camera, naturalistic muted colour, desaturated palette, realistic deep background",
        "palette": [
            [
                "#B0241F",
                "正红"
            ],
            [
                "#C9A227",
                "芥末黄"
            ],
            [
                "#4E8C3A",
                "草绿"
            ],
            [
                "#1F3A6E",
                "靛蓝"
            ],
            [
                "#E8E0CC",
                "纸门米"
            ],
            [
                "#6B5B45",
                "木褐"
            ]
        ],
        "video": {
            "运动": "几乎不动：纸门轻晃、布幡飘、人物端坐、水面微动",
            "运镜": "固定低机位；不要推拉摇移",
            "时长": "10 秒",
            "关键": "**低机位 + 正面构图 + 高饱和平涂色**；把颜色调自然就不是这部片了"
        },
        "pitfalls": [
            "写 50s Japanese drama 会得到低饱和怀旧调 → 这部片的彩色是**刻意夸张、平涂**的",
            "背景要舞台感（彩绘），写实远景是反的",
            "运镜是反的"
        ],
        "see_also": [
            "ukiyo-e",
            "pop-art"
        ],
        "title_original": "Floating Weeds",
        "filmgrab": "https://film-grab.com/2015/03/27/floating-weeds/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/yasujiro-ozu/",
        "source": "curated"
    },

    # ---------------------------------------------------- 黑泽清
    {
        "slug": "kiyoshi-kurosawa-pulse",
        "director_zh": "黑泽清",
        "director_en": "Kiyoshi Kurosawa",
        "director_slug": "kiyoshi-kurosawa",
        "title_zh": "脉冲",
        "title_en": "Pulse",
        "year": 2001,
        "one_liner": "**灰绿平光与门后的黑影**——把「连接」拍成一种可见的孤独，恐怖不靠打光。",
        "core": [
            "灰绿平光：日光灯与阴天天光，无方向、无戏剧性明暗，画面平淡得像监控",
            "大量空房间与走廊，人物常背对镜头或站在门框里",
            "黑影与人影出现在画面深处或门后，恐怖靠位置而非光",
            "数字摄影的冷绿调，暗部有噪点"
        ],
        "visual": {
            "色彩": "灰绿、青灰、污白、暗褐；极低饱和，绿色调明显",
            "光影": "均匀的日光灯与显示器光；无方向性，影子极浅；暗部保留噪点",
            "笔触": "（电影媒介）早期数字摄影，冷绿调，低对比，有噪点",
            "构图": "空房间与长走廊的正面纵深、门框内的人影、人物背对；大量留白",
            "材质": "水泥、瓷砖、CRT 显示器、电缆、旧家具、塑料帘、雨",
            "情绪": "孤独、疏离、被连接吞没的虚无"
        },
        "layers": {
            "style": "Kiyoshi Kurosawa Pulse, flat grey-green digital, empty rooms and corridors, dread from placement not light, early internet ghost story",
            "lighting": "even fluorescent and monitor glow with no direction, very shallow shadows, low contrast, noise in the darks",
            "color": "grey-green, slate, soiled white, dark brown; extremely low saturation with a clear green cast",
            "composition": "frontal depth down empty rooms and corridors, figures inside doorframes or facing away, large empty areas",
            "medium": "early digital cinematography, cool green cast, low contrast, visible noise",
            "mood": "lonely, alienated, void of endless connection",
            "camera": "static long take, slow pan, figures held at distance, no handheld"
        },
        "negative": "dramatic chiaroscuro, warm light, jump scares, saturated colours, handheld chaos, cgi",
        "palette": [
            [
                "#6E7A6E",
                "灰绿"
            ],
            [
                "#8C9490",
                "青灰"
            ],
            [
                "#C4C0B4",
                "污白"
            ],
            [
                "#4A4238",
                "暗褐"
            ],
            [
                "#2E3A32",
                "暗绿"
            ],
            [
                "#5A6B6B",
                "显示器青"
            ]
        ],
        "video": {
            "运动": "几乎不动：灰尘、屏幕微闪、雨、人物极缓慢地转身",
            "运镜": "固定机位、极慢横移；不要运镜",
            "时长": "10–15 秒",
            "关键": "**光要平、画面要空、人出现在门框或深处**；加戏剧打光就不是黑泽清"
        },
        "pitfalls": [
            "写 horror 会得到高对比惊吓片 → 这部片的恐怖在平淡里",
            "暖光与饱和是反的",
            "空房间与走廊的留白是语法，塞满元素就失去「多出来的那个人」"
        ],
        "see_also": [
            "minimalism-art",
            "realism"
        ],
        "title_original": "Pulse",
        "filmgrab": "https://film-grab.com/2026/07/22/pulse/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/kiyoshi-kurosawa/",
        "source": "curated"
    },

    # ---------------------------------------------------- 米开朗基罗·安东尼奥尼
    {
        "slug": "antonioni-the-passenger",
        "director_zh": "米开朗基罗·安东尼奥尼",
        "director_en": "Michelangelo Antonioni",
        "director_slug": "michelangelo-antonioni",
        "title_zh": "过客",
        "title_en": "The Passenger",
        "year": 1975,
        "one_liner": "**七分钟不剪断的最后一个镜头**——北非的白墙、沙漠与蓝窗，色块比对话更响。",
        "core": [
            "结尾那个七分钟的长镜：镜头缓慢穿过铁窗、庭院与广场，叙事在画外完成",
            "北非的白墙、赭土、钴蓝窗与绿百叶是主要色块，面积大且干净",
            "构图被建筑切割：窗、门、拱、栅栏把画面分成几何块",
            "大量远景与背影，人物常被放在画面边缘或深处"
        ],
        "visual": {
            "色彩": "白墙、赭土、钴蓝、绿百叶、沙黄；高调明快，色块干净",
            "光影": "北非硬日光与白墙反光；影子短而硬，室内为拱窗的柔散光",
            "笔触": "（电影媒介）35mm 彩色胶片，色彩明快，颗粒细",
            "构图": "建筑切割画面（窗、拱、栅栏）、远景与背影、人物偏置；长镜缓慢横移",
            "材质": "白灰墙、木百叶、铁栅栏、沙、玻璃、旧车、缆绳",
            "情绪": "逃离、身份置换的空洞、自由与虚无并存"
        },
        "layers": {
            "style": "Antonioni The Passenger, North African white walls and cobalt, architecture slicing the frame, famous seven-minute final take, identity swap",
            "lighting": "hard North African sun with white-wall bounce, short hard shadows, soft arched-window light indoors",
            "color": "white wall, ochre earth, cobalt blue, green shutters, sand yellow; high key with large clean blocks",
            "composition": "frame divided by windows, arches and railings, distant figures often seen from behind, subject pushed to the edge, slow lateral camera",
            "medium": "35mm colour film, bright tonality, fine grain",
            "mood": "escape, hollowness of swapped identity, freedom and void together",
            "camera": "very long slow lateral take, distant observation, camera lingering after the subject leaves"
        },
        "negative": "handheld, close-up driven coverage, dark low-key grade, cluttered composition, saturated sunset",
        "palette": [
            [
                "#E8E4DC",
                "白墙"
            ],
            [
                "#C9A227",
                "赭土"
            ],
            [
                "#1F4A8C",
                "钴蓝窗"
            ],
            [
                "#4E7A3A",
                "绿百叶"
            ],
            [
                "#D8C4A0",
                "沙黄"
            ],
            [
                "#2E3A42",
                "暗部灰"
            ]
        ],
        "video": {
            "运动": "窗帘被风掀起、沙尘、人物在远景里缓慢走动、水面",
            "运镜": "极长缓慢横移；镜头要比人物待得久",
            "时长": "15 秒以上",
            "关键": "**色块要大要干净 + 长镜横移 + 人物在远景**；贴近特写会毁掉它"
        },
        "pitfalls": [
            "写 thriller 会得到类型片节奏 → 这部片是极慢的观察",
            "手持与特写是反的",
            "把颜色调灰会失去北非的明快"
        ],
        "see_also": [
            "precisionism",
            "minimalism-art"
        ],
        "title_original": "The Passenger",
        "filmgrab": "https://film-grab.com/2014/08/25/the-passenger/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/michelangelo-antonioni/",
        "source": "curated"
    },

    # ---------------------------------------------------- 罗贝尔·布列松
    {
        "slug": "bresson-a-man-escaped",
        "director_zh": "罗贝尔·布列松",
        "director_en": "Robert Bresson",
        "director_slug": "robert-bresson",
        "title_zh": "死囚越狱",
        "title_en": "A Man Escaped",
        "year": 1956,
        "one_liner": "**只拍手、门与绳索**——画外音与声音先于画面，把「等待」拍成动作。",
        "core": [
            "只拍手、门、勺、绳索的局部特写：动作被拆成零件，人物表情几乎不出现",
            "画外音叙述与画面分离，声音（脚步、钥匙、火车）先于画面出现",
            "灰阶干净平均，无强反差，画面朴素",
            "构图扁平克制，人物贴墙或坐在床沿，空间是牢房的几何"
        ],
        "visual": {
            "色彩": "黑白；灰阶干净平均，无强反差",
            "光影": "自然散射与窗光；柔和、无戏剧光源，阴影浅",
            "笔触": "（电影媒介）35mm 黑白胶片，颗粒细，画面极简",
            "构图": "局部特写（手、门、工具）、扁平构图、人物贴墙；静止",
            "材质": "木、铁、布、绳索、勺、纸、石墙、窗栏",
            "情绪": "克制的紧张、孤独的坚持、被抽离的情感"
        },
        "layers": {
            "style": "Robert Bresson A Man Escaped, 35mm black and white, hands and doors as subject, offscreen sound, austere prison geometry",
            "lighting": "natural diffuse and window light, soft and undramatic, shallow shadows, no decorative contrast",
            "color": "black and white; clean even grey scale without strong contrast",
            "composition": "close-up of hands and objects, flat restrained framing, figures against walls, static",
            "medium": "35mm black-and-white film, fine grain, austere image",
            "mood": "restrained tension, solitary persistence, emotion drained out",
            "camera": "static, precise reframing, no movement, sound arriving before image"
        },
        "negative": "dramatic lighting, expressive close-up of faces, handheld, saturated color, sweeping camera movement, music cues",
        "palette": [
            [
                "#3E3A38",
                "暗灰"
            ],
            [
                "#8C8880",
                "中灰"
            ],
            [
                "#C4C0B8",
                "浅灰"
            ],
            [
                "#0A0A0A",
                "墨黑"
            ],
            [
                "#E0DCD4",
                "窗光白"
            ],
            [
                "#5E5A54",
                "石墙灰"
            ]
        ],
        "video": {
            "运动": "手部极精确的小动作、门开合、绳索摩擦、人物静立",
            "运镜": "固定机位、精确重新取景；不要运镜",
            "时长": "10 秒",
            "关键": "**拍手不拍脸 + 声音先行**；加表演式特写与配乐就变成普通越狱片"
        },
        "pitfalls": [
            "写 prison escape 会得到紧张刺激的越狱片 → 这部片是冷、静、去表演的",
            "面部表情特写是反的",
            "配乐与戏剧打光都冲突"
        ],
        "see_also": [
            "precisionism",
            "photorealism"
        ],
        "title_original": "A Man Escaped",
        "filmgrab": "https://film-grab.com/2026/06/18/a-man-escaped/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/robert-bresson/",
        "source": "curated"
    },
    {
        "slug": "bresson-mouchette",
        "director_zh": "罗贝尔·布列松",
        "director_en": "Robert Bresson",
        "director_slug": "robert-bresson",
        "title_zh": "穆谢特",
        "title_en": "Mouchette",
        "year": 1967,
        "one_liner": "**灰调乡野与陷阱**——用无人称的远景记录一个被围困的孩子。",
        "core": [
            "灰调乡野：湿草、泥、雨、石墙，颜色被压到近乎单色",
            "大量远景与背影，人物在画面里很小，环境占大面积",
            "动作被抽离：事件发生在画外或镜头之外，观众只看到前因后果",
            "构图扁平，人物贴墙、蹲在田埂或站在门口"
        ],
        "visual": {
            "色彩": "灰绿、泥褐、石灰白、暗黑；极低饱和，近乎单色",
            "光影": "阴天散射与雨；柔和、无戏剧光源，暗部保留细节",
            "笔触": "（电影媒介）35mm 近单色胶片，颗粒明显，色调冷脏",
            "构图": "远景与背影、扁平构图、人物贴墙或蹲伏；大量环境",
            "材质": "湿草、泥、雨、石墙、粗布、木、猎具、陶器",
            "情绪": "被围困、屈辱、沉默的绝望"
        },
        "layers": {
            "style": "Robert Bresson Mouchette, near-monochrome grey rural, distant impersonal framing, offscreen action, austere misery",
            "lighting": "overcast diffuse with rain, soft and undramatic, detailed shadows, no dramatic source",
            "color": "grey-green, mud brown, lime white, deep black; extremely low saturation, close to monochrome",
            "composition": "distant shots with small figures seen from behind, flat framing, figures pressed against walls or crouching, environment dominant",
            "medium": "35mm film, pronounced grain, cold dirty tonality",
            "mood": "trapped, humiliated, silent despair",
            "camera": "static distant shot, slow pan, precise reframing, no handheld"
        },
        "negative": "dramatic lighting, close-up of emotion, handheld, saturated color, sweeping music cues, warm tones",
        "palette": [
            [
                "#5E6B5A",
                "灰绿"
            ],
            [
                "#6B5B45",
                "泥褐"
            ],
            [
                "#C4C0B4",
                "石灰白"
            ],
            [
                "#0F0F0F",
                "暗黑"
            ],
            [
                "#8C9490",
                "雨幕灰"
            ],
            [
                "#4A4438",
                "湿草褐"
            ]
        ],
        "video": {
            "运动": "雨落、湿草被风压、水面、人物在远景里极小的动作",
            "运镜": "固定远景、缓慢横移",
            "时长": "10 秒",
            "关键": "**人物要小、环境要大、颜色要压到近乎单色**；贴近与暖调都反"
        },
        "pitfalls": [
            "写 coming-of-age 会得到温情成长片 → 这部片是冷、远、去戏剧化的",
            "特写与手持是反的",
            "事件发生在画外是它的手法，不要补上"
        ],
        "see_also": [
            "realism",
            "minimalism-art"
        ],
        "title_original": "Mouchette",
        "filmgrab": "https://film-grab.com/2026/07/09/mouchette/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/robert-bresson/",
        "source": "curated"
    },

    # ---------------------------------------------------- 小林正树
    {
        "slug": "kobayashi-the-human-condition-i",
        "director_zh": "小林正树",
        "director_en": "Masaki Kobayashi",
        "director_slug": "masaki-kobayashi",
        "title_zh": "人间的条件 I：纯爱篇",
        "title_en": "The Human Condition I: No Greater Love",
        "year": 1959,
        "one_liner": "**宽银幕黑白里的满洲**——泥、雪与矿场的人群横向铺陈，体制的碾压迫进每一个远景。",
        "core": [
            "宽银幕黑白，人群被横向铺陈在矿场、雪原与站台上",
            "泥、雪、烟尘是主要材质，衣服永远是脏的",
            "大量远景与俯视，个体在体制的几何里变得极小",
            "构图常把人物压在画面下缘，上方是大面积的天或山"
        ],
        "visual": {
            "色彩": "黑白；灰阶开阔，雪原的高光与矿场的深黑拉开极大差距",
            "光影": "阴天散射与雪面反光；矿场用火光与烟遮挡，暗部保留细节",
            "笔触": "（电影媒介）35mm 黑白宽银幕胶片，颗粒明显",
            "构图": "宽银幕横向群像、远景俯视、低地平线；人物小且偏置",
            "材质": "泥、雪、煤、烟、粗布、铁、木、马",
            "情绪": "沉重、被碾压的尊严、体制的窒息"
        },
        "layers": {
            "style": "Kobayashi The Human Condition, 2.35:1 black and white, Manchurian labour camps, horizontal crowd staging, institutional weight",
            "lighting": "overcast diffuse with strong snow bounce, firelight and smoke in the mines, wide grey range with detailed darks",
            "color": "black and white; wide grey scale, snow highlights against deep black mine interiors",
            "composition": "widescreen horizontal crowd staging, distant high angles, low horizon with large sky or mountain above, small off-centre figures",
            "medium": "35mm black-and-white widescreen film, pronounced grain",
            "mood": "heavy, dignity ground down, institutional suffocation",
            "camera": "static wide, slow lateral tracking across crowds, high distant angle"
        },
        "negative": "close-up driven coverage, warm color, handheld intimacy, clean costumes, narrow framing",
        "palette": [
            [
                "#0F0F0F",
                "矿场黑"
            ],
            [
                "#3E3A34",
                "泥褐"
            ],
            [
                "#8C8C86",
                "中灰"
            ],
            [
                "#E8E8E4",
                "雪白"
            ],
            [
                "#5E5A54",
                "烟灰"
            ],
            [
                "#6B6459",
                "粗布灰"
            ]
        ],
        "video": {
            "运动": "雪落、烟囱冒烟、人群缓慢移动、马匹与推车",
            "运镜": "固定宽景、缓慢横移、高位俯视",
            "时长": "10 秒",
            "关键": "**宽银幕 + 横向人群 + 低地平线**；逼近特写会丢掉体制的尺度感"
        },
        "pitfalls": [
            "写 war epic 会得到聚焦英雄的战争片 → 这部片的重点是**人群与尺度**",
            "彩色与特写是反的",
            "材质要脏（泥、煤、雪），干净制服会毁掉它"
        ],
        "see_also": [
            "realism",
            "precisionism"
        ],
        "source": "curated",
        "title_original": "The Human Condition I: No Greater Love",
        "filmgrab": "https://film-grab.com/2025/07/01/the-human-condition-i-no-greater-love/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/masaki-kobayashi/"
    },

    # ---------------------------------------------------- 克日什托夫·基耶斯洛夫斯基
    {
        "slug": "kieslowski-three-colours-blue",
        "director_zh": "克日什托夫·基耶斯洛夫斯基",
        "director_en": "Krzysztof Kieślowski",
        "director_slug": "krzysztof-kieslowski",
        "title_zh": "蓝",
        "title_en": "Three Colours: Blue",
        "year": 1993,
        "one_liner": "**整片被一种蓝统治**——泳池、吊灯、糖纸，蓝是情绪唯一的出口。",
        "core": [
            "蓝色在几乎每个画面里都出现一次：泳池、吊灯、玻璃纸、光斑、墨水",
            "颜色的用法是**主观的**：蓝不是环境色，而是人物的心理状态外化",
            "大量特写与浅景深：手、糖块、乐谱、皮肤，把世界压缩到触觉层面",
            "光斑与反射频繁入画（吊灯、玻璃），把画面切成碎片"
        ],
        "visual": {
            "色彩": "钴蓝、深蓝、金褐、琥珀、纯黑；蓝是唯一被允许饱和的颜色",
            "光影": "柔和的自然侧光与窗光；金色调用于室内暖处，暗部偏蓝",
            "笔触": "（电影媒介）35mm 彩色胶片，柔焦，颗粒细，色彩纯净",
            "构图": "浅景深特写、框中框、反射与光斑入画；人物常偏置或只出现局部",
            "材质": "玻璃、吊灯水晶、糖纸、乐谱纸、水、皮肤、羽毛",
            "情绪": "哀悼、内敛、情感的冻结与缓慢融化"
        },
        "layers": {
            "style": "Kieślowski Three Colours: Blue, subjective dominant blue, tactile close-ups, shallow depth of field, European art cinema",
            "lighting": "soft natural side light and window light, warm gold in interiors against blue-leaning shadows, no dramatic key",
            "color": "cobalt and deep blue as the only saturated hue, against gold-brown, amber and pure black; colour carries emotion rather than describing place",
            "composition": "shallow-focus close-up of hands and objects, frame within frame, reflections and light blobs entering the frame, partial figures",
            "medium": "35mm colour film, soft focus, fine grain, pure colour",
            "mood": "mourning, restraint, frozen feeling slowly thawing",
            "camera": "static close-up, slow drift, shallow focus, occasional slow push"
        },
        "negative": "multi-hue palette, saturated warm colours, handheld, wide establishing shots, busy composition",
        "palette": [
            [
                "#1F3A8C",
                "钴蓝"
            ],
            [
                "#141E4A",
                "深蓝"
            ],
            [
                "#8A6A2B",
                "金褐"
            ],
            [
                "#C9A227",
                "琥珀"
            ],
            [
                "#0A0A0A",
                "纯黑"
            ],
            [
                "#C4CFE0",
                "冷白蓝"
            ]
        ],
        "video": {
            "运动": "水波、吊灯水晶轻晃、糖纸被捏皱、光斑移动",
            "运镜": "静止特写、极慢推进；浅景深",
            "时长": "10 秒",
            "关键": "**每个画面都要有蓝，且蓝是唯一饱和色**；多色会立刻稀释掉它的心理焦点"
        },
        "pitfalls": [
            "写 European drama 会得到普通文艺片 → 蓝是**主观的、被强制的**，不是环境色",
            "多色调色会毁掉「一种蓝」的结构",
            "手持与大全景是反的（它靠特写与浅景深）"
        ],
        "see_also": [
            "minimalism-art",
            "photorealism"
        ],
        "title_original": "Three Colours: Blue",
        "filmgrab": "https://film-grab.com/2014/09/15/three-colours-blue/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/krzysztof-kieslowski/",
        "source": "curated"
    },

    # ---------------------------------------------------- 香特尔·阿克曼
    {
        "slug": "akerman-jeanne-dielman",
        "director_zh": "香特尔·阿克曼",
        "director_en": "Chantal Akerman",
        "director_slug": "chantal-akerman",
        "title_zh": "让娜·迪尔曼",
        "title_en": "Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles",
        "year": 1975,
        "one_liner": "**固定机位与走廊中景的重复**——把家务拍成结构，颜色只有墙的黄与围裙的蓝。",
        "core": [
            "固定机位、正面中景，摄影机从不移动：家务被完整拍完，不省略",
            "重复是结构：同一动作在三天里以几乎相同的镜头完成，微小的偏移就是叙事",
            "构图以走廊、厨房、客厅的固定视角为主，人物在其中进出画框",
            "颜色被严格限制：墙的黄、围裙的蓝、褐木与米白"
        ],
        "visual": {
            "色彩": "芥末黄、钴蓝（围裙）、褐、米白；低饱和，色块固定且重复",
            "光影": "室内均匀的实用光（顶灯、台灯）；无戏剧性打光，阴影平",
            "笔触": "（电影媒介）16mm/35mm 彩色胶片，颗粒可见，色调朴素",
            "构图": "固定正面中景、走廊纵深的对称、门框切成画格；人物进出画框",
            "材质": "墙纸、木桌、瓷、布、金属锅、塑料、日光灯",
            "情绪": "日常的重复、被结构化的时间、平静中的压迫"
        },
        "layers": {
            "style": "Chantal Akerman Jeanne Dielman, fixed frontal camera, domestic repetition as structure, real-time duration, limited palette",
            "lighting": "even practical interior light (ceiling lamp, table lamp), flat and undramatic, shallow shadows, no key light",
            "color": "mustard yellow, cobalt blue apron, brown, off-white; low saturation with a handful of repeated flat colour blocks",
            "composition": "locked-off frontal medium shot, symmetrical corridor depth, doorframes dividing the frame into panels, subject entering and leaving",
            "medium": "16mm/35mm colour film, visible grain, plain tonality",
            "mood": "domestic repetition, structured time, calm oppression",
            "camera": "completely locked-off frontal medium, no movement whatsoever, real-time duration"
        },
        "negative": "moving camera, handheld, fast cutting, close-up coverage, dramatic lighting, saturated multi-hue palette",
        "palette": [
            [
                "#C9A227",
                "芥末黄"
            ],
            [
                "#1F3A8C",
                "围裙钴蓝"
            ],
            [
                "#6B4A2B",
                "褐"
            ],
            [
                "#E8E4DC",
                "米白"
            ],
            [
                "#8C8C86",
                "瓷灰"
            ],
            [
                "#3E3A34",
                "暗褐"
            ]
        ],
        "video": {
            "运动": "极少：水龙头、蒸汽、手部动作、窗帘极轻的晃动",
            "运镜": "完全固定；不要任何运镜",
            "时长": "15 秒以上（短了就失去「真实时间」）",
            "关键": "**机位固定、动作完整不省略、颜色只有那几块**；加运镜或快剪就完全反了"
        },
        "pitfalls": [
            "写 domestic drama 会得到有配乐与运镜的家庭剧 → 这部片是固定的、实时的、不省略的",
            "任何运镜都破坏它",
            "颜色必须节制到只剩几块，多色会失去结构感"
        ],
        "see_also": [
            "minimalism-art",
            "realism"
        ],
        "title_original": "Jeanne Dielman, 23 quai du Commerce, 1080 Bruxelles",
        "filmgrab": "https://film-grab.com/2022/02/16/jeanne-dielman-23-quai-du-commerce-1080-bruxelles/",
        "crew": {},
        "filmgrab_director": "https://film-grab.com/category/directors/chantal-akerman/",
        "source": "curated"
    },

    # ---------------------------------------------------- 蔡明亮
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

    # ---------------------------------------------------- 尼古拉斯·温丁·雷弗恩
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

    # ---------------------------------------------------- 泰伦斯·马力克
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
    # <<< 新增完整片 END
]


def director_index():
    """按导演分组，用于 40-films/<导演>/ 的目录结构与导演索引页。

    返回 [(director_slug, {director_zh, director_en, films:[...]})]
    按导演中文名的出现顺序排列（保持 FILMS 里的编排顺序，不按字母重排——
    手写顺序本身就是一种策展，按 slug 排序会把它毁掉）。
    """
    order = []
    by = {}
    for f in FILMS:
        ds = f["director_slug"]
        if ds not in by:
            by[ds] = {"director_slug": ds,
                      "director_zh": f["director_zh"],
                      "director_en": f["director_en"],
                      "films": []}
            order.append(ds)
        by[ds]["films"].append(f)
    return [(ds, by[ds]) for ds in order]


def by_slug(slug):
    for f in FILMS:
        if f["slug"] == slug:
            return f
    return None


def stats():
    """现算统计，不写死数字（本库因为写死统计吃过亏）。"""
    return {
        "films": len(FILMS),
        "directors": len(director_index()),
        "curated": sum(1 for f in FILMS if f.get("source") == "curated"),
        "inferred": sum(1 for f in FILMS if f.get("source") != "curated"),
    }


if __name__ == "__main__":
    s = stats()
    print("电影风格库：%d 部片 / %d 位导演（手写 %d，推断 %d）"
          % (s["films"], s["directors"], s["curated"], s["inferred"]))
    for ds, d in director_index():
        print("  %-14s %-22s %d 部" % (ds, d["director_zh"], len(d["films"])))
        for f in d["films"]:
            print("      %-38s %s %s" % (f["slug"], f["year"], f["title_zh"]))

# ------------------------------------------------------------------ 导演索引
# 每位导演在 film-grab 上的分类页。**集中一处**而不是逐条写进每部片：
# 手写时只给每导演的第一部片补了 URL，第二部就成了空链接（实测踩到）。
# 集中映射 + 模块加载时兜底，就不存在「漏了某部」这种状态。
FILMGRAB_DIRECTORS = {
    "tarkovsky": "andrei-tarkovsky",
    "wong-kar-wai": "wong-kar-wai",
    "kubrick": "stanley-kubrick",
    "kurosawa": "akira-kurosawa",
    "bong-joon-ho": "joon-ho-bong",
    "villeneuve": "denis-villeneuve",
    "fincher": "david-fincher",
    "hou-hsiao-hsien": "hsiao-hsien-hou",
    "godard": "jean-luc-godard",
    "yang": "edward-yang",
    "kobayashi": "masaki-kobayashi",
    "antonioni": "michelangelo-antonioni",
    "satoshi-kon": "satoshi-kon",
    "bergman": "ingmar-bergman",
    "carpenter": "john-carpenter",
    "chantal-akerman": "chantal-akerman",
    "coppola": "francis-ford-coppola",
    "edward-yang": "edward-yang",
    "fellini": "federico-fellini",
    "friedkin": "william-friedkin",
    "hayao-miyazaki": "hayao-miyazaki",
    "hitchcock": "alfred-hitchcock",
    "isao-takahata": "isao-takahata",
    "katsuhiro-otomo": "katsuhiro-otomo",
    "kiyoshi-kurosawa": "kiyoshi-kurosawa",
    "krzysztof-kieslowski": "krzysztof-kieslowski",
    "lee-chang-dong": "chang-dong-lee",
    "lynch": "david-lynch",
    "mamoru-oshii": "mamoru-oshii",
    "masaki-kobayashi": "masaki-kobayashi",
    "melville": "jean-pierre-melville",
    "michael-mann": "michael-mann",
    "michelangelo-antonioni": "michelangelo-antonioni",
    "miike": "takashi-miike",
    "mizoguchi": "kenji-mizoguchi",
    "nicolas-winding-refn": "nicolas-winding-refn",
    "park-chan-wook": "chan-wook-park",
    "ridley-scott": "ridley-scott",
    "robert-bresson": "robert-bresson",
    "scorsese": "martin-scorsese",
    "shinkai": "makoto-shinkai",
    "terrence-malick": "terrence-malick",
    "tsai-ming-liang": "tsai-ming-liang",
    "welles": "orson-welles",
    "wenders": "wim-wenders",
    "yasujiro-ozu": "yasujiro-ozu",
    "zhang": "zhang-yimou",
}

for _f in FILMS:
    _ds = _f["director_slug"]
    if _ds not in FILMGRAB_DIRECTORS:
        raise KeyError("导演 %s 缺 film-grab 分类页映射 —— 加上它，"
                       "否则卡片的导演索引链接会是空的" % _ds)
    # 手写值优先，缺了才由映射补（两者一致时结果相同）
    _f.setdefault("filmgrab_director",
                  "https://film-grab.com/category/directors/%s/"
                  % FILMGRAB_DIRECTORS[_ds])
