---
type: 镜头卡
招式: type-and-filter
类别: 交互
类别slug: interaction
能量: 中（发牌高能段之后的从容一拍）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/interaction/type-and-filter.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - type-and-filter
---

# type-and-filter

> [!abstract] 这一下是什么
> 真实 UI 上打字搜索、网格自己收敛成一张卡、点击穿透进详情页

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|交互]] | 功能演示的"操作叙事"段；搜索/筛选/进入详情的任何交互链路 | 约 2.5s（118–190f） | 中（发牌高能段之后的从容一拍） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/interaction/type-and-filter.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

让观众"跟着做一遍"：看清输入了什么、页面怎么响应、点了哪里。这是全片唯一模拟真人操作的镜头，节奏必须像人手，不能像脚本。

## 动效核心

- 相机上移到搜索框，逐字符打字，光标常亮→闪烁
- 打完留一口气，然后非目标卡按阅读序错峰淡出下沉，网格收敛
- 目标卡滑到首行槽位，途中浮起 + 阴影变宽
- 双圈强调色（模板片为琥珀）ripple 点击确认，相机推进穿透进详情页交棒转场

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 打字速度 | 3f/字符（TYPE_START=128，"nano-lab" 8 字符 ≈149 收尾） | 初版嫌快返工后的定稿值（"unhurried"）；交互演示按真人操作速度走（R3） |
| 呼吸位 | 打完到过滤 FILTER_START=160，留 ~11f（0.37s） | 打完立刻过滤读作机器自动，观众跟不上因果 |
| 光标 | 打字时常亮，之后 8f 周期闪烁；点击 176f，光标 185f 消失 | 打字中闪烁会读作卡顿；常亮→闪烁的切换本身就是"打完了"的信号 |
| 过滤退场 | 25 张非目标卡按阅读序 0.4f 间隔错峰，各 5f 淡出+下沉 8px | 同时消失读作页面崩溃；错峰哪怕只差 0.4f 也够 |
| 目标卡滑位 | 10f 滑到首行槽位，bezier(0.35,0,0.2,1)，途中 sin 浮起 z 18px、scale +0.02、阴影随浮起变宽 | 终点必须是布局真实槽位（Q9），滑到画面中央悬停就假了 |
| 点击确认 | 两圈同心强调色 ripple（起点差 3f、各 10f、半径 14→54/78）+ 3px 描边 + 40px 辉光，随后相机 16f 推进 zoom 2.2 | 单圈 ripple 太轻看不见；推进交棒给 flash-cut 盖住换页硬切（组件见 assets/lib/FlashCut.tsx，用法：from = 切点 − 5，跨骑硬切两侧各 5f） |
| 搜索框 | 页面底色补丁盖掉纹理里的 placeholder（保留放大镜图标），文字层叠上去打 | 直接在截图纹理上叠字会和烤入的 placeholder 重影 |

## 声音

打字段钉 keyboard.mp3 并按 Sequence 截 24f 与动作严格等长（S4）；点击钉 click-camera（全片最响 vol 0.6，S2 响度分层）；网格飞走钉 whoosh-fast。

## 已知坑

- 初版打字+过滤"太快了"被返工（R3）——交互镜头的第一版几乎总是偏快，起稿就按 3f/字符
- 过滤后目标卡若不归位到真实槽位、悬浮在网格上方，读作假（Q9，曾因此近乎整文件重写）

## 参考实现

demos/interaction/type-and-filter/TypeAndFilter.tsx（原 template/src/aifl/live/SceneFlyIn.tsx 118–190 段）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/interaction/type-and-filter.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/interaction/type-and-filter/TypeAndFilter.tsx（原 template/src/aifl/live/SceneFlyIn.tsx 118–190 段）` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|交互]]
