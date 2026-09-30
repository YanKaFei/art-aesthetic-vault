# -*- coding: utf-8 -*-
"""
fv_core.py —— 电影风格库的「可被调用的那一层」。

和 `artvault_core.py` 是同一个角色的孪生兄弟：
artvault_core 把 421 张**艺术流派卡**变成可检索可组合的数据；
fv_core 把**导演-电影卡**变成同样形态的东西，让 AI（或你自己）能：

    films()       取全部电影卡（结构化）
    directors()   按导演分组
    search()      按风格词/导演/片名/技法检索
    resolve()     把「花样年华」/「Chungking Express」/slug 解析成一张卡
    layers()      取七层提示词片段（省 token 的主路径）
    palette()     取配色
    related()     找关联的**艺术流派卡**（跨库）

## 关键设计：七层词表与艺术流派库共用

`LAYERS` 直接从 artvault_core 取，不在本文件重写一份。
理由不是省字，是**跨源混搭的前提**：
`artvault.py compose --style baroque --lighting wong-kar-wai-...` 这种
「巴洛克的构图 + 王家卫的光照」只有在两边层名与语义一致时才拼得起来。
两边各写一份 LAYERS，早晚漂移，漂移的那天跨源混搭会静默给出错误结果。

## 不给电影另造一套解读

七层、负向词、配色、翻车点这些字段与艺术流派卡**同名同义**，
所以上层的渲染/校验/CLI 可以一套代码吃两种卡。
新增的字段只有电影独有的那几样：director_* / year / crew / filmgrab / stills。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# 层名与顺序沿用艺术流派库，**不重写**（见模块 docstring）
from artvault_core import LAYERS, LAYER_ZH  # noqa: E402

import fv_data  # noqa: E402

FILMS_DIR = os.path.join(VAULT, "40-films")
# 剧照的**本地私有**副本。版权作品，gitignore，不进版本库、不嵌卡片。
STILLS_DIR = os.path.join(VAULT, "99-attachments", "images-films")
# 抓取结果缓存（外链清单 + 班底），可重建
STILLS_DATA = os.path.join(HERE, "_data", "films")


def _positive(m):
    """没有手写 positive 时，用七层里的六层自动拼（**不含镜头层**）。

    镜头层是「你要什么景别」，是使用者的选择，不是这部片的属性 ——
    把它并进「风格片段」会替你决定机位。这与艺术流派卡的处理一致。
    """
    if m.get("positive"):
        return m["positive"].strip()
    p = m["layers"]
    parts = [p["style"], p["lighting"], p["color"],
             p["composition"], p["medium"], p["mood"]]
    return ", ".join(x.strip().rstrip(",") for x in parts if x)


def load():
    """把 fv_data.FILMS 展开成统一形状的卡，并合并抓取到的剧照清单。"""
    crawled = _crawled()
    cards = []
    for m in fv_data.FILMS:
        sn = m["slug"]
        c = dict(m)
        c["positive"] = _positive(m)
        c["stills"] = list(crawled.get(sn, {}).get("stills") or m.get("stills") or [])
        # 抓取脚本用画廊页的真实值校对班底；抓不到时保留手写值，
        # 但**标出未核对**，避免把「抄来的」说成「核对过的」。
        c["crew_verified"] = bool(crawled.get(sn, {}).get("crew"))
        if c["crew_verified"]:
            c["crew"] = crawled[sn]["crew"]
        c["gallery_title"] = crawled.get(sn, {}).get("title") or m["title_en"]
        cards.append(c)
    return cards


_CACHE = {}


def _crawled():
    """读 fv_fetch.py 的抓取结果（没有就是空，不影响手写数据出卡）。"""
    if "crawled" in _CACHE:
        return _CACHE["crawled"]
    out = {}
    if os.path.isdir(STILLS_DATA):
        for fn in sorted(os.listdir(STILLS_DATA)):
            if fn.endswith(".json"):
                try:
                    d = json.load(open(os.path.join(STILLS_DATA, fn), encoding="utf-8"))
                    out[d["slug"]] = d
                except Exception:
                    pass
    _CACHE["crawled"] = out
    return out


def films():
    if "films" not in _CACHE:
        _CACHE["films"] = load()
    return _CACHE["films"]


def by_slug():
    if "byslug" not in _CACHE:
        _CACHE["byslug"] = {f["slug"]: f for f in films()}
    return _CACHE["byslug"]


def directors():
    """按导演分组。顺序沿用 fv_data 的策展顺序，不重排。"""
    if "directors" not in _CACHE:
        out = []
        by = {}
        for f in films():
            ds = f["director_slug"]
            if ds not in by:
                by[ds] = {"director_slug": ds,
                          "director_zh": f["director_zh"],
                          "director_en": f["director_en"],
                          "films": []}
                out.append(by[ds])
            by[ds]["films"].append(f)
        _CACHE["directors"] = out
    return _CACHE["directors"]


def layers(f):
    return {k: f["layers"][k] for k in LAYERS}


def palette(f):
    return [{"hex": h, "name": n} for h, n in f["palette"]]


def related(f):
    """关联的是**艺术流派卡**。取不到就跳过，不返回半成品。"""
    import artvault_core as A
    out = []
    for s in f.get("see_also", []):
        c = A.by_slug().get(s)
        if c:
            out.append(c)
    return out


# ------------------------------------------------------------------ 检索

# 中文与英文都进索引，且把**技法词**显式挂进去 —— 「bleach bypass」
# 这样的词在正文里出现过，但中文用户会用「漂白」来找，两边都要能命中。
_ALIASES = {
    "tarkovsky-stalker": ["塔可夫斯基", "潜行者", "stalker", "诗电影", "长镜头", "slow cinema"],
    "tarkovsky-mirror": ["塔可夫斯基", "镜子", "the mirror", "记忆", "自传"],
    "wong-kar-wai-in-the-mood-for-love": ["王家卫", "花样年华", "杜可风", "旗袍", "step printing",
                                          "降格", "frame within frame", "框中框"],
    "wong-kar-wai-chungking-express": ["王家卫", "重庆森林", "杜可风", "霓虹", "雨夜", "手持",
                                       "neon", "handheld", "跳切"],
    "kubrick-the-shining": ["库布里克", "闪灵", "对称", "一点透视", "symmetry", "one point perspective"],
    "kubrick-barry-lyndon": ["库布里克", "巴里林登", "烛光", "油画", "candlelight", "zoom"],
    "kurosawa-ran": ["黑泽明", "乱", "绘卷", "横幅", "天空", "长焦", "telephoto"],
    "bong-parasite": ["奉俊昊", "寄生虫", "阶级", "楼梯", "垂直", "荧光灯", "vertical"],
    "villeneuve-blade-runner-2049": ["维伦纽瓦", "银翼杀手", "狄金斯", "deakins", "体积光",
                                     "雾", "雨夜", "青蓝", "volumetric", "cyberpunk"],
    "villeneuve-dune": ["维伦纽瓦", "沙丘", "沙", "逆光", "剪影", "极简", "silhouette", "minimal"],
    "fincher-se7en": ["芬奇", "七宗罪", "bleach bypass", "漂白", "脏绿", "雨", "黑色电影"],
    "hou-hsiao-hsien-the-assassin": ["侯孝贤", "聂隐娘", "唐朝", "纱帘", "遮挡", "静止", "gauze"],
    "goddard-breathless": ["戈达尔", "精疲力尽", "新浪潮", "跳切", "手持", "黑白", "new wave"],
    "kon-satoshi-perfect-blue": ["今敏", "未麻的部屋", "赛璐璐", "镜面", "心理惊悚", "cel"],
}


def _haystack(f):
    parts = [f["slug"], f["director_zh"], f["director_en"], f["title_zh"], f["title_en"],
             f.get("title_original") or "", str(f["year"]), f["one_liner"]]
    parts += f.get("core", [])
    parts += list(f["visual"].values())
    parts += list(f["layers"].values())
    parts += [f["negative"]]
    parts += f.get("pitfalls", [])
    parts += [n for _, n in f["palette"]]
    parts += _ALIASES.get(f["slug"], [])
    return "\n".join(parts).lower()


def search(query, limit=8):
    """把查询拆成词，按命中位置加权。没命中就返回空——**不返回「大概相关」**。

    本库的规矩：宁可空手，不要答错。问一个不存在的片子得到另一张卡，
    比明确说「没找到」糟得多。
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    terms = [t for t in re.split(r"[\s,、，/]+", q) if t]
    scored = []
    for f in films():
        hay = _haystack(f)
        score = 0
        for t in terms:
            if t in f["slug"].lower() or t in f["title_zh"].lower() \
                    or t in f["title_en"].lower() or t in f["director_zh"].lower() \
                    or t in f["director_en"].lower():
                score += 12          # 命中标识符/片名/导演，权重最高
            elif t in _ALIASES.get(f["slug"], ""):
                score += 8
            elif t in hay:
                score += 3
        if score:
            scored.append((score, f))
    scored.sort(key=lambda x: (-x[0], x[1]["slug"]))
    return [f for _, f in scored[:limit]]


def name_matches(ident, limit=5):
    """模糊候选：给「你是不是想找」用。"""
    q = (ident or "").strip().lower()
    if not q:
        return []
    qn = _norm(q)
    out = []
    for f in films():
        for probe in (f["slug"], f["title_zh"], f["title_en"],
                      f.get("title_original") or "", f["director_zh"]):
            if q in probe.lower() or (qn and qn in _norm(probe)):
                out.append(f)
                break
    return out[:limit]


def _norm(s):
    """归一化：小写 + **去掉所有空白与常见分隔符**。

    为什么必须去空白：片名里有空格的片子（`银翼杀手 2049`、`Blade Runner
    2049`）在自然书写时常常不带那个空格。实测踩到 —— 文档里写的
    `film layers 银翼杀手2049` 直接报「没找到」，而库里的片名是
    「银翼杀手 2049」。空格是排版细节，不该决定一次查找的成败。
    """
    return re.sub(r"[\s·・:：\-—–_'\"“”（）()]+", "", (s or "").lower())


def resolve(ident):
    """把标识符解析成一张卡。返回 (card|None, hints)。

    严格匹配优先（slug → 中文名 → 英文名 → 原文名 → **去空格后的同形**），
    都失败才退到模糊候选。绝不静默挑一张最像的。
    """
    if not ident:
        return None, []
    q = ident.strip()
    ql = q.lower()
    bs = by_slug()
    if ql in bs:
        return bs[ql], []
    qn = _norm(q)
    # 第一轮：精确（原样）
    for key in ("title_zh", "title_en", "title_original"):
        for f in films():
            v = (f.get(key) or "").lower()
            if v and v == ql:
                return f, []
    # 第二轮：去掉空格/标点后的同形（「银翼杀手2049」↔「银翼杀手 2049」）
    for key in ("title_zh", "title_en", "title_original"):
        for f in films():
            if _norm(f.get(key)) == qn:
                return f, []
    # 第三轮：唯一子串命中
    hits = [f for f in films()
            if qn and (qn in _norm(f["title_zh"]) or qn in _norm(f["title_en"])
                       or qn == _norm(f.get("title_original")))]
    if len(hits) == 1:
        return hits[0], []
    return None, (hits or name_matches(q))


def stats():
    fs = films()
    return {
        "films": len(fs),
        "directors": len(directors()),
        "curated": sum(1 for f in fs if f["source"] == "curated"),
        "inferred": sum(1 for f in fs if f["source"] != "curated"),
        "with_stills": sum(1 for f in fs if f["stills"]),
    }


if __name__ == "__main__":
    s = stats()
    print("电影风格库：%d 部片 / %d 位导演（手写 %d，推断 %d，已抓剧照 %d 部）"
          % (s["films"], s["directors"], s["curated"], s["inferred"], s["with_stills"]))
    for d in directors():
        print("\n【%s · %s】" % (d["director_zh"], d["director_en"]))
        for f in d["films"]:
            n = len(f["stills"])
            print("  %-38s %s  %s%s" % (f["slug"], f["year"], f["title_zh"],
                                        ("  [%d 张剧照]" % n) if n else ""))
