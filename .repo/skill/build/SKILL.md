---
name: "build-art-aesthetic-vault"
description: "从零构建一个 Obsidian 艺术审美风格库：141 个艺术流派的视觉语言拆解与七层提示词层，配 CC0 公共领域实图，含关键词图谱、AI 调取接口（CLI + MCP）、图片分析工具与投递箱，并能把你**自己文件夹里的图**扫进来按流派归类、与权威库挂在同一张图谱上。当用户想建立自己的艺术/审美/风格参考库、给 AI 绘画或角色设计准备提示词素材库、或想系统整理视觉参考时使用。"
metadata:
  short-description: "从零建一个 141 流派、带 AI 接口的 Obsidian 艺术审美库"
---

# 构建艺术审美风格库

为用户建一套 **Obsidian 艺术审美参考库**：141 个艺术流派的视觉语言拆成
七层可复用的提示词层，配公共领域实图，并提供让 AI 调取的接口。

**产物**：约 180 篇笔记、约 370 张 CC0 图片、约 140 MB。

---

## 零、数据从哪来（重要）

**本 skill 不自带任何数据。** 仓库本身就是数据源：

```
github.com/YanKaFei/art-aesthetic-vault
├── .repo/mv_*.py     ← 141 个流派的完整定义（约 5700 行）
├── .repo/*.py        ← 抓图 / 生成 / 检索 / 分析 全部脚本
├── skill/               ← 查询 skill（软链安装）
└── skill/build/         ← 本 skill
```

所以第一步永远是**拿到仓库**：

```bash
# 方式 A：直接 clone
git clone --depth 1 https://github.com/YanKaFei/art-aesthetic-vault.git my-art-vault

# 方式 B：用 GitHub Template（在仓库页面点 "Use this template"）
#         得到一份属于你自己的副本，改 mv_*.py 就是自己的库

# 方式 C：用户已有仓库，直接用
```

> **为什么不在 skill 里打包一份数据**：那样就有两份 `mv_*.py`，
> 一定会分叉。实测过 —— 打包版本里有 4 个文件与仓库不同步，
> 用那个建出来的库分类是错的（浮世绘会落在「西方古典」而不是「东亚」）。
> **单一数据源**是唯一能长期正确的做法。

---

## 一、先和用户确认两件事

抓图很慢（首次 60–90 分钟），方向错了是浪费。

1. **建在哪里？** 默认就把 clone 下来的目录当仓库。
2. **图片策略？**
   - **只收 CC0 / 公共领域**（默认，推荐）——整个库「随便用不用想」
   - 额外接受 CC BY（`--include-ccby`，覆盖面更大但要署名）

---

## 二、这套库长什么样

```
<仓库根>/
├── 00-guides/          流派总览、分类索引、关键词图谱、七层方法、
│                     视频结构、配色速查、反推工具链、版权说明、AI 调用指南
├── 10-movements/          141 张流派卡（六维视觉拆解 + 七层提示词 + 配色 + 视频层）
├── 20-my-prompts/     用户自己的卡片（脚本永不覆盖）
├── 90-templates/          新建笔记用的模板
├── 99-attachments/images/   从开放数据源抓来的图
├── pinterest/        图片投递箱（丢图进去 → 分析 → 归档）
├── skill/            AI skill 源码
└── .repo/         数据定义 + 抓图 + 生成 + 检索 + 分析
```

**每张流派卡的结构**：核心主张 / 六维视觉拆解 / 配色板 /
**七层提示词 + 针对性负向** / AI 视频层 / CC0 实图 / 常见翻车点 / 关联流派。

---

## 三、执行流程

### 阶段 0：环境

```bash
python3 -V                      # 需要 3.8+
cd <仓库>/.repo && python3 movements.py    # 应输出「合计 141 个流派，6 个分类」
```

**核心脚本只用标准库，不需要 pip 安装任何东西。**

### 阶段 1：抓图（最慢）

```bash
cd <仓库>/.repo
python3 -u fetch_art.py --per 6 2>&1 | tee /tmp/fetch.log
```

**放后台跑**，约 60–90 分钟（瓶颈在大都会 API，每个条目单独请求）。

- 四个源轮转：`cleveland → artic → met → commons`（按来源轮流取，避免第一个源垄断）
- **两层过滤**：作者关键词命中 + 平面作品
- **刻意不做「放宽补充」**——宁可某流派只有 1 张图，也不塞无关作品
- 中断可续：已有 `_data/<slug>.json` 的会跳过

**只想要提示词卡不要图**：跳过本阶段，直接进阶段 2。

### 阶段 2：生成笔记

```bash
python3 build_vault.py     # 生成全部笔记 + 关键词图谱 + README + LICENSE
```

关键词图谱把 **218 styles / 189 movements / 68 genres** 全部投影到库内流派卡 ——
这是「完整性」的保证。

### 阶段 3：AI 调取接口

```bash
python3 artvault.py categories              # 自检
python3 artvault.py layers 巴洛克            # 七层提示词（省 token）
python3 artvault.py compose "雨夜霓虹的赏金猎人，要巴洛克的光照" --subject "a bounty hunter"
```

`compose` 把创意想法按意图分层、从不同流派各取一层组合，并**自动消解层级冲突**
（打架的负向词会被拿掉并在 `dropped` 里说明；`--keep-conflicts` 保留原样）。

MCP 服务（纯标准库，9 个工具，含 analyze_image / match_movement）：`python3 mcp_server.py`

### 阶段 4：图片分析与投递箱

```bash
python3 image_analysis.py <图片>              # 七维度客观测量（纯 Pillow）
python3 image_analysis.py <目录> --json       # 批量
ARTVAULT_NO_EXT=1 python3 image_analysis.py <图片>   # 关掉增强维度
python3 image_analysis_ext.py <图片>          # 三个可选增强（要 numpy + opencv）
# 图像→流派匹配：先 CLIP（跨平台、最准），macOS 上也可用系统自带 Vision
python3 clip_embed.py download                # 首次：下量化模型（约 150MB，一次性）
python3 clip_embed.py build                   # 建索引，600 张约 25 秒
python3 clip_match.py eval                    # 评测三条路
python3 clip_match.py match <图片>            # 最像的流派（含零样本）
python3 artvault_vision.py build              # 备选：macOS Vision 语义索引
python3 artvault_vision.py dups --thresh 0.08 # 近重复检测（验收第 5 项）

python3 ingest_inbox.py --scan                # 投递箱扫描（已带上以上维度 + CLIP 建议）
```

**七维度**：明度 / 对比 / 色彩 / 和谐 / 构图 / 质感 / 线条 —— 每一项都能翻译成
提示词（「低明调」→ `low-key lighting`，「繁杂」→ `intricate detail`）。

**三个可选增强**：人脸景别 / 霍夫直线 / 谱残差显著性。装了 numpy+opencv 才有，
没装自动跳过，主脚本照常跑（`ARTVAULT_NO_EXT=1` 可强制关掉）。

**图像→流派匹配实测三条路**（396 张、72 个流派、随机基准 1.4%）：

| 做法 | Top-1 | Top-3 |
|---|---|---|
| **CLIP + 融合** | **39.1%** | **61.4%** |
| Vision featureprint（macOS） | 30.6% | 50.8% |
| T1 客观维度（可解释，但实测最弱 —— 脚本已删，只留结论） | 13.2% | 25.3% |

CLIP 还能做**零样本** —— 用流派卡的英文描述直接匹配图像，所以那些一张实图
都没有的流派（赛博朋克、蒸汽朋克）也能被匹配到。

**关键提醒**：这些数字是**信号不是结论**，最好的 CLIP 也是十次错六次。
实测纯按配色距离匹配，一张油画会被算成最接近「现实主义」，而那只是土色系重合。
正确用法是先看图凭感觉判断，再看数字检查有没有看走眼，冲突时回去看图。

`--scan` 会给出 **CLIP 建议流派**（Top-3），比同输出里的「配色最近」可靠得多 ——
实测一张神奈川冲浪里被配色匹配判成「宝丽来与胶片」，CLIP 正确判成 ukiyo-e。

投递箱工作流：用户把参考图丢进 `pinterest/` → AI 逐张 `read_image` 看图 →
七层拆解 + 匹配流派 → 写 `20-my-prompts/投递箱-<日期>.md` → `--archive` 归档。

详见 `reference/analysis.md`（含和谐维度换过三版、人脸不能缩到 256 检测、
霍夫 threshold=45 会把噪声当直线、CLIP 融合权重扫过才知道等踩坑记录）。

### 阶段 5：安装查询 skill

```bash
cd <仓库>/skill && ./install.sh
```

软链安装到 `~/.agents/skills/`、`~/.claude/skills/`、`~/.codex/skills/`。
**软链**让 skill 用 `pwd -P` 解析真实位置，仓库放哪都能自动找到。

### 阶段 6：把你自己的图并进库（可选，但这是它最有用的地方）

到这里你有了一个 141 流派的权威库。但**你自己的参考图**在你自己硬盘上 ——
私人收集、可能没授权、数量不定。这一阶段把它们并进来，而且**并进同一张图谱**。

```bash
cd .repo

# 扫一个目录（只分析，不复制文件）
python3 scan_local.py ~/Pictures/refs --name 我的参考图

# 看待确认清单：按 CLIP 建议的流派分组，标注把握程度
python3 scan_local.py --list

# 确认归类（编号是扫描时分配的，稳定不变）
python3 scan_local.py --file 3 --to baroque
python3 scan_local.py --file 5,7,9 --to 浮世绘     # 中文名也行
python3 scan_local.py --file 12 --drop              # 不要这张

# 或者只自动归「很有把握」的
python3 scan_local.py --auto --min-margin 1.0

# 生成 15-my-library/ 的笔记，并在流派卡里加一行入口
python3 build_vault.py
```

**三层结构**，都在同一个 Obsidian 仓库里：

| 层 | 位置 | 发布吗 |
|---|---|---|
| 层 1 · 权威 | `10-movements/` + `99-attachments/images/<流派>/` | ✅ 随仓库发布 |
| **层 2 · 你的图库** | `15-my-library/` + `99-attachments/images-local/<流派>/` | ❌ gitignore |
| 层 3 · 你的提示词 | `20-my-prompts/` | ❌ gitignore |
| 暂存 | `pinterest/` 投递箱 | ❌ gitignore，不进图谱 |

**图谱是一张连通的图**，不是两块：每篇 `我的图库-<流派>.md` 都链回 `[[流派卡]]`，
所以 `我的图库-巴洛克 → 巴洛克 → 流派总览 → …` 串得起来。
流派卡底部会出现一行入口（只在本机有图时出现）：

```
> [!tip] 我的收藏
> 你自己扫进来的 **12 张** → [[我的图库-巴洛克]]
```

刻意**只放一行链接、不铺开图片**：万一这行被误提交，也只暴露「有几张」，
不暴露图片本身（图在 gitignore 的 `99-attachments/images-local/` 里）。
清单是 gitignore 的，所以别人 clone 后这一行根本不存在，不会留下悬空链接。

> [!warning] 为什么不是「扫一遍自动分好类」
> 实测过（396 张 / 72 个流派），按模型把握程度分层看准确率：
>
> | 第一名与第二名的分差 | 覆盖多少图 | 准确率 |
> |---|---|---|
> | ≥1.5 | 2% | 100% |
> | ≥1.0 | 7% | 80% |
> | ≥0.6 | 19% | 66% |
> | ≥0.3 | 41% | **54%** |
>
> **高把握的只覆盖 7% 的图；放宽到有用的覆盖率时就是掷硬币。**
> 所以脚本只给建议，归档要你看一眼确认 —— 这和这个库的「宁可少不要错」一致。

**投递箱也会汇进这一层**：`ingest_inbox.py --archive` 不再把图堆在
`pinterest/_已归档/`，而是按 CLIP 建议归入 `99-attachments/images-local/<流派>/`，
让你从投递箱进来的图也进图谱（没给出建议的进 `_未归类/`，在总览页里列出来等你归）。

### 阶段 7：验收（必做）

```bash
cd .repo
python3 verify_vault.py            # 全部检查
python3 verify_vault.py --quick    # 跳过第 5 项（近重复），其余七项照跑
```

八项检查：**断链 · 重名 · AI 生成图 · frontmatter · 近重复 · 授权字段 · 孤儿图 · JSON↔磁盘**。
退出码 0 = 全过，1 = 有问题（可以直接写进 CI 或 pre-commit）。

**必须全过的是 1/2/3/4/6/7/8 七项**（零可选依赖）。
只有第 5 项是**信息项** —— 它列出跨流派完全相同的图，但不判失败，
因为大部分跨流派重复是合理的（见下）：


```
1 断链        每个 ![[...]] 都能在 99-attachments/images/ 下找到文件
2 重名        全库 basename 唯一 —— Obsidian 的 ![[名]] 按 basename 解析，
              重名会让嵌入指向错误的那张
3 AI 图       全库 0 命中 —— 用模型的输出当模型的参考是致命的
4 frontmatter 合法 YAML，且无 HTML 注释（`<` 开头的行）
```

后三项里，第 5 项「近重复」值钱但要人工判断：

```bash
python3 artvault_vision.py build              # 600 张约 8 秒
python3 verify_vault.py                       # 会自动带上第 5 项
```

它一次就找出过 `abstract-art` 仅有 2 张图、却和 `de-stijl` 一模一样的问题。
但**大部分跨流派重复是合理的**，不是 bug —— 一件作品本来就可以同时是多个
流派的例证（Caravaggisti 属巴洛克、Diego Rivera 同属壁画运动与社会现实主义）。
人工过的时候判断的是：重叠说得通 → 保留；还是关键词选错了（该流派真正该有的
作品一张都没有）→ 改关键词。详见 `reference/pitfalls.md` 的 4.5。

第 6 项「授权字段」是发布的前提：每件作品都要能说清来源与授权。
第 7 项「孤儿图」通常意味着某次抓取中途断了，重建笔记即可。

---

## 四、给 AI 的硬性约束

1. **不要凭记忆编造流派术语。** 库里的 141 个流派对照过完整分类体系，
   比模型记忆可靠 —— 模型常把 Art Nouveau 和 Art Deco、巴比松和印象派搞混。

2. **宁可少，不要错。** 筛选不加「放宽补充」。某个流派只有 1 张图就 1 张。
   > 一个参考库最怕的不是图少，是图错。错的参考会污染提示词直觉，
   > 而且用户自己不会发现。

3. **建完必须复扫 AI 生成图。** 维基共享上有大量 AI 生成图标注 CC0，
   会渗进「魔幻现实主义」这类流派。**给 AI 做参考的库里放着 AI 生成的图，
   等于用模型输出当模型参考。**

4. **加新流派必须同时加 `ARTIST_KEYS`**，否则会抓进大量无关作品。
   实测：`lange` 会命中 miche**lange**lo、`henri` 会命中 Fantin-Latour、
   `delaunay` 会命中 17 世纪的同名画家。

5. **版权分级要落到文件。** 每张图记录来源/授权/授权链接；
   非 CC0 来源的目录写进 `.gitignore`；1950 年后的流派生成纯提示词卡。

6. **不要用 curl 测站点可达性。** 出口代理可能拦 curl 的 TLS 指纹却放过 Python。
   实测因为这条错误判断，白白漏掉了芝加哥艺术博物馆（13 万件的一流源）。

7. **改生成物之前先改模板。** `README.md` / `10-movements/*.md` / `.gitignore`
   都是 `build_vault.py` 生成的 —— 直接手改会在下次重跑时被覆盖。

---

## 五、参考文档

| 文档 | 什么时候读 |
|---|---|
| `reference/pitfalls.md` | **执行前必读**。每个坑都真实发生过并导致过返工 |
| `reference/method.md` | 七层拆解法、为什么这么分、怎么调、冲突检测 |
| `reference/sources.md` | 数据源端点、授权分级、可达性实测、预估产出 |
| `reference/analysis.md` | 图片客观测量（七维度）、怎么用数字交叉验证、和谐维度的踩坑 |
| `reference/tools.md` | **反推管道内部参考**：现在管线做了什么、主体描述为什么没自动化、要扩展时接哪些工具 |

---

## 六、常见调整

| 用户想要 | 怎么做 |
|---|---|
| 只保留某几个分类 | 改 `.repo/movements.py` 的 `MODULES` 列表 |
| 加自己的流派 | 在对应 `mv_*.py` 加一条 + **同文件 `ARTIST_KEYS` 加过滤词** |
| 每个流派多抓几张 | `fetch_art.py --per 12` |
| 换/加数据源 | 在 `providers.py` 写一个返回统一字段的函数，注册进 `PROVIDERS` |
| 不要图片只要提示词 | 跳过阶段 1 |
| 追加更多网站的关键词 | 改 `keyword_map.py` 的 `CLUSTERS` 与 `WIKIART_MAP` |

新增数据源需要的统一字段：

```python
{"title","artist","date","medium","image_url","image_url_hi",
 "page_url","source","license","license_url"}
```
