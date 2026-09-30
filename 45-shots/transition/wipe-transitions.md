---
type: 镜头卡
招式: wipe-transitions
类别: 转场
类别slug: transition
能量: 中
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/transition/wipe-transitions.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - wipe-transitions
---

# wipe-transitions

> [!abstract] 这一下是什么
> 几何擦除转场两式——clock-wipe 时钟扫描（雷达指针扫一圈换页）与 blinds-slice 百叶窗切条（12 竖条错峰翻换成波）

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|转场]] | 新旧页都不动、一条几何边界扫过完成交接的通用转场；不依赖构图里有合适元素，哪儿都能用 | 单式 前态 ≥20f + 擦除 32–60f + 收尾 ≥40f，约 5s（150f） | 中 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/transition/wipe-transitions.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

转场库已有三族：穿越系（钻进去）、藏切系（遮住切）、体块系（页面是
实体）。本卡是第四族**几何擦除系**——新旧页都不动，一条几何边界扫过
完成交接，擦除的形状即语义：A 圆扫是"仪表盘刷新了一屏数据"，B 条扫
是"百叶窗逐叶翻面换页"。与 shot-transitions F 元素遮罩擦除的区别：
F 用页面内真实元素当遮罩（依赖构图），本卡是纯几何形——通用性即定位。
按语义选：数据刷新用 A，横向推进翻页用 B。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| A clock-wipe | B 页上层套扇形 clip-path polygon，指针从屏心 12 点顺时针匀速扫 360°，扫过处露 B；扫描沿带多层亮线 | 数据/状态刷新语义；仪表盘类页面 |
| B blinds-slice | 12 根 160px 竖条 overflow hidden + 内层整页负 margin 对位；条内 A scaleX(1-p) 左缘收缩、B scaleX(p) 右缘展开，错峰 delay 成波，缝上亮线随波扫 | 翻页/推进语义；横向阅读动线页面 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| A 扇形 | 中心屏心(960,540)、半径 1400 盖满四角，固定 73 顶点(SEGS=72) | 顶点数恒定且够密（40+）防锯齿跳变——命门 |
| A 扫速 | 30–90f 指针 0→360° 纯 linear，双向 clamp | 雷达要匀速；加缓动就不是雷达是钟摆 |
| A 亮线 | 四层 SVG line：26px 白 0.35 柔光 + 13px 白 0.60 + 9px 黑 0.55 暗描边 + 4px 白核 | 白底判例：纯提亮不可见，必须加暗描边；首渲 3px 白线太弱，加码 1.5x 才过 |
| B 波 | 20–52f：delay=列号×2f，每条 10f Easing.in(cubic) | 交接点恒为 x+160(1-p)，数学上无露底 |
| B 缝亮线 | 三层 SVG：16px 白 0.45 柔光 + 6px 黑 0.55 暗描边 + 3px 白核，进出各 2f 淡入淡出 | 同 A 白底判例 |
| 摘罩 | A 96f / B 52f 起条件卸载全部擦除结构，B 页直出 | opacity 0 不算摘，残留 clip-path 毁真静止 |
| 收尾 | A 54f / B 98f 真静止（≥40f） | R1 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 擦除边界必须带亮线/高光——无亮线的 wipe 读作 PPT 转场，命门；
  亮线在浅色区靠黑描边、深色区靠白核，两侧都要可读
- A 与 circle-match-iris 的区别：iris 是从锚点炸开的圆（半径在长），
  clock 是角度在扫（半径恒定）——别因为都是圆混用
- 几何擦除全片 ≤2 次，且 A/B 别同片连用（两次"边界扫过"读作模板感）
- 亮线淡出与摘罩必须同帧衔接（A 90–96f 淡出、96f 卸载），
  差一帧就是残线穿帮

## 参考实现

demos/transition/wipe-transitions/
（BlindsSlice.tsx / ClockWipe.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/transition/wipe-transitions.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/transition/wipe-transitions/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|转场]]
