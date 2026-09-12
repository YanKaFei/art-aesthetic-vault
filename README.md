<div align="center">

# 艺术审美风格库

**把 141 个艺术流派的视觉语言，拆成可以直接用的 AI 提示词层**

从拜占庭到 Y2K ｜ 东亚 · 南亚 · 伊斯兰 ｜ 摄影谱系 ｜ 数字亚文化

163 篇笔记 · 372 张公共领域实图 · 21 个即用脚本

[English](README.en.md) ｜ **中文**

</div>

---

## 这是什么

大部分人收集「艺术风格参考」的方式是存图——存了几百张，但真要用的时候不知道该看什么、
该怎么描述。图是死的。

这个库换个做法：**把每个流派的视觉语言拆成七个可以独立替换的层**。

```
主体 Subject  +  风格 Style  +  光照 Lighting  +  色彩 Color
              +  构图 Composition  +  媒介 Medium  +  情绪 Mood  +  镜头 Camera
```

拆成层之后，你才能把 A 图的光照套到 B 图的主体上。**这才是参考库真正的用处。**

### 看一眼它怎么工作

假设你想画「雨夜霓虹街头的赏金猎人」，同时想要古典绘画的光影质感：

```bash
python3 artvault.py compose \
  "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \
  --subject "a female bounty hunter in a wet neon alley"
```

它会自动识别出「巴洛克」后面跟着「光照」→ 取巴洛克的光照层；
「赛博朋克」→ 取风格与构图层。然后拼成：

```
a female bounty hunter in a wet neon alley,        <- 你的主体
cyberpunk, neo-noir concept art, dense neon signage,   <- 风格层 · 赛博朋克
single hard light source from off-frame,               <- 光照层 · 巴洛克
deep crushed shadows, candlelight rim light,
cyan and magenta clash, amber accent, deep black,      <- 色彩层 · 赛博朋克
low angle looking up at megastructures,                <- 构图层 · 赛博朋克
alienated, oppressive, intoxicating                    <- 情绪层
```

**同一个主体，每一层都可以单独换掉。** 这是这个库和「风格词堆砌」的根本区别。

---

## 技能树

```
艺术审美风格库
│
├─ 🏛 西方古典与近代 · 47 个流派
│  ├─ 中世纪与拜占庭
│  │  └ 拜占庭艺术 · 罗马式艺术 · 哥特式艺术 · 国际哥特式
│  ├─ 文艺复兴
│  │  ├ 早期文艺复兴 · 文艺复兴 · 早期尼德兰绘画 · 威尼斯画派
│  │  └ 样式主义
│  ├─ 巴洛克与古典
│  │  ├ 巴洛克 · 卡拉瓦乔主义 · 荷兰黄金时代 · 洛可可
│  │  └ 古典主义 · 新古典主义
│  ├─ 19 世纪
│  │  ├ 浪漫主义 · 现实主义 · 自然主义 · 东方主义
│  │  └ 学院派艺术 · 拉斐尔前派
│  ├─ 印象派前后
│  │  ├ 印象派 · 新印象派（点彩） · 后印象派 · 纳比派
│  │  └ 象征主义 · 日本主义
│  ├─ 世纪之交
│  │  └ 新艺术运动 · 维也纳分离派 · 工艺美术运动
│  └─ 美国与近代诸派
│     ├ 哈德逊河派 · 发光主义 · 色调主义 · 阿什坎学派
│     ├ 美国现实主义 · 美国地域主义 · 精确主义 · 社会现实主义
│     ├ 社会主义现实主义 · 墨西哥壁画运动 · 魔幻现实主义（绘画） · 形而上绘画
│     ├ 新浪漫主义 · 稚拙艺术（原始主义） · 古典写实主义（当代） · 媚俗艺术
│     └ 新客观主义
├─ 🀄 东亚·南亚·伊斯兰 · 21 个流派
│  ├─ 中国
│  │  ├ 青绿山水 · 水墨写意 · 工笔重彩 · 宋代院体画
│  │  └ 敦煌壁画
│  ├─ 日本
│  │  ├ 浮世绘 · 琳派 · 日本水墨画（禅画） · 大和绘
│  │  └ 创作版画 · 新版画 · 禅艺术
│  ├─ 朝鲜半岛
│  │  └ 韩国民画
│  ├─ 波斯与伊斯兰
│  │  ├ 波斯细密画 · 萨法维绘画 · 莫卧儿细密画 · 伊斯兰几何纹样
│  │  └ 阿拉伯书法
│  ├─ 喜马拉雅与原住民
│  │  └ 西藏唐卡 · 本土主义（拉丁美洲）
│  └─ 其他
│     └ 原住民艺术
├─ 🎨 现代主义与战后 · 23 个流派
│  ├─ 表现与野兽
│  │  └ 表现主义 · 野兽派 · 青骑士
│  ├─ 立体与未来
│  │  └ 立体主义 · 俄耳甫斯主义 · 未来主义
│  ├─ 几何抽象
│  │  └ 至上主义 · 构成主义 · 风格派 · 包豪斯
│  ├─ 达达与超现实
│  │  └ 达达主义 · 超现实主义
│  ├─ 战后抽象
│  │  └ 抽象表现主义 · 色域绘画
│  ├─ 波普与极简
│  │  └ 波普艺术 · 欧普艺术 · 极简主义（艺术） · 装饰艺术
│  └─ 其他
│     ├ 观念艺术 · 照相写实主义 · 大地艺术 · 超扁平
│     └ 新表现主义
├─ 🌃 数字·亚文化·摄影美学 · 24 个流派
│  ├─ 朋克五支
│  │  ├ 赛博朋克 · 蒸汽朋克 · 柴油朋克 · 太阳朋克
│  │  └ 生物朋克
│  ├─ 网络怀旧
│  │  ├ 蒸汽波 · 合成器浪潮 · 像素艺术 · 90 年代复古动画
│  │  └ 梦核 · Y2K 千禧美学
│  ├─ 动画与插画
│  │  └ 日式动画赛璐璐
│  ├─ 银盐与印相
│  │  └ 蓝晒法 · 湿版摄影 · 宝丽来与胶片
│  ├─ 氛围与生活
│  │  ├ 暗黑学院 · 田园风 · 侘寂 · 哥特亚文化
│  │  └ 废土风
│  ├─ 平面设计
│  │  └ 极简主义设计 · 瑞士国际主义 · 孟菲斯设计
│  └─ 电影感
│     └ 黑色电影
├─ 🚀 先锋·当代·后现代 · 20 个流派
│  ├─ 三个总纲
│  │  └ 先锋艺术 · 当代艺术 · 后现代主义
│  ├─ 抽象诸支
│  │  └ 抽象艺术 · 硬边绘画 · 后绘画性抽象
│  ├─ 反艺术与媚俗
│  │  └ 新达达 · 新波普 · 超前卫
│  ├─ 边缘与身体
│  │  └ 原生艺术 · 域外艺术 · 女性主义艺术
│  ├─ 公共与空间
│  │  └ 街头艺术 · 动力艺术 · 光与空间运动
│  ├─ 新媒介与后观念
│  │  └ 数字艺术 · 超写实主义
│  └─ 其他
│     └ 无形式艺术 · 斑点主义 · 抒情抽象
└─ 📷 摄影与图像 · 6 个流派
   ├─ 两大传统
   │  └ 画意摄影 · 直接摄影
   ├─ 社会与街头
   │  └ 纪实摄影 · 街头摄影
   └─ 观念与时尚
      └ 超现实摄影 · 时尚编辑摄影
```

---

## 有多少东西

| | 数量 |
|---|---|
| **流派卡** | **141 张**，6 大分类，每张含六维视觉拆解 + 七层提示词 + 配色 + 视频层 |
| **公共领域实图** | **372 张**（134 MB），79 个流派配了图 |
| **导航与方法论** | 18 篇（流派总览、关键词图谱、七层方法、视频结构、配色速查、反推工具链…） |
| **关键词图谱** | 全部 **218 styles / 189 movements / 68 genres** 的完整映射 |
| **笔记模板** | 3 个（流派卡 / 提示词卡 / 作品拆解） |
| **脚本** | 21 个，抓图、生成、检索、提示词合成、MCP 服务 |

> **62 个流派是「纯提示词卡」**——抽象表现主义、波普、极简主义、观念艺术、
> 赛博朋克、蒸汽波这些，作品仍在版权期内，任何开放数据源都不会提供图。
> 它们的视觉语言与七层结构照常拆解，只是不配图。这是刻意的设计，不是缺失。

---

## 怎么用

### 方式一：当作 Obsidian 仓库读

用 Obsidian 打开这个文件夹。建议从这个顺序进入：

1. `00-导航/提示词拆解方法.md` —— **先读这个**，理解七层是怎么回事
2. `00-导航/流派总览.md` —— 141 个流派的总入口
3. `10-流派/` —— 挑一个你喜欢的流派，看它的完整拆解
4. `00-导航/关键词图谱.md` —— 以后看到陌生风格词就来这里查

### 方式二：让 AI 直接调用它

库不只是一堆给人看的 Markdown，还有一层**给机器用的接口**：

```bash
cd _scripts

python3 artvault.py categories              # 看 6 大分类
python3 artvault.py search "霓虹 雨夜"       # 模糊检索，中英文都行
python3 artvault.py layers 巴洛克            # 只要七层提示词（最省 token）
python3 artvault.py show 浮世绘              # 完整卡片
python3 artvault.py palette 赛博朋克         # 六色配色
python3 artvault.py related 立体主义         # 找关联流派
python3 artvault.py --json layers 巴洛克     # 机器可读
```

**核心能力是组合**：

```bash
# 自然语言，自动分层
python3 artvault.py compose "雨夜霓虹的赏金猎人，要巴洛克的光照" --subject "a bounty hunter"

# 显式指定，跨时代混搭
python3 artvault.py compose --style ukiyo-e --lighting baroque \
  --color vaporwave --composition precisionism --subject "a lone samurai"
```

它会**检出并打印层级冲突**。跨流派混搭时负向词会互相打架——
浮世绘禁止 `cast shadows`，巴洛克光照却要求 `deep crushed shadows`；
精确主义禁止 `people`，而你的主体是个人物。
**模型不会报错**，只会表现为「出图质量莫名地差」，极难排查。这个检查能省你几个小时。

### 方式三：装成 AI skill（推荐）

仓库自带一个 skill，装上之后**任何支持 skill 的 AI 助手**在遇到视觉/审美类任务时
会自动查这个库，而不是凭记忆编造流派术语。

```bash
cd skill && ./install.sh
```

仓库提供**两个** skill，一次装好：

| skill | 干什么 | 什么时候触发 |
|---|---|---|
| `art-aesthetic-vault` | **用**库：检索流派、取七层提示词、跨流派拼提示词 | 你问「这个角色该用什么风格」 |
| `build-art-aesthetic-vault` | **建**库：从零建一套新的 | 你说「我也想要一套这样的库」 |

> [!note] 为什么两个 skill 都不自带数据
> 它们都是**软链**指向本仓库 —— 数据只有仓库这一份。
> `mv_*.py`（141 个流派定义）如果被打包进 skill，就会出现两份、
> 必然会分叉。实测过：打包版本里有 4 个文件与仓库不同步，
> 用它建出来的库分类是错的。

它会把这些软链建到本机所有可用的 skill 目录：

| 目录 | 谁读它 |
|---|---|
| `~/.agents/skills/` | DSH / Codex / 通用约定 |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**为什么用软链**：skill 可以用 `pwd -P` 解析出自己的真实位置，
从而推断出仓库根目录 —— **仓库放在哪、移不移动都能自动找到**，不需要任何配置。
skill 里**没有写死任何路径**。

其他用法：

```bash
./install.sh --copy        # 复制安装（不用软链，但仓库移动后要重装）
./install.sh --uninstall   # 卸载
bash locate.sh             # 手动定位仓库（排查用）
```

装完**新开一个 AI 会话**才会生效。

### 方式四：接入 MCP（Claude Desktop / Cursor）

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<本仓库绝对路径>/_scripts/mcp_server.py"]
    }
  }
}
```

暴露 7 个工具：`search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories`。纯标准库实现，**不需要 pip 安装任何东西**。

---

## 它好在哪里

### 1. 不是图包，是可组合的结构

图包给你「这是什么感觉」，这个库给你「怎么做出这种感觉」。
每一层都可以单独摘出来复用，换主体不换风格层，就是风格迁移模板。

### 2. 光照层被单独拎出来了

大多数人写提示词时把一切混在一起，靠试错调。这个库明确告诉你：
**光照对最终质感的影响比风格词本身更大。**
每个流派的光照层都是独立一段，可以直接搬到别的主题上。

### 3. 每个流派都有「针对性负向词」

**针对这个流派的典型翻车点**：

- 印象派 → `black shadows, smooth blending, photorealistic`
- 文艺复兴 → `visible brushstrokes, impasto`（AI 默认会给油画加厚涂）
- 浮世绘 → `3d shading, cast shadows, gradient`（AI 会自动加立体感）

**注意不同流派的负向词经常是相反的**——这正是混搭会打架的原因，也是库帮你管住的东西。

### 4. AI 可以用，不只是你能看

大模型对艺术流派的记忆是模糊的，常把 Art Nouveau 和 Art Deco、
巴比松和印象派搞混。这个库把 141 个流派的具体术语固化下来，
AI 调用时不会瞎编。

### 5. 完整性有保证

关键词图谱**218 styles / 189 movements / 68 genres**

### 6. 只收公共领域，用起来不用想

全部图片来自 CC0 / 公共领域开放数据源，可以自由使用、修改、再分发，
也可以放进你自己的数据集。

### 7. 能扩展

加一个新流派只需要在一个 Python 文件里加一条定义。
抓图、生成笔记、关键词映射、AI 接口都会自动跟上。

---

## 快速开始

```bash
git clone https://github.com/YanKaFei/art-aesthetic-vault.git
cd art-aesthetic-vault

# 立刻能用的自检
cd _scripts && python3 artvault.py categories
```

**环境要求**：Python 3.8+ 和 Obsidian（推荐）。

**核心脚本只用 Python 标准库，不需要 pip 安装任何东西。**

可选依赖 —— 不装也能跑，装了多一层能力：

```bash
# Pinterest 抓取与投递箱
pip3 install --user requests Pillow

# 图片分析的增强维度（人脸景别 / 霍夫直线 / 显著性）与语义检索
pip3 install --target ./vendor/libs numpy opencv-python-headless
```

> 装到 `vendor/libs` 是为了不污染系统 Python，且该目录已 gitignore。
> 不想装：`ARTVAULT_NO_EXT=1` 可显式关掉增强维度。
> 另：`artvault_vision.py` 只在 macOS 上可用（依赖系统自带 Vision 框架），
> 其他系统会自动降级并说明原因，不影响任何核心功能。

---

## 自己重新生成 / 扩展

```bash
cd _scripts

python3 fetch_art.py                  # 补抓所有还没有图的流派
python3 fetch_art.py impressionism    # 只抓指定流派
python3 fetch_art.py --per 12         # 每个流派 12 张
python3 build_vault.py                # 用 mv_*.py 里的数据重新生成全部笔记
python3 make_links.py                 # 重新生成外部检索深链
```

### 加一个新流派

1. 在 `_scripts/mv_*.py` 对应的分类文件里加一条定义
2. 在**同一个文件的 `ARTIST_KEYS`** 里加过滤关键词 ← **必须，否则会抓进一堆无关作品**
3. `python3 fetch_art.py <slug>` 然后 `python3 build_vault.py`

| 数据文件 | 负责的分类 |
|---|---|
| `mv_core.py` | 最初的 18 个主干流派 |
| `mv_west.py` | 西方古典与近代 |
| `mv_asia.py` / `mv_asia2.py` | 东亚·南亚·伊斯兰 |
| `mv_modern.py` / `mv_gaps.py` | 现代主义与战后 |
| `mv_contemporary.py` | 先锋·当代·后现代 |
| `mv_visual.py` | 数字·亚文化·摄影美学 |
| `mv_photo.py` | 摄影与图像 |

---

## 工具清单

`_scripts/` 下每个脚本的分工。除了标注**可选**的，都只要 Python 3 + Pillow。

### 门面

| 脚本 | 干什么 |
|---|---|
| `artvault.py` | 主查询接口：`categories` `search` `layers` `show` `palette` `related` `compose` |
| `mcp_server.py` | 同一套能力包装成 MCP server，给 Claude Desktop / Cursor 直连 |

### 数据源与生成

| 脚本 | 干什么 |
|---|---|
| `movements.py` | 汇总 141 个流派定义，是**唯一数据源** |
| `mv_*.py` | 流派卡片与过滤关键词（按分类分成 8 个文件） |
| `providers.py` | 四个 CC0 数据源适配器 + 三层过滤（AI 图 / 平面作品 / 作者匹配） |
| `fetch_art.py` | 抓图：按来源轮转、两层过滤、`--refresh` 清孤儿图 |
| `build_vault.py` | **生成** Obsidian 笔记 / README / LICENSE / .gitignore |
| `make_links.py` | 生成外部检索深链 |
| `keyword_map.py` | 生成关键词图谱 |

### 图片分析

| 脚本 | 干什么 |
|---|---|
| `image_analysis.py` | 七维度客观测量：明度 / 对比 / 色彩 / 和谐 / 构图 / 质感 / 线条。纯 Pillow |
| `image_analysis_ext.py` | **可选**：人脸景别 / 霍夫直线 / 谱残差显著性。要 numpy + opencv，没装自动跳过 |
| `artvault_vision.py` | **可选**：macOS Vision 语义检索（以图搜图 / 近重复 / 相近流派） |
| `ingest_inbox.py` | 处理 `pinterest/` 投递箱，扫描时带上上面这些维度 |
| `verify_vault.py` | **验收检查**：断链 / 重名 / AI 图 / frontmatter / 近重复 / 授权 / 孤儿图 |
| `movement_fingerprint.py` | 用客观维度建流派指纹做图像→流派匹配（可解释，但实测不如 Vision） |
| `pinterest_grab.py` / `pinterest_export.py` | Pinterest 抓取与导出（本地自用，图**不入库**） |

### 两条容易被忽略的约定

1. **改生成物，先改模板。**
   `10-流派/*.md`、`00-导航/*.md`、`README.md` 全部由 `build_vault.py` 生成，
   直接编辑会在下次重建时被覆盖（这份工具清单本身也在模板里）。
2. **`20-我的提示词/` 是你自己的。** 脚本只读不覆盖，可以放心写。

---

## 三条原则

1. **宁可少，不要错。**
   筛选时刻意不做「放宽补充」——某个流派只有 1 张图就 1 张。
   一个参考库最怕的不是图少，是图错。错的参考会污染你的直觉，而且你自己不会发现。

2. **光照比风格词更重要。**
   如果你只有一个层可以调，调光照。

3. **不要凭记忆编造流派术语。**
   以大模型对艺术流派的记忆为准，容易把相近的画派搞混。以库里的具体术语为准。

---

## 图片来源

全部图片来自公共领域 / CC0 开放数据源（克利夫兰、芝加哥、大都会、维基共享），已逐条核对，可自由使用与再分发，每张作品下方都标注了来源与授权链接。

**代码** MIT ｜ **笔记内容** CC BY 4.0

---

<div align="center">

如果这个库对你有用，欢迎 Star ⭐ 或提交 PR 补充更多流派

</div>
