#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_vault.py —— 用 movements.py 的数据 + _data/*.json 的抓取结果，
生成整个 Obsidian 仓库的所有 Markdown 笔记。

用法：  python3 build_vault.py
重复运行是安全的：所有自动生成的文件都会被整体覆盖。
你自己写的笔记请放在 20-我的提示词/ 下，那个目录不会被碰。
"""

import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
DATA_DIR = os.path.join(HERE, "_data")

# 仓库地址只在**这一处**定义，README（中/英）与 skill 文档都引用它。
# 之前中英两版各写了一遍，结果中文版写成了 GitHub 的**显示名**而不是
# 用户名，克隆命令直接 404 —— 单一来源就不会再漂移。
# （显示名不写进这里：它是个人信息，而且对读代码的人没有信息量。）
REPO_SLUG = "YanKaFei/art-aesthetic-vault"
REPO_URL = "https://github.com/" + REPO_SLUG

sys.path.insert(0, HERE)
from movements import (MOVEMENTS, CATEGORIES, by_category,  # noqa: E402
                       build_positive)
import keyword_map  # noqa: E402
import refs  # noqa: E402
import artvault_core as _AC  # noqa: E402  （层的中文名只在这里定义一次）

LEGEND_LAYER = dict(_AC.LAYER_ZH)

# 笔记里**不再**写「本文件由脚本生成」这类工程标记 —— 读者打开一张流派卡
# 应该看到艺术作品，而不是构建信息。
#
# 但清理必须仍然是安全的：不能误删用户自己放进这些目录的笔记（实测踩过 ——
# 早先按「不在本次生成列表里就删」，用户在 10-流派/ 放一篇手写笔记，
# 跑一次 build_vault 就没了）。原来靠笔记里的生成标记当判据，现在改成
# 靠**上一次的生成清单**：这里只记我们自己写过哪些文件，除此之外一律不碰。
GENERATED_MANIFEST = os.path.join(DATA_DIR, "generated.json")

# ---------------------------------------------------------------- 发布视图
# README 里那几个统计数字（多少张图、多少篇笔记）必须描述**别人 clone 之后
# 真正拿到的东西**，不能描述作者这台机器上的工作树。
#
# 踩过的坑：README 写着「654 张公共领域实图」，克隆下来只有 442 张。原因是
# 统计直接 os.walk 了 99-附件/images/，而里面 212 张 Pinterest 图是 gitignore 的
# —— 在作者机上存在，在克隆里不存在。同一份 README，作者看是对的，读者看到
# 的就是虚报。20-我的提示词/ 的笔记数同理（本地 16 篇、克隆 3 篇）。
#
# 所以统计口径改成「git 跟踪的文件」：git 就是这个仓库「什么会发布」的权威
# 定义，不用再手写一份忽略规则去追着 .gitignore 跑（那份规则一定会漂移）。
# 不是 git 仓库时（比如用户把 _scripts/ 单独拷出来跑）退化为文件系统视图，
# 并在构建输出里说明。
_TRACKED = None


def tracked_files():
    """返回 git 跟踪的文件（相对仓库根的 POSIX 路径）；不是 git 仓库时返回 None。"""
    global _TRACKED
    if _TRACKED is not None:
        return _TRACKED or None
    try:
        r = subprocess.run(["git", "-C", VAULT, "ls-files", "-z"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            _TRACKED = set()
            return None
        _TRACKED = set(x.decode("utf-8", "surrogateescape")
                       for x in r.stdout.split(b"\0") if x)
    except Exception:
        _TRACKED = set()
        return None
    return _TRACKED or None


def shipped(rel_paths):
    """把候选路径收敛成「克隆之后还在」的那些。

    路径统一转成相对 VAULT 的 POSIX 形式再和 git 索引比对，所以
    Windows 的反斜杠和大小写差异都不会让统计漏项。
    """
    rels = [os.path.relpath(p, VAULT).replace(os.sep, "/") for p in rel_paths]
    tracked = tracked_files()
    if tracked is None:
        return rels
    return [r for r in rels if r in tracked]


def publish_stats():
    """README 里那几个数字，按**发布视图**算一遍。

    抽成独立函数是为了让 verify_vault.py 能拿到同一份口径做比对 ——
    不然「README 说自己有多少东西」和「验收脚本认为应该有多少」会各算各的，
    而这次的 bug 恰恰就是两者都漏了同一件事（把 gitignore 的图算进去）。
    """
    img_abs = []
    for r, _d, fs in os.walk(os.path.join(VAULT, "99-附件", "images")):
        for f in fs:
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff")):
                img_abs.append(os.path.join(r, f))
    img_rel = shipped(img_abs)
    # 只算**真的流派**目录：取 images/ 之后的第一段路径，再和流派 slug 求交集。
    # 直接用 basename(dirname()) 会把 pinterest/ 和嵌套子目录也算进来
    # （实测那样会得到 92，而真实是 81）。
    mv_dirs = {r.split("images/", 1)[1].split("/")[0] for r in img_rel if "images/" in r}
    note_rel = shipped(glob.glob(os.path.join(VAULT, "*", "**", "*.md"), recursive=True))
    return {
        "n_img": len(img_rel),
        "img_mb": int(round(sum(os.path.getsize(os.path.join(VAULT, r))
                                for r in img_rel) / 1048576.0)),
        "n_mv_with_img": len(mv_dirs & {m["slug"] for m in MOVEMENTS}),
        "n_scripts": len(shipped(glob.glob(os.path.join(HERE, "*.py")))),
        "n_notes": len([r for r in note_rel
                        if r.split("/", 1)[0] in ("00-导航", "10-流派",
                                                  "20-我的提示词", "90-模板")]),
    }


_WRITTEN = set()


def w(rel, text):
    p = os.path.join(VAULT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + "\n")
    _WRITTEN.add(rel.replace(os.sep, "/"))
    return rel


def sweep_generated(dirs=("00-导航", "10-流派", "15-我的图库")):
    """删掉这些目录里**本次没有生成**的 .md。

    这三个目录是 100% 生成物，所以清理是安全的（`20-我的提示词/` 绝不碰）。
    不加这一步的话，删掉一个页面模板之后旧文件会永远留在库里 ——
    实测踩过：把「反推工具链」从生成列表里去掉后，那份 .md 还在，
    链接也还都能解析，于是没有任何检查能发现它已经成了孤儿。
    """
    prev = None
    if os.path.exists(GENERATED_MANIFEST):
        try:
            prev = set(json.load(open(GENERATED_MANIFEST, encoding="utf-8")).get("files") or [])
        except Exception:
            prev = None
    removed, kept = [], []
    for d in dirs:
        full = os.path.join(VAULT, d)
        if not os.path.isdir(full):
            continue
        for r, _dirs, fs in os.walk(full):
            for f in fs:
                if not f.endswith(".md"):
                    continue
                p = os.path.join(r, f)
                rel = os.path.relpath(p, VAULT).replace(os.sep, "/")
                if rel in _WRITTEN:
                    continue
                # **只删「上一次确实是我们生成的文件」。**
                # 判据来自 GENERATED_MANIFEST（上一次运行写下的清单），
                # 不是笔记内容 —— 笔记里已经没有生成标记了。
                # 没有清单时（这次改动后的第一次运行）回退到旧标记，
                # 过渡一次之后清单接管。
                if prev is None:
                    try:
                        head = "".join(open(p, encoding="utf-8").readlines()[:4])
                    except Exception:
                        continue
                    if "auto-generated by build_vault.py" not in head:
                        kept.append(rel)
                        continue
                elif rel not in prev:
                    kept.append(rel)
                    continue
                try:
                    os.remove(p)
                    removed.append(rel)
                except Exception:
                    pass
    if kept:
        print("  （保留了 %d 个非生成物的文件：%s%s）"
              % (len(kept), "、".join(kept[:3]), "…" if len(kept) > 3 else ""))
    return removed


def load_works(slug):
    p = os.path.join(DATA_DIR, slug + ".json")
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return []


# ------------------------------------------------------------------ 流派卡
# 署名清洗的实现在 providers.clean_attribution —— 抓取时和渲染时共用同一份，
# 避免两处逻辑各自漂移。这里只是薄封装（渲染时再过一遍，兜住历史 JSON 里的脏值）。
from providers import clean_attribution as _clean_attribution  # noqa: E402


def _clean_meta(wk, mv=None):
    """返回 (artist, date, medium) 三元组，脏值已被换成得体内容。

    artist 一栏走 display_artist 的**正向校验**：只有当作者能对上该流派
    自己的艺术家关键词、或能从标题里可靠恢复时才显示，否则写「佚名」。
    黑名单永远列不全（实测 Daderot / Gary Todd / Cbl62 / Joaquín Martínez
    Rosado… 一个接一个冒出来），正向校验才收得住。
    """
    w = _clean_attribution(dict(wk))
    if mv is not None:
        from providers import display_artist as _da
        w["artist"] = _da(w, mv.get("artist_keys") or [],
                          mv.get("exclude_keys"), mv.get("title_keys"))
    return w["artist"], w["date"], w["medium"]


def movement_note(mv, works, local_map=None):
    slug = mv["slug"]
    lines = []
    A = lines.append
    A("---")
    A("type: 流派")
    A("流派: %s" % mv["name_zh"])
    A("英文: %s" % mv["name_en"])
    A("时期: %s" % mv["period"])
    A("地区: %s" % mv["region"])
    A("分类: %s" % mv["category"])
    A("图片授权: %s" % ("CC0 / 公共领域" if works else "无"))
    A("配色: [%s]" % ", ".join('"%s"' % h for h, _ in mv["palette"]))
    A("标签:")
    A("  - 流派")
    A("  - %s" % mv["name_en"].lower().replace(" ", "-"))
    A("---")
    A("")
    A("# %s · %s" % (mv["name_zh"], mv["name_en"]))
    A("")
    A("> [!abstract] 一句话")
    A("> **%s**" % mv["one_liner"])
    A("")
    A("| 分类 | 时期 | 地区 | 代表艺术家 |")
    A("|---|---|---|---|")
    A("| %s | %s | %s | %s |" % (
        mv["category"], mv["period"], mv["region"],
        "、".join(a for a, _ in mv["artists"][:4])))
    A("")
    A("---")
    A("")
    # 一、核心主张
    A("## 一、核心主张")
    A("")
    for c in mv["core"]:
        A("- %s" % c)
    A("")
    # 二、视觉语言拆解
    A("## 二、视觉语言拆解（六维）")
    A("")
    A("| 维度 | 拆解 |")
    A("|---|---|")
    for k, v in mv["visual"].items():
        A("| **%s** | %s |" % (k, v))
    A("")
    # 三、配色
    A("## 三、配色板")
    A("")
    for h, name in mv["palette"]:
        A("- **%s** `%s`" % (name, h))
    A("")
    A("> [!example] 配色提示词（直接粘）")
    A("> `%s`" % ", ".join("%s %s" % (n, h) for h, n in mv["palette"]))
    A("")
    # 四、提示词结构
    A("## 四、提示词结构")
    A("")
    A("> 每一层都能单独拆出来复用。镜头层是「要什么景别」而非流派属性，")
    A("> 所以不并入下面的整段，按画面需要自己接。")
    A("")
    A("| 层 | 可复用片段 |")
    A("|---|---|")
    order = [("style", "风格"), ("lighting", "光照"), ("color", "色彩"),
             ("composition", "构图"), ("medium", "媒介"), ("mood", "情绪"), ("camera", "镜头")]
    for key, label in order:
        A("| **%s** | `%s` |" % (label, mv["prompt"][key]))
    A("")
    A("### 整段正向提示词")
    A("")
    A("```text")
    A("%s" % build_positive(mv).strip())
    A("```")
    A("")
    A("> 这是**风格层**，接在你自己的主体描述后面用：")
    A("> `<你的主体>, %s`" % mv["prompt"]["style"][:80])
    A("")
    A("### 负向提示词")
    A("")
    A("```text")
    A("%s" % mv["negative"].strip())
    A("```")
    A("")
    # 五、视频层 —— 两块可直接粘贴的中文提示词
    import video_prompt as VP
    vp = VP.build(mv)
    A("## 五、AI 视频层")
    A("")
    A("> A 块给 **Seedance 2.5**，B 块给 **MiniMax H3**。两块格式不同，"
      "**别混用** —— 原因见 [[视频提示词结构]]。")
    A("")
    A("### A. Seedance 2.5 五段式")
    A("")
    A("```text")
    A(vp["seedance"])
    A("```")
    A("")
    A("### B. MiniMax H3（中文自然语言，直接粘进输入框）")
    A("")
    A("```text")
    A(vp["h3"])
    A("```")
    A("")
    A("> [!important] 这个流派的视频关键")
    A("> %s" % mv["video"]["note"])
    A("")
    A("| 参考 | 内容 |")
    A("|---|---|")
    A("| **运动** | %s |" % mv["video"]["motion"])
    A("| **运镜** | %s（%s） |" % (mv["video"]["camera"], vp["camera_zh"]))
    A("| **建议时长** | %d 秒%s |" % (
        vp["duration"],
        "（这个流派画面几乎静止，别硬加运镜）" if vp["static"] else
        "（H3 单次上限 15 秒；要更长需分段生成，接缝处会有一致性损耗）"))
    A("")
    # 六、代表作品
    A("## 六、代表作品（CC0 实图）")
    A("")
    if works:
        A("*全部来自开放授权数据源，图片与元数据均为 CC0 / 公共领域，可自由使用。*")
        A("")
        for i, wk in enumerate(works, 1):
            A("### %d. %s" % (i, wk["title"]))
            A("")
            if wk.get("local_image"):
                A("![[%s]]" % os.path.basename(wk["local_image"]))
                A("")
            _a, _d, _m = _clean_meta(wk, mv)
            meta = " · ".join(x for x in [_a, _d, _m] if x)
            A("**%s**" % (meta or "—"))
            A("")
            A("[%s](%s)" % (wk["source"], wk.get("page_url") or "#"))
            A("")
    else:
        A("> 本库暂未收录该流派的公共领域实图。")
        A("")
    # 本地图库入口 —— 只在**用户本机有图**时出现。
    # 清单是 gitignore 的，所以别人 clone 后这一行不存在，不会留下悬空链接。
    # 刻意只放一行链接、不铺开图片：万一这一行被误提交，也只暴露「有几张」，
    # 不暴露图片本身（图在 gitignore 的 99-附件/images-local/ 里）。
    _n_local = len((local_map or {}).get(mv["slug"], []))
    if _n_local:
        A("> [!tip] 我的收藏")
        A("> 你自己扫进来的 **%d 张** → [[我的图库-%s]]" % (_n_local, mv["name_zh"]))
        A("")

    # 七、翻车点
    A("## 七、常见翻车点")
    A("")
    for p in mv["pitfalls"]:
        A("- %s" % p)
    A("")
    # 八、关联
    A("## 八、关联流派")
    A("")
    for s in mv["see_also"]:
        tgt = next((m for m in MOVEMENTS if m["slug"] == s), None)
        A("- [[%s]]" % (tgt["name_zh"] if tgt else s))
    A("")
    # 九、出处 —— 只在**确实有**的时候才出现这一节。
    # 出处是「这一层的说法从哪来」，不是装饰：没有就整节省略，
    # 不写「待补」占位符（占位符会让人以为这张卡有出处）。
    _refs = refs.refs_for(mv["slug"])
    if _refs:
        A("## 九、出处")
        A("")
        A("| 层 | 概念 | 出处 |")
        A("|---|---|---|")
        for _layer, _topic, _src, _url in _refs:
            A("| %s | %s | [%s](%s) |"
              % (LEGEND_LAYER.get(_layer, _layer), _topic, _src, _url))
    A("---")
    A("")
    A("← [[流派总览]] · [[分类索引-%s]]　|　延伸阅读 [[提示词拆解方法]]" % mv["category"])
    return "\n".join(lines)



# ------------------------------------------------------------------ 技能树
# 分类下的编辑性分组（哪些流派在叙事上归属同一支）
SUBGROUPS = {
 "西方古典与近代": [
   ("中世纪与拜占庭", ["byzantine","romanesque","gothic","international-gothic"]),
   ("文艺复兴", ["early-renaissance","renaissance","early-netherlandish","venetian-school","mannerism"]),
   ("巴洛克与古典", ["baroque","caravaggisti","dutch-golden-age","rococo","classicism","neoclassicism"]),
   ("19 世纪", ["romanticism","realism","naturalism","orientalism","academic-art","pre-raphaelite"]),
   ("印象派前后", ["impressionism","neo-impressionism","post-impressionism","nabis","symbolism","japonism"]),
   ("世纪之交", ["art-nouveau","vienna-secession","arts-and-crafts"]),
   ("美国与近代诸派", ["hudson-river-school","luminism","tonalism","ashcan-school","american-realism",
                    "regionalism","precisionism","social-realism","socialist-realism","muralism",
                    "magic-realism","metaphysical-art","neo-romanticism","naive-art",
                    "classical-realism","kitsch","new-objectivity"]),
 ],
 "现代主义与战后": [
   ("表现与野兽", ["expressionism","fauvism","der-blaue-reiter"]),
   ("立体与未来", ["cubism","orphism","futurism"]),
   ("几何抽象", ["suprematism","constructivism","de-stijl","bauhaus"]),
   ("达达与超现实", ["dada","surrealism"]),
   ("战后抽象", ["abstract-expressionism","color-field","art-informel","tachisme","lyrical-abstraction"]),
   ("波普与极简", ["pop-art","op-art","minimalism-art","art-deco"]),
 ],
 "先锋·当代·后现代": [
   ("三个总纲", ["avant-garde","contemporary-art","postmodernism"]),
   ("抽象诸支", ["abstract-art","hard-edge","post-painterly-abstraction"]),
   ("反艺术与媚俗", ["neo-dada","neo-pop","transavantgarde"]),
   ("边缘与身体", ["art-brut","outsider-art","feminist-art","native-art"]),
   ("公共与空间", ["street-art","land-art","kinetic-art","light-and-space"]),
   ("新媒介与后观念", ["digital-art","hyper-realism","photorealism","conceptual-art","neo-expressionism","superflat"]),
 ],
 "数字·亚文化·摄影美学": [
   ("朋克五支", ["cyberpunk","steampunk","dieselpunk","solarpunk","biopunk"]),
   ("网络怀旧", ["vaporwave","synthwave","pixel-art","retro-anime","dreamcore","y2k"]),
   ("动画与插画", ["anime-cel"]),
   ("银盐与印相", ["cyanotype","wet-plate","polaroid-film"]),
   ("氛围与生活", ["dark-academia","cottagecore","wabi-sabi","gothic-subculture","wasteland"]),
   ("平面设计", ["minimalist-design","swiss-style","memphis-design"]),
   ("电影感", ["film-noir"]),
 ],
 "东亚·南亚·伊斯兰": [
   ("中国", ["blue-green-landscape","ink-wash-xieyi","gongbi","song-academic","dunhuang-murals"]),
   ("日本", ["ukiyo-e","rimpa","suiboku-ga","yamato-e","sosaku-hanga","shin-hanga","zen-art"]),
   ("朝鲜半岛", ["minhwa"]),
   ("波斯与伊斯兰", ["persian-miniature","safavid-painting","mughal-miniature",
                   "islamic-geometric","arabic-calligraphy"]),
   ("喜马拉雅与原住民", ["tibetan-thangka","indigenism"]),
 ],
 "摄影与图像": [
   ("两大传统", ["pictorialism","straight-photography"]),
   ("社会与街头", ["documentary-photography","street-photography"]),
   ("观念与时尚", ["surrealist-photography","fashion-editorial"]),
 ],
}

CAT_ICON = {"西方古典与近代": "🏛", "现代主义与战后": "🎨",
            "先锋·当代·后现代": "🚀", "数字·亚文化·摄影美学": "🌃",
            "东亚·南亚·伊斯兰": "🀄", "摄影与图像": "📷"}


CAT_EN = {
 "西方古典与近代": "Western Classical & Modern",
 "现代主义与战后": "Modernism & Post-war",
 "先锋·当代·后现代": "Avant-Garde · Contemporary · Postmodern",
 "数字·亚文化·摄影美学": "Digital · Subculture · Photography",
 "东亚·南亚·伊斯兰": "East Asia · South Asia · Islam",
 "摄影与图像": "Photography & Image",
}

SUBGROUPS_EN = {
 "中世纪与拜占庭": "Medieval & Byzantine", "文艺复兴": "Renaissance",
 "巴洛克与古典": "Baroque & Classical", "19 世纪": "19th Century",
 "印象派前后": "Impressionism & After", "世纪之交": "Fin de Siecle",
 "美国与近代诸派": "American & Modern Schools",
 "表现与野兽": "Expressionism & Fauvism", "立体与未来": "Cubism & Futurism",
 "几何抽象": "Geometric Abstraction", "达达与超现实": "Dada & Surrealism",
 "战后抽象": "Post-war Abstraction", "波普与极简": "Pop & Minimal",
 "三个总纲": "The Three Umbrellas", "抽象诸支": "Abstract Branches",
 "反艺术与媚俗": "Anti-Art & Kitsch", "边缘与身体": "Margins & Body",
 "公共与空间": "Public & Space", "新媒介与后观念": "New Media & Post-Conceptual",
 "朋克五支": "Five Punks", "网络怀旧": "Internet Nostalgia",
 "动画与插画": "Animation & Illustration", "银盐与印相": "Silver & Print",
 "氛围与生活": "Atmosphere & Living", "平面设计": "Graphic Design",
 "电影感": "Cinematic", "中国": "China", "日本": "Japan",
 "朝鲜半岛": "Korea", "波斯与伊斯兰": "Persia & Islam",
 "喜马拉雅与原住民": "Himalaya & Indigenous",
 "两大传统": "Two Traditions", "社会与街头": "Social & Street",
 "观念与时尚": "Conceptual & Fashion", "其他": "Others",
}


CAT_COVER_EN = {
 "西方古典与近代": "Byzantine to Ashcan School - the backbone of European painting",
 "现代主义与战后": "Fauvism to Neo-Expressionism - 20th century experiment",
 "数字·亚文化·摄影美学": "Cyberpunk, vaporwave, analogue photo processes, internet subcultures",
 "先锋·当代·后现代": "Avant-garde, contemporary, postmodern, installation / performance / digital",
 "东亚·南亚·伊斯兰": "Dunhuang murals, Tibetan thangka, ukiyo-e, Persian miniature, Islamic geometry",
 "摄影与图像": "Pictorialism, straight photography, documentary, street, surrealist photography",
}


def category_table_en():
    cats = by_category()
    L = ["| Category | Movements | Covers |", "|---|---|---|"]
    for c in CATEGORIES:
        L.append("| %s | %d | %s |" % (CAT_EN.get(c, c), len(cats[c]), CAT_COVER_EN.get(c, "")))
    L.append("| **Total** | **%d** | 6 categories |" % len(MOVEMENTS))
    return "\n".join(L)


def skill_tree_en():
    """英文版技能树，结构与中文版一一对应"""
    by = {m["slug"]: m for m in MOVEMENTS}
    cats = by_category()
    L = ["Art Aesthetic Style Library", "│"]
    for ci, cat in enumerate(CATEGORIES):
        ms = cats[cat]
        own = {m["slug"] for m in ms}
        last_cat = (ci == len(CATEGORIES) - 1)
        L.append("%s %s · %d" % ("└─" if last_cat else "├─", CAT_EN.get(cat, cat), len(ms)))
        prefix = "   " if last_cat else "│  "
        groups = [(g, [x for x in ss if x in own]) for g, ss in (SUBGROUPS.get(cat) or [])]
        claimed = {x for _, ss in groups for x in ss}
        rest = [m["slug"] for m in ms if m["slug"] not in claimed]
        if rest:
            groups.append(("其他", rest))
        groups = [(g, ss) for g, ss in groups if ss]
        for gi, (gname, slugs) in enumerate(groups):
            last_g = (gi == len(groups) - 1)
            L.append("%s%s %s" % (prefix, "└─" if last_g else "├─",
                                  SUBGROUPS_EN.get(gname, gname)))
            sub = prefix + ("    " if last_g else "│  ")
            names = [by[x]["name_en"] for x in slugs]
            for i in range(0, len(names), 3):
                L.append("%s%s %s" % (sub, "└" if i + 3 >= len(names) else "├",
                                      " . ".join(names[i:i + 3])))
    return "\n".join(L)


def skill_tree():
    """生成 Markdown 代码块里的技能树。只从本分类取成员，避免跨分类重复。"""
    by = {m["slug"]: m for m in MOVEMENTS}
    cats = by_category()
    L = ["艺术审美风格库", "│"]
    for ci, cat in enumerate(CATEGORIES):
        ms = cats[cat]
        own = {m["slug"] for m in ms}
        last_cat = (ci == len(CATEGORIES) - 1)
        L.append("%s %s %s · %d 个流派" % ("└─" if last_cat else "├─",
                                           CAT_ICON.get(cat, "▪"), cat, len(ms)))
        prefix = "   " if last_cat else "│  "
        groups = [(g, [x for x in ss if x in own]) for g, ss in (SUBGROUPS.get(cat) or [])]
        claimed = {x for _, ss in groups for x in ss}
        rest = [m["slug"] for m in ms if m["slug"] not in claimed]
        if rest:
            groups.append(("其他", rest))
        groups = [(g, ss) for g, ss in groups if ss]
        for gi, (gname, slugs) in enumerate(groups):
            last_g = (gi == len(groups) - 1)
            L.append("%s%s %s" % (prefix, "└─" if last_g else "├─", gname))
            sub = prefix + ("   " if last_g else "│  ")
            names = [by[x]["name_zh"] for x in slugs]
            for i in range(0, len(names), 4):
                L.append("%s%s %s" % (sub, "└" if i + 4 >= len(names) else "├",
                                      " · ".join(names[i:i + 4])))
    return "\n".join(L)


# ------------------------------------------------------------------ 总览
def overview_note(works_map):
    A = []
    A.append("---"); A.append("type: MOC"); A.append("---"); A.append("")
    A.append("# 流派总览")
    A.append("")
    A.append("> [!abstract] 怎么用这个仓库")
    A.append("> 1. 从下面的分类找到你要的方向")
    A.append("> 2. 点进流派卡，看「视觉语言拆解」——那是判断依据")
    A.append("> 3. 直接抄「提示词结构」里的分层片段，拼到你自己的主体描述上")
    A.append("> 4. 视频任务再加「AI 视频层」的运动 + 运镜")
    A.append("")
    A.append("> [!tip] 先读方法，再抄模板")
    A.append("> 方法在 [[提示词拆解方法]]，视频结构在 [[视频提示词结构]]，")
    A.append("> 配色速查在 [[配色速查]]，")
    A.append("> 图片均为公共领域 / CC0，可自由使用与再分发。")
    A.append("")
    n_img = sum(1 for m in MOVEMENTS if works_map.get(m["slug"]))
    A.append("**共 %d 个流派**，其中 %d 个带 CC0 / 公共领域实图，%d 个为纯提示词卡。"
             % (len(MOVEMENTS), n_img, len(MOVEMENTS) - n_img))
    A.append("")
    A.append("## 分类")
    A.append("")
    A.append("| 分类 | 流派数 | 配图流派 | 覆盖范围 |")
    A.append("|---|---|---|---|")
    covers = {
        "西方古典与近代": "拜占庭 → 阿什坎学派，欧洲绘画史主干",
        "东亚·南亚·伊斯兰": "中国、日本、韩国、波斯、莫卧儿、伊斯兰装饰",
        "现代主义与战后": "野兽派 → 新表现主义，20 世纪实验",
        "数字·亚文化·摄影美学": "赛博朋克、蒸汽波、胶片工艺、网络亚文化",
    }
    for c in CATEGORIES:
        ms = by_category()[c]
        got = sum(1 for m in ms if works_map.get(m["slug"]))
        A.append("| [[分类索引-%s\|%s]] | %d | %d | %s |"
                 % (c, c, len(ms), got, covers.get(c, "")))
    A.append("")
    for c in CATEGORIES:
        ms = by_category()[c]
        A.append("## %s" % c)
        A.append("")
        A.append("[[分类索引-%s\|查看本类索引 →]]" % c)
        A.append("")
        A.append("| 流派 | English | 时期 | 配图 | 一句话 |")
        A.append("|---|---|---|---|---|")
        for m in ms:
            n = len(works_map.get(m["slug"]) or [])
            A.append("| [[%s]] | %s | %s | %s | %s |"
                     % (m["name_zh"], m["name_en"], m["period"],
                        ("%d 张" % n) if n else "—", m["one_liner"]))
        A.append("")
    A.append("---")
    A.append("")
    A.append("延伸：[[提示词拆解方法]] · [[视频提示词结构]] · [[配色速查]] · [[视觉签名]]")
    return "\n".join(A)


def category_note(cat, works_map):
    ms = by_category()[cat]
    A = []
    A.append("---"); A.append("type: MOC"); A.append("分类: %s" % cat)
    A.append("---"); A.append("")
    A.append("# %s" % cat)
    A.append("")
    A.append("← 返回 [[流派总览]]")
    A.append("")
    A.append("| 流派 | English | 时期 | 地区 | 配图 |")
    A.append("|---|---|---|---|---|")
    for m in ms:
        n = len(works_map.get(m["slug"]) or [])
        A.append("| [[%s]] | %s | %s | %s | %s |"
                 % (m["name_zh"], m["name_en"], m["period"], m["region"],
                    ("%d 张" % n) if n else "—"))
    A.append("")
    A.append("## 一句话速览")
    A.append("")
    for m in ms:
        A.append("- **[[%s]]** %s" % (m["name_zh"], m["one_liner"]))
    A.append("")
    return "\n".join(A)


# ------------------------------------------------------------------ 方法
METHOD = """---
type: 方法
---

# 提示词拆解方法

> [!abstract] 核心思路
> 一张参考图的「风格」不是一个词，而是**七个可以独立替换的层**。
> 把图拆成层，你就能把 A 图的风格套到 B 图的主体上——这才是参考库的意义。

## 一、七层拆解法

看到任何一张图（不管是 AI 生成还是名画），按这个顺序问七个问题：

| # | 层 | 要问的问题 | 产出 |
|---|---|---|---|
| 1 | **主体 Subject** | 画的是谁/什么？姿态、服装、数量、年龄 | `a young woman in a beige trench coat` |
| 2 | **风格 Style** | 哪个流派/艺术家/媒介？ | `baroque oil painting, tenebrism` |
| 3 | **光照 Lighting** | 光源在哪？几个？硬还是软？什么时间？ | `single hard light from off-frame, candlelight rim` |
| 4 | **色彩 Color** | 主色、辅色、饱和度、明度关系 | `bitumen black, warm gold, deep crimson` |
| 5 | **构图 Composition** | 视角、对称性、主体位置、纵深 | `diagonal dynamic, low angle, shallow depth` |
| 6 | **媒介 Medium** | 什么材料？质感？颗粒？ | `oil on canvas, visible impasto, aged varnish` |
| 7 | **情绪 Mood** | 观众应该感觉到什么？ | `dramatic, intense, theatrical` |

**第 2 层是你这个仓库的主要内容。第 3–7 层每张卡里都拆好了。**

## 二、拆解顺序为什么重要

很多人写提示词失败，是因为把七层混在一起写，然后靠试错调。

正确的做法是**逐层锁定**：

1. 先只写主体，确认构图和姿态对了
2. 加风格层，看整体味道对不对
3. 加光照层——**这一层对最终质感的影响最大**，比风格词本身还大
4. 加色彩层，修正偏色
5. 最后加媒介层（`oil on canvas` / `35mm film` / `watercolour`），锁死质感

> [!warning] 最大的坑
> 只写流派名（比如 `baroque`）几乎一定会得到一张平庸的图。
> 流派名必须配上**光照 + 色彩 + 媒介**三层，模型才知道你要什么。

## 三、层与层之间的解耦

拆成层的最大好处是：**层可以混搭**。

```
主体      一个赛博朋克赏金猎人站在雨中
风格层 ←  [[巴洛克]] 的 lighting + color
构图层 ←  [[赛博朋克]] 的 low angle + wet reflection
媒介层 ←  digital concept painting
```

这就是「用古典光打未来场景」的做法。

混搭搭配可以记在你自己的笔记里 —— `20-我的提示词/` 是本地目录，不进版本库。

## 四、每层的关键词数量

| 层 | 建议词数 | 说明 |
|---|---|---|
| 主体 | 15–40 | 越具体越好 |
| 风格 | 3–8 | 太多会互相打架 |
| 光照 | 4–8 | **性价比最高的一层** |
| 色彩 | 3–6 | 给具体颜色名，不要只写 `colorful` |
| 构图 | 3–6 | 镜头语言同时管构图和运镜 |
| 媒介 | 2–5 | 决定「看起来像什么做的」 |
| 情绪 | 3–6 | 影响姿态和氛围 |

## 五、负向提示词怎么写

负向提示词要**针对这个流派的典型错误**，不是通用的一长串垃圾词。

每个流派卡最后的「常见翻车点」就是负向词的来源。例如印象派要写
`black shadows, smooth blending, photorealistic`，而文艺复兴要写
`visible brushstrokes, impasto`——**两者的负向词几乎相反**。

> [!danger] 反面教材
> `worst quality, low quality, bad anatomy, ugly, deformed, blurry, watermark, text`
> 这一串是 2022 年的遗物。现代模型基本不需要，而且会占用注意力。
> 只在真的出现问题时，加**针对性的**负向词。

## 六、配套工具

拆解流程里**反推是自动的** —— 图丢进投递箱或扫进本地图库时会自动跑完
测量与流派匹配，产物落在**那张图自己的卡**上（`15-我的图库/`）。
不用你去装任何外部工具。

> [!tip] 反推结果长什么样
> 打开任意一张「我的图片」卡，你会看到：客观测量（七维）、最接近的流派、
> **按那个流派组好的七层提示词**、配色、两块视频提示词。
> 唯一留空的是「主体」—— 画面里画了什么要靠看图，卡上不替你编。

## 七、空白模板

要自己动手写卡时，从这三个模板复制：

| 模板 | 什么时候用 |
|---|---|
| [[作品拆解模板]] | 拿到一张参考图，按七层拆出可复用的层 |
| [[提示词卡模板]] | 把拆解结果固化成一张能反复用的提示词卡 |
| [[流派卡模板]] | 想给库里补一个流派时用 |

模板在 `90-模板/`，frontmatter 里的字段都是空的，填完即可。
"""


VIDEO = """---
type: 方法
---

# 视频提示词结构

> [!abstract] 文生视频 ≠ 文生图 + 「会动」
> 视频模型需要你额外说清楚三件事：**谁在动、怎么动、镜头怎么动**。
> 图像提示词只覆盖了「画面长什么样」，剩下的全靠这一页。
>
> **每张流派卡的「五、AI 视频层」已经按下面两套格式生成好了**，
> 复制粘贴即可。这一页讲的是为什么那样写。

## 一、先选模型，再选格式（这一步最容易错）

两个模型对提示词的要求**不一样**，混用会出问题：

| | **Seedance 2.5** | **MiniMax H3（海螺 3）** |
|---|---|---|
| 格式 | **五段式**：主体 + 风格 + 时间线 + BGM + 限制 | 官网 / API：**中文自然语言** |
| 单条时长 | 最长 30 秒 | **4–15 秒**（模型规格，不是显存限制） |
| 素材上限 | ≤50 个 | 图 ≤9 / 视频 ≤3（合计 ≤15s）/ 音频 ≤3 / 总数 ≤12 |
| 分辨率 | — | 短边默认 768；2K 需接 Regenerate-2K；24 FPS |

> [!danger] H3 官网/API **不要**手工结构化
> H3 是三段式系统：`Context-IR（理解+改写）→ H3-Base → Regenerate-2K`。
> 官网和 API 端 Context-IR 在跑，它会替你做结构化。
> 你手工塞 `[Shot N]`、时间戳进去，**会和它打架**——已知症状是
> **镜头数翻倍、时间戳错位**。所以卡片的 B 块是纯自然语言，
> 只把「它不会替你决定的东西」讲清楚：时长、镜头意图、声音层次、素材分工。
>
> 只有**本地权重端**（ComfyUI / SGLang）才需要逐字精确的英文结构化格式，
> 那要按官方 references 写，不在这套卡片里。

## 二、Seedance 2.5 的五段式

```text
提示词 = 主体 + 风格 + 时间线 + BGM + 限制
```

| 部分 | 解决什么 | 最少要写什么 |
|---|---|---|
| **主体** | 拍谁、拍什么 | 人物/产品、场景、核心事件、参考素材职责 |
| **风格** | 成片什么感觉 | 时长、画幅、质感、光线、色彩、镜头节奏 |
| **时间线** | 动作怎么从 0 秒发展到结尾 | 每段的起始状态、动作、运镜、结束状态 |
| **BGM** | 画面怎么获得节奏 | 类型、速度、乐器、情绪曲线、同步点 |
| **限制** | 哪些错误必须避免 | 只写最相关的 3–8 个风险 |

两条来自实践的原则：

1. **前两秒放最强的视觉信息** —— 不要「缓缓推进」开场，那是最常见的浪费。
   卡片里的时间线已经按这条生成。
2. **改起来要对得上位置**：画面不对改「主体/时间线」，节奏不对改「BGM」，
   稳定性不够改「限制」。五段分隔就是为了让你知道该改哪。

## 三、MiniMax H3 的自然语言

H3 官方给的运镜词表（中文写法在括号里）：

`Push In`（机位推进）· `Pull Out`（机位拉远）· `Zoom In / Zoom Out`（变焦，和推拉不同）
· `Pan`（横摇）· `Truck`（平行横移）· `Tilt`（俯仰）· `Pedestal`（升降）
· `Arc Shot`（环绕）· `Tracking Shot`（跟拍）· `Static Shot`（固定）
· `Roll`（翻滚）· `Shake`（抖动）· `POV`（主观视角）

三条最容易翻车的：

- **台词必须给逐字原文**。只写「他说了句话」→ 模型生成乱语，这是 H3 最高频的翻车。
- **风格要锚定**。参考图是动漫立绘就写明 2D 动画感；不锁风格模型会往写实漂。
- **三层声音各司其职**：环境音/动作音归声景；台词、歌声归主描述；
  只有观众听得到的配乐单独写，且**写乐器与速度，不要写情绪词**。

## 四、必须显式声明的五个维度

视频模型不会自己推断这些，你不写它就随机。

### 1. 运动 Motion
`walks slowly` / `turns her head` / `hair drifts in the wind` / `rain falls steadily`

### 2. 景别 Shot Size
`extreme close-up (ECU)` · `close-up (CU)` · `medium close-up (MCU)` · `medium shot (MS)`
· `medium wide shot (MWS)` · `wide shot (WS)` · `extreme wide shot (EWS)`

### 3. 机位 Camera Angle
`eye-level` · `high angle` · `low angle` · `dutch angle` · `aerial` · `bird's eye` · `over-the-shoulder`

### 4. 运镜 Camera Movement
见上面 H3 词表。**运镜本身带风格信息**——给印象派用手持快切、给表现主义用平稳滑轨，
都是错的。所以每张卡的运镜是和流派同源推导出来的。

### 5. 时段与光照 Time & Light
时段：`sunrise` · `dawn` · `daylight` · `dusk` · `sunset` · `night`
光源：`sunny` · `overcast` · `moonlight` · `firelight` · `practical lighting` · `neon`
类型：`soft` · `hard` · `rim` · `backlight` · `silhouette` · `low contrast` · `high contrast`

## 五、常见错误

| 错误 | 后果 | 修正 |
|---|---|---|
| 只写画面不写运动 | 模型给一个几乎静止的镜头 | 显式写 motion |
| 写 `camera moves` | 运镜方向随机 | 写 `dolly in` / `pan left` 等具体术语 |
| 运动描述过多 | 画面崩坏、闪烁 | 一个镜头只做 1–2 个动作 |
| 忘了写景别 | 一会儿全身一会儿特写 | 每次生成都明确 shot size |
| 光照和流派冲突 | 风格被冲淡 | 视频的光照层直接复用流派卡里的 |
| 给固定机位的流派加运镜 | 「静止」的流派被推成动态（如色调主义） | 看卡片里标了「几乎静止」的那些，别加运镜 |
| 把 Seedance 的五段式粘进 H3 官网 | 镜头数翻倍、时间戳错位 | H3 用自然语言块 |

## 六、来源

- 五段式结构：[huangbai-AI/sd-2-5-prompt](https://github.com/huangbai-AI/sd-2-5-prompt)
  （Seedance 2.5 / SD 2.5 提示词 Skill，含 15 个真实案例）
- H3 三段式架构、官方运镜词表与硬上限：
  [MiniMaxAI/MiniMax-H3 模型卡](https://huggingface.co/MiniMaxAI/MiniMax-H3) ·
  [MiniMax-AI/MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing/references) ·
  [ye4wzp/minimax-h3-prompt-skill](https://github.com/ye4wzp/minimax-h3-prompt-skill)
- 通用五维度（运动/景别/机位/运镜/光照）参照
  [EricRollei/Local_LLM_Prompt_Enhancer — WAN_GUIDE_REFERENCE.md](https://github.com/EricRollei/Local_LLM_Prompt_Enhancer/blob/main/docs/WAN_GUIDE_REFERENCE.md)

同类模型（Veo / Kling / Runway / HunyuanVideo）结构基本一致，
差异主要在运镜术语的接受度上。
"""


# TOOLCHAIN 模板已移除 —— 反推工具链不再是用户导航页。
# 内容迁到 skill/build/reference/tools.md（给动手扩展管线的人看）。



LICENSE = """---
type: 说明
---

# 版权与来源

> [!warning] 一句话原则
> **公共领域的作品可以自由下载、再分发；版权期内的作品只存链接和提示词，不存图。**

## 一、这个仓库里的图，授权是什么

`10-流派/` 里的所有图片都来自 **CC0 / 公共领域**的开放数据源：

| 来源 | 授权 | 本仓库的使用方式 |
|---|---|---|
| 克利夫兰艺术博物馆 | **CC0 1.0** | 主力源，API 免密钥，一次返回完整元数据 |
| **芝加哥艺术博物馆** | **CC0 1.0** | 主力源，IIIF 分级取图 |
| 大都会艺术博物馆 | **CC0 1.0** (Open Access) | 主力源，`isPublicDomain=true` 过滤 |
| 维基共享资源 | **逐条判定**，脚本只接受 Public domain / CC0 | 补全非西方流派与现代流派 |

> [!warning] 关于芝加哥：我曾经把它误判为「图片抓不到」
> 早期用 `curl` 测它的 IIIF 图片得到 403，就写进了「有 Cloudflare 保护」。
> 后来用 Python `requests` 复测 —— **200，图片正常下载**。
> 出口代理会拦 `curl` 的 TLS 指纹但放过 Python。
> 这个错误让我白白漏掉了一个 13 万件规模的一流源，教训记在 `_scripts/providers.py` 里。

CC0 意味着**没有版权限制**：你可以下载、修改、商用、再分发，
包括把图放进你自己的数据集训练模型。每张作品下面都标了来源和授权链接。

> [!important] 维基共享资源为什么只取 PD / CC0
> Commons 上还有大量 CC BY / CC BY-SA 的图，那些**可以用，但必须署名**。
> 脚本默认不收，是为了让整个仓库的授权状态保持单一——「随便用，不用想」。
> 如果你确实需要更大的覆盖面，运行 `python3 fetch_art.py --include-ccby`，
> 脚本会把每个文件的授权与来源页一并记录下来，署名信息不会丢。

> [!note] 为什么 1950 年后的流派没有图
> 抽象表现主义、波普、极简主义、超扁平这些流派的作品**仍在版权期内**，
> 任何开放数据源都不会提供。所以它们生成为**纯提示词卡**——
> 视觉语言和提示词结构照常拆解，只是不配图。这是授权策略的结果，不是缺失。

## 二、WikiArt 到底能不能爬

**技术上：能。**

实测结果：

| 检查项 | 结果 |
|---|---|
| `robots.txt` | `User-agent: *` / `Allow: /` —— 明确允许抓取 |
| 站点地图 | 公开 `sitemap_index.xml`，含 16 个子图，`paintings-1.xml` 一个就 4 万条 URL |
| 页面渲染 | 服务端渲染，curl 直接拿 HTML，不需要 JS |
| 图片直链 | 可下载，`!Large.jpg` 后缀约 750px |
| 反爬 | 有 Cloudflare，但普通 UA 可过；高频会触发验证 |

**法律上：不行（或者说，很灰）。**

WikiArt 的服务条款（2016 版，管辖地乌克兰）**没有**明文禁止自动化访问，
但它对版权作品的定义写得很清楚：

> "WikiArt presents both public domain and copyright protected artworks.
> The latter are showcased in accordance with fair use principle:
> as historically significant artworks · as used for informational and
> educational purposes · as readily available on the internet ·
> **as low resolution copies unsuitable for commercial use**"

也就是说，那些图在 WikiArt 上的存在**本身就是靠合理使用撑着的**：
低分辨率 + 教育目的 + 非商业。你再把它们批量下载下来重新分发，
就把这个平衡打破了——责任落到你头上。

另外，WikiArt **没有免费的官方 API**，它只有商业授权渠道。

### 所以本仓库的做法

| 做法 | 是否采用 |
|---|---|
| 从 CC0 美术馆抓图入库 | ✅ 采用，这是主力 |
| 在笔记里放 WikiArt 的**链接** | ✅ 采用，只作线索 |
| 批量下载 WikiArt 图片进仓库 | ❌ 不做 |
| 把 WikiArt 的图用于训练 | ❌ 不做 |

## 三、个人使用 vs 公开分发

Obsidian 仓库如果只是自己看、自己参考，几乎不存在风险。
风险出现在两个动作上：

1. **把仓库（含图）传到公开的 GitHub / 网盘** —— 这时候你在再分发
2. **把图喂给模型做训练然后发布模型** —— 这时候你在商业化利用

如果确实需要，就用 `_scripts/fetch_art.py` 重新抓 CC0 的图，
那些是可以随便分发的。

## 四、如果你就是想要 WikiArt 的规模

有两个合法替代路径：

1. **WikiArt 数据集**（Hugging Face / Kaggle 上有公开的影像数据集，
   本身就带 style / artist / genre 标签），用于研究目的下载使用
2. **用 CC0 数据源自己攒**：本仓库的脚本已经能跑，
   把 `movements.py` 里的 `sources` 查询词换掉就行，换个流派照样跑

## 五、自查清单

- [ ] 笔记里的每张图都来自 CC0 表里的来源
- [ ] 每张图下面有来源链接和授权标注
- [ ] 没有批量下载 WikiArt / Google Arts & Culture / Pinterest 的图
- [ ] 如果公开仓库，确认 `99-附件/` 里没有版权图
"""


PALETTE = """---
type: 速查
---

# 配色速查

> [!abstract] 用法
> 每个流派一套六色。写提示词时给**具体颜色名**，不要只写 `colorful`。
> 下面每行都可以直接复制进提示词。

## 全流派配色

{palette_body}

## 跨流派的用色规律

| 想要的感觉 | 配色策略 | 参考流派 |
|---|---|---|
| 庄严、古老 | 低饱和土色 + 金 | [[文艺复兴]]、[[新古典主义]] |
| 戏剧、压迫 | 大面积黑 + 单点暖色 | [[巴洛克]] |
| 轻快、甜美 | 高明度粉彩、几乎无黑 | [[洛可可]] |
| 敬畏、壮阔 | 暗底 + 炽热高光 | [[浪漫主义]] |
| 诚实、沉重 | 土色系、低饱和 | [[现实主义]] |
| 明亮、即时 | 高明度 + **彩色阴影** | [[印象派]] |
| 强烈、主观 | 高饱和非自然色并置 | [[后印象派]]、[[表现主义]] |
| 神秘、奢华 | 宝石色 + 金箔 | [[象征主义]] |
| 优雅、装饰 | 柔和植物色 + 暗金 | [[新艺术运动]] |
| 平面、明快 | 靛蓝 + 朱红 + 米纸 | [[浮世绘]] |
| 浪漫、忧郁 | 宝石色在暗底上发光 | [[拉斐尔前派]] |
| 理性、智性 | 赭灰褐、近乎单色 | [[立体主义]] |
| 怪诞、清澈 | 纯净蓝天 + 焦黄荒地 | [[超现实主义]] |
| 摩登、奢华 | 黑金 + 镀铬 + 深宝石 | [[装饰艺术]] |
| 理性、功能 | **只有三原色 + 黑白灰** | [[包豪斯]] |
| 疏离、迷幻 | 青 + 品红对撞 + 琥珀点缀 | [[赛博朋克]] |

## 配色的三个技术点

1. **阴影不要用黑**。印象派之后，阴影是有颜色的（紫、蓝、青）。
   写提示词时明确 `coloured shadows, no black shadows`。
2. **决定明度关系，比决定色相更重要**。`high key low contrast`（洛可可）
   和 `low key high contrast`（巴洛克）是两种完全不同的画面，
   哪怕色相一样。**明度关系写进提示词。**
3. **点缀色只给一个**。巴洛克的暖金、赛博朋克的琥珀——
   画面里只有一个「暖点」时，其他颜色才会显得冷。
"""


# ------------------------------------------------------------------ 关键词图谱
def keyword_graph_note(works_map):
    by_slug = keyword_map.by_slug_map(
        [{"slug": m["slug"], "name_zh": m["name_zh"], "name_en": m["name_en"]} for m in MOVEMENTS])
    A = []
    A.append("---"); A.append("type: MOC"); A.append("---"); A.append("")
    A.append("# 关键词图谱")
    A.append("")
    A.append("> [!abstract] 这一页解决什么问题")
    A.append("> 同一个概念常有多个叫法（先锋 / 前卫 / avant-garde；")
    A.append("> 超现实 / 超现实主义 / surrealism）。这一页把最容易混的几组")
    A.append("> 聚成簇，说清它们的差别，让你看到任何一个说法都能找到对应的卡。")
    A.append("")
    A.append("## 四组最容易混的关键词")
    A.append("")
    for cl in keyword_map.CLUSTERS:
        A.append("### %s · %s" % (cl["key"], cl["en"]))
        A.append("")
        A.append("**对应卡片：** [[%s]]" % by_slug[cl["card"]]["name_zh"] if cl["card"] in by_slug else "**对应卡片：**（未建卡）")
        A.append("")
        A.append(cl["define"])
        A.append("")
        A.append("**容易混淆的地方：**")
        A.append("")
        for t, d in cl["boundary"]:
            A.append("- **%s** —— %s" % (t, d))
        A.append("")
        A.append("**同义词 / 近义词（搜任何一个都能找到同一张卡）：**")
        A.append("")
        A.append("　".join("`%s`" % x for x in cl["synonyms"]))
        A.append("")
        A.append("**关联网卡：** " + " · ".join(
            "[[%s]]" % by_slug[c]["name_zh"] for c in cl["related_cards"] if c in by_slug))
        A.append("")
        A.append("> [!tip] 写提示词时怎么用")
        A.append("> " + cl["prompt_use"])
        A.append("")
    A.append("---")
    A.append("")
    A.append("各流派之间的近义与易混关系见 [[流派总览]] 的分类索引。")
    A.append("")
    return "\n".join(A)
# ------------------------------------------------------------------ AI 调用指南
AI_GUIDE = """---
type: 说明
---

# AI 调用指南

> [!abstract] 这一页解决什么
> 让 AI（Claude / Cursor / DSH / 自建 agent）能**主动调取这个仓库**，
> 在你有一个创意想法时，帮你从全部流派里取料、拼成可用的提示词。
>
> 仓库提供了三层接口，按你的技术栈挑一个：
> **CLI（最通用）→ MCP 服务（最省事）→ JSON 导出（最灵活）**。

## 一、三层接口

| 接口 | 文件 | 谁用 |
|---|---|---|
| **命令行** | `_scripts/artvault.py` | 任何能执行 shell 的 AI，无需配置 |
| **MCP 服务** | `_scripts/mcp_server.py` | Claude Desktop / Cursor / Cline 等支持 MCP 的客户端 |
| **JSON 导出** | `artvault.py dump` | 你要自己接进别的程序或做 RAG |

三者共用 `_scripts/artvault_core.py` 的同一套逻辑，行为一致。

## 二、命令行（推荐先从这个开始）

```bash
cd "_scripts"
python3 artvault.py categories                 # 6 大分类
python3 artvault.py list --with-images          # 有实图的流派
python3 artvault.py search "霓虹 雨夜"           # 模糊检索
python3 artvault.py search "压抑但华丽的光" --semantic   # 语义检索（需下过 CLIP 模型）
python3 artvault.py layers 巴洛克                # 只要七层提示词（最省 token）
python3 artvault.py show 印象派                  # 完整卡片
python3 artvault.py palette 印象派               # 配色
python3 artvault.py related 立体主义             # 关联流派
```

**给 AI 的调用约定**：任何命令加 `--json` 都会输出机器可读的 JSON。例如

```bash
python3 artvault.py --json layers 巴洛克
```

### 组合提示词：把创意想法变成分层提示词

```bash
# 自然语言：自动识别提到的流派，按意图词分配层级
python3 artvault.py compose "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \\
        --subject "a female bounty hunter in a wet neon alley"

# 显式跨流派混搭
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
        --color vaporwave --composition precisionism --subject "a lone samurai"
```

输出包含：**分层结果 + 正向提示词 + 负向提示词 + 配色 + 视频层 + 冲突消解记录**。

> [!tip] 跨流派混搭的冲突已经自动处理了
> 把不同流派的负向词合并会**打架**。实测例子：
> 浮世绘要求 `no cast shadows`，而巴洛克的光照层恰恰要 `deep crushed shadows`；
> 精确主义的负向词里有 `people / figures`，你的主体却是个武士。
>
> `compose` 会把打架的负向词**自动从负向提示词里拿掉**，并在
> 「已自动消解的冲突」里逐条说明拿掉了哪个、让位给谁。规则只有一条：
> **正向是意图，负向是护栏，护栏让位于意图。**
>
> 想拿到未经处理的负向词合集（自己判断）：加 `--keep-conflicts`。

## 三、MCP 服务（一次配置，长期可用）

在客户端配置里加上（以 Claude Desktop 为例，路径换成你的实际位置）：

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["{MCP_PATH}"]
    }
  }
}
```

配置文件的常见位置：

| 客户端 | 路径 |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Cline / 其他 | 见各自文档 |

暴露的工具：

| 工具 | 作用 |
|---|---|
| `search_movements(query, limit)` | 检索流派 |
| `get_movement(slug)` | 完整卡片 |
| `get_layers(slug)` | 只要七层提示词（省 token） |
| `compose_prompt(brief, subject, style, lighting, …)` | **拼提示词** |
| `get_palette(slug)` | 配色 |
| `find_related(slug)` | 关联流派 |
| `list_categories()` | 分类概览 |
| `analyze_image(path)` | **图片客观测量**：七维度 + 人脸景别/霍夫直线/显著性（新） |
| `match_movement(path, topn)` | **给一张图找最像的流派**（CLIP 语义匹配，含零样本）（新） |

纯标准库实现，**不需要 `pip install mcp`**。
后两个工具依赖 Pillow（图片分析）与 CLIP 模型（语义匹配），未装时会返回
明确原因和修复命令，不影响前七个工具。

## 四、给 AI 的提示词怎么写

在你的 agent 系统提示里加一段：

```text
你有一个艺术风格知识库，通过 artvault 工具访问。
当用户描述一个视觉创意时：
1. 先用 search_movements 找出相关的 2–4 个流派
2. 用 get_layers 取它们的提示词层
3. 用 compose_prompt 拼成完整提示词；返回的 dropped 字段是**已自动拿掉的**
   打架负向词，交付时提一句你拿掉了什么、为什么，别默默丢掉
4. 输出时说明每一层来自哪个流派，以及为什么这样搭配

不要凭记忆编造风格词——库里的流派覆盖从拜占庭到 Y2K，
所有术语都以库里的为准。
```

> [!tip] 为什么强调「以库里的为准」
> 大模型对艺术流派的记忆是模糊的、容易把相近的搞混（比如把 Art Nouveau
> 和 Art Deco 的视觉特征混在一起）。这个库的价值就是给出**具体到光照、
> 色彩、媒介**的可执行描述，而不是一个风格名词。

## 五、Pinterest 投递箱：人找图，AI 拆解

`pinterest/` 是投递箱。分工是：**你负责找图和判断，AI 负责拆解和归档。**

```
你把图丢进 pinterest/
        ↓  说「处理 pinterest 投递箱」
python3 _scripts/ingest_inbox.py --scan     ← 客观测量：尺寸/主色/感知哈希/配色最近的流派
        ↓  AI 逐张 read_image 看图
七层拆解 + 匹配 1–3 个流派 + 可复用提示词
        ↓  写入
20-我的提示词/投递箱-<日期>.md
        ↓
python3 _scripts/ingest_inbox.py --archive  ← 图移到 pinterest/_已归档/
```

为什么这样分工：Pinterest 的搜索是登录态、个性化的，
**你手动挑的图比任何爬虫抓的都准。**
而拆解是机械劳动，正好交给 AI。

脚本做客观测量，AI 做语义判断——两者都做自己擅长的。
配色距离那类数字**只是参考信号**：实测有张土色系的调色板照片，
配色距离算出来最接近「现实主义」，但那是土色重合，不是风格相近。

## 六、和 Obsidian 里的笔记怎么配合

| 场景 | 用哪个 |
|---|---|
| 你想**读**、建立审美直觉 | Obsidian 里看 [[流派总览]] 和流派卡 |
| 你想**查**某个词是什么 | Obsidian 里搜 [[关键词图谱]] |
| 你想**用**、生成东西 | 让 AI 调 `artvault` |
| 你想**存**自己的成果 | [[提示词卡模板]] 存到 `20-我的提示词/` |

> 仓库里的 Markdown 是给人看的，`artvault` 是给机器用的。两者同源——
> 都从 `_scripts/mv_*.py` 生成，改一处两边都更新。

"""

README_EN = """<div align="center">

# Art Aesthetic Style Library

**141 art movements, decomposed into swappable AI prompt layers**

Byzantine to Y2K ｜ East & South Asia · Islamic ｜ Photography ｜ Digital subcultures

{n_notes} notes · {n_img} public-domain images · {n_scripts} ready-to-run scripts

**English** ｜ [中文](README.md)

</div>

---

## What is this

Most "art style reference" collections are just image folders. You save a few hundred
pictures, and then when it's time to actually use them you don't know what to look at
or how to describe it. The images are dead weight.

This library does something different: **it breaks each movement's visual language into
seven layers that can be swapped independently.**

```
Subject  +  Style  +  Lighting  +  Color
         +  Composition  +  Medium  +  Mood  +  Camera
```

Once it's layered, you can take the **lighting** from one painting and put it on the
**subject** of a completely different one. That's what a reference library is actually for.

> ### A note on language
> **The prompt layers are already in English** - they're what you paste into a model.
> Only the explanations (visual breakdowns, pitfalls, why-it-works notes) are in Chinese.
> If you only want the prompts, you can use this library as-is.

### See it work

Say you want a bounty hunter in a neon-lit alley, but with classical painting light:

```
python3 artvault.py compose "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" --subject "a female bounty hunter in a wet neon alley"
```

It recognises that "巴洛克" (Baroque) is followed by "光照" (lighting) and takes
Baroque's lighting layer; Cyberpunk supplies style and composition. Output:

```
a female bounty hunter in a wet neon alley,             <- your subject
cyberpunk, neo-noir concept art, dense neon signage,    <- Style layer (Cyberpunk)
single hard light source from off-frame,                <- Lighting layer (Baroque)
deep crushed shadows, candlelight rim light,
cyan and magenta clash, amber accent, deep black,       <- Color layer (Cyberpunk)
low angle looking up at megastructures,                 <- Composition layer (Cyberpunk)
alienated, oppressive, intoxicating                     <- Mood layer
```

**Same subject, every layer independently replaceable.** That's the difference between
this and piling up style keywords.

---

## Skill tree

```
{skill_tree_en}
```

---

## What's inside

| | |
|---|---|
| **Movement cards** | **141**, in 6 categories. Each has a 6-axis visual breakdown, 7 prompt layers, a 6-color palette, a video layer, and known failure modes |
| **Public-domain images** | **{n_img}** ({img_mb} MB), covering {n_mv_with_img} movements |
| **Guides & methodology** | 18 notes (overview, keyword atlas, the 7-layer method, video structure, palette index, reverse-engineering toolkit...) |
| **Keyword atlas** | All **218 styles / 189 movements / 68 genres** mapped to a card |
| **Note templates** | 3 |
| **Scripts** | 21 - fetch, generate, search, compose, MCP server |

> **62 movements are "prompt-only cards."** Abstract Expressionism, Pop Art, Minimalism,
> Conceptual Art, Cyberpunk, Vaporwave and others are still in copyright, so no open data
> source will supply images. Their visual language and 7-layer structure are documented
> exactly the same way - just without pictures. This is deliberate, not a gap.

---

## How to use

### 1. As an Obsidian vault

Open the folder in Obsidian. Recommended entry points:

- `00-导航/提示词拆解方法.md` - **start here**, it explains the 7 layers
- `00-导航/流派总览.md` - overview of all 141 movements
- `10-流派/` - pick a movement, read its full breakdown
- `00-导航/关键词图谱.md` - look up any unfamiliar style term

### 2. From the command line (or let an AI drive it)

```bash
cd _scripts

python3 artvault.py categories              # 6 categories, 141 movements
python3 artvault.py search "neon rain"      # fuzzy search, Chinese or English
python3 artvault.py search "oppressive but ornate light" --semantic   # semantic (needs the CLIP model)
python3 artvault.py layers baroque          # just the 7 prompt layers
python3 artvault.py show ukiyo-e            # full card
python3 artvault.py palette cyberpunk       # 6-color palette
python3 artvault.py related cubism          # find related movements
python3 artvault.py --json layers baroque   # machine-readable
```

**The core feature is composition:**

```bash
# Explicit cross-era mixing
python3 artvault.py compose --style ukiyo-e --lighting baroque --color vaporwave --composition precisionism --subject "a lone samurai"
```

It **resolves layer conflicts for you.** When you mix movements, their negative prompts
fight each other - ukiyo-e forbids `cast shadows` while Baroque lighting *requires*
`deep crushed shadows`; Precisionism forbids `people` while your subject is a person.
**The model won't error**, it just produces subtly worse images that are very hard to debug.
So the conflicting negative terms are **dropped automatically** and listed under
"resolved conflicts", with the rule stated plainly: *intent wins, guardrails yield*.
Want the raw union instead? Pass `--keep-conflicts`.

### 3. Install as an AI skill (recommended)

The repo ships **two** skills, installed together:

| Skill | Purpose | Triggers when |
|---|---|---|
| `art-aesthetic-vault` | **Use** the library: search movements, pull the 7 layers, compose prompts | you ask "what style should this character be" |
| `build-art-aesthetic-vault` | **Build** a library from scratch | you say "I want one of these too" |

> [!note] Neither skill bundles data
> Both are **symlinks** into this repo - the data exists in exactly one place.
> If `mv_*.py` (141 movement definitions) were bundled into a skill there would be
> two copies, and they would drift. Measured: the bundled copy had 4 files out of
> sync with the repo, and libraries built from it had **wrong category assignments**.

```bash
cd skill && ./install.sh
```

It **symlinks** the skill into every skill directory present on your machine:

| Directory | Read by |
|---|---|
| `~/.agents/skills/` | DSH / Codex / general convention |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**Why symlink:** the skill resolves its own real path via `pwd -P`, derives the repo
root from it, and therefore **finds the vault wherever it lives - no configuration,
survives moving the repo**. No path is hardcoded anywhere in the skill.

```bash
./install.sh --copy        # copy instead of symlink (breaks if you move the repo)
./install.sh --uninstall   # remove
bash locate.sh             # manual vault lookup (for troubleshooting)
```

Start a **new AI session** for it to take effect.

### 4. As an MCP server (Claude Desktop / Cursor)

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<absolute path to this repo>/_scripts/mcp_server.py"]
    }
  }
}
```

10 tools: `search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`.
Pure standard library - **no `pip install mcp` needed** (the last two also need
Pillow / the CLIP model; without them they return a clear reason and the other
seven keep working).

---

## Why it's different

### 1. Not an image pack - a composable structure

An image pack gives you "what this feels like." This gives you "how to make it."
Every layer can be lifted out on its own. Swap the subject but keep the style layer,
and you have a style-transfer template.

### 2. Lighting is pulled out as its own layer

Most people write prompts as one undifferentiated blob and then debug by trial and error.
This library makes an explicit claim: **lighting affects the final texture more than the
style keywords do.** Every movement's lighting layer is a separate snippet you can drop
onto an unrelated subject.

### 3. Every movement has *targeted* negative prompts

**The specific failure modes of that movement**:

- Impressionism → `black shadows, smooth blending, photorealistic`
- Renaissance → `visible brushstrokes, impasto` (AI defaults to thick oil paint; Renaissance surfaces are smooth)
- Ukiyo-e → `3d shading, cast shadows, gradient` (AI adds volume automatically; ukiyo-e is flat)

**Note that different movements' negative prompts are often opposites** - which is exactly
why mixing them breaks, and exactly what this library manages for you.

### 4. Usable by AI, not just by you

LLMs have fuzzy memories about art movements and routinely confuse Art Nouveau with
Art Deco, or Barbizon with Impressionism. This library pins down concrete terminology
for 141 movements, so an AI calling it won't make things up.

### 5. Completeness is verifiable

The keyword atlas maps **all 218 styles / 189 movements / 68 genres** onto cards.

### 6. Public domain only - no second thoughts

All images come from CC0 / public-domain open sources. Free to use, modify,
redistribute, and train on.

### 7. Extensible

Adding a movement means adding one entry to one Python file. Image fetching, note
generation, keyword mapping and the AI interfaces all follow automatically.

---

## Quick start

```bash
git clone --depth 1 {REPO_URL}.git
cd art-aesthetic-vault

# immediate self-check
cd _scripts && python3 artvault.py categories
```

**Requirements:** Python 3.8+ and Obsidian (recommended).

**The core scripts use only the Python standard library - nothing to pip install.**

Optional dependencies - everything works without them, they just add capability:

```bash
# Pinterest grabbing and the image inbox
pip3 install --user requests Pillow

# Enhanced image-analysis dimensions (face framing / Hough lines / saliency)
# and semantic search
pip3 install --target ./vendor/libs numpy opencv-python-headless
```

> Installing into `vendor/libs` keeps your system Python clean, and the
> directory is gitignored. To skip them explicitly: `ARTVAULT_NO_EXT=1`.
> Note `artvault_vision.py` is macOS-only (it uses the system Vision
> framework); elsewhere it degrades gracefully and says why, without
> affecting any core feature.

---

## Regenerate / extend

```bash
cd _scripts

python3 fetch_art.py                  # fetch images for movements that lack them
python3 fetch_art.py impressionism    # one movement only
python3 fetch_art.py --per 12         # 12 images per movement
python3 build_vault.py                # regenerate every note from the mv_*.py data
```

### Adding a movement

1. Add an entry to the right `_scripts/mv_*.py` file
2. Add filter keywords to **`ARTIST_KEYS` in the same file** ← **required, or you'll pull in unrelated works**
3. `python3 fetch_art.py <slug>` then `python3 build_vault.py`

| Data file | Category |
|---|---|
| `mv_core.py` | the original 18 core movements |
| `mv_west.py` | Western Classical & Modern |
| `mv_asia.py` / `mv_asia2.py` | East Asia · South Asia · Islam |
| `mv_modern.py` / `mv_gaps.py` | Modernism & Post-war |
| `mv_contemporary.py` | Avant-Garde · Contemporary · Postmodern |
| `mv_visual.py` | Digital · Subculture · Photography |
| `mv_photo.py` | Photography & Image |

---

## Tool inventory

What each script in `_scripts/` does. Unless marked **optional**, all of them
need only Python 3 + Pillow.

### Entry points

| Script | What it does |
|---|---|
| `artvault.py` | Main query interface: `categories` `search` `layers` `show` `palette` `related` `compose` |
| `mcp_server.py` | Same capabilities exposed as an MCP server for Claude Desktop / Cursor |

### Sources & generation

| Script | What it does |
|---|---|
| `movements.py` | Aggregates all {n_mv} movement definitions — the single source of truth |
| `mv_*.py` | Movement cards and filter keywords (8 files, split by category) |
| `providers.py` | Four CC0 source adapters + three-layer filtering (AI images / flat works / artist match) |
| `fetch_art.py` | Image fetching: round-robin across sources, two-layer filtering, `--refresh` clears orphaned files |
| `build_vault.py` | **Generates** the Obsidian notes / README / LICENSE / .gitignore |
| `keyword_map.py` | Generates the keyword map |

### Image analysis

| Script | What it does |
|---|---|
| `image_analysis.py` | Seven objective dimensions: luminance / contrast / colour / harmony / composition / texture / line. Pure Pillow |
| `image_analysis_ext.py` | **Optional**: face framing / Hough lines / spectral-residual saliency. Needs numpy + opencv, skipped automatically if absent |
| `clip_embed.py` | **Optional**: CLIP image/text embeddings (ONNX, no PyTorch). Run `download` once for the model |
| `clip_match.py` | **Optional**: image-to-movement matching with CLIP (zero-shot + fusion) — the most accurate of the three routes |
| `artvault_vision.py` | **Optional**: macOS Vision semantic search (search by image / near-duplicates / similar movements) |
| `ingest_inbox.py` | Processes the `pinterest/` inbox, including the dimensions above in its scan |
| `verify_vault.py` | **Acceptance checks**: broken links / duplicate names / AI images / frontmatter / near-duplicates / licences / orphans |
| `github_setup.py` | Push, set as Template, set topics/description in one go (token never appears in argv) |
| `video_prompt.py` | Generates two Chinese video-prompt blocks per movement (Seedance 2.5 five-part + MiniMax H3 natural language) |
| `i2v_prompt.py` | **Image-to-video prompts**: turns one image's measurements into subject / motion / camera and fills the placeholders the per-movement version leaves behind |
| `scan_local.py` | **Scans your own image folders into the vault**: measurement + CLIP suggestions + dedupe → review list → files into `15-我的图库/` |
| `reverse_prompt.py` | **Composes the reverse-engineering card**: measurements + movement match + 7 layers + video prompts, shared by all three entry points |
| `pinterest_grab.py` | Pinterest inbox scraper (local use only; images are **not** committed) |

### Two conventions that are easy to miss

1. **Change the template, not the output.**
   `10-流派/*.md`, `00-导航/*.md` and `README.md` are all generated by
   `build_vault.py`; editing them directly loses the change on the next rebuild
   (this tool inventory itself lives in the template).
2. **`20-我的提示词/` is yours.** Scripts read it but never overwrite it.

---

## Three principles

1. **Better fewer than wrong.**
   Filtering deliberately does *not* have a "top up with whatever's available" fallback -
   if a movement yields one image, it gets one image.
   > The worst thing for a reference library isn't too few images, it's wrong ones.
   > Wrong references corrupt your instincts, and you won't notice.

2. **Lighting matters more than style keywords.**
   If you can only tune one layer, tune lighting.

3. **Don't invent movement terminology from memory.**
   LLM recall on art movements is unreliable and blurs related schools together.
   Use the concrete terms in the library.

---

## Image sources

All images come from public-domain / CC0 open sources (Cleveland, Art Institute of Chicago, The Met, Wikimedia Commons), verified entry by entry.
Free to use and redistribute. Every work is annotated with its source and license link.

**Code** MIT ｜ **Notes** CC BY 4.0

---

<div align="center">

If this is useful, a star is appreciated - PRs adding more movements are welcome

</div>
"""

# ------------------------------------------------------------------ 许可
LICENSE_TEXT = """MIT License

Copyright (c) 2026 艺术审美风格库 contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
# 内容授权单独成文件，**不混在 LICENSE 里**。
# 原因：GitHub 的许可证识别要求 LICENSE 是一份*纯粹*的许可文本，
# 末尾追加几段中文说明会让它认不出来，仓库侧栏就显示成「NOASSERTION」——
# 对一个公开仓库来说，那比写错还糟：读者不知道到底能不能用。
LICENSE_CONTENT = """# 内容授权

本仓库的**代码**采用 MIT License（见 [LICENSE](LICENSE)）。

**笔记内容**（`00-导航/`、`10-流派/`、`90-模板/`、`README.md` 等）
采用 Creative Commons Attribution 4.0 International (CC BY 4.0)：
<https://creativecommons.org/licenses/by/4.0/>

**图片**（`99-附件/images/`）来自公共领域 / CC0 开放数据源，
可自由使用、修改、再分发，包括用于商业用途与训练数据集。
"""



TEMPLATES = {
"流派卡模板.md": """---
type: 流派
流派: 
英文: 
时期: 
地区: 
配色: []
标签:
  - 流派
---

# {{流派}} · {{English}}

> [!abstract] 一句话
> 

| 时期 | 地区 | 代表艺术家 |
|---|---|---|
|  |  |  |

## 一、核心主张

- 

## 二、视觉语言拆解

| 维度 | 拆解 |
|---|---|
| 色彩 |  |
| 光影 |  |
| 笔触 |  |
| 构图 |  |
| 材质 |  |
| 情绪 |  |

## 三、配色板

- 

## 四、提示词结构

| 层 | 可复用片段 |
|---|---|
| 风格 |  |
| 光照 |  |
| 色彩 |  |
| 构图 |  |
| 媒介 |  |
| 情绪 |  |
| 镜头 |  |

### 整段正向提示词

```text

```

### 负向提示词

```text

```

## 五、AI 视频层

| 层 | 内容 |
|---|---|
| Motion 运动 |  |
| Camera 运镜 |  |

## 六、代表作品

## 七、常见翻车点

- 

## 八、关联流派

- [[]]
""",

"提示词卡模板.md": """---
type: 我的提示词
用途: 
主风格: 
混搭风格: []
模型: 
评分: 
标签:
  - 我的提示词
---

# {{标题}}

> [!abstract] 想做的效果
> 

## 参考图

```text
（把参考图拖进来）
```

## 七层拆解

| 层 | 内容 |
|---|---|
| 主体 |  |
| 风格 |  |
| 光照 |  |
| 色彩 |  |
| 构图 |  |
| 媒介 |  |
| 情绪 |  |

## 正向提示词

```text

```

## 负向提示词

```text

```

## 参数

| 项 | 值 |
|---|---|
| 模型 |  |
| 采样器 |  |
| 步数 |  |
| CFG |  |
| 尺寸 |  |
| 种子 |  |

## 结果与迭代

| 版本 | 改动 | 结果 |
|---|---|---|
| v1 |  |  |

## 学到什么

- 

## 关联流派

- [[]]
""",

"作品拆解模板.md": """---
type: 作品
作品: 
艺术家: 
年份: 
流派: 
来源: 
授权: 
标签:
  - 作品
---

# {{作品名}}

![[此处放图]]

**{{艺术家}}** · {{年份}} · {{材质}}

来源：[[]] · 授权：

## 为什么好

- 

## 七层拆解

| 层 | 内容 |
|---|---|
| 主体 |  |
| 风格 |  |
| 光照 |  |
| 色彩 |  |
| 构图 |  |
| 媒介 |  |
| 情绪 |  |

## 可以偷走的三个点

1. 
2. 
3. 

## 转成提示词

```text

```

## 所属流派

- [[]]
""",
}

README = """<div align="center">

# 艺术审美风格库

**把 141 个艺术流派的视觉语言，拆成可以直接用的 AI 提示词层**

从拜占庭到 Y2K ｜ 东亚 · 南亚 · 伊斯兰 ｜ 摄影谱系 ｜ 数字亚文化

{n_notes} 篇笔记 · {n_img} 张公共领域实图 · {n_scripts} 个即用脚本

[English](README.en.md) ｜ **中文**

</div>

---

## 这是什么

大部分人收集「艺术风格参考」的方式是存图——存了几百张，但真要用的时候不知道该看什么、
该怎么描述。图是死的。

这个库换个做法：**把每个流派的视觉语言拆成七个可以独立替换的层**。

```
主体 Subject  +  风格 Style  +  光照 Lighting  +  色彩 Color
              +  构图 Composition  +  媒介 Medium  +  情绪 Mood  +  镜头 Camera
```

拆成层之后，你才能把 A 图的光照套到 B 图的主体上。**这才是参考库真正的用处。**

### 看一眼它怎么工作

假设你想画「雨夜霓虹街头的赏金猎人」，同时想要古典绘画的光影质感：

```bash
python3 artvault.py compose \\
  "雨夜霓虹街头的赏金猎人，要巴洛克的光照，赛博朋克的构图" \\
  --subject "a female bounty hunter in a wet neon alley"
```

它会自动识别出「巴洛克」后面跟着「光照」→ 取巴洛克的光照层；
「赛博朋克」→ 取风格与构图层。然后拼成：

```
a female bounty hunter in a wet neon alley,        <- 你的主体
cyberpunk, neo-noir concept art, dense neon signage,   <- 风格层 · 赛博朋克
single hard light source from off-frame,               <- 光照层 · 巴洛克
deep crushed shadows, candlelight rim light,
cyan and magenta clash, amber accent, deep black,      <- 色彩层 · 赛博朋克
low angle looking up at megastructures,                <- 构图层 · 赛博朋克
alienated, oppressive, intoxicating                    <- 情绪层
```

**同一个主体，每一层都可以单独换掉。** 这是这个库和「风格词堆砌」的根本区别。

---

## 技能树

```
{skill_tree}
```

---

## 有多少东西

| | 数量 |
|---|---|
| **流派卡** | **141 张**，6 大分类，每张含六维视觉拆解 + 七层提示词 + 配色 + 视频层 |
| **公共领域实图** | **{n_img} 张**（{img_mb} MB），{n_mv_with_img} 个流派配了图 |
| **导航与方法论** | 17 篇（流派总览、关键词图谱、七层方法、视频结构、配色速查…） |
| **关键词图谱** | 全部 **218 styles / 189 movements / 68 genres** 的完整映射 |
| **笔记模板** | 3 个（流派卡 / 提示词卡 / 作品拆解） |
| **脚本** | 21 个，抓图、生成、检索、提示词合成、MCP 服务 |

> **62 个流派是「纯提示词卡」**——抽象表现主义、波普、极简主义、观念艺术、
> 赛博朋克、蒸汽波这些，作品仍在版权期内，任何开放数据源都不会提供图。
> 它们的视觉语言与七层结构照常拆解，只是不配图。这是刻意的设计，不是缺失。

---

## 怎么用

### 方式一：当作 Obsidian 仓库读

用 Obsidian 打开这个文件夹。建议从这个顺序进入：

1. `00-导航/提示词拆解方法.md` —— **先读这个**，理解七层是怎么回事
2. `00-导航/流派总览.md` —— 全部流派的总入口
3. `10-流派/` —— 挑一个你喜欢的流派，看它的完整拆解
4. `00-导航/关键词图谱.md` —— 以后看到陌生风格词就来这里查

### 方式二：让 AI 直接调用它

库不只是一堆给人看的 Markdown，还有一层**给机器用的接口**：

```bash
cd _scripts

python3 artvault.py categories              # 看 6 大分类
python3 artvault.py search "霓虹 雨夜"       # 模糊检索，中英文都行
python3 artvault.py search "压抑但华丽的光" --semantic   # 描述性说法：关键词抓不住，语义能
python3 artvault.py layers 巴洛克            # 只要七层提示词（最省 token）
python3 artvault.py show 浮世绘              # 完整卡片
python3 artvault.py palette 赛博朋克         # 六色配色
python3 artvault.py related 立体主义         # 找关联流派
python3 artvault.py --json layers 巴洛克     # 机器可读
```

**核心能力是组合**：

```bash
# 自然语言，自动分层
python3 artvault.py compose "雨夜霓虹的赏金猎人，要巴洛克的光照" --subject "a bounty hunter"

# 显式指定，跨时代混搭
python3 artvault.py compose --style ukiyo-e --lighting baroque \\
  --color vaporwave --composition precisionism --subject "a lone samurai"
```

它会**自动消解层级冲突**。跨流派混搭时负向词会互相打架——
浮世绘禁止 `cast shadows`，巴洛克光照却要求 `deep crushed shadows`；
精确主义禁止 `people`，而你的主体是个人物。
**模型不会报错**，只会表现为「出图质量莫名地差」，极难排查。
所以打架的负向词会被**自动从负向提示词里拿掉**，并在「已自动消解的冲突」里
逐条说明拿掉了什么、让位给谁。规则一句话：**正向是意图，负向是护栏，护栏让位于意图。**
想要原样合集自己判断，加 `--keep-conflicts`。

### 方式三：装成 AI skill（推荐）

仓库自带一个 skill，装上之后**任何支持 skill 的 AI 助手**在遇到视觉/审美类任务时
会自动查这个库，而不是凭记忆编造流派术语。

```bash
cd skill && ./install.sh
```

仓库提供**两个** skill，一次装好：

| skill | 干什么 | 什么时候触发 |
|---|---|---|
| `art-aesthetic-vault` | **用**库：检索流派、取七层提示词、跨流派拼提示词 | 你问「这个角色该用什么风格」 |
| `build-art-aesthetic-vault` | **建**库：从零建一套新的 | 你说「我也想要一套这样的库」 |

> [!note] 为什么两个 skill 都不自带数据
> 它们都是**软链**指向本仓库 —— 数据只有仓库这一份。
> `mv_*.py`（流派定义）如果被打包进 skill，就会出现两份、
> 必然会分叉。实测过：打包版本里有 4 个文件与仓库不同步，
> 用它建出来的库分类是错的。

它会把这些软链建到本机所有可用的 skill 目录：

| 目录 | 谁读它 |
|---|---|
| `~/.agents/skills/` | DSH / Codex / 通用约定 |
| `~/.claude/skills/` | Claude Code |
| `~/.codex/skills/` | Codex |

**为什么用软链**：skill 可以用 `pwd -P` 解析出自己的真实位置，
从而推断出仓库根目录 —— **仓库放在哪、移不移动都能自动找到**，不需要任何配置。
skill 里**没有写死任何路径**。

其他用法：

```bash
./install.sh --copy        # 复制安装（不用软链，但仓库移动后要重装）
./install.sh --uninstall   # 卸载
bash locate.sh             # 手动定位仓库（排查用）
```

装完**新开一个 AI 会话**才会生效。

### 方式四：接入 MCP（Claude Desktop / Cursor）

```json
{
  "mcpServers": {
    "artvault": {
      "command": "python3",
      "args": ["<本仓库绝对路径>/_scripts/mcp_server.py"]
    }
  }
}
```

暴露 10 个工具：`search_movements` `get_movement` `get_layers` `compose_prompt`
`get_palette` `find_related` `list_categories` `analyze_image` `match_movement`
`get_video_prompt`。
纯标准库实现，**不需要 pip 安装任何东西**（后两个工具另需 Pillow / CLIP 模型，
没装会返回明确原因，不影响前七个）。

---

## 它好在哪里

### 1. 不是图包，是可组合的结构

图包给你「这是什么感觉」，这个库给你「怎么做出这种感觉」。
每一层都可以单独摘出来复用，换主体不换风格层，就是风格迁移模板。

### 2. 光照层被单独拎出来了

大多数人写提示词时把一切混在一起，靠试错调。这个库明确告诉你：
**光照对最终质感的影响比风格词本身更大。**
每个流派的光照层都是独立一段，可以直接搬到别的主题上。

### 3. 每个流派都有「针对性负向词」

**针对这个流派的典型翻车点**：

- 印象派 → `black shadows, smooth blending, photorealistic`
- 文艺复兴 → `visible brushstrokes, impasto`（AI 默认会给油画加厚涂）
- 浮世绘 → `3d shading, cast shadows, gradient`（AI 会自动加立体感）

**注意不同流派的负向词经常是相反的**——这正是混搭会打架的原因，也是库帮你管住的东西。

### 4. AI 可以用，不只是你能看

大模型对艺术流派的记忆是模糊的，常把 Art Nouveau 和 Art Deco、
巴比松和印象派搞混。这个库把每个流派的具体术语固化下来，
AI 调用时不会瞎编。

### 5. 完整性有保证

关键词图谱**218 styles / 189 movements / 68 genres**

### 6. 只收公共领域，用起来不用想

全部图片来自 CC0 / 公共领域开放数据源，可以自由使用、修改、再分发，
也可以放进你自己的数据集。

### 7. 能扩展

加一个新流派只需要在一个 Python 文件里加一条定义。
抓图、生成笔记、关键词映射、AI 接口都会自动跟上。

### 8. 每一层的说法都追得到出处

流派卡的「九、出处」逐层列出该概念在权威术语表里的定义页，
用的是 Tate 的艺术术语词典。

### 9. 你手里那张图，也能直接变成视频提示词

流派卡上的视频提示词是**通用**的 —— 主体那一行是占位符。但你真正要干的事
通常是「我有这张图，让它动起来」。所以反推卡上的视频块走的是另一条路：

```bash
python3 i2v_prompt.py 你的图.jpg --slug baroque
```

主体的景别、在画面哪个位置、画面内部的动势方向、光要不要动、镜头推还是移，
全部从**这张图的客观测量**推出来（人脸景别 / 显著性中心 / 线条方向 /
细节密度 / 明暗结构），并附一份「推导依据」让你核对。
生成出来仍留着「谁、在做什么，你自己补一句」—— 内容只有看图的人知道，
脚本不替你编。

---

## 快速开始

```bash
git clone {REPO_URL}.git
cd art-aesthetic-vault

cd _scripts

# 先看这台机器现在能用什么、缺什么（不需要装任何东西就能跑）
python3 artvault.py doctor

# 立刻能用的自检
python3 artvault.py categories
```

**环境要求**：Python 3.8+ 和 Obsidian（推荐）。

**核心脚本只用 Python 标准库，不需要 pip 安装任何东西。**

可选依赖 —— 不装也能跑，装了多一层能力：

```bash
# 图片分析的增强维度（人脸景别 / 霍夫直线 / 显著性）与语义检索
pip3 install --target ./vendor/libs numpy opencv-python-headless
```

> 装到 `vendor/libs` 是为了不污染系统 Python，且该目录已 gitignore。
> 完整清单（每一项换来什么能力）见 `requirements-optional.txt`，
> 或者直接 `python3 artvault.py doctor` 让他告诉你缺什么。
> 不想装：`ARTVAULT_NO_EXT=1` 可显式关掉增强维度。
> 另：`artvault_vision.py` 只在 macOS 上可用（依赖系统自带 Vision 框架），
> 其他系统会自动降级并说明原因，不影响任何核心功能。

---

## 自己重新生成 / 扩展

```bash
cd _scripts

python3 fetch_art.py                  # 补抓所有还没有图的流派
python3 fetch_art.py impressionism    # 只抓指定流派
python3 fetch_art.py --per 12         # 每个流派 12 张
python3 build_vault.py                # 用 mv_*.py 里的数据重新生成全部笔记
```

### 加一个新流派

1. 在 `_scripts/mv_*.py` 对应的分类文件里加一条定义
2. 在**同一个文件的 `ARTIST_KEYS`** 里加过滤关键词 ← **必须，否则会抓进一堆无关作品**
3. `python3 fetch_art.py <slug>` 抓图
4. `git add` 新生成的笔记，**然后**才 `python3 build_vault.py`

> [!warning] 第 4 步的顺序不能反
> README 里的统计数字是按**发布视图**算的 —— 也就是 `git ls-files`，
> 「下一次提交会带走的文件」。所以如果先 `build_vault` 再 `git add`，
> 那一刻新笔记还没进索引，README 就会**少算**（实测少算 6 篇笔记），
> 而这份陈旧的 README 会被一起提交上去。
>
> 验收第 16 项会抓住这种情况（它就是为此存在的），但那时你已经在改提交了。
> 记住顺序：**先 add，再 build，最后把 README 也 add 进去。**

### 改完代码怎么验

两层，职责不重叠，**都要跑**：

```bash
python3 tests/smoke_test.py      # 把命令真的跑一遍：退出码 / 副作用 / 可复现性
python3 _scripts/verify_vault.py # 查内容一致性：断链 / 授权 / README 数字 / 双链
```

`tests/smoke_test.py` 只用标准库，不需要 pip 装东西，也能在干净 clone 上跑。
CI（GitHub Actions）在 Ubuntu × macOS、Python 3.9 × 3.12 上自动跑这两层。

> [!note] 为什么要「真的跑一遍」这一层
> 曾经 README 声称「654 张公共领域实图」，克隆下来只有 442 张 —— 虚报 48%。
> 这个 bug 穿过了当时**全部 15 项验收**：因为那些检查都在读文件（比 mtime、
> 比引用、比数字），没有一项会执行命令看看会不会出事。数字对不对是一类问题，
> **命令跑不跑得起来、跑完有没有留下垃圾**是另一类。


| 数据文件 | 负责的分类 |
|---|---|
| `mv_core.py` | 最初的 18 个主干流派 |
| `mv_west.py` | 西方古典与近代 |
| `mv_asia.py` / `mv_asia2.py` | 东亚·南亚·伊斯兰 |
| `mv_modern.py` / `mv_gaps.py` | 现代主义与战后 |
| `mv_contemporary.py` | 先锋·当代·后现代 |
| `mv_visual.py` | 数字·亚文化·摄影美学 |
| `mv_photo.py` | 摄影与图像 |

---

## 工具清单

`_scripts/` 下每个脚本的分工。除了标注**可选**的，都只要 Python 3 + Pillow。

### 门面

| 脚本 | 干什么 |
|---|---|
| `artvault.py` | 主查询接口：`categories` `search` `layers` `show` `palette` `related` `compose` `doctor` |
| `visual_lexicon.py` | **中文视觉词 → 英文短语**的桥。CLIP 文本塔只认英文，中文查询不过桥等于随机 |
| `eval_search.py` | 检索评测：A 组守卫精确度、B 组测语义增益，并扫出接管阈值 |
| `refs.py` | **艺术史出处**：把每层提示词的说法接到权威术语表；`--check-urls` 联网复验链接 |
| `visual_signature.py` | 从实图反推每流派的**可测量区间**；`check <图> --slug X` 校验一张图像不像该流派 |
| `mcp_server.py` | 同一套能力包装成 MCP server，给 Claude Desktop / Cursor 直连 |

### 数据源与生成

| 脚本 | 干什么 |
|---|---|
| `movements.py` | 汇总全部流派定义，是**唯一数据源** |
| `mv_*.py` | 流派卡片与过滤关键词（按分类分成 8 个文件） |
| `providers.py` | 四个 CC0 数据源适配器 + 三层过滤（AI 图 / 平面作品 / 作者匹配） |
| `fetch_art.py` | 抓图：按来源轮转、两层过滤、`--refresh` 清孤儿图 |
| `build_vault.py` | **生成** Obsidian 笔记 / README / LICENSE / .gitignore |
| `keyword_map.py` | 生成关键词图谱 |

### 图片分析

| 脚本 | 干什么 |
|---|---|
| `image_analysis.py` | 七维度客观测量：明度 / 对比 / 色彩 / 和谐 / 构图 / 质感 / 线条。纯 Pillow |
| `image_analysis_ext.py` | **可选**：人脸景别 / 霍夫直线 / 谱残差显著性。要 numpy + opencv，没装自动跳过 |
| `clip_embed.py` | **可选**：CLIP 图像/文本嵌入（ONNX，不需要 PyTorch）。首次跑 `download` 下模型 |
| `clip_match.py` | **可选**：用 CLIP 做图像→流派匹配（零样本 + 融合），三条路里最准的一条 |
| `artvault_vision.py` | **可选**：macOS Vision 语义检索（以图搜图 / 近重复 / 相近流派） |
| `ingest_inbox.py` | 处理 `pinterest/` 投递箱，扫描时带上上面这些维度 |
| `verify_vault.py` | **验收检查**：断链 / 重名 / AI 图 / frontmatter / 近重复 / 授权 / 孤儿图 |
| `github_setup.py` | 推送 + 设为 Template + 设 topics/description 一条龙（token 不进命令行参数） |
| `video_prompt.py` | 从流派数据生成两块中文视频提示词（Seedance 2.5 五段式 + MiniMax H3 自然语言） |
| `i2v_prompt.py` | **图生视频提示词**：把一张图的客观测量翻成主体 / 运动 / 运镜，填掉流派通用版里的占位符。反推卡默认走这条 |
| `scan_local.py` | **把你自己的图扫进库**：测量 + CLIP 建议 + 去重 → 待确认清单 → 归入 `15-我的图库/` |
| `reverse_prompt.py` | **组装反推卡**：把测量 + 流派匹配 + 七层 + 视频提示词拼成那张图的卡（三个入口共用） |

### 三条容易被忽略的约定

1. **改生成物，先改模板。**
   `10-流派/*.md`、`00-导航/*.md`、`README.md` 全部由 `build_vault.py` 生成，
   直接编辑会在下次重建时被覆盖（这份工具清单本身也在模板里）。
2. **`20-我的提示词/` 与 `pinterest/` 是本地目录，整个不发布。**
   脚本只往里写、不覆盖你的内容；`.gitignore` 把它们整体排除。
3. **改清单类文件，包在 `safefile.locked()` 里。**
   原子写只保证「不会留下半截文件」，防不住两个进程各自「读 → 改 → 写」、
   后写的把先写的整体覆盖 —— 文件是完整的，只是**少了一次改动**。
   实测 8 个进程各 +1，不加锁最后只剩 1。

   ```python
   import safefile as SF
   with SF.locked(MANIFEST):                 # 锁覆盖整个读-改-写
       d = SF.read_json(MANIFEST) or {}
       d["items"][k] = v
       SF.write_json(MANIFEST, d)
   ```

   或者一步到位：`SF.update_json(MANIFEST, fn)`。
   锁挂在 `<路径>.lock` 这个**旁挂文件**上，不挂在目标文件上 ——
   目标文件每次写入都会被 `os.replace` 换掉 inode，锁在旧 inode 上会失效。

   > [!tip] 加新流派时的另一个顺序陷阱
   > README 的统计数字按 `git ls-files`（下一次提交会带走的文件）算，
   > 所以要**先 `git add` 新笔记，再 `build_vault.py`**，否则 README 会少算，
   > 而这份陈旧的 README 会被一起提交出去。验收第 16 项会抓住它。

---

## 三条原则

1. **宁可少，不要错。**
   筛选时刻意不做「放宽补充」——某个流派只有 1 张图就 1 张。
   一个参考库最怕的不是图少，是图错。错的参考会污染你的直觉，而且你自己不会发现。

2. **光照比风格词更重要。**
   如果你只有一个层可以调，调光照。

3. **不要凭记忆编造流派术语。**
   以大模型对艺术流派的记忆为准，容易把相近的画派搞混。以库里的具体术语为准。

---

## 授权

全部图片来自公共领域 / CC0 开放数据源，已逐条核对，可自由使用与再分发。

**代码** MIT ｜ **笔记内容** CC BY 4.0 ｜ **图片** 公共领域 / CC0

详见 [LICENSE](LICENSE) 与 [LICENSE-CONTENT.md](LICENSE-CONTENT.md)。

---

<div align="center">

如果这个库对你有用，欢迎 Star ⭐ 或提交 PR 补充更多流派

</div>
"""


# ---------------------------------------------------------------- 本地图库（层 2）
# 用户自己扫进来的图。清单是 gitignore 的，别人 clone 后这里为空，
# 于是流派卡上「我的收藏」那一行也不会出现。
LOCAL_MANIFEST = os.path.join(DATA_DIR, "local_library.json")


def load_local():
    """读本地图库清单，返回 {slug: [条目]}。没有清单就返回空 dict。"""
    if not os.path.exists(LOCAL_MANIFEST):
        return {}
    try:
        man = json.load(open(LOCAL_MANIFEST, encoding="utf-8"))
    except Exception:
        return {}
    by = {}
    for rel, it in (man.get("items") or {}).items():
        by.setdefault(it.get("movement"), []).append(dict(it, rel=rel))
    for k in by:
        by[k].sort(key=lambda x: x.get("added_at") or "")
    return by


def local_image_note(mv, it, image_name):
    """生成**单张图**的反推卡：15-我的图库/<流派>/<图片名>.md

    这是用户上传一张图之后「打开就能看到反推结果」的那个页面。
    反推的实现在 reverse_prompt.py —— 扫描/投递箱归档/渲染三处共用一份。
    """
    import reverse_prompt as RP
    return RP.compose(it, mv, image_name,
                      back=("我的图库-%s" % mv["name_zh"]) if mv else None)


def local_note(mv, items):
    """流派级索引：列出该流派下每张图的反推卡。"""
    L = ["---",
         "type: 我的图库",
         "流派: %s" % mv["name_zh"],
         "张数: %d" % len(items),
         "标签:",
         "  - 我的图库",
         "---", "",
         "# 我的图库 · %s" % mv["name_zh"], "",
         "> [!info] 这是什么",
         "> 这是**你自己扫进来的**图，按流派归到了这里。每张图都有自己的反推卡",
         "> （点图名进去看七层提示词、客观测量、视频提示词）。",
         ">",
         "> 这些图是本地私有的（`15-我的图库/` 与 `99-附件/images-local/` 都已 gitignore），",
         "> 不会随仓库发布。",
         "",
         "← 回到 [[%s]] ｜ [[我的图库总览]]" % mv["name_zh"], "",
         "| # | 图 | 明度 | 饱和度 | 最接近的流派 |", "|---|---|---|---|---|"]
    for i, it in enumerate(items, 1):
        a = it.get("analysis") or {}
        lu = (a.get("luminance") or {}).get("key", "")
        sat = (a.get("color") or {}).get("saturation")
        sug = (it.get("suggest") or [{}])[0]
        card = os.path.splitext(os.path.basename(it["rel"]))[0]
        L.append("| %d | [[%s\|%s]] | %s | %s | %s |" % (
            i, card, (it.get("title") or card)[:28], lu,
            ("%.2f" % sat) if sat is not None else "—",
            sug.get("name") or "—"))
    return "\n".join(L) + "\n"


def local_index_note(by_slug):
    """15-我的图库/我的图库总览.md —— 把所有本地笔记和流派卡串起来。"""
    total = sum(len(v) for v in by_slug.values())
    L = ["---",
         "type: 我的图库",
         "张数: %d" % total,
         "标签:",
         "  - 我的图库",
         "---", "",
         "# 我的图库", "",
         "> [!info] 这是什么",
         "> 你自己扫进来的图，按流派归类。**和权威的 141 张流派卡挂在同一张图谱上** ——",
         "> 每篇都链回了对应的流派卡，所以从流派卡也能反查回来。",
         ">",
         "> 全部 gitignore，不会随仓库发布。", "",
         "共 **%d** 张，分布在 **%d** 个流派：" % (total, len(by_slug)), "",
         "| 流派 | 张数 | 我的图库 |", "|---|---|---|"]
    for slug in sorted(by_slug, key=lambda k: -len(by_slug[k])):
        if slug == "_未归类":
            continue
        mv = next((m for m in MOVEMENTS if m["slug"] == slug), None)
        if not mv:
            continue
        L.append("| [[%s]] | %d | [[我的图库-%s]] |" % (mv["name_zh"], len(by_slug[slug]), mv["name_zh"]))
    n_un = len(by_slug.get("_未归类", []))
    if n_un:
        L.append("| *（未归类）* | %d | 见下方清单 |" % n_un)
    L += ["", "← 回到 [[流派总览]]", "",
          "## 怎么往里加图", "",
          "```bash",
          "python3 _scripts/scan_local.py ~/你的图片文件夹",
          "python3 _scripts/scan_local.py --list                 # 看待确认清单",
          "python3 _scripts/scan_local.py --file 3 --to baroque  # 确认归类",
          "python3 build_vault.py                                # 重新生成本页",
          "```", "",
          "> [!warning] 为什么不是全自动",
          "> 实测 CLIP 的 Top-1 只有约四成；按把握程度分层也救不了 ——",
          "> 分差 ≥1.0 时准确率约 80% 但只覆盖 7% 的图，放宽到 41% 覆盖率时准确率掉到 54%。",
          "> 所以脚本只给建议，归类要你看一眼确认。"]
    if n_un:
        L += ["", "## 未归类（%d 张）" % n_un, "",
              "这些是归档时 CLIP 没给出建议的图，列出来让你一眼看到：", ""]
        for it in by_slug["_未归类"]:
            L.append("- `%s`" % os.path.basename(it["rel"]))
        L += ["", "归类：`python3 _scripts/scan_local.py --list` 找到编号后 "
                  "`--file <编号> --to <流派>`"]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- Pinterest 汇总（按来源的组织轴）
def pinterest_hub_note(local_map=None):
    """生成 20-我的提示词/Pinterest.md —— Pinterest 来源的图全汇总在这里。

    为什么要有这一页：库里有两套组织轴，各管一件事。

      **按流派**（15-我的图库/<流派>/）—— 拼提示词时用，找「这种风格还有什么参考」
      **按来源**（本页）——          授权与出处用，Pinterest 的图版权归原作者，
                                     没有统一授权，和 CC0 的流派图不是一回事

    两轴不冲突：一张图可以既在某个流派的图库里，也出现在本页。

    收录两种来源，它们走同一条管线（反推 → 按流派归类 → 落成卡），只是入口不同：
      · 脚本抓的板子 → 20-我的提示词/Pinterest-<板子>.md + 99-附件/images/pinterest/<板子>/
      · 手动下载后丢进 pinterest/ 投递箱的 → 归档后进 15-我的图库/，来源记为投递箱
    """
    import glob as _glob
    boards = []
    for p in sorted(_glob.glob(os.path.join(VAULT, "20-我的提示词", "Pinterest-*.md"))):
        name = os.path.basename(p)[:-3]
        board = name[len("Pinterest-"):]
        d = os.path.join(VAULT, "99-附件", "images", "pinterest", board)
        n = len([f for f in os.listdir(d)]) if os.path.isdir(d) else 0
        boards.append((board, n, name))

    # 手动放进来的：清单里来源为投递箱的
    mine = {}
    for slug, items in (local_map or {}).items():
        for it in items:
            if "投递箱" in str(it.get("source") or ""):
                mine.setdefault(slug, []).append(it)

    L = ["---",
         "type: MOC",
         "标签:",
         "  - pinterest",
         "---", "",
         "# Pinterest", "",
         "> [!warning] 版权",
         "> Pinterest 是二次聚合平台，图片版权归各自原作者，**没有统一授权**。",
         "> 这些图只供你个人做审美参考，**不要再分发**（库里的 CC0 图才可自由再分发）。", "",
         "> [!info] 这一页是什么",
         "> Pinterest 来源的图**全部汇总在这里** —— 脚本抓来的板子、",
         "> 以及你手动下载后丢进 `pinterest/` 投递箱的，两种来源走同一条管线",
         "> （反推 → 按流派归类 → 落成卡），只是入口不同。", "",
         "库里有两套组织轴，各管一件事：", "",
         "| 轴 | 在哪 | 干什么用 |",
         "|---|---|---|",
         "| **按来源** | 本页 | 授权与出处 —— Pinterest 的图和 CC0 的流派图不是一回事 |",
         "| **按流派** | `15-我的图库/<流派>/` | 拼提示词 —— 找「这种风格还有什么参考」 |", "",
         "一张图可以同时在两边。", "",
         "---", ""]

    L += ["## 一、抓取的板子（%d 个，%d 张）" % (len(boards), sum(n for _b, n, _x in boards)), ""]
    if boards:
        L += ["| 板子 | 张数 | 笔记 |", "|---|---|---|"]
        for board, n, name in boards:
            L.append("| %s | %d | [[%s]] |" % (board, n, name))
    else:
        L.append("还没有抓过。`python3 _scripts/pinterest_grab.py --discover` 看看有哪些板子。")
    L.append("")

    n_mine = sum(len(v) for v in mine.values())
    L += ["## 二、你放进来的（%d 张）" % n_mine, ""]
    if n_mine:
        L += ["| 流派 | 张数 | 反推卡 |", "|---|---|---|"]
        for slug in sorted(mine, key=lambda k: -len(mine[k])):
            mv = next((m for m in MOVEMENTS if m["slug"] == slug), None)
            cards = " ".join("[[%s]]" % os.path.splitext(os.path.basename(it["rel"]))[0]
                             for it in mine[slug][:6])
            L.append("| %s | %d | %s |" % (mv["name_zh"] if mv else slug, len(mine[slug]), cards))
    else:
        L.append("还没有。把 Pinterest 下载的图丢进 `pinterest/` 投递箱，然后：")
        L.append("")
        L.append("```bash")
        L.append("python3 _scripts/ingest_inbox.py --scan      # 反推自动跑，给建议")
        L.append("python3 _scripts/ingest_inbox.py --archive   # 按建议归入流派")
        L.append("python3 _scripts/build_vault.py              # 更新本页")
        L.append("```")
    L += ["", "---", "",
          "## 三、怎么往里加图", "",
          "**手动下载的（推荐）** —— 丢进投递箱，剩下自动：", "",
          "```bash",
          "cp ~/Downloads/xxx.jpg pinterest/            # 丢进去",
          "python3 _scripts/ingest_inbox.py --scan      # 测量 + CLIP 建议流派",
          "python3 _scripts/ingest_inbox.py --archive   # 按建议归档，反推卡自动生成",
          "python3 _scripts/build_vault.py              # 本页和流派卡一起更新",
          "```", "",
          "---", "",
          "## 四、这些图后来去哪了", "",
          "归档之后每张图都有一张**反推卡**（`15-我的图库/<流派>/<图名>.md`），",
          "里面有：客观测量七维、最接近的流派、**按那个流派组好的七层提示词**、",
          "配色、两块视频提示词。打开就能用。", "",
          "顺带一提：这些反推卡也链回对应的流派卡，所以从 [[流派总览]] 一路点过来也能到。", ""]
    return "\n".join(L) + "\n"


def _no_image_reason(mv):
    """这张卡为什么没有图 —— 三选一，因为处理办法完全不同。

    not_fetched  从来没跑过抓图（新补的卡）→ 跑一下就有
    copyright    代表作在版权期内             → 没有办法，只能存链接
    coverage     早已公版但开放源没收录        → 可以放宽到 CC-BY

    原来一律写「版权期内」，对毕德麦雅（1815–1848）这类卡是错的，
    而且会让人以为无解。
    """
    import os as _os
    if not _os.path.exists(_os.path.join(DATA_DIR, mv["slug"] + ".json")):
        return "not_fetched"
    m = re.findall(r"(1[5-9]\d\d|20\d\d)", mv.get("period") or "")
    if m and int(m[0]) < 1930:
        return "coverage"
    return "copyright"


def signature_note(works_map):
    """视觉签名页 —— 从实图反推的可测量区间。

    只在**算出过签名**时才生成（需要 Pillow + 跑过 visual_signature.py build）。
    没有就直接不生成这一页，并在 README 里也不提 —— 不写「待生成」的占位页。
    """
    try:
        import visual_signature as VS
    except Exception:
        return None
    sigs, meta = VS.load()
    if not sigs:
        return None
    L = ["---", "type: MOC", "---", "",
         "# 视觉签名", "",
         "每个流派的可测量区间，从**实图反推**出来的。", "",
         "## 它回答的是哪个问题", "",
         "不是「这是哪个流派」（那件事物理测量做不好，见下），而是：", "",
         "> **这张图真的像它声称的那个流派吗？**", "",
         "分类要求跨流派可比，物理测量做不到；而验收只要求同一流派内部自洽，",
         "这就宽松得多 —— 所以这一页的用法是**校验**，不是分类。", "",
         "```bash",
         "python3 visual_signature.py check <图片> --slug <流派>",
         "```", "",
         "## 有多少区分度（如实说）", "",
         "类间方差 / 类内方差，越大越能区分流派：", "",
         "| 维度 | 类间 | 类内 | 比值 |", "|---|---|---|---|"]
    for d in (meta.get("discriminative") or [])[:12]:
        L.append("| %s | %.3f | %.3f | %s |"
                 % (d["zh"], d["between"], d["within"], d["ratio"]))
    L += ["",
          "**比值只有 1–1.6，别高估它。** 这说明同一流派内部 6 张图的差异，",
          "和流派之间的差异差不多大 —— 和另一条实测结论一致：",
          "纯客观维度做「图像→流派」匹配只有 13.4%（随机基准 1.4%）。", ""]
    ns = meta.get("no_signal") or []
    if ns:
        L += ["这些维度**没有区分度**（类间/类内 < 0.25），不要拿它们判像不像：",
              "", "> " + "、".join(ns), ""]
    L += ["用法是看**偏离幅度**，不是看「有没有越界」：签名由 p10–p90 构造，",
          "样本内的图天然就有约 20% 的维度落在区间外。", "",
          "## 各流派的签名", "",
          "只列**最有信息**的几个维度（按上面的区分度排）。", "",
          "| 流派 | 样本 | 签名（p10–p90） |", "|---|---|---|"]
    bs = {m["slug"]: m for m in MOVEMENTS}
    for slug in sorted(sigs, key=lambda s: bs.get(s, {}).get("name_zh", s)):
        mv = bs.get(slug)
        if not mv:
            continue
        L.append("| [[%s]] | %d 张 | %s |"
                 % (mv["name_zh"], sigs[slug]["n_img"], VS.describe(slug)))
    L += ["", "---", "",
          "覆盖 %d 个流派 / %d 张实图（每流派至少 %d 张才算，样本太少区间宽到没有约束力）。"
          % (meta.get("n_movements", len(sigs)), meta.get("n_images", 0),
             meta.get("min_n", 4)), "",
          "重算：`python3 visual_signature.py build`", "",
          "← [[流派总览]] · [[关键词图谱]]", ""]
    return "\n".join(L)


def main():
    works_map = {m["slug"]: load_works(m["slug"]) for m in MOVEMENTS}
    local_map = load_local()

    for mv in MOVEMENTS:
        w("10-流派/%s.md" % mv["name_zh"],
          movement_note(mv, works_map[mv["slug"]], local_map))

    # 本地图库（层 2）：只在用户本机有清单时才生成
    local = local_map
    if local:
        by_slug = {m["slug"]: m for m in MOVEMENTS}
        n_cards = 0
        for slug, items in local.items():
            mv = by_slug.get(slug)
            for it in items:
                image_name = os.path.basename(it["rel"])
                if not mv:
                    continue
                # **每张图一张反推卡** —— 这是「上传一张图，打开就能看到反推结果」
                # 的那个页面。放在 <流派>/ 子目录下，和它的索引放一起。
                w("15-我的图库/%s/%s.md" % (mv["name_zh"], os.path.splitext(image_name)[0]),
                  local_image_note(mv, it, image_name))
                n_cards += 1
            if mv:
                w("15-我的图库/我的图库-%s.md" % mv["name_zh"], local_note(mv, items))
        w("15-我的图库/我的图库总览.md", local_index_note(local))
        print("  我的图库    %d 张反推卡" % n_cards)

    # Pinterest 汇总页：按来源的组织轴。**无论有没有本地图库都要生成** ——
    # 抓来的板子可能已经存在，而它正是这颗「星」应该有的中心。
    w("20-我的提示词/Pinterest.md", pinterest_hub_note(local_map))

    w("00-导航/流派总览.md", overview_note(works_map))
    w("00-导航/关键词图谱.md", keyword_graph_note(works_map))
    _sig = signature_note(works_map)
    if _sig:
        w("00-导航/视觉签名.md", _sig)
    for cat in CATEGORIES:
        w("00-导航/分类索引-%s.md" % cat, category_note(cat, works_map))
    w("00-导航/提示词拆解方法.md", METHOD)
    w("00-导航/视频提示词结构.md", VIDEO)
    # 注意：这里刻意用占位符而不是本机绝对路径。
    # 仓库是要发布的，写死 /Users/xxx 对任何人（包括作者换个位置 clone）都是错的。
    _guide = AI_GUIDE.replace(
        "{MCP_PATH}", "<仓库绝对路径>/_scripts/mcp_server.py")
    w("00-导航/AI 调用指南.md", _guide)
    body = []
    for cat in CATEGORIES:
        body.append("## %s" % cat)
        body.append("")
        for m in by_category()[cat]:
            body.append("### [[%s]] · %s" % (m["name_zh"], m["name_en"]))
            body.append("")
            for h, n in m["palette"]:
                body.append("- **%s** `%s`" % (n, h))
            body.append("")
            body.append("> `%s`" % ", ".join("%s %s" % (n, h) for h, n in m["palette"]))
            body.append("")
    w("00-导航/配色速查.md", PALETTE.format(palette_body="\n".join(body)))

    for name, tpl in TEMPLATES.items():
        w("90-模板/%s" % name, tpl)

    STATS = publish_stats()
    if tracked_files() is None:
        print("  ! 不是 git 仓库，README 统计退化为文件系统视图"
              "（可能把 gitignore 的文件也算进去）")

    def _fill(t):
        for k, v in STATS.items():
            t = t.replace("{%s}" % k, str(v))
        return t

    _rm = _fill(README.replace("{n_mv}", str(len(MOVEMENTS)))
                 .replace("{REPO_URL}", REPO_URL)
                 .replace("{skill_tree}", skill_tree()))
    w("README.md", _rm)
    w("LICENSE", LICENSE_TEXT)
    w("LICENSE-CONTENT.md", LICENSE_CONTENT)
    _en = _fill(README_EN.replace("{n_mv}", str(len(MOVEMENTS)))
                    .replace("{REPO_URL}", REPO_URL)
                    .replace("{skill_tree_en}", skill_tree_en())
                    .replace("{cat_table_en}", category_table_en()))
    w("README.en.md", _en)
    w(".gitignore", """# Obsidian 运行时文件
.DS_Store
.trash/
# 下面是每次用 Obsidian 都会变的**会话状态**，跟着提交只产生噪音。
# （app.json / appearance.json / core-plugins.json 是稳定设置，保留在仓库里）
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
# 主题是**个人界面选择**，不是参考内容：1.7MB 的 CSS 跟着公开仓库走
# 会让每个 clone 都多背一份，也把个人审美强加给别人。
# 另外社区主题的授权不一（实测 Royal Velvet 是 MIT，Wasp 没声明许可），
# 不声明许可的那些不宜随公开仓库再分发。
.obsidian/themes/
# graph.json 只有缩放比例等视图状态 —— 实测一个提交里唯一的变化就是 scale。
# 这一行曾在 849101d 加过，随后被无关的 ff52937 从模板里删掉了；
# 因为 .gitignore 是模板生成的，删一次就等于永久回退。别再删。
.obsidian/graph.json

# 脚本缓存与本地依赖
_scripts/__pycache__/
_scripts/vendor/

# 抓取过程的临时清单（每次扫描都会重写）
_scripts/_data/inbox_manifest.json

# 生成物：换台机器重建即可，不必入库
#   python3 artvault_vision.py build          （图像语义索引，几 MB）
# 向量缓存用 npz（比 json 小 6 倍、加载快 100 倍）；旧 json 也一并忽略，
# 免得升级后残留的文件被提交
_scripts/_data/vision_index.npz
_scripts/_data/vision_index.json
_scripts/_data/feature_cache.npz
_scripts/_data/feature_cache.json
_scripts/_data/clip_cache.npz
_scripts/_data/clip_cache.json
_scripts/_data/clip_text_cache.json

# CLIP 量化模型（约 150MB，跑 clip_embed.py download 自动获取）
_scripts/vendor/clip/

# ---------------------------------------------------------------- 你的私人工作区
# 20-我的提示词/ 是「你自己的地盘」，**整个目录都不发布**。
# 早先只放行了一个 README，但那自相矛盾：一份说明「这个目录不进版本库」
# 的 README，本身就在版本库里。现在整个目录忽略，clone 下来不会有它。
20-我的提示词/

# ---------------------------------------------------------------- 层 2：我自己的图库
# 扫描你自己文件夹进来的私人收藏。**全部本地私有**，不随仓库发布：
#   python3 _scripts/scan_local.py <目录>   →  --list → --file <编号> --to <流派>
# 清单和图片是私有的，但 15-我的图库/ 的笔记是生成的（build_vault 无条件重写），
# 一并忽略，避免把你的收藏清单提交上去。
_scripts/_data/local_library.json
_scripts/_data/local_pending.json
15-我的图库/
99-附件/images-local/

# Vision 特征提取器的编译产物（架构相关，首次使用时自动编译）
_scripts/vision/vision_feat

# Pinterest 抓来的图版权归原作者、无统一授权，**不要提交也不要公开**
# （10-流派/ 里的 CC0 图不受影响，那是可以随便分发的）
99-附件/images/pinterest/

# 投递箱（本地工作目录，整个不发布）：
# 里面是抓来的图和投递箱笔记，版权归原作者；那个 README 讲的是抓取流程，
# 对读者没有意义 —— 一并不发布。
pinterest/

# 本地推送助手（含个人仓库名，不必发布）
push-to-github.sh
""")

    # 清理本次没生成的旧文件（见 sweep_generated 的说明）
    swept = sweep_generated()
    if swept:
        print("  清理了 %d 个已不再生成的旧文件：" % len(swept))
        for x in swept[:6]:
            print("    - %s" % x)
        if len(swept) > 6:
            print("    … 另有 %d 个" % (len(swept) - 6))

    # 记下这次生成了哪些文件，供下次 sweep 判断（见 GENERATED_MANIFEST 的说明）
    try:
        json.dump({"files": sorted(_WRITTEN)},
                  open(GENERATED_MANIFEST, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=0)
    except Exception as e:
        print("  ! 生成清单写入失败：%s（下次清理会退回到读笔记标记）" % e)

    n_img = sum(len(v) for v in works_map.values())
    print("生成完成：")
    print("  流派卡      %d 张" % len(MOVEMENTS))
    _nav = [r for r in _WRITTEN if r.startswith("00-导航/")]
    print("  导航与方法  %d 篇" % len(_nav))
    print("  模板        %d 个" % len(TEMPLATES))
    print("  入库作品图  %d 件" % n_img)
    empty = [m["name_zh"] for m in MOVEMENTS if not works_map[m["slug"]]]
    if empty:
        print("  无 CC0 图的流派（纯提示词卡）：%s" % "、".join(empty))


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 build_vault.py",
          ["重新生成全部笔记（流派卡 / 导航 / 模板 / README / .gitignore）。",
           "没有任何选项；不带参数直接跑。重复运行是安全的。"])
    main()
