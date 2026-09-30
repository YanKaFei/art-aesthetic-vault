# -*- coding: utf-8 -*-
"""
shot_core.py —— 镜头配方卡库（45-shots/）的「可被调用的那一层」。

和 `artvault_core.py`（艺术流派）、`fv_core.py`（导演-电影）是**并列的第三条轴**：

    artvault_core  421 张   轴 = 风格    问「这是什么风格、怎么拼提示词」
    fv_core         14 张   轴 = 电影    问「这部片长什么样、怎么模仿它」
    shot_core      157 张   轴 = 招式    问「这一下动效怎么做出来」

## 为什么这里**没有** LAYERS

前两条轴共用七层（风格/光照/色彩/构图/媒介/情绪/镜头），所以 `compose`
能把两边混着拼。这一条轴**刻意不参与**：

上游的镜头卡讲的是动效时序与参数 —— `zoom 6f ease-in，1→2.6`、
`震屏包络 14px·e^(−t/1.8)`、`前 hold ≥30f`。这些卡里**没有一张**有色彩或
光照字段（157 张实测为 0）。给它套七层只能靠编，而 `compose --style
crash-zoom-punch` 会拼出一段没有色彩语义的提示词，且不会报错 ——
那是最坏的一种错：看起来能用。

所以这里暴露的是 `LIST_KEYS`（它自己真实拥有的字段），不是 `LAYERS`。
`tests/shot_test.py` 里有测试守着这条边界。

## 与前两条轴的接法

不是靠七层，是靠**引用**：`40-films/<导演>/<电影>.md` 的「五、AI 视频层」
里那两行（**运动**/**运镜**）描述的就是这些招式，两边互相 `[[双链]]`。
电影卡说「要什么画面」，镜头卡说「那一下怎么拍出来」。
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

DATA_DIR = os.path.join(HERE, "_data", "shots")
OUT_DIR = os.path.join(VAULT, "45-shots")

# 上游的类别目录名 → 中文显示名。**保留英文 slug 作目录名**
# （上游身份，改了就对不上来源），中文名只用于显示与检索。
CATEGORY_ZH = {
    "opening": "开场",
    "camera": "运镜",
    "interaction": "交互",
    "data": "数据可视化",
    "typography": "文字排版",
    "ui-entrance": "界面入场",
    "transition": "转场",
    "effects": "特效",
    "rhythm": "节奏",
    "outro": "收尾",
}
CATEGORY_ORDER = list(CATEGORY_ZH)

# 这些是镜头卡**真实拥有**的字段。与艺术/电影卡的七层是两回事，
# 故意不同名，免得被误当成同一套 schema。
LIST_KEYS = ["one_liner", "purpose", "duration", "energy", "tags"]

# 中文检索别名。上游卡名与正文是中文的，但用户会用更口语的说法来找。
ALIASES = {
    "crash-zoom-punch": ["急推", "冲击", "砸近", "推近特写", "震屏", "回弹"],
    "radial-wave": ["放射波", "涟漪扩散", "圆形扩散"],
    "text-as-mask": ["文字遮罩", "文字当蒙版"],
    "color-block-step-wipe": ["色块擦除", "阶跃擦除", "色块转场"],
    "riso-print-hits": ["孔版印刷", "叠印", "印刷质感"],
    "beat-step-list-theme-cycle": ["卡点", "节拍", "循环"],
}


def _data():
    if "shots" in _CACHE:
        return _CACHE["shots"]
    out = []
    if os.path.isdir(DATA_DIR):
        for fn in sorted(os.listdir(DATA_DIR)):
            if fn.endswith(".json"):
                try:
                    out.append(json.load(open(os.path.join(DATA_DIR, fn), encoding="utf-8")))
                except Exception:
                    pass
    out.sort(key=lambda c: (CATEGORY_ORDER.index(c["category"])
                            if c.get("category") in CATEGORY_ORDER else 99,
                            c["name"]))
    _CACHE["shots"] = out
    return out


_CACHE = {}


def shots():
    return _data()


def by_slug():
    if "byslug" not in _CACHE:
        _CACHE["byslug"] = {s["name"]: s for s in shots()}
    return _CACHE["byslug"]


def by_category(cat):
    return [s for s in shots() if s["category"] == cat]


def categories():
    """按上游的固定顺序返回，带中文名与张数。"""
    out = []
    for slug in CATEGORY_ORDER:
        n = len(by_category(slug))
        if n:
            out.append({"category": slug, "name_zh": CATEGORY_ZH[slug], "count": n})
    return out


def stats():
    return {
        "shots": len(shots()),
        "categories": len(categories()),
        "source": shots()[0]["source_repo"] if shots() else "",
        "commit": shots()[0]["source_commit"] if shots() else "",
        "license": shots()[0]["license"] if shots() else "",
    }


# ------------------------------------------------------------------ 检索

def _haystack(s):
    parts = [s["name"], s["one_liner"], s["purpose"], s["duration"], s["energy"],
             CATEGORY_ZH.get(s["category"], ""), s["category"]]
    parts += s.get("tags") or []
    parts += [s.get("intent", ""), s.get("motion", ""), s.get("params", ""),
              s.get("pitfalls", "")]
    parts += ALIASES.get(s["name"], [])
    return "\n".join(parts).lower()


def _norm(s):
    """小写 + 去掉空白与常见分隔符。

    和 fv_core 同一条理由：`crash-zoom-punch` / `crash zoom punch` /
    `crashzoompunch` 是同一个名字，空格不该决定查找成败。
    """
    return re.sub(r"[\s·・:：\-—–_/]+", "", (s or "").lower())


def search(query, limit=8, category=None):
    """按「我想做什么」或名字搜。命中标识符/名字权重最高。"""
    q = (query or "").strip().lower()
    if not q:
        return []
    terms = [t for t in re.split(r"[\s,、，/]+", q) if t]
    scored = []
    for s in shots():
        if category and s["category"] != category:
            continue
        hay = _haystack(s)
        score = 0
        for t in terms:
            if t == s["name"].lower() or t in _norm(s["name"]):
                score += 12
            elif t in ALIASES.get(s["name"], ""):
                score += 8
            elif t in CATEGORY_ZH.get(s["category"], ""):
                score += 6
            elif t in hay:
                score += 3
        if score:
            scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], x[1]["name"]))
    return [s for _, s in scored[:limit]]


def name_matches(ident, limit=6):
    q = (ident or "").strip().lower()
    qn = _norm(q)
    out = []
    for s in shots():
        probes = [s["name"], s["one_liner"], CATEGORY_ZH.get(s["category"], "")]
        if q in s["name"].lower() or (qn and qn in _norm(s["name"])):
            out.append(s)
        elif any(q and q in p.lower() for p in probes[1:] if p):
            out.append(s)
    return out[:limit]


def resolve(ident):
    """返回 (卡|None, 候选)。严格优先，绝不静默给一张别的卡。"""
    if not ident:
        return None, []
    q = ident.strip()
    bs = by_slug()
    if q in bs:
        return bs[q], []
    ql, qn = q.lower(), _norm(q)
    for s in shots():
        if s["name"].lower() == ql or _norm(s["name"]) == qn:
            return s, []
    # 别名：用户会用「急推」「色块擦除」这种意图词来找，
    # 而那不在卡名或一句话里（实测「急推」解析失败）。别名表是**精确**匹配，
    # 不做子串 —— 否则「推」会命中一堆卡，等于没筛。
    for sl in ALIASES:
        for a in ALIASES[sl]:
            if ql == a or qn == _norm(a):
                c = by_slug().get(sl)
                if c:
                    return c, []
    hits = [s for s in shots()
            if qn and (qn in _norm(s["name"]) or qn in _norm(s["one_liner"]))]
    if len(hits) == 1:
        return hits[0], []
    return None, (hits or name_matches(q))


if __name__ == "__main__":
    s = stats()
    print("镜头配方卡库：%d 张 / %d 类" % (s["shots"], s["categories"]))
    print("来源：%s @ %s（%s）" % (s["source"], s["commit"][:12], s["license"]))
    for c in categories():
        print("\n【%s · %s】%d 张" % (c["category"], c["name_zh"], c["count"]))
        for x in by_category(c["category"]):
            print("   %-42s %s" % (x["name"], x["one_liner"][:44]))
