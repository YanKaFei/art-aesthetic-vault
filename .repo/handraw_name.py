# -*- coding: utf-8 -*-
"""
handraw_name.py —— 给 274 条手绘风格起**中文名**（原来只有编号）。

## 为什么要有名字

原来这些卡叫 `手绘001`…`手绘274`。编号适合做**id**（稳定、无歧义），
但不适合做**名字** —— 没有人能记住「手绘137 是什么」，也没法在对话里
说「我要那种手绘137 的感觉」。名字要能被人复述。

## 名字从哪来：traits 为主，生图名校验

每条 handraw 风格有四样材料：

    number           编号（保留为 slug，不动）
    generation_name  英文生图名，如 `Playful Deadpan Doodle`（274 条全有）
    traits           中文核心特征（**254 条有，20 条为空**）
    reference        索引标签（不是描述，不参与命名）

命名走这条线：

    1. 从 traits 里按词表抽出**有角色**的关键词（媒介/笔法/风格/色/主题/情绪）
    2. 按「越靠前越有辨识度」排序，取最能定义这条的两个词
    3. 用英文生图名做**媒介与技法校验**（两边不一致时以 traits 为准，
       但要在依据里记下这次不一致，方便回看）
    4. traits 为空的 20 条，退回把生图名的媒介词译成中文，
       并显式标 `basis = generation_name` —— **缺依据要显形，不要伪装**

## 每条名字都带得出依据

返回结构里 `from` 是「这个名字用到了哪几个词」，`traits` 是那句原文。
`tests/handraw_name_test.py` 有一条机械检查：`basis=traits` 的名字，
`from` 里至少有一个词能在 traits 原文里找到。

这是本库一贯的态度：**名字也是结论，结论要能核对**。

## 手工改写

规则抽出来的名字有时读着别扭（中文画派名讲究，不像英文那样能直接堆词）。
所以留了一张 `OVERRIDES` 表 —— 手工改写**只换字面，不换依据**：
改写过的名字照样要能在 traits 里找到 `from` 里的词，检查一样跑。

别把 OVERRIDES 当成「随便起名」的入口：它存在的理由是**可读性**，
不是绕过可核对性。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# ⚠ **不能** `import mv_handraw`：mv_handraw._blueprint 里要 import 本模块
# 拿名字，两边一互相导入就成了循环 —— 谁先被导入，另一个就读到半成品，
# 表现为「别名全空」。实测就是这样：单独跑都好，按测试的导入顺序就全空。
# 所以这里**直接读 styles.json**，自己算路径，不依赖 mv_handraw。
import handraw_lexicon as LX  # noqa: E402
import json as _json  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
_VAULT = os.path.dirname(_HERE)
STYLES_JSON = os.path.join(_VAULT, LX.STYLES_JSON)


def load_entries():
    with open(STYLES_JSON, encoding="utf-8") as f:
        return _json.load(f)

# ------------------------------------------------------------------ 词表
# 角色决定这个词在名字里的位置：
#   medium   媒介（放最后：…漫画 / …线稿 / …绘本）
#   style    风格修饰（放最前）
#   color    色彩（可作中段）
#   subject  主题（人物/动物/城市…）
#   mood     情绪（冷脸/治愈/怪诞…）
ROLE = {}
for _w in ("漫画", "线稿", "涂鸦", "绘本", "插画", "速写", "素描", "连环画",
           "赛璐珞", "动画", "贴纸", "手帐", "拼贴", "剪纸", "版画", "丝网印刷",
           "马克笔", "水彩", "水粉", "丙烯", "油画", "水墨", "墨线", "钢笔",
           "圆珠笔", "铅笔", "炭笔", "色粉", "壁画", "海报", "广告画", "插画风"):
    ROLE[_w] = "medium"

for _w in ("极简", "松散", "粗糙", "精致", "细密", "密集", "清线", "几何",
           "抽象", "写意", "工笔", "平涂", "大留白", "白底", "复古", "现代",
           "古典", "民族", "民俗", "装饰", "高对比", "低饱和", "高饱和",
           "负空间", "单线", "连续线", "排线", "交叉排线", "粗线", "细线",
           "黑白", "冷淡", "温柔", "硬朗", "柔软", "弹性", "断裂", "抖动",
           "厚涂", "透明", "颗粒", "电影感", "图形化", "符号化"):
    ROLE.setdefault(_w, "style")

for _w in ("冷脸", "冷幽默", "幽默", "荒诞", "怪诞", "治愈", "温柔", "孤独",
           "安静", "诗意", "疯狂", "焦虑", "日常", "生活", "少女", "童趣",
           "奇幻", "科幻", "都市", "怪谈", "妖怪", "朋克", "恶搞", "讽刺",
           "社论", "情绪", "叙事", "童话", "梦境", "超现实"):
    ROLE.setdefault(_w, "mood")

for _w in ("人物", "角色", "女孩", "少女", "动物", "拟人", "怪物", "生物",
           "城市", "乡村", "建筑", "风景", "静物", "群像", "家庭", "职业",
           "时尚", "服装", "头像", "半身", "全身", "场景"):
    ROLE.setdefault(_w, "subject")

for _w in ("白底", "点色", "撞色", "灰", "橙", "蓝", "绿", "红", "黄", "青",
           "赭石", "米白", "粉彩", "马卡龙", "糖果色", "矿物色", "暖色", "冷色"):
    ROLE.setdefault(_w, "color")


# 第二批：实测 traits 里的高频词（原表漏掉的，会让抽词退回「手绘」这种废词）
for _w in ("钢笔速写", "圆珠笔", "手写", "手帐感", "抠图感", "厚轮廓",
           "细轮廓", "无阴影", "单色", "双色", "三色", "大色块", "小色块",
           "撞色块", "亮色", "暗色", "中性色", "纸感", "纸纹", "印刷感",
           "纹理", "笔压", "速写感", "草图感", "完成度低", "反精致"):
    ROLE.setdefault(_w, "style")
for _w in ("拟人动物", "小人物", "大头", "半身像", "全身像", "群像感",
           "女性", "男性", "老人", "儿童", "宠物", "猫咪", "鸟类",
           "植物", "花卉", "食物", "器物", "室内", "街景", "自然"):
    ROLE.setdefault(_w, "subject")
for _w in ("反鸡汤", "自嘲", "冷面", "一本正经", "无厘头", "荒诞感", "疏离",
           "克制", "松弛", "亲密", "温馨", "安静感", "孤独感", "怀旧",
           "复古感", "未来感", "神秘", "妖异", "黑暗", "治愈感"):
    ROLE.setdefault(_w, "mood")
for _w in ("黑墨", "蓝橙", "黄橙蓝绿", "红蓝黄", "米色", "灰蓝", "青绿",
           "赭石色", "棕橙", "奶油白", "芥末黄"):
    ROLE.setdefault(_w, "color")
for _w in ("清线漫画", "水墨风", "铅笔淡彩", "钢笔淡彩", "马克笔叠色",
           "水彩晕染", "水墨晕染", "透明叠染", "湿边晕染", "颗粒质感",
           "丝网感", "木刻感"):
    ROLE.setdefault(_w, "medium")


# 第三批：补上 36 条「无逐字命中」条目的说法（实测跑 `--stats` 找出来的）。
# 这些词都是 traits 原文里**逐字存在**的，只是前两批词表没收。
for _w in ("图腾", "隐喻", "低保真", "失控", "弯曲结构", "极端比例",
           "原生艺术", "商业插画", "圆润人物", "优雅留白", "极少线条",
           "粉彩", "低对比", "新国风", "流畅线条", "山海经", "异兽",
           "视觉隐喻", "反转", "奶油色", "签字笔", "地下刊物", "蜡笔",
           "越界", "笔刷", "错透视", "歪比例", "平静", "别扭", "社恐",
           "拙趣", "成人幽默", "轻松", "油画棒", "蜡质", "越线", "拆纸",
           "风格化", "卡通", "定格", "毛毡", "针织", "黏土", "毛绒",
           "雪尼尔", "玩偶", "马海毛", "剪影", "机甲", "机娘", "潮玩",
           "文人", "纸雕", "撕纸", "概括造型"):
    ROLE.setdefault(_w, "style")
for _w in ("手撕纸", "拼贴", "纸雕", "油画棒", "签字笔", "蜡笔", "笔刷",
           "毛毡", "针织", "黏土", "毛绒", "定格", "机甲", "3D", "2D"):
    ROLE.setdefault(_w, "medium")
for _w in ("山海经异兽", "机甲机娘", "文人", "市井", "动物", "日式", "韩系",
           "昭和", "国潮", "青年", "成人"):
    ROLE.setdefault(_w, "mood")


# 第四批：最后 6 条。它们只需补一个逐字存在的词就能命中。
for _w in ("街头", "小人", "随手", "黑线", "冷面", "视觉梗", "毛笔",
           "高度概括", "笨拙有趣", "手撕纸", "拼贴", "人形符号", "粗糙线"):
    ROLE.setdefault(_w, "style")
for _w in ("毛笔", "手撕纸"):
    ROLE.setdefault(_w, "medium")

# 英文生图名里的媒介/技法词 → 中文媒介。用于**校验** traits 抽出来的媒介，
# 也用于 traits 为空时兜底命名。
GEN_MEDIUM = {
    "cartoon": "漫画", "comic": "漫画", "manga": "漫画", "doodle": "涂鸦",
    "illustration": "插画", "storybook": "绘本", "picturebook": "绘本",
    "sketch": "速写", "watercolor": "水彩", "gouache": "水粉",
    "ink": "墨线", "wash": "淡彩", "collage": "拼贴", "cut-paper": "剪纸",
    "line": "线稿", "cel": "赛璐珞", "animation": "动画", "sticker": "贴纸",
    "notebook": "手帐", "diary": "手帐", "poster": "海报", "editorial": "社论",
    "lianhuanhua": "连环画", "gongbi": "工笔", "silkscreen": "丝网印刷",
    "pictogram": "图形", "graphic": "图形", "print": "版画",
}

# 手工改写：只换字面，不换依据（依据仍由 traits 抽取，检查照跑）
CURATED = {
    "001": "松散黑线怪萌冷幽默", "002": "极简线描连续线隐喻", "003": "极细钢笔线小人物大空间",
    "004": "故意笨拙极简线冷幽默", "005": "儿童式自由造型荒诞", "006": "黑白钢笔密集排线冷峻",
    "007": "狂躁钢笔断裂墨线细长", "008": "神经质歪斜线条都市焦虑", "009": "粗糙手帐原始情绪反精致",
    "010": "极小几何冷面文学梗", "011": "故意画坏荒诞粗糙黑线", "012": "极简视觉双关脑洞构图",
    "013": "粗黑轮廓扁平色块讽刺", "014": "随手钢笔反鸡汤恶趣味", "015": "极简人物线稿柔和色块",
    "016": "粗糙黑线心理情绪自嘲", "017": "黑白简线圆眼反应表情", "018": "极简圆头面无表情对话",
    "019": "爆发式夸张圆眼甩动", "020": "低保真鼠绘失控大眼", "021": "细黑线柔和水彩点染",
    "022": "日常女性蓬松手绘线稿", "023": "黑色简线坐姿暖色腮红", "024": "夸张大头松散黑线冷面",
    "025": "单格漫画极简黑线荒诞", "026": "密集小动物粗黑线夸张", "027": "黑色密排线粗重轮廓",
    "028": "冷静平涂色块正面站立", "029": "几何精密线条信息图留白", "030": "清晰细线侧身回望留白",
    "031": "黑白高对比粗黑剪影", "032": "松散法式墨线随意坐姿", "033": "极简报纸漫画低动作",
    "034": "松散弹性墨线儿童表情", "035": "波普成人讽刺漫画", "036": "墨线水彩松散绘本",
    "037": "北欧细线奇幻小人物", "038": "拟人动物职业绘本", "039": "复古水彩暖调绘本",
    "040": "交叉排线怪物绘本", "041": "极端比例弯曲绘本", "042": "自然主义水彩动物绘本",
    "043": "钢笔淡彩古典绘本", "044": "怪趣墨线水彩童话", "045": "极简诗意手写绘本",
    "046": "几何剪影高饱和绘本", "047": "低饱和冷面动物绘本", "048": "民俗线描装饰绘本",
    "049": "梦境超现实柔和绘本", "050": "复古拼贴纸感绘本", "051": "速写式夸张人物漫画",
    "052": "清线科幻梦境人物", "053": "欧式清线平涂漫画", "054": "几何清线欧洲人物",
    "055": "即兴彩色怪物涂鸦", "056": "杂志涂鸦波普覆盖", "057": "复古几何城市卡通",
    "058": "几何撞色时尚人物", "059": "正负形高对比剪影", "060": "负空间视觉双关图形",
    "061": "中世纪几何童话", "062": "极端几何自然角色", "063": "剪纸粗粝现代图形",
    "064": "玩具式现代拼贴", "065": "复古波普社论人物", "066": "粗线复古广告卡通",
    "067": "复古商业装饰插画", "068": "自由剪纸色块人物", "069": "诗意单线人物",
    "070": "抽象连续线人物", "071": "粗黑动态街头符号", "072": "原始涂鸦符号人物",
    "073": "朋克墨线文字社论", "074": "怪诞古典漫画肖像", "075": "新艺术海报人物",
    "076": "断裂细瘦情绪人物", "077": "原生艺术粗线人物", "078": "诗意几何符号人物",
    "079": "生物符号点色人物", "080": "流畅单线动态人物", "081": "电影感颗粒色块插画",
    "082": "复古丝网几何人物", "083": "流动东方墨线社论", "084": "安静低饱和日系社论",
    "085": "极简黑线时尚人物", "086": "无表情黑白极简人物", "087": "昭和圆润商业卡通",
    "088": "透明水彩湿边人物", "089": "昭和家庭日常漫画", "090": "民俗妖怪黑白漫画",
    "091": "圆润经典日式漫画", "092": "大头冷脸叛逆人物", "093": "八十年代都市波普少女",
    "094": "精密钢笔奇异植物", "095": "时尚穿搭速写少女", "096": "脱力生活吐槽速写",
    "097": "极简反逻辑日常漫画", "098": "手帐小人物生活涂鸦", "099": "可爱生活职场小品漫画",
    "100": "粗糙搞笑反应漫画", "101": "清秀线稿年轻女性", "102": "女生日常博客漫画",
    "103": "荒诞冷笑话极简漫画", "104": "温暖轻怪生活线稿", "105": "家庭速写日常观察",
    "106": "极简古怪图形动画", "107": "极少线条优雅少女", "108": "纤细女性情绪线稿",
    "109": "波普极简时尚人物", "110": "现代女性编辑线稿", "111": "日系杂志细线淡彩",
    "112": "极简女生日常细线", "113": "透明水彩杂志人物", "114": "彩色马克笔童话人物",
    "115": "波普广告松弛女孩", "116": "青春透明色流动插画", "117": "温暖生活杂志人物",
    "118": "柔软共感社交漫画", "119": "高饱和潮流世代少女", "120": "柔和梦境轻动画插画",
    "121": "低对比粉彩梦幻少女", "122": "东京街头图形女孩", "123": "强配色神秘时尚图形",
    "124": "温柔自然梦境插画", "125": "黑白极简视觉双关漫画", "126": "修长无脸新中式人物",
    "127": "高密度东方奇幻社论", "128": "季节旅行水彩手帐", "129": "蓝橙撞色颗粒社论",
    "130": "电影感饱和故事插画", "131": "新国风流畅线条插画", "132": "国潮装饰人物插画",
    "133": "飘逸东方幻想装饰人物", "134": "柔和水彩中国氛围", "135": "传统文化现代社论",
    "136": "写意水墨古风人物", "137": "野生墨线东方妖异", "138": "清雅水墨古风人物",
    "139": "精致东方线稿人物", "140": "新国风东方奇幻角色", "141": "清雅古风漫画线稿",
    "142": "华丽暗黑幻想人物", "143": "山海经异兽墨线角色", "144": "蓝灰梦境孤独绘本",
    "145": "女生吐槽夸张漫画", "146": "极简青年社交情绪漫画", "147": "诗意都市童话插画",
    "148": "极简都市男女关系讽刺", "149": "东方女性细腻线条漫画", "150": "梦境青春绘本色彩",
    "151": "网络少女生活漫画", "152": "中文互联网梗漫画", "153": "自由线条城市青年漫画",
    "154": "当代都市科技商业人物", "155": "随手黑线社论涂鸦", "156": "断续墨线即兴快速手绘",
    "157": "极少线条视觉隐喻", "158": "冷脸单格成人漫画", "159": "法式咖啡馆钢笔速写",
    "160": "日式脱力极细线漫画", "161": "日式手帐小人物涂鸦", "162": "日式低饱和生活插画",
    "163": "日式反转四格漫画", "164": "韩系奶油色生活涂鸦", "165": "韩系黑白红色点睛社论",
    "166": "签字笔地下刊物粗绘", "167": "双色套印错版颗粒", "168": "粗蜡笔越界社论",
    "169": "彩铅纸纹生活日记", "170": "黑色笔刷强动作漫画", "171": "连续单线时尚极简",
    "172": "错透视民族朴拙漫画", "173": "粗黑线歪比例漫画", "174": "干笔断裂笔刷社论",
    "175": "黑墨主体单色点睛", "176": "圆珠笔便签小人物", "177": "平静冷面荒诞涂鸦",
    "178": "别扭怪萌社恐手绘", "179": "拙趣怪味成人手绘", "180": "昭和杂志复古少女",
    "181": "平成少女手帐插画", "182": "大量白纸轻水彩", "183": "马克笔叠色糖果粉彩",
    "184": "昭和咖啡馆钢笔淡彩", "185": "奶油色社媒轻松涂鸦", "186": "高饱和贴纸涂鸦",
    "187": "韩系高饱和波普涂鸦", "188": "中式连环画旧纸细线", "189": "新国潮平面工笔",
    "190": "现代敦煌矿物色壁画", "191": "宋代青绿极简淡彩", "192": "新中式水墨小人物",
    "193": "岭南点心生活国潮", "194": "上海月份牌复古", "195": "民国广告现代重绘",
    "196": "油画棒蜡质治愈插画", "197": "儿童蜡笔越线拙趣", "198": "黑白钢笔冷面幽默",
    "199": "红蓝套印国潮青年刊", "200": "中世纪冷面墨线吉祥物", "201": "萌系圆润治愈插画",
    "202": "诗意青春清透插画", "203": "唯美漫画柔和插画", "204": "水墨新国风插画",
    "205": "Q版轻幽默魔性漫画", "206": "都市生活轻漫画", "207": "极简温暖叙事插画",
    "208": "东方美学商业插画", "209": "童趣水彩绘本", "210": "东方奇幻绘本",
    "211": "清新文艺插画", "212": "复古潮流插画", "213": "萌系圆润可爱插画",
    "214": "国风幻想插画", "215": "治愈生活插画", "216": "时尚女性插画",
    "217": "风格化3D卡通人格", "218": "六七十年代复古绘本", "219": "暖调复古儿童绘本",
    "220": "几何剪影2D动画角色", "221": "毛毡针织定格人偶", "222": "中叶诗意墨水水彩绘本",
    "223": "水彩模切贴纸卡通", "224": "七十年代羊毛黏土定格人偶", "225": "剪纸拼贴纸感绘本",
    "226": "厚涂水粉动画绘本", "227": "冷面风格化3D都市角色", "228": "北欧民间稚拙绘本",
    "229": "极简有机粉彩社论", "230": "复古墨水水彩漫画绘本", "231": "都市时尚动态剪影",
    "232": "毛绒雪尼尔3D玩偶", "233": "水粉彩铅温暖绘本", "234": "粗针马海毛定格人偶",
    "235": "爱德华墨水时尚社论", "236": "温润3D动画长片角色", "237": "圆滚粉彩针织3D玩偶",
    "238": "奇幻概念速写角色", "239": "八十年代末赛博朋克赛璐珞", "240": "法比清线城市速写",
    "241": "静电复印赛璐珞动画", "242": "等轴测奇幻地图插画", "243": "松散墨水水粉绘本",
    "244": "中世纪暗黑墨线赭调", "245": "八十年代剑与魔法赛璐珞", "246": "七十年代欧洲动画赛璐珞",
    "247": "电影级2D动画角色", "248": "国潮奇幻建筑插画", "249": "复古点彩像素奇幻",
    "250": "大块面剪影动作喜剧", "251": "高光机甲机娘潮玩", "252": "蜡笔水墨和风猫咪绘本",
    "253": "极简法式诗意线描", "254": "新中式工笔月份牌", "255": "极简水墨红黑撞色",
    "256": "水墨旅行木刻拼贴", "257": "粉色浪漫水墨晕染", "258": "鲜艳水彩动画奇幻",
    "259": "复古厚涂水粉叙事", "260": "潮流日系动漫插画", "261": "2D动画长片角色概念",
    "262": "扁平几何粗线电视动画", "263": "帕塔蓬节奏战鼓卡通", "264": "饥荒暗黑手绘动画",
    "265": "卡通沙龙手绘动画", "266": "森林儿童自然绘本", "267": "极简毛笔白底漫画",
    "268": "当代文人水墨漫画", "269": "社会主义现实主义宣传画", "270": "中国农民画鲜艳平涂",
    "271": "八九十年代课本插图", "272": "纸雕概括造型插画", "273": "手撕纸拼贴插画",
    "274": "手绘火柴人漫画",
}

# 规则自动定名的产物读着别扭（实测出过「剪纸」「图形」「线稿」这种
# 直接拿媒介词当名字，以及 19 条都叫「手绘」）。所以 274 条**全部**由
# CURATED 定名；规则只用来抽「依据」（from 字段），保证名字可核对。
#
# 定名过程：把每条 traits 与英文生图名并排看，取最能定义它的两三个词。
# 依据仍然机械抽取 —— tests/handraw_name_test.py 会验证每条名字里
# 至少有一个词能在 traits 原文找到。
CURATED = CURATED


def curated_name(number):
    return CURATED.get(str(number).zfill(3))



def _terms(text):
    """把 traits 切成候选词，按出现位置排序。"""
    if not text:
        return []
    segs = re.split(r"[、，,；;。：:/／和与及]", text)
    out = []
    for s in segs:
        s = s.strip()
        if not s:
            continue
        # 只取有角色的词：整段命中优先，否则取段内最长的命中词
        if s in ROLE:
            out.append(s)
            continue
        hits = [w for w in ROLE if w in s]
        if hits:
            hits.sort(key=len, reverse=True)
            out.append(hits[0])
    return out


def _gen_medium(gen):
    """英文生图名里的媒介词（用于校验与兜底）。"""
    g = (gen or "").lower()
    for en, zh in GEN_MEDIUM.items():
        if en.replace("-", " ") in g or en in g:
            return zh
    return ""


def _gen_style_words(gen):
    """英文生图名里的风格词 → 中文（兜底时用）。

    只收**语义明确**的映射。生图名的长尾（425 个词元）大部分是一次性的
    专有名词，硬翻只会造出不知所云的名字 —— 那还不如老实标「依据不足」。
    """
    g = (gen or "").lower()
    table = [
        ("tactile|felt|knitted|plush|mohair|yarn", "毛线针织"),
        ("stop-motion", "定格"),
        ("3d", "三维"),
        ("puppet", "人偶"),
        ("clay", "黏土"),
        ("plush", "毛绒"),
        ("isometric", "等轴测"),
        ("xerox", "静电复印"),
        ("dunhuang", "敦煌"),
        ("song-dynasty", "宋代"),
        ("ligne-claire|clear-line", "清线"),
        ("cyberpunk", "赛博朋克"),
        ("guochao|guofeng", "国潮"),
        ("medieval", "中世纪"),
        ("edwardian", "爱德华"),
        ("victorian", "维多利亚"),
        ("retro", "复古"),
        ("vintage", "复古"),
        ("fantasy", "奇幻"),
        ("sci-fi", "科幻"),
        ("knitted", "针织"),
        ("textbook", "课本"),
        ("calendar-poster", "月份牌"),
        ("advertising", "广告"),
        ("travel", "旅行"),
        ("seasonal", "季节"),
        ("editorial", "社论"),
        ("fashion", "时尚"),
        ("urban", "都市"),
        ("everyday", "日常"),
        ("girl", "少女"),
        ("animal", "动物"),
        ("character", "角色"),
        ("figure", "人物"),
    ]
    out = []
    for pat, zh in table:
        if re.search(pat, g):
            out.append(zh)
    return out


def _corpus_freq(entries):
    """每个词在 274 条里出现在**多少条** traits 中。

    这是「区分度」的依据：`手绘` / `漫画` 这种词几乎每条都有，
    拿它当名字等于没命名（实测第一版 19 条叫「手绘」）。
    越罕见的词越能定义这一条，所以选词时优先低频。
    """
    freq = {w: 0 for w in ROLE}
    for e in entries:
        t = e.get("traits") or ""
        for w in ROLE:
            if w in t:
                freq[w] += 1
    return freq


def _rank_words(traits, freq):
    """按「区分度 × 角色」给候选词排序。

    排序键（从重要到次要）：
      1. 低频优先（区分度）
      2. 媒介优先（中文画派名以媒介收尾，先确定媒介再配修饰）
      3. 原文位置靠前优先（traits 由主到次写）
    """
    segs = re.split(r"[、，,；;。：:/／和与及]", traits or "")
    cand = []
    for i, seg in enumerate(segs):
        seg = seg.strip()
        if not seg:
            continue
        hits = [w for w in ROLE if w in seg]
        if not hits:
            continue
        hits.sort(key=lambda w: (-len(w), freq.get(w, 999)))
        w = hits[0]
        cand.append((freq.get(w, 999), 0 if ROLE.get(w) == "medium" else 1, i, w))
    cand.sort()
    # 去重保序
    seen, out = set(), []
    for _f, _r, _i, w in cand:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def _compose(words, gen, freq):
    """按角色把词拼成名字。

    结构按可用角色择优（中文画派名以媒介收尾是惯例）：
        [主题] + [媒介]          主题明确时最自然：人物漫画 / 猫咪水彩
        [修饰] + [主题] + [媒介]  三者都有时最完整
        [修饰] + [媒介]          没有主题时：松散涂鸦 / 低饱和水彩
        [媒介]                   兜底（太笼统，下面会补词）

    取词时**都取低频的**（区分度高），词的顺序按角色固定，不按原文顺序 ——
    原文顺序会拼出「墨线水彩绘本」这种堆叠，角色顺序才读得顺。
    """
    by_role = {}
    for w in words:
        by_role.setdefault(ROLE.get(w, "style"), []).append(w)

    def pick(role, n=1):
        return by_role.get(role, [])[:n]

    med_zh = (pick("medium") or [_gen_medium(gen)] or [""])[0]
    subj = pick("subject")
    mod = pick("style") + pick("mood")
    col = pick("color")

    name = ""
    if subj:
        name = subj[0] + (mod[0] if mod else "") + (med_zh or "")
    elif mod:
        name = mod[0] + (col[0] if col and col[0] not in mod[0] else "") + (med_zh or "")
    else:
        name = (col[0] if col else "") + (med_zh or "")

    # 去掉相邻重复（实测出过「赛璐珞赛璐珞」）
    for p in (med_zh, subj[0] if subj else "", mod[0] if mod else ""):
        if p and name.count(p) > 1:
            name = name.replace(p, "", 1)
    # 太短就把还没用到的候选词按「修饰 → 主题 → 媒介」的缺口补上
    have = lambda w: w in name
    for w in words:
        if len(re.findall(r"[\u4e00-\u9fff]", name)) >= 6:
            break
        if not have(w):
            name = w + name if ROLE.get(w) in ("style", "mood") else name + w
    if len(re.findall(r"[\u4e00-\u9fff]", name)) < 3:
        for w in _gen_style_words(gen):
            if not have(w):
                name = w + name
                break
    if len(re.findall(r"[\u4e00-\u9fff]", name)) < 2:
        name = (_gen_style_words(gen) or ["手绘风格"])[0]
    return name


def _evidence(name, traits, freq):
    """从 traits 里抽出**名字用到的那些词** —— 这就是可核对性的凭据。

    做法：拿名字的每个 2–4 字子串去 traits 原文里找，命中且是词表里的词
    就算一个凭据。找不到就退回「名义上用了但没逐字命中」的排序前几个，
    并在 basis 上标出来（**缺依据要显形，不要假装**）。
    """
    if not traits:
        return [], "generation_name"
    hits = []
    # ⚠ 这里原来在内层写了 `continue` —— 4 字没命中就**跳过该位置的 3 字与
    # 2 字**匹配，于是「手撕纸拼贴插画」明明含 traits 里的「手撕纸」「拼贴」，
    # 却报成「无逐字命中」。四个长度各自独立扫一遍，不互相短路。
    for n in (4, 3, 2):
        for i in range(len(name) - n + 1):
            sub = name[i:i + n]
            if sub in traits and sub in ROLE and sub not in hits:
                hits.append(sub)
    if hits:
        return hits, "traits"
    # 词表一个词都没命中（实测 8 条：071/157/163/166/170/173/178/197 ——
    # 它们的 traits 用的是「街头图腾」「视觉隐喻」这类词表没收录的说法）。
    # **不拿排序结果冒充凭据**：宁可如实标「没找到逐字命中」，
    # 也不要给一个看着像证据、实际与名字无关的列表。
    return [], "traits_unmatched"


def name_one(entry, traits_words=None, freq=None):
    """给一条风格算名字，并留下依据。

    名字来自 `CURATED`（274 条人工定名，见那张表的说明）；
    `from` / `basis` 由 `_evidence` 机械抽取 —— 名字可以人工定，
    **凭据不能人工写**。
    """
    num = entry["number"]
    traits = (entry.get("traits") or "").strip()
    gen = (entry.get("generation_name") or "").strip()
    freq = freq or {}

    curated = CURATED.get(num)
    if curated:
        name = curated
    else:
        # 兜底：CURATED 漏了（不该发生，测试会抓），退回规则命名
        words = _rank_words(traits, freq) if traits else []
        name = _compose(words, gen, freq) if words else \
            "".join(_gen_style_words(gen)[:2]) + (_gen_medium(gen) or "手绘")
    src, basis = _evidence(name, traits, freq)
    return {
        "number": num,
        "name": name,
        "basis": basis if traits else "generation_name",
        "from": src,
        "traits": traits,
        "traits_chars": len(traits),
        "generation_name": gen,
        "group": entry.get("group", ""),
        "reference": entry.get("reference", ""),
    }


_CACHE = {}


def all_names(entries=None):
    """返回 {编号: 记录}。"""
    if entries is None and _CACHE.get("all"):
        return _CACHE["all"]
    es = entries if entries is not None else load_entries()
    freq = _corpus_freq(es)
    out = {}
    used = {}
    for e in es:
        rec = name_one(e, freq=freq)
        # ── 去重兜底 ──────────────────────────────────────────────
        # traits 相似的条目抽出来的词会撞（实测 4 条都叫「柔软人物透明叠染」）。
        # 中文名撞车不只是难看：双链 [[名字]] 会歧义、检索会指向错的卡。
        # 撞了就往下取一个更罕见的候选词补进去 —— 依据仍是同一条 traits。
        if rec["name"] in used:
            pool = _rank_words(rec["traits"], freq)
            for extra in pool:
                if extra in rec["name"]:
                    continue
                cand = rec["name"] + extra
                if cand not in used:
                    rec["name"] = cand
                    rec["from"] = rec["from"] + [extra]
                    break
            else:
                # traits 用尽了还撞：用生图名里的风格词区分
                for extra in _gen_style_words(rec["generation_name"]):
                    cand = rec["name"] + extra
                    if cand not in used:
                        rec["name"] = cand
                        rec["from"] = rec["from"] + [extra]
                        break
                else:
                    n = 2
                    while ("%s%d" % (rec["name"], n)) in used:
                        n += 1
                    rec["name"] = "%s%d" % (rec["name"], n)
                    rec["basis"] = "generation_name"
        used[rec["name"]] = rec["number"]
        out[rec["number"]] = rec
    if entries is None:
        _CACHE["all"] = out
    return out


def name_for(number):
    return all_names().get(str(number).zfill(3))


def stats():
    ns = all_names()
    total = len(ns)
    from_traits = sum(1 for r in ns.values() if r["basis"] == "traits")
    dup = {}
    for r in ns.values():
        dup.setdefault(r["name"], []).append(r["number"])
    return {
        "total": total,
        "from_traits": from_traits,
        "from_generation_name": total - from_traits,
        "curated": len(CURATED),
        "duplicates": {k: v for k, v in dup.items() if len(v) > 1},
        "traits_coverage": round(100.0 * from_traits / total, 1) if total else 0,
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="手绘卡中文命名")
    ap.add_argument("--list", action="store_true", help="列出全部名字")
    ap.add_argument("--stats", action="store_true", help="统计与查重")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.stats:
        print(json.dumps(stats(), ensure_ascii=False, indent=1))
    else:
        ns = all_names()
        for num in sorted(ns):
            r = ns[num]
            mark = "·" if r["basis"] == "traits" else ("≈" if r["basis"] == "traits_ranked" else "?")
            if a.json:
                print(json.dumps(r, ensure_ascii=False))
            else:
                print("%s %s  %-22s %s" % (mark, num, r["name"], r["generation_name"][:38]))
