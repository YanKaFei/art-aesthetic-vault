---
type: 镜头卡
招式: icon-performance-moves
类别: 特效
类别slug: effects
能量: A 高潮点缀 / B 蓄势引入
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/effects/icon-performance-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - icon-performance-moves
---

# icon-performance-moves

> [!abstract] 这一下是什么
> 图标表演两式——pop-burst-confirm 爆花确认（对勾蓄力弹大+炸粒子+扩散环）与 attention-bounce 求关注弹跳（图标连跳递增+落地压扁+镜头被吸引）

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|特效]] | 半屏级 icon 特写段落；A "完成/成功"的标点符号，B 新功能引出 | A 3–4s / B 4–5s | A 高潮点缀 / B 蓄势引入 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/effects/icon-performance-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

库内图标动画品类首批入库：icon 是镜头怼着拍的表演者，不是 UI 角落的
微交互。A 是确认时刻的三连爆——大对勾先缩 0.6x 蓄力 3f、弹 1.35x 过冲
落回，同帧中心射出 10 根短线粒子+一圈描边环从边缘扩到 2.5 倍直径淡出，
"部署成功"不是画出来的是炸出来的；B 是 macOS Dock 语汇——app 图标
原地连跳 4 次一次比一次高（0.5→1.2 倍 icon 高），每次落地压扁
（宽 1.2x 高 0.8x）+溅尘点，跳最高那下镜头向它轻推 8%（被吸引），
落定后弹开功能面板——把"用户注意力"剪进叙事。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| A pop-burst-confirm | scale 蓄力-过冲-落回 spring + N 条径向 line translate + 圆环 scale/opacity，全程 ~20f，随后标签弹出 | 任务完成/部署成功/打勾时刻，卡点音效 |
| B attention-bounce | translateY 弹跳缓动递增 + 落地帧 scaleX/Y 挤压 + 尘点，峰值帧镜头 scale 1.08 推近，落定触发面板卡弹出 | 新功能引出："看我"→镜头看它→它开面板 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| icon 尺寸 | 400–500px 高（半屏特写） | 角落小图标做表演没人看见——表演者必须占 C 位 |
| A 蓄力 | 缩 0.6x 停 3f | anticipation：无蓄力的弹出没有"爆"感 |
| A 粒子/环 | 10 根短线飞 40–60px + 环扩 2.5 倍 | 三件套同帧齐发是"爆花"成立条件 |
| B 递增弹跳 | 4 跳 0.5→1.2 倍 icon 高 | 等高连跳读作 loading；递增才是"越喊越大声" |
| B 落地挤压 | 宽 1.2x 高 0.8x（1–2f） | squash 缺席=没有重量 |
| B 镜头推近 | 峰值帧 8% | 镜头动作把"被吸引"的观众视角演出来 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 同批 bell-swing-alert（铃铛甩摆）淘汰无附言——挂点摆动型 icon
  表演相性存疑，做新 icon 表演优先弹跳/爆发型
- A 与 particle-celebrate-hits 同属爆发点缀，同一段落二选一
- B 首版曾出画框（末跳最高点顶出），弹跳高度与画面上留白先算像素
- 声音：A 蓄力静默→爆发帧"pop"+粒子细响；B 每次落地一声"duk"
  音调递升，面板弹出一声轻"叮"

## 参考实现

demos/effects/icon-performance-moves/
（AttentionBounce.tsx / PopBurstConfirm.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/effects/icon-performance-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/effects/icon-performance-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|特效]]
