# Vision 特征提取器（T3 语义匹配）

用 **macOS 自带 Vision 框架**计算图像的 768 维特征向量，用于：
- 语义相似度：这张参考图最像库里哪个流派
- 近重复检测：两张图是不是同一张

## 为什么用这个而不是 CLIP

| | CLIP (PyTorch) | **Vision (本方案)** |
|---|---|---|
| 依赖 | PyTorch ~2.5 GB | **macOS 系统自带** |
| 模型下载 | 需从 HuggingFace 下 | **不需要** |
| 联网 | 要 | **完全离线** |
| 平台 | 跨平台 | 仅 macOS |

实测：PyTorch / onnxruntime / tensorflow **全部装不上**（PyPI 读超时），
且 HuggingFace 被网络挡住（http=000）——CLIP 路线在这台机器上走不通。

## 为什么用 Objective-C 而不是 Swift

Swift 编译器在本机坏了：

```
error: redefinition of module 'SwiftBridging'
  at CommandLineTools/usr/include/swift/module.modulemap:13
```

这是 Command Line Tools 的 modulemap 冲突，`xcrun swiftc`、指定 SDK 都绕不过。
**clang + Objective-C 走的是同一套 Vision 框架，clang 是好的。**

## 编译

```bash
clang -O2 -fobjc-arc -framework Foundation -framework AppKit -framework Vision \
      vision_feat.m -o vision_feat
```

二进制不入库（架构相关），首次使用时由 `artvault_vision.py` 自动编译并缓存。

## 输出格式

单张：

```
DIM 768
VEC -0.010002 -0.020340 ...
```

批量（`vision_feat -`，从 stdin 逐行读路径）：

```
=== /path/to/a.jpg
DIM 768
VEC ...
=== /path/to/b.jpg
DIM 768
VEC ...
ERROR /path/to/c.jpg load
```

批量是必须的：603 张图逐个起进程约 19 秒，一个进程批量跑 **8 秒**。

---

## ⚠ 实测结论：这个特征**不能判断艺术流派**

标定过 603 张图的成对距离，结果很泼冷水：

| 指标 | 实测 |
|---|---|
| 最近邻是同一流派的命中率 | **44%**（近乎随机） |
| 同流派成对距离（中位） | 1.080 |
| 跨流派成对距离（中位） | 1.046 |
| 阈值 1.00 时 | 抓到 23% 同流派，**误判 35.5% 跨流派** |

同流派和跨流派的距离分布**几乎完全重合**，阈值调到哪一边都是误判多于命中。

原因不难理解：`VNGenerateImageFeaturePrint` 是给**物体/场景识别**用的
（这是同一栋楼、同一只狗、同一个商品），它编码的是「画面里有什么」，
不是「画得像哪个流派」。两幅不同的浮世绘之间的距离，
和一幅浮世绘到一幅立体主义之间的距离，没有系统差别。

### 所以这个工具能干什么、不能干什么

**能用** ——
- **近重复检测**：距离 <0.10 基本就是同一张。实测在本库找出 **17 对完全重复**（距离 0.000），详见下面
- **同题材/同构图**：距离 <0.35 说明画面内容高度接近
- 拿一张参考图找**内容**上相似的图

**不能用** ——
- 判断「这张图像哪个流派」→ 用 `artvault.py related`（基于文字关联）
- 按流派聚类 → 数据不支持
- 当风格相似度的依据 → 会得出误导性结论

`similar <流派>` 命令保留着，但输出里带了明确警告。
它的排序仍是「最接近的」，只是绝对水平不可靠。

---

## 顺带找出的库质量问题：17 对重复图

`artvault_vision.py dups --thresh 0.08` 找出 17 对距离 0.000 的图，**全是跨流派**。

大部分是**合理重叠**，不是 bug —— 一件作品本来就可以同时是多个流派的例证：

| 重叠 | 为什么合理 |
|---|---|
| `baroque` ↔ `caravaggisti` | 卡拉瓦乔主义本就是巴洛克的支流 |
| `renaissance` ↔ `early-renaissance` | 同一件文艺复兴作品 |
| `muralism` ↔ `social-realism` | Diego Rivera 同属两个运动 |
| `post-impressionism` ↔ `neo-impressionism` | 修拉《大碗岛》同属两者 |
| `gongbi` ↔ `song-academic` | 《捣练图》同属两者 |

**但有一处是真问题**：

```
abstract-art/01 = de-stijl/01   (蒙德里安 红黄蓝构图)
abstract-art/02 = de-stijl/02   (蒙德里安 前景幼树的田野)
```

`abstract-art` 一共只有 2 张图，**两张都是蒙德里安，和 `de-stijl` 完全重复**。
而它自己在 `mv_contemporary.py` 里列的关键词是
`["abstract", "mondrian", "kandinsky", "malevich", "de kooning", "rothko"]` ——
`mondrian` 排在前面，抓取时把名额全占了，于是这个流派真正的跨度
（康定斯基、马列维奇、德库宁、罗斯科）一张都没有。

修法：把 `mondrian` 从 `abstract-art` 的关键词里去掉（他已经是 `de-stijl` 的代表），
让它去抓另外四位。改完重新抓这一个流派即可：

```bash
python3 fetch_art.py abstract-art --per 6 --refresh
```

