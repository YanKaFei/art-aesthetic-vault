#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pinterest_export.py —— 用 Pinterest 官方 API 把**你自己账号**的收藏板导出进仓库。

为什么只能导自己的：
    Pinterest API v5 有三个 search 端点，但只有一个是搜全站的：
      GET /v5/search/partner/pins   ← 按关键词搜全站，但是 beta，需要单独申请
      GET /v5/search/pins           ← 只搜「你自己」的 pin
      GET /v5/search/boards         ← 只搜「你自己」的 board
    所以全站关键词检索要么申请 beta，要么用浏览器手动浏览。

    但「导出自己的收藏」这条链路是完全合法的，而且很实用：
    你在 Pinterest 上做人工策展 → 脚本把板子同步进 Obsidian → 再反推提示词。

准备：
    1. 到 https://developers.pinterest.com/apps/ 建一个 app
    2. 申请 scope: boards:read, pins:read
    3. 走 OAuth 拿到 access token（三脚 OAuth，或开发者后台的 token 生成器）
    4. export PINTEREST_TOKEN=你的token

用法：
    python3 pinterest_export.py --boards            # 列出你的所有板子
    python3 pinterest_export.py --export "艺术参考"  # 导出指定板子
    python3 pinterest_export.py --export-all        # 导出全部板子

产出：
    20-我的提示词/Pinterest-<板子名>.md   每张 pin 一条，含图片直链与反推提示
    99-附件/images/pinterest/<板子>/      可选，加 --download 会把图下下来
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
API = "https://api.pinterest.com/v5"


def get(path, token, params=None, tries=3):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/json",
                "User-Agent": "ArtAestheticVault/1.0",
            })
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503) and i < tries - 1:
                time.sleep(3 * (i + 1)); continue
            print("  ! HTTP %s %s\n    %s" % (e.code, url, body))
            return None
        except Exception as e:
            if i == tries - 1:
                print("  ! %s -> %s" % (url, e)); return None
            time.sleep(2 * (i + 1))
    return None


def paginate(path, token, params=None, cap=500):
    out, bookmark = [], None
    while len(out) < cap:
        p = dict(params or {})
        p["page_size"] = 100
        if bookmark:
            p["bookmark"] = bookmark
        js = get(path, token, p)
        if not js:
            break
        out += js.get("items", [])
        bookmark = js.get("bookmark")
        if not bookmark:
            break
        time.sleep(0.3)
    return out


def safe_name(s, n=40):
    import re
    s = re.sub(r'[\\/:*?"<>|]', "-", s or "未命名").strip()
    return s[:n] or "未命名"


def export_board(token, board, download=False):
    name = safe_name(board.get("name"))
    print("· 板子：%s（%d pins）" % (name, board.get("pin_count", 0)))
    pins = paginate("/boards/%s/pins" % board["id"], token)
    if not pins:
        print("  没有取到 pin"); return
    imgdir = os.path.join(VAULT, "99-附件", "images", "pinterest", name)
    if download:
        os.makedirs(imgdir, exist_ok=True)

    L = []
    L.append("---")
    L.append("type: Pinterest导出")
    L.append("板子: %s" % name)
    L.append("pins: %d" % len(pins))
    L.append("标签:")
    L.append("  - pinterest")
    L.append("---")
    L.append("")
    L.append("# Pinterest · %s" % name)
    L.append("")
    L.append("> [!info] 来源")
    L.append("> 通过 Pinterest 官方 API 导出的**个人收藏板**，共 %d 张。" % len(pins))
    L.append("> 图片版权归原作者，这里只存链接供个人参考。")
    L.append("")
    L.append("> [!tip] 下一步")
    L.append("> 挑出真正有用的，用 [[反推工具链]] 反推提示词，再存成 [[提示词卡模板]]。")
    L.append("")

    for i, pin in enumerate(pins, 1):
        media = pin.get("media") or {}
        url = (media.get("images", {}).get("originals", {}).get("url")
               or media.get("images", {}).get("1200x", {}).get("url") or "")
        title = (pin.get("title") or pin.get("description") or "无题").strip()
        L.append("### %d. %s" % (i, title[:80]))
        L.append("")
        if download and url:
            import re
            ext = ".jpg"
            fn = "%03d-%s%s" % (i, safe_name(title, 40).lower().replace(" ", "-"), ext)
            dest = os.path.join(imgdir, fn)
            if not os.path.exists(dest):
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "ArtAestheticVault/1.0"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        blob = r.read()
                    if len(blob) > 2048:
                        open(dest, "wb").write(blob)
                except Exception as e:
                    print("    ! 下载失败 %s" % e)
            if os.path.exists(dest):
                L.append("![[%s]]" % fn); L.append("")
        elif url:
            L.append("[原图](%s)" % url); L.append("")
        if pin.get("description"):
            L.append("> %s" % pin["description"].replace("\n", " ")[:300]); L.append("")
        if pin.get("link"):
            L.append("链接：%s" % pin["link"]); L.append("")
        if pin.get("board_owner", {}).get("username"):
            L.append("来源板：`%s`" % pin["board_owner"]["username"]); L.append("")
        L.append("---")
        L.append("")

    outp = os.path.join(VAULT, "20-我的提示词", "Pinterest-%s.md" % name)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    open(outp, "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")
    print("  → 20-我的提示词/Pinterest-%s.md（%d 张）" % (name, len(pins)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards", action="store_true", help="列出你的所有板子")
    ap.add_argument("--export", metavar="板子名", help="导出指定名字的板子")
    ap.add_argument("--export-all", action="store_true", help="导出全部板子")
    ap.add_argument("--download", action="store_true", help="同时把图片下载进仓库")
    a = ap.parse_args()

    token = os.environ.get("PINTEREST_TOKEN", "").strip()
    if not token:
        print("缺少 PINTEREST_TOKEN 环境变量。")
        print("到 https://developers.pinterest.com/apps/ 建 app，申请 boards:read / pins:read，")
        print("拿到 token 后： export PINTEREST_TOKEN=xxx")
        return 1
    if not (a.boards or a.export or a.export_all):
        ap.print_help(); return 0

    boards = paginate("/boards", token, {"page_size": 100})
    if boards is None:
        print("取板子失败——检查 token 与 scope。"); return 1
    print("共 %d 个板子" % len(boards))
    if a.boards:
        for b in boards:
            print("  %-36s %4d pins  id=%s" % (b.get("name", "")[:36], b.get("pin_count", 0), b.get("id")))
        return 0

    if a.export:
        hit = [b for b in boards if b.get("name") == a.export] or \
              [b for b in boards if a.export in (b.get("name") or "")]
        if not hit:
            print("没找到板子：%s" % a.export); return 1
        for b in hit:
            export_board(token, b, a.download)
    else:
        for b in boards:
            export_board(token, b, a.download)
    print("\n完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
