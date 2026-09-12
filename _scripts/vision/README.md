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

### 顺便：还有一条路，但实测更差

同一个评估框架下也测了 T1 客观维度（31 维）建流派指纹的方案
（`movement_fingerprint.py`），实测反而不如 Vision：

| | 最近邻同流派 | Top-1 |
|---|---|---|
| Vision（768 维） | **27.6%** | **30.6%** |
| T1 客观维度（31 维） | 13.4% | 13.2% |

两者都远超随机（×12 和 ×25），但 Vision 在两个口径上都更好。
这和「客观维度更懂风格」的直觉相反，可能的原因是：T1 的 31 维里含大量
与流派无关的信息（画面比例、对称性受题材和构图支配），而 Vision 的 768 维
虽为物体识别训练，却隐含编码了笔触、材质、色调。

结论：两个都能用，但都只能当建议。真要判风格，**以库里的流派卡为准** ——
`artvault.py layers <流派>` 给的是人写的具体术语，比任何像素统计可靠。

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

