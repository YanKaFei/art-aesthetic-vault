---
type: 镜头卡
招式: overhead-camera-moves
类别: 运镜
类别slug: camera
能量: A 中 / B 中高
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/camera/overhead-camera-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - overhead-camera-moves
---

# overhead-camera-moves

> [!abstract] 这一下是什么
> 俯拍揭示两式——tilt-reveal 俯仰抬正揭示、overhead-tabletop-drop 桌面卡阵横滑骤降扎入

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|运镜]] | 用"俯仰角"讲故事的开场/转场：单页 establishing 用 A，多页巡视择一扎入用 B | A ~4.8s / B ~4.7s | A 中 / B 中高 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/camera/overhead-camera-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

库内俯拍视角一直空缺——crane-rise 是"平移+缩放"的升起（俯仰角
不动），space-camera C 式 drone-dive 是俯冲降落一镜到底；这两式让
**俯仰角本身讲故事**：A 是揭示——整页 rotateX 平躺、开场只见上缘
一条透视窄带，机位"抬头"回正，内容一排排涌入视野，像掀开桌上的
图纸；B 是选择——三张页面卡平躺成桌面卡阵，相机俯拍横向滑过依次
掠过（韦斯·安德森 tabletop），滑到目标页猛地俯冲扎入、抬正成满屏，
"巡视一圈，就选这张"。选型：单页开场用 A，多页转场/开场用 B。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| A tilt-reveal | perspective 容器内整页 rotateX -80° 平躺，~43f 抬正，rotateX/scale/translateY 共用 out-cubic，末端轻过冲 | 开场 establishing；单主体 |
| B overhead-tabletop-drop | 卡阵平躺 rotateX 62°，pan 段只动 translateX 横滑掠过，drop 段角度/缩放/位移三通道同跑扎入落版 | 多页巡视后择一；转场/开场两用 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| A 俯角 | rotateX 关键帧 [-80, 2.6, -0.9, 0]（f25→68→72→76），transformOrigin 50% 0% | 首版 -55° 太弱：f0 仍见半页，无"窄带"悬念（实渲判例） |
| A 联动 | perspective 600→1200、perspectiveOrigin 5%→40% 随进度插值；scale 3.2→1 + translateY 200→0 | perspective 不联动则俯角初始见不到"只露顶栏" |
| A 收尾 | 全部动画 f76 结束，145f 留 69f 真静止 | 过冲幅度 ≤3°，再大读作弹簧不是机位 |
| B pan 段 | 0–55f 只改 translateX +700→-650（in-out cubic），角度不动 | pan 段动角度 = 两段职责糊掉（判例：pan 巡视、drop 表态） |
| B drop 段 | 55–85f 三通道同跑：rotateX 62→-1.8→0.6→0（out-cubic 过冲）、scale 1→2.04→2.0、translateX -650→0 | 三通道必须同跑；分先后读作两个动作 |
| B 卡阵 | 卡片 996×560（16:9 精确比），落版 scale 2.0 恰满屏正视；transform 顺序 translateX→rotateX→scale | 顺序错了 pan 会带出弧线轨迹 |
| B 地板 | 浅灰网格地板 | 无地板参照，横滑段读不出"相机在动" |
| B 收尾 | 全部动画 f93 结束，140f 留 47f 真静止 | — |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 大角度透视下卡片必须 backfaceVisibility hidden + translateZ(4px)
  兜底，否则个别帧背面/深度穿帮
- A 与 crane-rise-reveal 同片二选一——都是开场揭示，两个"揭示开场"
  等于没有揭示
- B pan 段角度锁死是命门（两段职责分离判例）：巡视归巡视、扎入归
  扎入，混着动观众不知道相机想干嘛
- 两式都是"相机大动作"，与 space-camera/crane-rise 同屏段落互斥，
  一个段落只能有一个持镜人

## 参考实现

demos/camera/overhead-camera-moves/
（OverheadTabletopDrop.tsx / TiltReveal.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/camera/overhead-camera-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/camera/overhead-camera-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|运镜]]
