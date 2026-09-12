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
import sys

import artvault_core as A


def out(obj, as_json):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=1))
    return as_json


def main():
    ap = argparse.ArgumentParser(description="艺术审美风格库 · 检索与提示词组合")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("categories")
    p = sub.add_parser("list"); p.add_argument("--category"); p.add_argument("--with-images", action="store_true")
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=8)
    p = sub.add_parser("show"); p.add_argument("slug")
    p = sub.add_parser("layers"); p.add_argument("slug")
    p = sub.add_parser("palette"); p.add_argument("slug")
    p = sub.add_parser("related"); p.add_argument("slug")
    p = sub.add_parser("compose")
    p.add_argument("brief", nargs="?", default="")
    p.add_argument("--subject")
    for l in A.LAYERS:
        p.add_argument("--" + l)
    sub.add_parser("dump")

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
        r = A.search(a.query, a.n)
        if out([{k: c[k] for k in ("slug", "name_zh", "name_en", "category", "one_liner")} for c in r], a.json):
            return 0
        for c in r:
            print("  %-12s %-10s %s" % (c["slug"], c["name_zh"], c["one_liner"]))

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
        r = A.compose(brief=a.brief, subject=a.subject, **kw)
        if out(r, a.json): return 0
        print(A.render(r))

    elif a.cmd == "dump":
        print(json.dumps(A.cards(), ensure_ascii=False, indent=1))

    return 0


if __name__ == "__main__":
    sys.exit(main())
