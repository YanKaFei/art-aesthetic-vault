---
type: 镜头卡
招式: space-camera-moves
类别: 运镜
类别slug: camera
能量: 高
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/camera/space-camera-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - space-camera-moves
---

# space-camera-moves

> [!abstract] 这一下是什么
> 3D 空间化运镜两式——exploded-view 爆炸分解（构件沿 Z 炸开再合体）、drone-dive-landing 无人机俯冲降落

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|运镜]] | 把平面页面当 3D 实体拍的高光段落；两式都是"大动作"，一支片合计 ≤2 次 | A 5s（炸开-悬停-合体全程）；C 3–5s 单向俯冲 | 高 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/camera/space-camera-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

depth-layer 卡是给平移加纵深——层在动、页面还是页面。这两式更进一步：
整页被当成一个 3D 实体，相机（或世界）绕着它做实拍级机动。两式叙事
语义各占一格：A 说"看看它由什么组成"（拆解展示，Apple 发布片语言）；
C 说"从全局俯瞰砸到主角"（上帝视角一头扎进 hero 特写，全景→焦点）。

## 两式选型

| 式 | 做法 | 适用段落 |
|----|------|----------|
| A exploded-view | 整页 3D 倾斜后构件沿 Z 轴错峰炸开悬停，一拍后逆序合体震屏收口 | 架构/组成展示："这个产品里有什么"；模块总览段 |
| C drone-dive-landing | 近垂直俯角悬停 → 猛扎俯冲 → 气垫减速停在 hero 卡特写 | 开场定场→入题；全局地图砸进单点的章节启动 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| A 空间基座 | perspective 1600 + 整组 scale 0.76 + rotateX 18° rotateY -12° + preserve-3d | 倾角是空间感来源；正视炸开读不出深度 |
| A 炸开 | 各构件 translateZ 60–320px 错落分布，错峰 3f，每层 14f ease-out-back(1.7) | back 回弹给"咔"一声的机械感；深度全同读作整页浮起 |
| A 合体 | 逆序 ease-in 12f，归位帧 2f 指数衰减震屏（幅 ~13px） | 震屏是落锤——没有它合体读作软趴趴的淡入 |
| A 深度锚 | 投影随 z·p 下移变虚 + 底板压暗 22% + 远层 brightness ↓28% | 三个线索缺一层间关系就糊 |
| C 行程 | 同一条 p 驱动 rotateX 72°→0 + scale 0.42→1.35 + translate 收拢；origin 钉死 hero 卡中心（如 518,335） | 一条 p = 一台相机一次机动；分开驱动读作三个动画打架 |
| C 速度曲线 | 主俯冲 25f Easing.in(cubic) 吃 82% 行程 → 气垫 20f Easing.out(poly(5)) 走 18% | 切换帧速度骤降 = 气垫顶住的体感；82/18 比例比帧数更关键 |
| C 氛围 | 全场包 CameraMotionBlur(shutterAngle 220, samples 9)；俯视期页面下方椭圆软影随落地收干 | 软影卖"悬空高度"；blur 卖速度，缺一维就假 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 两式都吃真实截图分层/高清纹理：A 需页面按构件切块截图（顶栏/侧栏/
  卡各自独立成图，整页一张图炸不开）；C 终点是特写，素材先按
  审美准则 Q2 的高分辨率栅格化技法处理
- C 式易错：Remotion 无 Easing.quint，写 Easing.poly(5)（本批实渲踩坑）
- A 式构件布局要绝对定位复刻原页面网格（demo 里 8 层复刻 FakeDashboard
  A），流式布局做不了 per-构件 translateZ

## 参考实现

demos/camera/space-camera-moves/
（DroneDiveLanding.tsx / ExplodedView.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/camera/space-camera-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/camera/space-camera-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|运镜]]
