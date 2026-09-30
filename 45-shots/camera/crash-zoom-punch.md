---
type: 镜头卡
招式: crash-zoom-punch
类别: 运镜
类别slug: camera
能量: 高（瞬时冲击，非持续高能）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/camera/crash-zoom-punch.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - crash-zoom-punch
---

# crash-zoom-punch

> [!abstract] 这一下是什么
> 全景一拍急推到目标特写（6f），落位二选一——过冲回弹（弹性）或撞停震屏（重量）

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|运镜]] | 功能段"点名"镜头——把观众视线一拍按到目标卡/模块上；强调级用撞停 | 约 0.5s 动作 + 前后 hold（动作 6–11f，前 hold ≥30f 建立全景、后 hold ≥45f 读特写） | 高（瞬时冲击，非持续高能） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/camera/crash-zoom-punch.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

慢推近（spotlight-hero-card）是"请看"，急推是"看这个！"——一拍之内
从全景砸到特写，视线没有选择余地。落位质感分两款：回弹是弹性
（"看这个"），撞停震屏是重量（"就是它"），按强调级选。

## 动效核心

- zoom 6f ease-in 急加速（如 1→2.6），cx/cy 同步 ease-in 收敛到目标中心
- 回弹款：zoom 过冲后 5f 回收 3–6%（2.6→2.45）
- 撞停款：到位帧起机位高频抖 + 指数衰减（amp 14px、τ≈1.8f、6f 收干），
  不回弹
- `<CameraMotionBlur shutterAngle={200} samples={20}>` **只包急推段**
  （撞停震屏段保持清晰抖动）；采样按"回波间距 ≤ 字高"配（轮 A 判例）

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 急推时长 | 6f（4–8f） | >10f 读作普通推近，冲击感消失 |
| 目标 zoom | 2.4–2.8 | 终点构图以目标卡占画面 60–75% 为准 |
| 回弹幅度 | zoom 的 3–6% | 过大读作弹簧玩具 |
| 震屏包络 | 14px·e^(−t/1.8) | 幅度须过肉眼阈值（可感性判例），>20px 读作故障 |

## 已知坑

- 终点必须是高清纹理槽位（card4-hires 级）——急推后全程特写它，
  低倍截图糊字（Q2）；终点先按 Q2 的高分辨率栅格化技法处理
- 两款别混用：回弹后再震屏读作穿帮；一支片急推 ≤2 次（P4 手法去重精神）
- 参数经占位素材调校转正，非实战定稿，首次实战后回验

## 参考实现

demos/camera/crash-zoom-punch/
（CrashImpactReal.tsx / CrashZoomReal.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/camera/crash-zoom-punch.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/camera/crash-zoom-punch/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|运镜]]
