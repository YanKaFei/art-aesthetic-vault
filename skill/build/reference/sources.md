# 数据源与授权

全部经实测验证（2026-09）。**判断可达性必须用最终要用的客户端测，不要用 curl 代测。**

---

## 一、图片源（按推荐度）

### 1. 克利夫兰艺术博物馆 ★ 主力

```
https://openaccess-api.clevelandart.org/api/artworks/?q=<词>&cc0=1&has_image=1&limit=20
```
- 授权：**CC0 1.0**（无条件公共领域奉献）
- 免密钥，**一次请求返回完整元数据**（标题/作者/年代/媒介/图片URL）
- 图片尺寸：用 `images.web.url`（约 250KB），`print`/`full` 留作高清链接
- 支持 `cc0=1` 服务器端过滤

### 2. 大都会艺术博物馆 ★ 主力

```
搜索：https://collectionapi.metmuseum.org/public/collection/v1/search?q=<词>&hasImages=true&isPublicDomain=true
条目：https://collectionapi.metmuseum.org/public/collection/v1/objects/<objectID>
```
- 授权：**CC0 1.0**（Open Access）
- 免密钥。搜索返回 objectID 列表，**每个条目要单独请求**（慢，注意限速）
- 用 `primaryImageSmall`（约 600px），`primaryImage` 留作高清链接
- ⚠️ 搜索里混有 404 的失效条目，静默跳过

### 3. 维基共享资源 ★ 补全非西方与现代

```
搜索：https://commons.wikimedia.org/w/api.php?action=query&format=json
      &generator=search&gsrsearch=filetype:bitmap <词>&gsrnamespace=6&gsrlimit=30
      &prop=imageinfo&iiprop=url|extmetadata|size&iiurlwidth=1024
下载：https://commons.wikimedia.org/wiki/Special:FilePath/<文件名>?width=1024
```
- 授权：**逐条判定**。读 `extmetadata.LicenseShortName`，只收
  `Public domain` / `CC0`（可选 CC BY）
- 覆盖东亚/南亚/伊斯兰/摄影等前两个馆缺的部分
- ⚠️ **三个大坑**（详见 `pitfalls.md`）：
  - 不要下原图（429），用 `Special:FilePath`
  - `Artist` 字段常是上传者不是画家 → 按文件名匹配
  - **有 AI 生成图混在里面，必须过滤**

### 4. 其他可用（需免费 key，未接）

| 源 | 授权 | 备注 |
|---|---|---|
| 史密森尼 Open Access | CC0 | 需 key |
| Rijksmuseum | 公共领域 | 需 key |
| Harvard Art Museums | 部分 CC0 | 需 key |
| Europeana | 逐条 | 需 key |
| 芝加哥艺术博物馆 | CC0 | API 免密钥，但**图片 CDN 有 Cloudflare，脚本下不了**（元数据可用） |

### 5. WikiArt —— 只拿分类体系

- `robots.txt` 是 `Allow: /`，页面服务端渲染，**技术可爬**
- 但**不是开放数据源**：版权作品靠"合理使用"展示低分辨率副本
- **正确用法**：抓它的分类体系当完整性骨架
  ```
  https://www.wikiart.org/en/paintings-by-style        → 218 styles
  https://www.wikiart.org/en/artists-by-art-movement   → 189 movements
  https://www.wikiart.org/zh/paintings-by-genre        → 68 genres（带繁中名）
  ```
  每个条目带作品数，中英对照可按**出现顺序**对齐（218/218 同序已验证）
- ❌ 不要下载它的图片进仓库

### 6. Pinterest —— 只能按分类抓

```
分类页（服务端渲染）：https://www.pinterest.com/ideas/<分类>/<数字ID>/
图片：https://i.pinimg.com/originals/...
```
- ⚠️ **`curl` 返回 000，Python `requests` 返回 200**（TLS 指纹被拦）
- ✅ 可用：`/ideas/` 分类树（10 个顶层分类 + 各 5 个子分类）
- ❌ 不可用：
  - `/resource/BaseSearchResource/get/` → 403（`pinscrape` 等维护中的库也失败）
  - `/ideas/<关键词>/` → 200 但无图（必须带数字 ID）
  - `/search/pins/?q=X` → JS 渲染，HTML 里没数据
- **结论：按分类抓可以，按关键词搜不行。** 关键词检索用深链在浏览器里做。
- 授权：**二次聚合，版权归各自原作者，无统一授权**。只做个人参考，**不要公开**。

---

## 二、官方 API 里的搜索能力（Pinterest 为例）

| 端点 | 能力 | 限制 |
|---|---|---|
| `GET /v5/search/partner/pins` | 按关键词搜**全站** | ⚠️ beta，需单独申请，**只返回前 10 条** |
| `GET /v5/search/pins` | 只搜**自己账号**的 pin | 搜不到别人的 |
| `GET /v5/search/boards` | 只搜**自己账号**的 board | 同上 |

**"导出自己的收藏"是完全合法且实用的路径**（`boards:read` + `pins:read`），
工作流：人工在 Pinterest 策展 → API 导出 → 进仓库 → 反推提示词。

---

## 三、"能链接"和"能抓取"是两件事

抓不到不等于用不了。三条并行的路径：

| 路线 | 合法性 | 适用 |
|---|---|---|
| **① 深链跳转** | ✅ 完全合法 | 用你自己的浏览器会话访问，等同地址栏输入 |
| **② 官方 API** | ✅ 需授权 | 导出自己的数据；全站搜索申请 beta |
| **③ 第三方抓取库** | ⚠️ 违反 ToS | 只在个人网络下、个人用途 |

**深链生成**是性价比最高的一条：为每个流派的技法术语生成
`https://www.pinterest.com/search/pins/?q=<技法词>` 之类的链接，
用户在浏览器里点开——**不需要爬，也没风险**。

---

## 四、授权分级（决定"这些图能干什么"）

| 级别 | 来源 | 能做什么 |
|---|---|---|
| **CC0 / 公共领域** | 克利夫兰、大都会、Smithsonian | 下载、修改、商用、训练、**再分发** |
| **CC BY / CC BY-SA** | 部分共享资源 | 可以用，**必须署名** |
| **合理使用** | WikiArt 的版权作品 | 只能看，不能下载再分发 |
| **二次聚合** | Pinterest | 版权归原作者，**无统一授权** |

**默认只收 PD/CC0**，让整个库的授权状态单一（"随便用不用想"）。
需要更大覆盖面时显式开启 CC BY，并把署名信息一并记录。

### 建库时的硬性要求

1. 每张作品**必须记录**：来源、授权名称、授权链接、原始页面 URL
2. 版权期内的作品**不存图，只存提示词结构**
3. `99-附件/images/<非CC0来源>/` 目录**写进 `.gitignore`**
4. 在库里放一份 `版权与来源.md`，把上表抄进去

---

## 五、1950 年后的流派拿不到图是正常的

抽象表现主义、波普、极简主义、观念艺术、超扁平、赛博朋克……
作品**都在版权期内**，任何开放数据源都不会提供。

它们应该生成为**纯提示词卡**：视觉语言与七层结构照常拆解，只是不配图。

> 这是授权策略的自然结果，**不是缺陷**。
> 硬塞图只会塞进错的。

---

## 六、预估产出（141 流派规模）

| 项 | 数量 |
|---|---|
| 流派卡 | 141 |
| 有实图的 | 约 80 |
| 纯提示词卡 | 约 61 |
| 图片 | 约 370 张 / 约 140 MB |
| 总笔记 | 约 180 篇 |
| 抓取耗时 | 首次全量约 60–90 分钟（受大都会 API 限速制约） |
