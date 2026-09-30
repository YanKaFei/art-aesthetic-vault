---
type: 镜头卡
招式: letterspace-materialize
类别: 开场
类别slug: opening
能量: 低（静谧仪式感，一次呼吸完成）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/opening/letterspace-materialize.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - letterspace-materialize
---

# letterspace-materialize

> [!abstract] 这一下是什么
> 大字距字标全字符并行连续描画结晶——所有字母同帧起笔、笔画像手写一样连续生长、同帧齐收成词；氛围底景上的品牌字标显影

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|开场]] | 片尾/片头品牌字标登场（SUPERHUMAN 式大字距全大写）；章节题字；needs 静谧/高级感的收束帧 | 静置 ~15f + 描画 ~50f + 终态静置 ≥30f；全段 3–4s | 低（静谧仪式感，一次呼吸完成） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/opening/letterspace-materialize.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

字标不是淡入也不是打字机，而是"结晶"：全部字母的笔画同时
开始连续生长，像一只看不见的手同时写所有字母，同一瞬间齐收
成词。两个命门：**连续**（笔画必须是连续画出的过程，不许遮罩
分段——先半截再另半截会被读穿；任何中间帧都该像"写到一半"）；
**同步**（所有字母同帧起笔、同帧完成——逐字错峰是打字机语义，
这里是整词一体的仪式感）。

## 动效核心

- 每个字符用骨架笔画 SVG path（单线条字形），pathLength 归一 +
  strokeDashoffset 从 1→0 连续描画
- 全字符共享同一进度 p：同帧起笔、pathLength 归一保证不同笔画
  长度的字母同帧齐收（不做 per-char delay/jitter）
- 字形比例：方正略宽（字面宽高比 ≈1.07，实测判例：竖长字形被
  裁"太竖长"）；细笔画+大字距（letterSpacing ≈0.6em）
- 描画曲线：整体 ease-in-out，中段略快首尾略缓（起笔收笔的手感）
- 底景：氛围渐变/实拍空镜（暮色山景类），字标是画面唯一动作

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 描画时长 | ~50f（f16 起 f68 收 @30fps） | <30f 读不出"画"的过程；>80f 拖 |
| 同步性 | 全字符同帧起收、零错峰 | 判例：逐字错峰版被裁"所有字母是在同一个时间完成书写" |
| 连续性 | pathLength 连续生长、无分段跳变 | 判例：遮罩分段版被裁"应该是连续的笔画画出来" |
| 字形 | 骨架单线、字面宽高比 ~1.07、笔画细 | 竖长（比 <0.8）被裁；粗笔画丢结晶感 |
| 字距 | ~0.6em | 大字距是本卡身份；<0.3em 改用普通描画卡 |
| 终态静置 | ≥30f | 结晶完成后必须让观众读一次整词 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 与 draw-svg-trace 分工：那张是通用描画（图标/插画/单元素）；
  本卡命门是**全字符同步**的整词结晶仪式，且限品牌字标语境
- 与 type-assembly-moves 分工：那张是字块组装（位移拼合）；
  本卡笔画从无到有生长，字符不位移
- 骨架字形需手绘 path（现成字体轮廓是双线勾边，描画观感不同）；
  9 字形工作量 ≈1h，实战优先复用 demo 里的字形库
- 原片（superhuman-promo）底景是实拍暮色山景+水面倒影；demo 为
  渐变近似，实战建议用实拍/AI 生成空镜

## 参考实现

demos/opening/letterspace-materialize/
（LetterspaceMaterialize.tsx）
原片出处：superhuman-promo.mp4 ≈4.5–6.5s

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/opening/letterspace-materialize.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/opening/letterspace-materialize/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|开场]]
