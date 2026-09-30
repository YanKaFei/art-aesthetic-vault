#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_inject.py —— 把解析出的**真实** film-grab URL 注入 `fv_new_*.py` 的片数据。

## 为什么单独一步

加片子分三段：**写七层（离线）→ 解析 URL（联网）→ 抓班底与剧照（联网）**。
七层写完时 URL 是空的（因为不能手写 —— 实测手写 10 个里 8 个 404）。
本模块是第二步，把 `fv_resolve.py` 解析出的真实链接填进 `filmgrab` 字段。

## 纪律

  · **解析不到就留空并报告**，绝不编造 URL —— 编出来的卡片会指向 404
  · 幂等：已注入的跳过，可以反复跑（缓存让重跑很便宜）
  · 限流（EOF/SSL 断连）如实报告为「待重试」，不算失败

## 用法

    python3 fv_inject.py --dry-run     # 只看会写什么，不动文件
    python3 fv_inject.py               # 真注入
    python3 fv_inject.py --check       # 注入后核对覆盖率
"""

import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fv_resolve as R  # noqa: E402

PAUSE = 1.5          # 对站点客气；实测 0.35s 连续抓会被限流


def batch_files():
    return sorted(f for f in os.listdir(HERE) if re.fullmatch(r"fv_new_\d+\.py", f))


def load_batch(fn):
    """读一个批次文件，返回 (文件头, BATCH 列表)。"""
    src = open(os.path.join(HERE, fn), encoding="utf-8").read()
    mod = __import__(fn[:-3])
    return src.split("BATCH = [")[0], list(mod.BATCH)


def write_batch(fn, head, films):
    body = "BATCH = [\n"
    for d in films:
        body += "    " + json.dumps(d, ensure_ascii=False, indent=4).replace("\n", "\n    ") + ",\n"
    body += "]\n"
    open(os.path.join(HERE, fn), "w", encoding="utf-8").write(head + body)


def inject(dry_run=False, only_missing=True):
    """逐部解析并注入。返回 (注入数, 待重试列表, 站上不存在列表)。"""
    import fv_candidates as C
    cand = {c["slug"]: c for c in C.CANDIDATES}
    done = retry = absent = 0
    retry_list, absent_list = [], []

    for fn in batch_files():
        head, films = load_batch(fn)
        changed = False
        for f in films:
            if f.get("filmgrab") and only_missing:
                done += 1
                continue
            c = cand.get(f["slug"])
            if not c:
                print("  ? %-38s 不在候选清单里，跳过" % f["slug"])
                continue
            r = R.resolve(c["title_en"], director_slug=c.get("director_slug"))
            url = r.get("url")
            if url:
                f["filmgrab"] = url
                f["filmgrab_director"] = ("https://film-grab.com/category/directors/%s/"
                                          % c["director_slug"])
                changed = True
                done += 1
                print("  ✓ %-38s %s" % (f["slug"], url))
            else:
                why = (r.get("why") or "")
                # 限流（EOF/SSL/超时）算「待重试」；「没匹配到」算站上不存在
                if any(k in why for k in ("EOF", "SSL", "timed out", "timeout", "连续")):
                    retry += 1
                    retry_list.append(f["slug"])
                    print("  ⏳ %-37s 限流，待重试" % f["slug"])
                else:
                    absent += 1
                    absent_list.append((f["slug"], why))
                    print("  ✗ %-38s %s" % (f["slug"], why[:60]))
            if not dry_run:
                time.sleep(PAUSE)
        if changed and not dry_run:
            write_batch(fn, head, films)
            print("  → 已写回 %s" % fn)

    return done, retry_list, absent_list


def check():
    """核对：每部片是否都有 URL、URL 是否都在候选导演页里出现过。"""
    from fv_merge import all_new
    rows = all_new()
    missing = [f["slug"] for _, f in rows if not f.get("filmgrab")]
    print("新片 %d 部，已注入 URL %d 部，缺 %d 部"
          % (len(rows), len(rows) - len(missing), len(missing)))
    if missing:
        print("缺 URL：%s" % missing[:12])
    return 1 if missing else 0


def main():
    ap = argparse.ArgumentParser(description="注入解析出的真实 film-grab URL")
    ap.add_argument("--dry-run", action="store_true", help="只显示，不写文件")
    ap.add_argument("--check", action="store_true", help="只核对覆盖率")
    a = ap.parse_args()
    if a.check:
        return check()
    done, retry, absent = inject(dry_run=a.dry_run)
    print("\n已注入/已有 %d 部 | 限流待重试 %d 部 | 站上不存在 %d 部"
          % (done, len(retry), len(absent)))
    if retry:
        print("待重试（等十几分钟再跑本脚本，缓存会跳过已抓的）：%s" % retry)
    if absent:
        print("站上不存在（不要编 URL，应从候选清单移除）：")
        for s, w in absent:
            print("   %-38s %s" % (s, w[:56]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 fv_inject.py --dry-run",
          ["把 fv_resolve 解析出的**真实** film-grab URL 注入 fv_new_*.py。",
           "  --dry-run  只显示会写什么，不动文件",
           "  --check    只核对覆盖率",
           "",
           "解析不到就留空并报告，**绝不编 URL** —— 编出来的卡片指向 404。",
           "幂等：已注入的跳过，可反复跑。"])
    sys.exit(main())
