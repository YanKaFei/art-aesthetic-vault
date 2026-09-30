---
type: 来源说明
---

# 来源与署名（handraw-style）

这个目录是 [yang0/handraw-style](https://github.com/yang0/handraw-style.git) 的**原样副本**，
作为本库第 7 大类「手绘艺术风格」的原始数据与编号参考图来源。

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/yang0/handraw-style.git |
| 抓取提交 | `2a12842d94c5a9c403fd9b91992ed5f105604119` |
| 抓取日期 | 2026-09-20 |
| 授权 | MIT（见本目录 `LICENSE`） |
| 本库的改动 | **无**。文件内容一字未改；只删掉了 `.git/` |

## 与本库的关系

- `.repo/mv_handraw.py` 读本目录的
  `skills/handdraw-style-prompter/references/styles.json`（274 条）。
- 274 张编号单图与 20 张拼图**硬链接**到
  `99-attachments/images/handraw/`：内容是同一份（同一 inode，磁盘不翻倍），
  但 Obsidian 与验收只认 `99-attachments/images/` 下的图。
- 本库**不修改**本目录里的任何文件。要升级 handraw，整棵替换本目录即可，
  然后重跑 `python3 .repo/build_vault.py`。

## 授权

上游是 MIT，本库原样保留了它的 `LICENSE`。编号参考图按上游仓库的授权
随仓库一并分发。
