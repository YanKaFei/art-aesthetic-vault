#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shot_import.py —— 把上游 video-shotcraft 的「镜头配方卡」读成结构化数据。

## 上游是什么、不是什么（这一步决定整个模块的归类）

上游 [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)
（Apache-2.0）是一套**动效工作室 skill**：157 张镜头配方卡，按 10 个类别分：
`opening / camera / interaction / data / typography / ui-entrance / transition /
effects / rhythm / outro`。每张卡讲的是「**这一下怎么落地**」——
动效核心、参数表（帧数、缓动、幅度）、已知坑、Remotion 参考实现。

**它不是电影风格卡。** 对比本库已有的两条轴：

    `10-movements/`  轴 = 艺术流派   讲「这个流派长什么样」（色彩/光照/媒介）
    `40-films/`      轴 = 导演-电影  讲「这部片长什么样」（含六色配色板、剧照）
    `45-shots/`      轴 = 运镜招式   讲「这一下怎么做出来」（帧数/缓动/参数）

所以**不套七层**：157 张上游卡里没有一张有色彩或光照字段，而"动效核心"
不是"风格层"。给它套七层只能靠编 —— 那正是本库最反对的事。
卡片保留上游自己的四字段结构（适用/时长/能量/标签），这是诚实的做法。

## 与 40-films 的关系：互补，不是重复

`40-films/` 每张卡的「五、AI 视频层」里有**运动**与**运镜**两行，
那是描述性的（如「缓慢横移跟随，前景遮挡物在镜头前滑过」）。
这个模块提供同一类运镜的**参数化落地**（多少帧、什么缓动、多少幅度）。
两条轴各管一段：电影卡说「要什么画面」，镜头卡说「那一下怎么拍出来」。

## 许可

Apache-2.0。所以每张卡都记上游路径、仓库与 commit，卡面上写明来源，
**不得读起来像本站原创**。上游 `references/shots/ATTRIBUTION.md` 另有一层
说明要原样转述：动效手法研究自公开作品，但**全部实现从零重写**，
仓库不含任何原片片段、截图、美术资产；且「公开发布≠授权」。

## 用法

    python3 shot_import.py --check          # 只校验夹具/上游能解析
    python3 shot_import.py --import         # 从夹具（离线）导入 _data/shots/
    python3 shot_import.py --from-github    # 从 GitHub raw 拉最新再导入
"""

import argparse
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# 上游身份：写进每张卡，来源可回查
UPSTREAM_REPO = "Vincentwei1021/video-shotcraft"
UPSTREAM_URL = "https://github.com/Vincentwei1021/video-shotcraft"
UPSTREAM_COMMIT = "5e71af35a2daee492dd3ea93e5e8903f32dcd13c"
UPSTREAM_LICENSE = "Apache-2.0"
# 离线夹具就是上游那张卡的逐字副本（Apache-2.0 允许），所以可以拿它当来源
FIXTURE_DIR = os.path.join(HERE, "tests", "fixtures", "shots")
DATA_DIR = os.path.join(HERE, "_data", "shots")

# 段落名 → 语义键。**保留原段名**（读者看的就是这个名字），
# 同时给一个语义键供程序使用。变体必须都认：
#   实测 10 个类别里，effects/outro 用「两式选型」，另有「单式选型」，
#   其余用「动效核心」—— 三者是同一段的不同说法。
SECTION_KEYS = {
    "意图": "intent",
    "动效核心": "motion",
    "两式选型": "motion",
    "单式选型": "motion",
    "三式选型": "motion",
    "参数表": "params",
    "已知坑": "pitfalls",
    "参考实现": "reference",
}


class BadCard(Exception):
    """卡的结构不对。**必须带上路径** —— 否则上游改版时只看到一行报错，
    不知道是哪张卡坏了（失败模式②）。"""


def _frontmatter(text):
    m = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    raw = m.group(1)
    fm = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def _sections(body):
    """按 `## 标题` 切段，返回 [{title, key, body}]，保持原顺序。"""
    parts = re.split(r"^##\s+(.+?)\s*$", body, flags=re.M)
    out = []
    # parts = [前言, 标题1, 正文1, 标题2, 正文2, ...]
    for i in range(1, len(parts) - 1, 2):
        title = parts[i].strip()
        content = parts[i + 1].strip()
        out.append({"title": title,
                    "key": SECTION_KEYS.get(title, "other"),
                    "body": content})
    return out


def parse_card(text, path=None):
    """解析一张卡。结构不对就抛 BadCard（带 path）。"""
    fm, body = _frontmatter(text)
    name = (fm.get("name") or "").strip()
    if not name:
        raise BadCard("%s：frontmatter 里没有 name（上游结构可能变了）"
                      % (path or "<内存>"))
    secs = _sections(body)
    if not secs:
        raise BadCard("%s：正文里一个 `## 段落` 都没有（上游结构可能变了）"
                      % (path or "<内存>"))

    def sec(key):
        for s in secs:
            if s["key"] == key:
                return s["body"]
        return ""

    tags = fm.get("标签") or ""
    tags = [t.strip() for t in re.split(r"[,，、/]", tags) if t.strip()]
    if not tags and path:
        # 上游只有 66/157 张带「标签」字段，其余靠目录名归类别。
        # 不做猜测式补全：目录名本身就是类别，标签保持为空是事实。
        tags = []
    return {
        "name": name,
        "slug": name,
        "category": (path.split("/")[2] if path and "/" in path else ""),
        "one_liner": fm.get("一句话", ""),
        "purpose": fm.get("适用", ""),
        "duration": fm.get("时长", ""),
        "energy": fm.get("能量", ""),
        "tags": tags,
        "sections": secs,
        "intent": sec("intent"),
        "motion": sec("motion"),
        "params": sec("params"),
        "pitfalls": sec("pitfalls"),
        "reference": sec("reference"),
        "path": path or "",
        "source_repo": UPSTREAM_REPO,
        "source_url": UPSTREAM_URL,
        "source_path": path or "",
        "source_commit": UPSTREAM_COMMIT,
        "license": UPSTREAM_LICENSE,
    }


def parse_dir(root=None):
    """递归解析一个上游 `references/shots/` 目录树。

    `ATTRIBUTION.md` 不是卡，跳过。返回按 (类别, name) 排序的列表 ——
    顺序稳定，生成物才不会每次 diff 都在抖。
    """
    root = root or FIXTURE_DIR
    cards = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith(".md") or fn == "ATTRIBUTION.md":
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            path = "references/shots/" + rel
            try:
                txt = open(full, encoding="utf-8").read()
            except Exception as e:
                raise BadCard("%s：读不了（%s）" % (path, e))
            cards.append(parse_card(txt, path=path))
    cards.sort(key=lambda c: (c["category"], c["name"]))
    return cards


# ------------------------------------------------------------------ 从 GitHub
def fetch_from_github():
    """从 GitHub raw 拉上游全部卡（备用路径；夹具已经够用时不必要）。"""
    import json as _json
    api = ("https://api.github.com/repos/%s/git/trees/%s?recursive=1"
           % (UPSTREAM_REPO, UPSTREAM_COMMIT))
    req = urllib.request.Request(api, headers={"User-Agent": "artvault",
                                               "Accept": "application/vnd.github+json"})
    tree = _json.loads(urllib.request.urlopen(req, timeout=60).read().decode("utf-8"))
    paths = [x["path"] for x in tree.get("tree", [])
             if x["path"].startswith("references/shots/") and x["path"].endswith(".md")
             and not x["path"].endswith("ATTRIBUTION.md")]
    out = []
    for p in sorted(paths):
        url = "https://raw.githubusercontent.com/%s/%s/%s" % (UPSTREAM_REPO, UPSTREAM_COMMIT, p)
        r = urllib.request.Request(url, headers={"User-Agent": "artvault"})
        out.append(parse_card(urllib.request.urlopen(r, timeout=60).read().decode("utf-8"),
                              path=p))
    out.sort(key=lambda c: (c["category"], c["name"]))
    return out


def save(cards):
    os.makedirs(DATA_DIR, exist_ok=True)
    # 先清掉旧的：卡被上游删掉时不能留下孤儿 json（否则生成出幽灵卡）
    for fn in os.listdir(DATA_DIR):
        if fn.endswith(".json"):
            os.remove(os.path.join(DATA_DIR, fn))
    for c in cards:
        with open(os.path.join(DATA_DIR, c["name"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(c, f, ensure_ascii=False, indent=1, sort_keys=True)
    return len(cards)


def main():
    ap = argparse.ArgumentParser(description="导入上游 video-shotcraft 的镜头配方卡")
    ap.add_argument("--check", action="store_true", help="只解析夹具，报告统计")
    ap.add_argument("--import", dest="do_import", action="store_true",
                    help="从离线夹具导入 _data/shots/")
    ap.add_argument("--from-github", action="store_true",
                    help="从 GitHub raw 拉上游最新再导入")
    a = ap.parse_args()
    if not (a.check or a.do_import or a.from_github):
        ap.print_help()
        return 0

    if a.from_github:
        cards = fetch_from_github()
        print("从 GitHub 拉到 %d 张卡" % len(cards))
    else:
        cards = parse_dir()
    cats = {}
    for c in cards:
        cats[c["category"]] = cats.get(c["category"], 0) + 1
    print("解析成功：%d 张卡 / %d 类" % (len(cards), len(cats)))
    for k in sorted(cats):
        print("   %-14s %d" % (k, cats[k]))
    if a.do_import or a.from_github:
        n = save(cards)
        print("已写入 %s（%d 个 json）" % (DATA_DIR, n))
    elif a.check:
        print("（--check 只校验，不写盘）")
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 shot_import.py --import",
          ["把上游 video-shotcraft 的镜头配方卡（Apache-2.0）导入本库。",
           "  --check        只解析夹具，报告统计",
           "  --import       从离线夹具写入 _data/shots/",
           "  --from-github  从 GitHub raw 拉上游最新再导入",
           "",
           "夹具是上游卡文件的逐字副本（tests/fixtures/shots/），",
           "所以默认路径离线可跑；上游改版时测试会在这里红。"])
    sys.exit(main())
