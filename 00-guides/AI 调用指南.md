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

## 一之二、电影风格库（按「导演 → 电影」的另一条轴）

`10-movements/` 是**艺术流派**（按风格命名），`40-films/` 是**电影**（按导演命名）。
两者**共用同一套七层词表**，所以可以跨源混搭 —— 这不是文档里的一句口号，
`artvault.py compose` 的层解析里真的挂了电影库的兜底。

```bash
python3 .repo/artvault.py film list              # 列出全部片子
python3 .repo/artvault.py film directors         # 按导演分组
python3 .repo/artvault.py film search "霓虹 雨夜"  # 按画面特征找片（也可按导演/片名）
python3 .repo/artvault.py film layers 银翼杀手2049 # 只要七层（最省 token）
python3 .repo/artvault.py film show dune          # 整张卡
python3 .repo/artvault.py film palette 闪灵        # 配色

# 跨源混搭：拿电影的光照层 + 艺术流派的配色
python3 .repo/artvault.py compose     --lighting villeneuve-dune --color baroque --subject "a lone figure on a dune"
```

> [!note] 这 14 部片是**逐片看过画面**才定稿的
>
> 每部片都跑过一遍「全量实测 → k-medoids 选代表帧 → 拼 3×3 印相图 → 人眼精读」，
> 再把看到的与卡上写的核对。结果是**大部分描述站得住**，只有少数偏窄的被改：
>
> - 已按画面修正：《镜子》的色温漂移、《潜行者》的雨夜单色段与湿地饱和、
>   《寄生虫》的「光＝阶级标记」、《未麻的部屋》的两套打光对撞
> - 看过确认无误、未改：《乱》《未麻的部屋》《银翼杀手 2049》《七宗罪》
>   《重庆森林》《闪灵》《刺客聂隐娘》《沙丘》《精疲力尽》《巴里·林登》
>
> 自己复现：`python3 .repo/contact_sheet.py <片名>` 出印相图。
> 为何必须做这一步：实测页给的是「明度 65.9、饱和 0.31」这类数字，
> **如实但冷** —— 数字能告诉你偏暗，告诉不了你「暗得脏还是暗得神圣」。

> [!warning] 电影卡与艺术流派卡的**证据强度不一样**
>
> - **班底与年份**：抓自 film-grab 画廊页，卡片上标 ✅ 且带外链，可回查
> - **七层拆解**：**手写解读**，依据是这部片公认的摄影特征 —— 不是逐帧测量结果
> - **剧照**：卡片**本地嵌入**每部 6 张代表帧（约 15 MB 随仓库走，clone 后能看图）；
>   版权属原片方，**仅供个人研究**，公开分发/商用前请自行取得授权。
>   其余语料留在本地做分析（`image_analysis` / CLIP 重选代表帧），不随仓库发布。
>
> 引用时别说成「量出来的」。

## 一之三、镜头配方卡库（`45-shots/`，第三条轴：运镜招式）

前两条轴回答「长什么样」，这一条回答「**这一下怎么做出来**」：

| 模块 | 轴 | 回答的问题 |
|---|---|---|
| `10-movements/` | 风格 | 这个流派长什么样、提示词怎么拼 |
| `40-films/` | 导演-电影 | 这部片长什么样、怎么模仿它 |
| `45-shots/` | **运镜招式** | **这一下动效怎么做出来** |

```bash
python3 .repo/artvault.py shots list              # 157 张 / 10 类
python3 .repo/artvault.py shots categories
python3 .repo/artvault.py shots search "急推 冲击"  # 按「我想做什么」找
python3 .repo/artvault.py shots show crash-zoom-punch
```

> [!warning] 这一轴**没有七层**，而且是故意的
>
> 前两条轴共用七层，所以能跨源混搭。镜头卡讲的是帧数与缓动
> （`zoom 6f ease-in，1→2.6`、`震屏 14px·e^(−t/1.8)`）——
> **157 张里一张都没有色彩或光照字段**。套七层只能靠编，而
> `compose --style crash-zoom-punch` 会拼出一段看起来能用、实际在编的提示词。
> 所以它按上游自己的四字段（适用/时长/能量/标签）排，并且**刻意不参与
> `compose` 的层解析**。
>
> 这些卡来自上游 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)
> （Apache-2.0），**技法描述不是本库原创**，本库只做归类与排版。
> 上游另写明：手法研究自公开作品，但实现全部从零重写、不含原片素材，
> 且「公开发布**不等于**授权」。详见 [[出处与许可]]。

## 二、命令行（推荐先从这个开始）

```bash
cd ".repo"
python3 artvault.py categories                 # 7 大分类
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

后两个工具需要 Pillow 与 CLIP 模型；条件不满足时它们会说明原因，
不影响前七个工具。

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
20-my-prompts/投递箱-<日期>.md
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
| 你想**存**自己的成果 | [[提示词卡模板]] 存到 `20-my-prompts/` |

> 仓库里的 Markdown 是给人看的，`artvault` 是给机器用的。两者同源——
> 都从 `.repo/mv_*.py` 生成，改一处两边都更新。
