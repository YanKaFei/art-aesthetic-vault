---
type: 镜头卡
招式: word-relay-filmstrip
类别: 文字排版
类别slug: typography
能量: "中低（编辑部气质，节奏靠切词的\"咔哒\"感）"
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/typography/word-relay-filmstrip.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - word-relay-filmstrip
---

# word-relay-filmstrip

> [!abstract] 这一下是什么
> 左列黑白相间等高页面卡步进滚动、右侧衬线大词原位接力（名词恒定+动词轮换）——切词瞬间才滚动一格，词块垂直中心与当前页面卡中点精确对齐

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|文字排版]] | "一个主体 × 多种能力"的枚举段（Computer researches/builds/codes…）；作品集/案例流展示；产品多场景巡礼 | 每词期 ~1.5–2s × 3–4 词；全段 5–7s | 中低（编辑部气质，节奏靠切词的"咔哒"感） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/typography/word-relay-filmstrip.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

左边是证据（页面截图胶片），右边是论点（大词）：动词换一次，
胶片就步进一格给出新证据——文字与画面互为注脚。命门是**步进制**：
左列平时完全静止，只在切词瞬间滚动一格（滚动=换证据的机械动作），
持续滚动会让左列沦为背景装饰、切词失去"咔哒"感。第二命门是
**对齐**：大词块垂直中心必须与当前页面卡中点精确对齐（像素级），
歪了整个版式的"编辑部严谨感"就塌了。

## 动效核心

- 左列：等高页面卡纵向排列，黑白（深浅）强制相间以显滚动步进；
  切词窗口内 ease-in-out 滚动恰好一卡高，其余时间零位移
- 右侧：衬线体（Didot 类）两行——主体名词恒定，动词原位接力：
  旧词灰化淡出（先出），新词落位（后进），先出后进不许叠影
  （判例：v2 叠影"resebuilds"被抓）
- 对齐：词块总高的垂直中心 = 当前卡顶 + 卡高/2（实测 y=540@1080p，
  精确到个位像素）
- 滚动与切词同步：滚动起点=旧词开始灰化，滚动终点=新词落稳

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 页面卡 | 等高（530px@1080p）、黑白相间、约半屏宽 | 不等高/同色系读不出步进；卡太窄失去"证据"分量 |
| 词期 | ~45–60f/词 | <40f 读不完词+胶片看不清；词期不必均匀 |
| 滚动窗口 | ~12f ease-in-out，恰一卡高 | 持续滚动=命门违例；滚过头/不足读作机械故障 |
| 词接力 | 旧词 4–6f 灰化淡出 → 新词 6–8f 落位 | 同帧交叉必叠影；间隙 >10f 读作断片 |
| 垂直对齐 | 词块中心=当前卡中点（像素级） | 用户单点意见"文字高度和中间的页面中点要对齐"；差 >8px 可感 |
| 字体 | 衬线 Didot 类、动词字重比名词轻或同 | 无衬线会丢"编辑部"气质 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 与 text-column-converge 分工：那张是左右对峙合拢的揭晓戏；
  本卡是纵向证据流+原位接力，无合拢无揭晓
- 与 pill-slot-cycle 分工：那张是胶囊槽位轮换 UI 元素；
  本卡是版式级的图文对位系统
- 实战素材：页面卡应使用真实截图（demo 为灰条示意，残余差距
  已知）；截图亮度要人工分档保证相间可读

## 参考实现

demos/typography/word-relay-filmstrip/
（WordRelayFilmstrip.tsx）
原片出处：perplexity-promo.mp4 ≈76–90s

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/typography/word-relay-filmstrip.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/typography/word-relay-filmstrip/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|文字排版]]
