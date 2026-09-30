---
type: 镜头卡
招式: rhythm-interrupt-moves
类别: 节奏
类别slug: rhythm
能量: B 中 / C 高
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/rhythm/rhythm-interrupt-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - rhythm-interrupt-moves
---

# rhythm-interrupt-moves

> [!abstract] 这一下是什么
> 打断节奏两式——jump-cut-punch-in 三级跳切推近、strobe-black-frames 频闪黑帧

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|节奏]] | 用"打断连续性"本身当节奏器：顿挫推近（B）、窒息逼近（C）；与 beat-cut-moves（切点排布）、montage-rhythm（段落呼吸）互补 | B ~4.5s / C ~4.5s | B 中 / C 高 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/rhythm/rhythm-interrupt-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

库内节奏卡管的都是"怎么切、切多密"；这两式管**怎么断**——观众预期
连续，你偏打断，打断方式即表达：B 是空间断——同构图三次无补间跳大
（1x→1.6x→2.6x），戈达尔跳切的顿挫，比连续推近更有"看这里、再近点、
就是它"的指令感；C 是存在断——画面与纯黑交替频闪且间隔收紧，
高潮前的窒息倒数。选型：强制聚焦指标用 B，高潮前蓄压用 C。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| B jump-cut-punch-in | transform-origin 钉目标中心，三档 scale 阶梯跳变（零补间），每跳 2f 加深脉冲当 tick | 逐级逼近核心指标；纪录片式盯住 |
| C strobe-black-frames | 全屏黑帧按写死帧号表闪现（每次 2f，间隔 8f→3f 收敛），末闪掀开即硬切放大落定 | 全片最高潮前的倒数蓄压 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| B 跳挡 | 1.0→1.6→2.6，各 hold ≥35f | 挡差 <1.5× 读作画面抖了一下 |
| B tick | 跳变帧起 2f brightness 0.92 全画面脉冲 | 无 tick 的跳切读作丢帧 |
| C 帧号表 | [40,48,55,61,66,70,73,76,79] 各 2f 纯黑 | 间隔必须收敛；等距频闪只是闪没有"逼近" |
| C 落锤 | 末闪掀开一帧到位 scale 1.35 + 2f 加深脉冲 | 掀开后还在原构图，频闪就白憋了 |
| 收尾 | B 末挡 ≥45f / C 硬切后 ≥50f 真静止 | 打断系事后 hold 从重给 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 两式与 speed-ramp-freeze 都动"时间轴"，同一镜头只能有一个时间
  操纵者
- C 式**光敏警示**：频闪画面需注意光敏性癫痫观众提示；且必须配乐
  渐强同步（无声频闪读作信号故障），全片 ≤1 次
- B 式三挡构图必须同 origin（钉死目标中心）——每挡重新构图就是
  三个镜头，不是跳切
- 声音强依赖：B 每跳一声 tick、C 每闪一声打点（sound-design §4.5）

## 参考实现

demos/rhythm/rhythm-interrupt-moves/
（JumpCutPunchIn.tsx / StrobeBlackFrames.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/rhythm/rhythm-interrupt-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/rhythm/rhythm-interrupt-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|节奏]]
