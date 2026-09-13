# 方法论：七层拆解法

这套库的核心不是"收集了很多画"，而是**把风格拆成可独立替换的层**。
拆成层之后，你才能把 A 图的光照套到 B 图的主体上——这才是参考库的意义。

---

## 一、七个层

看到任何一张图（不管是名画还是 AI 生成），按顺序问七个问题：

| # | 层 | 要问的问题 | 产出示例 |
|---|---|---|---|
| 1 | **主体** Subject | 画的是谁/什么？姿态、服装、数量、年龄 | `a young woman in a beige trench coat` |
| 2 | **风格** Style | 哪个流派/艺术家/媒介？ | `baroque oil painting, tenebrism` |
| 3 | **光照** Lighting | 光源在哪？几个？硬还是软？什么时间？ | `single hard light from off-frame, candlelight rim` |
| 4 | **色彩** Color | 主色、辅色、饱和度、明度关系 | `bitumen black, warm gold, deep crimson` |
| 5 | **构图** Composition | 视角、对称性、主体位置、纵深 | `diagonal dynamic, low angle, shallow depth` |
| 6 | **媒介** Medium | 什么材料？质感？颗粒？ | `oil on canvas, visible impasto, aged varnish` |
| 7 | **情绪** Mood | 观众应该感觉到什么？ | `dramatic, intense, theatrical` |

**流派卡提供的是第 2–7 层；第 1 层永远是你自己的。**

---

## 二、为什么必须分层，而不是堆砌

### 错误做法

```
巴洛克风格的赛博朋克女孩，很酷，有霓虹灯，氛围感强
```

问题：`巴洛克风格` 是什么？光照？构图？色彩？模型不知道，只能猜。
结果通常是一张平庸的、什么都像一点又什么都不像的图。

### 正确做法

```
a female bounty hunter in a wet neon alley,          ← 主体（你自己的）
single hard light source from off-frame,             ← 光照层（取自巴洛克）
deep crushed shadows, candlelight rim light,
cyan and magenta clash, deep black shadows,          ← 色彩层（取自赛博朋克）
low angle looking up at megastructures,              ← 构图层（取自赛博朋克）
digital concept painting, wet reflective surfaces,   ← 媒介层
alienated, oppressive, intoxicating                  ← 情绪层
```

**同一个主体，每一层都可以单独换掉**，这就是风格迁移的本质。

---

## 三、逐层锁定的调试顺序

不要一次写完所有层然后靠试错调。按这个顺序：

1. **只写主体** → 确认构图和姿态对了
2. **加风格层** → 看整体味道对不对
3. **加光照层** → ⚠️ **这一层对最终质感的影响最大，比风格词本身还大**
4. **加色彩层** → 修正偏色
5. **加媒介层** → 锁死质感（`oil on canvas` / `35mm film` / `watercolour`）
6. **最后加情绪层**

> **光照层的性价比最高。** 如果你只有一个层可以调，调光照。

---

## 四、每层的建议词数

| 层 | 建议词数 | 说明 |
|---|---|---|
| 主体 | 15–40 | 越具体越好 |
| 风格 | 3–8 | 太多会互相打架 |
| 光照 | 4–8 | 性价比最高 |
| 色彩 | 3–6 | 给具体颜色名，不要只写 `colorful` |
| 构图 | 3–6 | 镜头语言同时管构图和运镜 |
| 媒介 | 2–5 | 决定"看起来像什么做的" |
| 情绪 | 3–6 | 影响姿态和氛围 |

---

## 五、负向提示词要"针对性"，不要"通用长串"

### 反面教材（2022 年的遗物）

```
worst quality, low quality, bad anatomy, ugly, deformed, blurry, watermark, text
```

现代模型基本不需要这一串，而且会占用注意力。

### 正确做法：针对**这个流派的典型翻车点**

| 流派 | 负向词 | 为什么 |
|---|---|---|
| 印象派 | `black shadows, smooth blending, photorealistic` | AI 默认给油画加黑色阴影和厚涂 |
| 文艺复兴 | `visible brushstrokes, impasto` | AI 默认给油画加厚涂笔触（文艺复兴表面是光滑的） |
| 浮世绘 | `3d shading, cast shadows, gradient` | AI 会自动加立体感和渐变（浮世绘是平面的） |
| 精确主义 | `people, figures` | 这一派画面里没有人 |

**注意：不同流派的负向词经常是相反的。** 这正是跨流派混搭会打架的原因。

---

## 六、跨流派混搭的冲突消解

当各层来自不同流派时，负向词会互相矛盾：

```
浮世绘（风格层）的 negative 含：cast shadows
巴洛克（光照层）的 positive 要：deep crushed shadows
                           ↑ 直接打架
```

**要检出三类冲突：**

1. **词面冲突**：某层的负向词出现在另一层的正向词里
2. **人物冲突**：负向词含 `people/figures` 而主体是人物
3. **时代冲突**：混搭了物理上不兼容的媒介（如"湿壁画的厚涂笔触"）

**检出之后要消解，不能只报告。** 实测抽 300 组「风格层 × 光照层」混搭，
**205 组（68%）**会撞，平均 1.72 处 —— 如果只打印警告，等于让每个用混搭的人
都手工收拾一遍。规则只有一条，且没有例外：

> **正向是意图，负向是护栏，护栏让位于意图。**

- 你说要巴洛克的光照 → 浮世绘的 `cast shadows` 必须让路
- 你给的主体是个人 → 精确主义的 `no people` 必须让路

拿到打架的负向词就**从负向提示词里删掉**，并逐条记录「删了哪个、让位给谁」。
使用者要能看到这个决策，但不需要自己重做一遍。想自己判断的给个开关
（`--keep-conflicts`）保留原样合集。

第 3 类「时代冲突」目前**只能报告不能自动消解** —— 判断「湿壁画的厚涂笔触」
这种组合是否成立需要语义理解，不是词面对照能解决的。这一条交给使用者。

---

## 七、给视频再加五维

文生视频 = 静态描述 + 运动。原七层只覆盖了"画面长什么样"。

| 维度 | 例子 |
|---|---|
| **运动** Motion | `hair drifts in the wind`, `rain falls steadily` |
| **景别** Shot Size | `extreme close-up (ECU)` … `extreme wide shot (EWS)` |
| **机位** Camera Angle | `eye-level` `low angle` `dutch angle` `aerial` |
| **运镜** Camera Movement | `static` `dolly in` `pan left` `tracking` `arc` `crane` |
| **时段与光照** | `sunrise` `dusk` `overcast` `rim light` `backlight` |

> **运镜本身带风格信息。** 给印象派用手持快切、给表现主义用平稳滑轨，
> 都是错的——**运镜和流派必须同源**。每张流派卡里都标了该流派的
> motion 和 camera 建议。

---

## 八、检索词怎么选

**用技法术语，不用风格名。**

| 差的检索词 | 好的检索词 | 为什么 |
|---|---|---|
| `baroque` | `tenebrism chiaroscuro` | 前者是时代标签，后者是画法，精确得多 |
| `impressionism` | `broken brushwork plein air` | 同上 |
| `ukiyo-e` | `bokashi gradation woodblock` | 同上 |

Pinterest 这类网站的标签是用户随手打的扁平体系，
精确的**技法术语**命中率明显高于风格标签。

生成外部检索链接时，检索词应取自流派卡 `prompt.style` 的
前几个逗号项（那正是技法术语），而不是 `name_en`。

---

## 九、一句话版

> **层可以换，光最重要，负向要针对性，混搭必检冲突。**
