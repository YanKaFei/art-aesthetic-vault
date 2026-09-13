#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
artvault —— 仓库的命令行入口，也是给 AI 用的调用接口。

任何能执行 shell 的 AI（Claude Code / Cursor / DSH / 自建 agent）都可以直接调它，
拿到结构化的流派数据与拼好的提示词。

用法：
  python3 artvault.py categories                     列出所有分类
  python3 artvault.py list [--category 分类] [--with-images]
  python3 artvault.py search "霓虹 雨夜"               模糊检索
  python3 artvault.py show 巴洛克                      看一张卡的完整内容
  python3 artvault.py layers 巴洛克                    只看七层提示词（最省 token）
  python3 artvault.py palette 印象派                   取配色
  python3 artvault.py related 立体主义                 关联流派
  python3 artvault.py compose "雨夜霓虹的赏金猎人，要巴洛克的光照" \
        --subject "a female bounty hunter"
  python3 artvault.py compose --style ukiyo-e --lighting baroque --subject "a samurai"
  python3 artvault.py dump --json                     导出全库 JSON（喂给别的程序）

加 --json 到任意命令可得到机器可读输出。
"""

import argparse
import json
import os
import sys

import artvault_core as A


def out(obj, as_json):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=1))
    return as_json



# ------------------------------------------------------------------ doctor
def _dep_paths():
    """和别的脚本一致的依赖发现顺序（vendor/libs 优先）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    for c in (os.environ.get("ARTVAULT_DEPS", ""),
              os.path.join(here, "vendor", "libs"),
              os.path.expanduser("~/.artvault/deps")):
        if c and os.path.isdir(c) and c not in sys.path:
            sys.path.insert(0, c)


def _has(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def doctor():
    """环境自检：现在能用什么、缺什么、装了能多什么。

    ## 为什么要有这个命令

    README 说「核心只用标准库」，可选依赖散在文档各处，还有个特殊约定
    （装到 `./vendor/libs` 而不是系统 Python）。读者 clone 下来第一件事是
    「我到底要不要装东西」，而这个问题的答案散在四五个小节里。
    这里一次性回答，并给出**可以直接复制的那一条命令**。

    ## 判断来源

    不在这里另写一套可用性判断 —— 能用各模块自己的检查就用它们的
    （`clip_embed.available()` / `image_analysis_ext.available()` /
    `artvault_vision.unavailable_reason()`），省得两处判断各说各话。
    """
    _dep_paths()
    core = [
        ("流派检索与分层提示词", True, "categories / search / layers / show / palette / related"),
        ("拼提示词与冲突消解", True, "compose（跨流派混搭自动消解矛盾负向词）"),
        ("视频提示词 / 图生视频", True, "video / i2v_prompt 的文本部分"),
        ("重建整个仓库", True, "build_vault"),
        ("MCP 服务", True, "mcp_server（10 个工具）"),
    ]
    opt = []

    have_pil = _has("PIL")
    opt.append(("图片客观测量（七维）", have_pil, "Pillow",
                "image_analysis：明度/对比/色彩/和谐/构图/质感/线条"))

    have_np, have_cv = _has("numpy"), _has("cv2")
    opt.append(("增强维度（人脸/直线/显著性）", have_np and have_cv,
                "numpy + opencv-python-headless",
                "image_analysis_ext：只在装了 opencv 时才有这三项"))

    # CLIP：用模块自己的判断
    clip_ok, clip_why = False, "没试"
    try:
        import clip_embed as CE
        clip_ok = CE.available() is None
        clip_why = "" if clip_ok else CE.available()
    except Exception as e:
        clip_why = "%s: %s" % (type(e).__name__, e)
    opt.append(("语义检索 / 图像→流派匹配", clip_ok,
                "onnxruntime + tokenizers + 模型(>150MB)",
                "clip_match / search --semantic；中文会先过 visual_lexicon 的桥"))

    # macOS Vision：不用装东西，但只有 macOS 有
    vis_ok, vis_why = False, ""
    try:
        import artvault_vision as AV
        r = AV.unavailable_reason()
        vis_ok = not r
        vis_why = r or ""
    except Exception as e:
        vis_why = str(e)
    opt.append(("近重复检测 / 以图搜图", vis_ok, "macOS 系统自带（无需安装）",
                vis_why or "artvault_vision：近重复这一项实测最可靠"))

    req = _has("requests")
    opt.append(("抓图（CC0 数据源 / Pinterest）", req, "requests",
                "fetch_art / pinterest_grab"))

    print("艺术审美风格库 · 环境自检")
    print("=" * 62)
    print("\n【核心】不需要装任何东西（只用标准库）")
    for name, ok, note in core:
        print("  %s %-24s %s" % ("✓" if ok else "✗", name, note))

    print("\n【可选】装了多一层能力，不装不影响上面的核心")
    missing = []
    for name, ok, need, note in opt:
        print("  %s %-24s %s" % ("✓" if ok else "·", name, note))
        if not ok:
            missing.append((name, need))
    if missing:
        print("\n【缺什么】")
        for name, need in missing:
            print("  · %-24s 需要 %s" % (name, need))
        deps = ["Pillow", "numpy", "opencv-python-headless",
                "onnxruntime", "tokenizers", "requests"]
        print("\n【怎么装】在 _scripts/ 下执行（装到 vendor/libs，不动系统 Python）：")
        print("  pip3 install --target ./vendor/libs " + " ".join(deps))
        print("  或只装你要的： pip3 install --target ./vendor/libs Pillow")
        print("  也可以：     pip3 install --target ./vendor/libs -r ../requirements-optional.txt")
        print("\n  装完 CLIP 还要下模型：python3 clip_embed.py download")
    else:
        print("\n可选依赖都齐了。")
    print("\n【核对】依赖装在哪：ARTVAULT_DEPS 环境变量 > vendor/libs > ~/.artvault/deps")
    # 不写死项数 —— 这个仓库已经因为写死数字吃过好几次亏（README 统计、
    # 冒烟里的「141 张卡」、以及这里原本写着的「22 项 / 38 项」）。
    # 项数会随改动变化，写死那个数字唯一的作用就是某天变成错的。
    print("\n【验收】python3 verify_vault.py ｜ python3 ../tests/smoke_test.py")
    return 0


def main():
    # `--json` 要能放在命令**前面或后面**。
    # 原来只在顶层定义，于是 `artvault.py dump --json` 直接报
    # 「unrecognized arguments: --json」—— 而帮助里写着「加 --json 到任意命令」，
    # 使用者自然会写在后面。两处都能认的做法：子命令各挂一个同名的
    # `--json`，但 default 用 SUPPRESS —— 没写时**不设这个属性**，
    # 顶层解析到的值就不会被 False 覆盖。（argparse 的经典覆盖陷阱。）
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="输出 JSON（放命令前或后都行）")

    ap = argparse.ArgumentParser(description="艺术审美风格库 · 检索与提示词组合")
    ap.add_argument("--json", action="store_true", help="输出 JSON（放命令前或后都行）")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, **kw):
        return sub.add_parser(name, parents=[common], **kw)

    add("categories")
    p = add("list"); p.add_argument("--category"); p.add_argument("--with-images", action="store_true")
    p = add("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=8)
    p.add_argument("--semantic", action="store_true",
                   help="把 CLIP 语义分融进来（中文会先过 visual_lexicon 的桥）；"
                        "没下模型时自动退回纯关键词")
    p = add("show"); p.add_argument("slug")
    p = add("layers"); p.add_argument("slug")
    p = add("palette"); p.add_argument("slug")
    p = add("related"); p.add_argument("slug")
    p = add("video"); p.add_argument("slug")   # 两块可粘贴的视频提示词
    p = add("compose")
    p.add_argument("brief", nargs="?", default="")
    p.add_argument("--subject")
    p.add_argument("--keep-conflicts", action="store_true",
                   help="只报告层级冲突，不自动丢掉打架的负向词（默认会自动丢）")
    for l in A.LAYERS:
        p.add_argument("--" + l)
    add("dump")
    add("doctor")

    a = ap.parse_args()
    if not a.cmd:
        ap.print_help(); return 0
    A.cards()

    if a.cmd == "categories":
        if out(A._CACHE["cats"], a.json): return 0
        for c in A._CACHE["cats"]:
            n = len(A._CACHE["bycat"][c])
            print("  %-24s %3d 个流派" % (c, n))

    elif a.cmd == "list":
        cs = [c for c in A.cards() if (not a.category or c["category"] == a.category)
              and (not a.with_images or c["has_images"])]
        if out([{k: c[k] for k in ("slug", "name_zh", "name_en", "category", "has_images")} for c in cs], a.json):
            return 0
        cur = None
        for c in cs:
            if c["category"] != cur:
                cur = c["category"]; print("\n【%s】" % cur)
            print("  %-12s %-30s %s" % (c["slug"], c["name_zh"], "有图" if c["has_images"] else ""))

    elif a.cmd == "search":
        r = A.search(a.query, a.n, semantic=a.semantic)
        if out([{k: c[k] for k in ("slug", "name_zh", "name_en", "category", "one_liner")} for c in r], a.json):
            return 0
        if not r:
            print("  没找到。试试换个说法，或加 --semantic（要下过 CLIP 模型）")
            if not a.semantic:
                print("  提示：中文描述性查询（如「压抑但华丽的光」）关键词匹配抓不住，"
                      "语义检索才有用")
            return 0
        for c in r:
            print("  %-12s %-10s %s" % (c["slug"], c["name_zh"], c["one_liner"]))

    elif a.cmd == "video":
        c, hints = A.resolve(a.slug)
        if not c:
            print("没找到：%s" % a.slug); return 1
        r = A.video_prompts(c)
        if out({"seedance": r["seedance"], "minimax_h3": r["h3"],
                "duration": r["duration"]}, a.json):
            return 0
        print("== %s · AI 视频层 ==" % c["name_zh"])
        print()
        print("【A】Seedance 2.5 五段式（直接粘贴，单条最长 30s）")
        print("─" * 58)
        print(r["seedance"])
        print()
        print("【B】MiniMax H3 海螺（官网/API，中文自然语言，4–15 秒）")
        print("─" * 58)
        print(r["h3"])
        print()
        print("※ 两块不要混用：H3 有 Context-IR 前置，手工塞分镜和时间戳会和它打架。")
        return 0

    elif a.cmd in ("show", "layers", "palette", "related"):
        # 标识符查找走 A.resolve()，不走 search() —— search 是全文模糊检索，
        # 会命中卡片正文（实测 show 一个不存在的名字会返回「原生艺术」，
        # 因为那张卡的描述里有「不存在」这个词）。问一个流派得到另一个，
        # 比明确报错糟得多。
        c, hints = A.resolve(a.slug)
        if not c:
            print("没找到：%s" % a.slug)
            if hints:
                print("你是不是想找：")
                for x in hints:
                    print("  %-12s %-10s %s" % (x["slug"], x["name_zh"], x["one_liner"]))
            else:
                print("用 search 做模糊检索，或 categories 看全部流派。")
            return 1
        if a.cmd == "show":
            if out(c, a.json): return 0
            print(A.format_card(c))
        elif a.cmd == "layers":
            if out(c["prompt"], a.json): return 0
            for l in A.LAYERS:
                if c["prompt"].get(l):
                    print("%-4s %s" % (A.LAYER_ZH[l], c["prompt"][l]))
        elif a.cmd == "palette":
            if out(c["palette"], a.json): return 0
            for h, n in c["palette"]:
                print("  %s  %s" % (h, n))
        else:
            # see_also 里存的是 slug，直接按 slug 取；取不到再退回解析
            rel = [A.by_slug().get(s) or A.lookup(s) for s in c["see_also"]]
            rel = [x for x in rel if x]
            if out([{k: x[k] for k in ("slug", "name_zh", "name_en")} for x in rel], a.json):
                return 0
            for x in rel:
                print("  %-12s %-10s %s" % (x["slug"], x["name_zh"], x["one_liner"]))

    elif a.cmd == "compose":
        kw = {l: getattr(a, l) for l in A.LAYERS if getattr(a, l)}
        r = A.compose(brief=a.brief, subject=a.subject,
                      resolve_conflicts=not a.keep_conflicts, **kw)
        if out(r, a.json): return 0
        print(A.render(r))

    elif a.cmd == "doctor":
        return doctor()

    elif a.cmd == "dump":
        print(json.dumps(A.cards(), ensure_ascii=False, indent=1))

    return 0


if __name__ == "__main__":
    sys.exit(main())
