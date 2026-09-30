---
type: 镜头卡
招式: paper-plane-messenger
类别: 转场
类别slug: transition
能量: 中
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/transition/paper-plane-messenger.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - paper-plane-messenger
---

# paper-plane-messenger

> [!abstract] 这一下是什么
> 纸飞机信使转场——点击"发送"后镜头拉远脱离窗口 A，折纸飞机沿贝塞尔弧线飞出（俯仰跟随切线），镜头伴飞穿过多层视差道具，飞抵窗口 B 门前落定，B 放大接管全屏

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|转场]] | "发送/邀请/分享"动作连接两个人物/场景视角的叙事转场；抽象动作需要一个隐喻实体当转场载具时 | ~5s（150f：点击 12f → 拉远 16–42f → 飞行 34–104f → B 接管 112–146f） | 中 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/transition/paper-plane-messenger.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

transition-travel 是镜头钻进画面里的既有元素换景；本卡反过来——从
动作里**放出一个语义信使**，让镜头跟着它飞去下一个场景。"发送"这个
抽象动作被实体化成折纸飞机，A/B 两窗的空间关系被飞行轨迹真实丈量
过，观众对"消息去了哪"有了身体感。命门是 2.5D 相机管线：所有元素
挂在同一世界坐标系上，镜头中心 A→跟飞机→B、变焦拉远再推近，视差
道具按 depth 乘相机位移——重 3D 原片降级成一台"假三维"，成本掉一个
量级而纵深感保留。飞机俯仰角跟随弧线切线是"它在飞"而非"它在平移"
的全部区别。

## 动效核心

- 世界坐标系相机：`screen = 960 + (world − camCenter) × zoom × depth`；
  镜头中心 A(520,560) → 跟飞机 → B(3200,600)，变焦 1.55（贴脸 A）
  → 0.62（拉远伴飞）→ 3.1（B 接管全屏）
- 飞机三次贝塞尔：A 发送按钮 → 高抛控制点（y=−80）→ 下压控制点 →
  B 门前；朝向 = bez(t) 与 bez(t+0.012) 的 atan2 切线角
- 飞行整体缓动 Easing.bezier(0.45,0.05,0.25,1)（起飞加速、落定
  减速）70f；途中 scale 放大 1.7 倍保可读，落定收回 1.1
- 视差道具 16 件（圆环/圆角方块，seed 随机）分 depth 0.45/0.75/1.3
  三层，远层 blur3、近层 blur8 焦外；各带正弦漂浮
- 飞机 = SVG 三块折面（白/浅灰/深灰示折痕）+ 描边；入场
  Easing.back(1.6) 弹出，B 接管期 opacity 淡出不留残影
- 点击脉冲：按钮 scale ×1.22 + 扩散圈（CLICK 12f 起 3f 峰值）

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 变焦三段 | 1.55 → 0.62 → 3.1 | 不先拉远直接跟飞，观众不知道 B 在哪个方位；拉远 <0.7 才装得下旅程感 |
| 飞行时长 | 70f，ease-in-out | <45f 读作弹射；匀速读作拖拽平移 |
| 切线采样 | dt = 0.012 | 太大角度滞后、太小抖动；俯仰角是"飞"的命门，删掉立即变贴图滑动 |
| 途中放大 | ×1.7（0.25–0.75 区间），落定 ×1.1 | 拉远后飞机只剩几十像素，不放大就丢主角 |
| 视差层 | depth 0.45/0.75/1.3，远 blur3 近 blur8 | 全同 depth 就没有穿越感；近景不虚会抢飞机视线 |
| B 接管 | 112–146f，变焦推到 3.1，道具/飞机同步淡出 | 道具不淡出会在推近时变成巨大糊块扫过全屏 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 与 transition-travel 分工：那卡钻进**画面里既有的**元素/容器完成
  换景（空间早已在构图里）；本卡**放出一个新实体**连接画外的第二场景
  ——A/B 无既有空间关系时才轮到本卡
- 与 glow-flyline-moves B（flyline-arc）分工：飞线是暗场数据流向的
  抽象示意（线是主角），本卡是明场叙事旅程（信使是主角、镜头伴飞）
  ——讲数据用飞线，讲人与人用信使
- 信使实体必须来自动作语义（发送→纸飞机、上传→气球、部署→火箭），
  随便找个吉祥物飞一趟读不出因果
- 相机三段（拉远/伴飞/接管）的切换帧上中心与变焦都要连续——demo 里
  zBase/zTake 在 TAKEOVER[0] 处相等（0.62）才不跳帧，改时间轴先查这点
- 2.5D 的极限：道具只能是剪影级形状，写实道具会暴露"没有真透视"；
  要重 3D 质感请回原片路线（成本高一档）

## 参考实现

demos/transition/paper-plane-messenger/
（PaperPlaneMessenger.tsx）
原片出处：pitch-app 77–82s（重 3D 原版的 2.5D 降级）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/transition/paper-plane-messenger.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/transition/paper-plane-messenger/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|转场]]
