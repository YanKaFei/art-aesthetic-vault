---
name: "art-aesthetic-vault"
description: "艺术审美风格库：141 个艺术流派的视觉语言与可复用提示词层。角色造型、服装气质、场景氛围、插画/概念图/AI 绘画与视频提示词、配色与光影方案、风格辨认——凡涉及视觉审美方向的任务，先查这个库，不要凭记忆编造流派术语。"
metadata:
  short-description: "查 141 个艺术流派的七层提示词，可跨流派组合"
---

# 艺术审美风格库

一个 Obsidian 知识库，把 **141 个艺术流派**的视觉语言拆成七层可复用的提示词层。
覆盖拜占庭到 Y2K，含东亚 / 南亚 / 伊斯兰、摄影谱系、数字亚文化。

**提示词层本身就是英文的**，可直接粘进模型；中文只用于解释。

## 第一步：定位仓库

仓库位置因机器而异，先运行：

```bash
bash <本skill目录>/locate.sh
```

输出即仓库根目录（记为 `$VAULT`）。找不到就用 `find ~ -name artvault.py -path '*/.repo/*'` 搜，
或直接问用户仓库在哪。**不要猜路径。**

## 何时使用

任务涉及以下任一项，**先查库再回答**：

- 角色造型、服装、气质、人设的视觉方向
- 场景、氛围、环境设计
- 插画 / 概念图 / AI 绘画 / AI 视频的提示词
- 配色方案、光影方案、材质方案
- 「这个风格叫什么」「怎么做出这种感觉」
- 用户提到任何画风、流派、艺术家、视觉风格

## 怎么查

```bash
cd "$VAULT/.repo"

python3 artvault.py categories            # 6 大分类 141 流派
python3 artvault.py search "霓虹 雨夜"     # 模糊检索，中英文皆可
python3 artvault.py layers 巴洛克          # 七层提示词 ← 优先用这个，最省 token
python3 artvault.py show 浮世绘            # 完整卡片（内容多，只在需要时用）
python3 artvault.py palette 赛博朋克       # 六色配色
python3 artvault.py related 立体主义       # 关联流派
python3 artvault.py --json layers 巴洛克   # 机器可读
```

**省 token 的要点**：先用 `search` 找 slug，再只取需要的层。
不要一上来 `show` 整个卡片——每张卡约 5KB。

## 核心用法：跨流派组合提示词

```bash
python3 artvault.py compose \
  "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \
  --subject "a female bounty hunter in a wet neon alley"
```

自然语言里带意图词（"…的光照" / "…的构图" / "…的配色"）时，会自动把对应流派
分配到对应层。也可显式指定：

```bash
python3 artvault.py compose --style ukiyo-e --lighting baroque \
  --color vaporwave --composition precisionism --subject "a lone samurai"
```

返回：分层结果 + 正向 + 负向 + 配色 + 视频层 + **已自动消解的冲突**。

> **冲突已经自动处理，但你要转述。** 跨流派混搭时负向词会互相打架：
> 浮世绘禁止 `cast shadows`，巴洛克光照却要 `deep crushed shadows`；
> 精确主义禁止 `people`，而你给了人物主体。
> **模型不会报错**，只表现为「出图莫名地差」。
>
> `compose` 默认把打架的负向词**从负向提示词里拿掉**，拿掉了什么在 `dropped` 里。
> 交付时**提一句你拿掉了什么、为什么** —— 别默默丢掉，那等于把决策藏起来。
> 需要原样合集自己判断：加 `--keep-conflicts`。

## 七层结构

`主体 Subject` + **风格 Style** + **光照 Lighting** + **色彩 Color**
+ **构图 Composition** + **媒介 Medium** + **情绪 Mood** + **镜头 Camera**

每张卡都把这七层拆好了，可单独取用。**光照层的性价比最高**——
它比风格词本身更能决定最终质感。

## 三条原则

1. **以库里的术语为准。** 大模型对艺术流派的记忆模糊，常把
   Art Nouveau 和 Art Deco、巴比松和印象派搞混。库里有具体到光照/色彩/媒介的描述。
2. **分层而不是堆砌。** 不说「巴洛克风格」，说
   「巴洛克的光照层 + 赛博朋克的构图层 + 浮世绘的媒介层」。
3. **先取层，再接主体。** 先 `layers` 拿到风格层，再把主体描述放最前面。

## 分析一张参考图

用户给一张图（或问「这是什么风格」）时，先测量再判断：

```bash
cd "$VAULT/.repo"
python3 image_analysis.py <图片>            # 七维度：明度/对比/色彩/和谐/构图/质感/线条
python3 clip_match.py match <图片>          # 最像的流派（CLIP，含零样本）
```

`image_analysis` 只用 Pillow，永远可用。`clip_match` 需要先下模型
（约 150MB，一次性）：`python3 clip_embed.py download && python3 clip_embed.py build`。

**⚠ 两者都只是信号，不是结论。**
- 客观测量的每一项都能翻译成提示词（「低明调」→ `low-key lighting`），
  但**风格判断不能只看数字**。实测纯按配色距离匹配，一张油画会被算成
  最接近「现实主义」，而那只是土色系重合。
- CLIP 的 Top-1 实测 39%（随机基准 1.4%），十次错六次。

正确用法：**先看图凭感觉判断 → 再看数字检查有没有看走眼 → 冲突时回去看图**
（通常是感觉错了）。几个真正有用的信号：
- `暗部溢出` 高 = 有意为之的深压暗调（巴洛克/明暗对照），不是曝光失误
- `RMS 低但 Michelson 高` = 大面积暗调 + 小面积高光 → 明暗对照法的签名
- `和谐` 判「互补 / 两组色相对峙」能抓出「纸底 vs 颜料」这类色彩骨架

最后用 `artvault.py layers <流派>` 拿到人写的具体术语来落定风格。

## 做视频提示词

每张卡的「五、AI 视频层」给了**两块可直接粘贴的中文提示词**，格式不同别混用：

```bash
cd "$VAULT/.repo"
python3 artvault.py video 巴洛克        # A 块 Seedance 2.5 + B 块 MiniMax H3
```

- **A 块 → Seedance 2.5**（五段式：主体/风格/时间线/BGM/限制）
- **B 块 → MiniMax H3 海螺官网/API**（纯中文自然语言）

⚠ H3 前面有 Context-IR 做理解与改写，**手工塞分镜和时间戳会和它打架**
（镜头数翻倍、时间戳错位），所以 B 块刻意不结构化。细节见
`00-guides/视频提示词结构.md`。

## Pinterest 投递箱

`$VAULT/pinterest/` 是投递箱。用户说「处理 pinterest 投递箱」时：

```bash
cd "$VAULT/.repo" && python3 ingest_inbox.py --scan
```

`--scan` 一次给全：七维度客观测量、人脸景别/霍夫直线/显著性
（装了 numpy+opencv 时）、**CLIP 建议流派 Top-3**、配色最近的流派。
`--no-analysis` 可跳过分析只要清单。

其中 **CLIP 建议流派最有用** —— 实测一张神奈川冲浪里被「配色最近」判成
「宝丽来与胶片」，CLIP 正确判成 ukiyo-e。但它仍是**建议**（Top-1 39%）。

然后**逐张 `read_image` 看图**，做七层拆解 + 匹配 1–3 个流派，
写入 `20-my-prompts/投递箱-<日期>.md`，最后 `--archive` 归档。
（需要 Pillow；没有就 `pip3 install --user Pillow`）

## 更多文档

库内 `00-guides/`：流派总览、关键词图谱（218 styles / 189 movements / 68 genres 映射）、
提示词拆解方法、视频提示词结构、AI 调用指南、反推工具链、版权与来源。

## MCP（可选）

支持 MCP 的客户端（Claude Desktop / Cursor）可直连：

```json
{"mcpServers": {"artvault": {"command": "python3",
  "args": ["<VAULT>/.repo/mcp_server.py"]}}}
```

工具（10 个）：`search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`。纯标准库实现。

- `analyze_image(path)` 图片客观测量、`match_movement(path, topn)` 找最像的流派 ——
  需要 Pillow / CLIP 模型，没装会返回明确原因和修复命令，不影响其余工具
- `get_video_prompt(slug)` 取该流派**两块可粘贴的中文视频提示词**
  （Seedance 2.5 五段式 / MiniMax H3 自然语言），命令行等价于
  `python3 artvault.py video <流派>`
