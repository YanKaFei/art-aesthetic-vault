#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_i18n.py —— 四语 README 的正文模板（中 / 英 / 日 / 法）。

## 为什么单独一个文件

四份 README 说的是同一件事。它们最危险的失效方式不是「翻译得不好」，而是
**四种说法互相漂移** —— 中文版补了一句话，日文版还停在上一版，读者看哪份
取决于他点开哪个链接。放在同一个文件里、按同样的章节顺序排，改的时候
四份就在眼前，漂移会难受得多。

模板里 `{n_*}` 是统计占位符，由 `build_vault.build_vault()` 用
`publish_stats()` 现算的值填进去；`{skill_tree*}` 是技能树。

## 数字为什么全部写成占位符

这个库吃过一次亏：README 写「654 张公共领域实图」，克隆下来只有 442 张 ——
虚报 48%。根因是统计口径与 README 文案各写各的。所以正文里**任何一个
「这个库有多少东西」的数字都必须来自 `{n_*}`**，并且
`verify_vault.check_readme_numbers()` 会用同一份口径逐条核对四份 README。
新增一个数字 = 在那边加一行声明，否则这项数字没人守。
"""

# ===================================================================== 中文
README_ZH = """<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="画派、手绘与电影剧照：本库覆盖的四条轴">

# 艺术审美风格库

**把「视觉风格」拆成可以直接调用的提示词层**

画派 · 手绘 · 导演 · 运镜 —— 四条轴，同一套结构

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/{REPO_SLUG}?style=flat-square)](LICENSE)

`{n_mv} 个画派` · `{n_hn} 个手绘风格` · `{n_films} 部电影` · `{n_shots} 张运镜配方` · `{n_notes} 篇笔记` · `{n_img} 张图`

[English](README.en.md) ｜ [日本語](README.ja.md) ｜ [Français](README.fr.md) ｜ **中文**

</div>

---

## 这是什么

大多数人收集「风格参考」的方式是存图 —— 存了几百张，真要用的时候不知道该看什么、
该怎么描述。图是死的。

这个库换个做法：**把每一种视觉语言的构成，拆成七个可以独立替换的层**。

<img src="99-attachments/readme/layers.png" width="100%" alt="七层：风格 / 光照 / 色彩 / 构图 / 媒介 / 情绪 / 镜头">

拆成层之后，你才能把 A 图的光照套到 B 图的主体上。**这才是参考库真正的用处。**

```bash
python3 artvault.py compose \\
  "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \\
  --subject "a female bounty hunter in a wet neon alley"
```

它会自动识别「巴洛克」后面跟着「光照」→ 取巴洛克的光照层；「赛博朋克」→ 取风格与构图层。
输出是分好层的正向提示词、负向提示词、配色、视频层，以及一份**冲突消解记录**。

> **同一个主体，每一层都可以单独换掉。** 这是这个库和「风格词堆砌」的根本区别。

---

## 四条轴

四条轴共用同一套卡片结构与同一套七层词表，所以可以跨轴混搭 ——
电影的光照 + 画派的配色 + 手绘的媒介。

| | 轴 · 规模 | 它回答什么 |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="画派风格"> | **画派风格 · {n_mv} 个**<br>（{n_cats} 大分类） | 从拜占庭到 Y2K，从浮世绘到赛博朋克。每个流派一张卡：六维视觉拆解 + 七层提示词 + 六色配色 + 针对性负向词 + 视频层<br>`python3 artvault.py layers 巴洛克` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="手绘风格"> | **手绘风格 · {n_hn} 个**<br>（A–H 八组） | 绘本、社论漫画、当代插画、国风……来自 [handraw-style](https://github.com/yang0/handraw-style)（MIT），整块并入本库。卡片以中文名命名，编号作别名保留<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="导演与电影"> | **导演与电影 · {n_films} 部**<br>（{n_film_directors} 位导演） | 不只是「长什么样」，而是「谁拍的、怎么拍的」。按「导演 → 电影」组织：代表帧 + 六维拆解 + 七层提示词 + 配色 + 视频层，另索引 **{n_film_stills} 条剧照外链**（只索引不转载）<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="运镜配方"> | **运镜配方 · {n_shots} 张**<br>（{n_shot_cats} 类） | 前三条轴回答「长什么样」，这一条回答「**这一下怎么做出来**」。帧数、缓动、幅度写成参数表，附已知坑。来自 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0，本库只做归类与排版）<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **镜头卡没有色彩与光照字段，这是故意的。** 它讲的是帧数与缓动
> （`zoom 6f ease-in，1→2.6`），套七层只能靠编。所以它按自己的四字段排，
> 并且**刻意不参与 `compose` 的层解析** —— 有测试守着这条边界。

---

## 一眼看规模

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="本库覆盖的画派、手绘与电影示例">

| | 数量 |
|---|---|
| **流派卡** | **{n_mv} 张**，{n_cats} 大分类，每张含六维视觉拆解 + 七层提示词 + 配色 + 视频层 |
| **实图** | **{n_img} 张**（{img_mb} MB）：公共领域实图 **{n_work_img} 张** + handraw-style 编号参考图 **{n_ref_img} 张**（MIT）；{n_mv_with_img} 个流派配了图 |
| **手绘卡中文名** | **{n_hn_named} / {n_hn}** 张已有名字（其中 {n_hn_traits} 张由 `traits` 逐字抽出、{n_hn_gen} 张因无 traits 由英文生图名回译） |
| **导航与方法论** | {n_guides} 篇（流派总览、关键词图谱、七层方法、视频结构、配色速查…） |
| **关键词图谱** | 最容易混的 **{n_concepts} 组**概念，共 **{n_synonyms} 个**同义说法，搜任何一个都落到同一张卡 |
| **电影风格卡** | **{n_films} 部**（{n_film_directors} 位导演）：按「导演 → 电影」组织，每张含剧照索引 + 六维拆解 + 七层提示词 + 配色 + 视频层，另有 **{n_film_stills} 条剧照外链**（只索引不转载） |
| **镜头配方卡** | **{n_shots} 张**（{n_shot_cats} 类）：运镜与动效招式，含参数表（帧数/缓动/幅度）与已知坑。来自 [{shot_source}](https://github.com/{shot_source})，**Apache-2.0，本库只做归类与排版** |
| **笔记模板** | {n_templates} 个（流派卡 / 提示词卡 / 作品拆解） |
| **脚本** | {n_scripts} 个，抓图、生成、检索、提示词合成、MCP 服务 |

> **{n_mv_no_img} 个流派是「纯提示词卡」** —— 抽象表现主义、波普、极简主义、观念艺术、
> 赛博朋克、蒸汽波这些，几乎找不到可自由分发的实图。它们的视觉语言与七层结构照常
> 拆解，只是不配图。这是刻意的设计，不是缺失。

---

## 怎么用

### 一、当作 Obsidian 仓库读

直接用 Obsidian 打开这个文件夹。建议按这个顺序进入：

1. `00-guides/提示词拆解方法.md` —— **先读这个**，理解七层是怎么回事
2. `00-guides/流派总览.md` —— 全部流派的总入口
3. `10-movements/` —— 挑一个你喜欢的流派，看它的完整拆解
4. `00-guides/关键词图谱.md` —— 以后看到陌生风格词就来这里查

### 二、让 AI 直接调用它

库不只是一堆给人看的 Markdown，还有一层**给机器用的接口**：

```bash
cd .repo

python3 artvault.py categories              # 看 {n_cats} 大分类
python3 artvault.py search "霓虹 雨夜"       # 模糊检索，中英文都行
python3 artvault.py search "压抑但华丽的光" --semantic   # 描述性说法：关键词抓不住，语义能
python3 artvault.py layers 巴洛克            # 只要七层提示词（最省 token）
python3 artvault.py show 浮世绘              # 完整卡片
python3 artvault.py palette 赛博朋克         # 六色配色
python3 artvault.py related 立体主义         # 找关联流派

python3 artvault.py film list               # {n_films} 部电影
python3 artvault.py shots search "急推 冲击"  # 按「我想做什么」找运镜

python3 artvault.py --json layers 巴洛克     # 机器可读
```

**核心能力是组合**：

```bash
# 自然语言，自动分层
python3 artvault.py compose "雨夜霓虹的赏金猎人，要巴洛克的光照" --subject "a bounty hunter"

# 显式指定，跨时代混搭
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
  --color vaporwave --composition precisionism --subject "a lone samurai"

# 跨轴：电影的光照 + 画派的配色
python3 artvault.py compose --lighting villeneuve-dune --color baroque \\
  --subject "a lone figure on a dune"
```

它会**自动消解层级冲突**。跨流派混搭时负向词会互相打架 ——
浮世绘禁止 `cast shadows`，巴洛克光照却要求 `deep crushed shadows`；
精确主义禁止 `people`，而你的主体是个人物。
**模型不会报错**，只会表现为「出图质量莫名地差」，极难排查。
所以打架的负向词会被**自动从负向提示词里拿掉**，并在「已自动消解的冲突」里
逐条说明拿掉了什么、让位给谁。规则一句话：**正向是意图，负向是护栏，护栏让位于意图。**
想要原样合集自己判断，加 `--keep-conflicts`。

### 三、装成 AI skill（推荐）

仓库自带两个 skill，装上之后**任何支持 skill 的 AI 助手**在遇到视觉 / 审美类任务时
会自动查这个库，而不是凭记忆编造流派术语。

```bash
cd .repo/skill && ./install.sh
```

| skill | 干什么 | 什么时候触发 |
|---|---|---|
| `art-aesthetic-vault` | **用**库：检索流派、取七层提示词、跨流派拼提示词 | 你问「这个角色该用什么风格」 |
| `build-art-aesthetic-vault` | **建**库：从零建一套新的 | 你说「我也想要一套这样的库」 |

> [!note] 为什么两个 skill 都不自带数据
> 它们都是**软链**指向本仓库 —— 数据只有仓库这一份。
> `mv_*.py`（流派定义）如果被打包进 skill，就会出现两份、必然会分叉。
> 实测过：打包版本里有 4 个文件与仓库不同步，用它建出来的库分类是错的。

它会把这些软链建到本机所有可用的 skill 目录：

| 目录 | 谁读它 |
|---|---|
| `~/.agents/skills/` | DSH / Codex / 通用约定 |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**为什么用软链**：skill 可以用 `pwd -P` 解析出自己的真实位置，从而推断出仓库根目录
—— **仓库放在哪、移不移动都能自动找到**，不需要任何配置。

```bash
.repo/skill/install.sh --copy        # 复制安装（不用软链，但仓库移动后要重装）
.repo/skill/install.sh --uninstall   # 卸载
bash .repo/skill/locate.sh           # 手动定位仓库（排查用）
```

装完**新开一个 AI 会话**才会生效。

### 四、接入 MCP（Claude Desktop / Cursor）

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<本仓库绝对路径>/.repo/mcp_server.py"]
    }
  }
}
```

暴露 16 个工具：`search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`，电影库 `search_films` `get_film` `get_film_layers` `get_film_stills`，
镜头库 `search_shots` `get_shot`。
后几个工具另需 Pillow / CLIP 模型；条件不满足时会说明原因，不影响前七个。

---

## 它好在哪里

### 1. 不是图包，是可组合的结构

图包给你「这是什么感觉」，这个库给你「怎么做出这种感觉」。
每一层都可以单独摘出来复用：换主体不换风格层，就是风格迁移模板。

### 2. 光照层被单独拎出来了

大多数人写提示词时把一切混在一起，靠试错调。这个库明确告诉你：
**光照对最终质感的影响比风格词本身更大。**
每个流派的光照层都是独立一段，可以直接搬到别的主题上。

### 3. 每条轴都有「针对性负向词」

针对**这个流派**的典型翻车点，而不是一份通用负面清单：

- 印象派 → `black shadows, smooth blending, photorealistic`
- 文艺复兴 → `visible brushstrokes, impasto`（AI 默认会给油画加厚涂）
- 浮世绘 → `3d shading, cast shadows, gradient`（AI 会自动加立体感）

**注意不同流派的负向词经常是相反的** —— 这正是混搭会打架的原因，
也是库帮你管住的东西。

### 4. AI 可以用，不只是你能看

大模型对艺术流派的记忆是模糊的，常把 Art Nouveau 和 Art Deco、
巴比松和印象派搞混。这个库把每个流派的具体术语固化下来，AI 调用时不会瞎编。

### 5. 术语是钉住的，不是编的

关键词图谱挑出最容易混的 **{n_concepts} 组**概念 —— 先锋、当代、后现代、超现实。
每组给一条定义、若干条「它不等于什么」的边界，以及 **{n_synonyms} 个**同义说法，
搜任何一个都落到同一张卡。

### 6. 你手里那张图，也能直接变成视频提示词

卡片上的视频提示词是**通用**的 —— 主体那一行是占位符。但你真正要干的事
通常是「我有这张图，让它动起来」：

```bash
python3 i2v_prompt.py 你的图.jpg --slug baroque
```

主体的景别、在画面哪个位置、画面内部的动势方向、光要不要动、镜头推还是移，
全部从**这张图的客观测量**推出来（人脸景别 / 显著性中心 / 线条方向 / 细节密度 /
明暗结构），并附一份「推导依据」让你核对。生成出来仍留着「谁、在做什么，
你自己补一句」—— 内容只有看图的人知道，脚本不替你编。

### 7. 数字是现算的，不是写死的

README 上每一个「这个库有多少东西」的数字，都由 `publish_stats()` 按**发布视图**
（git 跟踪了什么，而不是作者机上有什么）现算，再被 `verify_vault.py` 逐条核对。
写死的数字唯一的作用，就是某天变成错的 —— 这个库在这一点上栽过，所以加了锁。

---

## 三条原则

1. **宁可少，不要错。**
   筛选时刻意不做「放宽补充」—— 某个流派只有 1 张图就 1 张。
   一个参考库最怕的不是图少，是图错。错的参考会污染你的直觉，而且你自己不会发现。

2. **光照比风格词更重要。**
   如果你只有一个层可以调，调光照。

3. **不要凭记忆编造流派术语。**
   大模型对艺术流派的记忆是模糊的，容易把相近的画派搞混。以库里的具体术语为准。

---

<details>
<summary><b>展开完整技能树（{n_mv} 个流派 / {n_cats} 大分类）</b></summary>

{skill_tree}

</details>

---

## 贡献者与来源

这个库能成立，靠的是一批**愿意把成果开放出来的人**。下面每一处都不是「参考了一下」，
而是**整块搬进来、按同一套结构重排**的：

| 来源 | 贡献了什么 | 许可 |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **{n_hn} 个手绘风格**与编号参考图，构成本库第 7 大类 | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **{n_shots} 张运镜配方卡**（{n_shot_cats} 类），本库只做归类与排版 | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | 电影剧照索引；卡片内嵌的代表帧**版权属原片方** | 站点声明：*images are not permitted for commercial use*。仅个人研究参考 |
| [Tate 艺术术语表](https://www.tate.org.uk/art/art-terms) | 每张流派卡「出处」一节的术语定义页 —— 七层的说法追得到权威出处 | 术语版权归 Tate，本库**仅作出处引用** |
| [克利夫兰艺术博物馆](https://openaccess-api.clevelandart.org) · [芝加哥艺术博物馆](https://api.artic.edu/docs/) · [大都会艺术博物馆](https://collectionapi.metmuseum.org) · [维基共享资源](https://commons.wikimedia.org) | **{n_work_img} 张公共领域实图** | **CC0 / 公共领域** |

**三条要说明白的边界**：

1. **镜头卡不是本库原创。** 那 {n_shots} 张的技法描述版权归上游（Apache-2.0），
   本库只做归类与排版，逐卡带上游路径与 commit。上游自己写明：动效手法研究自公开作品，
   但**实现全部从零重写**、不含任何原片素材；且「公开发布**不等于**授权」。
   别拿这些卡去复刻某一支具体作品的可辨识整体视听呈现。
2. **电影剧照版权属原片方。** 卡片内嵌的代表帧仅供**个人研究参考**；
   film-grab 写明不得商用。公开分发或商用前请自行取得授权。
3. **「参考作者 / 风格名称」是索引标签**，不是对作者本人的描述，也不是模仿指令。
   编号参考图只取画风 —— 不要把图里的主体、构图、文字一起搬走。

本库自己的部分（七层拆解、卡片结构、CLI / MCP、检索与合成逻辑）以 MIT 发布。

---

## 许可

- **代码与卡片文本**：[MIT](LICENSE)
- **公共领域实图**：CC0 / 公共领域，来源与授权写在每张卡的「出处」一节
- **handraw-style 编号参考图**：MIT（上游）
- **镜头配方卡**：Apache-2.0（上游），本库只做归类与排版
- **电影剧照**：版权属原片方，仅个人研究参考

---

<div align="center">

如果这个库对你有用，欢迎 Star ⭐ 或提交 PR 补充更多流派

</div>
"""


# ===================================================================== English
README_EN = """<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="Art movements, hand-drawn styles and film stills across the four axes">

# Art Aesthetic Style Library

**Visual style, decomposed into prompt layers you can actually call**

Movements · Hand-drawn · Directors · Camera moves - four axes, one structure

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/{REPO_SLUG}?style=flat-square)](LICENSE)

`{n_mv} movements` · `{n_hn} hand-drawn styles` · `{n_films} films` · `{n_shots} shot recipes` · `{n_notes} notes` · `{n_img} images`

[中文](README.md) ｜ [日本語](README.ja.md) ｜ [Français](README.fr.md) ｜ **English**

</div>

---

## What this is

Most people collect style references by saving images. You end up with a few hundred
of them and no idea what to look at or how to describe it. Images are dead weight.

This vault does something else: **it decomposes each visual language into seven
independently replaceable layers.**

<img src="99-attachments/readme/layers.png" width="100%" alt="Seven layers: style / lighting / color / composition / medium / mood / camera">

Once it is in layers, you can put the lighting of image A onto the subject of image B.
**That is the actual point of a reference library.**

```bash
python3 artvault.py compose \\
  "a bounty hunter in a rainy neon street, baroque lighting, cyberpunk framing" \\
  --subject "a female bounty hunter in a wet neon alley"
```

It reads the intent behind each phrase ("baroque" followed by "lighting" gets the
baroque lighting layer), then emits layered positive prompts, negative prompts,
a palette, a video layer, and a **conflict-resolution record**.

> **Same subject, every layer swappable.** That is the difference between this and a
> pile of style keywords.

---

## Four axes

All four axes share the same card structure and the same seven-layer vocabulary,
so you can mix across axes: a film's lighting + a movement's palette + a
hand-drawn medium.

| | Axis · scale | What it answers |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="Art movements"> | **Art movements · {n_mv}**<br>({n_cats} categories) | Byzantine to Y2K, ukiyo-e to cyberpunk. One card per movement: six-axis visual breakdown + seven prompt layers + six-colour palette + targeted negatives + video layer<br>`python3 artvault.py layers baroque` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="Hand-drawn styles"> | **Hand-drawn styles · {n_hn}**<br>(groups A-H) | Storybooks, editorial cartoons, contemporary illustration, guofeng... from [handraw-style](https://github.com/yang0/handraw-style) (**MIT**), merged in whole. Cards are named in Chinese, with the upstream number kept as an alias<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="Directors and films"> | **Directors & films · {n_films}**<br>({n_film_directors} directors) | Not just "what it looks like" but "who shot it and how". Organised director then film: representative frames + six-axis breakdown + seven prompt layers + palette + video layer, plus **{n_film_stills} external still links** (indexed, never rehosted)<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="Shot recipes"> | **Shot recipes · {n_shots}**<br>({n_shot_cats} categories) | The first three axes answer "what does it look like"; this one answers "**how do I actually make that move**". Frames, easing and amplitude as parameter tables, with known pitfalls. From [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) (**Apache-2.0** - this vault only categorises and formats them)<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **Shot cards have no colour or lighting fields, deliberately.** They talk about
> frame counts and easing (`zoom 6f ease-in, 1 to 2.6`); forcing them into the
> seven layers would mean inventing content. So they carry their own four fields and
> **stay out of `compose` layer resolution** - a test guards that boundary.

---

## At a glance

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="Sample movements, hand-drawn styles and films in this vault">

| | |
|---|---|
| **Movement cards** | **{n_mv}**, in {n_cats} categories. Each has a 6-axis visual breakdown, 7 prompt layers, a 6-color palette, a video layer, and known failure modes |
| **Images** | **{n_img}** ({img_mb} MB) = **{n_work_img}** public-domain museum images + **{n_ref_img}** handraw-style numbered reference sheets (MIT); covering {n_mv_with_img} movements |
| **Hand-drawn card names** | **{n_hn_named} / {n_hn}** named ({n_hn_traits} derived word-for-word from `traits`; {n_hn_gen} back-translated from the English generation name where `traits` is empty) |
| **Guides & methodology** | {n_guides} notes (overview, keyword atlas, the 7-layer method, video structure, palette index...) |
| **Keyword atlas** | The **{n_concepts} most-confused concept groups**, **{n_synonyms} synonyms** in total - search any of them and land on the same card |
| **Film style cards** | **{n_films}** ({n_film_directors} directors), organised director then film: still index + six-axis breakdown + seven prompt layers + palette + video layer, plus **{n_film_stills} external still links** (indexed, never rehosted) |
| **Shot recipe cards** | **{n_shots}** ({n_shot_cats} categories): camera moves and motion effects with parameter tables (frames/easing/amplitude) and known pitfalls. From [{shot_source}](https://github.com/{shot_source}), **Apache-2.0 - this vault only categorises and formats them** |
| **Note templates** | {n_templates} |
| **Scripts** | {n_scripts} - fetch, generate, search, compose, MCP server |

> **{n_mv_no_img} movements are "prompt-only cards."** Abstract Expressionism, Pop Art,
> Minimalism, Conceptual Art, Cyberpunk, Vaporwave - freely distributable images for
> these essentially do not exist. Their visual language and seven layers are broken
> down exactly as usual; they simply carry no images. That is a deliberate design
> decision, not a gap.

---

## How to use it

### 1. Read it as an Obsidian vault

Open this folder in Obsidian. A good order to walk in:

1. `00-guides/提示词拆解方法.md` - **start here** to understand the seven layers
2. `00-guides/流派总览.md` - the master index of every movement
3. `10-movements/` - pick a movement you like and read its full breakdown
4. `00-guides/关键词图谱.md` - look up any unfamiliar style term later

### 2. Let an AI call it

This is not only Markdown for humans; there is a **machine-facing interface**:

```bash
cd .repo

python3 artvault.py categories              # the {n_cats} categories
python3 artvault.py search "neon rain"      # fuzzy search, Chinese or English
python3 artvault.py search "oppressive but gorgeous light" --semantic
python3 artvault.py layers baroque          # just the seven layers (cheapest)
python3 artvault.py show ukiyo-e            # the full card
python3 artvault.py palette cyberpunk       # the six-colour palette
python3 artvault.py related cubism          # neighbouring movements

python3 artvault.py film list               # {n_films} films
python3 artvault.py shots search "crash zoom punch"

python3 artvault.py --json layers baroque   # machine readable
```

**Composition is the core capability**:

```bash
# natural language, layered automatically
python3 artvault.py compose "a bounty hunter in rainy neon, baroque lighting" \\
  --subject "a bounty hunter"

# explicit, mixing eras
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
  --color vaporwave --composition precisionism --subject "a lone samurai"

# across axes: a film's lighting + a movement's palette
python3 artvault.py compose --lighting villeneuve-dune --color baroque \\
  --subject "a lone figure on a dune"
```

It **resolves layer conflicts automatically**. When you mix movements, their negative
prompts contradict each other - ukiyo-e bans `cast shadows`, baroque lighting demands
`deep crushed shadows`; precisionism bans `people` while your subject *is* a person.
**The model does not error**; you just get "mysteriously bad images", which is
extremely hard to debug. So conflicting negatives are **removed from the negative
prompt** and listed one by one under "auto-resolved conflicts", saying what was
dropped and what it yielded to. The rule in one line: **positives are intent,
negatives are guardrails, and guardrails yield to intent.** Add `--keep-conflicts`
to see the raw union and judge for yourself.

### 3. Install it as an AI skill (recommended)

The repo ships two skills. Once installed, **any skill-aware AI assistant** will
consult this vault for visual/aesthetic tasks instead of inventing movement
terminology from memory.

```bash
cd .repo/skill && ./install.sh
```

| skill | Does what | Triggers when |
|---|---|---|
| `art-aesthetic-vault` | **Use** the vault: search movements, pull seven layers, compose across movements | You ask "what style should this character be?" |
| `build-art-aesthetic-vault` | **Build** a vault: start one from scratch | You say "I want a library like this" |

> [!note] Why neither skill bundles the data
> Both are **symlinks** into this repo - there is exactly one copy of the data.
> If `mv_*.py` (the movement definitions) were packaged into the skill, there would
> be two copies and they would inevitably diverge. We tested this: the packaged
> version had 4 files out of sync with the repo, and vaults built from it had the
> wrong categories.

It creates symlinks in every skill directory it can find:

| Directory | Read by |
|---|---|
| `~/.agents/skills/` | DSH / Codex / general convention |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Why symlinks**: the skill resolves its own real location with `pwd -P` and infers
the repo root from it - **wherever the repo lives, and however you move it, it is
found automatically**, with no configuration.

```bash
.repo/skill/install.sh --copy        # copy instead (must reinstall if the repo moves)
.repo/skill/install.sh --uninstall
bash .repo/skill/locate.sh           # locate the repo manually (for debugging)
```

Skills take effect in a **newly started AI session**.

### 4. Hook it up over MCP (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<absolute path to this repo>/.repo/mcp_server.py"]
    }
  }
}
```

16 tools are exposed: `search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`, plus `search_films` `get_film` `get_film_layers` `get_film_stills`
for the film library and `search_shots` `get_shot` for the shot library.
The last few need Pillow / a CLIP model; when unavailable they explain why, and the
first seven are unaffected.

---

## Why it is different

### 1. Not an image pack - a composable structure

An image pack gives you "what this feels like"; this gives you "how to produce that
feeling". Every layer can be lifted out on its own: keep the style layer, swap the
subject, and you have a style-transfer template.

### 2. Lighting is pulled out as its own layer

Most people write prompts as one blended lump and tune by trial and error. This vault
states it plainly: **lighting affects the final texture more than the style words do.**
Each movement's lighting layer is a separate block you can move onto another subject.

### 3. Every axis has targeted negatives

Aimed at **this movement's** typical failure mode, not a generic negative list:

- Impressionism -> `black shadows, smooth blending, photorealistic`
- Renaissance -> `visible brushstrokes, impasto` (AI adds impasto to oils by default)
- Ukiyo-e -> `3d shading, cast shadows, gradient` (AI adds volume by default)

**Note that different movements' negatives often contradict each other** - which is
exactly why mixing fights, and exactly what this vault manages for you.

### 4. An AI can use it, not just look at it

LLMs remember art movements fuzzily and routinely confuse Art Nouveau with Art Deco,
or Barbizon with Impressionism. This vault pins down the concrete terminology so an
AI calling it will not make things up.

### 5. The terminology is pinned, not invented

The keyword atlas picks the **{n_concepts} most-confused concept groups** - avant-garde,
contemporary, postmodern, surreal. Each gets a definition, several "what it is not"
boundaries, and **{n_synonyms} synonyms**; searching any of them lands on the same card.

### 6. An image you already have can become a video prompt

The video prompts on the cards are **generic** - the subject line is a placeholder.
But what you usually want is "I have this image, make it move":

```bash
python3 i2v_prompt.py your-image.jpg --slug baroque
```

Shot size, position in frame, internal motion direction, whether the light should
move, whether the camera pushes or pans - all derived from **objective measurements
of that image** (face-based shot size / saliency centre / line direction / detail
density / light-dark structure), with a "derivation basis" sheet for you to check.
The output still leaves "who, doing what - add one line yourself": only the person
looking at the image knows that, and the script will not invent it.

### 7. The numbers are computed, not hard-coded

Every "how much is in this vault" number in the READMEs is computed by
`publish_stats()` against the **published view** (what git tracks, not what happens to
be on the author's machine) and then checked line by line by `verify_vault.py`.
The only thing a hard-coded number ever does is become wrong one day - this vault has
been burned by that, so the lock is in place.

---

## Three principles

1. **Rather less than wrong.**
   Curation deliberately refuses "broaden it a bit" - if a movement has one image,
   it has one image. The real danger for a reference library is not too few images
   but wrong ones: a wrong reference contaminates your intuition and you never find out.

2. **Lighting matters more than style words.**
   If you can only tune one layer, tune lighting.

3. **Do not invent movement terminology from memory.**
   LLM memory of art movements is fuzzy and conflates neighbouring schools.
   Trust the concrete terminology in the vault.

---

<details>
<summary><b>Expand the full skill tree ({n_mv} movements / {n_cats} categories)</b></summary>

{skill_tree_en}

</details>

---

## Contributors & sources

This vault exists because a number of people **chose to open their work up**. None of
the items below is a passing "we looked at it" - each was **taken in whole and
re-cut into the same card structure**:

| Source | What it contributed | License |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **{n_hn} hand-drawn styles** and their numbered reference sheets, forming category 7 | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **{n_shots} shot recipe cards** ({n_shot_cats} categories); this vault only categorises and formats them | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | The film still index; the representative frames embedded in cards remain the **copyright of the respective rights holders** | Site states: *images are not permitted for commercial use*. Personal study reference only |
| [Tate art terms](https://www.tate.org.uk/art/art-terms) | The glossary pages cited in each movement card's sources section - the seven layers trace back to authoritative definitions | Term text is **copyright Tate**; this vault **cites the source only** |
| [Cleveland Museum of Art](https://openaccess-api.clevelandart.org) · [Art Institute of Chicago](https://api.artic.edu/docs/) · [The Met](https://collectionapi.metmuseum.org) · [Wikimedia Commons](https://commons.wikimedia.org) | **{n_work_img} public-domain museum images** | **CC0 / public domain** |

**Three boundaries worth stating plainly**:

1. **The shot cards are not original to this vault.** Copyright in those
   {n_shots} technique descriptions belongs to the upstream project (Apache-2.0).
   This vault only categorises and formats them, and each card carries the upstream
   path and commit. The upstream project states that the motion techniques were
   studied from publicly released works, that **every implementation was rewritten
   from scratch** with no original footage, and that "publicly released" is
   **not** the same as "licensed". Do not use these cards to reproduce the
   recognisable overall audiovisual presentation of a specific work.
2. **Film stills remain the copyright of the respective rights holders.** The
   representative frames embedded in cards are for **personal study reference only**;
   film-grab states they may not be used commercially. Obtain permission before
   redistributing or using commercially.
3. **"Referenced artist / style names" are index labels** - not descriptions of the
   people themselves, and not an instruction to imitate. The numbered reference
   sheets are used for style only: do not carry over their subjects, compositions
   or text.

This vault's own parts (the seven-layer breakdown, card structure, CLI / MCP,
retrieval and composition logic) are released under MIT.

---

## License

- **Code and card text**: [MIT](LICENSE)
- **Public-domain images**: CC0 / public domain; source and license are stated in each card's sources section
- **handraw-style numbered reference sheets**: MIT (upstream)
- **Shot recipe cards**: Apache-2.0 (upstream); this vault only categorises and formats them
- **Film stills**: copyright of the respective rights holders; personal study reference only

---

<div align="center">

If this is useful, a star is appreciated - PRs adding more movements are welcome

</div>
"""


# ===================================================================== 日本語
README_JA = """<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="4 つの軸：画派・手描き・映画">

# 芸術美学スタイル庫

**「視覚スタイル」を、そのまま呼び出せるプロンプト層に分解する**

画派 · 手描き · 監督 · カメラワーク —— 4 つの軸、1 つの構造

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/{REPO_SLUG}?style=flat-square)](LICENSE)

`{n_mv} 流派` · `{n_hn} 手描きスタイル` · `{n_films} 本の映画` · `{n_shots} 枚のショットレシピ` · `{n_notes} 本のノート` · `{n_img} 枚の画像`

[中文](README.md) ｜ [English](README.en.md) ｜ [Français](README.fr.md) ｜ **日本語**

</div>

---

## これは何か

多くの人は「スタイルの参考」を画像を保存することで集めます。数百枚たまっても、
いざ使うときには何を見ればいいのか、どう言葉にすればいいのか分かりません。
画像は動きません。

この庫はやり方を変えます：**それぞれの視覚言語を、独立に差し替えられる 7 つの層に分解する。**

<img src="99-attachments/readme/layers.png" width="100%" alt="7 つの層：スタイル / ライティング / 色彩 / 構図 / 素材 / 情緒 / カメラ">

層に分けてはじめて、A の光を B の主体に載せられます。
**それこそが参考庫の本当の用途です。**

```bash
python3 artvault.py compose \\
  "雨のネオン街の賞金稼ぎ、バロックの光、サイバーパンクの構図" \\
  --subject "a female bounty hunter in a wet neon alley"
```

「バロック」の直後が「光」ならバロックのライティング層を、「サイバーパンク」なら
スタイル層と構図層を取ります。出力は層に分かれたポジティブプロンプト、ネガティブ
プロンプト、配色、動画層、そして**衝突解決の記録**です。

> **同じ主体のまま、どの層でも単独で差し替えられます。**
> これが「スタイル語の寄せ集め」との決定的な違いです。

---

## 4 つの軸

4 つの軸は同じカード構造と同じ 7 層の語彙を共有しているので、軸をまたいで
混ぜられます —— 映画の光 + 画派の配色 + 手描きの素材。

| | 軸 · 規模 | 何に答えるか |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="画派"> | **画派スタイル · {n_mv}**<br>（{n_cats} 大分類） | ビザンティンから Y2K まで、浮世絵からサイバーパンクまで。流派ごとに 1 枚：6 軸の視覚分解 + 7 層プロンプト + 6 色配色 + 専用ネガティブ + 動画層<br>`python3 artvault.py layers 巴洛克` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="手描き"> | **手描きスタイル · {n_hn}**<br>（A〜H の 8 群） | 絵本、風刺漫画、現代イラスト、国風……[handraw-style](https://github.com/yang0/handraw-style)（**MIT**）から丸ごと取り込み。カードは中国語名、上流の番号は別名として保持<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="監督と映画"> | **監督と映画 · {n_films}**<br>（{n_film_directors} 人の監督） | 「どんな見た目か」だけでなく「誰がどう撮ったか」。監督 → 映画の順に整理：代表フレーム + 6 軸分解 + 7 層プロンプト + 配色 + 動画層、さらに **{n_film_stills} 件のスチル外部リンク**（索引のみ、転載なし）<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="ショットレシピ"> | **ショットレシピ · {n_shots}**<br>（{n_shot_cats} 類） | 最初の 3 軸は「どんな見た目か」に答えます。この軸は「**その動きをどう作るか**」に答えます。フレーム数・イージング・振幅をパラメータ表にし、既知の落とし穴を添えます。[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（**Apache-2.0**、本庫は分類と整形のみ）<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **ショットカードに色彩・ライティング欄が無いのは意図的です。** 扱うのは
> フレーム数とイージング（`zoom 6f ease-in、1→2.6`）で、7 層に当てはめるには
> 創作するしかありません。だから独自の 4 項目で並べ、**`compose` の層解決には
> あえて参加しません** —— この境界はテストで守っています。

---

## 規模

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="収録されている画派・手描き・映画の例">

| | 数 |
|---|---|
| **流派カード** | **{n_mv} 枚**（{n_cats} 大分類）。各カードに 6 軸の視覚分解 + 7 層プロンプト + 配色 + 動画層 |
| **実画像** | **{n_img} 枚**（{img_mb} MB）：パブリックドメイン実画像 **{n_work_img} 枚** + handraw-style 番号参考図 **{n_ref_img} 枚**（MIT）。{n_mv_with_img} 流派に画像あり |
| **手描きカードの中国語名** | **{n_hn_named} / {n_hn}** に命名済み（うち {n_hn_traits} 枚は `traits` からの逐語抽出、{n_hn_gen} 枚は `traits` が空のため英語生成名からの逆訳） |
| **ガイドと方法論** | {n_guides} 本（流派総覧、キーワード図譜、7 層の方法、動画構造、配色早見…） |
| **キーワード図譜** | 最も混同しやすい **{n_concepts} 組**の概念、**{n_synonyms} 個**の同義表現。どれで検索しても同じカードに着地 |
| **映画スタイルカード** | **{n_films} 本**（{n_film_directors} 人の監督）：監督 → 映画の順に整理。各カードにスチル索引 + 6 軸分解 + 7 層プロンプト + 配色 + 動画層、さらに **{n_film_stills} 件のスチル外部リンク**（索引のみ、転載なし） |
| **ショットレシピカード** | **{n_shots} 枚**（{n_shot_cats} 類）：カメラワークとモーションの技、パラメータ表（フレーム/イージング/振幅）と既知の落とし穴付き。[{shot_source}](https://github.com/{shot_source}) より、**Apache-2.0、本庫は分類と整形のみ** |
| **ノートテンプレート** | {n_templates} 個 |
| **スクリプト** | {n_scripts} 本（取得・生成・検索・プロンプト合成・MCP サーバー） |

> **{n_mv_no_img} 流派は「プロンプトのみのカード」です。** 抽象表現主義、ポップアート、
> ミニマリズム、概念芸術、サイバーパンク、ヴェイパーウェイヴ —— これらは自由に
> 再配布できる実画像がほとんど存在しません。視覚言語と 7 層は通常どおり分解し、
> 画像だけを付けていません。これは意図した設計で、欠落ではありません。

---

## 使い方

### 1. Obsidian の保管庫として読む

このフォルダを Obsidian で開きます。次の順で入るのがおすすめです：

1. `00-guides/提示词拆解方法.md` —— **まずこれ**。7 層の仕組みを理解する
2. `00-guides/流派总览.md` —— 全流派の総合入口
3. `10-movements/` —— 好きな流派を選び、完全な分解を読む
4. `00-guides/关键词图谱.md` —— 未知のスタイル用語を後で引く

### 2. AI に直接呼ばせる

本庫は人向けの Markdown だけでなく、**機械向けのインターフェース**も持ちます：

```bash
cd .repo

python3 artvault.py categories              # {n_cats} 大分類
python3 artvault.py search "ネオン 雨夜"      # あいまい検索（中国語・英語）
python3 artvault.py search "抑圧的だが華麗な光" --semantic
python3 artvault.py layers 巴洛克            # 7 層だけ（最もトークンが少ない）
python3 artvault.py show 浮世絵              # カード全体
python3 artvault.py palette 赛博朋克         # 6 色の配色
python3 artvault.py related 立体主义         # 近い流派を探す

python3 artvault.py film list               # {n_films} 本の映画
python3 artvault.py shots search "急推 衝撃"  # 「何をしたいか」から技を探す

python3 artvault.py --json layers 巴洛克     # 機械可読
```

**中核は組み合わせです**：

```bash
# 自然言語、自動で層に分ける
python3 artvault.py compose "雨のネオンの賞金稼ぎ、バロックの光" --subject "a bounty hunter"

# 明示指定、時代をまたぐ
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
  --color vaporwave --composition precisionism --subject "a lone samurai"

# 軸をまたぐ：映画の光 + 画派の配色
python3 artvault.py compose --lighting villeneuve-dune --color baroque \\
  --subject "a lone figure on a dune"
```

**層の衝突は自動で解決します。** 流派を混ぜるとネガティブ語がぶつかります ——
浮世絵は `cast shadows` を禁じ、バロックの光は `deep crushed shadows` を要求する。
精度主義は `people` を禁じるのに、主体は人物である。
**モデルはエラーを出しません**。ただ「なぜか出図が悪い」という、極めて
原因を追いにくい形で現れます。そこでぶつかったネガティブ語は**ネガティブ
プロンプトから自動的に外し**、「自動解決した衝突」に何を外し、何に譲ったかを
一行ずつ書きます。規則は一行で：**ポジティブは意図、ネガティブはガードレール、
ガードレールは意図に譲る。** 生の合算を自分で判断したいときは `--keep-conflicts`。

### 3. AI skill として入れる（推奨）

リポジトリには skill が 2 つ付属します。入れると、**skill に対応した任意の AI
アシスタント**が視覚・美的なタスクで本庫を参照するようになり、記憶から流派用語を
でっち上げなくなります。

```bash
cd .repo/skill && ./install.sh
```

| skill | 役割 | 発動するとき |
|---|---|---|
| `art-aesthetic-vault` | 庫を**使う**：流派検索、7 層の取得、流派をまたいだ合成 | 「このキャラはどのスタイル？」と聞いたとき |
| `build-art-aesthetic-vault` | 庫を**作る**：ゼロから 1 セット構築 | 「同じような庫が欲しい」と言ったとき |

> [!note] なぜ skill がデータを同梱しないのか
> どちらも本リポジトリへの**シンボリックリンク**です —— データはリポジトリの
> 1 部だけ。`mv_*.py`（流派定義）を skill に梱包すると 2 部になり、必ず分岐します。
> 実測済み：梱包版は 4 ファイルがリポジトリと同期しておらず、それで作った庫は
> 分類が誤っていました。

見つかった skill ディレクトリすべてにリンクを作ります：

| ディレクトリ | 読むもの |
|---|---|
| `~/.agents/skills/` | DSH / Codex / 汎用規約 |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**なぜシンボリックリンクか**：skill は `pwd -P` で自身の実体位置を解決し、そこから
リポジトリ根を推定できます —— **リポジトリがどこにあり、移動しても自動で見つかり**、
設定は一切不要です。

```bash
.repo/skill/install.sh --copy        # コピーで導入（移動したら再導入が必要）
.repo/skill/install.sh --uninstall   # アンインストール
bash .repo/skill/locate.sh           # 手動でリポジトリを特定（調査用）
```

反映されるのは**新しく開始した AI セッション**です。

### 4. MCP で接続（Claude Desktop / Cursor）

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<本リポジトリの絶対パス>/.repo/mcp_server.py"]
    }
  }
}
```

16 個のツールを公開します：`search_movements` `get_movement` `get_layers`
`compose_prompt` `get_palette` `find_related` `list_categories` `analyze_image`
`match_movement` `get_video_prompt`、映画庫から `search_films` `get_film`
`get_film_layers` `get_film_stills`、ショット庫から `search_shots` `get_shot`。
後半のいくつかは Pillow / CLIP モデルが必要です。条件が満たされない場合は理由を
説明し、前半の 7 つには影響しません。

---

## 何が違うのか

### 1. 画像パックではなく、組み合わせ可能な構造

画像パックは「どんな感じか」を渡します。本庫は「どうやってその感じを作るか」を渡します。
どの層も単独で取り出して再利用できます。主体を替えてスタイル層を残せば、
それはスタイル転写のテンプレートです。

### 2. ライティングが独立した層になっている

多くの人はプロンプトをひと塊で書き、試行錯誤で調整します。本庫は明言します：
**最終的な質感に効くのは、スタイル語そのものより光である。**
各流派のライティング層は独立した一区切りで、他の主題にそのまま載せられます。

### 3. 軸ごとに「専用のネガティブ語」がある

**その流派**の典型的な失敗に狙いを定めたもので、汎用のネガティブ一覧ではありません：

- 印象派 → `black shadows, smooth blending, photorealistic`
- ルネサンス → `visible brushstrokes, impasto`（AI は油彩に厚塗りを足しがち）
- 浮世絵 → `3d shading, cast shadows, gradient`（AI は立体感を足しがち）

**流派が違えばネガティブ語はしばしば正反対**です —— だから混ぜるとぶつかり、
本庫がそれを管理します。

### 4. AI が使える。人が眺めるだけではない

大規模言語モデルの芸術流派の記憶は曖昧で、アール・ヌーヴォーとアール・デコ、
バルビゾン派と印象派をよく混同します。本庫は流派ごとの具体用語を固定するので、
AI が呼び出しても作り話をしません。

### 5. 用語は打ち込まれている。でっち上げではない

キーワード図譜は最も混同しやすい **{n_concepts} 組** —— 前衛、現代、ポストモダン、
シュルレアリスム —— を選びます。各組に定義 1 つ、「それは何ではないか」という
境界をいくつか、そして **{n_synonyms} 個**の同義表現。どれで検索しても同じカードに
着地します。

### 6. 手元の 1 枚も、そのまま動画プロンプトになる

カード上の動画プロンプトは**汎用**で、主体の行はプレースホルダです。しかし実際に
やりたいのは「この画像を動かす」ことでしょう：

```bash
python3 i2v_prompt.py あなたの画像.jpg --slug baroque
```

主体のショットサイズ、画面内の位置、画面内の運動方向、光を動かすか、カメラを
押すか流すか —— すべて**その画像の客観測定**（顔によるショットサイズ / 顕著性
中心 / 線の方向 / 細部密度 / 明暗構造）から導き、「導出根拠」を添えて検証できる
ようにします。それでも「誰が、何をしているかは一言だけ自分で補ってください」
は残します —— 見ている人だけが知っていることで、スクリプトは代わりに作りません。

### 7. 数字は現算。書き込みではない

README にある「本庫に何がどれだけあるか」という数字はすべて、`publish_stats()` が
**公開ビュー**（作者のマシンにあるものではなく、git が追跡しているもの）に対して
現算し、`verify_vault.py` が一行ずつ照合します。書き込んだ数字の唯一の効能は、
いつか間違いになることです —— 本庫はそれで痛い目を見たので、錠をかけました。

---

## 3 つの原則

1. **少なさより、誤りの無さ。**
   選定では意図的に「少し緩めて足す」をしません —— 画像が 1 枚の流派は 1 枚のままです。
   参考庫の本当の敵は画像の少なさではなく、誤った画像です。誤った参考は直感を汚し、
   しかも自分では気づけません。

2. **スタイル語より光。**
   調整できる層が 1 つだけなら、光を調整する。

3. **記憶から流派用語をでっち上げない。**
   大規模言語モデルの流派の記憶は曖昧で、近い画派を混同します。庫の具体用語に従う。

---

<details>
<summary><b>完全なスキルツリーを開く（{n_mv} 流派 / {n_cats} 大分類）</b></summary>

{skill_tree_en}

</details>

---

## クレジットと出典

この庫が成り立つのは、**成果を開いてくれた人たち**がいるからです。以下のどれも
「参考にした」程度のものではなく、**丸ごと取り込み、同じカード構造に組み直した**
ものです：

| 出典 | 提供したもの | ライセンス |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **{n_hn} 個の手描きスタイル**と番号参考図。第 7 大分類を構成 | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **{n_shots} 枚のショットレシピカード**（{n_shot_cats} 類）。本庫は分類と整形のみ | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | 映画スチルの索引。カードに埋め込んだ代表フレームの**著作権は各権利者に帰属** | サイト明記：*images are not permitted for commercial use*。個人の研究参考のみ |
| [Tate 芸術用語集](https://www.tate.org.uk/art/art-terms) | 各流派カードの「出典」節に挙げた用語定義ページ。7 層の記述は権威ある定義に遡れる | 用語の**著作権は Tate** に帰属。本庫は**出典として引用するのみ** |
| [クリーブランド美術館](https://openaccess-api.clevelandart.org) · [シカゴ美術館](https://api.artic.edu/docs/) · [メトロポリタン美術館](https://collectionapi.metmuseum.org) · [ウィキメディア・コモンズ](https://commons.wikimedia.org) | **{n_work_img} 枚のパブリックドメイン実画像** | **CC0 / パブリックドメイン** |

**はっきり書いておくべき 3 つの境界**：

1. **ショットカードは本庫のオリジナルではありません。** その {n_shots} 枚の技法
   記述の著作権は上流（Apache-2.0）に帰属します。本庫は分類と整形のみを行い、
   各カードに上流のパスと commit を記載しています。上流自身が明記しています：
   モーション手法は公開作品から研究したが、**実装はすべてゼロから書き直し**、
   原盤素材を一切含まない。そして「公開されていること」は**許諾とは違う**。
   特定作品の識別可能な全体の視聴覚的提示を再現するためにこれらのカードを
   使わないでください。
2. **映画スチルの著作権は各権利者に帰属します。** カードに埋め込んだ代表フレームは
   **個人の研究参考のみ**です。film-grab は商用利用不可と明記しています。再配布や
   商用の前にご自身で許諾を得てください。
3. **「参考作者 / スタイル名」は索引ラベルです** —— 作者本人の説明でも、模倣の
   指示でもありません。番号参考図は画風のみを取ります。図中の主体・構図・文字を
   一緒に持ってこないでください。

本庫自身の部分（7 層の分解、カード構造、CLI / MCP、検索と合成のロジック）は
MIT で公開します。

---

## ライセンス

- **コードとカード本文**：[MIT](LICENSE)
- **パブリックドメイン実画像**：CC0 / パブリックドメイン。出典とライセンスは各カードの「出典」節に記載
- **handraw-style 番号参考図**：MIT（上流）
- **ショットレシピカード**：Apache-2.0（上流）。本庫は分類と整形のみ
- **映画スチル**：著作権は各権利者に帰属。個人の研究参考のみ

---

<div align="center">

このライブラリが役に立ったら、Star ⭐ や PR での流派追加を歓迎します

</div>
"""


# ===================================================================== Français
README_FR = """<div align="center">

<img src="99-attachments/readme/hero.jpg" width="100%" alt="Quatre axes : mouvements, dessin, cinéma">

# Bibliothèque d'esthétique artistique

**Le style visuel, décomposé en couches de prompt réellement appelables**

Mouvements · Dessin · Réalisateurs · Mouvements de caméra — quatre axes, une structure

[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-dsh--plugin-4D6BFE?style=flat-square)](https://github.com/deepseek-ai/deepseek-harness)
[![Agent Skill](https://img.shields.io/badge/Agent-Skill-7C3AED?style=flat-square)](.repo/skill)
[![License](https://img.shields.io/github/license/{REPO_SLUG}?style=flat-square)](LICENSE)

`{n_mv} mouvements` · `{n_hn} styles dessinés` · `{n_films} films` · `{n_shots} recettes de plan` · `{n_notes} notes` · `{n_img} images`

[中文](README.md) ｜ [English](README.en.md) ｜ [日本語](README.ja.md) ｜ **Français**

</div>

---

## Qu'est-ce que c'est

La plupart des gens collectionnent les références de style en enregistrant des images.
On finit avec quelques centaines de fichiers et aucune idée de quoi regarder ni de
comment le décrire. Les images ne servent à rien toutes seules.

Cette bibliothèque fait autrement : **elle décompose chaque langage visuel en sept
couches remplaçables indépendamment.**

<img src="99-attachments/readme/layers.png" width="100%" alt="Sept couches : style / lumière / couleur / composition / matière / ambiance / caméra">

Une fois découpé en couches, vous pouvez poser la lumière de l'image A sur le sujet
de l'image B. **C'est là tout l'intérêt d'une bibliothèque de références.**

```bash
python3 artvault.py compose \\
  "un chasseur de primes dans une rue néon sous la pluie, lumière baroque, cadrage cyberpunk" \\
  --subject "a female bounty hunter in a wet neon alley"
```

L'outil lit l'intention derrière chaque groupe de mots (« baroque » suivi de
« lumière » prend la couche lumière du baroque), puis produit des prompts positifs
en couches, des prompts négatifs, une palette, une couche vidéo et un
**journal de résolution des conflits**.

> **Même sujet, chaque couche interchangeable.** C'est la différence avec un simple
> tas de mots-clés de style.

---

## Quatre axes

Les quatre axes partagent la même structure de fiche et le même vocabulaire de sept
couches : on peut donc les mélanger — la lumière d'un film + la palette d'un
mouvement + la matière d'un dessin.

| | Axe · ampleur | À quoi cela répond |
|---|---|---|
| <img src="99-attachments/readme/axis-1-movements.jpg" width="300" alt="Mouvements artistiques"> | **Mouvements · {n_mv}**<br>（{n_cats} catégories） | De Byzance à Y2K, de l'ukiyo-e au cyberpunk. Une fiche par mouvement : analyse visuelle en 6 axes + 7 couches de prompt + palette de 6 couleurs + négatifs ciblés + couche vidéo<br>`python3 artvault.py layers 巴洛克` |
| <img src="99-attachments/readme/axis-2-handraw.jpg" width="300" alt="Styles dessinés"> | **Styles dessinés · {n_hn}**<br>（groupes A à H） | Albums, caricature de presse, illustration contemporaine, guofeng… issus de [handraw-style](https://github.com/yang0/handraw-style) (**MIT**), intégrés en entier. Les fiches sont nommées en chinois, le numéro d'origine restant un alias<br>`python3 artvault.py layers 极端比例弯曲绘本` |
| <img src="99-attachments/readme/axis-3-films.jpg" width="300" alt="Réalisateurs et films"> | **Réalisateurs et films · {n_films}**<br>（{n_film_directors} réalisateurs） | Pas seulement « à quoi ça ressemble » mais « qui l'a filmé et comment ». Organisé réalisateur puis film : images représentatives + analyse en 6 axes + 7 couches + palette + couche vidéo, plus **{n_film_stills} liens externes vers des photogrammes** (indexés, jamais réhébergés)<br>`python3 artvault.py film show dune` |
| <img src="99-attachments/readme/axis-4-shots.jpg" width="300" alt="Recettes de plan"> | **Recettes de plan · {n_shots}**<br>（{n_shot_cats} catégories） | Les trois premiers axes répondent à « à quoi ça ressemble » ; celui-ci répond à « **comment produire ce mouvement** ». Images, easing et amplitude en tableaux de paramètres, avec les pièges connus. Issu de [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) (**Apache-2.0** — cette bibliothèque ne fait que classer et mettre en forme)<br>`python3 artvault.py shots show crash-zoom-punch` |

> ⚠ **Les fiches de plan n'ont volontairement ni couleur ni lumière.** Elles parlent
> de nombres d'images et d'easing (`zoom 6f ease-in, 1 à 2.6`) ; les forcer dans les
> sept couches reviendrait à inventer du contenu. Elles portent donc leurs propres
> quatre champs et **restent hors de la résolution de couches de `compose`** —
> un test garde cette frontière.

---

## En un coup d'œil

<img src="99-attachments/readme/gallery.jpg" width="100%" alt="Exemples de mouvements, de dessins et de films présents">

| | |
|---|---|
| **Fiches de mouvement** | **{n_mv} fiches**, en {n_cats} catégories. Chacune : analyse visuelle en 6 axes, 7 couches de prompt, palette de 6 couleurs, couche vidéo et pièges connus |
| **Images** | **{n_img}** ({img_mb} Mo) = **{n_work_img}** images de musée du domaine public + **{n_ref_img}** planches numérotées handraw-style (MIT) ; couvrant {n_mv_with_img} mouvements |
| **Noms des fiches dessinées** | **{n_hn_named} / {n_hn}** nommées ({n_hn_traits} tirées mot pour mot des `traits` ; {n_hn_gen} rétro-traduites du nom de génération anglais quand `traits` est vide) |
| **Guides et méthode** | {n_guides} notes (vue d'ensemble, atlas de mots-clés, la méthode des 7 couches, structure vidéo, index des palettes…) |
| **Atlas de mots-clés** | Les **{n_concepts} groupes de concepts les plus confondus**, **{n_synonyms} synonymes** au total — cherchez n'importe lequel et vous arrivez sur la même fiche |
| **Fiches de film** | **{n_films} fiches** ({n_film_directors} réalisateurs), organisées réalisateur puis film : index de photogrammes + analyse en 6 axes + 7 couches + palette + couche vidéo, plus **{n_film_stills} liens externes** (indexés, jamais réhébergés) |
| **Fiches de plan** | **{n_shots} fiches** ({n_shot_cats} catégories) : mouvements de caméra et effets avec tableaux de paramètres (images/easing/amplitude) et pièges connus. Depuis [{shot_source}](https://github.com/{shot_source}), **Apache-2.0 — cette bibliothèque ne fait que classer et mettre en forme** |
| **Modèles de note** | {n_templates} |
| **Scripts** | {n_scripts} — récupération, génération, recherche, composition, serveur MCP |

> **{n_mv_no_img} mouvements sont des « fiches prompt seul ».** Expressionnisme abstrait,
> pop art, minimalisme, art conceptuel, cyberpunk, vaporwave : il n'existe
> pratiquement pas d'images librement rediffusables pour ceux-là. Leur langage visuel
> et leurs sept couches sont analysés normalement ; ils n'ont simplement pas d'image.
> C'est un choix délibéré, pas une lacune.

---

## Comment l'utiliser

### 1. Le lire comme un coffre Obsidian

Ouvrez ce dossier dans Obsidian. Un bon ordre de parcours :

1. `00-guides/提示词拆解方法.md` — **commencez ici** pour comprendre les sept couches
2. `00-guides/流派总览.md` — l'index général de tous les mouvements
3. `10-movements/` — choisissez un mouvement et lisez son analyse complète
4. `00-guides/关键词图谱.md` — pour chercher plus tard un terme inconnu

### 2. Laisser une IA l'appeler

Ce n'est pas seulement du Markdown pour humains ; il y a une **interface pour la machine** :

```bash
cd .repo

python3 artvault.py categories              # les {n_cats} catégories
python3 artvault.py search "néon pluie"     # recherche floue, chinois ou anglais
python3 artvault.py search "lumière oppressante mais somptueuse" --semantic
python3 artvault.py layers baroque          # seulement les sept couches (le moins de tokens)
python3 artvault.py show ukiyo-e            # la fiche complète
python3 artvault.py palette cyberpunk       # la palette de six couleurs
python3 artvault.py related cubism          # mouvements voisins

python3 artvault.py film list               # {n_films} films
python3 artvault.py shots search "crash zoom punch"

python3 artvault.py --json layers baroque   # lisible par machine
```

**La composition est la capacité centrale** :

```bash
# langage naturel, découpage automatique en couches
python3 artvault.py compose "un chasseur de primes sous le néon, lumière baroque" \\
  --subject "a bounty hunter"

# explicite, en mélangeant les époques
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
  --color vaporwave --composition precisionism --subject "a lone samurai"

# entre axes : la lumière d'un film + la palette d'un mouvement
python3 artvault.py compose --lighting villeneuve-dune --color baroque \\
  --subject "a lone figure on a dune"
```

L'outil **résout automatiquement les conflits de couches**. En mélangeant des
mouvements, leurs prompts négatifs se contredisent — l'ukiyo-e interdit
`cast shadows`, la lumière baroque exige `deep crushed shadows` ; le précisionnisme
interdit `people` alors que votre sujet *est* une personne.
**Le modèle ne renvoie pas d'erreur** ; vous obtenez seulement des « images
bizarrement mauvaises », ce qui est extrêmement difficile à diagnostiquer. Les
négatifs en conflit sont donc **retirés du prompt négatif** et listés un par un sous
« conflits résolus automatiquement », en indiquant ce qui a été retiré et à quoi il
a cédé. La règle en une ligne : **les positifs sont l'intention, les négatifs sont
des garde-fous, et les garde-fous cèdent devant l'intention.** Ajoutez
`--keep-conflicts` pour voir l'union brute et juger vous-même.

### 3. L'installer comme skill d'IA (recommandé)

Le dépôt fournit deux skills. Une fois installés, **tout assistant IA compatible**
consultera cette bibliothèque pour les tâches visuelles ou esthétiques au lieu
d'inventer de la terminologie de mémoire.

```bash
cd .repo/skill && ./install.sh
```

| skill | Rôle | Se déclenche quand |
|---|---|---|
| `art-aesthetic-vault` | **Utiliser** la bibliothèque : chercher un mouvement, extraire les sept couches, composer | Vous demandez « quel style pour ce personnage ? » |
| `build-art-aesthetic-vault` | **Construire** une bibliothèque de zéro | Vous dites « je veux la même chose » |

> [!note] Pourquoi aucun skill n'embarque les données
> Les deux sont des **liens symboliques** vers ce dépôt — il n'y a qu'une seule copie
> des données. Si `mv_*.py` (les définitions de mouvements) étaient empaquetés dans
> le skill, il y aurait deux copies et elles divergeraient forcément. Testé : la
> version empaquetée avait 4 fichiers désynchronisés, et les bibliothèques
> construites avec elle avaient de mauvaises catégories.

Il crée les liens dans tous les répertoires de skills trouvés :

| Répertoire | Lu par |
|---|---|
| `~/.agents/skills/` | DSH / Codex / convention générale |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Pourquoi des liens symboliques** : le skill résout sa propre position réelle avec
`pwd -P` et en déduit la racine du dépôt — **où qu'il soit, et même déplacé, il est
retrouvé automatiquement**, sans aucune configuration.

```bash
.repo/skill/install.sh --copy        # installer par copie (à refaire si le dépôt bouge)
.repo/skill/install.sh --uninstall
bash .repo/skill/locate.sh           # localiser le dépôt manuellement (diagnostic)
```

Les skills prennent effet dans une **nouvelle session d'IA**.

### 4. Le brancher en MCP (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<chemin absolu de ce dépôt>/.repo/mcp_server.py"]
    }
  }
}
```

16 outils sont exposés : `search_movements` `get_movement` `get_layers`
`compose_prompt` `get_palette` `find_related` `list_categories` `analyze_image`
`match_movement` `get_video_prompt`, plus `search_films` `get_film`
`get_film_layers` `get_film_stills` pour la filmothèque et `search_shots` `get_shot`
pour les plans. Les derniers demandent Pillow / un modèle CLIP ; en leur absence ils
expliquent pourquoi, sans affecter les sept premiers.

---

## Ce qui le distingue

### 1. Pas un pack d'images — une structure composable

Un pack d'images vous donne « l'effet que ça fait » ; ceci vous donne « comment
produire cet effet ». Chaque couche se retire seule : gardez la couche style,
changez le sujet, vous avez un modèle de transfert de style.

### 2. La lumière est une couche à part entière

La plupart des gens écrivent leurs prompts en un bloc et ajustent par essais-erreurs.
Cette bibliothèque l'affirme : **la lumière pèse plus sur le rendu final que les mots
de style.** La couche lumière de chaque mouvement est un bloc séparé, déplaçable sur
un autre sujet.

### 3. Chaque axe a des négatifs ciblés

Visant le mode d'échec **de ce mouvement précis**, pas une liste négative générique :

- Impressionnisme → `black shadows, smooth blending, photorealistic`
- Renaissance → `visible brushstrokes, impasto` (l'IA ajoute de l'empâtement aux huiles)
- Ukiyo-e → `3d shading, cast shadows, gradient` (l'IA ajoute du volume)

**Notez que les négatifs de mouvements différents se contredisent souvent** — c'est
exactement pourquoi les mélanges se battent, et exactement ce que cette bibliothèque
gère pour vous.

### 4. Une IA peut l'utiliser, pas seulement le regarder

Les grands modèles se souviennent vaguement des mouvements artistiques et confondent
régulièrement Art nouveau et Art déco, ou Barbizon et impressionnisme. Cette
bibliothèque fixe la terminologie concrète : une IA qui l'appelle n'inventera rien.

### 5. La terminologie est fixée, pas inventée

L'atlas de mots-clés retient les **{n_concepts} groupes de concepts les plus
confondus** — avant-garde, contemporain, postmoderne, surréaliste. Chacun reçoit une
définition, plusieurs limites « ce que ce n'est pas », et **{n_synonyms} synonymes** ;
chercher l'un d'eux mène à la même fiche.

### 6. Une image que vous avez déjà peut devenir un prompt vidéo

Les prompts vidéo des fiches sont **génériques** — la ligne du sujet est un
emplacement réservé. Mais ce que vous voulez vraiment, c'est « j'ai cette image,
fais-la bouger » :

```bash
python3 i2v_prompt.py votre-image.jpg --slug baroque
```

Taille de plan, position dans le cadre, direction du mouvement interne, faut-il
animer la lumière, la caméra avance-t-elle ou panoramique-t-elle : tout est dérivé de
**mesures objectives de cette image** (taille de plan par détection de visage / centre
de saillance / direction des lignes / densité de détail / structure clair-obscur),
avec une fiche « base de dérivation » à vérifier. La sortie laisse toujours
« qui, faisant quoi — ajoutez une ligne vous-même » : seul celui qui regarde l'image
le sait, et le script ne l'inventera pas.

### 7. Les chiffres sont calculés, pas écrits en dur

Chaque chiffre « combien y a-t-il dans cette bibliothèque » est calculé par
`publish_stats()` sur la **vue publiée** (ce que git suit, pas ce qui traîne sur la
machine de l'auteur), puis vérifié ligne par ligne par `verify_vault.py`. La seule
chose qu'un chiffre écrit en dur finit toujours par faire, c'est devenir faux —
cette bibliothèque en a fait l'expérience, donc le verrou est là.

---

## Trois principes

1. **Plutôt moins que faux.**
   La sélection refuse délibérément le « élargissons un peu » — si un mouvement n'a
   qu'une image, il en a une. Le vrai danger d'une bibliothèque de références n'est
   pas le manque d'images mais les mauvaises : une mauvaise référence contamine votre
   intuition et vous ne le découvrez jamais.

2. **La lumière compte plus que les mots de style.**
   Si vous ne pouvez régler qu'une couche, réglez la lumière.

3. **N'inventez pas la terminologie de mémoire.**
   La mémoire des grands modèles est floue et confond les écoles voisines.
   Fiez-vous à la terminologie concrète de la bibliothèque.

---

<details>
<summary><b>Déplier l'arbre complet ({n_mv} mouvements / {n_cats} catégories)</b></summary>

{skill_tree_en}

</details>

---

## Crédits et sources

Cette bibliothèque existe parce que des personnes **ont choisi d'ouvrir leur
travail**. Aucun des éléments ci-dessous n'est un simple « nous l'avons consulté » :
chacun a été **repris en entier et redécoupé dans la même structure de fiche** :

| Source | Apport | Licence |
|---|---|---|
| [yang0/handraw-style](https://github.com/yang0/handraw-style) | **{n_hn} styles dessinés** et leurs planches numérotées, formant la 7e catégorie | **MIT** |
| [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | **{n_shots} fiches de recette de plan** ({n_shot_cats} catégories) ; cette bibliothèque ne fait que classer et mettre en forme | **Apache-2.0** |
| [film-grab.com](https://film-grab.com/) | L'index de photogrammes de films ; les images représentatives intégrées aux fiches restent la **propriété de leurs ayants droit** | Le site indique : *images are not permitted for commercial use*. Référence d'étude personnelle uniquement |
| [Glossaire Tate](https://www.tate.org.uk/art/art-terms) | Les pages de définition citées dans la section « sources » de chaque fiche — les sept couches remontent à des définitions faisant autorité | Le texte des termes est **copyright Tate** ; cette bibliothèque ne fait que **citer la source** |
| [Cleveland Museum of Art](https://openaccess-api.clevelandart.org) · [Art Institute of Chicago](https://api.artic.edu/docs/) · [Metropolitan Museum](https://collectionapi.metmuseum.org) · [Wikimedia Commons](https://commons.wikimedia.org) | **{n_work_img} images de musée du domaine public** | **CC0 / domaine public** |

**Trois limites à énoncer clairement** :

1. **Les fiches de plan ne sont pas originales.** Le droit d'auteur sur ces
   {n_shots} descriptions de techniques appartient au projet amont (Apache-2.0).
   Cette bibliothèque ne fait que les classer et les mettre en forme, et chaque fiche
   porte le chemin et le commit amont. L'amont précise que les techniques de mouvement
   ont été étudiées à partir d'œuvres publiques, que **toute implémentation a été
   réécrite de zéro** sans aucune image d'origine, et que « publié » **n'est pas**
   synonyme de « sous licence ». N'utilisez pas ces fiches pour reproduire la
   présentation audiovisuelle globale et reconnaissable d'une œuvre précise.
2. **Les photogrammes restent la propriété de leurs ayants droit.** Les images
   intégrées aux fiches sont destinées à la **référence d'étude personnelle** ;
   film-grab précise qu'elles ne peuvent pas être utilisées commercialement. Obtenez
   une autorisation avant toute rediffusion ou usage commercial.
3. **Les « noms d'artistes / styles référencés » sont des étiquettes d'index** — ni
   des descriptions des personnes, ni une consigne d'imitation. Les planches
   numérotées ne servent qu'au style : n'en reprenez ni les sujets, ni les
   compositions, ni les textes.

Les parties propres à cette bibliothèque (décomposition en sept couches, structure
des fiches, CLI / MCP, logique de recherche et de composition) sont publiées sous MIT.

---

## Licence

- **Code et texte des fiches** : [MIT](LICENSE)
- **Images du domaine public** : CC0 / domaine public ; source et licence indiquées dans la section « sources » de chaque fiche
- **Planches numérotées handraw-style** : MIT (amont)
- **Fiches de recette de plan** : Apache-2.0 (amont) ; cette bibliothèque ne fait que classer et mettre en forme
- **Photogrammes de films** : propriété de leurs ayants droit ; référence d'étude personnelle uniquement

---

<div align="center">

Si cela vous est utile, une étoile ⭐ fait plaisir — les PR ajoutant des mouvements sont bienvenues

</div>
"""
