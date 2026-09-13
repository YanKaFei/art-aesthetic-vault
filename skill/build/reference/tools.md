# 反推：从一张图得到提示词（管道内部参考）

> [!note] 这份文档是给**动手改管线的人**看的，不是用户导航页。
> 库里用户的「反推」是**自动跑的** —— 图进库时（`scan_local.py` 或
> `ingest_inbox.py --archive`）就完成测量、流派匹配、七层组装，产物落在
> **那张图自己的卡**上（`15-我的图库/<流派>/<图片名>.md`）。
> 用户不需要知道底下用了什么工具。
>
> 这一页留给想扩展的人：当你想把「主体描述」也自动化时，该接哪个模型。

## 现在管线里已经做了什么（不需要外部工具）

| 步骤 | 实现 | 产物 |
|---|---|---|
| 客观测量 | `image_analysis.py`（纯 Pillow） | 七维 + 人脸/直线/显著性 |
| 流派匹配 | `clip_embed.py` + `clip_match.py`（CLIP ONNX） | Top-3 流派 + 把握程度 |
| 七层组装 | `reverse_prompt.py` | 按匹配到的流派卡取七层 |
| 视频提示词 | `video_prompt.py` | Seedance 五段式 + H3 自然语言 |
| 落成卡片 | `build_vault.py` | `15-我的图库/<流派>/<图片名>.md` |

**唯一算不出来的是「主体」**（画面里具体画了什么）—— 见下。

## 主体描述：为什么现在没做

试过 `Xenova/vit-gpt2-image-captioning`（量化后约 230MB，可行）。放弃的原因：

- 它对**绘画**的描述质量很差，只会给 `a painting of a man in a suit` 这种，
  对「这张图像哪个流派」没有增量信息
- 它需要自己实现自回归解码（约 150 行），是真实的维护成本
- **AI 直接看图比它准得多** —— 技能流程里 `read_image` 看一眼就能写出
  「穿红裙的女人站在窗边，逆光」这种句子

所以主体一栏**留空并明确标注**，让 AI 或用户填。不假装填好了。

**如果你确实要接一个描述模型**，候选见下面的「图 → 提示词」。它会给出
关键词骨架，但仍不擅长「指向想要」—— 只能当辅助。

---

## 候选工具（如果你要扩展管线）

> 下面这些是**管线外部**的工具，需要你自己装。库里已经内置的部分
> （测量、流派匹配、七层组装、视频提示词）不需要它们。
### 一、图 → 提示词（核心工具）

| 工具 | 仓库 | 作用 | 适合 |
|---|---|---|---|
| **CLIP Interrogator** | [pharmapsychotic/CLIP-Interrogator](https://github.com/pharmapsychotic/CLIP-Interrogator) | BLIP 描述 + CLIP 排序，输出 SD 友好的提示词 | **首选**，古典绘画/艺术图效果好 |
| **JoyCaption** | [fpgaminer/joycaption](https://github.com/fpgaminer/joycaption) | 从零训练的图像描述 VLM，描述自然语言化 | 需要**长句描述**而非关键词堆叠时 |
| **WD14 Tagger** | [turbo-boo/stable-diffusion-webui-wd14-tagger](https://github.com/turbo-boo/stable-diffusion-webui-wd14-tagger) | Danbooru 标签体系反推 | **动漫/角色/插画**，标签粒度极细 |
| **Local LLM Prompt Enhancer** | [EricRollei/Local_LLM_Prompt_Enhancer](https://github.com/EricRollei/Local_LLM_Prompt_Enhancer) | ComfyUI 节点，用本地 LLM 扩写提示词 | 视频提示词扩写（含 Wan 指南） |

> [!note] WD14 Tagger 的模型权重在哪
> 模型本身发布在 Hugging Face 上（作者 `SmilingWolf`，模型名形如 `wd-v1-4-*`）。
> 直接在 Hugging Face 搜索 `wd-v1-4` 即可，不要从第三方镜像下权重。

> [!tip] 组合用法（推荐）
> 1. CLIP Interrogator 拿到**关键词骨架**
> 2. JoyCaption 拿到**一句话描述**，用来理解画面意图
> 3. 你自己按七层表把两者归位 + 补上流派卡里的术语
>
> 不要把工具输出直接当提示词用——它擅长「描述已有」，不擅长「指向想要」。

### 二、审美打分

| 工具 | 仓库 | 作用 |
|---|---|---|
| **Improved Aesthetic Predictor** | [christophschuhmann/improved-aesthetic-predictor](https://github.com/christophschuhmann/improved-aesthetic-predictor) | CLIP+MLP 给图打美学分，可批量筛选参考图 |
| **LAION Aesthetics** | LAION 系列 | 大规模美学评分模型，用于数据集过滤 |

用途：把收集到的几百张参考图**批量打分排序**，只留高分图进仓库。

### 三、批量抓取与数据集

| 工具 | 仓库 | 作用 |
|---|---|---|
| **img2dataset** | [rom1504/img2dataset](https://github.com/rom1504/img2dataset) | 从 URL 列表批量下载/缩放/打包成数据集 |
| **本仓库脚本** | `_scripts/fetch_art.py` | 从 CC0 美术馆 API 抓图 + 元数据 |

### 四、提示词工程总纲

| 资源 | 链接 |
|---|---|
| Prompt Engineering Guide | [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) |
| 图像反推 Skill（中文） | [luozhilzh/image-prompt-reverse](https://github.com/luozhilzh/image-prompt-reverse) |

### 五、数据集：如果你想要 WikiArt 那个量级

不想一个个爬，可以用已发布的公开艺术数据集。它们自带
style / artist / genre 标签，比你自己爬完再标注省事得多：

| 数据集 | 内容 | 去哪找 |
|---|---|---|
| **ArtBench-10** | 6 万张，10 个流派，标签干净，专为风格研究做的 | Hugging Face / 论文附带数据 |
| **WikiArt 数据集** | 约 8 万张画作，带 style / genre / artist 标签 | Hugging Face / Kaggle 搜 `wikiart` |
| **AVA** | 25 万张，带美学评分 | 搜 `AVA aesthetic visual analysis` |

> [!tip] 为什么这条路更干净
> 数据集是**研究者已经发布出来供研究使用**的，授权链条比你自己爬清楚。
> 而且标签是结构化的，直接就能对应到这个仓库的流派卡上。

### 六、数据源（找参考图用）

| 源 | 授权 | 免密钥 | 本仓库是否使用 |
|---|---|---|---|
| [克利夫兰艺术博物馆](https://openaccess-api.clevelandart.org) | **CC0** | ✅ | ✅ 主力 |
| [芝加哥艺术博物馆](https://api.artic.edu/docs/) | **CC0** | ✅ | ✅ 主力（IIIF 分级取图） |
| [大都会艺术博物馆](https://collectionapi.metmuseum.org/public/collection/v1/search) | **CC0** | ✅ | ✅ 主力 |
| [维基共享资源](https://commons.wikimedia.org/w/api.php) | 逐条 | ✅ | ✅ 只取 PD/CC0 |
| [丹麦国立美术馆 SMK](https://api.smk.dk/api/v1/art/search/) | 公共领域 | ✅ | 🔶 可接入，需解析 IIIF v3 |
| [美国国家美术馆 NGA](https://github.com/NationalGalleryOfArt/opendata) | **CC0** | ✅ | 🔶 开放数据 82MB CSV |
| [史密森尼 Open Access](https://www.si.edu/openaccess) | **CC0** | ❌ 需 key | 🔶 DEMO_KEY 可测通路 |
| [Europeana](https://www.europeana.eu/en/apis) | 逐条 | ❌ 需 key | 🔶 demo key 可测通路 |
| [维基数据 SPARQL](https://query.wikidata.org) | **CC0** | ✅ | 🔶 结构化查询，另一种范式 |
| [史密森尼 Open Access](https://www.si.edu/openaccess) | **CC0** | ❌ 需 key | 可扩展 |
| [Rijksmuseum](https://data.rijksmuseum.nl/) | 公共领域 | ❌ 需 key | 可扩展 |
| [Harvard Art Museums](https://harvardartmuseums.org/collections/api) | 部分 CC0 | ❌ 需 key | 可扩展 |
| [史密森尼 / Europeana](https://www.europeana.eu/en/apis) | 逐条 | ❌ 需 key | 可扩展 |
| [WikiArt](https://www.wikiart.org) | **混合** | — | ❌ 只作浏览参考，见 [[版权与来源]] |

> [!tip] 想再加数据源
> 在 `_scripts/providers.py` 里写一个函数，返回统一的字段结构
> （title / artist / date / medium / image_url / page_url / source / license / license_url），
> 注册进 `PROVIDERS`，然后在流派的 `sources` 里写上 `"提供商名": ["查询词"]` 即可。

### 七、关于 WikiArt

WikiArt 的 `robots.txt` 是 `User-agent: * / Allow: /`，技术上**允许抓取**，
页面也是服务端渲染、用 curl 就能拿到。但它**不是**开放数据源：

- 网站自己的文字、编排、分类体系受版权保护
- 版权期内的作品，WikiArt 是以「合理使用」的**低分辨率**方式展示的
- 它没有免费的官方 API（只有商业授权）

**结论：可以用它找线索，不要把它的图和文字当成可自由分发的素材。**
详见 [[版权与来源]]。

---

### 另一个方向：把反推当成「给数据集打标」

如果你要处理的是**几百上千张**自己的图（不是几十张参考图），
人工确认就不现实了。这时该做的是：

1. 用上面的工具批量跑出关键词骨架
2. 用 `clip_match.py` 批量匹配流派（它支持一次编码多张，见 `suggest()`）
3. 用美学打分模型过滤掉低分图，只留高分
4. **按「把握程度」分层处理**：分差 ≥1.0 的自动归（实测准确率约 80%），
   其余进待确认清单

第 4 步是关键 —— 实测数据在 `skill/build/SKILL.md` 阶段 6：
分差 ≥1.5 覆盖 2% 准确率 100%，≥1.0 覆盖 7% 准确率 80%，
放宽到 41% 覆盖率时准确率掉到 54%。**不要试图全自动。**
