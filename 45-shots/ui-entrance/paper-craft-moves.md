---
type: 镜头卡
招式: paper-craft-moves
类别: 界面入场
类别slug: ui-entrance
能量: A 中（两拍打击）/ B 中高（立墙有纵深冲击）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/ui-entrance/paper-craft-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - paper-craft-moves
---

# paper-craft-moves

> [!abstract] 这一下是什么
> 纸艺两式——masking-tape-slap 纸胶带拍定（悬浮微晃被"啪啪"按死）与 popup-book-rise 立体书立起（卡片沿底边错峰立墙）

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|界面入场]] | 纸墨主视觉片的实体材料语言：单卡定妆入场用 A、整版 dashboard 开场建立用 B；与纸墨+强调色的主视觉（模板片为纸/墨/琥珀）天然同源 | A 3–4s / B 4–5.5s | A 中（两拍打击）/ B 中高（立墙有纵深冲击） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/ui-entrance/paper-craft-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

Wes Anderson 手账美术与立体书纸艺的 UI 翻译。A：卡片轻飘入位后
悬着微晃（未固定的纸），两条撕边半透明胶带"啪、啪"先后拍在对角，
第二条拍下**同帧**卡片停晃、投影变薄、整卡下沉——"按死"的定妆
一瞬是主角，两声"啪"是天然音效点。B：整页平躺如摊开书页（俯视），
卡片像贴在页上的纸片沿各自底边错峰立起成墙，立到 95° 回弹 90°
（纸的韧性），根部投影随立起收窄。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| A masking-tape-slap | 晃动=幅度包络×正弦（rot ±1.5°/bob ±5px）；胶带扑入 6f：scale 1.45→1 + rotate 欠 16°→过冲 7°→回正 + 落帧 scaleY 0.72 一帧压扁；撕边 14 点 clipPath 锯齿 | 单卡/徽章的定妆入场；文案重音对齐 |
| B popup-book-rise | 双层 3D：场景 rotateX 75° 俯视（persp 2600），每卡 rotateX 0→-90° spring（damping 11 过冲 -95°），origin 底边，preserve-3d 贯通；远排先近排后错峰 7f | 整版 dashboard 开场；"系统被搭建起来" |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| A 按死三件套 | 同帧：晃动 2f 归零 + 投影 34px→8px + 全卡下沉 2px | 三件拆帧就没有"按死"感；第一条胶带只把包络衰到 0.45（半死） |
| A 胶带质感 | 半透明 + 锯齿撕边 + 落点故意歪 2–3° | 歪斜是设计的手工感；直挺挺读作 UI 元素 |
| B 立起方向 | rotateX 0→**-90°**（向观众立起） | demo 判例：方向写反卡片往画面里倒被底板裁切 |
| B 根部投影 | blur 矩形不随卡立起，高 104→14px、透明度 0.26→0.1 随角度插值 | 无投影纸片浮空；投影跟着立起来穿帮 |
| B 收尾 | 全部站定后场景 75°→68° 轻回正（in-out cubic） | 直接定住少一口呼吸 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- A 的晃动是"未固定"的叙事铺垫不是手持抖动（Q3 边界）：
  振幅包络必须最终归零，全片只在被按死前存在
- B 与 tilt-reveal 分工：tilt 是**机位**抬头看静止页面，
  本卡机位基本不动、**构件自己**站起来
- B 立墙后卡片呈 90° 侧立态，文字不可读——立墙是构图动作，
  信息交给立起后的正视段落（Q6 同源）
- 声音：A 两声"啪"（纸拍击拟音）；B 每排立起一声轻纸响，
  错峰对齐（S2/S4 同源）

## 参考实现

demos/ui-entrance/paper-craft-moves/
（MaskingTapeSlap.tsx / PopupBookRise.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/ui-entrance/paper-craft-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/ui-entrance/paper-craft-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|界面入场]]
