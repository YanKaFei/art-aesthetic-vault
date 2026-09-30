#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
still_build.py —— 把剧照实测结果渲染成 Obsidian 笔记。

产物两份：

    `40-films/<导演>/<电影>-实测.md`  每部片一张「画面实测」页（详细）
    `40-films/_剧照实测总览.md`       14 部片的横向对比（哪部最暗、最饱和…）

两张都只写**数字**，不碰手写的七层与配色。电影卡正文里用 `![[…-实测]]`
嵌入这份实测页，所以你在卡上打开就能看到，不必另找。

## 为什么单开一页而不是塞进电影卡

电影卡是**人写的解读**，实测页是**机器量的数字**。两者的可信度来源不同，
混在一起会让读者分不清哪句是人判断的、哪句是像素算的。分开：
卡上说「这部片用冷蓝紫的阴天外景」，实测页说「蓝紫占 p50 的 23%，
平均明度 65.9」—— 对照着看，谁也不冒充谁。

## 配色为什么并列两套

手写六色是**艺术判断**（「暖金」不只等于一个像素均值）；
实测主色是**像素事实**（全片面积占比最高的六个色）。
两个都对，回答的不是同一个问题。所以并列 + 标差异，**不互相覆盖**。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import still_analysis as SA  # noqa: E402

OUT_DIR = os.path.join(VAULT, "40-films")


def measurement_name(film):
    return "%s-实测" % film["title_zh"]


def _swatch(hexv, label):
    return ('<span style="display:inline-block;width:56px;height:24px;'
            'background:%s;border:1px solid #8888;border-radius:3px;'
            'vertical-align:middle;margin-right:6px"></span> `%s` %s'
            % (hexv, hexv, label))


def _bar(v, vmax, width=22):
    """一个朴素条形图。数字之外给一眼可比的形状。"""
    if v is None or not vmax:
        return ""
    n = int(round(max(0.0, min(1.0, v / vmax)) * width))
    return "█" * n + "·" * (width - n)


def measurement_note(r, film):
    """一部片的「画面实测」页。"""
    ag = r["aggregate"]
    L = []
    A = L.append
    n, total = r["measured"], r["total_linked"]

    A("---")
    A("type: 剧照实测")
    A("电影: %s" % film["title_zh"])
    A("导演: %s" % film["director_zh"])
    A("年份: %d" % film["year"])
    A("已量: %d" % n)
    A("共链接: %d" % total)
    A("标签:")
    A("  - 剧照实测")
    A("  - %s" % film["slug"])
    A("---")
    A("")
    A("# %s · 画面实测" % film["title_zh"])
    A("")
    A("> [!info] 这一页是什么")
    A("> 把这部片在 film-grab 上的剧照**逐张量成数字**，再聚合成全片图景。")
    A("> 与电影卡上的七层/配色**并列阅读**，不是替代 —— 卡上是人写的解读，")
    A("> 这里是像素算出来的事实。")
    A("")

    # ---------------------------------------------------------- 覆盖度
    A("## 一、覆盖度（先看这里）")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 已量 | **%d** 张 |" % n)
    A("| 画廊页链接总数 | **%d** 张 |" % total)
    A("| 本地文件 | %d 个 |" % r["local_files"])
    if r["skipped"]:
        A("| 量不了的 | %d 张（见下） |" % len(r["skipped"]))
    A("")
    if n < total:
        A("> [!warning] 这不是全量")
        A("> 全片均值来自 **已量的 %d 张**，不是全部 %d 张。还差 %d 张没下到本地。"
          % (n, total, total - n))
        A("> 补齐：`python3 .repo/fv_fetch.py --download --per 0`"
          "（已下好的会跳过；站点限流时等一会儿再跑）。")
        A("> **不要把这个均值当成全片结论** —— 样本不对，数字再准也没用。")
        A("")
    else:
        A("> 全部 %d 张都已量到。" % n)
        A("")
    if r["skipped"]:
        A("量不了的：%s" % "、".join("`%s`" % f for f, _ in r["skipped"][:8]))
        A("")
    # 覆盖度之后紧接着回答「那已量的这部分算得准吗」
    st = r.get("stability") or {}
    if st.get("verdict"):
        A("**抽样稳定性**：%s" % st["verdict"])
        A("")
        if st.get("all_mean") is not None:
            A("- 前 %d 张明度均值 %s，全量 %s（差 %+.1f）"
              % (st.get("k"), st["first_quarter_mean"], st["all_mean"],
                 st["delta_luminance"]))
            A("- 饱和度差 %+.3f" % st["delta_saturation"])
        A("")
        A("> %s" % st.get("note", ""))
        A("")

    if not ag:
        A("> 本地还没有这部剧照。先跑 `python3 .repo/fv_fetch.py --download --per 0`。")
        A("")
        A("← [[电影风格总览]] · [[剧照实测总览]]")
        A("")
        return "\n".join(L)

    # ---------------------------------------------------------- 尺寸与画幅
    A("## 二、尺寸与画幅")
    A("")
    A("| 画幅比 | 张数 |")
    A("|---|---|")
    for rt, c in ag["ratios"]:
        tag = {"2.39": "宽银幕 2.39:1", "2.35": "宽银幕 2.35:1",
               "1.85": "学院宽银幕 1.85:1", "1.78": "16:9",
               "1.33": "4:3 学院", "1.37": "学院 1.37:1"}.get("%.2f" % rt, "")
        A("| %s%s | %d |" % (rt, ("（%s）" % tag) if tag else "", c))
    A("")
    A("方向：%s" % "，".join("%s %d 张" % (k, v) for k, v in ag["orientations"]))
    A("")

    # ---------------------------------------------------------- 七维
    A("## 三、七维客观测量（全片）")
    A("")
    A("| 维度 | 均值 | p10 | p50 | p90 | 最小 | 最大 | 分布 |")
    A("|---|---|---|---|---|---|---|---|")
    for key, m in ag["metrics"].items():
        vmax = {"luminance": 255, "contrast": 128, "saturation": 1.0,
                "entropy": 8, "shadow_clip_pct": 100, "highlight_clip_pct": 100,
                "warm_score": 60, "edge_density": 40}.get(key, m["max"] or 1)
        A("| %s | **%s** | %s | %s | %s | %s | %s | `%s` |"
          % (m["zh"], m["mean"], m["p10"], m["p50"], m["p90"], m["min"], m["max"],
             _bar(m["mean"], vmax)))
    A("")
    if ag.get("lowlight"):
        A("> [!warning] %s" % ag["lowlight_note"])
        A(">")
        A("> %s" % "、".join("`%s`（明度 %.1f）" % (x["file"], x["luminance"])
                              for x in ag["lowlight"][:8]))
        A("")
    A("> [!note] 怎么读这几个数")
    A("> · **明度**是 0–255 的均值；p10–p90 说明画面有多「跳」。")
    A("> · **对比**用 RMS；RMS 低但高光/暗部溢出高 = 大面积单调 + 小面积极值。")
    A("> · **暗部溢出 / 高光溢出** 是百分比。暗部溢出高是**有意为之的压暗**"
      "（明暗对照），不一定是曝光失误。")
    A("> · **暖度**为正偏暖、为负偏冷。")
    A("> · 这些是**信号不是结论**。判断风格仍以电影卡上的七层为准。")
    A("")

    # ---------------------------------------------------------- 光影与景别
    A("## 四、影调与景别分布")
    A("")
    A("**明调分布**（按平均明度分档）")
    A("")
    A("| 档次 | 张数 |")
    A("|---|---|")
    for k, v in ag["keys"]:
        A("| %s | %d |" % (k, v))
    A("")
    A("**色温分布**")
    A("")
    A("| 色温 | 张数 |")
    A("|---|---|")
    for k, v in ag["temperatures"]:
        A("| %s | %d |" % (k, v))
    A("")
    A("**景别分布**（人脸尺寸）")
    A("")
    A("| 景别 | 张数 |")
    A("|---|---|")
    for k, v in ag["framing"]:
        A("| %s | %d |" % (k, v))
    A("")
    A("> %s" % ag["framing_note"])
    A("")

    # ---------------------------------------------------------- 构图
    A("## 五、构图与线条")
    A("")
    A("**色彩和谐结构**（哪几组色相对峙）")
    A("")
    A("| 结构 | 张数 |")
    A("|---|---|")
    for k, v in ag["harmonies"][:8]:
        A("| %s | %d |" % (k, v))
    A("")
    A("**线条主导方向**")
    A("")
    A("| 方向 | 张数 |")
    A("|---|---|")
    from collections import Counter
    lo = Counter(s.get("line_orientation") or "—" for s in r["stills"])
    for k, v in sorted(lo.items(), key=lambda x: (-x[1], x[0])):
        A("| %s | %d |" % (k, v))
    A("")
    A("**对称性**（中心能量相对整体的权重，1.0 = 不偏不倚）")
    A("")
    A("| 提示 | 张数 |")
    A("|---|---|")
    sym = Counter(s.get("symmetry_hint") or "—" for s in r["stills"])
    for k, v in sorted(sym.items(), key=lambda x: (-x[1], x[0])):
        A("| %s | %d |" % (k, v))
    A("")

    # ---------------------------------------------------------- 配色比对
    A("## 六、配色：手写 vs 实测")
    A("")
    A("**手写配色**（电影卡上的六色，艺术判断）")
    A("")
    for hx, name in r.get("palette_written_named") or []:
        A(_swatch(hx, name))
        A("")
    A("**实测主色**（全片剧照里面积占比最高的六色，像素事实）")
    A("")
    for hx, pct in r["palette_measured"]:
        A(_swatch(hx, "占画面 %.1f%%" % pct))
        A("")
    pd = r["palette_diff"]
    A("**比对结果：%s**（平均 Lab 距离 %s）" % (pd["verdict"], pd.get("距离")))
    A("")
    if pd.get("pairs"):
        A("| 手写色 | 最接近的实测色 | Lab 距离 |")
        A("|---|---|---|")
        for p in pd["pairs"]:
            A("| `%s` | `%s` | %.1f |" % (p["written"], p["nearest_measured"],
                                          p["distance"]))
        A("")
    A("> [!important] 差异只标注，不覆盖")
    A("> 库的规矩是**数字是信号不是结论**：实测一张油画的土色系会被配色匹配")
    A("> 误判成「现实主义」，而它其实毫不相干。所以这里**不会**自动改写卡上")
    A("> 手写的六色 —— 两个都对，回答的不是同一个问题：")
    A("> 手写色是『这部片的色彩性格』，实测色是『像素面积占比』。")
    A("> 距离偏大时值得回看两边，但改不改由你决定。")
    A("")

    # ---------------------------------------------------------- 代表帧
    A("## 七、代表帧（k-medoids）")
    A("")
    A("> 从全片已量的 %d 张里挑出**最能代表整体**的 %d 张。"
      % (n, len(r["representative"])))
    A("> 用 k-medoids 而不是 k-means：中心必须是**真实存在的一张画面**，")
    A("> 不能是算出来的平均向量。选择是确定性的，同输入两次跑结果一致。")
    A("")
    A("| # | 文件 | 明度 | 饱和度 | 色温 | 影调 | 景别 |")
    A("|---|---|---|---|---|---|---|")
    for x in r["representative"]:
        A("| %02d | `%s` | %s | %s | %s | %s | %s |"
          % (x["index"], x["file"], x["luminance"], x["saturation"],
             x["temperature"], x["key"], x["framing"]))
    A("")
    A("本地路径：`99-attachments/images-films/%s/`（已 gitignore，"
      "纯个人研究参考，不随仓库分发）" % film["slug"])
    A("")

    # ---------------------------------------------------------- 出处
    A("## 八、出处")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 剧照来源 | [film-grab 画廊页](%s) |" % film["filmgrab"])
    A("| 版权 | 属原片方。**只索引外链，不转载**；本地副本仅个人研究 |")
    A("| 测量方法 | `image_analysis.py` 七维 + 人脸/霍夫直线/显著性 |")
    A("| 代表帧算法 | k-medoids（色相-饱和度直方图特征） |")
    A("| 重建 | `python3 .repo/still_analysis.py --slug %s` |" % film["slug"])
    A("")
    A("---")
    A("")
    A("← [[%s]] · [[剧照实测总览]]　|　延伸阅读 [[提示词拆解方法]]"
      % film["title_zh"])
    A("")
    return "\n".join(L)


def overview_note(results, films_by_slug):
    """14 部片的横向对比。"""
    L = ["---", "type: 总览", "标签:", "  - 总览", "  - 剧照实测", "---", "",
         "# 剧照实测总览", "",
         "> [!info] 这一页是什么",
         "> 把 14 部片的剧照逐张量成数字后的**横向对比**。",
         "> 每部片的详细实测见其电影卡内嵌的「-实测」页。", "",
         "| 导演 | 电影 | 覆盖 | 明度 | 对比 | 饱和度 | 暖度 | 暗部溢出 | 主色 |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        ag = r["aggregate"]
        f = films_by_slug.get(r["slug"], {})
        if not ag:
            L.append("| %s | %s | 未测量 | — | — | — | — | — | — |"
                     % (r["director_zh"], r["title_zh"]))
            continue
        m = ag["metrics"]
        cov = "%d/%d" % (r["measured"], r["total_linked"])
        top = "、".join("`%s`" % h for h, _ in r["palette_measured"][:3])
        L.append("| %s | [[%s]] | %s | %s | %s | %s | %s | %s | %s |"
                 % (r["director_zh"], r["title_zh"], cov,
                    m.get("luminance", {}).get("mean", "—"),
                    m.get("contrast", {}).get("mean", "—"),
                    m.get("saturation", {}).get("mean", "—"),
                    m.get("warm_score", {}).get("mean", "—"),
                    m.get("shadow_clip_pct", {}).get("mean", "—"), top))
    L += ["", "> [!warning] 覆盖度不一样，别直接横比",
          "> 上表「覆盖」列是 `已量/共链接`。还没下齐的片子，其均值只代表**已量的那部分**，",
          "> 与下齐的片子横向比较是不成立的。补齐后重跑这一页即可。", "",
          "## 怎么读这张表", "",
          "- **明度**低 = 整体压暗；**暗部溢出**高配合低明度 = 有意为之的深压暗调",
          "- **饱和度**低而**对比**高 = 硬光高反差的路线",
          "- **暖度**为负 = 冷调；这部库里的冷调片（银翼杀手 2049、七宗罪）尤其明显",
          "", "## 重建", "",
          "```bash",
          "python3 .repo/fv_fetch.py --download --per 0   # 把剧照下全（限流时等一会儿再跑）",
          "python3 .repo/still_analysis.py               # 逐张测量（有缓存，增量跑）",
          "python3 .repo/still_build.py                  # 生成实测页",
          "python3 .repo/tests/still_test.py             # 本模块测试",
          "```", "",
          "← [[电影风格总览]] · [[流派总览]]", ""]
    return "\n".join(L)


def sweep():
    """清掉上次生成留下的「-实测.md」。"""
    import glob
    killed = 0
    for p in glob.glob(os.path.join(OUT_DIR, "**", "*-实测.md"), recursive=True):
        try:
            os.remove(p)
            killed += 1
        except OSError:
            pass
    return killed


def build(slugs=None):
    import fv_core
    sweep()
    films = fv_core.films()
    if slugs:
        films = [f for f in films if f["slug"] in slugs]
    results, by_slug, n = [], {}, 0
    for f in films:
        r = SA.analyse_film(f, use_cache=True)
        results.append(r)
        by_slug[f["slug"]] = f
        sub = os.path.join(OUT_DIR, f["director_slug"])
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "%s.md" % measurement_name(f)), "w",
                  encoding="utf-8") as fh:
            fh.write(measurement_note(r, f))
        n += 1
    if not slugs:
        with open(os.path.join(OUT_DIR, "剧照实测总览.md"), "w", encoding="utf-8") as fh:
            fh.write(overview_note(results, by_slug))
        n += 1
    return n, results


def main():
    import argparse
    ap = argparse.ArgumentParser(description="生成剧照实测页")
    ap.add_argument("--slug", help="只生成某一部片")
    a = ap.parse_args()
    n, results = build([a.slug] if a.slug else None)
    print("已生成 %d 个文件 → %s" % (n, OUT_DIR))
    done = sum(1 for r in results if r["measured"] >= r["total_linked"])
    print("  覆盖情况：%d/%d 部片已下齐，共量到 %d 张"
          % (done, len(results), sum(r["measured"] for r in results)))
    for r in results:
        if r["measured"] < r["total_linked"]:
            print("    · %-38s 已量 %d/%d"
                  % (r["slug"], r["measured"], r["total_linked"]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 still_build.py",
          ["把剧照实测结果生成成 Obsidian 笔记。",
           "  --slug SLUG   只生成某一部片",
           "",
           "产物：40-films/<导演>/<电影>-实测.md + _剧照实测总览.md。",
           "数据来自 still_analysis.py（有缓存，增量跑）。"])
    sys.exit(main())
