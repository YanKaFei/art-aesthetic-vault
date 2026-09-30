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

# 工具描述里的数字**现算**，不写死。这个库已经因为写死的统计数字吃过一次亏
# （README 声称 654 张实图，别人克隆下来只有 442 张）。
_N_CARDS = len(A.cards())
_N_CATS = len({c["category"] for c in A.cards()})

# 电影风格库的片数也现算。电影模块缺失（或 fv_data 读不到）时退回 0，
# 工具描述里就会显示 0 部 —— 比在 import 期把整个 MCP 服务炸掉好。
try:
    import fv_core as _F

    _N_FILMS = len(_F.films())
except Exception:
    _N_FILMS = 0

# 镜头配方卡的张数也现算。注意这一轴**不参与** compose 的层解析：
# 它没有色彩/光照语义，混进去只会拼出在编的提示词。
try:
    import shot_core as _S

    _N_SHOTS = len(_S.shots())
except Exception:
    _N_SHOTS = 0

TOOLS = [
    {
        "name": "search_movements",
        "description": ("在 %d 个艺术流派/风格里检索。返回 slug、中英文名、分类、一句话定义。"
                        "当用户提到某种画风、某个艺术家、某种视觉效果时，先用这个找候选。"
                        % _N_CARDS),
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
                        "返回正向、负向、配色、视频层；跨流派时打架的负向词会被自动"
                        "拿掉，拿掉了什么在 dropped 字段里。"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "brief": {"type": "string", "description": "自然语言描述，例如「雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图」"},
                "subject": {"type": "string", "description": "画面主体，建议用英文写，会放在提示词最前面"},
                "style": {"type": "string"}, "lighting": {"type": "string"},
                "color": {"type": "string"}, "composition": {"type": "string"},
                "medium": {"type": "string"}, "mood": {"type": "string"},
                "camera": {"type": "string"},
                "keep_conflicts": {"type": "boolean",
                                   "description": "默认 false：打架的负向词会被自动拿掉。设 true 则只报告、保留原样合集。"},
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
        "description": "列出仓库的 %d 大分类及各自的流派数量。" % _N_CATS,
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
    {
        "name": "search_films",
        "description": ("在电影风格库里检索（按「导演-电影」组织的 %d 部片）。"
                        "当用户说「像某某电影那种画面」「要王家卫的光」「那种霓虹雨夜的感觉」时，"
                        "先用这个找候选片。可以按导演（王家卫）、片名（花样年华）、"
                        "或画面特征（霓虹/逆光/对称/手持/单色/烛光）来搜。" % _N_FILMS),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "关键词，中英文均可。例如「霓虹 雨夜」「王家卫」「bleach bypass」"},
                "limit": {"type": "integer", "description": "返回条数，默认 8", "default": 8},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_film",
        "description": ("取一部电影的完整卡：核心主张、六维视觉拆解、七层提示词、配色、"
                        "视频层、剧照外链、翻车点、关联艺术流派、拍摄班底。"
                        "注意：班底与年份来自 film-grab 可回查；七层是**手写解读**，"
                        "不是逐帧测量结果 —— 返回里的 evidence_note 写明了这一点。"),
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string",
                                    "description": "电影 slug / 中文名 / 英文名，例如 dune / 沙丘 / villeneuve-dune"}},
            "required": ["slug"],
        },
    },
    {
        "name": "get_film_layers",
        "description": ("只取一部电影的七层提示词片段（风格/光照/色彩/构图/媒介/情绪/镜头）。"
                        "比 get_film 省很多 token，适合你要自己组装提示词时用。"
                        "这些层名与艺术流派卡**完全一致**，所以可以跨源混搭："
                        "用 compose_prompt 的 lighting 层传电影 slug、color 层传流派 slug。"),
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "search_shots",
        "description": ("在镜头配方卡库里检索（%d 张运镜/动效招式，来自上游 "
                        "video-shotcraft，Apache-2.0）。当用户问「这个动效怎么做」"
                        "「急推那一下怎么落地」「转场用什么手法」时用这个。"
                        "可以按意图（急推/擦除/卡点/遮罩）、类别（运镜/转场/文字排版）"
                        "或卡名（crash-zoom-punch）搜。"
                        "注意：这些卡讲的是**帧数与缓动参数**，不是画面风格 —— "
                        "要风格请用 search_movements 或 search_films。" % _N_SHOTS),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "关键词，中英文均可。例如「急推 冲击」「crash-zoom-punch」「转场」"},
                "limit": {"type": "integer", "description": "返回条数，默认 8", "default": 8},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_film_stills",
        "description": ("取一部片的**剧照实测**结果：逐张客观测量（明度/对比/饱和度/"
                        "暖度/信息熵/边缘密度/溢出）的全片聚合、实测主色、代表帧"
                        "（k-medoids 选出的真实画面）、景别与构图分布，以及与卡上"
                        "**手写配色**的差异比对。"
                        "注意：返回里的 measured/total_linked 是覆盖度 —— "
                        "未下齐时均值只代表已量的那部分，别当成全片结论。"
                        "实测是**信号不是结论**，它不会覆盖手写的七层与配色。"),
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string",
                                    "description": "电影 slug / 中文名 / 英文名"}},
            "required": ["slug"],
        },
    },
    {
        "name": "get_shot",
        "description": ("取一张镜头配方卡的完整内容：适用场景、时长、能量、"
                        "意图、动效核心、**参数表**（帧数/缓动/幅度）、已知坑、"
                        "Remotion 参考实现，以及上游出处与许可。"
                        "这张卡不是本库原创，技法描述来自上游 video-shotcraft（Apache-2.0）。"),
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string",
                                    "description": "卡名或中文意图，例如 crash-zoom-punch / 急推"}},
            "required": ["slug"],
        },
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


# ------------------------------------------------------------------ 电影风格库
# 电影卡与流派卡的字段名不同（导演而非时期/地区），所以单独一组辅助函数，
# 而不是硬把它塞进 _card_brief —— 那会让流派卡的调用方收到陌生的键。

def _film_brief(f):
    return {"slug": f["slug"], "title_zh": f["title_zh"], "title_en": f["title_en"],
            "director_zh": f["director_zh"], "year": f["year"],
            "one_liner": f["one_liner"], "stills": len(f.get("stills") or []),
            "evidence": f["source"]}


def _film_card(f):
    """整张电影卡。字段与 `artvault.py film show` 一致。"""
    import fv_core as F
    return {
        "slug": f["slug"],
        "title_zh": f["title_zh"], "title_en": f["title_en"],
        "title_original": f.get("title_original"),
        "director_zh": f["director_zh"], "director_en": f["director_en"],
        "year": f["year"],
        "one_liner": f["one_liner"],
        "core": f["core"],
        "visual": f["visual"],
        "palette": ["%s %s" % (h, n) for h, n in f["palette"]],
        "layers": {A.LAYER_ZH[k]: f["layers"][k] for k in F.LAYERS},
        "positive": f["positive"],
        "negative": f["negative"],
        "video": f["video"],
        "pitfalls": f["pitfalls"],
        "see_also": f.get("see_also", []),
        "crew": f.get("crew") or {},
        "crew_verified": f.get("crew_verified", False),
        "filmgrab": f["filmgrab"],
        "stills_sample": (f.get("stills") or [])[:8],
        "stills_total": len(f.get("stills") or []),
        "evidence": f["source"],
        "evidence_note": ("班底与年份已用 film-grab 画廊页核对；七层与视觉拆解是基于"
                          "该片公认摄影特征的**手写解读**，不是逐帧测量结果。"
                          "剧照版权属原片方，这里只给外链不转载。"
                          if f["source"] == "curated" else
                          "从有限信息（片名/导演/年份/剧照）推断，未经画廊页逐项核对。"),
    }


def _film_stills(m, film):
    """剧照实测的精简返回。**必须带上覆盖度** —— 缺了它，调用方会把
    176 张的均值当成 1001 张的结论。"""
    ag = m.get("aggregate") or {}
    n, total = m.get("measured", 0), m.get("total_linked", 0)
    return {
        "slug": m.get("slug"), "title_zh": m.get("title_zh"),
        "director_zh": m.get("director_zh"),
        "measured": n, "total_linked": total,
        "coverage_note": ("已量 %d / 共 %d 张。未下齐时均值只代表已量的那部分，"
                          "不要当成全片结论。" % (n, total) if n < total
                          else "全部 %d 张都已量到。" % n),
        "aggregate": {
            "metrics": {k: {"zh": v["zh"], "mean": v["mean"], "p10": v["p10"],
                            "p50": v["p50"], "p90": v["p90"]}
                        for k, v in (ag.get("metrics") or {}).items()},
            "ratios": ag.get("ratios"), "framing": ag.get("framing"),
            "keys": ag.get("keys"), "temperatures": ag.get("temperatures"),
            "harmonies": ag.get("harmonies"),
            "framing_note": ag.get("framing_note"),
        },
        "palette_written": ["%s %s" % (h, nm) for h, nm in
                            (m.get("palette_written_named") or [])],
        "palette_measured": ["%s %.1f%%" % (h, p) for h, p in
                             (m.get("palette_measured") or [])],
        "palette_diff": m.get("palette_diff"),
        "representative": [{k: x[k] for k in ("index", "file", "luminance",
                                              "saturation", "temperature",
                                              "framing", "key")}
                           for x in (m.get("representative") or [])],
        "skipped": m.get("skipped") or [],
        "note": "实测是信号不是结论：它**不会**覆盖手写的七层与配色。"
                "剧照版权属原片方，本地副本仅供个人研究（gitignore）。",
    }


def _shot_brief(x):
    import shot_core as S
    return {"name": x["name"], "category": x["category"],
            "category_zh": S.CATEGORY_ZH.get(x["category"], ""),
            "one_liner": x["one_liner"], "duration": x["duration"],
            "energy": x["energy"], "tags": x["tags"]}


def _shot_card(x):
    """整张镜头卡。**带上游出处与许可** —— Apache-2.0 的要求，
    也是「不得读起来像本站原创」的底线。"""
    import shot_core as S
    return {
        "name": x["name"],
        "category": x["category"],
        "category_zh": S.CATEGORY_ZH.get(x["category"], ""),
        "one_liner": x["one_liner"],
        "purpose": x["purpose"],
        "duration": x["duration"],
        "energy": x["energy"],
        "tags": x["tags"],
        "intent": x["intent"],
        "motion": x["motion"],
        "params": x["params"],
        "pitfalls": x["pitfalls"],
        "reference_impl": x["reference"],
        "sections": [{"title": s2["title"], "body": s2["body"]} for s2 in x["sections"]],
        "source_repo": x["source_repo"],
        "source_url": x["source_url"],
        "source_path": x["source_path"],
        "source_commit": x["source_commit"],
        "license": x["license"],
        "note": "技法描述版权归上游 video-shotcraft（Apache-2.0），本库只做归类与排版。"
                "这些卡讲的是动效时序与参数，不是画面风格，因此不参与风格层混搭。",
    }


def _shot_not_found(ident, hints):
    out = {"error": "未找到镜头卡：%s" % ident}
    if hints:
        out["did_you_mean"] = [{"name": h["name"], "one_liner": h["one_liner"][:50]}
                               for h in hints]
    else:
        out["hint"] = "用 search_shots 按意图或卡名检索（如「急推」「转场」「crash-zoom-punch」）"
    return out


def _film_not_found(ident, hints):
    out = {"error": "未找到电影：%s" % ident}
    if hints:
        out["did_you_mean"] = [{"slug": x["slug"], "title_zh": x["title_zh"],
                                "director_zh": x["director_zh"]} for x in hints]
    else:
        out["hint"] = "用 search_films 按风格词/导演/片名做模糊检索"
    return out


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
        r = A.compose(brief=args.get("brief", ""), subject=args.get("subject"),
                      resolve_conflicts=not args.get("keep_conflicts"), **kw)
        return {"positive": r["positive"], "negative": r["negative"],
                "palette": ["%s %s" % (h, n) for h, n in r["palette"]],
                "layers": {A.LAYER_ZH.get(k, k): v["name"] for k, v in r["layers"].items()},
                "video": r["video"], "conflicts": r["conflicts"], "dropped": r["dropped"],
                "notes": r["notes"], "rendered": A.render(r)}
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

    # ---------------------------------------------------------- 电影风格库
    if name in ("search_films", "get_film", "get_film_layers"):
        import fv_core as F
        if name == "search_films":
            return [_film_brief(f) for f in F.search(args.get("query", ""),
                                                     int(args.get("limit", 8)))]
        f, hints = F.resolve(args.get("slug", ""))
        if not f:
            return _film_not_found(args.get("slug"), hints)
        if name == "get_film_layers":
            return {"slug": f["slug"], "title_zh": f["title_zh"],
                    "director": f["director_zh"], "year": f["year"],
                    "layers": {A.LAYER_ZH[k]: f["layers"][k] for k in F.LAYERS},
                    "negative": f["negative"]}
        return _film_card(f)

    if name == "get_film_stills":
        import fv_core as F2
        f, hints = F2.resolve(args.get("slug", ""))
        if not f:
            return _film_not_found(args.get("slug"), hints)
        import still_analysis as SA
        m = SA.load_measurements(f["slug"])
        if not m:
            return {"error": "这部片还没实测过：%s" % f["slug"],
                    "hint": "跑 python3 still_analysis.py --slug %s" % f["slug"]}
        return _film_stills(m, f)

    # ---------------------------------------------------------- 镜头配方卡库
    if name in ("search_shots", "get_shot"):
        import shot_core as S
        if name == "search_shots":
            return [_shot_brief(x) for x in S.search(args.get("query", ""),
                                                     int(args.get("limit", 8)))]
        x, hints = S.resolve(args.get("slug", ""))
        if not x:
            return _shot_not_found(args.get("slug"), hints)
        return _shot_card(x)
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
                "how_to_fix": "cd .repo && python3 clip_embed.py download && python3 clip_embed.py build"}
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
    from clihelp import guard
    guard(sys.argv[1:], "python3 mcp_server.py",
          ["起一个 stdio MCP 服务，供 Claude Desktop / Cursor / DSH 直连。",
           "没有任何选项：服务通过 stdin/stdout 收发 JSON-RPC，",
           "所以直接运行它会「卡住」—— 那是在等客户端说话，不是死循环。",
           "配置样例见本文件开头和 README 的「方式四：接入 MCP」。"])
    sys.exit(main())
