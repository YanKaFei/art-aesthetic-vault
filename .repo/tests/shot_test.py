#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""shot_test.py —— 镜头配方卡模块（45-shots/）的单元测试。纯标准库。

    python3 tests/shot_test.py
    python3 tests/shot_test.py -v

## 这一层守什么

1. **解析器对上游的真实文本要稳** —— 用 158 个上游卡文件的**离线夹具**跑，
   不联网。上游改版会在这里红，而不是等到生成一堆空卡才发现。
2. **不误归类** —— 镜头卡是「运镜招式」，不是「风格」。所以它
   **不能**被塞进七层体系：`fv_core.LAYERS` 里不该有它，`compose`
   也不该把一张镜头卡当成风格层去拼提示词（那会拼出没有色彩语义的句子）。
   这条边界必须有测试，否则有一天有人「顺手统一一下」，库就悄悄错了。
3. **许可干净** —— Apache-2.0 要求保留出处。每张卡都要有上游路径与 commit，
   卡片上不得声称原创。
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VAULT = os.path.dirname(REPO)
SHOTS_FIX = os.path.join(HERE, "fixtures", "shots")
sys.path.insert(0, REPO)


class ParserTests(unittest.TestCase):
    """解析器：把上游的卡 Markdown 变成结构化数据。"""

    def test_imports(self):
        import shot_import  # noqa: F401

    def test_parses_one_card(self):
        import shot_import
        s = shot_import.parse_card(
            open(os.path.join(SHOTS_FIX, "camera", "crash-zoom-punch.md"),
                 encoding="utf-8").read(),
            # 类别是从**路径**来的（上游用目录名分类，不是靠 frontmatter），
            # 所以单张解析也要把路径传进去 —— 这也正是 parse_dir 的做法。
            path="references/shots/camera/crash-zoom-punch.md")
        self.assertEqual(s["name"], "crash-zoom-punch")
        self.assertEqual(s["category"], "camera")
        self.assertIn("急推", s["one_liner"])
        self.assertTrue(s["purpose"])
        self.assertTrue(s["duration"])
        self.assertTrue(s["energy"])

    def test_parses_all_fixture_cards(self):
        """全部 157 张都要能解析，且都必须有必填字段。"""
        import shot_import
        cards = shot_import.parse_dir(SHOTS_FIX)
        self.assertEqual(len(cards), 157, "夹具里有 157 张卡（不含 ATTRIBUTION）")
        for c in cards:
            self.assertTrue(c["name"], c)
            self.assertTrue(c["one_liner"], c["name"])
            self.assertTrue(c["category"], c["name"])
            self.assertTrue(c["path"].startswith("references/shots/"), c["name"])

    def test_attribution_file_is_not_a_card(self):
        import shot_import
        names = {c["name"] for c in shot_import.parse_dir(SHOTS_FIX)}
        self.assertNotIn("ATTRIBUTION", names)

    def test_body_sections_preserved(self):
        """五个段落必须按原样保住 —— 这是卡片的主体内容。"""
        import shot_import
        s = shot_import.parse_card(
            open(os.path.join(SHOTS_FIX, "camera", "crash-zoom-punch.md"),
                 encoding="utf-8").read())
        titles = [sec["title"] for sec in s["sections"]]
        self.assertIn("意图", titles)
        self.assertIn("参数表", titles)
        self.assertIn("已知坑", titles)
        self.assertIn("参考实现", titles)
        # 参数表要真的带上表格内容
        params = [x for x in s["sections"] if x["title"] == "参数表"][0]
        self.assertIn("|", params["body"])

    def test_section_name_variants_are_kept(self):
        """段落名有变体：动效核心 / 两式选型 / 单式选型。

        解析器要**原样保留**段名（读者看的就是这个），同时按语义归类，
        不能因为名字不同就丢掉那一段 —— 丢了就等于卡片少了主体。
        """
        import shot_import
        effects = shot_import.parse_card(
            open(os.path.join(SHOTS_FIX, "effects", "riso-print-hits.md"),
                 encoding="utf-8").read())
        titles = [s["title"] for s in effects["sections"]]
        self.assertTrue(any(t in ("动效核心", "两式选型", "单式选型") for t in titles),
                        titles)
        self.assertTrue(effects["motion"], "动效主体段不能为空")

    def test_energy_and_tags_are_structured(self):
        import shot_import
        cards = {c["name"]: c for c in shot_import.parse_dir(SHOTS_FIX)}
        c = cards["crash-zoom-punch"]
        self.assertTrue(c["energy"])
        self.assertIsInstance(c["tags"], list)
        self.assertIn("effects", c["tags"])

    def test_malformed_card_raises_with_path(self):
        """结构不对必须**报错并指出是哪张卡**，不能静默返回空卡。

        这是失败模式②：上游改版后如果安静地解析出空内容，会生成一堆
        没有正文的卡，而且没有任何报警。
        """
        import shot_import
        with self.assertRaises(shot_import.BadCard) as cm:
            shot_import.parse_card("这不是一张卡", path="references/shots/x/y.md")
        self.assertIn("references/shots/x/y.md", str(cm.exception))


class ProvenanceTests(unittest.TestCase):
    """许可与出处：Apache-2.0 的要求，也是「不得声称原创」的底线。"""

    def test_every_card_has_upstream_provenance(self):
        import shot_import
        for c in shot_import.parse_dir(SHOTS_FIX):
            self.assertTrue(c["source_repo"], c["name"])
            self.assertTrue(c["source_path"].startswith("references/shots/"), c["name"])
            self.assertTrue(c["source_commit"], c["name"])
            self.assertEqual(c["license"], "Apache-2.0", c["name"])

    def test_generated_cards_name_the_upstream(self):
        """生成的卡上必须写明来自上游，不能读起来像本站原创。"""
        import shot_build, shot_core
        shots = shot_core.shots()
        if not shots:
            self.skipTest("45-shots 还没生成")
        md = shot_build.card_note(shots[0])
        self.assertIn("video-shotcraft", md)
        self.assertIn("Apache-2.0", md)

    def test_attribution_note_exists_and_is_honest(self):
        """出处页要写明上游边界：手法参考、从零重写、不含原片素材。"""
        import shot_build
        md = shot_build.attribution_note()
        self.assertIn("video-shotcraft", md)
        self.assertIn("Apache-2.0", md)
        self.assertIn("重新实现", md)
        # 上游明说「公开发布不等于授权」—— 转述时必须保住这个意思
        self.assertIn("不是授权", md)


class BoundaryTests(unittest.TestCase):
    """边界：镜头卡是另一条轴，不能被当成风格层。"""

    def test_shots_are_not_in_the_seven_layer_schema(self):
        """镜头卡**没有**七层。

        它们讲的是动效时序与参数（`6f ease-in`、`zoom 1→2.6`），
        没有任何色彩/光照/媒介语义。给它们套七层就是编造。
        """
        import shot_core
        self.assertFalse(hasattr(shot_core, "LAYERS"))
        self.assertFalse(getattr(shot_core, "HAS_LAYER_SCHEMA", False))

    def test_compose_cannot_take_a_shot_slug_as_a_style_layer(self):
        """compose 不能把镜头卡当成风格层。

        这条是**真实风险**：如果哪天有人把镜头卡也注册进 artvault_core
        的 lookup，`compose --style crash-zoom-punch` 就会拼出一段
        没有色彩语义的提示词，而且不会报错。
        """
        import artvault_core as A
        for probe in ("crash-zoom-punch", "radial-wave", "text-as-mask"):
            self.assertIsNone(A.by_slug().get(probe),
                              "镜头卡混进了风格库：%s" % probe)

    def test_shot_slugs_do_not_collide_with_movement_slugs(self):
        """第三轴与前两轴的 slug 不能撞车。"""
        import artvault_core as A
        import shot_core
        mv = set(A.by_slug())
        for s in shot_core.shots():
            self.assertNotIn(s["slug"], mv, "slug 与流派卡撞车：%s" % s["slug"])


class CardIntegrityTests(unittest.TestCase):
    """生成物的完整性：断链是生成器最容易犯的错。"""

    def test_all_wiki_links_resolve(self):
        """生成物里每个 `[[双链]]` 都要能解析到一篇真实笔记。

        真实目标取自「目录里有哪些 .md」，与 verify_vault 第 9 项的判定一致。
        不手写目标清单 —— 手写的清单会随模板改动过时，而过时的检查比没有更糟。
        """
        import glob, re as _re
        d = os.path.join(VAULT, "45-shots")
        if not os.path.isdir(d):
            self.skipTest("45-shots 还没生成")
        notes = set()
        for root in ("45-shots", "40-films", "00-guides", "10-movements"):
            for p in glob.glob(os.path.join(VAULT, root, "**", "*.md"), recursive=True):
                notes.add(os.path.splitext(os.path.basename(p))[0])
        broken = []
        for root, _d, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                t = open(os.path.join(root, fn), encoding="utf-8").read()
                t = _re.sub(r"```.*?```", "", t, flags=_re.S)
                t = t.replace("\\|", "|")
                for m in _re.findall(r"(?<!!)\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]", t):
                    if m.strip() and m.strip() not in notes:
                        broken.append((fn, m.strip()))
        self.assertFalse(broken, "断链：%s" % broken[:6])

    def test_upstream_text_is_not_altered(self):
        """卡片正文必须**逐字**保留上游段落 —— 本库只归类，不改技法描述。

        这条守的是 Apache-2.0 下最基本的一件事：改动别人的文字要说明，
        而我们选择的是不改。任何「顺手润色一下」都会在这里红。
        """
        import shot_core, shot_import
        for x in shot_core.shots()[:40]:
            self.assertEqual(x["sections"], shot_import.parse_card(
                open(os.path.join(SHOTS_FIX, x["source_path"].split("references/shots/")[1]),
                     encoding="utf-8").read(),
                path=x["source_path"])["sections"], x["name"])


class CoreTests(unittest.TestCase):
    """调用层：AI 要能按类别、按意图、按关键词找到卡。"""

    def test_shots_load(self):
        import shot_core
        shots = shot_core.shots()
        self.assertEqual(len(shots), 157)
        self.assertEqual(len(shot_core.categories()), 10)

    def test_categories_match_upstream(self):
        import shot_core
        cats = {c["category"] for c in shot_core.shots()}
        self.assertEqual(cats, {"ui-entrance", "typography", "transition", "effects",
                                "interaction", "data", "rhythm", "opening", "camera",
                                "outro"})

    def test_search_by_intention(self):
        """按「我想做什么」搜 —— 这是这个库的主用法。"""
        import shot_core
        r = shot_core.search("急推 冲击")
        self.assertTrue(r)
        self.assertEqual(r[0]["name"], "crash-zoom-punch")

    def test_search_by_english_name(self):
        import shot_core
        r = shot_core.search("crash-zoom-punch")
        self.assertTrue(r)
        self.assertEqual(r[0]["name"], "crash-zoom-punch")

    def test_resolve_by_name_and_alias_without_spaces(self):
        import shot_core
        for probe in ("crash-zoom-punch", "crash zoom punch", "crashzoom punch"):
            s, _ = shot_core.resolve(probe)
            self.assertIsNotNone(s, "解析不了：%r" % probe)

    def test_resolve_by_chinese_intention_alias(self):
        """按中文意图词解析 —— 这是国人（和 AI）最自然的叫法。

        踩过：`get_shot("急推")` 解析不了，因为「急推」不在卡名或一句话里，
        只在别名表里。而别名恰恰是最常用的入口（没人记得住
        `crash-zoom-punch` 这种名字）。
        """
        import shot_core
        for probe in ("急推", "震屏", "色块擦除", "卡点"):
            x, _ = shot_core.resolve(probe)
            self.assertIsNotNone(x, "中文意图解析不了：%r" % probe)

    def test_alias_match_is_exact_not_substring(self):
        """别名匹配必须精确，不能子串 —— 否则「推」会命中一堆卡，等于没筛。"""
        import shot_core
        x, hints = shot_core.resolve("推")
        self.assertIsNone(x, "单字「推」不该被当成精确别名命中")

    def test_resolve_unknown_gives_hints_not_a_wrong_card(self):
        import shot_core
        s, hints = shot_core.resolve("完全不存在的招式zzz")
        self.assertIsNone(s)
        self.assertIsInstance(hints, list)

    def test_filter_by_category(self):
        import shot_core
        r = shot_core.by_category("camera")
        self.assertEqual(len(r), 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
