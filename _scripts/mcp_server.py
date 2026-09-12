#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_server.py —— 把艺术审美风格库暴露成一个 MCP 服务。

这样 Claude Desktop / Cursor / Cline / DSH 等任何支持 MCP 的客户端
就能直接「调取」这个仓库：搜流派、取提示词层、按创意想法拼提示词。

只依赖标准库，不需要 pip install mcp。

接到客户端（以 Claude Desktop 为例，配置放在
  ~/Library/Application Support/Claude/claude_desktop_config.json）：

  {
    "mcpServers": {
      "artvault": {
        "command": "python3",
        "args": ["<本文件绝对路径>"]
      }
    }
  }

手动测试：
  echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 mcp_server.py
"""

import json
import os
import sys
import traceback

import artvault_core as A

PROTOCOL = "2024-11-05"
SERVER = {"name": "artvault", "version": "1.0.0"}

TOOLS = [
    {
        "name": "search_movements",
        "description": ("在 141 个艺术流派/风格里检索。返回 slug、中英文名、分类、一句话定义。"
                        "当用户提到某种画风、某个艺术家、某种视觉效果时，先用这个找候选。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "关键词，中英文均可。例如「巴洛克」「tenebrism」「霓虹雨夜」"},
                "limit": {"type": "integer", "description": "返回条数，默认 8", "default": 8},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_movement",
        "description": "取某个流派的完整卡片：核心主张、六维视觉拆解、七层提示词、配色、视频层、常见翻车点、关联流派。",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string", "description": "流派 slug 或中文名，例如 baroque / 巴洛克"}},
            "required": ["slug"],
        },
    },
    {
        "name": "get_layers",
        "description": ("只取某个流派的七层提示词片段（风格/光照/色彩/构图/媒介/情绪/镜头）。"
                        "比 get_movement 省很多 token，适合你要自己组装提示词时用。"),
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "compose_prompt",
        "description": ("把创意想法拼成完整提示词。支持两种用法："
                        "① brief 传一句自然语言，会自动识别提到的流派并按意图分配到各层；"
                        "② 显式指定 style/lighting/color/composition 等层做跨流派混搭。"
                        "返回正向、负向、配色、视频层，以及层级冲突警告。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brief": {"type": "string", "description": "自然语言描述，例如「雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图」"},
                "subject": {"type": "string", "description": "画面主体，建议用英文写，会放在提示词最前面"},
                "style": {"type": "string"}, "lighting": {"type": "string"},
                "color": {"type": "string"}, "composition": {"type": "string"},
                "medium": {"type": "string"}, "mood": {"type": "string"},
                "camera": {"type": "string"},
            },
        },
    },
    {
        "name": "get_palette",
        "description": "取某个流派的六色配色（hex + 颜色名）。",
        "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}}, "required": ["slug"]},
    },
    {
        "name": "list_categories",
        "description": "列出仓库的 6 大分类及各自的流派数量。",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "find_related",
        "description": "找某个流派的关联流派，用于风格迁移和混搭探索。",
        "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}}, "required": ["slug"]},
    },
    {
        "name": "analyze_image",
        "description": ("对一张本地图片做客观测量，返回明度/对比/色彩/和谐/构图/质感/线条"
                        "七个维度，以及人脸景别、霍夫直线、显著性（装了 numpy+opencv 时）。"
                        "用途：拆解参考图时先拿到可量化的信号，再结合看图做判断。"
                        "注意：这些数字是**信号不是结论**，风格判断仍需以流派卡为准。"),
        "inputSchema": {"type": "object",
                        "properties": {"path": {"type": "string",
                                                "description": "图片的本地路径（绝对或相对仓库根）"}},
                        "required": ["path"]},
    },
    {
        "name": "match_movement",
        "description": ("给一张本地图片，返回画面内容最像的几个艺术流派（CLIP 语义匹配，"
                        "含零样本：库里没有实图的流派也能匹配到）。"
                        "实测 Top-1 准确率约 39%（随机基准 1.4%），是**建议**不是结论。"
                        "需要先跑 clip_embed.py download 下模型，未下模型时返回明确原因。"),
        "inputSchema": {"type": "object",
                        "properties": {"path": {"type": "string", "description": "图片的本地路径"},
                                       "topn": {"type": "integer", "default": 5}},
                        "required": ["path"]},
    },
    {
        "name": "get_video_prompt",
        "description": ("取某个流派**可直接粘贴的中文视频提示词**，两块格式不同、不能混用："
                        "A 块是 Seedance 2.5 五段式（主体/风格/时间线/BGM/限制）；"
                        "B 块是 MiniMax H3（海螺）官网/API 用的中文自然语言 —— "
                        "H3 有 Context-IR 前置，手工结构化会和它打架，所以 B 块刻意不结构化。"),
        "inputSchema": {"type": "object",
                        "properties": {"slug": {"type": "string",
                                                "description": "流派 slug 或中文名，例如 baroque / 巴洛克"}},
                        "required": ["slug"]},
    },
]


def _not_found(ident, hints):
    """统一的「没找到」响应 —— 带候选而不是静默挑一个。

    原来这几个工具都用 A.search() 做标识符查找，而 search 是全文模糊检索：
    实测 get_movement("不存在") 会返回「原生艺术 Art Brut」，因为那张卡片的
    描述里恰好有「不存在」这个词。问一个流派得到另一个流派，
    比明确报错糟得多。
    """
    out = {"error": "未找到流派：%s" % ident}
    if hints:
        out["did_you_mean"] = [{"slug": x["slug"], "name_zh": x["name_zh"]} for x in hints]
    else:
        out["hint"] = "用 search_movements 做模糊检索，或 list_categories 看全部流派"
    return out


def _card_brief(c):
    return {"slug": c["slug"], "name_zh": c["name_zh"], "name_en": c["name_en"],
            "category": c["category"], "period": c["period"], "has_images": c["has_images"],
            "one_liner": c["one_liner"]}


def call_tool(name, args):
    A.cards()
    if name == "search_movements":
        return [_card_brief(c) for c in A.search(args.get("query", ""), int(args.get("limit", 8)))]
    if name == "get_movement":
        c, hints = A.resolve(args.get("slug", ""))
        if not c:
            return _not_found(args.get("slug"), hints)
        return c
    if name == "get_layers":
        c, hints = A.resolve(args.get("slug", ""))
        if not c:
            return _not_found(args.get("slug"), hints)
        return {"slug": c["slug"], "name_zh": c["name_zh"],
                "layers": {A.LAYER_ZH[k]: v for k, v in c["prompt"].items()},
                "negative": c["negative"]}
    if name == "compose_prompt":
        kw = {l: args.get(l) for l in A.LAYERS if args.get(l)}
        r = A.compose(brief=args.get("brief", ""), subject=args.get("subject"), **kw)
        return {"positive": r["positive"], "negative": r["negative"],
                "palette": ["%s %s" % (h, n) for h, n in r["palette"]],
                "layers": {A.LAYER_ZH.get(k, k): v["name"] for k, v in r["layers"].items()},
                "video": r["video"], "conflicts": r["conflicts"], "notes": r["notes"],
                "rendered": A.render(r)}
    if name == "get_palette":
        c, hints = A.resolve(args.get("slug", ""))
        if not c:
            return _not_found(args.get("slug"), hints)
        return ["%s %s" % (h, n) for h, n in c["palette"]]
    if name == "list_categories":
        return [{"category": k, "count": len(v)} for k, v in A._CACHE["bycat"].items()]
    if name == "find_related":
        c, hints = A.resolve(args.get("slug", ""))
        if not c:
            return _not_found(args.get("slug"), hints)
        out = []
        for s in c["see_also"]:
            x = A.by_slug().get(s) or A.lookup(s)
            if x:
                out.append(_card_brief(x))
        return out
    if name == "analyze_image":
        return _analyze_image(args.get("path", ""))
    if name == "match_movement":
        return _match_movement(args.get("path", ""), int(args.get("topn", 5)))
    if name == "get_video_prompt":
        c, hints = A.resolve(args.get("slug", ""))
        if not c:
            return _not_found(args.get("slug"), hints)
        r = A.video_prompts(c)
        return {"movement": c["name_zh"], "duration_seconds": r["duration"],
                "seedance_2_5": r["seedance"], "minimax_h3": r["h3"],
                "note": "两块格式不同不能混用：H3 官网/API 用 minimax_h3（自然语言），"
                        "Seedance 用 seedance_2_5（五段式）。"}
    raise ValueError("未知工具：" + name)


def _analyze_image(path):
    """T1 客观测量。返回拍平后的字段（原始的嵌套结构对模型不友好）。"""
    if not path:
        return {"error": "缺少 path"}
    try:
        import image_analysis as IA
    except Exception as e:
        return {"error": "图片分析不可用（需要 Pillow）：%s" % str(e)[:80]}
    r = IA.analyze(path)
    if r.get("error"):
        return {"error": r["error"]}
    lu, co, cl = r["luminance"], r["contrast"], r["color"]
    hm, cp, tx, ln = r["harmony"], r["composition"], r["texture"], r["lines"]
    out = {
        "file": r["file"], "size": r["size"], "orientation": r["orientation"],
        "明度": {"均值": lu["mean"], "标准差": lu["std"], "基调": lu["key"],
                 "暗部溢出%": lu["shadow_clip_pct"], "高光溢出%": lu["highlight_clip_pct"]},
        "对比": {"RMS": co["rms"], "Michelson": co["michelson"], "分级": co["level"]},
        "色彩": {"色温": cl["temperature"], "暖度分": cl["warm_score"],
                 "饱和度": cl["saturation"],
                 "主色": ["%s %.0f%%" % (d["hex"], d["pct"]) for d in cl["dominant"]]},
        "和谐": {"关系": hm["scheme"], "集中度": hm["concentration"],
                 "有效色相数": hm["effective_hues"], "主色相": hm["mean_hue_name"]},
        "构图": {"三分法": cp["subject_on_thirds"], "对称": cp["symmetry_hint"],
                 "中心权重": cp["center_weight"]},
        "质感": {"边缘密度": tx["edge_density"], "熵": tx["entropy"], "繁杂度": tx["busyness"]},
        "线条": {"方向": ln["orientation"], "主导角": ln["dominant_angle"]},
    }
    # 两个对比度打架是个有意义的信号：大面积暗调 + 小面积高光 = 明暗对照法
    if co["rms"] < 45 and co["michelson"] > 0.85:
        out["提示"] = "RMS 低但 Michelson 高 —— 明暗对照法（chiaroscuro）的签名"
    if r.get("extended"):
        e = r["extended"]
        if isinstance(e.get("faces"), dict) and "error" not in e["faces"]:
            out["人脸"] = e["faces"]
        if isinstance(e.get("hough"), dict) and "error" not in e["hough"]:
            h = e["hough"]
            out["直线"] = {"条数": h["count"], "水平": h["horizontal"],
                           "垂直": h["vertical"], "斜向": h["diagonal"], "说明": h["hint"]}
        if isinstance(e.get("saliency"), dict) and "error" not in e["saliency"]:
            sz = e["saliency"]
            out["显著性"] = {"重心": [sz["center_x"], sz["center_y"]],
                             "最大显著区": sz["main_region"], "判定": sz["focus"]}
    out["免责"] = "这些是客观测量信号，不是风格结论。风格判断以 artvault 的流派卡为准。"
    return out


def _match_movement(path, topn):
    """T3 图像→流派匹配（CLIP）。"""
    if not path:
        return {"error": "缺少 path"}
    try:
        import clip_embed
        import clip_match
    except Exception as e:
        return {"error": "CLIP 模块不可用：%s" % str(e)[:80]}
    why = clip_embed.available()
    if why:
        return {"error": why,
                "how_to_fix": "cd _scripts && python3 clip_embed.py download && python3 clip_embed.py build"}
    r = clip_match.suggest([path], topn=topn)
    rows = r.get(path) or []
    if not rows:
        return {"error": "匹配失败（文件不存在或不是有效图片）：%s" % path}
    return {
        "query": os.path.basename(path),
        "suggestions": [{"slug": s, "name": n, "score": round(sc, 3)} for s, n, sc in rows],
        "accuracy": "实测 Top-1 39.1% / Top-3 61.4%（随机基准 1.4%）—— 当建议用",
        "next": "用 get_movement 取建议流派的完整卡片来确认是否真的对得上",
    }


def _tool_error(mid, text):
    """统一构造一个「工具执行失败」的响应。"""
    return {"jsonrpc": "2.0", "id": mid, "result": {
        "content": [{"type": "text", "text": text}], "isError": True}}


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": PROTOCOL,
            "capabilities": {"tools": {}},
            "serverInfo": SERVER,
        }}
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        p = msg.get("params") or {}
        name = p.get("name")
        try:
            data = call_tool(name, p.get("arguments") or {})
        except Exception as e:
            return _tool_error(mid, "调用失败：%s\n%s" % (e, traceback.format_exc()[-400:]))
        text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=1)
        # 工具层的失败（找不到流派、图片读不了、CLIP 没装…）是以 {"error": ...}
        # **正常返回**的，不是抛异常。按 MCP 约定这类也要标 isError: true，
        # 否则客户端会把「没找到」当成成功结果。原来只有抛异常那条路径标了，
        # 于是同一个协议里有两种错误表示 —— 实测 analyze_image 传不存在的
        # 路径时返回 isError: false，这是错的。
        is_err = isinstance(data, dict) and "error" in data
        return {"jsonrpc": "2.0", "id": mid, "result": {
            "content": [{"type": "text", "text": text}], "isError": bool(is_err)}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}
    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid,
            "error": {"code": -32601, "message": "未实现的方法：" + str(method)}}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        resp = handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
