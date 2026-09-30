---
type: 镜头卡
招式: type-rhythm-sync
类别: 文字排版
类别slug: typography
能量: A 高（蹦迪感）/ B 中（跟读引导）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/typography/type-rhythm-sync.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - type-rhythm-sync
---

# type-rhythm-sync

> [!abstract] 这一下是什么
> 文字随声同步两式——font-weight-pump 字重脉冲（笔画随鼓点变粗弹回）与 karaoke-fill-sync 卡拉OK填色（词随旁白逐个点亮）

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|文字排版]] | 标题/标语与音轨强绑定的段落；A 绑节拍（鼓点），B 绑语音（旁白逐词） | 单式 4–5s；A 每拍占 10f 衰减窗、B 每词按语速 15–35f | A 高（蹦迪感）/ B 中（跟读引导） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/typography/type-rhythm-sync.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

文字动效库内此前全是"入场怎么进"，没有词管"在场的字怎么跟着声音活"。
这两式补上：A 让标题变成节奏器官——笔画随低音鼓抽动变粗又弹回，
文字在蹦迪，适合高能段落的视觉低音炮；B 让标语变成跟读字幕——
旁白读到哪个词哪个词从左到右填色点亮，视线被牵着走，适合口播/
标语强调段。共同点是**字不动、属性动**：无位移、无入退场，
纯粹是字重/颜色在声音的拍点上呼吸。

## 两式选型

| 式 | 做法 | 适用 |
|----|------|------|
| A font-weight-pump 字重脉冲 | 命中帧笔画瞬间变粗（stroke+字重跳变），~10f 衰减弹回；重音拍额外撑宽 8% | 音乐驱动的高能段；标题当低音炮 |
| B karaoke-fill-sync 填色随读 | 每词深色从左到右填亮，进度跟语速，读完保持；活跃词下带读指下划线 | 旁白/口播强调段；多词标语的视线引导 |

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| A 脉冲包络 | `env=(1−t/10)^0.8`（t=命中后帧数，≥10f 精确归 0）；`-webkit-text-stroke: 10px·env` + fontWeight 在 env>0.15 窗口 400↔900 跳变 | stroke 连续衰减 + 字重离散跳变叠加才读作"连续变粗"；单用 fontWeight 只有两挡、单用 stroke 变化太细 |
| A 节拍 | 每 20f 一拍；重音拍额外 `scaleX = 1+0.08·env`（transform 缩放不改排版） | 拍距必须 > 衰减窗（20>10），两拍重叠读作抽搐 |
| A 节拍参照物 | 画面下方一排小节拍点，命中哪拍哪个点闪深并放大 | 静音环境（预览/静帧）没有这排点就读不出"在跟拍" |
| B 词级时间表 | 逐词 [start,end] 帧区间，词内 linear 填充；词间留 4–10f 停顿（换气） | 时间戳实战来自旁白打点表；均匀分配读作机器朗读 |
| B 填色实现 | 每词双层同文本叠放：底层浅灰 + 上层深色 `clipPath: inset(0 X% 0 0)`，X=(1−p)·100 | 逐词独立叠层免量测词宽占比；整行单层 clip 需精确像素表、易漂 |
| B 读指 | 活跃词下 8px 深色下划线，宽度 = p·100% | 4px 浅灰在 1080p 缩略下不可见（本批实渲踩坑）；读完的词不留线 |
| 收尾 | A 末拍衰减归零后 / B 末词填完后真静止 ≥20f | R1 呼吸判例 |

## 已知坑

- demo 在灰阶/占位素材上调校通过——参数是调校起点非实战定稿，
  首次实战须以真实素材回验
- 两式都是**声音强依赖**手法：A 命中帧必须与鼓点同帧、B 填色区间必须
  跟旁白词边界（钉帧走 sound-design §4.5 相对起点）——无声上片则 A 读作
  抽风、B 读作莫名变色，别在无音轨段落用
- A 式实战想要真·可变字体连续字重（wght 轴逐帧插值）需先确认字体加载
  与渲染器支持；demo 的 stroke+跳变方案是无字体风险的兜底，效果已可感
- A 式全片 ≤1 段（P4）——标题蹦迪是抢戏大户，两段同片互相拆台
- B 式词数 ≤6/屏：更多词时填色进度读不过来，拆行或拆镜

## 参考实现

demos/typography/type-rhythm-sync/
（FontWeightPump.tsx / KaraokeFillSync.tsx）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/typography/type-rhythm-sync.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/typography/type-rhythm-sync/` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|文字排版]]
