#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""readme_i18n_test.py —— 四语 README 与它的配图。纯标准库 + 可选 Pillow。

    python3 tests/readme_i18n_test.py
    python3 tests/readme_i18n_test.py -v

## 这一层守什么

仓库原本只有中英两份 README。加到四份（中/英/日/法）之后，多出来的失败模式
不是「翻译得不好」，而是**四种说法互相漂移**：

1. **四份都得在，而且互相链得上。** 少一份、或某一份的语种切换条里漏掉一个，
   读者就走进死胡同 —— 而这种错在单语读者眼里永远看不见（他只看自己那份）。
2. **数字在四份里必须一样真。** README 里的规模数字是这个库最容易被虚报的地方
   （历史：写 654 张、实录 442 张，虚报 48%）。多三份 README 就是多三处会烂的
   数字，所以四份的数字都要能被 `verify_vault.check_readme_numbers()` 核对。
3. **配图必须真的发布出去。** 图放在 `99-attachments/readme/`，四份 README 共用。
   引用一张只在作者机上存在的图，读者看到的是破图 —— 同「clone 完整性」那一项
   的道理，只是这次引用方不是笔记而是 README。
4. **上游作者必须被署名。** 第 7 大类来自 handraw-style，镜头卡来自
   video-shotcraft，剧照索引来自 film-grab。这几处署名**四份 README 都要有** ——
   署名只写在中文版里，等于对读英文版的读者隐瞒了来源。
5. **配图是生成物，就得可复现。** 清单里记下每张图的 sha256：CI 上没有 Pillow，
   就只核对「磁盘上的图 = 清单里的图」；本地有 Pillow 时再往前走一步，
   真的重画一遍比哈希。
"""

import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VAULT = os.path.dirname(REPO)
sys.path.insert(0, REPO)

LANGS = ("README.md", "README.en.md", "README.ja.md", "README.fr.md")
ASSET_DIR = os.path.join(VAULT, "99-attachments", "readme")
MANIFEST = os.path.join(ASSET_DIR, "MANIFEST.txt")

# 四份 README 都必须点名的上游来源。写成 (显示名, 必须出现的字符串)。
UPSTREAM = (
    ("handraw-style", "yang0/handraw-style"),
    ("video-shotcraft", "Vincentwei1021/video-shotcraft"),
    ("film-grab", "film-grab.com"),
    ("Tate 术语表", "tate.org.uk"),
)

IMG_REF = re.compile(r"99-attachments/readme/([A-Za-z0-9._-]+\.(?:jpg|jpeg|png|webp))")

# 署名章节的标题（四语各一个）。署名要求「写清借了什么、什么许可」，
# 所以核对的范围应当是**这一节**，而不是全篇 —— 正文里第一次提到上游名字的
# 地方未必挨着许可说明，按全篇找会变成一条时灵时不灵的检查。
CONTRIB_HEADING = {
    "README.md": "## 贡献者与来源",
    "README.en.md": "## Contributors & sources",
    "README.ja.md": "## クレジットと出典",
    "README.fr.md": "## Crédits et sources",
}

# 四份 README 的统计表行。**这是唯一的声明处**：测试与 verify_vault 都从这里取，
# 免得「测试以为它长这样、README 其实长那样」——那正是绿着却什么都没守的形态。
STATS_ROW = {
    "README.md": ("**流派卡**", "张", "**流派卡** | **{n} 张**"),
    "README.en.md": ("**Movement cards**", "", "**Movement cards** | **{n}**"),
    "README.ja.md": ("**流派カード**", "枚", "**流派カード** | **{n} 枚**"),
    "README.fr.md": ("**Fiches de mouvement**", "fiches",
                     "**Fiches de mouvement** | **{n} fiches**"),
}


def read(name):
    p = os.path.join(VAULT, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return f.read()


def git_tracked(paths):
    """这些路径里，哪些被 git 跟踪了。

    `--error-unmatch` 会让未跟踪的路径返回非 0，但我们这里是批量问，
    用 `ls-files` 的输出做交集更省事。
    """
    if not paths:
        return set()
    r = subprocess.run(["git", "-C", VAULT, "ls-files", "-z", "--"] + list(paths),
                       capture_output=True, text=True)
    if r.returncode != 0:
        return set()
    return {p for p in r.stdout.split("\0") if p}


class LanguageSetTests(unittest.TestCase):
    """四份 README 都在，而且互相链得上。"""

    def test_all_four_languages_exist(self):
        missing = [n for n in LANGS if not read(n)]
        self.assertEqual([], missing, "缺这些语种的 README：%s" % missing)

    def test_each_readme_is_a_real_document(self):
        """不是占位文件。四份都该有正文、章节结构、代码块。"""
        for n in LANGS:
            t = read(n)
            if t is None:
                self.fail("%s 不存在" % n)
            self.assertGreater(len(t), 4000,
                               "%s 太短，像是占位文件（%d 字符）" % (n, len(t)))
            self.assertGreaterEqual(t.count("\n## "), 6,
                                    "%s 的章节太少，四份应当结构一致" % n)
            self.assertIn("```", t, "%s 里一个代码块都没有" % n)

    def test_every_readme_links_to_the_other_three(self):
        for n in LANGS:
            t = read(n) or ""
            for other in LANGS:
                if other == n:
                    continue
                self.assertIn(other, t, "%s 里没有指向 %s 的链接" % (n, other))


class ReadmeNumbersTests(unittest.TestCase):
    """数字在四份里都要能被核对。"""

    def test_verify_vault_covers_every_language(self):
        with open(os.path.join(REPO, "verify_vault.py"), encoding="utf-8") as f:
            src = f.read()
        block = src.split("CLAIMS = [", 1)[1].split("\n    ]", 1)[0]
        for n in LANGS:
            self.assertIn('"%s"' % n, block,
                          "verify_vault 的数字清单里没有 %s —— 这份 README 的数字无人守"
                          % n)

    def test_numbers_are_consistent_right_now(self):
        import verify_vault as VV
        got = VV.check_readme_numbers()
        self.assertEqual([], got or [], "README 数字与发布视图不一致：%r" % (got,))

    def test_number_check_bites_in_every_language(self):
        """反向对照：四份里各改坏一个数字，第 16 项都必须报出来。

        中英两份已有同类测试（smoke_test）。新加的两份如果没有这一条，
        就可能只是「正则写了个不匹配的」，永远绿着却什么都没守 ——
        这个仓库在 README 数字上正是这么栽过一次的。
        """
        import verify_vault as VV
        import build_vault as BV
        st = BV.publish_stats()
        for name in LANGS:
            orig = read(name)
            if orig is None:
                self.fail("%s 不存在" % name)
            _label, _unit, tpl = STATS_ROW[name]
            good = tpl.format(n=st["n_mv"])
            bad = tpl.format(n=st["n_mv"] + 7)
            self.assertIn(good, orig,
                          "测试前提失效：%s 里找不到 %r" % (name, good))
            p = os.path.join(VAULT, name)
            try:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(orig.replace(good, bad))
                got = VV.check_readme_numbers() or []
                self.assertTrue(any(name in f for f, _m in got),
                                "把 %s 的数字改坏之后居然没报：%r" % (name, got))
            finally:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(orig)
        self.assertEqual([], VV.check_readme_numbers() or [],
                         "还原之后仍在报错，说明测试自己写坏了文件")


class ContributorTests(unittest.TestCase):
    """上游作者在四份里都要署名。"""

    def test_upstream_is_credited_in_every_language(self):
        for n in LANGS:
            t = read(n) or ""
            for label, needle in UPSTREAM:
                self.assertIn(needle, t,
                              "%s 里没有署名 %s（%s）" % (n, label, needle))

    def test_there_is_a_contributors_section(self):
        for n in LANGS:
            self.assertIn(CONTRIB_HEADING[n], read(n) or "",
                          "%s 里没有独立的署名章节（%s）" % (n, CONTRIB_HEADING[n]))

    def test_each_credit_says_what_was_borrowed_and_under_what_license(self):
        """署名不能只是一行链接 —— 要写清借了什么、什么许可。

        只看**署名章节这一段**：正文里第一次提到上游名字的地方未必挨着许可说明，
        按全篇找会变成一条时灵时不灵的检查。
        """
        LIC = ("mit", "apache", "cc0", "许可", "license", "licence",
               "ライセンス", "非商用", "non-commercial", "版权", "public domain",
               "domaine public", "パブリックドメイン")
        for n in LANGS:
            t = read(n) or ""
            idx = t.find(CONTRIB_HEADING[n])
            self.assertGreater(idx, 0, "%s 缺署名章节" % n)
            section = t[idx:].lower()
            for label, needle in UPSTREAM:
                # section 已经小写，needle 也要小写再比 —— 否则大小写一变就假报
                self.assertIn(needle.lower(), section,
                              "%s 的署名章节里没有 %s（%s）" % (n, label, needle))
            self.assertTrue(any(k in section for k in LIC),
                            "%s 的署名章节没写任何许可信息" % n)


class ReadmeAssetTests(unittest.TestCase):
    """配图：发布得出去，而且可复现。"""

    def test_readmes_reference_assets(self):
        for n in LANGS:
            self.assertTrue(IMG_REF.findall(read(n) or ""),
                            "%s 里没引用任何配图" % n)

    def test_every_referenced_asset_exists_and_is_tracked(self):
        refs = set()
        for n in LANGS:
            refs |= set(IMG_REF.findall(read(n) or ""))
        self.assertTrue(refs, "四份 README 一张配图都没引用")
        missing = sorted(r for r in refs
                         if not os.path.exists(os.path.join(ASSET_DIR, r)))
        self.assertEqual([], missing, "README 引用了不存在的图：%s" % missing)
        rel = ["99-attachments/readme/" + r for r in sorted(refs)]
        untracked = sorted(set(rel) - git_tracked(rel))
        self.assertEqual([], untracked,
                         "这些配图没被 git 跟踪，clone 之后是破图：%s" % untracked)

    def test_manifest_matches_files_on_disk(self):
        self.assertTrue(os.path.exists(MANIFEST),
                        "缺 MANIFEST.txt（跑 python3 readme_assets.py）")
        with open(MANIFEST, encoding="utf-8") as f:
            lines = [l.rstrip("\n") for l in f if l.strip() and not l.startswith("#")]
        self.assertTrue(lines, "MANIFEST.txt 是空的")
        for line in lines:
            parts = line.split()
            sha, size, name = parts[0], int(parts[1]), parts[2]
            p = os.path.join(ASSET_DIR, name)
            self.assertTrue(os.path.exists(p), "清单里的 %s 不在磁盘上" % name)
            with open(p, "rb") as f:
                data = f.read()
            self.assertEqual(size, len(data), "%s 大小与清单不符" % name)
            self.assertEqual(sha, hashlib.sha256(data).hexdigest(),
                             "%s 内容与清单不符（手工改过图？跑 readme_assets.py 重建）"
                             % name)

    def test_manifest_sources_exist_and_are_tracked(self):
        """清单里记的源图必须真的在库里、且被跟踪 —— 否则这张图下次重建就没了。"""
        with open(MANIFEST, encoding="utf-8") as f:
            text = f.read()
        srcs = set(re.findall(r"99-attachments/[A-Za-z0-9._/%-]+\.(?:jpg|jpeg|png|webp)",
                              text))
        self.assertTrue(srcs, "清单里一张源图都没记")
        missing = sorted(s for s in srcs if not os.path.exists(os.path.join(VAULT, s)))
        self.assertEqual([], missing, "清单记的源图不在库里：%s" % missing)
        self.assertEqual([], sorted(srcs - git_tracked(sorted(srcs))),
                         "清单记的源图没被 git 跟踪（别人 clone 后重建不出来）")

    def test_generator_refuses_to_run_without_its_fonts(self):
        """缺字体时必须**报错**，不能悄悄退回默认位图字体。

        图的字节取决于字体。没有字体时 Pillow 的 load_default() 会照常出图，
        只是画出来的是另一套东西 —— 于是「同一份源码在任何机器上重建出同一张图」
        这条承诺就静默失效了，而且校验只跑在有 Pillow 的机器上，恰好是字体齐全
        的那一台。所以要求它在字体缺失时直接失败。
        """
        try:
            import PIL  # noqa: F401
            import readme_assets as RA
        except Exception as e:
            self.skipTest("本机没有 Pillow：%s" % str(e)[:60])
        keep = RA._FONTS
        try:
            RA._FONTS = ()
            RA._CACHE.clear()
            with self.assertRaises(RuntimeError):
                RA.font("sans", 20)
        finally:
            RA._FONTS = keep
            RA._CACHE.clear()

    def test_assets_are_reproducible(self):
        """有 Pillow 时：重画一遍，逐字节比。没有就跳过（CI 不装 Pillow）。"""
        try:
            import PIL  # noqa: F401
            import readme_assets as RA
        except Exception as e:
            self.skipTest("本机没有 Pillow，跳过重画比对：%s" % str(e)[:60])
        tmp = tempfile.mkdtemp(prefix="readme-assets-")
        old = RA.OUT_DIR
        try:
            RA.OUT_DIR = tmp
            for name, fn in RA.JOBS.items():
                fn(os.path.join(tmp, name))
            for name in RA.JOBS:
                with open(os.path.join(ASSET_DIR, name), "rb") as f:
                    da = f.read()
                with open(os.path.join(tmp, name), "rb") as f:
                    db = f.read()
                self.assertEqual(hashlib.sha256(da).hexdigest(),
                                 hashlib.sha256(db).hexdigest(),
                                 "%s 重建后不一致 —— 配图不是确定性的" % name)
        finally:
            RA.OUT_DIR = old


if __name__ == "__main__":
    unittest.main(verbosity=2, argv=[sys.argv[0]] + sys.argv[1:])
