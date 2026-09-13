#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""i2v_prompt.py —— 把**一张具体的图**接进视频提示词。

## 为什么单独一个模块

原来的视频层是「流派的」：`video_prompt.build(mv)` 只吃流派，所以
反推卡上那两块提示词，**换一张同流派的图，内容一模一样**。
而主体那一行干脆是占位符：

    【主体】<你的主体>，出现在<场景>。<写清核心事件…>

使用者真正要干的事是「我有这张图，让它动起来」（i2v），
但图的主体、景别、线条走向、明暗结构**早就测出来了**（image_analysis），
只是没有一条路把它送进视频提示词。

这个模块就是那条路：把客观测量翻译成**中文的视频语言**，填掉占位符。

## 翻译规则从哪来

只用可测量的量，不猜内容：

    人脸数 / 景别      → 主体是什么景别
    显著性中心         → 主体在画面哪一侧
    线条方向           → 画面内的动势方向
    细节密度 / 熵      → 适合「微动」还是「静中有动」
    明度调性 + 对比    → 光本身要不要动（烛火 / 窗光 / 暗部加深）
    霍夫直线有无       → 有没有硬边可以当运动参照
    构图中心权重       → 缓推 vs 横掠

**这些是提示，不是结论。** 图里到底是什么内容（谁、在做什么）只有看图的人知道，
所以生成出来的主体行保留「<你补一句发生了什么>」，不假装看懂了内容。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import video_prompt as VP  # noqa: E402


# ------------------------------------------------------------------ 小工具

def _g(d, *path, default=None):
    """安全取嵌套字段。"""
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _side(cx):
    if cx is None:
        return ""
    if cx < 0.42:
        return "画面左侧"
    if cx > 0.58:
        return "画面右侧"
    return "画面中央"


# ------------------------------------------------------------------ 主体

def subject_facts(a):
    """从人脸 + 显著性推出「主体是什么景别、在哪儿」。"""
    faces = _g(a, "extended", "faces", default={}) or {}
    sal = _g(a, "extended", "saliency", default={}) or {}
    comp = _g(a, "composition", default={}) or {}
    n_face = faces.get("count") or 0
    where = _side(sal.get("center_x"))
    ev = {}

    if n_face:
        framing = faces.get("framing") or "人物"
        ev["人脸数"] = n_face
        ev["景别"] = framing
        ev["最大人脸占比"] = "%.1f%%" % (faces.get("largest_face_pct") or 0)
        # 「一组人物」只在**真的检出多张脸**时才说。第一版看到显著性「分散」
        # 就写「一组人物」，而这张图只检出 1 张脸 —— 凭空把一个人的画面
        # 说成群像，属于过度断言。分散只说明「主体不够突出」，不等于人多。
        if n_face >= 2:
            subject = "一组人物（%d 张人脸），%s" % (n_face, framing)
        else:
            subject = "一个人物，%s" % framing
            if "分散" in (sal.get("focus") or ""):
                subject += "（画面注意力较分散，主体不算突出）"
    else:
        # 没有人脸：可能是风景、静物、抽象、或风格化到 Haar 认不出
        # （extended.faces.note 自己就写明「绘画风格化人脸可能漏检」）
        focus = sal.get("focus") or ""
        if "集中" in focus:
            subject = "一个明确的单一主体"
            ev["显著性"] = "集中"
        elif "分散" in focus:
            subject = "满构图的多主体画面，没有单一焦点"
            ev["显著性"] = "分散"
        else:
            subject = "一个主体（未检测到人脸，可能是风景 / 静物 / 抽象，也可能是风格化人像漏检）"
        if where:
            subject += "，视觉重心在%s" % where

    if where and n_face:
        subject += "，位于%s" % where
    ev["视觉重心"] = where or "—"
    ev["中心权重"] = comp.get("center_weight")
    return subject, ev


# ------------------------------------------------------------------ 场景/画面

def scene_facts(a):
    """画面的整体调性 —— 直接进「风格」那句的补充。"""
    lum = _g(a, "luminance", default={}) or {}
    con = _g(a, "contrast", default={}) or {}
    col = _g(a, "color", default={}) or {}
    har = _g(a, "harmony", default={}) or {}
    tex = _g(a, "texture", default={}) or {}
    parts, ev = [], {}
    if a.get("orientation"):
        parts.append(a["orientation"])
        ev["构图"] = a["orientation"]
    if lum.get("key"):
        parts.append(lum["key"])
        ev["明度调性"] = lum["key"]
    if con.get("level"):
        parts.append(con["level"])
        ev["对比"] = con["level"]
    if col.get("temperature"):
        parts.append("%s色主导" % col["temperature"])
        ev["色温"] = col["temperature"]
    if har.get("scheme"):
        parts.append(har["scheme"])
        ev["色彩结构"] = har["scheme"]
    if tex.get("busyness"):
        parts.append("细节密度%s" % tex["busyness"])
        ev["细节密度"] = tex["busyness"]
    return "；".join(parts), ev


# ------------------------------------------------------------------ 运动

def motion_facts(a):
    """画面内适合发生什么运动 —— 全部由线条 / 质感 / 明暗推出。"""
    lines = _g(a, "lines", default={}) or {}
    tex = _g(a, "texture", default={}) or {}
    lum = _g(a, "luminance", default={}) or {}
    con = _g(a, "contrast", default={}) or {}
    hough = _g(a, "extended", "hough", default={}) or {}
    out, ev = [], {}

    orient = lines.get("orientation") or ""
    ang = lines.get("dominant_angle")
    if "对角" in orient:
        out.append("沿对角线方向缓慢位移或擦过，让斜向结构带出速度感")
        ev["线条"] = "对角 %s°" % ang
    elif "水平" in orient:
        out.append("横向平移：云层、水面、横向扫过的光")
        ev["线条"] = "水平 %s°" % ang
    elif "垂直" in orient:
        out.append("纵向变化：烟、雨丝、垂落的织物或帷幕")
        ev["线条"] = "垂直 %s°" % ang
    elif orient:
        out.append("线条方向不突出，改用画面内部的细微变化推进")
        ev["线条"] = orient

    busy = tex.get("busyness") or ""
    ent = tex.get("entropy")
    if "繁" in busy or "密" in busy or (ent or 0) >= 7.0:
        out.append("笔触与细节密集，让细小元素缓慢浮动（尘粒、衣褶、反光）")
        ev["熵"] = ent
    elif "简" in busy or "疏" in busy or (ent or 9) <= 5.5:
        out.append("画面元素少，动得越少越高级 —— 只留一处极缓的变化")

    # 低明调 + 高 Michelson = 大面积暗 + 小面积高光 → 光本身就是戏
    key = lum.get("key") or ""
    mich = con.get("michelson") or 0
    if "低明调" in key and mich >= 0.85:
        out.append("光源本身在轻轻呼吸（烛火 / 窗光 / 单点光源），暗部缓慢加深")
        ev["光"] = "%s + Michelson %.2f" % (key, mich)
    elif "高明调" in key:
        out.append("整体明亮，用空气中微尘的浮动代替大幅动作")

    if (hough.get("count") or 0) > 0:
        out.append("画面里有明确硬边（建筑 / 器物轮廓），让它作为不动的参照物，"
                   "衬托运动的部分")
        ev["硬边"] = hough.get("count")
    return out, ev


def camera_facts(a, mv=None):
    """运镜建议 —— **只在流派卡没给明确运镜时**才覆盖它。

    流派卡里的运镜是该流派视觉语言的一部分（浮世绘要「模仿绘卷展开」），
    优先级高于从这张图推出来的通用建议。这里只在流派没交代时补位。
    """
    v = (mv or {}).get("video") or {}
    if (v.get("camera") or "").strip():
        return None, {"运镜": "沿用流派卡：%s" % v["camera"]}
    comp = _g(a, "composition", default={}) or {}
    out, ev = None, {}
    cw = comp.get("center_weight")
    sym = comp.get("symmetry_hint") or ""
    orient = a.get("orientation") or ""
    if (cw or 0) >= 1.1:
        out = "缓慢推进"
        ev["运镜依据"] = "中心权重 %.2f（主体集中在中心）" % cw
    elif "非对称" in sym:
        out = "横向缓慢掠过"
        ev["运镜依据"] = "非对称构图"
    if out and "竖构图" in orient:
        out += "（竖构图，幅度要更小）"
        ev["构图限制"] = orient
    return out, ev


def light_facts(a):
    """光照描述 —— 用测出来的明暗结构补强流派卡的说法。"""
    lum = _g(a, "luminance", default={}) or {}
    con = _g(a, "contrast", default={}) or {}
    sc = lum.get("shadow_clip_pct")
    parts = []
    if (sc or 0) >= 1.0:
        parts.append("暗部有 %.1f%% 压到纯黑，是有意为之的深压暗调" % sc)
    if (con.get("michelson") or 0) >= 0.85:
        parts.append("Michelson %.2f，小面积高光对大面积暗调" % con["michelson"])
    if (lum.get("dynamic_range") or 0) >= 110:
        parts.append("动态范围 %d，明暗跨度大" % lum["dynamic_range"])
    return "；".join(parts), {}


# ------------------------------------------------------------------ 汇总

def derive(a):
    """把一份 image_analysis 结果翻成视频语言。返回 facts dict。

    `a` 就是 `image_analysis.analyze(path)` 的返回值（一个普通 dict），
    所以本模块不依赖 Pillow / numpy —— 拿不到分析结果时调用方别调它就行。
    """
    subject, ev1 = subject_facts(a)
    scene, ev2 = scene_facts(a)
    motion, ev3 = motion_facts(a)
    light, _ = light_facts(a)
    facts = {
        "subject_zh": subject,
        "scene_zh": scene,
        "motion_zh": motion,
        "light_zh": light,
        "source_file": a.get("file") or "",
        "evidence": {},
    }
    facts["evidence"].update(ev1)
    facts["evidence"].update(ev2)
    facts["evidence"].update(ev3)
    return facts


def build(mv, analysis, duration=10):
    """i2v：这张图 + 它最像的流派 → 两块中文视频提示词。

    mv 可以为 None —— 那就只有图、没有流派锚定。
    """
    facts = derive(analysis or {})
    cam, cam_ev = camera_facts(analysis or {}, mv)
    if cam:
        facts["camera_zh"] = cam
    facts["evidence"].update(cam_ev)
    return VP.build(mv, duration=duration, facts=facts)


# ------------------------------------------------------------------ CLI

def _print_report(mv, a, r):
    print("图片：%s" % a.get("file"))
    if mv:
        print("锚定流派：%s（%s）" % (mv.get("name_zh"), mv.get("name_en")))
    ev = r.get("image_evidence") or {}
    if ev:
        print("推导依据（都是测出来的，不是猜的）：")
        for k, v in ev.items():
            print("  %-12s %s" % (k, v))
    print()
    print("=== A. Seedance 2.5 五段式 ===")
    print(r["seedance"])
    print("\n=== B. MiniMax H3 自然语言 ===")
    print(r["h3"])


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(
        prog="i2v_prompt.py",
        description="给**一张具体的图**生成视频提示词（主体/运动/运镜由客观测量推出）")
    ap.add_argument("image", help="图片路径")
    ap.add_argument("--slug", help="锚定流派 slug；不给就自动用 CLIP 找最像的（需模型）")
    ap.add_argument("--duration", type=int, default=10)
    a = ap.parse_args(argv)

    from movements import MOVEMENTS
    mv = None
    if a.slug:
        hit = [m for m in MOVEMENTS if m["slug"] == a.slug]
        if not hit:
            print("未知流派: %s（可用 python3 artvault.py categories 查）" % a.slug)
            return 1
        mv = hit[0]
    else:
        try:
            import clip_match as CM
            sug = CM.suggest([a.image], topn=1)
            top = (sug or {}).get(a.image) or []
            if top:
                slug = top[0].get("slug")
                mv = [m for m in MOVEMENTS if m["slug"] == slug][0]
                print("（CLIP 自动锚定：%s，Top-1；准确率约四成，可用 --slug 覆盖）\n"
                      % mv["name_zh"])
        except Exception:
            print("（没装 CLIP 模型，未自动锚定流派；用 --slug 指定，或只当纯画面提示词用）\n")

    import image_analysis as IA
    ana = IA.analyze(a.image)
    if ana.get("error"):
        print("分析失败：%s" % ana["error"])
        return 1
    r = build(mv, ana, duration=a.duration)
    _print_report(mv, ana, r)
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 i2v_prompt.py <图片> [--slug 流派] [--duration N]",
          ["给一张具体的图生成两块中文视频提示词。",
           "主体 / 运动 / 运镜从图片的客观测量推出，不再是流派卡的通用文案。",
           "不指定 --slug 时用 CLIP 自动锚定流派（需先跑 clip_embed.py download）。",
           "Seedance 块与 H3 块格式不同，**不要混用**。"])
    sys.exit(main(sys.argv[1:]))
