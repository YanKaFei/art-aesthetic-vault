#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_vault.py —— 抓完/改完之后的验收检查。

一个参考库最怕的不是图少，是**图错**：错的参考会污染你的提示词直觉，
而且你自己不会发现。所以每次抓取或重建之后，固定跑这一遍。

用法：
    python3 verify_vault.py            # 跑全部检查
    python3 verify_vault.py --quick    # 只跑不需要索引的前四项

检查项
    1 断链       每个 ![[...]] 都能在 99-附件/images/ 下找到文件
    2 重名       全库 basename 唯一（Obsidian 的 ![[名]] 按 basename 解析，
                 重名会让嵌入指向错误的那张）
    3 AI 图      全库 0 命中（用模型的输出当模型的参考是致命的）
    4 frontmatter 每个笔记的 frontmatter 都是合法 YAML，且无 HTML 注释
    5 近重复     跨流派完全相同的图（需要先建 Vision 索引，仅 macOS）
    6 授权       每条作品记录都有 license 字段（来源合法是发布的前提）
    7 孤儿图     磁盘上存在但没有被任何笔记引用的图
    8 JSON↔磁盘  每个流派的抓取记录与磁盘上的图是否一一对应

退出码：0 全部通过；1 有问题（便于写进 CI 或 pre-commit）。
"""

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
IMAGES = os.path.join(VAULT, "99-附件", "images")
DATA = os.path.join(HERE, "_data")

NOTE_DIRS = ("00-导航", "10-流派", "20-我的提示词", "90-模板")
# 模板目录里是给用户抄的骨架，本来就带占位符（如 `![[此处放图]]`），
# 检查断链时要跳过，否则每次都会报一个假问题。
TEMPLATE_DIR = "90-模板"
EMBED = re.compile(r"!\[\[([^\]|#]+)")
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff")

OK, BAD, WARN = "  ✓", "  ✗", "  ·"


def _notes(skip_templates=False):
    for d in NOTE_DIRS:
        if skip_templates and d == TEMPLATE_DIR:
            continue
        for p in sorted(glob.glob(os.path.join(VAULT, d, "**", "*.md"), recursive=True)):
            yield p


def check_links():
    """1 断链。只看像文件名的嵌入（带图片扩展名），占位符不算。"""
    have = set()
    for p in glob.glob(os.path.join(IMAGES, "**", "*"), recursive=True):
        if os.path.isfile(p) and not os.path.basename(p).startswith("."):
            have.add(os.path.basename(p))
    missing = []
    for md in _notes(skip_templates=True):
        try:
            txt = open(md, encoding="utf-8").read()
        except Exception:
            continue
        for m in EMBED.findall(txt):
            name = m.strip()
            if not name.lower().endswith(IMG_EXT):
                continue                # 占位符 / 非图片嵌入，不算断链
            if name not in have:
                missing.append((os.path.relpath(md, VAULT), name))
    return missing


def check_duplicate_names():
    """2 重名。"""
    names = []
    for p in glob.glob(os.path.join(IMAGES, "**", "*"), recursive=True):
        if os.path.isfile(p) and not os.path.basename(p).startswith("."):
            names.append(os.path.basename(p))
    return [k for k, v in Counter(names).items() if v > 1]


def check_ai():
    """3 AI 生成图残留。"""
    sys.path.insert(0, HERE)
    try:
        from providers import is_ai_generated
    except Exception:
        return None                     # 无法判断，返回 None 让调用方显示「跳过」
    hits = []
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        base = os.path.basename(p)
        if base.startswith("inbox") or base.startswith("vision"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else (d.get("items") or d.get("works") or [])
        if isinstance(items, dict):
            items = [v for v in items.values() if isinstance(v, dict)]
        for w in items:
            if isinstance(w, dict) and is_ai_generated(w):
                hits.append((base, str(w.get("title"))[:50]))
    return hits


def check_frontmatter():
    """4 frontmatter 合法性。

    两个真实踩过的坑：
      - frontmatter 里放 HTML 注释（`<!-- -->`）不是合法 YAML
      - 生成模板里用 str.format() 会让 JSON 示例的花括号炸掉
    """
    bad = []
    for md in _notes():
        try:
            lines = open(md, encoding="utf-8").read().split("\n")
        except Exception:
            continue
        if not lines or lines[0].strip() != "---":
            bad.append((os.path.relpath(md, VAULT), "缺少 frontmatter"))
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            bad.append((os.path.relpath(md, VAULT), "frontmatter 未闭合"))
            continue
        for i, ln in enumerate(lines[1:end], start=2):
            if ln.lstrip().startswith("<"):
                bad.append((os.path.relpath(md, VAULT), "第 %d 行以 < 开头（非法）" % i))
            if "\t" in ln:
                bad.append((os.path.relpath(md, VAULT), "第 %d 行含制表符（YAML 不允许）" % i))
    return bad


def check_duplicates_visual(thresh=0.08):
    """5 近重复。需要 vision 索引，没有就跳过。"""
    idx_path = os.path.join(DATA, "vision_index.json")
    if not os.path.exists(idx_path):
        return None
    try:
        sys.path.insert(0, HERE)
        import artvault_vision as V
        idx = json.load(open(idx_path, encoding="utf-8"))
        vecs = idx.get("vectors") or {}
    except Exception:
        return None
    if not vecs:
        return None
    items = sorted(vecs.items())
    use_np = V._have_numpy()
    pairs = []
    for i in range(len(items)):
        ri, vi = items[i]
        for j in range(i + 1, len(items)):
            rj, vj = items[j]
            if len(vi) != len(vj):
                continue
            d = V._dist_np(vi, vj) if use_np else V._dist(vi, vj)
            if d < thresh:
                pairs.append((d, V.slug_of(ri), V.slug_of(rj), ri, rj))
    pairs.sort()
    return pairs


def check_license():
    """6 授权字段。发布的前提是每件作品都能说清来源与授权。"""
    missing = []
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        base = os.path.basename(p)
        if base.startswith("inbox") or base.startswith("vision"):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else (d.get("items") or d.get("works") or [])
        if isinstance(items, dict):
            items = [v for v in items.values() if isinstance(v, dict)]
        for w in items:
            if not isinstance(w, dict):
                continue
            if not w.get("license"):
                missing.append((base, str(w.get("title"))[:46]))
    return missing


def check_orphans():
    """7 孤儿图：在磁盘上但没有任何笔记引用。"""
    referenced = set()
    for md in _notes():
        try:
            referenced.update(m.strip() for m in EMBED.findall(open(md, encoding="utf-8").read()))
        except Exception:
            continue
    orphans = []
    for p in glob.glob(os.path.join(IMAGES, "**", "*"), recursive=True):
        if not os.path.isfile(p) or os.path.basename(p).startswith("."):
            continue
        if os.path.basename(p) not in referenced:
            orphans.append(os.path.relpath(p, VAULT))
    return sorted(orphans)


def check_data_disk_sync():
    """8 JSON ↔ 磁盘一致性。这是最直接的一项，能在重建笔记之前就发现问题。

    每个流派的 `_data/<slug>.json` 是抓取结果，磁盘上的图是它的落地。
    两者必须一一对应。实测真的会脱节：第一轮抓取处理 tonalism 时
    **下载完图片但在写 JSON 之前中断了**，结果 JSON 还是前一天的 6 条旧记录，
    磁盘上是 1 张旧图 + 2 张新图。

    这种状态很隐蔽：笔记是按 JSON 生成的，所以笔记引用 5 个不存在的文件，
    同时磁盘上有 2 张没人引用的孤儿图。要等下一次重建 + 验收才暴露。
    这一项直接比对两者，不用等。
    """
    problems = []
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        base = os.path.basename(p)
        if base.startswith(("inbox", "vision", "feature", "clip")):
            continue
        slug = base[:-5]
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        items = d if isinstance(d, list) else (d.get("items") or d.get("works") or [])
        if isinstance(items, dict):
            items = [v for v in items.values() if isinstance(v, dict)]

        recorded = set()
        for w in items:
            if not isinstance(w, dict) or not w.get("local_image"):
                continue
            name = os.path.basename(w["local_image"])
            recorded.add(name)
            if not os.path.exists(os.path.join(VAULT, w["local_image"])):
                problems.append(("JSON 有记录但磁盘缺文件", slug, name))

        folder = os.path.join(IMAGES, slug)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.startswith("."):
                    continue
                if f not in recorded:
                    problems.append(("磁盘有文件但 JSON 无记录", slug, f))
    return problems


def main():
    ap = argparse.ArgumentParser(description="艺术审美风格库验收检查")
    ap.add_argument("--quick", action="store_true",
                    help="只跑不需要 Vision 索引的前四项")
    ap.add_argument("--max-list", type=int, default=8, help="每项最多列几条明细")
    a = ap.parse_args()

    if not os.path.isdir(VAULT):
        print("找不到仓库根目录"); return 1
    print("仓库：%s" % VAULT)
    print("=" * 70)

    failed = []

    def report(name, result, empty_msg="通过"):
        if result is None:
            print("%s %s：跳过（依赖不可用）" % (WARN, name)); return
        if not result:
            print("%s %s：%s" % (OK, name, empty_msg)); return
        failed.append(name)
        print("%s %s：%d 处问题" % (BAD, name, len(result)))
        for row in result[:a.max_list]:
            print("      %s" % (row if isinstance(row, str) else "  ".join(str(x) for x in row),))
        if len(result) > a.max_list:
            print("      … 另有 %d 处" % (len(result) - a.max_list))

    report("1 断链", check_links())
    report("2 重名", check_duplicate_names())
    report("3 AI 生成图", check_ai())
    report("4 frontmatter", check_frontmatter())

    if not a.quick:
        pairs = check_duplicates_visual()
        if pairs is None:
            print("%s 5 近重复：跳过（先跑 artvault_vision.py build，且仅 macOS）" % WARN)
        else:
            cross = [p for p in pairs if p[1] != p[2]]
            print("%s 5 近重复：%d 对完全相同（阈值 0.08），其中跨流派 %d 对"
                  % (OK if not pairs else WARN, len(pairs), len(cross)))
            for d, s1, s2, r1, r2 in pairs[:a.max_list]:
                tag = "跨流派" if s1 != s2 else "同流派"
                print("      %.3f  [%s] %s" % (d, tag, r1))
                print("             %s" % r2)
            if cross:
                print("      · 跨流派重复**大多合理**（一件作品可以同时是多个流派的例证），")
                print("        要判断的是：重叠说得通就保留；该流派真正该有的作品一张都没有 → 改关键词")

    report("6 授权字段", check_license())
    report("7 孤儿图", check_orphans())
    report("8 JSON↔磁盘", check_data_disk_sync())

    print("=" * 70)
    if failed:
        print("未通过：%s" % "、".join(failed))
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
