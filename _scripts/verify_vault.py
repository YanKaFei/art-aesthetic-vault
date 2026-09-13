#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_vault.py —— 抓完/改完之后的验收检查。

一个参考库最怕的不是图少，是**图错**：错的参考会污染你的提示词直觉，
而且你自己不会发现。所以每次抓取或重建之后，固定跑这一遍。

用法：
    python3 verify_vault.py            # 跑全部检查
    python3 verify_vault.py --quick    # 跳过第 5 项（近重复），其余七项照跑

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
    9 笔记双链   每个 [[...]] 都能解析到一篇笔记（含表格转义处理）
   10 署名质量   卡片上没有「上传者当画家」「机器语法当日期」
   11 视频层     每张卡都有 Seedance 五段式 + H3 自然语言两块中文提示词
   12 新鲜度     生成脚本没比笔记新（否则说明上次重建失败，笔记是旧的）
   13 本地图库   层 2 的清单 / 图片 / 笔记三者一致（没有本地图库时自动跳过）
   14 板子反推   Pinterest 每个板子笔记里，每张图下面都有提示词与视频分析

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

NOTE_DIRS = ("00-导航", "10-流派", "15-我的图库", "20-我的提示词", "90-模板")
# 图片有两个根：权威层的 99-附件/images/ 和用户自己的 99-附件/images-local/。
# 断链与孤儿图两项都要同时认这两个根，否则本地图库的嵌入会被误报成断链。
IMAGE_ROOTS = ("99-附件/images", "99-附件/images-local")
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
    for root in IMAGE_ROOTS:
        for p in glob.glob(os.path.join(VAULT, root, "**", "*"), recursive=True):
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
    for root in IMAGE_ROOTS:
        for p in glob.glob(os.path.join(VAULT, root, "**", "*"), recursive=True):
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
        if base.startswith(("inbox", "vision", "local_")):
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
        if base.startswith(("inbox", "vision", "local_")):
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
    for root in IMAGE_ROOTS:
        for p in glob.glob(os.path.join(VAULT, root, "**", "*"), recursive=True):
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
        if base.startswith(("inbox", "vision", "feature", "clip", "local_")):
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


def check_note_links():
    """9 笔记双链：每个 [[...]] 都能解析到一篇笔记。

    这一项一直缺 —— 原来的断链检查只覆盖 `![[图片]]` 嵌入，
    不覆盖 `[[笔记]]` 双链。

    **必须正确处理表格里的转义 `\|`。** Markdown 表格中不转义的 `|`
    会破坏单元格，所以 Obsidian 规定表格内的别名写法就是
    `[[笔记\|别名]]`（见官方文档 “Vertical bars in tables”）。
    最初没处理这个转义，把 12 条**完全合法**的链接报成了断链 ——
    检查器自己的 bug，不是库的 bug。
    """
    notes = set()
    for d in NOTE_DIRS:
        for p in glob.glob(os.path.join(VAULT, d, "**", "*.md"), recursive=True):
            notes.add(os.path.splitext(os.path.basename(p))[0])
    unresolved = []
    for md in _notes():
        try:
            t = open(md, encoding="utf-8").read()
        except Exception:
            continue
        t = re.sub(r"```.*?```", "", t, flags=re.S)      # 去掉代码块里的示例
        t = t.replace("\\|", "|")                        # 还原表格转义
        for m in re.findall(r"(?<!!)\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", t):
            name = m.strip()
            if name and name not in notes:
                unresolved.append((os.path.relpath(md, VAULT), name))
    return unresolved


def check_attribution():
    """10 署名质量：卡片上不能出现「上传者当画家」「机器语法当日期」。

    实测过的脏值形态（都真实出现在卡片上过）：
      **Daderot · 2016-12-01 15:50:04 · John the Baptist, Crete…**   上传者当画家
      **Gary Todd from Xinzheng, China · 2012-07-06 05:32 · …**     同上
      **song dynasty · 13th century**                               时期标签当画家
      date QS:P571,+1650-00-00T00:00:00Z/7                          Wikidata 机器语法
      title QS:P1476,en:"The Pink Candle"                           同上（出现在材质里）
      Designed by William Morris, British                           编目口癖
    一个标着「公共领域、可自由使用」的参考库出现这些，比图少更伤可信度。
    """
    import re as _re
    sus = _re.compile(
        r"(QS:|daderot|gary todd|cbl62|gryffindor|hiart|christies|sotheby|bonhams|"
        r"rijksmuseum|library of congress|descouens|egorova|lupercio|martínez rosado|"
        r"digital id|unknown author|from xinzheng|designed by|uploaded by|"
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})", _re.I)
    hits = []
    for md in _notes(skip_templates=False):
        try:
            t = open(md, encoding="utf-8").read()
        except Exception:
            continue
        for m in _re.findall(r"\*\*([^*]+)\*\*", t):
            if sus.search(m):
                hits.append((os.path.relpath(md, VAULT), m.strip()[:60]))
    return hits


def check_video_layer():
    """11 视频层：每张流派卡都要有可粘贴的中文视频提示词两块。

    需要的两块（格式要求不同，缺一块就有半个模型用不了）：
      A. Seedance 2.5 五段式 —— 必须含【主体】【风格】【时间线】【BGM】【限制】
      B. MiniMax H3 自然语言 —— 不许出现 [Shot N] / 时间戳（会和 Context-IR 打架）
    """
    problems = []
    for md in glob.glob(os.path.join(VAULT, "10-流派", "*.md")):
        try:
            t = open(md, encoding="utf-8").read()
        except Exception:
            continue
        name = os.path.basename(md)
        if "## 五、AI 视频层" not in t:
            problems.append((name, "缺『五、AI 视频层』"))
            continue
        seg = t.split("## 五、AI 视频层", 1)[1].split("## 六、", 1)[0]
        for tag in ("【主体】", "【风格】", "【时间线】", "【BGM】", "【限制】"):
            if tag not in seg:
                problems.append((name, "Seedance 五段式缺 " + tag))
        if "### B. MiniMax H3" not in seg and "### B. MiniMax H3" not in t:
            problems.append((name, "缺 H3 自然语言块"))
        # H3 块里不该出现结构化字段名/时间戳
        if "### B. MiniMax H3" in seg:
            h3 = seg.split("### B. MiniMax H3", 1)[1]
            h3 = h3.split("```")[1] if "```" in h3 else h3
            for bad in ("[Shot ", "integrated_multimodal_description",
                        "overall_soundscape", "non_diegetic_music"):
                if bad in h3:
                    problems.append((name, "H3 块混进了结构化字段 " + bad))
    return problems


def check_generated_freshness():
    """12 生成物新鲜度：生成脚本比笔记新 → 上次重建失败或没重建。

    这是今天踩了两次的坑：`build_vault.py` 报错退出（exit 1）时，
    **10-流派/ 下的笔记还是上一次成功构建的旧文件**，于是所有检查照常通过 ——
    验收全绿，但内容是旧的。只查「笔记里的东西对不对」看不出这个问题，
    必须比对**时间**。
    """
    srcs = [os.path.join(HERE, "build_vault.py"), os.path.join(HERE, "movements.py"),
            os.path.join(HERE, "video_prompt.py"), os.path.join(HERE, "providers.py")]
    srcs += glob.glob(os.path.join(HERE, "mv_*.py"))
    srcs = [p for p in srcs if os.path.exists(p)]
    if not srcs:
        return None
    newest = max(os.path.getmtime(p) for p in srcs)
    newest_name = os.path.basename(max(srcs, key=os.path.getmtime))

    stale = []
    for d in ("10-流派", "00-导航"):
        for p in glob.glob(os.path.join(VAULT, d, "*.md")):
            if os.path.getmtime(p) < newest - 1:      # 容 1 秒误差
                stale.append((os.path.relpath(p, VAULT), "比 " + newest_name + " 旧"))
    return stale


def check_local_library():
    """13 本地图库：层 2 的清单、图片、笔记三者要一致。

    只在用户本机有本地图库时才有意义 —— 没有清单就直接通过（别人 clone 后就是这种）。
    三件事要同时成立：
      · 清单里每条记录对应的图片文件都在
      · images-local/ 下的每张图都在清单里（否则是孤儿）
      · 流派卡里的 [[我的图库-X]] 链接都有对应笔记（否则是悬空链接）
    """
    man_path = os.path.join(DATA, "local_library.json")
    if not os.path.exists(man_path):
        return []
    try:
        man = json.load(open(man_path, encoding="utf-8"))
    except Exception:
        return [("local_library.json", "解析失败")]
    items = man.get("items") or {}
    problems = []
    for rel, it in items.items():
        if not os.path.exists(os.path.join(VAULT, rel)):
            problems.append((rel, "清单里有但文件不在"))
    root = os.path.join(VAULT, "99-附件", "images-local")
    if os.path.isdir(root):
        for r, _d, fs in os.walk(root):
            for f in fs:
                if f.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(r, f), VAULT).replace(os.sep, "/")
                if rel not in items:
                    problems.append((rel, "图片在但清单里没有"))
    # 流派卡引用的本地笔记必须存在
    notes = {os.path.splitext(os.path.basename(x))[0]
             for x in glob.glob(os.path.join(VAULT, "15-我的图库", "*.md"))}
    for md in _notes():
        try:
            t = open(md, encoding="utf-8").read()
        except Exception:
            continue
        for m in re.findall(r"\[\[我的图库-([^\]|]+)", t):
            if ("我的图库-" + m) not in notes:
                problems.append((os.path.relpath(md, VAULT), "链接了不存在的 我的图库-" + m))
    return problems


def check_board_analysis():
    """14 Pinterest 板子：每张图下面都要有反推（提示词 + 视频分析）。

    实测踩过：抓取脚本原来只写图片和原图直链，212 张图下面**什么都没有** ——
    而用户在库里看到这些图时，期待的是「图下面有提示词分析和视频分析」。
    抓取和分析是两件事（一个要联网、一个是纯本地计算），
    分开之后很容易只做前一半，所以这里固定查一次。
    """
    problems = []
    for p in sorted(glob.glob(os.path.join(VAULT, "20-我的提示词", "Pinterest-*.md"))):
        name = os.path.basename(p)
        if name == "Pinterest.md":
            continue                       # 汇总页，不含单图
        try:
            t = open(p, encoding="utf-8").read()
        except Exception:
            continue
        n_img = t.count("[原图直链]")
        n_prompt = t.count("**提示词**（按")
        n_video = t.count("视频 · Seedance")
        if n_img and n_prompt < n_img:
            problems.append((name, "%d 张图只有 %d 个提示词块" % (n_img, n_prompt)))
        if n_img and n_video < n_img:
            problems.append((name, "%d 张图只有 %d 个视频块" % (n_img, n_video)))
    return problems


def main():
    ap = argparse.ArgumentParser(description="艺术审美风格库验收检查")
    ap.add_argument("--quick", action="store_true",
                    help="跳过第 5 项（近重复，需要 CLIP/Vision 索引），其余七项照跑")
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
    report("9 笔记双链", check_note_links())
    report("10 署名质量", check_attribution())
    report("11 视频层", check_video_layer())
    report("12 生成物新鲜度", check_generated_freshness())
    report("13 本地图库", check_local_library())
    report("14 板子反推", check_board_analysis())

    print("=" * 70)
    if failed:
        print("未通过：%s" % "、".join(failed))
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
