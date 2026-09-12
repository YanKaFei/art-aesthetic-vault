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

## 实测结论：能判断流派，但只能当建议

### 先说一个我犯过的错

我先前的结论是「这个特征对艺术流派几乎没有区分度，最近邻同流派命中率只有
44%，近乎随机」。**这个结论是错的**，两个原因：

1. **基准比错了。** 我把 44% 和 50% 比，可随机的正确基准是「随便挑另一张图
   恰好属于同一流派」—— 本库 78 个流派、每流派约 5 张图，所以基准约 **1%**。
   44% 是随机水平的 30 多倍，不是「近乎随机」。
2. **44% 那个数还被污染了。** `pinterest/` 目录是用户的投递箱（212 张混杂
   参考图，占全库三分之一），这些图互相成为最近邻，把命中率抬高了，
   同时把随机基准也抬到 12%，真实倍数只剩 ×3.6。

### 正确口径下的实测

排除 `pinterest/`，400+ 张图、78 个流派，留一法：

| 口径 | 实测 | 随机基准 | 倍数 |
|---|---|---|---|
| 最近邻是否同流派 | **27.6%** | 1.1% | **×25** |
| 72 选 1 质心分类 Top-1 | **30.6%** | 1.4% | ×22 |
| 72 选 1 质心分类 Top-3 | 50.8% | 4.2% | ×12 |

所以这个特征**含有真实信号**，是随机水平的二十多倍。

### 但它是「建议」不是「分类器」

Top-1 约 30% 意味着**十次里错七次**。原因是样本太薄（78 个流派、每个约 5 张）
且相邻流派的画面本来就接近。

**能放心用** ——
- **近重复检测**：距离 <0.10 基本就是同一张。实测找出 **17 对完全重复**（距离 0.000）
- **同题材/同构图**：距离 <0.35 说明画面内容高度接近

**只当建议** ——
- 判断「这张图最像哪个流派」：排序有信息量，但别当结论
- 要更确定的风格关联，配合 `artvault.py related`（基于文字关联）一起看

`similar <流派>` 命令的输出里带了这些数字和提醒。

### 顺便：又试了两条路，都比 Vision 好或差

同一个评估框架下还试了两条：

| 做法 | 最近邻同流派 | Top-1 | Top-3 |
|---|---|---|---|
| **CLIP + 融合（零样本权重 0.15）** | — | **39.1%** | **61.4%** |
| CLIP 图像质心 | 33.1% | 37.6% | 59.8% |
| CLIP 零样本（图 vs 流派文字） | — | 21.5% | 36.6% |
| Vision featureprint（768 维） | 27.6% | 30.6% | 50.8% |
| T1 客观维度（31 维） | 13.4% | 13.2% | 25.3% |

- **CLIP 最好**（比 Vision 高 8.5 个百分点）→ 见 `_scripts/clip_match.py`，
  它还能做**零样本**：用流派卡的英文描述直接匹配图像，连一张实图都没有的
  流派（赛博朋克、蒸汽朋克）也能被匹配到
- **T1 客观维度最弱**（31 维，用明度/饱和/笔触建流派指纹）
  → 见 `_scripts/movement_fingerprint.py`

所以「要判流派」的推荐顺序是：**CLIP → Vision → T1 客观维度**。

**基准一定要算对**：这里的「随机」是「随便挑另一张图恰好同流派」，本库约 1%。
不是 50% —— 曾经用 50% 当基准，得出过「Vision 近乎随机」的相反结论。

---

## 顺带找出的库质量问题：17 对重复图

`artvault_vision.py dups --thresh 0.08` 找出 17 对距离 0.000 的图，**全是跨流派**。
这一项不受上面那个「建议级」限制 —— 距离 0.000 就是同一张，没有误判空间。

大部分是**合理重叠**，不是 bug —— 一件作品本来就可以同时是多个流派的例证：
`baroque` ↔ `caravaggisti`（卡拉瓦乔主义本就是巴洛克支流）、
`renaissance` ↔ `early-renaissance`、`muralism` ↔ `social-realism`（Diego Rivera）、
`post-impressionism` ↔ `neo-impressionism`（修拉《大碗岛》）、
`gongbi` ↔ `song-academic`（《捣练图》）。

**有一处是真问题**（已修）：`abstract-art` 仅有的 2 张图全是蒙德里安、
与 `de-stijl` 完全重复，而它自己列的康定斯基/马列维奇/德库宁/罗斯科一张没有。
详见 `skill/build/reference/pitfalls.md` 的 2.2.1~2.2.3。
