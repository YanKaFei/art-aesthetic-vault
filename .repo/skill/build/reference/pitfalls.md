# 踩过的坑

这份文档是这套流程里**最值钱的部分**。每一个坑都真实发生过、导致过返工。
照抄流程不会踩，自己重新发明一定会踩。

---

## 一、网络与抓取

### 1.1 `curl` 连不上 ≠ 站点连不上

**症状**：`curl` 测 Pinterest 全部返回 `http=000`，据此判断"站点不可访问"，放弃了。

**真相**：出口代理在做 **TLS 指纹识别**——拦 `curl` 的握手，放过 Python/OpenSSL。
同一个 URL，`curl` → 000，`python requests` → 200 + 1MB 真实 HTML。

**教训**：**判断一个站点能否使用，必须用你最终要用的那个客户端去测。**
不要用 `curl` 代测然后下结论。这一条让我白丢了一整轮。

### 1.2 维基共享资源：不要下原图，要下缩略图

**症状**：`upload.wikimedia.org` 原图返回 `429 Too many requests`。

**原因**：Wikimedia 对原图下载限流极严，官方要求改用缩略图。

**第二个坑**：自己拼 `/1024px-文件名.jpg` 又会返回
`400 Use thumbnail sizes listed on ...` ——**只有预渲染的标准宽度可用**，
而且部分文件只预渲染了少数几档。

**最终解法**：用 `Special:FilePath`，由服务端选尺寸：

```
https://commons.wikimedia.org/wiki/Special:FilePath/<文件名>?width=1024
```

这个端点稳定、会 302 到合法缩略图。**不要手拼 `/NNNpx-` 路径。**

> 宽度白名单：320 / 640 / 800 / 1024 / 1280 / 1920 / 2560。
> 请求宽度必须 ≤ 原图宽度，否则 400。

### 1.3 大都会 API 有失效条目

搜索返回的 objectID 里有 404 的。不要当成错误打印刷屏，静默跳过即可。

---

## 二、图片筛选（最容易毁掉整个库的地方）

### 2.1 泛化查询会混进完全无关的作品

**症状**：跑完第一版，一幅《圣杰罗姆的忏悔》出现在**几乎每一个流派**里。

**原因**：用「风格名」做 API 搜索词，返回的是相关性很低的宽泛匹配。

**解法**：**两层过滤**

1. **艺术家关键词**：维护每个流派的 `artist_keys`（画家姓氏 + 画派名），
   只有作者或文件名命中才收。
2. **平面作品过滤**：按媒介字段排除瓷器、家具、玻璃器（`is_flat_work`）。

### 2.2 关键词子串误命中（最阴的一类 bug）

实测踩到的：

| 关键词 | 误命中 | 原因 |
|---|---|---|
| `lange` | **Miche**lange**lo** | "michelangelo" 含 "lange" |
| `henri` | Henri **Fantin-Latour** | 谁的名字里都有 henri |
| `delaunay` | Nicolas **Delaunay**（17世纪） | 和 Robert Delaunay 同名不同人 |
| `morris` | William **Morris Hunt** | 另一个画家 |
| `church` | Henry **Church** | 和 Frederic Edwin Church 无关 |
| `gerard` | **Gerard** David | 和 François Gérard 无关 |
| `ernst` | **Ernst** Ludwig Kirchner | 和 Max Ernst 无关 |

**解法**：
- 关键词**优先用全名**（`dorothea lange` 而不是 `lange`）
- 加 `exclude_keys` 排除词机制
- 写完后跑一次**短关键词审计**：列出所有只靠 ≤6 字符关键词命中的条目，人工过一遍

#### 2.2.1 姓氏匹配的四类陷阱（加新关键词前必看）

给一个流派挑艺术家关键词时，姓氏会撞上四类东西。**这四类都不是「关键词写错了」，
而是「关键词天然不够」**，必须配 `exclude_keys`：

| 类型 | 实测例子 | 挡法 |
|---|---|---|
| **在世同姓者** | `delaunay` 命中 "Catherine Delaunay 2025 Jazz D'or Berlin" | 排除词难以穷举 → 优先用全名 |
| **别人给他画/拍的东西** | `klee` 命中 "August Macke, Zeichnung Paul Klee"；`malevich` 命中 "Ivan Kliun, Portrait of Kazimir Malevich"；`de kooning` 命中 "Elaine de Kooning, RIT NandE 1974" | `exclude_keys` 加 `macke` / `portrait of` |
| **签名 / 手迹 / 文献** | `balla` 命中 "Balla signature" | `exclude_keys` 加 `signature` |
| **匿名上传的人物照** | `malevich` 命中 "Casimir Malevich photo"（作者栏是 Unknown author） | `exclude_keys` 加 `unknown author` / `photo` |

**最容易误判的是第二类**：匿名作者 + 标题里有画家名 → 走「匿名标题兜底」路径被收进来，
但收进来的其实是**关于这个人的照片/别人画的肖像**，不是他的作品。
`exclude_keys: ["portrait of", "photo", "unknown author"]` 能一次挡掉大半。

#### 2.2.2 有些艺术家在这些 CC0 源里**根本没有真迹**

给 `abstract-art` 挑关键词时实测：`malevich` / `de kooning` / `rothko` 三个名字
在克利夫兰、芝加哥、大都会、维基共享里筛出来的**全是文献照片**，
一件真迹都没有（他们要么仍在版权期，要么源里只有档案照片）。

同一批查询里，两个源还会**在搜不到时回退成通用浏览列表**，返回任意 CC0 作品：

```
q=rothko  → Met 返回 Patinir / Vigée Le Brun / Gauguin / 周亮工
q=malevich → Met 返回和上面完全相同的那一批
```

**症状是计数异常整齐**（每个名字都返回 5 或 6 件）。这类结果会被 `artist_matches`
挡掉，不会污染库 —— 但它意味着**你以为能收的艺术家其实是空的**。

**解法**：挑关键词时先干跑一次，按「过滤后通过件数 / 其中作者栏是真人」统计：

```python
passed = [w for w in raw if artist_matches(w, keys, excl) and not is_ai_generated(w) and not is_flat_work(w)]
real   = [w for w in passed if not is_anonymous(w["artist"])]
```

`real` 才是真实可得数量。低于 3 件就别写进关键词了 —— 写了也是空跑。

#### 2.2.3 还有一个更隐蔽的：泛化词会拉进业余图库图

`abstract-art` 原来关键词里有 `"abstract"`，结果拉进来的是
"Abstract background image-03"（上传者 KawsarRushan）、
"Symmetrical Abstract Art - Bird Emoticon" 这类**业余/图库素材**，
不是艺术品。

**泛化形容词（abstract / modern / contemporary / decorative）几乎一定有害** ——
它们匹配的是上传者的描述习惯，不是艺术史分类。关键词尽量只放**人名**和
**专有流派名**。

### 2.3 维基共享的 `Artist` 字段常常是上传者，不是画家

**症状**：罗马式壁画条目的"作者"是 **Joe Mabel**（一个维基摄影师）。

**解法**：来自共享资源的作品**只按文件名匹配**（文件名通常含画家名），
并用 `extract_artist_from_title()` 从文件名还原真正的作者
（格式多为 `画家名 - 作品名` 或 `作品名 by 画家名`）。

### 2.4 匿名传统的作品没有作者名

敦煌壁画、唐卡、伊斯兰瓷砖、原住民艺术——**根本没有画家**。
按作者匹配会得到 0 条。

**解法**：让关键词表同时匹配**作品名/画派关键词**
（`dunhuang` `mogao` `thangka` `mihrab` `zellige`）。

### 2.5 器物类流派会被"只要平面作品"的规则误杀

侘寂的主角是**茶碗**，伊斯兰几何的主角是**瓷砖**——
按媒介过滤时会被当成"非平面作品"排除。

**解法**：给这类流派加 `allow_3d: true` 开关。

### 2.6 AI 生成的图会混进来（对参考库是致命的）

**症状**：维基共享上有大量 AI 生成图（DALL·E、Fooocus 上传），标注 CC0，
文件名形如 `DALL-E - Paintings in Magic Realism style`。它们渗进了"魔幻现实主义"。

**为什么致命**：一个**给 AI 生成做参考**的库，里面放着 AI 生成的图，
等于用模型的输出当模型的参考——会污染整个库的可信度。

**解法**：`is_ai_generated()` 黑名单过滤：
`dall-e` `stable diffusion` `midjourney` `fooocus` `ai generated` `novelai`
`comfyui` `sdxl` `flux` 等二十多个标记词。**建完库必须复扫一遍。**

### 2.7 图太大撑爆仓库

**症状**：美术馆的 `print` 尺寸单张 6MB，100 张就 600MB。

**解法**：克利夫兰用 `web` 尺寸（约 250KB），Met 用 `primaryImageSmall`，
把 `print`/`full`/`original` 留作"高清原图"链接。**单张控制在 300KB 上下。**

### 2.8 Obsidian 的 `![[文件名]]` 按 basename 解析

**症状**：两个流派都收了卡拉瓦乔的同一幅画，同名文件互相覆盖，
embed 指向了错误的那张（或随机一张）。

**解法**：文件名加 slug 前缀 → `01-barokk-the-crucifixion-of-saint-andrew.jpg`。
建完库**必须检查全库文件名唯一性**。

---

## 三、内容与方法

### 3.1 流派名单独写进提示词几乎没用

`baroque`、`impressionism` 这种词，模型只知道个大概。

**解法**：**七层拆解法**。流派名必须配上**光照 + 色彩 + 媒介**三层，
模型才知道你要什么。见 `method.md`。

### 3.2 负向提示词不能跨流派合并

**症状**：把配色、光照、构图来自不同流派的 `negative` 简单合并。

**后果**：
- 浮世绘禁止 `cast shadows`，而巴洛克的光照层恰恰要 `deep crushed shadows`
- 精确主义禁止 `people / figures`，而主体是个武士

**为什么危险**：**模型不会报错**。提示词里有互相矛盾的指令，
只会表现为"出图质量莫名其妙地差"，极难排查。

**解法**：组合提示词时**检出冲突并自动消解**，而不是只打印警告：

1. 词面冲突：某层的负向词出现在另一层的正向词里
2. 语义规则：负向词含 `people/figures/person` 而主体是人物 → 冲突

规则是「**正向是意图，负向是护栏，护栏让位于意图**」—— 打架的负向词直接从
负向提示词里删掉，并逐条记录「删了哪个、让位给谁」。

**为什么必须自动做，不能只警告**：实测抽 300 组跨流派混搭，**68% 会撞**。
只打印警告等于把这份手工活摊给每一个用混搭的人；而且警告是「软」的，
使用者看到一长串输出，很容易直接复制负向词那一行，把矛盾带进模型。
**默认行为就应该是可用的结果**，想自己判断的再给开关（`--keep-conflicts`）。

### 3.3 配色距离只能当参考，不能当结论

**实测**：一张油画调色板照片，配色距离算出最接近「现实主义」。
但那只是因为**土色系重合**，风格毫不相干。

**教训**：客观测量（尺寸、主色、哈希）交给脚本，
**风格判断必须由看图的那个来做**。

### 3.4 版权：不是所有"免费"都一样

| 类型 | 能做什么 |
|---|---|
| **CC0 / 公共领域**（克利夫兰、大都会、Smithsonian） | 下载、修改、商用、训练、再分发 |
| **CC BY / CC BY-SA**（部分共享资源） | 可以用，**必须署名** |
| **合理使用**（WikiArt 的版权作品） | 只能看，不能下载再分发 |
| **二次聚合**（Pinterest） | 版权归各自原作者，**无统一授权** |

**默认策略**：只收 PD/CC0，让整个库的授权状态单一（"随便用不用想"）。
需要更大覆盖面时用 `--include-ccby` 显式开启，并把署名记录下来。

**1950 年后的流派拿不到图是正常的**——抽象表现主义、波普、极简主义
的作品都在版权期内，任何开放数据源都不会给。它们生成**纯提示词卡**
（视觉语言与七层结构照常拆解），这是有意为之，不是缺陷。

### 3.5 WikiArt 能爬，但只该拿它的分类体系

`robots.txt` 是 `Allow: /`，页面服务端渲染，curl 就能拿。
但它**不是开放数据源**：版权作品是靠"合理使用"展示的低分辨率副本。

**正确用法**：抓它的 **218 styles / 189 movements / 68 genres** 分类体系
（事实性数据）作为**完整性骨架**，图片仍然来自开放数据源。

### 3.6 "宁可少，不要错"

**这是整个库最重要的原则。**

筛选时刻意**不做"放宽补充"**：某个流派只有 1 张图就 1 张，
**绝不为了凑数塞进无关作品**。

> 一个参考库最怕的不是图少，是图错。
> 错的参考会污染你的提示词直觉，而且你自己不会发现。

---

## 四、工程细节

### 4.1 生成的 Markdown 里不能放非法 YAML

`<!-- 注释 -->` 放在 frontmatter 里会让 Obsidian 的属性面板解析失败。
**YAML 注释必须用 `#` 开头。**

### 4.2 `str.format()` 遇到 JSON 示例会炸

笔记模板里有 `{"mcpServers": {...}}`，`.format()` 会把 `{` 当占位符。
**用 `.replace("{mark}", ...)` 而不是 `.format(mark=...)`。**

### 4.3 依赖不要装进 Obsidian 仓库

`pip install --target ./libs` 会往仓库里塞 170MB。
装是可以的（沙箱内唯一可行），但**必须写进 `.gitignore` 并排除同步**。

更稳的做法：让脚本**多路径查找依赖**
（`$ARTVAULT_DEPS` → `.repo/vendor/libs` → `~/.artvault/deps` → 用户 site-packages），
找不到就降级（只列文件，不报错退出）。

### 4.4 同步要保护用户的个人目录

`20-my-prompts/` 是用户自己写卡片的地方。
同步时用**两趟 rsync**：生成内容带 `--delete`，个人目录只增不删。

### 4.5 抓完必须验收

固定跑这几项，缺一不可：

```
1. 断链检查      —— 每个 ![[...]] 都能找到文件
2. 文件名唯一性  —— 全库 basename 无重复
3. AI 图复扫     —— is_ai_generated() 全库 0 命中
4. frontmatter   —— 无非法行（不出现 < 开头的行）
5. 近重复检测    —— 跨流派完全相同（距离 0.000）的图要人工过一遍
```

第 5 项用 T3 的语义检索跑（需要 macOS，可选）：

```bash
python3 artvault_vision.py build          # 先建索引，600 张约 8 秒
python3 artvault_vision.py dups --thresh 0.08
```

**为什么这一项值钱**：它一次就找出了 `abstract-art` 的问题 ——
那个流派仅有的 2 张图和 `de-stijl` 一模一样。

但要注意**大部分跨流派重复是合理的**，不是 bug：
一件作品本来就可以同时是多个流派的例证（Caravaggisti 属巴洛克、
Diego Rivera 同属壁画运动与社会现实主义、修拉《大碗岛》同属
后印象与新印象）。人工过的时候要判断的是：

- 重叠**说得通**吗（两个流派确有从属/交集关系）→ 保留
- 还是**关键词选错了**（该流派真正该有的作品一张都没有）→ 改关键词

---

## 五、一句话版

> **筛得狠，标的清，留证据，勤验收。**
>
> 图少没关系，错图会毁掉整个库的可信度。
