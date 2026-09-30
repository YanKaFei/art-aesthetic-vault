---
type: 镜头卡
招式: cloner-depth-echo
类别: 界面入场
类别slug: ui-entrance
能量: 中（陈列-收束型）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/ui-entrance/cloner-depth-echo.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - cloner-depth-echo
---

# cloner-depth-echo

> [!abstract] 这一下是什么
> 克隆纵队——主卡瞬间"复印"出 7 个半透明分身沿斜向纵深排开成队，停一拍后全体加速吸回本体合一+弹跳

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|界面入场]] | "多副本/多租户/规模感/批量处理"卖点；一镜讲完"一个=很多" | 4–5s | 中（陈列-收束型） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/ui-entrance/cloner-depth-echo.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

Spline/C4D Cloner 语汇的 UI 翻译：一张主卡"啪"地复印出 7 个克隆体
沿 Z 轴向后等距排开（间隔 120px、透明度 100%→20% 递减），错峰弹出
成纵队；停 ~25f 让观众数得清"有很多个"；然后全体 ease-in 加速吸回
本体合一，合体瞬间本体弹 1.08x 收束。与 depth-layer-moves 视差
（不同内容分层）分工：这是**同一内容**的等距重影阵列，语义是规模
不是空间。

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 斜向错位 | dx=64·idx / dy=−34·idx | **命门**：纯 translateZ 排开在正视角下克隆体全被本体挡住（不可感）；斜向错位让纵队肉眼可见 |
| 侧视角 | 整队 rotateY 16° | 8° 仍近正视，16° 纵队清晰 |
| 克隆数/间隔 | 7 个 / 120px | 少于 5 读不出"队"，多于 9 尾部糊成一团 |
| 透明衰减 | 100%→20% 线性 | 越远越淡=纵深证据；等透明读作贴纸阵 |
| 排开/吸回 | spring 错峰 1.6f/个；merge ease-in 10f 全体同步 | 排开要错峰（复印感），吸回要同步（收束感）——节奏不对称是设计 |
| 合体弹跳 | sin(spring×π) 单脉冲 1.08x | 吸回无弹跳读作淡出；弹跳=质量证据 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 克隆体必须从后往前渲染保证遮挡正确；透明度 ≤0.005 条件卸载
- 同批 3D 渠道另两条（厚板转台淘汰、走廊改改再看）——纯陈列型
  3D 运镜相性存疑，本卡过墙靠的是"排开-吸回"的叙事动作，
  实战别退化成静态纵队陈列
- 声音：排开一串细"啪"错峰，吸回一声上扬 whoosh，合体一声实"咚"

## 参考实现

demos/ui-entrance/cloner-depth-echo/
（ClonerDepthEcho.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/ui-entrance/cloner-depth-echo.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/ui-entrance/cloner-depth-echo/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|界面入场]]
