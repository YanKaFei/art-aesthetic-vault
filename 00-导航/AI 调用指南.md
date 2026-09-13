---
type: 说明
---

# AI 调用指南

> [!abstract] 这一页解决什么
> 让 AI（Claude / Cursor / DSH / 自建 agent）能**主动调取这个仓库**，
> 在你有一个创意想法时，帮你从全部流派里取料、拼成可用的提示词。
>
> 仓库提供了三层接口，按你的技术栈挑一个：
> **CLI（最通用）→ MCP 服务（最省事）→ JSON 导出（最灵活）**。

## 一、三层接口

| 接口 | 文件 | 谁用 |
|---|---|---|
| **命令行** | `.repo/artvault.py` | 任何能执行 shell 的 AI，无需配置 |
| **MCP 服务** | `.repo/mcp_server.py` | Claude Desktop / Cursor / Cline 等支持 MCP 的客户端 |
| **JSON 导出** | `artvault.py dump` | 你要自己接进别的程序或做 RAG |

三者共用 `.repo/artvault_core.py` 的同一套逻辑，行为一致。

## 二、命令行（推荐先从这个开始）

```bash
cd ".repo"
python3 artvault.py categories                 # 6 大分类
python3 artvault.py list --with-images          # 有实图的流派
python3 artvault.py search "霓虹 雨夜"           # 模糊检索
python3 artvault.py search "压抑但华丽的光" --semantic   # 语义检索（需下过 CLIP 模型）
python3 artvault.py layers 巴洛克                # 只要七层提示词（最省 token）
python3 artvault.py show 印象派                  # 完整卡片
python3 artvault.py palette 印象派               # 配色
python3 artvault.py related 立体主义             # 关联流派
```

**给 AI 的调用约定**：任何命令加 `--json` 都会输出机器可读的 JSON。例如

```bash
python3 artvault.py --json layers 巴洛克
```

### 组合提示词：把创意想法变成分层提示词

```bash
# 自然语言：自动识别提到的流派，按意图词分配层级
python3 artvault.py compose "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \
        --subject "a female bounty hunter in a wet neon alley"

# 显式跨流派混搭
python3 artvault.py compose --style ukiyo-e --lighting baroque \
        --color vaporwave --composition precisionism --subject "a lone samurai"
```

输出包含：**分层结果 + 正向提示词 + 负向提示词 + 配色 + 视频层 + 冲突消解记录**。

> [!tip] 跨流派混搭的冲突已经自动处理了
> 把不同流派的负向词合并会**打架**。实测例子：
> 浮世绘要求 `no cast shadows`，而巴洛克的光照层恰恰要 `deep crushed shadows`；
> 精确主义的负向词里有 `people / figures`，你的主体却是个武士。
>
> `compose` 会把打架的负向词**自动从负向提示词里拿掉**，并在
> 「已自动消解的冲突」里逐条说明拿掉了哪个、让位给谁。规则只有一条：
> **正向是意图，负向是护栏，护栏让位于意图。**
>
> 想拿到未经处理的负向词合集（自己判断）：加 `--keep-conflicts`。

## 三、MCP 服务（一次配置，长期可用）

在客户端配置里加上（以 Claude Desktop 为例，路径换成你的实际位置）：

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<仓库绝对路径>/.repo/mcp_server.py"]
    }
  }
}
```

配置文件的常见位置：

| 客户端 | 路径 |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Cline / 其他 | 见各自文档 |

暴露的工具：

| 工具 | 作用 |
|---|---|
| `search_movements(query, limit)` | 检索流派 |
| `get_movement(slug)` | 完整卡片 |
| `get_layers(slug)` | 只要七层提示词（省 token） |
| `compose_prompt(brief, subject, style, lighting, …)` | **拼提示词** |
| `get_palette(slug)` | 配色 |
| `find_related(slug)` | 关联流派 |
| `list_categories()` | 分类概览 |
| `analyze_image(path)` | **图片客观测量**：七维度 + 人脸景别/霍夫直线/显著性（新） |
| `match_movement(path, topn)` | **给一张图找最像的流派**（CLIP 语义匹配，含零样本）（新） |

纯标准库实现，**不需要 `pip install mcp`**。
后两个工具依赖 Pillow（图片分析）与 CLIP 模型（语义匹配），未装时会返回
明确原因和修复命令，不影响前七个工具。

## 四、给 AI 的提示词怎么写

在你的 agent 系统提示里加一段：

```text
你有一个艺术风格知识库，通过 artvault 工具访问。
当用户描述一个视觉创意时：
1. 先用 search_movements 找出相关的 2–4 个流派
2. 用 get_layers 取它们的提示词层
3. 用 compose_prompt 拼成完整提示词；返回的 dropped 字段是**已自动拿掉的**
   打架负向词，交付时提一句你拿掉了什么、为什么，别默默丢掉
4. 输出时说明每一层来自哪个流派，以及为什么这样搭配

不要凭记忆编造风格词——库里的流派覆盖从拜占庭到 Y2K，
所有术语都以库里的为准。
```

> [!tip] 为什么强调「以库里的为准」
> 大模型对艺术流派的记忆是模糊的、容易把相近的搞混（比如把 Art Nouveau
> 和 Art Deco 的视觉特征混在一起）。这个库的价值就是给出**具体到光照、
> 色彩、媒介**的可执行描述，而不是一个风格名词。

## 五、Pinterest 投递箱：人找图，AI 拆解

`pinterest/` 是投递箱。分工是：**你负责找图和判断，AI 负责拆解和归档。**

```
你把图丢进 pinterest/
        ↓  说「处理 pinterest 投递箱」
python3 .repo/ingest_inbox.py --scan     ← 客观测量：尺寸/主色/感知哈希/配色最近的流派
        ↓  AI 逐张 read_image 看图
七层拆解 + 匹配 1–3 个流派 + 可复用提示词
        ↓  写入
20-我的提示词/投递箱-<日期>.md
        ↓
python3 .repo/ingest_inbox.py --archive  ← 图移到 pinterest/_已归档/
```

为什么这样分工：Pinterest 的搜索是登录态、个性化的，
**你手动挑的图比任何爬虫抓的都准。**
而拆解是机械劳动，正好交给 AI。

脚本做客观测量，AI 做语义判断——两者都做自己擅长的。
配色距离那类数字**只是参考信号**：实测有张土色系的调色板照片，
配色距离算出来最接近「现实主义」，但那是土色重合，不是风格相近。

## 六、和 Obsidian 里的笔记怎么配合

| 场景 | 用哪个 |
|---|---|
| 你想**读**、建立审美直觉 | Obsidian 里看 [[流派总览]] 和流派卡 |
| 你想**查**某个词是什么 | Obsidian 里搜 [[关键词图谱]] |
| 你想**用**、生成东西 | 让 AI 调 `artvault` |
| 你想**存**自己的成果 | [[提示词卡模板]] 存到 `20-我的提示词/` |

> 仓库里的 Markdown 是给人看的，`artvault` 是给机器用的。两者同源——
> 都从 `.repo/mv_*.py` 生成，改一处两边都更新。
