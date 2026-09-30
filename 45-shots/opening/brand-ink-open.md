---
type: 镜头卡
招式: brand-ink-open
类别: 开场
类别slug: opening
能量: 低（起步位，为后续镜头留爬升空间）
上游: Vincentwei1021/video-shotcraft
上游路径: references/shots/opening/brand-ink-open.md
上游commit: 5e71af35a2da
许可: Apache-2.0
标签:
  - 镜头
  - brand-ink-open
---

# brand-ink-open

> [!abstract] 这一下是什么
> 墨线十字准星描画→字标逐字压印→打字机副标→满一秒静止再上浮消散

| 类别 | 适用 | 时长 | 能量 |
|---|---|---|---|
| [[镜头总览\|开场]] | 品牌开场；任何"先立名号再进产品"的片头 | 约 2.8s（83f） | 低（起步位，为后续镜头留爬升空间） |

> [!info] 这张卡不是本库原创
> 来自 [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)（Apache-2.0），原始路径 `references/shots/opening/brand-ink-open.md`，commit `5e71af35a2da`。
> 本库只做了归类与排版，**没有改动技法描述**。

---

## 意图

第一拍先给品牌记忆点：观众在任何产品画面出现之前，先看清并记住名字。安静、纸墨质感、有一个完整的静止时刻。

## 动效核心

- SVG 十字准星笔画描画（pathLength dashoffset），先竖后横，画完淡出
- 字标逐字 letterpress：scale 从大压到 1 + blur→0，字底强调色（模板片为琥珀）glint 短划闪过
- kicker 副标打字机逐字符出现，强调色块光标周期闪烁
- lockup 完整静止满 1 秒，然后整体上浮 + 缩小 + 淡出，交棒 dashboard

## 参数表

| 参数 | 典型值 | 调节手感 |
|------|--------|----------|
| 准星描画 | 竖线 0→9f、横线 8→18f，24→34f 淡出 | 描画完必须淡出，残留准星会和字标抢焦点 |
| 字标逐字 | 第 i 字 delay=10+i·3、12f；scale 1.6→1（origin center bottom）+ blur 6px→0 | "opacity+位移/scale+blur→0"是全片入场三件套定式，缺 blur 会显得硬 |
| kicker 打字机 | 0.7f/字符（28 起 ~43.4 完），光标 2f 周期闪、74f 停闪 | 0.7f/字符只适用于装饰性小字；正文交互打字要 3f/字符（对照 type-and-filter，用户嫌快返工过） |
| 品牌 hold | 46→76 帧整整 1 秒 | 硬底线：用户两轮点名"出现后延长停留1秒"（R1）；短于 1s 必返工 |
| 退场 | 7f 上浮 40px + 缩 12% + 淡出 | 退场快于入场——观众已读完，拖长反而泄气 |

## 声音

品牌落定钉 transition-soft（模板片钉在 f12），brand→dashboard 运镜钉 whoosh-fast（f78）。SFX 逐拍钉帧、声明式表管理（S2）；音色走电影系词汇，不用游戏 UI tap（S1）。

## 已知坑

- hold 要给的是 wordmark 落定时刻，不是普通字卡/内容卡（R1）——曾把 hold 错加给普通内容卡后很快回滚；指代含糊的"停留"反馈先确认对象再动手（P3）
- 开场能量必须低起步：全片能量曲线低开→中段推进→outro 峰值，开场炫技会压死后面的爬升（对照 Q8 的能量曲线要求）

## 参考实现

demos/typography/brand-ink-open/BrandInkOpen.tsx（原 template/src/aifl/live/SceneOpen.tsx 帧 0–83 段）

## 上游出处

| 项 | 值 |
|---|---|
| 仓库 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) |
| 原始路径 | `references/shots/opening/brand-ink-open.md` |
| commit | `5e71af35a2daee492dd3ea93e5e8903f32dcd13c` |
| 许可 | Apache-2.0 |
| 参考实现 | `demos/typography/brand-ink-open/BrandInkOpen.tsx（原 template/src/aifl/live/SceneOpen.tsx 帧 0–83 段）` |

> [!warning] 用之前先看 [[出处与许可]]
> 上游写明：动效手法研究自公开作品，**实现全部从零重写**，不含原片片段、截图或美术资产；且「公开发布**不等于**授权」。

---

← [[镜头总览]] · [[电影风格总览]]　|　类别：[[镜头总览\|开场]]
