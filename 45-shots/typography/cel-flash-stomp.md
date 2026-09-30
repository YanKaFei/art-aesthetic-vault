---
type: 镜头卡
招式: cel-flash-stomp
类别: 文字排版
类别slug: typography
能量: 高
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/typography/cel-flash-stomp.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - cel-flash-stomp
---

# cel-flash-stomp

> [!abstract] 这一下是什么
> 底色闪砸字——大词逐拍像图章歪着砸满屏，每词落定瞬间背景层在两个纯色间频闪数帧而文字纹丝不动；动漫必杀技字卡的 UI 翻译

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|文字排版]] | 口号/三连词的高能段落（"SHIP / FASTER / TODAY"式）；文字节奏卡，与 type-rhythm-sync 互补（那是字属性动，这是字砸+底闪） | 每词 ~30f × 词数 + 收尾 ≥45f；三词约 4.8s | 高 |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/typography/cel-flash-stomp.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

逐词砸字（stomp typography）单用只有重量；背景纯色闪（动漫背景
フラッシュ——必杀技名出现时底色交替闪）单用只是闪。焊在一起互补
成立：词砸下的落定帧正是底闪的起爆帧，**主体稳、背景闪**——观众
盯着字，眼角余光里整个世界在震颤，打击感来自周边视野而不来自主体
抖动。这是与震屏完全相反的路线：震屏晃主体，本卡晃世界。三词逐拍
递进，末词闪加倍+标签条收束，一句口号剪成三记盖章。

## 动效核心

- 每词 ~30f 硬切无过渡；入场 6f scale 1.18→0.98→1
  （Easing.out(poly(5))，2% 过冲）+ rotate 交替 +2.5°/−2.5°/0°
  ——歪角是"图章"的一半，全正读作幻灯片
- **底闪与文字分层是命门**：落定帧起背景色在 G.bg(#ececea) 与
  加深灰 #cfcfca 间每 2f 交替共 6f，文字独立上层纹丝不动
  ——白底上闪加深灰不闪白（判例）
- 末词加倍：闪 8f + 暗色拉大到 #c4c4c0 + 同帧底部标签条 14f 淡入
  ——最后一击必须比前两击响
- 词间零 crossfade；全程帧确定

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 词时长 | ~30f/词，3–4 词 | <22f 读不完词；5+ 词读作 rap 字幕（那去用 karaoke） |
| 砸落 | 6f scale 1.18→1 + 2% 过冲 | 幅度 >1.3 起步会先读到"缩小动画"再读到"砸" |
| 歪角 | ±2.5° 交替，末词归 0° | 同方向连歪读作版式错误 |
| 底闪 | 2f 交替 × 6f；末词 8f + 对比拉大 | 闪 >10f 读作背景故障；1f 交替在 30fps 下读不出色差 |
| 标签条 | 末词闪结束同帧起 14f 淡入 | 早于末闪出现会被闪没 |
| 收尾 | 末词落定真静止 ≥45f | R1；重拳双倍 hold |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- **声音强依赖**：每词砸落一声 kick、底闪对齐鼓点（sound-design
  §4.5）——无声版读作 PPT 快翻；这卡就是给音乐段写的
- 底闪层里不许有任何内容元素（logo/纹理都不行）——闪的必须是
  "空气"，有物在闪就变成内容故障（同 drop-blackout"黑场无物"判例）
- 与 background-cel-flash 单用（关键词驻场只闪底）的区别：本卡词
  在换、拍在推进；驻场强调版是它的静态子集，不另立卡
- 与 beat-cut-moves A（递进硬切串）能量档相同且都是"切+拍"，
  同片二选一；全片本卡 ≤1 段（P4）
- 实战品牌色版：底闪两色用品牌色对（如强调色×深墨），对比度须 ≥
  demo 的 #ececea/#cfcfca 灰差，不然白闪一场

## 参考实现

demos/typography/cel-flash-stomp/
（CelFlashStomp.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/typography/cel-flash-stomp.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/typography/cel-flash-stomp/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|文字排版]]
