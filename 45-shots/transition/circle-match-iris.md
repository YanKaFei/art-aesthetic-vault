---
type: 镜头卡
招式: circle-match-iris
类别: 转场
类别slug: transition
能量: 中高
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/transition/circle-match-iris.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - circle-match-iris
---

# circle-match-iris

> [!abstract] 这一下是什么
> 圆心匹配光圈切——光圈从页面上圆形元素的圆心炸开，圈内新页的圆形图表接在同一个圆上；匹配剪辑给光圈一个语义锚点

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|转场]] | 前景有圆形元素（头像/图标/圆钮）、后景有圆形主体（donut 图/圆环进度）的接缝；转场技法卡 | 4.7s（锚点脉冲 30f + 光圈扩张 45f + 图表生长 55f + 静止 40f） | 中高 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/transition/circle-match-iris.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

普通 iris 光圈（词汇表原条目）从任意点开圈，观众只读到"换页了"。
本卡把它和 match-cut 焊死：光圈必须从前景一个**真实圆形元素**的圆心
炸开，圈内长出的新页里有个圆形图表恰好接在同一个圆上——观众看到的
是"头像的圆变成了图表的圆"，圆形本身完成叙事（这个人→这个人的数据）。
这是 match-cut 在 UI 语境里的落地形态：不靠构图巧合，靠语义圆对圆。
与穿越三式同属"后景在前景里预先在场"，但锚点是抽象形状而非容器。

## 动效核心

- **两景的圆严格同心是命门**：锚点圆心写死为一组常量（demo：CX=308,
  CY=384.8，手算自布局），clip-path circle、新景圆环、脉冲光环全部
  引用同一组常量——坐标各算各的必然错心
- 定睛引导：光圈开圈前锚点元素两次放大脉冲 + 两道扩散光环（30f），
  把视线钉在圆上再动
- 光圈 `clip-path: circle(r at x y)`，r 22→2100px（45f inOut cubic）；
  新景圆环同窗从 22→170px 生长——**接圆发生在扩张中途**（观众在
  光圈还没吃满屏时就看到圆被接住了），不是开完圈再画图
- 圆环 sweep：strokeDasharray = sweep×周长，rotate(-90) 从顶部起笔，
  中央数字随 sweep 同步计数

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 锚点脉冲 | 2 次 scale 1→1.15 + 光环扩两道 / 30f | 没有定睛引导，开圈瞬间观众找不到圆心 |
| 光圈扩张 | 22→2100px / 45f Easing.inOut(cubic) | 快于 30f 接圆读不到；圆心偏移 >10px 一眼穿帮 |
| 接圆时机 | 圆环在光圈扩张中途（~40% 进度）即可见并同心生长 | 开完圈再长图表 = 普通转场+普通图表动画，匹配感归零 |
| sweep | 45–100f 到目标值，数字同步计数 | 数字与 sweep 异步读作两个动画 |
| 收尾 | sweep 完成后真静止 ≥40f | R1 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 真实素材上锚点坐标从截图量测（devtools/标尺），量到的是元素盒不是
  视觉圆心——带内边距的头像取内容圆心；量完渲一帧对不齐就调常量，
  别信第一次量的数（同 transition-travel C 腔心判例）
- 前景锚点必须是**真圆**：圆角方块（border-radius < 50%）当锚点，
  开圈瞬间方圆错型一眼假；demo 里就是用白补丁把方块盖成真圆的
- 语义要成对：头像→个人数据、产品图标→产品指标——圆对圆只是形，
  "这个圆的内容变成它的展开"才是匹配剪辑成立的因
- 一缝一式规矩同 shot-transitions；本卡自带图表生长段，圈内新景
  别再叠入场动效

## 参考实现

demos/transition/circle-match-iris/
（CircleMatchIris.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/transition/circle-match-iris.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/transition/circle-match-iris/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|转场]]
