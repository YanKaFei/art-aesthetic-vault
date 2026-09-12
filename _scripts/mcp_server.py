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
]


def _card_brief(c):
    return {"slug": c["slug"], "name_zh": c["name_zh"], "name_en": c["name_en"],
            "category": c["category"], "period": c["period"], "has_images": c["has_images"],
            "one_liner": c["one_liner"]}


def call_tool(name, args):
    A.cards()
    if name == "search_movements":
        return [_card_brief(c) for c in A.search(args.get("query", ""), int(args.get("limit", 8)))]
    if name == "get_movement":
        r = A.search(args.get("slug", ""), 1)
        return r[0] if r else {"error": "未找到流派：" + str(args.get("slug"))}
    if name == "get_layers":
        r = A.search(args.get("slug", ""), 1)
        if not r:
            return {"error": "未找到流派：" + str(args.get("slug"))}
        c = r[0]
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
        r = A.search(args.get("slug", ""), 1)
        return ["%s %s" % (h, n) for h, n in r[0]["palette"]] if r else {"error": "未找到"}
    if name == "list_categories":
        return [{"category": k, "count": len(v)} for k, v in A._CACHE["bycat"].items()]
    if name == "find_related":
        r = A.search(args.get("slug", ""), 1)
        if not r:
            return {"error": "未找到"}
        out = []
        for s in r[0]["see_also"]:
            x = A.by_slug().get(s) or (A.search(s, 1) or [None])[0]
            if x:
                out.append(_card_brief(x))
        return out
    raise ValueError("未知工具：" + name)


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
            text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=1)
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": text}], "isError": False}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": "调用失败：%s\n%s" % (e, traceback.format_exc()[-400:])}],
                "isError": True}}
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
