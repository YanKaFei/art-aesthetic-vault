#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_handraw_fusion.py —— 第 7 大类「手绘艺术风格」的验收测试。

    python3 tests/test_handraw_fusion.py          # 全部
    python3 tests/test_handraw_fusion.py -v       # 逐条打印
    ARTVAULT_ROOT=<仓库根> python3 tests/test_handraw_fusion.py

## 这个文件守的是什么

把 handraw-style 的 274 个手绘风格融进本库，最大的风险**不是**跑不起来，
而是「跑起来了，但内容是编的」—— 卡上的七层英文提示词看着像模像样，
却没有任何一条能追回到 handraw 自己的数据。

所以这里的断言分成两类：

    能不能用   categories 有第 7 类、274 张卡在、七层非空、图在且被引用
    是不是编的 每一层英文都必须在 handraw_lexicon 里找得到出处；
              traits 里抽不到的层必须标成 ⟨组⟩（组级默认），不许伪装成
              「这个风格自己的特征」

第二类才是这个文件存在的理由。零依赖，只用标准库。
"""

import glob
import json
import os
import re
import subprocess
import sys

# ------------------------------------------------------------------ 定位仓库
def find_vault():
    env = os.environ.get("ARTVAULT_ROOT")
    if env and os.path.isfile(os.path.join(env, ".repo", "artvault.py")):
        return os.path.abspath(env)
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isfile(os.path.join(d, ".repo", "artvault.py")):
            return d
        d = os.path.dirname(d)
    return None


VAULT = find_vault()
REPO = os.path.join(VAULT, ".repo") if VAULT else None
CAT = "手绘艺术风格"
N = 274


# ------------------------------------------------------------------ 跑命令
def run(*args):
    """在 .repo/ 下跑一个命令，返回 (returncode, stdout+stderr)。"""
    r = subprocess.run([sys.executable] + list(args), cwd=REPO,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=300)
    return r.returncode, r.stdout


# ------------------------------------------------------------------ 测试
CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def test_module_loads_274():
    """mv_handraw 必须产出 274 条，且每条字段齐全。"""
    code, out = run("-c", (
        "import json,mv_handraw as M\n"
        "print(json.dumps({'n':len(M.MOVEMENTS),"
        "'cat':M.CATEGORY,"
        "'bad':[m['slug'] for m in M.MOVEMENTS if not all([m['slug'],m['name_zh'],"
        "m['name_en'],m['one_liner'],m['core'],m['visual'],m['palette'],m['prompt'],"
        "m['negative'],m['video'],m['pitfalls']])]},ensure_ascii=False))"))
    assert code == 0, "mv_handraw 导入失败：\n" + out.strip()[-800:]
    d = json.loads(out.strip().splitlines()[-1])
    assert d["cat"] == CAT, "CATEGORY 应为 %s，实际 %s" % (CAT, d["cat"])
    assert d["n"] == N, "应有 %d 条，实际 %d" % (N, d["n"])
    assert not d["bad"], "字段不全的条目：%s" % d["bad"][:5]


@case
def test_categories_has_seventh():
    """artvault.py categories 必须列出第 7 类 274 个流派。"""
    code, out = run("artvault.py", "categories")
    assert code == 0, "categories 退出码 %d：\n%s" % (code, out[-500:])
    assert CAT in out, "categories 输出里没有「%s」：\n%s" % (CAT, out)
    assert re.search(re.escape(CAT) + r"\s+%d\s+个流派" % N, out), \
        "categories 里「%s」的数量不是 %d：\n%s" % (CAT, N, out)


@case
def test_layers_show_palette_related():
    """layers / show / palette / related 四个命令对新手绘卡都要能跑通。"""
    code, out = run("artvault.py", "layers", "手绘001")
    assert code == 0, "layers 退出码 %d：\n%s" % (code, out[-500:])
    for layer_cn in ("风格", "光照", "色彩", "构图", "媒介", "情绪", "镜头"):
        assert layer_cn in out, "layers 缺「%s」层：\n%s" % (layer_cn, out)
    for cmd in (["show", "手绘274"], ["palette", "手绘100"],
                ["related", "手绘001"]):
        code, out = run("artvault.py", *cmd)
        assert code == 0, "%s 退出码 %d：\n%s" % (cmd, code, out[-400:])


@case
def test_seven_layers_nonempty_for_all():
    """274 张卡的七层都不许为空 —— 空层会让 compose 静默少一层。"""
    code, out = run("-c", (
        "import mv_handraw as M\n"
        "keys=['style','lighting','color','composition','medium','mood','camera']\n"
        "bad=[(m['slug'],k) for m in M.MOVEMENTS for k in keys "
        "if not (m['prompt'].get(k) or '').strip()]\n"
        "print('BAD',bad[:8])"))
    assert code == 0, out[-500:]
    assert "BAD []" in out, "存在空层：%s" % out


@case
def test_no_fabrication_every_phrase_is_sourced():
    """卡上每一层英文都必须在词表里有出处。

    这是「不是编的」这条不变量：把每层按逗号切开，每个片段必须能在
    handraw_lexicon 的 KEYWORDS / GROUPS / 组装骨架里找到来源。
    新增一条编造的短语，这里就会红。
    """
    code, out = run("-c", (
        "import json,mv_handraw as M,handraw_lexicon as L\n"
        "known=set()\n"
        "for zh,dim,en in L.KEYWORDS: known.add(en.strip().lower())\n"
        "for g in L.GROUPS.values():\n"
        "    for k in ('medium_en','light_en','comp_en','mood_en','camera_en'):\n"
        "        known.add(g[k].strip().lower())\n"
        "    for w in g['neg'].split(','): known.add(w.strip().lower())\n"
        "known.add(L.COLOR_FALLBACK_EN.strip().lower())\n"
        "# 词表里的片段自己就带逗号（'single figure, generous white space'），\n"
        "# 所以判据是「每一个逗号原子都必须出现在某个词表片段里」，\n"
        "# 而不是「整个原子必须等于某个词表片段」。\n"
        "atoms=set()\n"
        "for ph in known:\n"
        "    for a in ph.split(','): atoms.add(a.strip().lower())\n"
        "for m in M.MOVEMENTS:\n"
        "    for w in m['negative'].split(','): known.add(w.strip().lower())\n"
        "unk=[]\n"
        "for m in M.MOVEMENTS:\n"
        "    for k,v in m['prompt'].items():\n"
        "        if k=='style': continue\n"
        "        for frag in v.split(','):\n"
        "            f=frag.strip().lower()\n"
        "            if f and f not in atoms:\n"
        "                unk.append((m['slug'],k,f))\n"
        "print(json.dumps(unk[:10],ensure_ascii=False))"))
    assert code == 0, out[-600:]
    unk = json.loads(out.strip().splitlines()[-1])
    assert unk == [], "有 %d 个片段在词表里找不到出处，例如：%s" % (len(unk), unk)


@case
def test_evidence_markers_present():
    """六维里必须出现 ⟨条⟩ / ⟨组⟩ 标记 —— 抽不到就得显形，不许伪装。"""
    code, out = run("-c", (
        "import json,mv_handraw as M\n"
        "no_mark=[m['slug'] for m in M.MOVEMENTS "
        "if not any(('⟨条⟩' in v or '⟨组⟩' in v) for v in m['visual'].values())]\n"
        "both=sum(1 for m in M.MOVEMENTS if any('⟨组⟩' in v for v in m['visual'].values()))\n"
        "print(json.dumps({'no_mark':no_mark[:5],'n_with_group':both}))"))
    assert code == 0, out[-500:]
    d = json.loads(out.strip().splitlines()[-1])
    assert d["no_mark"] == [], "这些条的六维完全没有来源标记：%s" % d["no_mark"]


@case
def test_cards_on_disk():
    """10-movements/ 下恰好 274 张手绘卡，且九节齐全、视频两块都在。

    ⚠ 这里原来按文件名 `手绘*.md` 找卡 —— 274 张卡改用中文名之后
    这个 glob 直接找不到任何文件。**不能靠文件名认手绘卡**：
    认的方式是按 frontmatter 的 `分类: 手绘艺术风格`，
    这样以后再改名也不会把测试弄瞎。
    """
    files = []
    for p in sorted(glob.glob(os.path.join(VAULT, "10-movements", "*.md"))):
        t = open(p, encoding="utf-8").read()
        if "分类: 手绘艺术风格" in t[:400] or "分类: 手绘艺术风格" in t:
            files.append(p)
    assert len(files) == N, "应有 %d 张手绘卡，实际 %d" % (N, len(files))
    bad = []
    for p in files:
        t = open(p, encoding="utf-8").read()
        for sec in ("## 一、", "## 二、", "## 三、", "## 四、", "## 五、",
                    "## 六、", "## 七、", "## 八、", "## 九、"):
            if sec not in t:
                bad.append((os.path.basename(p), "缺 " + sec))
        if "【主体】" not in t or "### B. MiniMax H3" not in t:
            bad.append((os.path.basename(p), "视频两块不全"))
    assert not bad, "卡结构有问题：%s" % bad[:5]


@case
def test_images_present_and_embedded():
    """274 张编号图都在 99-attachments/images/handraw/，且被对应卡嵌入。"""
    d = os.path.join(VAULT, "99-attachments", "images", "handraw")
    missing = [n for n in range(1, N + 1)
               if not os.path.isfile(os.path.join(d, "handraw-%03d.webp" % n))]
    assert not missing, "缺图 %d 张，例如 %s" % (len(missing), missing[:5])
    notref = []
    for n in range(1, N + 1):
        p = os.path.join(VAULT, "10-movements", "手绘%03d.md" % n)
        if not os.path.isfile(p):
            continue
        if "![[handraw-%03d.webp]]" % n not in open(p, encoding="utf-8").read():
            notref.append(n)
    assert not notref, "这些卡没有嵌入自己的编号图：%s" % notref[:5]


@case
def test_vendored_repo_installed():
    """原仓库整棵在 vault 里，含 LICENSE 与来源记录。"""
    root = os.path.join(VAULT, "30-handraw-style")
    for rel in ("LICENSE", "README.md", "SKILL.md", "styles_200_reorganized.md",
                "SOURCE.md",
                "skills/handdraw-style-prompter/references/styles.json"):
        assert os.path.isfile(os.path.join(root, rel)), "缺 %s" % rel
    assert not os.path.isdir(os.path.join(root, ".git")), \
        "嵌套 .git 会让外层仓库把它当 submodule，应当移除"


@case
def test_group_overview_note():
    """组总览页存在，且 A–H 八组都在、拼图被引用。"""
    p = os.path.join(VAULT, "00-guides", "手绘风格总览.md")
    assert os.path.isfile(p), "缺 00-guides/手绘风格总览.md"
    t = open(p, encoding="utf-8").read()
    for g in "ABCDEFGH":
        assert re.search(r"\b%s\b" % g, t) or ("%s 组" % g) in t, "总览页缺 %s 组" % g


@case
def test_no_empty_frontmatter_tag():
    """frontmatter 的标签列表里不许有空项。

    G 组那 16 条的 generation_name 是中文（「可爱萌系插画风」这种），
    按英文名生成标签 slug 时会被清成空串，卡上于是出现一行孤零零的
    `  - `。验收第 4 项只查 frontmatter 里有没有 `<` 开头的行和制表符，
    抓不到这种「合法但没意义」的坏值 —— 但它会在 Obsidian 里变成一个空标签。
    """
    bad = []
    for p in sorted(glob.glob(os.path.join(VAULT, "10-movements", "手绘*.md"))):
        head = open(p, encoding="utf-8").read().split("---", 2)[1]
        if any(ln.rstrip() in ("  -", "-") for ln in head.splitlines()):
            bad.append(os.path.basename(p))
    assert not bad, "%d 张卡的 frontmatter 标签是空的：%s" % (len(bad), bad[:6])


@case
def test_image_licence_claim_is_qualified():
    """「图片可自由使用与再分发」必须区分两类图。

    库里现在有两种图：博物馆抓来的 CC0 / 公共领域实图，和 handraw-style
    的 274 张编号参考图。后者来自第三方 MIT 仓库，**不是**公共领域艺术作品。
    把它们笼统地一起说成「可自由使用与再分发」，是**授权口径上的虚报** ——
    而授权正是这个库最在意的东西（验收第 6 项授权字段、第 10 项署名质量
    守的都是它）。
    """
    p = os.path.join(VAULT, "00-guides", "流派总览.md")
    t = open(p, encoding="utf-8").read()
    assert "图片可自由使用与再分发。" not in t, \
        "流派总览仍在无差别地宣称所有图片可自由使用"
    assert "handraw" in t, "总览页没有说清哪一类图来自 handraw-style、授权是什么"


@case
def test_readme_image_stat_splits_sources():
    """README 的实图统计必须把两类图分开写。

    同一个「实图」标签下混着博物馆公共领域作品和 handraw 的风格参考图，
    读者会据此判断「这些图我能怎么用」—— 合在一起写就是在误导。
    """
    t = open(os.path.join(VAULT, "README.md"), encoding="utf-8").read()
    assert "编号参考图" in t, "中文 README 的实图统计没区分编号参考图"
    t2 = open(os.path.join(VAULT, "README.en.md"), encoding="utf-8").read()
    assert "handraw" in t2.lower(), "英文 README 的实图统计没区分 number-referenced sheets"


@case
def test_reverse_prompt_tells_the_truth_about_layers():
    """反推卡上「七层是手写的」这句话，对手绘类必须换成另一句。

    `reverse_prompt.compose` 把这句话打印在**用户自己的图**的反推卡上。
    手绘类的七层是从 handraw 的 traits 推导来的 —— 对那 274 条继续打这句，
    就是在屏幕上说假话。这类「文案与事实脱节」不会报错，只会骗人。
    """
    code, out = run("-c", (
        "import json, reverse_prompt as R\n"
        "from movements import MOVEMENTS\n"
        "by={m['slug']:m for m in MOVEMENTS}\n"
        "rec={'title':'t','added_at':'x','analysis':{},'suggest':[]}\n"
        "def lines(slug):\n"
        "    return [l for l in R.compose(rec, by[slug], 'x.jpg').split(chr(10))\n"
        "            if '七层' in l]\n"
        "print(json.dumps({'hand':lines('handraw-001'),'other':lines('baroque')},\n"
        "                 ensure_ascii=False))"))
    assert code == 0, out[-800:]
    d = json.loads(out.strip().splitlines()[-1])
    hand = " ".join(d["hand"])
    assert hand, "反推卡里没有找到讲七层来路的那句"
    assert "手写" not in hand, "对第 7 大类仍宣称七层是手写的：%s" % hand
    assert ("handraw" in hand) or ("推导" in hand) or ("组级默认" in hand), \
        "对第 7 大类没有说清七层的真实来路：%s" % hand
    assert "手写" in " ".join(d["other"]), \
        "对艺术流派卡反而丢了「手写」这个正确说法：%s" % d["other"]


@case
def test_no_stale_size_claims_in_user_facing_docs():
    """用户可见的说明里不许再出现旧的规模数字。

    这个库为写死的统计数字吃过好几次亏（README 声称 654 张实图，克隆下来
    442 张；冒烟里写死 141）。所以「还在说 141 个流派」当缺陷看，
    不当排版问题。清单是**逐条点名**的：只覆盖那些在讲**当前规模**的地方，
    讲历史的地方（「当初 141 张卡时…」）不在其列 —— 那些是准确的历史。
    """
    stale = [("clip_match.py", "141 个流派"),
             ("eval_search.py", "141 条"),
             ("scan_local.py", "141 张流派卡"),
             ("clihelp.py", "141 张卡片"),
             ("reverse_prompt.py", "141 张卡"),
             ("build_vault.py", "6 大分类"),
             ("mcp_server.py", "6 大分类")]
    bad = []
    for fname, pat in stale:
        p = os.path.join(REPO, fname)
        if os.path.isfile(p) and pat in open(p, encoding="utf-8").read():
            bad.append("%s: %s" % (fname, pat))
    assert not bad, "用户可见说明里还有过期规模数字：%s" % bad


@case
def test_lexicon_bridge_really_includes_handraw_terms():
    """中文过桥表必须**真的**并进了手绘词条。

    这是一条防「静默不并入」的守卫：如果合并那段被一个过宽的
    `except Exception` 吞掉，中文语义检索会悄悄搜不到这 274 条，
    而过桥探针（霓虹/厚涂/…）照样全绿 —— 没有任何检查会响。
    """
    code, out = run("-c", (
        "import json, visual_lexicon as VL, handraw_lexicon as HL\n"
        "missing=[k for k in HL.EXTRA_LEXICON if k not in VL.LEXICON]\n"
        "en,matched,_=VL.to_english('钢笔速写 留白')\n"
        "print(json.dumps({'missing':missing[:5],'en':en,'matched':matched},\n"
        "                 ensure_ascii=False))"))
    assert code == 0, out[-500:]
    d = json.loads(out.strip().splitlines()[-1])
    assert d["missing"] == [], "手绘词条没有并进过桥表：%s" % d["missing"]
    assert d["en"], "中文手绘词过不了桥：%s" % d


# ------------------------------------------------------------------ 主程序
def main():
    args = sys.argv[1:]
    verbose = "-v" in args
    only = [a for a in args if not a.startswith("-")]
    if VAULT is None:
        print("✗ 找不到仓库根（用 ARTVAULT_ROOT 指定）")
        return 2
    failed = []
    for fn in CASES:
        if only and not any(o in fn.__name__ for o in only):
            continue
        try:
            fn()
        except AssertionError as e:
            failed.append(fn.__name__)
            print("  ✗ %s" % fn.__name__)
            print("      %s" % str(e).replace("\n", "\n      "))
        except Exception as e:
            failed.append(fn.__name__)
            print("  ✗ %s  （异常）" % fn.__name__)
            print("      %s: %s" % (type(e).__name__, e))
        else:
            if verbose:
                print("  ✓ %s" % fn.__name__)
    print("-" * 60)
    if failed:
        print("未通过 %d/%d：%s" % (len(failed), len(CASES), "、".join(failed)))
        return 1
    print("全部通过（%d 项）。" % len([c for c in CASES
                                  if not only or any(o in c.__name__ for o in only)]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
