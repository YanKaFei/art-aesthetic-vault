---
type: 镜头卡
招式: document-typewriter-reveal
类别: 文字排版
类别slug: typography
能量: 低中（信息密度最高，节奏放稳让观众读字）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/typography/document-typewriter-reveal.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - document-typewriter-reveal
---

# document-typewriter-reveal

> [!abstract] 这一下是什么
> 整页真排版文档在光标后自己"写"出来、侧栏跟进、历史条目逐个落入轨道

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|文字排版]] | 文档/报告/笔记类功能镜头；信息密度最高的一拍 | 约 3.7s（110f，含 history-list-stack 尾段） | 低中（信息密度最高，节奏放稳让观众读字） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/typography/document-typewriter-reveal.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

观众会读清屏幕上每个字——这一镜的说服力全在"文档是真的"。打字机式写入把静态页面变成"正在被写出来的文档"，侧栏历史条目落入补上"持续产出"的时间纵深。

## 动效核心

- 内容块两两一对按节拍写入：页面底色遮罩右锚左→右收窄，强调色 caret 骑在揭示前沿
- 人名 @-mention 在 wipe 完成后长出强调色底色
- 左右双栏靠底色补丁上→下收走入场，内缘强调色细线随揭示生长后淡去
- 尾段（history-list-stack）：6 条历史条目从上方逐个落入侧栏轨道，每落一条配一声 pop
- 相机从标题特写拉到全页（双栏必须都入画），之后只做微呼吸

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 写入节拍 | 20 块两两一对，第 g 对 cue = 6 + g·3.5，每块 wipe 8f，最后一对 ~49f 完成（赶在 64f 全页 settle 前） | 逐块写会超预算——"块数×节拍要先对预算"是这卡的核心算术，先算再写 |
| 写入手法 | 底色遮罩 width 100%→0，bezier(0.4,0,0.6,1)；强调色 caret 2px 只跟最新块，写完 2f 淡出 | caret 同时出现多个立刻穿帮；永远只有一个"笔尖" |
| li 圆点 | 遮罩向左多盖 28px（::marker 在文本左 ~22px） | 不多盖圆点会提前穿帮——截图纹理里烤入的排版细节都要这样排查 |
| @-mention | wipe 完成后 4f 起、8f 长出强调色底色 opacity 0.7；跳过非人名标题 | 高亮晚于写入才读作"重点被标出"；同帧出现读作贴图 |
| 双栏入场 | 左栏 cue 46 / 右栏 cue 54，底色补丁上→下 10f 收走 + 内缘 1.5px 强调色线随揭示生长、24f 淡去 | 双栏与正文错开节拍，同时入场会互相抢视线 |
| 历史条目落入 | 6 条，cue = 58 + i·5（排在侧栏 wipe 完成 56f 后），每条 8f 落下；起点 −44px，bezier(0.2,1.15,0.3,1) 轻弹跳，空中影 `0 10·air px 20·air px` | 条目几何紧贴烤入纹理已有条目的下方、行高对齐——DOM 重绘条目必须和纹理里的活条目严格对齐 |
| 相机 | 标题特写 zoom 1.25 → 64f 全页 zoom 0.997，78/102f 1.003/0.995 微呼吸 | 全页时双栏必须都入画——文档镜头砍掉侧栏等于砍掉"完整产品"的说服力（Q10） |

## 声音

写入段钉 keyboard.mp3 修剪到 44f 盖住书写段（拟音与动作严格等长，S4）；历史条目 6 连 pop 每 5f 一发、音量 0.40→0.25 阶梯递减做距离衰减（S2）。

## 已知坑

- mock 内容必须出版级：产品原生排版、文字铺满、侧栏完整入镜（Q10）——"贴图+标语"级的敷衍文档会导致整镜头重做
- 数据合规：mock 内容里绝不出现客户/成员真名（Q1）
- 素材页面是活数据源（协作文档类）时，全量重采会刷掉已定稿纹理——用增量脚本只刷单页单键
- 强调色示例（caret/@-mention/内缘线）在模板片中为琥珀色，适配新品牌时统一换成目标品牌强调色

## 参考实现

demos/ui-entrance/document-typewriter-reveal/DocumentTypewriterReveal.tsx（原 template/src/aifl/live/SceneWbr.tsx；打字音效见 template/src/aifl/Main.tsx SFX 表；模板片中此镜承载的是周报文档场景）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/typography/document-typewriter-reveal.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/ui-entrance/document-typewriter-reveal/DocumentTypewriterReveal.tsx（原 template/src/aifl/live/SceneWbr.tsx；打字音效见 template/src/aifl/Main.tsx SFX 表；模板片中此镜承载的是周报文档场景）` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|文字排版]]
