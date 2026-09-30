#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shot_build.py —— 把镜头配方卡生成成 Obsidian 笔记：45-shots/<类别>/<name>.md

## 生成物长什么样、为什么和另外两条轴不同

    `10-movements/` 与 `40-films/` 的卡都是**九个小节 + 七层提示词**，
    因为那两条轴问的是「长什么样」，七层正好回答它。

    `45-shots/` 的卡**不套那个模板**。它回答的是「这一下怎么做出来」，
    所以照上游的四字段 + 五段来排：适用 / 时长 / 能量 / 标签，加
    意图 / 动效核心 / 参数表 / 已知坑 / 参考实现。

**这不是不统一，是不假装统一。** 上游 157 张卡里一张都没有色彩或光照
字段；硬套七层只能靠编。宁可第三个模板，也不要一张看起来能用、
实际在编的卡。

## 许可（Apache-2.0）

每张卡都带上游仓库、commit 与原始路径。卡片上写清「本卡来自上游，
本站只做归类与排版」。出处页另转述上游 `ATTRIBUTION.md` 的边界说明：
动效手法研究自公开作品，但**实现全部从零重写**、不含任何原片素材，
且**公开发布不等于授权**。
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import shot_core  # noqa: E402

OUT_DIR = shot_core.OUT_DIR


def _yq(s):
    s = str(s)
    if s == "" or any(c in s for c in ":#[]{}&*!|>'\"%@`,") or s[0] in "-? ":
        return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')
    return s


def card_note(s):
    """一张镜头配方卡的完整正文。"""
    L = []
    A = L.append
    zh = shot_core.CATEGORY_ZH.get(s["category"], s["category"])

    A("---")
    A("type: 镜头卡")
    A("招式: %s" % _yq(s["name"]))
    A("类别: %s" % zh)
    A("类别slug: %s" % s["category"])
    if s.get("energy"):
        A("能量: %s" % _yq(s["energy"]))
    A("上游: %s" % s["source_repo"])
    A("上游路径: %s" % s["source_path"])
    A("上游commit: %s" % s["source_commit"][:12])
    A("许可: %s" % s["license"])
    A("标签:")
    A("  - 镜头")
    A("  - %s" % s["name"])
    A("---")
    A("")
    A("# %s" % s["name"])
    A("")
    A("> [!abstract] 这一下是什么")
    A("> %s" % s["one_liner"])
    A("")
    A("| 类别 | 适用 | 时长 | 能量 |")
    A("|---|---|---|---|")
    A("| [[%s\\|%s]] | %s | %s | %s |"
      % ("镜头总览", zh, s["purpose"] or "—", s["duration"] or "—", s["energy"] or "—"))
    A("")
    A("> [!info] 这张卡不是本库原创")
    A("> 来自 [%s](%s)（%s），原始路径 `%s`，commit `%s`。"
      % (s["source_repo"], s["source_url"], s["license"],
         s["source_path"], s["source_commit"][:12]))
    A("> 本库只做了归类与排版，**没有改动技法描述**。")
    A("")
    A("---")
    A("")

    # 五段：按上游原段名与原顺序排。**变体段名保留原样**
    # （「两式选型」「单式选型」和「动效核心」是同一段的不同说法，
    #  读者要看到的是上游写的那个名字）。
    for sec in s["sections"]:
        A("## %s" % sec["title"])
        A("")
        A(sec["body"])
        A("")

    # 出处
    A("## 上游出处")
    A("")
    A("| 项 | 值 |")
    A("|---|---|")
    A("| 仓库 | [%s](%s) |" % (s["source_repo"], s["source_url"]))
    A("| 原始路径 | `%s` |" % s["source_path"])
    A("| commit | `%s` |" % s["source_commit"])
    A("| 许可 | %s |" % s["license"])
    A("| 参考实现 | `%s` |" % (s["reference"].splitlines()[0] if s["reference"] else "—"))
    A("")
    # 双链按**文件名**解析（verify_vault 第 9 项与 Obsidian 都是）。
    # 写路径式 `[[45-shots/出处与许可]]` 会成断链 —— 实测 158 条一起红。
    A("> [!warning] 用之前先看 [[出处与许可]]")
    A("> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，"
      "不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。")
    A("")
    A("---")
    A("")
    A("← [[镜头总览]] · [[电影风格总览]]　|　类别：[[%s\\|%s]]"
      % ("镜头总览", zh))
    A("")
    return "\n".join(L)


def overview_note():
    """45-shots/镜头总览.md"""
    st = shot_core.stats()
    L = ["---", "type: 总览", "标签:", "  - 总览", "  - 镜头", "---", "",
         "# 镜头总览（镜头配方卡）", "",
         "> [!info] 这是什么",
         "> **第三条并列的轴**，和另外两条各管一段：",
         ">",
         "> | 模块 | 轴 | 回答的问题 |",
         "> |---|---|---|",
         "> | `10-movements/` | 风格 | 这个流派长什么样、提示词怎么拼 |",
         "> | `40-films/` | 导演-电影 | 这部片长什么样、怎么模仿它 |",
         "> | `45-shots/` | **运镜招式** | **这一下动效怎么做出来** |",
         "",
         "**共 %d 张 / %d 类**，来自 [%s](%s)（%s）。"
         % (st["shots"], st["categories"], st["source"], 
            shot_core.shots()[0]["source_url"] if shot_core.shots() else "",
            st["license"]),
         "",
         "> [!important] 为什么这一轴**没有七层**",
         "> 前两条轴共用七层（风格/光照/色彩/构图/媒介/情绪/镜头），所以能混搭。",
         "> 这一轴的卡讲的是帧数、缓动、幅度（`zoom 6f ease-in，1→2.6`、"
         "`震屏 14px·e^(−t/1.8)`），",
         "> **157 张里没有一张有色彩或光照字段**。给它套七层只能靠编。",
         "> 所以它按上游自己的四字段（适用/时长/能量/标签）排 —— 不假装统一。",
         "",
         "## 怎么用（命令行 / MCP）", "",
         "```bash",
         "python3 .repo/artvault.py shots list              # 全部 157 张",
         "python3 .repo/artvault.py shots categories        # 10 类",
         'python3 .repo/artvault.py shots search "急推 冲击"  # 按「我想做什么」找',
         "python3 .repo/artvault.py shots show crash-zoom-punch",
         "```", "",
         "MCP 侧两个工具：`search_shots` / `get_shot`。", "",
         "## 和电影卡怎么接", "",
         "`40-films/` 每张卡的「五、AI 视频层」里有 **运动** 与 **运镜** 两行，",
         "描述的正是这些招式。两边是互补的：",
         "",
         "- 电影卡说「要什么画面」（如「缓慢横移跟随，前景遮挡物在镜头前滑过」）",
         "- 镜头卡说「那一下怎么落地」（如「急推时长 6f，>10f 读作普通推近」）", "",
         "## 按类别", ""]
    for c in shot_core.categories():
        L.append("### [[%s\\|%s · %s]]（%d 张）"
                 % ("镜头总览", c["category"], c["name_zh"], c["count"]))
        L.append("")
        for s in shot_core.by_category(c["category"]):
            L.append("- `%s` —— %s" % (s["name"], s["one_liner"][:70]))
        L.append("")
    L += ["## 出处与许可", "",
          "全部卡片的技法描述版权归上游作者，**Apache-2.0**。",
          "逐卡的上游路径与 commit 见 [[出处与许可]]。", "",
          "← [[流派总览]] · [[电影风格总览]] · [[AI 调用指南]]", ""]
    return "\n".join(L)


def attribution_note():
    """45-shots/出处与许可.md

    这一页不是形式主义：Apache-2.0 要求保留出处，而上游 `ATTRIBUTION.md`
    里那段法律边界（「公开发布不等于授权」「实现全部从零重写」）如果丢了，
    读者会误以为这些卡带着某种复刻许可。
    """
    st = shot_core.stats()
    L = ["---", "type: 说明", "标签:", "  - 许可", "  - 镜头", "---", "",
         "# 镜头配方卡的出处与许可", "",
         "> [!warning] 一句话",
         "> 这 157 张卡的**技法描述来自上游，不是本库原创**。"
         "本库只做归类与排版，", "> 许可是 Apache-2.0。", "",
         "## 上游", "",
         "| 项 | 值 |", "|---|---|",
         "| 仓库 | [%s](%s) |" % (st["source"], shot_core.shots()[0]["source_url"]
                                   if shot_core.shots() else ""),
         "| 本库收录的 commit | `%s` |" % st["commit"],
         "| 许可 | %s |" % st["license"],
         "| 收录张数 | %d 张 / %d 类 |" % (st["shots"], st["categories"]),
         "| 相对上游的改动 | 无。只做归类、加出处、排版 |", "",
         "本库另有同源的 DSH 适配 fork "
         "[kingselyjoe/video-shotcraft-dsh](https://github.com/kingselyjoe/video-shotcraft-dsh)"
         "（152 张），两者是同一套卡，**本库只收一份**，以原仓库为准。", "",
         "## 上游自己写的法律边界（原样转述，别丢）", "",
         "上游 `references/shots/ATTRIBUTION.md` 写明：", "",
         "1. 这批卡的动效手法**研究自公开发布的产品宣传片与开源项目主页**；",
         "2. **所有实现均为从零重写**（re-implemented from scratch）——",
         "   仓库不包含任何原片片段、截图、美术资产或品牌元素；",
         "   实现中的文案、配色、UI 内容均为中性占位模板；",
         "3. 原作者未参与该项目，卡片标注来源**仅为致敬与研究溯源**"
         "（「仅参考、重新实现」）；",
         "4. **来源作品「公开发布」不等于授予复刻或衍生的许可** ——"
         " 该表是研究溯源记录，**不是授权凭证**。", "",
         "## 这对使用者意味着什么", "",
         "- ✅ 你可以照着这些卡做自己的动效（手法与技法一般属方法与创意范畴）",
         "- ❌ 不要拿这些卡去复刻某一支具体作品的可辨识整体视听呈现"
         "（画面、美术、文案、品牌元素受版权与商标保护）",
         "- ⚠️ 本库没有复制上游的 `assets/` 音频与 Remotion 模板代码，"
         "只收了 `references/shots/` 的卡文本", "",
         "## 重建", "",
         "```bash",
         "python3 .repo/shot_import.py --check        # 校验解析（离线夹具）",
         "python3 .repo/shot_import.py --import      # 写入 _data/shots/",
         "python3 .repo/shot_import.py --from-github # 拉上游最新再导入",
         "python3 .repo/shot_build.py                # 生成 45-shots/",
         "python3 .repo/tests/shot_test.py           # 本模块测试",
         "```", "",
         "← [[镜头总览]]", ""]
    return "\n".join(L)


def sweep():
    """清掉上次生成留下的 .md（与 fv_build 同一条理由）。"""
    if not os.path.isdir(OUT_DIR):
        return 0
    import glob
    killed = 0
    for p in glob.glob(os.path.join(OUT_DIR, "**", "*.md"), recursive=True):
        try:
            os.remove(p)
            killed += 1
        except OSError:
            pass
    for root, _d, _f in os.walk(OUT_DIR, topdown=False):
        if root != OUT_DIR:
            try:
                if not os.listdir(root):
                    os.rmdir(root)
            except OSError:
                pass
    return killed


def build():
    sweep()
    n = 0
    for c in shot_core.categories():
        sub = os.path.join(OUT_DIR, c["category"])
        os.makedirs(sub, exist_ok=True)
        for s in shot_core.by_category(c["category"]):
            with open(os.path.join(sub, "%s.md" % s["name"]), "w", encoding="utf-8") as f:
                f.write(card_note(s))
            n += 1
    with open(os.path.join(OUT_DIR, "镜头总览.md"), "w", encoding="utf-8") as f:
        f.write(overview_note())
    with open(os.path.join(OUT_DIR, "出处与许可.md"), "w", encoding="utf-8") as f:
        f.write(attribution_note())
    return n + 2


def main():
    n = build()
    st = shot_core.stats()
    print("已生成 %d 个文件 → %s" % (n, OUT_DIR))
    print("  %d 张卡 / %d 类（来源 %s，%s）"
          % (st["shots"], st["categories"], st["source"], st["license"]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 shot_build.py",
          ["把镜头配方卡生成成 Obsidian 笔记 → 45-shots/<类别>/<name>.md",
           "没有任何选项：读 _data/shots/*.json，重写 45-shots/。"])
    sys.exit(main())
