#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_merge.py —— 校验 `fv_new_*.py` 里的新片数据，齐全后合并进 `fv_data.FILMS`。

## 为什么需要这一步

加片子分三段：**写七层（离线）→ 解析 URL（联网）→ 抓班底与剧照（联网）**。
如果七层一写好就塞进 `fv_data.FILMS`，那么在 URL 还没注入之前，
`fv_build.py` 会生成一批**没有画廊页链接的空壳卡**，而验收只检查
「卡片文件在不在」，不会发现内容缺了 —— 这类错最难查。

所以分批数据先独立存放，本模块负责**闸门**：

    --check    只校验（schema 完整、与候选清单对得上、无重名）
    --merge    校验通过后把新片写进 fv_data.py 的 FILMS（先备份）

## 合并是**可重复**的，靠标记块

写进去的新片被包在

    # >>> 新增完整片（fv_merge.py 生成，勿手改）BEGIN
    ...
    # <<< 新增完整片 END

之间。重跑 `--merge` 会**替换这个块**而不是再追加一遍 —— 否则第二次
合并就会让每部片出现两遍（这个错误会一路传到卡片生成，很难回查）。
`--check` 里有一条专门守「没有重复 slug」。

## 校验什么

1. 字段齐全（与 `fv_data.FILMS` 同一套 schema）
2. `see_also` 里的 slug 在艺术/电影库里真的存在（否则生成断链）
3. `palette` 恰好 6 色且是合法 hex
4. 七层齐全、非空
5. slug 不与现有片子或其它批次撞车
6. batch 里的片都在 `fv_candidates.CANDIDATES` 里（选片口径不能悄悄跑偏）
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

REQUIRED = ("slug", "director_zh", "director_en", "director_slug", "title_zh",
            "title_en", "year", "one_liner", "core", "visual", "layers",
            "negative", "palette", "video", "pitfalls", "see_also", "source")
LAYERS = ("style", "lighting", "color", "composition", "medium", "mood", "camera")
DIMS = ("色彩", "光影", "笔触", "构图", "材质", "情绪")


def batches():
    """找出全部 fv_new_*.py，按编号排序返回 [(模块名, BATCH)]。"""
    import importlib
    out = []
    for fn in sorted(os.listdir(HERE)):
        m = re.fullmatch(r"(fv_new_\d+)\.py", fn)
        if not m:
            continue
        mod = importlib.import_module(m.group(1))
        out.append((m.group(1), list(getattr(mod, "BATCH", []))))
    return out


def all_new():
    out = []
    for name, b in batches():
        for f in b:
            out.append((name, f))
    return out


def _handwritten_slugs():
    """fv_data.FILMS 里**标记块之外**（即人写的）的 slug。

    ⚠ 为什么不能直接用 `fv_data.FILMS`：合并成功之后再跑 `--check`，
    已合并的片子也在 FILMS 里，于是每一个都会被判成「与现有片子撞 slug」
    而拒绝合并 —— 工具就**不能重跑**了，与「幂等」直接矛盾（实测踩到，
    86 部全报撞车）。

    标记块是我们自己写的区域，里面的 slug 本来就该在这里；只有**块外**
    的同名才是真的撞车。
    """
    src = open(os.path.join(HERE, "fv_data.py"), encoding="utf-8").read()
    if BEGIN.strip() in src and END.strip() in src:
        i = src.index(BEGIN.strip())
        j = src.index(END.strip())
        src = src[:i] + src[j:]
    return set(re.findall(r'"slug":\s*"([^"]+)"', src))


def check():
    import fv_data
    import fv_candidates as C
    import artvault_core as A
    problems = []
    have = _handwritten_slugs()
    cand = {c["slug"] for c in C.CANDIDATES}
    seen = {}
    mv_slugs = set(A.by_slug())

    for mod, f in all_new():
        slug = f.get("slug", "?")
        where = "%s/%s" % (mod, slug)
        if slug in seen:
            problems.append((where, "与前一批撞 slug（%s）" % seen[slug]))
        seen[slug] = mod
        if slug in have:
            problems.append((where, "与现有片子撞 slug"))
        if slug not in cand:
            problems.append((where, "不在 fv_candidates 清单里（选片口径跑偏？）"))
        for k in REQUIRED:
            if k not in f:
                problems.append((where, "缺字段 %s" % k))
        # ⚠ 只查「字段在不在」不够 —— 实测有两部片的 negative 被写成了
        # **列表**而不是字符串，一路通过校验，直到卡片生成时才炸
        # （`'list' object has no attribute 'strip'`）。所以这里查类型。
        TYPES = {"slug": str, "director_zh": str, "director_en": str,
                 "director_slug": str, "title_zh": str, "title_en": str,
                 "year": int, "one_liner": str, "negative": str,
                 "source": str, "visual": dict, "layers": dict, "video": dict,
                 "palette": list, "core": list, "pitfalls": list, "see_also": list,
                 "filmgrab": str, "crew": dict}
        for k, t in TYPES.items():
            if k in f and not isinstance(f[k], t):
                problems.append((where, "字段 %s 类型应为 %s，实际 %s"
                                 % (k, t.__name__, type(f[k]).__name__)))
        for l in LAYERS:
            if not (f.get("layers", {}).get(l) or "").strip():
                problems.append((where, "缺提示词层 %s" % l))
        for d in DIMS:
            if not (f.get("visual", {}).get(d) or "").strip():
                problems.append((where, "缺六维 %s" % d))
        pal = f.get("palette") or []
        if len(pal) != 6:
            problems.append((where, "配色 %d 色（应 6）" % len(pal)))
        for hx, nm in pal:
            if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hx or ""):
                problems.append((where, "非法 hex %r" % hx))
        for s in f.get("see_also") or []:
            # 电影 see_also 指向艺术流派 slug；也允许指另一部片
            if s not in mv_slugs and s not in have and s not in cand:
                problems.append((where, "see_also 里的 %s 不存在（会成为断链）" % s))
        if f.get("source") != "curated":
            problems.append((where, "source 应为 curated"))
        # 未注入 URL 时允许为空，但要显式标出来（合并前必须填）
        if not f.get("filmgrab"):
            problems.append((where, "filmgrab URL 还没注入（合并前必须解析）"))
    return problems


BEGIN = "    # >>> 新增完整片（fv_merge.py 生成，勿手改）BEGIN"
END = "    # <<< 新增完整片 END"


def merge(dry_run=False):
    """把 `fv_new_*.py` 的新片写进 `fv_data.py` 的 FILMS。

    用标记块包裹，**重跑替换而非追加**（幂等）。写前备份 `fv_data.py.bak`。
    返回 (合并数量, 备份路径)。
    """
    import shutil
    path = os.path.join(HERE, "fv_data.py")
    src = open(path, encoding="utf-8").read()
    rows = all_new()

    # 找出 FILMS 的收尾 `]`
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("FILMS = ["))
    close = next(i for i in range(start + 1, len(lines)) if lines[i].rstrip() == "]")

    # 去掉旧的标记块
    head, tail = lines[:start + 1], lines[close:]
    body = []
    skipping = False
    for l in head + []:
        pass
    keep = []
    for l in lines[start + 1:close]:
        if l.strip() == BEGIN.strip():
            skipping = True
            continue
        if l.strip() == END.strip():
            skipping = False
            continue
        if not skipping:
            keep.append(l)

    block = [BEGIN]
    last_dir = None
    for _, f in rows:
        if f["director_zh"] != last_dir:
            block.append("")
            block.append("    # ---------------------------------------------------- %s"
                         % f["director_zh"])
            last_dir = f["director_zh"]
        block.append("    " + json.dumps(f, ensure_ascii=False, indent=4).replace("\n", "\n    ") + ",")
    block.append(END)

    out = lines[:start + 1] + keep + [""] + block + lines[close:]
    new_src = "\n".join(out) + ("\n" if src.endswith("\n") else "")

    backup = path + ".bak"
    if not dry_run:
        if not os.path.exists(backup):
            shutil.copy2(path, backup)          # 只留一份最初的备份，不覆盖
        open(path, "w", encoding="utf-8").write(new_src)
    return len(rows), backup


def main():
    ap = argparse.ArgumentParser(description="校验并合并新片数据")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--merge", action="store_true", help="校验通过后写进 fv_data.py")
    ap.add_argument("--dry-run", action="store_true", help="只显示，不写")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    probs = check()
    n_new = len(all_new())
    import fv_data
    print("新片批次：%d 批 / %d 部；现有 %d 部 → 合计 %d 部"
          % (len(batches()), n_new, len(fv_data.FILMS), n_new + len(fv_data.FILMS)))
    if a.stats:
        import collections
        c = collections.Counter(mod for mod, _ in all_new())
        for k, v in c.items():
            print("  %-12s %d 部" % (k, v))
    if probs:
        # 按问题类型归并打印，便于看出是「全都缺 URL」还是个别问题
        import collections
        grouped = collections.defaultdict(list)
        for where, msg in probs:
            grouped[re.sub(r"（.*?）|%s|\d+" % re.escape("x"), "", msg)].append(where)
        print("\n问题 %d 条：" % len(probs))
        for msg, wheres in sorted(grouped.items(), key=lambda x: -len(x[1])):
            print("  %-46s %d 处  例：%s" % (msg[:46], len(wheres), wheres[0]))
    if not probs:
        print("\n全部校验通过。")
    if a.merge or a.dry_run:
        if probs:
            print("\n有 %d 条问题，**拒绝合并**（先修干净）。" % len(probs))
            return 1
        n, backup = merge(dry_run=a.dry_run)
        if a.dry_run:
            print("\n[dry-run] 会合并 %d 部；未改文件。" % n)
        else:
            print("\n已合并 %d 部进 fv_data.py（备份：%s）" % (n, os.path.basename(backup)))
            print("  下一步：python3 fv_fetch.py --fetch  然后 python3 fv_build.py")
    return 0 if not probs else 1


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 fv_merge.py --check",
          ["校验 fv_new_*.py 里的新片数据（字段、七层、配色、see_also、选片口径）。",
           "  --check  只校验",
           "  --stats  按批次统计张数",
           "",
           "校验通过才把数据合并进 fv_data.FILMS；半成品不混进主数据，",
           "否则会生成没有画廊页链接的空壳卡，而验收查不出来。"])
    sys.exit(main())
