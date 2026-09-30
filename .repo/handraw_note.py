#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""handraw_note.py —— 第 7 大类「手绘艺术风格」的卡片渲染层。

单独一个文件而不是塞进 build_vault.py（那个文件已经 2500 行），理由是
**这一类的卡片模板和其它 6 类不是同一件事**：

    其它 6 类  七层提示词 = 手写的艺术史结论，出处是 Tate 术语词条
    手绘类     七层提示词 = 从 handraw 的 traits 原文按词表抽出（⟨条⟩）
                            + A–H 组级默认（⟨组⟩）

字段来源不同，卡就必须长得不一样 —— 至少要让读者一眼看出「这句话是
handraw 说的」还是「这句话是我们按组推的」。把两种卡塞进同一个模板、
只换数据，正是那种「看着统一、读起来骗人」的做法。

本模块只依赖标准库 + 本库既有模块。所有数字（条数、覆盖率、组大小）
一律现算，不写死 —— 这个库为写死的统计数字吃过一次亏。
"""

import glob
import os
import re

from movements import MOVEMENTS, build_positive
import artvault_core as AC
import video_prompt as VP
import mv_handraw as HW

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)

BY_SLUG = {m["slug"]: m for m in MOVEMENTS}

SHEET_RE = re.compile(r"^[A-H]_\d{3}-\d{3}\.webp$")

# 「另外 6 类有多少张卡」**现算**。这个库为写死的统计数字吃过一次亏
# （README 声称 654 张实图，克隆下来 442 张），而这里的 147 正好是最容易
# 变的那一类数字 —— 加一张卡就错。
N_OTHER = len([m for m in MOVEMENTS if m.get("kind") != "handraw"])


# ------------------------------------------------------------------ 小工具
def _yq(s):
    """frontmatter 里的单行标量：包双引号并转义。

    手绘类的字段来自第三方数据（参考作者里就有「Poorly Drawn Lines /
    Reza Farazmand」这种），不引号化的话，哪天出现一个带冒号的名字就会
    让 frontmatter 变成非法 YAML —— 验收第 4 项会红，但那时候已经很难
    定位是谁造成的。
    """
    return '"%s"' % str(s).replace("\\", "\\\\").replace('"', '\\"')


def _cell(s):
    """表格单元格里的文字。

    手绘类的文字全部来自第三方数据，出现一个 `|` 就会把整张表撕成两半，
    而 Markdown 表格不会报错 —— 只会静静地少显示几列。所以进表格的
    字符串一律先转义。
    """
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def ref_image(mv):
    """这条的编号参考图（发布视图里的相对路径），没有就返回 None。

    **只认落位在 99-attachments/images/ 下的那份**：验收第 1/7/15 项
    （断链 / 孤儿图 / 克隆完整性）都只认这个根。
    """
    rel = mv.get("handraw_image") or ""
    if rel and os.path.isfile(os.path.join(VAULT, rel)):
        return rel
    return None


def sheets():
    """(组字母, 发布视图路径) —— 拼图也复制进了 99-attachments，同样要能嵌入。"""
    out = []
    for p in sorted(glob.glob(os.path.join(VAULT, HW.LX.IMAGES_REL,
                                           "handraw-group-*.webp"))):
        b = os.path.basename(p)
        m = re.match(r"^handraw-group-([A-H])_", b)
        if m:
            out.append((m.group(1), os.path.join(HW.LX.IMAGES_REL, b).replace(os.sep, "/")))
    return out


def source_paths():
    """原始仓库里的相对路径，供卡上标注「本地副本」。"""
    return "30-handraw-style"


# ------------------------------------------------------------------ 流派卡
def card(mv):
    """渲染一张手绘风格卡。

    节次固定为 一~九，与其它流派卡**保持同一套编号** —— 验收第 11 项按
    「## 五、AI 视频层」到「## 六、」切段来查两块视频提示词，编号一乱
    它就会静默查不到。
    """
    A = []
    n = mv["handraw_number"]
    img = ref_image(mv)

    # name_zh 现在是**中文名**（274 条由 handraw_name.py 定名），
    # `别名` 放编号 —— Obsidian 里打开卡片看到的是名字，编号仍可检索。
    num_alias = mv.get("alias") or ""
    A.append("---")
    A.append("type: 流派")
    A.append("流派: %s" % mv["name_zh"])
    if num_alias:
        A.append("别名: %s" % _yq(num_alias))
    A.append("英文: %s" % _yq(mv["name_en"]))
    A.append("时期: %s" % mv["period"])
    A.append("地区: %s" % mv["region"])
    A.append("分类: %s" % mv["category"])
    A.append("编号: %s" % _yq(n))
    A.append("分组: %s" % _yq("%s %s" % (mv["handraw_group"], mv["handraw_group_label"])))
    A.append("参考作者/风格名称: %s" % _yq(mv["handraw_reference"]))
    A.append("配色: [%s]" % ", ".join('"%s"' % h for h, _ in mv["palette"]))
    A.append("标签:")
    A.append("  - 流派")
    A.append("  - 手绘")
    # 标签 slug 从英文名生成；G 组那 16 条的 name_en 是中文（「可爱萌系插画风」），
    # 清完之后得到空串 —— 卡上于是出现一行孤零零的 `  - `，在 Obsidian 里变成
    # 一个空标签。验收第 4 项抓不到它（那不是非法 YAML），所以这里自己兜住。
    _tag = re.sub(r"[^a-z0-9]+", "-", mv["name_en"].lower()).strip("-")
    A.append("  - %s" % (_tag or (HW.LX.IMAGE_PREFIX + n)))
    A.append("---")
    A.append("")
    if num_alias:
        A.append("# %s · %s" % (mv["name_zh"], mv["name_en"]))
        A.append("")
        A.append("> [!note] 这个名字是怎么来的")
        A.append("> **%s** —— 由本卡的 `traits` 原文抽出：" % mv["name_zh"])
        _from = mv.get("name_from") or []
        _basis = mv.get("name_basis") or ""
        if _basis == "traits" and _from:
            A.append("> %s" % "、".join("`%s`" % w for w in _from))
            A.append(">")
            A.append("> 每个词都能在本卡的「一、核心视觉特征」里逐字找到（可核对）。")
        elif _basis == "traits_unmatched":
            A.append("> ⚠️ 这条的 traits 用的是词表未收录的说法，**没有逐字命中的词**。")
            A.append("> 名字取自该条 traits 的整体意思，依据不如其它条硬 —— 用时请注意。")
        else:
            A.append("> ⚠️ 这条**没有 traits 原文**，名字退回英文生图名"
                     "（`%s`）译出。" % mv["name_en"])
            A.append("> 也就是说：这条的名字**不是**从中文特征里推出来的。")
        A.append(">")
        A.append("> 编号仍是 `%s`（本卡别名）；`%s` 与 `%s` 都能查到它。"
                 % (num_alias, num_alias, mv["name_zh"]))
    else:
        A.append("# %s · %s" % (mv["name_zh"], mv["name_en"]))
    A.append("")
    A.append("> [!abstract] 一句话")
    A.append("> **%s**" % _cell(mv["one_liner"]))
    A.append("")
    A.append("| 编号 | 分组 | 参考作者/风格名称 | 生图名称 |")
    A.append("|---|---|---|---|")
    A.append("| %s | %s | %s | %s |"
             % (_cell(n), _cell("%s %s" % (mv["handraw_group"],
                                    mv["handraw_group_label"])),
                _cell(mv["handraw_reference"]), _cell(mv["name_en"])))
    A.append("")
    A.append("> [!warning] 这张卡和另外 6 类的卡不是同一种证据强度")
    A.append("> 其它 %d 张卡的七层提示词是**手写的艺术史结论**，每层都能追到" % N_OTHER + "")
    A.append("> Tate 术语词条。这一类的七层是**从 handraw-style 的 `traits` 原文里")
    A.append("> 按词表抽出来的**，抽不到的层用 A–H 的组级默认补，所以六维表带标记：")
    A.append(">")
    A.append("> - `⟨条⟩` 该词在 traits 原文里逐字命中，可核对")
    A.append("> - `⟨组⟩` 该组（A–H）的组级共识，**不是这一条独有的特征**")
    A.append(">")
    A.append("> 「参考作者/风格名称」是 handraw 的**索引标签**：它标的是这条风格在")
    A.append("> 索引里挂在谁名下，既不是对作者本人的描述，也不是「照抄某人」的指令。")
    A.append("")
    if mv.get("handraw_traits_empty"):
        A.append("> [!caution] 这一条在原数据里没有 traits")
        A.append("> handraw-style 的 `styles.json` 里，编号 %s 的 `traits` 字段是空的。" % n)
        A.append("> 所以下面「一、核心视觉特征」没有内容，六维全部是组级默认 ——")
        A.append("> 这不是漏抓，是**原数据本身就没写**。要用这一条，请直接看编号参考图。")
        A.append("")
    A.append("---")
    A.append("")
    # 一、核心视觉特征
    A.append("## 一、核心视觉特征")
    A.append("")
    A.append("> 以下每一条都是 handraw-style `styles.json` 的 `traits` 原文，一字未改。")
    A.append("")
    for c in mv["core"]:
        A.append("- %s" % c)
    A.append("")
    # 二、六维
    A.append("## 二、视觉语言拆解（六维）")
    A.append("")
    A.append("| 维度 | 拆解（`⟨条⟩`=traits 原文命中，`⟨组⟩`=组级默认） |")
    A.append("|---|---|")
    for dim in HW.LX.DIMS:
        A.append("| **%s** | %s |" % (dim, _cell(mv["visual"][dim])))
    A.append("")
    # 三、配色
    A.append("## 三、配色板")
    A.append("")
    for h, name in mv["palette"]:
        A.append("- **%s** `%s`" % (name, h))
    A.append("")
    A.append("> [!example] 配色提示词（直接粘）")
    A.append("> `%s`" % ", ".join("%s %s" % (nm, h) for h, nm in mv["palette"]))
    A.append("")
    A.append("> 配色是**推导**：handraw 的数据里没有色值。这几个色取自 traits 提到的")
    A.append("> 颜色词，加上 %s 组的组级底色 —— 它不是从原图采样的。" % mv["handraw_group"])
    A.append("")
    # 四、提示词结构
    A.append("## 四、提示词结构")
    A.append("")
    A.append("> 每一层都能单独拆出来复用。镜头层是「要什么景别」而非风格属性，")
    A.append("> 所以不并入下面的整段，按画面需要自己接。")
    A.append("")
    A.append("| 层 | 可复用片段 |")
    A.append("|---|---|")
    for key, label in (("style", "风格"), ("lighting", "光照"), ("color", "色彩"),
                       ("composition", "构图"), ("medium", "媒介"),
                       ("mood", "情绪"), ("camera", "镜头")):
        A.append("| **%s** | `%s` |" % (label, _cell(mv["prompt"][key])))
    A.append("")
    A.append("### 整段正向提示词")
    A.append("")
    A.append("```text")
    A.append(build_positive(mv).strip())
    A.append("```")
    A.append("")
    A.append("> 这是**风格层**，接在你自己的主体描述后面用：")
    A.append("> `<你的主体>, %s`" % mv["prompt"]["style"][:80])
    A.append("")
    A.append("### 负向提示词")
    A.append("")
    A.append("```text")
    A.append(mv["negative"].strip())
    A.append("```")
    A.append("")
    # 五、视频层
    vp = VP.build(mv)
    A.append("## 五、AI 视频层")
    A.append("")
    A.append("> A 块给 **Seedance 2.5**，B 块给 **MiniMax H3**。两块格式不同，"
             "**别混用** —— 原因见 [[视频提示词结构]]。")
    A.append("")
    A.append("> 这一节的运动 / 运镜按 %s 组给，不是逐条从 traits 推的 ——"
             " %s。" % (mv["handraw_group"],
                        "手绘类原文里本来就不写镜头" if not mv.get("handraw_traits_empty")
                        else "这一条原文是空的，只能按组给"))
    A.append("")
    A.append("### A. Seedance 2.5 五段式")
    A.append("")
    A.append("```text")
    A.append(vp["seedance"])
    A.append("```")
    A.append("")
    A.append("### B. MiniMax H3（中文自然语言，直接粘进输入框）")
    A.append("")
    A.append("```text")
    A.append(vp["h3"])
    A.append("```")
    A.append("")
    A.append("> [!important] 这个组的视频关键")
    A.append("> %s" % mv["video"]["note"])
    A.append("")
    A.append("| 参考 | 内容 |")
    A.append("|---|---|")
    A.append("| **运动** | %s |" % _cell(mv["video"]["motion"]))
    A.append("| **运镜** | %s（%s） |" % (_cell(mv["video"]["camera"]), vp["camera_zh"]))
    A.append("| **建议时长** | %d 秒%s |" % (
        vp["duration"],
        "（这个组画面几乎静止，别硬加运镜）" if vp["static"] else
        "（H3 单次上限 15 秒；要更长需分段生成，接缝处会有一致性损耗）"))
    A.append("")
    # 六、编号参考图
    A.append("## 六、编号参考图")
    A.append("")
    if img:
        A.append("![[%s]]" % os.path.basename(img))
        A.append("")
        A.append("**handraw-style 编号 %s · %s**" % (n, mv["handraw_reference"]))
        A.append("")
        A.append("> 这张图是 handraw-style 的**风格参考**，不是本库抓的公共领域实图。")
        A.append("> 用它时只取画风（线条、笔触、媒介、材质、色彩倾向、整体视觉语言），")
        A.append("> 不要把图里的主体、人物、道具、构图、文字一起搬过去 —— 画面内容只由")
        A.append("> 你自己的主题决定。")
    else:
        A.append("> 编号参考图不在库里（期望位置：`%s`）。" % (
            mv.get("handraw_image") or
            "%s/handraw-%s.webp" % (HW.LX.IMAGES_REL, n)))
        A.append("> 这里**不写嵌入占位** —— 嵌一张不存在的图会让验收第 1 项（断链）")
        A.append("> 与第 15 项（克隆完整性）同时报错，而那不是内容问题。")
    A.append("")
    # 七、翻车点
    A.append("## 七、常见翻车点")
    A.append("")
    for p in mv["pitfalls"]:
        A.append("- %s" % p)
    A.append("")
    # 八、关联
    A.append("## 八、关联风格")
    A.append("")
    same = [s for s in mv["see_also"] if s.startswith("handraw-")]
    cross = [s for s in mv["see_also"] if not s.startswith("handraw-")]
    A.append("同组近邻（编号相邻，画面最接近）：")
    A.append("")
    for s in same:
        t = BY_SLUG.get(s)
        if t:
            A.append("- [[%s]] · %s" % (t["name_zh"], t["name_en"]))
    A.append("")
    if cross:
        A.append("跨类谱系（**编者加的**，不是 handraw-style 的数据）：")
        A.append("")
        for s in cross:
            t = BY_SLUG.get(s)
            if t:
                A.append("- [[%s]] · %s" % (t["name_zh"], t["name_en"]))
        A.append("")
    A.append("本组全部编号 → [[分类索引-%s]]；编号用法与画廊 → [[手绘风格总览]]"
             % mv["category"])
    A.append("")
    # 九、来源与署名
    A.append("## 九、来源与署名")
    A.append("")
    A.append("| 项 | 内容 |")
    A.append("|---|---|")
    A.append("| 数据来源 | [yang0/handraw-style](https://github.com/yang0/handraw-style) "
             "· `skills/handdraw-style-prompter/references/styles.json` |")
    A.append("| 本条编号 | %s（%s 组 · %s） |" % (n, mv["handraw_group"],
                                                mv["handraw_group_label"]))
    A.append("| 参考作者/风格名称 | %s —— **索引标签**，不代表作者本人，也不构成模仿指令 |"
             % _cell(mv["handraw_reference"]))
    A.append("| 授权 | MIT（原仓库 LICENSE 随仓库一并保留在 `%s/`） |" % source_paths())
    A.append("| 本地副本 | `%s/` 整棵，未作修改 |" % source_paths())
    A.append("| 本库角色 | 第 7 大类「%s」的第 %s 条 |" % (mv["category"], n))
    A.append("")
    A.append("---")
    A.append("")
    A.append("← [[流派总览]] · [[分类索引-%s]]　|　延伸阅读 [[手绘风格总览]]、[[提示词拆解方法]]"
             % mv["category"])
    return "\n".join(A)


# ------------------------------------------------------------------ 组总览页
def overview():
    """00-guides/手绘风格总览.md —— 这一大类的门厅。

    同时承担一个验收上的职责：把 20 张拼图**真的引用一遍**。
    99-attachments/images/ 下的每张图都必须被某篇笔记引用（验收第 7 项），
    嵌在门厅页上比散在各组卡片里更合理 —— 拼图本来就是「一眼看一组」用的。
    """
    cov = HW.coverage()
    A = []
    A.append("---")
    A.append("type: MOC")
    A.append("分类: %s" % HW.CATEGORY)
    A.append("---")
    A.append("")
    A.append("# %s · 总览" % HW.CATEGORY)
    A.append("")
    A.append("← 返回 [[流派总览]]　|　分类索引 [[分类索引-%s]]" % HW.CATEGORY)
    A.append("")
    A.append("> [!abstract] 这是什么")
    A.append("> [handraw-style](https://github.com/yang0/handraw-style) 的 **%d 个编号"
             "手绘风格**，整棵装进本库，成为第 7 大类。" % cov["n"])
    A.append("> 原仓库原样保留在 `%s/`（含它自己的画廊、脚本与校验工具，"
             "一个字没改）。" % source_paths())
    A.append("")
    A.append("> [!warning] 这一类与另外 6 类的证据强度不同")
    A.append("> 另外 %d 张卡的七层提示词是**手写的艺术史结论**，每层追得到 Tate 术语词条；" % N_OTHER + "")
    A.append("> 这一类的七层是**从 handraw 的 `traits` 原文里按词表抽出来的**，")
    A.append("> 抽不到的层用 A–H 的组级默认补。卡上的六维表因此带标记：")
    A.append(">")
    A.append("> - `⟨条⟩` 该词在 traits 原文里逐字命中，可核对")
    A.append("> - `⟨组⟩` 该组（A–H）的组级共识，不是这一条独有的特征")
    A.append(">")
    A.append("> 现算的抽取覆盖率：六维共 **%d** 格，其中 **%d** 格来自 traits 原文"
             "（**%.1f%%**），其余为组级默认。"
             % (cov["cells"], cov["extracted"],
                100.0 * cov["extracted"] / max(1, cov["cells"])))
    A.append("> 逐维明细与复算命令：`cd .repo && python3 mv_handraw.py --stats`")
    A.append("")
    A.append("| 维度 | 抽到（条 / %d） |" % cov["n"])
    A.append("|---|---|")
    for dim, k in cov["by_dim"].items():
        A.append("| %s | %d |" % (dim, k))
    A.append("")
    A.append("## 怎么用")
    A.append("")
    A.append("1. **卡片以中文名命名**（不再是编号）。名字由该条的 `traits` "
             "原文抽出，卡上写明用了哪几个词（可核对）。编号降为 `别名:` —— "
             "`手绘041` 与 `极端比例弯曲绘本` 都能查到同一张卡。")
    A.append("   · 按名字找：`python3 artvault.py show 极端比例弯曲绘本`")
    A.append("   · 按编号找：`python3 artvault.py show 手绘041`（编号是别名）")
    A.append("   · 列出全部名字：`python3 .repo/handraw_name.py --list`")
    A.append("   · 名字的依据统计：`python3 .repo/handraw_name.py --stats`")
    A.append("2. 想按图挑：打开原仓库的编号画廊 "
             "[gallery/index.html](../%s/skills/handdraw-style-prompter/gallery/index.html)，"
             "记下喜欢的编号。" % source_paths())
    A.append("3. 想按词挑：`python3 artvault.py search \"钢笔速写 留白\"`，"
             "或直接看下面的分组。")
    A.append("4. 拿到七层：`python3 artvault.py layers 手绘041`。")
    A.append("5. 拼提示词：`python3 artvault.py compose --style handraw-041 "
             "--lighting baroque --subject \"...\"` —— 手绘类可以和另外 6 类混搭。")
    A.append("")
    A.append("> [!tip] 两种模式（来自 handraw 自己的约定）")
    A.append("> **纯图模式**（默认）：主题只决定画面内容，画面里不出现文字。")
    A.append("> **图文模式**：保留你写的主题原文，让文字参与构图，适合金句、海报。")
    A.append("> 切换时说一句「切换为图文模式」即可；本库的卡只负责给风格层。")
    A.append("")
    A.append("> [!important] 参考图的用法")
    A.append("> 只取画风（线条、笔触、媒介、材质、色彩倾向、整体视觉语言），")
    A.append("> **不要**把参考图里的主体、人物、服装、道具、动作、场景、构图、文字")
    A.append("> 一起搬过去 —— 画面内容只由你的主题决定。")
    A.append("")
    A.append("## 八个组")
    A.append("")
    by_group = {}
    for _g, _label, ms in HW.groups():
        by_group[_g] = ms
    smap = {}
    for g, rel in sheets():
        smap.setdefault(g, []).append(rel)
    for g, label, ms in HW.groups():
        A.append("### %s · %s（%d 条）" % (g, label, len(ms)))
        A.append("")
        A.append("编号 %s–%s ｜ [[分类索引-%s|本组全部条目 →]]"
                 % (ms[0]["handraw_number"], ms[-1]["handraw_number"], HW.CATEGORY))
        A.append("")
        for rel in smap.get(g, []):
            A.append("![[%s]]" % os.path.basename(rel))
            A.append("")
        A.append("例：[[%s]] · [[%s]] · [[%s]]"
                 % (ms[0]["name_zh"], ms[len(ms) // 2]["name_zh"], ms[-1]["name_zh"]))
        A.append("")
    A.append("## 来源与署名")
    A.append("")
    A.append("| 项 | 内容 |")
    A.append("|---|---|")
    A.append("| 原仓库 | [yang0/handraw-style](https://github.com/yang0/handraw-style)（MIT） |")
    A.append("| 本地副本 | `%s/` 整棵，未作修改；来源与提交见其 `SOURCE.md` |" % source_paths())
    A.append("| 编号参考图 | `%s/`，编号 `001`–`274`，与卡一一对应 |" % HW.LX.IMAGES_REL)
    A.append("| 参考作者/风格名称 | handraw 的**索引标签**，不代表作者本人，"
             "也不构成模仿指令 |")
    A.append("| 本库做的加工 | 只做翻译与推导：`traits` 原文进卡，七层由词表抽取，"
             "其余为组级默认 |")
    A.append("")
    A.append("---")
    A.append("")
    A.append("延伸：[[流派总览]] · [[分类索引-%s]] · [[关键词图谱]] · [[配色速查]]"
             % HW.CATEGORY)
    return "\n".join(A)
