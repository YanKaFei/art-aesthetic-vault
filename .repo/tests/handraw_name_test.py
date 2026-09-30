#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""handraw_name_test.py —— 第 7 大类手绘卡的**中文命名**测试。

    python3 tests/handraw_name_test.py
    python3 tests/handraw_name_test.py -v

## 这一层守什么

命名这件事最容易出的错不是「名字不好听」，而是**不可核对**：

  · 名字里的词在 traits 里根本找不到 → 读者无法验证，等于编的
  · 274 条里有两条同名 → 双链 `[[名字]]` 歧义，库里立刻多出断链
  · 名字里混进编号/ASCII → 「001 松散黑线」这种，读起来还是编号卡
  · 20 条 traits 为空的，如果静默跳过 → 读者不会知道那 20 条没名字

所以测试全部围绕「可核对、唯一、覆盖有交代」三件事，而不是文采。
"""

import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)

CJK = re.compile(r"[\u4e00-\u9fff]")


class CoverageTests(unittest.TestCase):
    """覆盖：274 条一条都不能少，且缺依据的要显形。"""

    def test_imports(self):
        import handraw_name  # noqa: F401

    def test_every_style_gets_a_name(self):
        import handraw_name as HN
        names = HN.all_names()
        self.assertEqual(len(names), 274, "274 条必须都有名字")
        for num, rec in names.items():
            self.assertTrue(rec["name"].strip(), "编号 %s 没有名字" % num)

    def test_keys_are_the_numbers(self):
        import handraw_name as HN
        nums = set(HN.all_names())
        self.assertEqual(len(nums), 274)
        self.assertIn("001", nums)
        self.assertIn("274", nums)

    def test_empty_traits_are_flagged_not_hidden(self):
        """traits 为空的 20 条必须显式标出来源，不能假装有依据。"""
        import handraw_name as HN
        for num, rec in HN.all_names().items():
            if not rec["traits_chars"]:
                self.assertEqual(rec["basis"], "generation_name",
                                 "编号 %s traits 为空，却没标出兜底来源" % num)
            else:
                # 有 traits 的，凭据只能是逐字命中或词表排序两种
                self.assertIn(rec["basis"],
                              ("traits", "traits_unmatched"), num)

    def test_unmatched_evidence_is_flagged_not_faked(self):
        """词表没命中时要**如实标 `traits_unmatched`**，不能编一份凭据。

        实测 8 条的 traits 用的是词表没收录的说法（「街头图腾」「视觉隐喻」
        「成人主题」…）。这时正确的做法是承认「没有逐字命中」，
        而不是拿排序结果冒充证据 —— 后者会让 `from` 看起来有据可查，
        实际与名字无关。所以这里断言的是**标记存在**，不是凭据非空。
        """
        import handraw_name as HN
        unmatched = [n for n, r in HN.all_names().items()
                     if r["basis"] == "traits_unmatched"]
        for n in unmatched:
            self.assertEqual(HN.all_names()[n]["from"], [],
                             "标了 unmatched 却还带着凭据，自相矛盾")
        self.assertLessEqual(len(unmatched), 20,
                             "无逐字命中的条目太多（%d），词表该补了" % len(unmatched))


class TraceabilityTests(unittest.TestCase):
    """可核对：名字里的词必须能在依据里找到。"""

    def test_name_words_come_from_traits_when_available(self):
        """basis=traits 的名字，至少有一个词能在 traits 原文里找到。

        这是「名字不是编的」的唯一机械证明。名字是压缩，不可能每个字
        都来自 traits；但**至少要有一个词同源**，否则无从核对。
        """
        import handraw_name as HN
        bad = []
        for num, rec in HN.all_names().items():
            if rec["basis"] != "traits":
                continue
            t = rec["traits"]
            if not any(w and w in t for w in rec["from"]):
                bad.append((num, rec["name"], rec["from"]))
        self.assertFalse(bad, "这些名字在 traits 里找不到出处：%s" % bad[:5])

    def test_generation_name_basis_records_the_source(self):
        """traits 为空的条目，要留得下生图名当依据。

        ⚠ 不能断言生图名是英文：201–216 那 16 条 handraw 的生图名本身
        就是中文（`可爱萌系插画风`）—— 第一版测试断言 `isascii()`，
        于是把这 16 条**合法**条目误报成失败。
        """
        import handraw_name as HN
        for num, rec in HN.all_names().items():
            if rec["basis"] == "generation_name":
                self.assertTrue(rec["generation_name"], num)

    def test_every_record_carries_its_evidence(self):
        import handraw_name as HN
        for num, rec in HN.all_names().items():
            for k in ("name", "basis", "from", "traits", "traits_chars",
                      "generation_name", "group"):
                self.assertIn(k, rec, "编号 %s 缺字段 %s" % (num, k))


class UniquenessTests(unittest.TestCase):
    """唯一：同名会让双链歧义。"""

    def test_names_are_unique(self):
        import handraw_name as HN
        names = [r["name"] for r in HN.all_names().values()]
        dup = [n for n in set(names) if names.count(n) > 1]
        self.assertFalse(dup, "这些名字重复：%s" % dup[:6])

    def test_no_name_collides_with_a_non_handraw_movement(self):
        """新名不得与既有流派卡的文件名撞车（否则 [[名字]] 指向两张卡）。"""
        import handraw_name as HN
        import artvault_core as A
        taken = {c["name_zh"] for c in A.cards() if not c.get("handraw_number")}
        clash = [r["name"] for r in HN.all_names().values() if r["name"] in taken]
        self.assertFalse(clash, "与既有流派卡同名：%s" % clash[:6])


class ReadabilityTests(unittest.TestCase):
    """可读：中文、长度像名字、不带编号。"""

    def test_names_are_chinese(self):
        import handraw_name as HN
        for num, rec in HN.all_names().items():
            self.assertTrue(CJK.search(rec["name"]), "编号 %s 的名字没有中文" % num)

    def test_length_is_name_like(self):
        """2–14 字。短于 2 不是名字，长于 14 是描述。"""
        import handraw_name as HN
        bad = []
        for num, rec in HN.all_names().items():
            n = len(CJK.findall(rec["name"]))
            if n < 2 or n > 14:
                bad.append((num, rec["name"], n))
        self.assertFalse(bad, "长度异常：%s" % bad[:6])

    # 合法出现的拉丁/数字片段：它们是**媒介词**，不是索引信息。
    # 中文里说「3D 动画」「Q 版」是常态，把这些也禁掉是把好名字误伤。
    _OK_LATIN = {"2D", "3D", "Q", "Z", "Instagram"}

    def test_no_index_numbers_or_stray_english(self):
        """名字里不该出现**编号**或**孤立英文单词**。

        禁的是索引信息（`手绘137` 这种），不是所有拉丁字符：
        实测 9 条合法名字里带 `2D`/`3D`/`Q版`，那是媒介词。
        第一版断言 `[0-9A-Za-z]` 一票否决，把这 9 条好名字误报成失败。
        """
        import handraw_name as HN
        bad = []
        for r in HN.all_names().values():
            name = r["name"]
            # 纯编号形态（如「手绘137」「137」）
            if re.fullmatch(r"[\u4e00-\u9fff]{0,3}\d{2,}", name):
                bad.append(name)
                continue
            for tok in re.findall(r"[0-9A-Za-z]+", name):
                if tok not in self._OK_LATIN:
                    bad.append((name, tok))
        self.assertFalse(bad, "名字里混进了编号/孤立英文：%s" % bad[:6])


class IntegrationTests(unittest.TestCase):
    """接入：卡片与检索都要真的用上新名字。"""

    def test_movement_definitions_carry_the_name(self):
        import mv_handraw
        miss = [m["slug"] for m in mv_handraw.MOVEMENTS
                if not m.get("name_alias")]
        self.assertFalse(miss, "这些手绘卡没带上新名字：%s" % miss[:5])

    def test_alias_points_at_the_same_card(self):
        import handraw_name as HN
        import artvault_core as A
        rec = HN.all_names()["001"]
        got = A.lookup(rec["name"])
        self.assertIsNotNone(got, "用新名字查不到卡：%s" % rec["name"])
        self.assertEqual(got["slug"], "handraw-001")
        # 编号仍然可用（两种叫法都指向同一张卡）
        self.assertEqual(A.lookup("手绘001")["slug"], "handraw-001")

    def test_search_finds_card_by_new_name(self):
        import artvault_core as A
        import handraw_name as HN
        r = A.search(HN.all_names()["001"]["name"], 3)
        self.assertTrue(r)
        self.assertEqual(r[0]["slug"], "handraw-001")

    def test_alias_survives_either_import_order(self):
        """循环导入必须被切断 —— 否则「谁先被导入」决定别名是否为空。

        实测症状：单独跑 `python3 -c "import artvault_core"` 一切正常，
        但按测试文件的顺序（先 import handraw_name 再 import artvault_core）
        274 条别名**全空**。原因：handraw_name 顶层 import mv_handraw，
        而 mv_handraw._blueprint 里又 import handraw_name。现在
        handraw_name 直接读 styles.json，不再依赖 mv_handraw。
        """
        import subprocess
        for order in (["handraw_name", "artvault_core", "mv_handraw"],
                      ["artvault_core", "mv_handraw", "handraw_name"]):
            code = ("import %s; import mv_handraw;"
                    "m=[x for x in mv_handraw.MOVEMENTS"
                    " if x['handraw_number']=='001'][0];"
                    "print(m.get('name_alias') or 'EMPTY')" % "; import ".join(order))
            p = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                               capture_output=True, text=True, timeout=90)
            self.assertNotIn("EMPTY", p.stdout,
                             "导入顺序 %s 下别名为空" % order)
            self.assertIn("松散", p.stdout, p.stdout + p.stderr[-200:])

    def test_aliases_are_unique(self):
        """别名也要唯一 —— 别名进检索索引，重名会让搜索指向错的卡。"""
        import handraw_name as HN
        a = [r["name"] for r in HN.all_names().values()]
        self.assertEqual(len(a), len(set(a)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
