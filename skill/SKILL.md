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

输出即仓库根目录（记为 `$VAULT`）。找不到就用 `find ~ -name artvault.py -path '*/_scripts/*'` 搜，
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
cd "$VAULT/_scripts"

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

返回：分层结果 + 正向 + 负向 + 配色 + 视频层 + `conflicts` 冲突警告。

> **必须检查 `conflicts`。** 跨流派混搭时负向词会互相打架：
> 浮世绘禁止 `cast shadows`，巴洛克光照却要 `deep crushed shadows`；
> 精确主义禁止 `people`，而你给了人物主体。
> **模型不会报错**，只表现为「出图莫名地差」。检出后要逐条删掉冲突词再交付。

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

## Pinterest 投递箱

`$VAULT/pinterest/` 是投递箱。用户说「处理 pinterest 投递箱」时：

```bash
cd "$VAULT/_scripts" && python3 ingest_inbox.py --scan   # 尺寸/主色/感知哈希/配色最近的流派
```

然后**逐张 `read_image` 看图**，做七层拆解 + 匹配 1–3 个流派，
写入 `20-我的提示词/投递箱-<日期>.md`，最后 `--archive` 归档。
（需要 Pillow；没有就 `pip3 install --user Pillow`）

## 更多文档

库内 `00-导航/`：流派总览、关键词图谱（218 styles / 189 movements / 68 genres 映射）、
提示词拆解方法、视频提示词结构、AI 调用指南、反推工具链、版权与来源。

## MCP（可选）

支持 MCP 的客户端（Claude Desktop / Cursor）可直连：

```json
{"mcpServers": {"artvault": {"command": "python3",
  "args": ["<VAULT>/_scripts/mcp_server.py"]}}}
```

工具：`search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories`。纯标准库。
