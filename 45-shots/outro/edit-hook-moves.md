---
type: 镜头卡
招式: edit-hook-moves
类别: 收尾
类别slug: outro
能量: 低→瞬时中→低
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/outro/edit-hook-moves.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - edit-hook-moves
---

# edit-hook-moves

> [!abstract] 这一下是什么
> logo-sting-button 片尾钩子——片尾 logo 定住后突插 12f 彩蛋再收，预告片 button ending

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|收尾]] | 片尾收束（全片 ≤1 次） | ~5s | 低→瞬时中→低 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/outro/edit-hook-moves.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

库内声画卡管的都是"画面上的事"；这一式管**时间线本身的修辞**——
终点的反悔：收黑→logo 淡入定住（观众以为结束）→突然 12f UI 特写
彩蛋硬切插入→切回 logo 收尾，预告片 button ending，留最后一个钩子。
拿观众的"已经结束了"的预期开玩笑。

## 单式选型

| 式 | 做法 | 适用 |
|----|------|------|
| B logo-sting-button | 收黑 6f→logo 入场 10f（opacity+scale 0.96→1）→定住 30f→彩蛋 12f 硬切插入→切回 logo 真静止 ≥60f | 片尾；正片收束后再给一记 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 彩蛋时长 | 12f 级，内含 tick 圆点只亮第 4–5f（2f，条件挂载） | 长于 20f 就不是"眨眼"是一个镜头 |
| 彩蛋构图 | 面板 translate+scale(2.4) 特写按钮行，平移量把 sidebar 完全推出画面 | 彩蛋里露出旧构图残边读作切错了 |
| 像素级一致 | logo 段 interpolate 全 clamp 到终值，彩蛋前后 logo 共用同一分支渲染 | 硬切回来 logo 跳 1px 都读作抖动 |
| 剪辑方式 | 全程硬切分支渲染（frame 区间 return 不同子树），无交叉溶解 | 节奏靠剪不靠淡；任何溶解都泄劲 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 全片 ≤1 次且只在片尾——中段用 button ending 变成故障，
  观众以为片子坏了
- 彩蛋内容必须是全片未见的新特写——复用旧镜头读作剪辑失误
  不是钩子，命门

## 参考实现

demos/outro/edit-hook-moves/
（LogoStingButton.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/outro/edit-hook-moves.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/outro/edit-hook-moves/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|收尾]]
