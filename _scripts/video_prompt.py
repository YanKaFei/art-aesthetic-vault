#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
video_prompt.py —— 从流派数据生成**可直接粘贴的中文视频提示词**。

## 为什么是两个块而不是一个

MiniMax H3（海螺）和 Seedance 2.5 对提示词的要求**不一样**，混用会出问题：

    Seedance 2.5              五段式：主体 + 风格 + 时间线 + BGM + 限制
                              （官方 skill 定义的结构，单条最长 30s、素材 ≤50）

    MiniMax H3（官网 / API）   **中文自然语言**，不要手工结构化 ——
                              H3 前面有 Context-IR 做理解与改写，
                              你手工塞 [Shot N] / 时间戳会和它打架
                              （已知症状：镜头数翻倍、时间戳错位）

    MiniMax H3（本地权重）     完整英文结构化格式（ComfyUI / SGLang）。
                              本模块不生成这一块 —— 那需要逐字精确的字段名，
                              要按官方 references 写，不适合塞进流派卡。

## 中文正文从哪来

**不用英文 prompt 字段**（那是给图像模型的），改用卡片的 `visual`
六维中文拆解（色彩/光影/笔触/构图/材质/情绪）—— 实测 141 个流派全覆盖。
英文只保留在最后一行「风格锚定」里，因为那些术语更精确、且卡片第四节
已经列过。这样正文读起来是中文，模型该拿到的精确锚点也没丢。

    风格   ← visual.光影 / 色彩 / 材质 / 情绪  + prompt.style（英文锚定行）
    时间线 ← video.motion（按分句拆 3 段）+ video.camera（判方向、判是否固定机位）
    BGM    ← prompt.mood 的关键词映射
    限制   ← video.note + 通用视频风险
"""

import re

# 运镜词 → 中文。**顺序重要**：带方向的放前面，
# 否则 "dolly in" 会先命中 "dolly"，把方向丢掉（实测踩过）。
CAMERA_PATTERNS = [
    (r"dolly\s*in|push\s*in", "机位向前推进"),
    (r"dolly\s*out|pull\s*out", "机位向后拉远"),
    (r"zoom\s*in", "变焦推近"),
    (r"zoom\s*out", "变焦拉远"),
    (r"static|固定机位|镜头不动", "固定机位"),
    (r"\bpan\b|横摇", "横向摇镜"),
    (r"\btruck\b", "平行横移"),
    (r"\btilt\b|俯仰", "上下俯仰"),
    (r"pedestal", "升降机位"),
    (r"arc\s*shot|\barc\b|环绕", "环绕拍摄"),
    (r"track|跟拍|跟移", "跟拍移动"),
    (r"handheld|手持", "手持跟拍"),
    (r"\broll\b", "机身翻滚"),
    (r"shake|抖动", "镜头抖动"),
    (r"\bpov\b|主观视角", "主观视角"),
]

BGM_RULES = [
    (("serene", "calm", "quiet", "stillness", "meditative", "contemplative", "peaceful",
      "restrained", "solemn", "devotional", "transcendent", "eternal", "stoic"),
     "极简或干脆不用配乐，以环境音为主；若要配乐只用单件乐器长音（古琴、竖琴、大提琴任一），音量压在环境音之下"),
    (("dramatic", "intense", "theatrical", "heroic", "turbulent", "vigorous", "angry"),
     "低频弦乐铺底加克制的定音鼓；情绪随画面递进，不要从头就满"),
    (("melancholic", "yearning", "sombre", "mournful", "wistful", "nostalgic"),
     "钢琴或弦乐独奏，中慢速，留白多；不要加鼓点"),
    (("mysterious", "uncanny", "oneiric", "unsettling", "dangerous", "intoxicating"),
     "低频嗡鸣加稀疏的金属或拨弦点缀；刻意不给出明确调性"),
    (("playful", "lighthearted", "carefree", "humorous", "flirtatious", "spontaneous"),
     "轻快的中高频乐器（拨弦、木管、马林巴），节奏明快但不抢画面"),
    (("rational", "detached", "functional", "impersonal", "meticulous", "cool"),
     "近乎无配乐；用干净的环境音与机械音建立节奏"),
    (("modern", "futuristic", "luxurious", "glamorous", "futuristic"),
     "合成器 pad 加电子节拍，中速；质感干净，不要复古音色"),
    (("opulent", "ornate", "sensuous", "decorative"),
     "弦乐与竖琴的装饰性织体，中速偏慢；音色温暖华丽"),
    (("alienated", "oppressive", "anxious", "repressed", "uneasy"),
     "持续的低频压力音加不解决的和声；不要旋律"),
]

COMMON_LIMITS = [
    "不要出现文字、字幕、水印",
    "一次只让一个东西动，不要主体和背景同时运动",
    "角色不要变形、多手多指、面部漂移",
    "不要镜头穿模、物体凭空出现或消失",
    "不要中途风格漂移成另一套质感",
]


def _clauses(text):
    t = re.sub(r"[；;]+", "、", (text or "").strip())
    return [x.strip(" 。，,") for x in re.split(r"[、,，]+", t) if x.strip(" 。，,")]


def _camera(cam):
    """返回 (中文说明, 是否固定机位)。"""
    low = (cam or "").lower()
    hits, static = [], False
    for pat, zh in CAMERA_PATTERNS:
        if re.search(pat, low) and zh not in hits:
            hits.append(zh)
            if zh == "固定机位":
                static = True
    if not hits:
        return (cam.strip() or "固定机位"), not cam.strip()
    return "／".join(hits[:2]), static


def _bgm(mood):
    low = (mood or "").lower()
    for keys, val in BGM_RULES:
        if any(k in low for k in keys):
            return val
    return "以环境音为主，配乐克制；不要用情绪过满的管弦乐"


def _zh(visual, key, fallback):
    v = (visual or {}).get(key)
    return (v or fallback).strip()


def build(mv, duration=10):
    """生成两块中文视频提示词。返回 dict。"""
    v = mv.get("video") or {}
    p = mv.get("prompt") or {}
    vis = mv.get("visual") or {}
    motion = v.get("motion") or ""
    note = v.get("note") or ""
    mood = p.get("mood") or ""
    anchor = (p.get("style") or "").strip().rstrip(",")

    dur = int(v.get("duration") or duration)
    seg = max(2, dur // 3)
    camzh, static = _camera(v.get("camera"))
    cl = _clauses(motion) or ["画面内的细微变化"]
    n = max(1, len(cl))
    a = "、".join(cl[:max(1, n // 3)]) or cl[0]
    b = "、".join(cl[max(1, n // 3):max(2, 2 * n // 3)]) or cl[min(1, n - 1)]
    c = "、".join(cl[max(2, 2 * n // 3):]) or cl[-1]

    # 固定机位的流派不能说「镜头缓慢推进」—— 实测色调主义这类流派会自相矛盾
    # camzh 本身常已含「机位/镜头」，再加前缀会变成「镜头机位向前推进」
    _pre = "" if any(x in camzh for x in ("机位", "镜头")) else "镜头"
    cam2 = "镜头全程固定不动" if static else (_pre + camzh + "，幅度很小")
    cam3 = "镜头保持不动" if static else (_pre + camzh + "，缓慢收住")

    body_style = (
        "光线%s；色彩%s；质感取%s。整体情绪是%s。"
        % (_zh(vis, "光影", "按该流派典型光照"),
           _zh(vis, "色彩", "按该流派典型配色"),
           _zh(vis, "材质", "该流派的典型媒介"),
           _zh(vis, "情绪", "该流派的典型情绪"))
    )

    # ---------- A. Seedance 2.5 五段式 ----------
    if v.get("shots"):
        timeline = v["shots"].strip()
    else:
        timeline = (
            "【0—%d秒】起手就给画面最强的视觉信息：%s；%s，第一帧就要立住。\n"
            "【%d—%d秒】%s；%s，让观众看清质感。\n"
            "【%d—%d秒】%s；%s，最后一帧停在能当封面的构图上。"
            % (seg, a, cam2, seg, 2 * seg, b, cam2.replace("固定不动", "仍固定不动")
               if static else cam2, 2 * seg, dur, c, cam3)
        )
    limits = v.get("limits") or ([note] if note else []) + COMMON_LIMITS[:3]
    seedance = "\n".join([
        "【主体】<你的主体>，出现在<场景>。<写清核心事件：谁、在做什么、和什么互动>",
        "",
        "【风格】%d 秒，16:9，高清。%s" % (dur, body_style),
        "风格锚定：%s" % (anchor or mv.get("name_en") or ""),
        "",
        "【时间线】",
        timeline,
        "",
        "【BGM】%s" % (v.get("bgm") or _bgm(mood)),
        "",
        "【限制】%s" % "；".join(limits[:8]),
    ])

    # ---------- B. MiniMax H3（官网 / API）中文自然语言 ----------
    # 刻意不出现 [Shot N]、时间戳、字段名 —— H3 有 Context-IR 前置，
    # 手工结构化会和它打架。只把「它不会替你决定的东西」讲清楚：
    # 时长、镜头意图、声音层次、素材分工。
    # 三元表达式里混 % 格式化很容易写错（实测踩过），改成显式 if/else
    _pre_cam = "" if any(x in camzh for x in ("机位", "镜头")) else "镜头"
    if static:
        h3 = (
            "一段 %d 秒的%s风格视频。画面是<你的主体>，在<场景>中%s。%s"
            "开头两秒就要给出最强的视觉信息。这是几乎静止的画面，镜头全程固定不动，"
            "靠画面内部自身的缓慢变化推进（%s），不要加任何运镜。"
            % (dur, mv.get("name_zh") or "", ("，" + cl[0]) if cl else "", body_style, a)
        )
    else:
        h3 = (
            "一段 %d 秒的%s风格视频。画面是<你的主体>，在<场景>中%s。%s"
            "开头两秒就要给出最强的视觉信息，不要用缓慢推进开场。全片%s。"
            % (dur, mv.get("name_zh") or "", ("，" + cl[0]) if cl else "",
               body_style, _pre_cam + camzh)
        )
    h3 += (
        "声音分三层：环境音按场景给；动作音跟着画面里的动作走；配乐%s。"
        % (v.get("bgm") or _bgm(mood))
    )
    if note:
        h3 += "最容易翻车的一点：%s。" % note
    h3 += "画面里不要出现任何文字、字幕或水印。"
    if v.get("h3_extra"):
        h3 += v["h3_extra"].strip()

    return {"duration": dur, "seedance": seedance, "h3": h3,
            "key": note, "camera_zh": camzh, "static": static,
            "anchor": anchor}


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from movements import MOVEMENTS
    slug = sys.argv[1] if len(sys.argv) > 1 else "baroque"
    m = [x for x in MOVEMENTS if x["slug"] == slug]
    if not m:
        print("未知流派:", slug); sys.exit(1)
    r = build(m[0])
    print("=== A. Seedance 2.5 五段式 ===")
    print(r["seedance"])
    print("\n=== B. MiniMax H3 自然语言 ===")
    print(r["h3"])
