#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_local.py —— 把你**自己文件夹里的图**扫进库，按流派归类。

## 它解决什么

权威层的 141 张流派卡是从博物馆抓的 CC0 图（`fetch_art.py`）。
但你自己的参考图在你自己硬盘上，是另一回事：私人收集、可能没授权、
数量不定、而且**你希望它们和流派卡挂在同一张图谱里**。

这个脚本做中间那一段：扫描 → 测量 + 建议 → 你确认 → 归入本地图库。

## 为什么不做「扫一遍自动分好类」

实测过（396 张、72 个流派），按模型把握程度分层看准确率：

    第一名与第二名分差 ≥1.5   覆盖  2% 的图   准确率 100%
                        ≥1.0        7%           80%
                        ≥0.6       19%           66%
                        ≥0.3       41%           54%   ← 抛硬币

**高把握的只覆盖 7% 的图；放宽到有用覆盖率时准确率就是掷硬币。**
所以自动归类不成立 —— 正确形态是「脚本给建议 + 你看一眼确认」，
这也和这个库一贯的「宁可少不要错」一致。

## 三层结构

    层 1 · 权威    10-流派/            141 张流派卡 + 99-附件/images/<流派>/   随仓库发布
    层 2 · 你的图库 15-我的图库/          ← 本脚本产出，链回 [[流派卡]]         gitignore
                   99-附件/images-local/<流派>/                               gitignore
    暂存            pinterest/          丢图区，不进图谱

层 2 的每篇笔记都 `[[链回]]` 对应的流派卡，所以图谱是**一张连通的图**：

    我的图库-巴洛克 → 巴洛克 → 流派总览 → …

## 用法

    # 1. 扫描一个目录（只分析，不复制文件）
    python3 scan_local.py ~/Pictures/refs --name 我的参考图

    # 2. 看待确认清单（按建议流派分组，标注把握程度）
    python3 scan_local.py --list

    # 3. 确认归类（序号来自 --list）
    python3 scan_local.py --file 3 baroque
    python3 scan_local.py --file 5,7,9 ukiyo-e
    python3 scan_local.py --file 12 --drop          # 不要这张

    # 只自动归「很有把握」的那些（准确率高但覆盖少，上限由 --min-margin 控制）
    python3 scan_local.py --auto --min-margin 1.0

    # 4. 生成/更新 15-我的图库/ 的笔记（跑 build_vault 也行，它会顺带生成）
    python3 build_vault.py
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "_data")
PENDING = os.path.join(DATA, "local_pending.json")
MANIFEST = os.path.join(DATA, "local_library.json")
LOCAL_IMAGES = os.path.join(VAULT, "99-附件", "images-local")
LOCAL_NOTES = os.path.join(VAULT, "15-我的图库")

IMAGES_DIR = os.path.join(VAULT, "99-附件", "images")
EXTS = (".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic", ".gif")

sys.path.insert(0, HERE)
for _c in (os.path.join(HERE, "vendor", "libs"),
           os.environ.get("ARTVAULT_DEPS", ""),
           os.path.expanduser("~/.artvault/deps")):
    if _c and os.path.isdir(_c) and _c not in sys.path:
        sys.path.insert(0, _c)


def _load(path, default):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            pass
    return default


def _save(path, obj):
    """原子写：先写临时文件再 rename。写到一半被打断不会留下截断的 JSON。"""
    import safefile as SF
    return SF.write_json(path, obj)


def _sha(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def _dhash(path, size=8):
    """差分哈希，用于跨来源去重（同一张图从不同地方来要认出来）。"""
    try:
        from PIL import Image
    except Exception:
        return None
    try:
        im = Image.open(path).convert("L").resize((size + 1, size), 1)
    except Exception:
        return None
    px = list(im.getdata())
    bits = []
    for r in range(size):
        for c in range(size):
            bits.append("1" if px[r * (size + 1) + c] > px[r * (size + 1) + c + 1] else "0")
    return "%016x" % int("".join(bits), 2)


def _hamming(a, b):
    return bin(int(a, 16) ^ int(b, 16)).count("1")


# ---------------------------------------------------------------- 去重索引
def known_hashes():
    """已经在本地的图（权威库 + 已归档的本地图）的哈希，避免重复收。"""
    idx = {}
    for root in (IMAGES_DIR, LOCAL_IMAGES):
        if not os.path.isdir(root):
            continue
        for r, _d, fs in os.walk(root):
            if "pinterest" in r:
                continue
            for f in fs:
                if f.lower().endswith(EXTS):
                    p = os.path.join(r, f)
                    h = _dhash(p)
                    if h:
                        idx[h] = os.path.relpath(p, VAULT)
    return idx


# ---------------------------------------------------------------- 扫描
def _inside_vault(folder):
    """判断目录是否落在仓库的图库范围内。"""
    full = os.path.realpath(os.path.expanduser(folder))
    for sub in (os.path.join(VAULT, "99-附件"),):
        if full == os.path.realpath(sub) or full.startswith(os.path.realpath(sub) + os.sep):
            return True
    return False


def iter_images(folder):
    """遍历图片。**跳过仓库自己的图库目录** —— 否则把 `99-附件/images` 当扫描
    源时会 654 张全复制进 `images-local/`，再扫一次又把副本复制一遍，
    磁盘越滚越大（实测过这个风险）。

    另外 os.walk 默认 followlinks=False，符号链接环不会造成死循环。
    """
    root_v = os.path.realpath(VAULT)
    skip = [os.path.realpath(os.path.join(VAULT, "99-附件")),
            os.path.realpath(os.path.join(VAULT, ".git")),
            os.path.realpath(os.path.join(VAULT, "_scripts", "vendor"))]
    for r, d, fs in os.walk(os.path.expanduser(folder)):
        d[:] = [x for x in d if not x.startswith(".")]
        # 剪掉库自己的目录（用 realpath 比，避免相对路径绕过去）
        rr = os.path.realpath(r)
        d[:] = [x for x in d
                if not any(os.path.realpath(os.path.join(rr, x)) == sp or
                           os.path.realpath(os.path.join(rr, x)).startswith(sp + os.sep)
                           for sp in skip)]
        for f in sorted(fs):
            if f.lower().endswith(EXTS) and not f.startswith("."):
                yield os.path.join(r, f)


def scan(folder, name=None, verbose=True):
    """扫描一个目录：测量 + CLIP 建议 + 去重。只写待确认清单，不动任何文件。"""
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        print("目录不存在：%s" % folder); return None

    if _inside_vault(folder):
        print("✗ 这个目录在仓库自己的图库范围内：%s" % folder)
        print("  扫它会把库里的图复制进 99-附件/images-local/，自己复制自己。")
        print("  要扫的是你自己的图片文件夹，例如 ~/Pictures/refs。")
        return None

    files = list(iter_images(folder))
    if not files:
        print("这个目录里没找到图片（支持 %s）" % "、".join(EXTS)); return None

    # 依赖检查放在打印之前 —— 不然会先说「找到 4 张图」再说「需要 Pillow」，
    # 顺序读起来别扭，也容易让人以为已经开始了
    import image_analysis as IA
    if IA.Image is None:
        # **要在这里拦住**。早先只 guard 了 import，而 image_analysis 模块
        # 本身能 import 成功（只是 Image 是 None），于是脚本继续往下跑，
        # 给每张图生成一条「读取失败」的记录 —— 用户拿到一列没有分析的清单，
        # 却不知道为什么。宁可明确报错。
        print("需要 Pillow：pip3 install --user Pillow")
        print("  或装到本地：pip3 install --target ./vendor/libs Pillow")
        return None

    if verbose:
        print("扫描 %s" % folder)
        print("  找到 %d 张图" % len(files))

    # CLIP 建议（一次性批量，避免每张图重算文本矩阵）
    import clip_embed as CE
    import clip_match as CM
    sug = {}
    if CE.available() is None:            # available() 返回 None 表示可用
        if verbose:
            print("  CLIP 可用，正在算流派建议…")
        sug = CM.suggest(files, topn=3)
    elif verbose:
        print("  ⚠ CLIP 不可用（没下模型），只做客观测量。")
        print("    python3 clip_embed.py download && python3 clip_embed.py build")

    known = known_hashes()
    pending = _load(PENDING, {"items": []})
    exist_src = {it.get("source") for it in pending["items"]}
    # **id 必须稳定**：早先用「在待确认清单里的位置」当序号，结果归类一张之后
    # 后面所有的编号都移位了 —— 你照着清单操作第二次就会归错图。
    # 改成扫描时就分配一个只增不减的 id，--list 显示它、--file 接收它。
    next_id = max([it.get("id", 0) for it in pending["items"]] + [0]) + 1

    items = []
    dup, done = 0, 0
    for i, p in enumerate(files, 1):
        if p in exist_src:
            done += 1
            continue
        rec = {"id": next_id, "source": p, "file": os.path.basename(p)}
        next_id += 1
        try:
            st = os.stat(p)
            rec["bytes"] = st.st_size
        except Exception:
            pass
        h = _dhash(p)
        rec["dhash"] = h
        if h and h in known:
            rec["duplicate_of"] = known[h]
            dup += 1
        r = IA.analyze(p)
        if r.get("error"):
            rec["error"] = r["error"]
        else:
            rec["size"] = r["size"]
            rec["orientation"] = r["orientation"]
            # 存**完整分析结果**：反推卡是事后由 build_vault 生成的，那时原图
            # 未必还在原处，只存摘要不够用来组七层提示词。（实测踩过：
            # 只存 summary，结果生成的反推卡里测量一栏是空的。）
            rec["analysis"] = {k: v for k, v in r.items() if k != "path"}
            lu, cl, tx = r["luminance"], r["color"], r["texture"]
            rec["summary"] = {
                "明度": lu["key"], "饱和度": cl["saturation"],
                "色温": cl["temperature"], "繁杂度": tx["busyness"],
                "主色": [d["hex"] for d in cl["dominant"][:3]],
            }
        if p in sug:
            rec["suggest"] = [{"slug": s, "name": n, "score": round(sc, 3)}
                              for s, n, sc in sug[p]]
        items.append(rec)
        if verbose and (i % 20 == 0 or i == len(files)):
            print("    %d/%d" % (i, len(files)))

    pending["items"].extend(items)
    pending["last_scan"] = {"folder": folder, "name": name or os.path.basename(folder),
                            "at": time.strftime("%Y-%m-%d %H:%M:%S"), "count": len(items)}
    _save(PENDING, pending)

    if verbose:
        print()
        print("✓ 新增待确认 %d 张%s%s"
              % (len(items),
                 ("，跳过已扫过的 %d 张" % done) if done else "",
                 ("，其中 %d 张和库里已有的图重复（已标记）" % dup) if dup else ""))
        print("  下一步：python3 scan_local.py --list")
    return items


# ---------------------------------------------------------------- 看待确认
def list_pending(limit=None):
    p = _load(PENDING, {"items": []})
    items = [it for it in p.get("items", []) if not it.get("filed") and not it.get("dropped")]
    if not items:
        print("没有待确认的图。先扫一个目录：python3 scan_local.py <目录>")
        return []

    print("待确认 %d 张（按 CLIP 建议的流派分组）\n" % len(items))
    groups = {}
    for it in items:
        s = (it.get("suggest") or [{}])[0].get("slug", "(无建议)")
        groups.setdefault(s, []).append((it.get("id"), it))

    for slug in sorted(groups, key=lambda k: -len(groups[k])):
        rows = groups[slug]
        name = (rows[0][1].get("suggest") or [{}])[0].get("name", "")
        print("── %s%s  (%d 张)" % (slug, (" · " + name) if name else "", len(rows)))
        for n, it in rows[:limit or 8]:
            mark = " ⟲重复" if it.get("duplicate_of") else ""
            s = it.get("summary") or {}
            sug = it.get("suggest") or []
            conf = ""
            if len(sug) >= 2:
                m = sug[0]["score"] - sug[1]["score"]
                conf = "把握%s" % ("高" if m >= 1.0 else "中" if m >= 0.6 else "低")
            print("   %3d  %-34s %-8s %s%s  %s"
                  % (n, it["file"][:34], s.get("明度", ""), conf,
                     (" 建议:" + "/".join(x["slug"] for x in sug[:3])) if sug else "", mark))
        if len(rows) > (limit or 8):
            print("      … 另有 %d 张" % (len(rows) - (limit or 8)))
        print()
    print("确认归类：  python3 scan_local.py --file <编号> --to <流派>")
    print("丢弃：      python3 scan_local.py --file <序号> --drop")
    print("只归高把握：python3 scan_local.py --auto --min-margin 1.0")
    return items


def all_pending():
    p = _load(PENDING, {"items": []})
    return p, [it for it in p.get("items", []) if not it.get("filed") and not it.get("dropped")]


# ---------------------------------------------------------------- 归类
def file_items(nums, slug=None, drop=False, verbose=True):
    """把待确认清单里的第 N 项归入某流派（或丢弃）。"""
    from movements import MOVEMENTS
    by_slug = {m["slug"]: m for m in MOVEMENTS}
    p, items = all_pending()
    if not items:
        print("没有待确认的图。"); return 0

    if not drop and slug not in by_slug:
        print("未知流派：%s" % slug)
        cands = [s for s in by_slug if slug and slug.lower() in s.lower()][:6]
        if cands:
            print("你是不是想找：%s" % "、".join(cands))
        return 1

    man = _load(MANIFEST, {"items": {}})
    dest_dir = os.path.join(LOCAL_IMAGES, slug) if not drop else None
    by_id = {it.get("id"): it for it in items}
    ok = 0
    for n in nums:
        it = by_id.get(n)
        if it is None:
            print("  没有这个编号：%d（编号是扫描时分配的，用 --list 查）" % n)
            continue
        if drop:
            it["dropped"] = True
            ok += 1
            if verbose:
                print("  ✗ 丢弃 %s" % it["file"])
            continue
        # 复制进库（用流派做子目录，文件名带序号避免撞名）
        os.makedirs(dest_dir, exist_ok=True)
        stem, ext = os.path.splitext(it["file"])
        safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in stem)[:48]
        seq = len([k for k in man["items"]
                   if k.startswith("99-附件/images-local/%s/" % slug)]) + 1
        fn = "%02d-%s-%s%s" % (seq, slug, safe, ext.lower())
        dest = os.path.join(dest_dir, fn)
        try:
            shutil.copy2(it["source"], dest)
        except Exception as e:
            print("  ✗ 复制失败 %s：%s" % (it["file"], str(e)[:50])); continue
        rel = os.path.relpath(dest, VAULT).replace(os.sep, "/")
        # 存**完整分析结果**而不是摘要 —— 卡是事后由 build_vault 生成的，
        # 那时原图已经不在原处了，摘要不够用来组反推。
        import reverse_prompt as RP
        rec = RP.record(it["source"], it.get("analysis"),
                        [(x["slug"], x["name"], x["score"]) for x in (it.get("suggest") or [])],
                        source=it["source"],
                        extra={"dhash": it.get("dhash"), "sha": _sha(dest)})
        rec["movement"] = slug
        rec["title"] = stem
        rec["added_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        man["items"][rel] = rec
        it["filed"] = True
        it["filed_as"] = rel
        ok += 1
        if verbose:
            print("  ✓ %s → %s" % (it["file"][:34], rel))
    _save(PENDING, p)
    _save(MANIFEST, man)
    if verbose:
        print("\n归入 %d 张。跑 python3 build_vault.py 生成 15-我的图库/ 的笔记。" % ok)
    return ok


def auto_file(min_margin=1.0):
    """只自动归「第一名比第二名高 min_margin」的图。

    实测 margin≥1.0 时准确率 80%（但只覆盖 7% 的图）；margin≥1.5 是 100%
    （覆盖 2%）。默认 1.0 —— 宁可少归，错归比不归糟。
    """
    _, items = all_pending()
    nums = []
    for it in items:
        sug = it.get("suggest") or []
        if it.get("duplicate_of") or len(sug) < 2:
            continue
        if sug[0]["score"] - sug[1]["score"] >= min_margin:
            nums.append(it.get("id"))
    if not nums:
        print("没有达到把握阈值（分差 ≥%.1f）的图。" % min_margin)
        print("实测这个阈值只覆盖约 7% 的图 —— 剩下的需要你看一眼再归。")
        return 0
    print("自动归类 %d 张（把握阈值 ≥%.1f，实测这一档准确率约 80%%）\n" % (len(nums), min_margin))
    # 按建议流派分组后逐组归类
    groups = {}
    by_id = {it.get("id"): it for it in items}
    for n in nums:
        groups.setdefault(by_id[n]["suggest"][0]["slug"], []).append(n)
    total = 0
    for slug, ns in groups.items():
        print("→ %s" % slug)
        total += file_items(ns, slug)
    return total


def status():
    p, items = all_pending()
    man = _load(MANIFEST, {"items": {}})
    print("待确认：%d 张" % len(items))
    print("已归入本地图库：%d 张" % len(man.get("items", {})))
    by = {}
    for rel, it in man.get("items", {}).items():
        by[it["movement"]] = by.get(it["movement"], 0) + 1
    if by:
        print("按流派：")
        for k in sorted(by, key=lambda x: -by[x]):
            print("   %-24s %d" % (k, by[k]))
    ls = p.get("last_scan")
    if ls:
        print("上次扫描：%s（%s，%d 张）" % (ls["folder"], ls["at"], ls["count"]))


def main():
    ap = argparse.ArgumentParser(description="把你自己的图扫进库并按流派归类")
    ap.add_argument("folder", nargs="?", help="要扫描的目录")
    ap.add_argument("--name", help="给这批图起个名字（记进清单）")
    ap.add_argument("--list", action="store_true", help="看待确认清单")
    ap.add_argument("--status", action="store_true", help="看总体进度")
    ap.add_argument("--file", help="要归类的序号，逗号分隔，如 3 或 5,7,9")
    ap.add_argument("--to", help="配合 --file：归到哪个流派（slug 或中文名）")
    ap.add_argument("--drop", action="store_true", help="配合 --file 使用：丢弃这些")
    ap.add_argument("--auto", action="store_true", help="只自动归高把握的")
    ap.add_argument("--min-margin", type=float, default=1.0,
                    help="自动归类的把握阈值，默认 1.0（实测该档准确率约 80%%，仅覆盖约 7%%）")
    ap.add_argument("--limit", type=int, default=8, help="--list 每组显示几张")
    a = ap.parse_args()

    if a.folder:
        return 0 if scan(a.folder, a.name) is not None else 1
    if a.status:
        status(); return 0
    if a.auto:
        auto_file(a.min_margin); return 0
    if a.file:
        try:
            nums = [int(x) for x in a.file.replace("，", ",").split(",") if x.strip()]
        except ValueError:
            print("--file 要编号，如 3 或 5,7,9（用 --list 查）"); return 1
        if a.drop:
            file_items(nums, drop=True); return 0
        if not a.to:
            print("要指定归到哪：--file %s --to <流派>" % a.file); return 1
        # --to 允许写中文名
        import artvault_core as A
        c = A.lookup(a.to)
        file_items(nums, c["slug"] if c else a.to)
        return 0
    list_pending(a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
