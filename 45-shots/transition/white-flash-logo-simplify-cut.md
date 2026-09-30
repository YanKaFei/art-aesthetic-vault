---
type: 镜头卡
招式: white-flash-logo-simplify-cut
类别: 转场
类别slug: transition
能量: 中高（一次脉冲式重音，前后都是静场）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/transition/white-flash-logo-simplify-cut.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - white-flash-logo-simplify-cut
---

# white-flash-logo-simplify-cut

> [!abstract] 这一下是什么
> 彩色液态渐变字标静置流光，画面一拍冲白过曝，白底上扁平版字标淡入定格——一次闪白完成质感降维

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|转场]] | 品牌段落收束（华丽演绎→干净定妆）；情绪从炫技切换到正式宣告的转场拍 | 约 3.6s（108f@30fps；静置流光 0–1.2s · 冲白 1.2–1.5s · 扁平定格 1.7–2.7s） | 中高（一次脉冲式重音，前后都是静场） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/transition/white-flash-logo-simplify-cut.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

先给足华丽（六色液态渐变在字面上流动、柔光扫掠），再用一次白闪把它"净化"成扁平三色字标——观众读到的是"演出结束，这就是它的正式形象"。降维是修辞：从感性质感切到理性识别。

## 动效核心

- 液态层：六色渐变 `background-size:320%`，`backgroundPosition = t*100%` 全程缓慢流动；一块 220×120 径向柔光（blur 6px + screen 混合）随 t 横移 ±30px 做高光扫掠
- 冲白 t=0.34–0.42（inQuad 加速冲入）白层盖满；同窗口给液态层一个 `sin(π)` 脉冲：blur 0→5px + brightness 1→2.2——"过曝烧穿"的一帧
- 白层冲入后**保持不退**，后半场全程白底
- 扁平字标 t=0.48–0.74 淡入 + scale 0.96→1（outCubic），字色是三段线性渐变（`GRAD_A/B/C` 常量，可按项目替换）
- 柔光层随冲白同步熄灭（`1-flashK`），不残留在白底上

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 冲白窗口 | 0.34–0.42（inQuad） | 换算 0.29s@3.6s——冲白必须"快进慢不退"；用 outQuad 会显得白光是飘进来的 |
| 过曝脉冲 | blur 5px + brightness ×2.2，sin 包络 | 砍掉脉冲则冲白像纯剪辑；>8px blur 液态字彻底糊掉反而看不出"是它在烧" |
| 扁平入场 | 0.48–0.74，scale 0.96→1 | 与冲白间隔 0.06 的白屏静默是呼吸位；缩太短观众来不及"清屏" |
| 液态流速 | backgroundPosition t*100% | 拉长 dur 时流速自动变慢，静置段够 1s 以上流动感才可读 |
| 字标字号 | 液态 62px / 扁平 58px | 扁平版略小一号是"落定收束"暗示；同号会读作换皮不换人 |
| 渐变常量 | `GRAD_A/B/C`（块顶定义） | 换成项目品牌三色即完成收编；液态层六色一般保留（它是"演出"不是品牌） |

## 已知坑

- 白层是"冲入后保持"，不是闪一下回黑——后半场底色即白色，若下一镜是暗场需另接转场，或复用本卡结尾白底直切
- `WORDMARK` 常量是占位字标（5 字母），换长词需同步缩字号与 letter-spacing，两层（液态/扁平）都要改
- 冲白配 SFX 是必选项（impact/whoosh-bright 类），无声的白闪读作素材丢帧
- mix-blend-mode:screen 的柔光层在白底上不可见属预期，别在冲白后调它

## 参考实现

demos/transition/white-flash-logo-simplify-cut/
（WhiteFlashLogoSimplifyCut.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/transition/white-flash-logo-simplify-cut.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/transition/white-flash-logo-simplify-cut/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|转场]]
