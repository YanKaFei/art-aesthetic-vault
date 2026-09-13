# 20-我的提示词

**这个目录是你的私人工作区，不进版本库。**

`build_vault.py` 不会覆盖这里的任何东西（除了自动生成的 `Pinterest.md` 汇总页）。
你可以随便往里写。

## 里面会长出什么

| 文件 | 谁生成 | 说明 |
|---|---|---|
| `我的提示词卡.md` | 你 | 提示词卡的索引。每次调出满意的图，用 [[提示词卡模板]] 新建一张卡记下来 |
| `Pinterest-<板子>.md` | `pinterest_grab.py` | Pinterest 抓取结果。**每张图下面都有反推**：提示词 + 两块视频提示词 |
| `Pinterest.md` | `build_vault.py` | Pinterest 来源的总汇（抓取的 + 你手动放进投递箱的） |
| `投递箱-<日期>.md` | AI | 投递箱逐张拆解的结果 |

## 为什么整个目录都 gitignore

1. **版权**：Pinterest 的图没有统一授权，只能个人参考。笔记会嵌入这些图，
   而图在 `99-附件/images/pinterest/`（同样 gitignore）。
   笔记发布、图不发布的话，别人 clone 下来看到的是一堆加载不出来的图。
2. **隐私**：你的提示词卡和投递箱分析里有你自己的内容，没必要公开。

想把自己的提示词卡分享出去，单独复制那几张到别处、自己确认过内容再发。

## 从哪开始

```bash
cd ../_scripts
python3 artvault.py compose "你的创意"     # 拼提示词
python3 ingest_inbox.py --scan             # 处理投递箱
```
