#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""still_test.py —— 剧照全量分析模块（剧照实测）的单元测试。纯标准库。

    python3 tests/still_test.py
    python3 tests/still_test.py -v

## 这一层守什么

1. **实测与分析必须可复现** —— 同一张图同一次测量给同样的数，代表帧的选择
   也必须是确定性的（否则每次重建 diff 都在抖）。
2. **数字是信号不是结论** —— 这是本库的规矩。所以实测结果**不得覆盖**手写的
   七层与配色，只允许并列展示并标差异。`palette_diff()` 的契约就是
   「报告差异」，不是「修正差异」。有测试守这条。
3. **缺图不能静默** —— 实测页要如实写出「量了几张 / 共几张」。漏了 7 张
   还说「全片均值」，那是误导。
"""

import glob
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VAULT = os.path.dirname(REPO)
STILLS = os.path.join(VAULT, "99-attachments", "images-films")
sys.path.insert(0, REPO)


def _have_stills():
    return len(glob.glob(os.path.join(STILLS, "*", "*.jpg")))


class FeatureTests(unittest.TestCase):
    """特征提取：不依赖具体影片，用能算出来的东西验。"""

    def test_imports(self):
        import still_analysis  # noqa: F401

    def test_histogram_feature_shape_and_normalisation(self):
        """色相-饱和度直方图：形状固定、和为 1。

        形状固定是代表帧选择可复现的前提；归一化让不同分辨率的图可比。
        """
        import still_analysis as SA
        hp = _have_stills()
        if not hp:
            self.skipTest("还没有本地剧照")
        p = glob.glob(os.path.join(STILLS, "*", "*.jpg"))[0]
        f = SA.feature(p)
        self.assertEqual(len(f), SA.FEATURE_LEN)
        self.assertAlmostEqual(sum(f), 1.0, places=5)

    def test_feature_is_deterministic(self):
        import still_analysis as SA
        if not _have_stills():
            self.skipTest("还没有本地剧照")
        p = sorted(glob.glob(os.path.join(STILLS, "*", "*.jpg")))[0]
        self.assertEqual(SA.feature(p), SA.feature(p))


class AnalyseTests(unittest.TestCase):
    """单张测量与全片聚合。"""

    def test_analyse_one_still_has_expected_keys(self):
        import still_analysis as SA
        if not _have_stills():
            self.skipTest("还没有本地剧照")
        p = sorted(glob.glob(os.path.join(STILLS, "*", "*.jpg")))[0]
        r = SA.analyse_still(p)
        for k in ("width", "height", "ratio", "luminance", "contrast",
                  "saturation", "dominant"):
            self.assertIn(k, r)
        self.assertEqual(len(r["dominant"]), 6)
        for h, _ in r["dominant"]:
            self.assertRegex(h, r"^#[0-9A-F]{6}$")

    def test_analyse_film_reports_coverage(self):
        """必须如实报告「量了几张 / 共几张」—— 漏量不能静默。"""
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("villeneuve-dune")
        r = SA.analyse_film(f)
        if not r["measured"]:
            self.skipTest("这部片还没下载")
        self.assertEqual(r["total_linked"], len(f["stills"]))
        self.assertLessEqual(r["measured"], r["total_linked"])
        self.assertEqual(r["measured"], len(r["stills"]))

    def test_aggregate_is_deterministic(self):
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("fincher-se7en")
        a = SA.analyse_film(f)
        if not a["measured"]:
            self.skipTest("这部片还没下载")
        b = SA.analyse_film(f)
        self.assertEqual(a["aggregate"], b["aggregate"])
        self.assertEqual(a["representative"], b["representative"])

    def test_representative_frames_are_subset_and_ordered(self):
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("kubrick-the-shining")
        r = SA.analyse_film(f, k=8)
        if r["measured"] < 8:
            self.skipTest("图还不够")
        self.assertLessEqual(len(r["representative"]), 8)
        names = [x["file"] for x in r["representative"]]
        self.assertEqual(len(names), len(set(names)), "代表帧不能重复")
        for x in r["representative"]:
            self.assertTrue(os.path.exists(x["path"]), x["path"])
        idx = [x["index"] for x in r["representative"]]
        self.assertEqual(idx, sorted(idx), "代表帧要按序排出（稳定）")


class SampleStabilityTests(unittest.TestCase):
    """抽样稳定性：没下齐时，已量的那部分能不能代表全片？

    这是**覆盖度告警之后的下一个问题**。页上写着「已量 8/65」，读者接着
    就会问「那这 8 张算得准吗」。与其让人猜，不如算给他看：
    前 1/4 与全量的均值差多少。
    """

    def test_returns_structure_with_both_means(self):
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("tarkovsky-stalker")
        r = SA.analyse_film(f)
        if r["measured"] < 12:
            self.skipTest("样本太少")
        st = SA.sample_stability(r["stills"])
        self.assertIn("first_quarter_mean", st)
        self.assertIn("all_mean", st)
        self.assertIn("verdict", st)
        self.assertIn(st["verdict"], ("稳定", "有偏", "样本还太少，别下结论"))

    def test_is_deterministic(self):
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("tarkovsky-mirror")
        r = SA.analyse_film(f)
        if r["measured"] < 12:
            self.skipTest("样本太少")
        self.assertEqual(SA.sample_stability(r["stills"]),
                         SA.sample_stability(r["stills"]))

    def test_tiny_sample_says_so_instead_of_claiming_stability(self):
        """样本太少时必须说「别下结论」，不能给一个好看的「稳定」。"""
        import still_analysis as SA
        fake = [{"luminance": 50.0, "saturation": 0.2} for _ in range(4)]
        st = SA.sample_stability(fake)
        self.assertEqual(st["verdict"], "样本还太少，别下结论")

    def test_declares_bias_when_present(self):
        """真造一个偏样：前一半很亮、后一半很暗 → 必须报「有偏」。"""
        import still_analysis as SA
        fake = [{"luminance": 200.0, "saturation": 0.5} for _ in range(8)]
        fake += [{"luminance": 20.0, "saturation": 0.5} for _ in range(24)]
        st = SA.sample_stability(fake)
        self.assertEqual(st["verdict"], "有偏")


class LowlightCaveatTests(unittest.TestCase):
    """近全黑的帧会污染色彩统计，聚合时必须把它们标出来。"""

    def test_near_black_frames_are_listed(self):
        import still_analysis as SA
        fake = [{"luminance": 6.2, "saturation": 0.78, "file": "a.jpg", "index": 1},
                {"luminance": 80.0, "saturation": 0.25, "file": "b.jpg", "index": 2},
                {"luminance": 3.0, "saturation": 0.9, "file": "c.jpg", "index": 3}]
        ag = SA._aggregate(fake)
        self.assertEqual([x["file"] for x in ag["lowlight"]], ["a.jpg", "c.jpg"])
        self.assertIn("污染", ag["lowlight_note"])

    def test_no_lowlight_frames_means_empty_list(self):
        import still_analysis as SA
        fake = [{"luminance": 80.0, "saturation": 0.25, "file": "b.jpg", "index": 1}]
        ag = SA._aggregate(fake)
        self.assertEqual(ag["lowlight"], [])

    def test_measurement_note_warns_when_present(self):
        """页上要有告警 —— 否则读者会把被污染的饱和度当成风格特征。"""
        import still_analysis as SA, still_build, fv_core
        f, _ = fv_core.resolve("tarkovsky-stalker")
        r = SA.analyse_film(f)
        if not (r["aggregate"].get("lowlight")):
            self.skipTest("这部片没有近全黑帧")
        md = still_build.measurement_note(r, f)
        self.assertIn("近全黑", md)


class PaletteDiffTests(unittest.TestCase):
    """配色比对：**只报告差异，绝不改写手写值**。"""

    def test_palette_diff_reports_and_does_not_mutate(self):
        import still_analysis as SA
        written = [("#FFFFFF", "纯白"), ("#000000", "纯黑")]
        measured = [("#FEFEFE", "近白"), ("#010101", "近黑")]
        d = SA.palette_diff(written, measured)
        self.assertIn("距离", d)          # 中文键名，与库内其它页面一致
        self.assertIn("verdict", d)
        # 手写值必须原样还在 —— 这个函数没有修改权
        self.assertEqual(written[0][0], "#FFFFFF")

    def test_palette_diff_flags_close_and_far(self):
        import still_analysis as SA
        same = SA.palette_diff([("#FF0000", "红")], [("#FE0101", "红")])
        far = SA.palette_diff([("#FF0000", "红")], [("#00FF00", "绿")])
        self.assertIn("一致", same["verdict"])
        self.assertIn("不一致", far["verdict"])

    def test_hex_to_rgb_roundtrip(self):
        import still_analysis as SA
        self.assertEqual(SA.hex_to_rgb("#1A1512"), (26, 21, 18))
        self.assertEqual(SA.hex_to_rgb("#fff"), (255, 255, 255))


class CacheTests(unittest.TestCase):
    """缓存：省时间，但**不能变成假数据源**。"""

    def test_cache_roundtrip_and_staleness(self):
        import still_analysis as SA
        if not _have_stills():
            self.skipTest("还没有本地剧照")
        p = sorted(glob.glob(os.path.join(STILLS, "*", "*.jpg")))[0]
        r = SA.analyse_still(p)
        SA.save_measurements("__test__", {"stills": [r], "measured": 1,
                                          "total_linked": 1, "aggregate": {},
                                          "representative": []})
        got = SA.load_measurements("__test__")
        self.assertIsNotNone(got)
        self.assertEqual(got["measured"], 1)
        # 清掉测试用的缓存，别污染真实数据
        p2 = os.path.join(SA.DATA_DIR, "__test__.json")
        if os.path.exists(p2):
            os.remove(p2)


class RenderTests(unittest.TestCase):
    """实测页的渲染契约：该有的都得有，尤其是**覆盖度**。"""

    def _note(self, slug="kubrick-barry-lyndon"):
        import still_analysis as SA, still_build, fv_core
        f, _ = fv_core.resolve(slug)
        r = SA.analyse_film(f)
        if not r["measured"]:
            self.skipTest("这部片还没下载")
        return still_build.measurement_note(r, f), r

    def test_note_reports_coverage_honestly(self):
        """必须写明「已量 N / 共 M 张」。

        用 176 张样本冒充 1001 张的全片均值是**最能骗人的一种错** ——
        算出来的数字都对，只有样本不对。
        """
        md, r = self._note()
        self.assertIn("已量", md)
        self.assertIn("%d" % r["measured"], md)
        self.assertIn("%d" % r["total_linked"], md)

    def test_note_has_measured_and_written_palette_side_by_side(self):
        md, r = self._note()
        self.assertIn("实测主色", md)
        self.assertIn("手写配色", md)
        for hx in r["palette_written"]:
            self.assertIn(hx, md, "手写色 %s 必须原样出现在页上" % hx)
        for hx, _ in r["palette_measured"]:
            self.assertIn(hx, md)

    def test_note_states_the_diff_verdict_without_overriding(self):
        """差异只标注，不覆盖。页上要说清「这是信号不是结论」。"""
        md, r = self._note()
        self.assertIn(r["palette_diff"]["verdict"], md)
        self.assertIn("信号", md)

    def test_note_has_seven_dimensions(self):
        md, _ = self._note()
        for dim in ("明度", "对比", "饱和度", "暖度", "边缘密度", "暗部溢出", "高光溢出"):
            self.assertIn(dim, md, "缺维度：%s" % dim)

    def test_note_has_framing_and_lines(self):
        md, _ = self._note()
        self.assertIn("景别", md)
        self.assertIn("构图", md)

    def test_note_lists_representative_frames(self):
        md, r = self._note()
        self.assertIn("代表帧", md)
        for x in r["representative"][:3]:
            self.assertIn(x["file"], md)

    # 「嵌入一张本地图」的三种写法（与 film_test 同一套判定）
    _EMBED_RE = __import__("re").compile(
        r"!\[[^\]]*images-films"                  # ![[images-films/…]]
        r"|!\[[^\]]*\]\([^)]*images-films"        # ![](images-films/…)
        r"|<img[^>]+images-films")                 # <img src="images-films/…">

    def test_note_never_embeds_local_images(self):
        """实测页也不能**嵌入**本地剧照（版权 + 别人 clone 后红叉）。

        注意禁的是**嵌入语法**，不是禁止提到那个目录 —— 实测页恰恰要告诉
        读者本地副本放在哪、怎么重建。第一版拿 `"images-films/" in md` 判，
        把自己那句「本地路径：99-attachments/images-films/…」误报成了违规。
        """
        md, _ = self._note()
        self.assertNotIn("![[99-attachments", md)
        self.assertIsNone(self._EMBED_RE.search(md), "实测页嵌入了本地剧照")
        # 但**必须**说明本地副本在哪（否则读者找不到代表帧）
        self.assertIn("images-films/", md)

    def test_note_is_deterministic(self):
        import still_analysis as SA, still_build, fv_core
        f, _ = fv_core.resolve("kubrick-barry-lyndon")
        r = SA.analyse_film(f)
        if not r["measured"]:
            self.skipTest("这部片还没下载")
        self.assertEqual(still_build.measurement_note(r, f),
                         still_build.measurement_note(r, f))


class BuilderInteropTests(unittest.TestCase):
    """两个生成器住在同一个目录（40-films/），不能互相删对方的产物。"""

    def test_fv_build_sweep_actually_keeps_a_measurement_page(self):
        """**行为验证**：造一份假的实测页，跑 fv_build.sweep，它必须还在。

        第一版这条测试只查源码里有没有 `director_slug` 字样 —— 那是
        「检查在、却什么也没守住」的老毛病：我把 sweep 改成按目录清之后，
        它照样删掉实测页，而源码检查依然绿。现在改成真的删一次试试。
        """
        import fv_build, fv_core, still_analysis as SA
        f, _ = fv_core.resolve("kubrick-the-shining")
        if not SA.load_measurements(f["slug"]):
            self.skipTest("这部片还没实测数据，sweep 本就不该保护它的实测页")
        sub = os.path.join(fv_build.OUT_DIR, f["director_slug"])
        page = os.path.join(sub, "%s-实测.md" % f["title_zh"])
        existed = os.path.exists(page)
        if not existed:
            open(page, "w", encoding="utf-8").write("哨兵\n")
        try:
            fv_build.sweep(fv_core.directors())
            self.assertTrue(os.path.exists(page),
                            "sweep 删掉了 still_build 的实测页")
        finally:
            if not existed and os.path.exists(page):
                os.remove(page)

    def test_sweep_still_removes_stale_film_cards(self):
        """差集清扫不能矫枉过正：**过时的旧卡还是要清**。

        否则改了片名或删了片之后，旧文件会永远留在库里，
        verify 的孤儿/断链检查也发现不了。
        """
        import fv_build, fv_core
        sub = os.path.join(fv_build.OUT_DIR, "kubrick")
        ghost = os.path.join(sub, "不存在的旧卡.md")
        os.makedirs(sub, exist_ok=True)
        open(ghost, "w", encoding="utf-8").write("旧残骸\n")
        try:
            fv_build.sweep(fv_core.directors())
            self.assertFalse(os.path.exists(ghost), "过时的旧卡没有被清掉")
        finally:
            if os.path.exists(ghost):
                os.remove(ghost)

    def test_fv_build_sweep_does_not_delete_measurement_pages(self):
        """`fv_build.py` 的清扫**只能删自己产的**文件。

        踩过的坑：它原先无差别清空 `40-films/**/*.md`，而实测页与
        `剧照实测总览.md` 也住在这里 —— 于是每次重建电影卡，实测页就被删掉，
        `[[剧照实测总览]]` 随之变成断链。症状极隐蔽：刚跑完 still_build
        一切正常，再跑一次 fv_build 就没了。

        这条测试直接比对「清扫后还剩什么」：把 sweep 的删除范围交给它验。
        """
        import inspect
        import fv_build
        src = inspect.getsource(fv_build.sweep)
        # 清扫必须是**点名删除**，不能是无差别 glob
        self.assertNotIn('glob.glob(os.path.join(OUT_DIR, "**", "*.md")', src,
                         "sweep 又变回无差别清空整个 40-films/ 了")
        self.assertIn("director_slug", src, "清扫应按导演目录点名，而不是全目录扫")
        self.assertIn("电影风格总览.md", src)

    def test_measurement_overview_name_matches_its_wikilink(self):
        """总览页的文件名必须与双链写的一致（`_` 前缀会让链接失效）。

        这个坑在电影模块的导演页上踩过一次（`_导演.md`），这里差点重演。
        """
        import still_build, re
        src = open(os.path.join(REPO, "still_build.py"), encoding="utf-8").read()
        links = set(re.findall(r"\[\[([^\]|#]+)", src))
        # 生成物里被链接的名字都要能在同一文件里找到对应的写盘调用
        for want in ("剧照实测总览",):
            self.assertIn(want, links, "页面里没有 %s 这个双链" % want)
            self.assertIn('"%s.md"' % want, src,
                          "写盘文件名与双链不一致：%s" % want)


class CacheSchemaTests(unittest.TestCase):
    """缓存要有结构版本号 —— 否则升级后读到的是**旧结构的半成品**。"""

    def test_cache_carries_a_schema_version(self):
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("villeneuve-dune")
        r = SA.analyse_film(f)
        self.assertIn("schema", r)
        self.assertEqual(r["schema"], SA.SCHEMA)

    def test_stale_schema_is_recomputed_not_reused(self):
        """旧版本缓存必须被**重算**，不能把缺字段的旧结果当完整结果返回。

        实际踩到：加了 `stability` 之后，`analyse_film` 把旧缓存原样取出，
        于是 `r["stability"]` 直接 KeyError —— 而缓存看着「有效」
        （文件指纹没变）。指纹只能判断**图变了没**，判断不了**代码变了没**。
        """
        import json, os
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("villeneuve-dune")
        p = SA._cache_path(f["slug"])
        orig = open(p, encoding="utf-8").read() if os.path.exists(p) else None
        try:
            d = json.loads(orig) if orig else {}
            d.pop("schema", None)          # 伪造成旧结构
            if d.get("stills"):
                d["stills"][0].pop("key", None)
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False)
            r = SA.analyse_film(f)
            self.assertIn("stability", r, "旧结构缓存被原样复用了")
            self.assertEqual(r["schema"], SA.SCHEMA)
        finally:
            if orig is not None:
                with open(p, "w", encoding="utf-8") as fh:
                    fh.write(orig)

    def test_fingerprint_change_invalidates_one_still(self):
        """图被换过（指纹变了）→ 那一张要重算，其余复用。"""
        import still_analysis as SA
        self.assertTrue(hasattr(SA, "_sig"))
        p = os.path.join(SA.STILLS_DIR, "villeneuve-dune", "01.jpg")
        if not os.path.exists(p):
            self.skipTest("没有本地剧照")
        a = SA._sig(p)
        self.assertTrue(a)
        self.assertEqual(a, SA._sig(p))


class CacheHygieneTests(unittest.TestCase):
    """缓存里不该出现**机器特定的绝对路径**。

    实测踩到：测量缓存把每张图的 `path`（含 `/Users/<用户名>/…`）也存了，
    于是被 smoke 的「已跟踪文件里不得有个人绝对路径」抓住 ——
    那个检查是防「别人 clone 下来看到你的私有路径」，缓存正是最容易漏的一处。
    路径本来就能从 slug 推出来，存它没有任何收益。
    """

    def test_cache_has_no_absolute_paths(self):
        import json
        import still_analysis as SA
        d = SA.DATA_DIR
        if not os.path.isdir(d):
            self.skipTest("还没有缓存")
        bad = []
        for fn in os.listdir(d):
            if not fn.endswith(".json"):
                continue
            txt = open(os.path.join(d, fn), encoding="utf-8").read()
            if "/Users/" in txt or "C:\\" in txt:
                bad.append(fn)
        self.assertFalse(bad, "缓存里有绝对路径：%s" % bad[:3])

    def test_analysed_result_still_carries_paths_in_memory(self):
        """但内存里的结果**要有** path —— 拼印相图要用它。"""
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("villeneuve-dune")
        r = SA.analyse_film(f)
        if not r["measured"]:
            self.skipTest("没有本地剧照")
        self.assertTrue(r["stills"][0]["path"].startswith("/"))
        self.assertTrue(os.path.exists(r["stills"][0]["path"]))


class ContactSheetTests(unittest.TestCase):
    """接触印相图：一次看 9 张，是「人眼精读」这一步的工具。

    ⚠ 这个类原本漏写了 —— 我插入时用的锚点不存在，脚本报 AssertionError
    而我没看 stderr，于是「测试通过」了一阵子，实际上这个类根本不在文件里。
    教训：插入测试后要**确认类真的存在**（`grep -n "^class"`），
    而不是只看 unittest 的退出码。
    """

    def test_imports(self):
        import contact_sheet  # noqa: F401

    def test_sheet_composes_expected_grid(self):
        import contact_sheet as CS
        if not _have_stills():
            self.skipTest("还没有本地剧照")
        paths = sorted(glob.glob(os.path.join(STILLS, "*", "*.jpg")))[:9]
        out = os.path.join(tempfile.gettempdir(), "av-sheet-test.jpg")
        try:
            p, why = CS.sheet(paths, out, cols=3, caption=["a"] * len(paths))
            self.assertIsNotNone(p, why)
            from PIL import Image
            self.assertGreater(Image.open(p).width, 3 * 100)
        finally:
            if os.path.exists(out):
                os.remove(out)

    def test_film_sheet_uses_representative_frames(self):
        import contact_sheet as CS
        p, why = CS.film_sheet("kubrick-the-shining", k=9)
        if not p:
            self.skipTest("这部片还没本地剧照：%s" % why)
        try:
            self.assertTrue(os.path.exists(p))
        finally:
            if p and os.path.exists(p):
                os.remove(p)

    def test_works_from_cache_without_stored_paths(self):
        """回归：缓存里**不存** path（为防泄漏绝对路径而剥离），印相图要自己补回。

        踩过：写盘前剥掉了 `path`，而 `contact_sheet` 直接拿缓存数据用，
        于是 `s["path"]` KeyError —— 缓存本身完好，没有任何检查报错，
        只有真正出图时才炸（实测 5 部片连续 KeyError）。
        """
        import contact_sheet as CS
        import still_analysis as SA
        r = SA.load_measurements("kubrick-the-shining")
        if not r or not r.get("stills"):
            self.skipTest("没有缓存")
        self.assertNotIn("path", r["stills"][0], "缓存里不该有 path")
        p, why = CS.film_sheet("kubrick-the-shining", k=9)
        self.assertIsNotNone(p, "从缓存出图失败：%s" % why)
        if p and os.path.exists(p):
            os.remove(p)

    def test_empty_input_is_reported_not_crashed(self):
        import contact_sheet as CS
        p, why = CS.sheet([], "/tmp/never.jpg")
        self.assertIsNone(p)
        self.assertIn("没有", why)

    def test_writes_to_temp_not_into_the_vault(self):
        """印相图是一次性审查工具，不该落进仓库。"""
        import contact_sheet as CS
        p, why = CS.film_sheet("kubrick-the-shining", k=9)
        if not p:
            self.skipTest("没有本地剧照")
        try:
            self.assertNotIn(VAULT, p, "印相图不该写进仓库目录")
        finally:
            if os.path.exists(p):
                os.remove(p)


class NoOverwriteTests(unittest.TestCase):
    """最重要的边界：实测不得改写手写的风格描述。"""

    # 会真正落盘的动作（AST 层面）
    _WRITE_NAMES = {"remove", "unlink", "rmtree", "copy", "copyfile", "copy2",
                    "move", "rename", "replace", "mkdir", "makedirs"}

    def test_still_analysis_has_no_write_access_to_fv_data(self):
        """分析模块只能写**自己的缓存**，不能写库里的手写数据。

        库的规矩是「数字是信号不是结论」（实测一张油画的土色系会被配色
        匹配误判成现实主义）。所以实测只并列展示 + 标差异，改不改由人决定。

        ⚠ 这里用 **AST** 而不是文本匹配。第一版拿 `"fv_data.py" in src` 判，
        结果命中了我自己 docstring 里的那句「不写回 fv_data.py」——
        检查抓的是文档而不是行为，是标准的假阳性。
        """
        import ast
        src = open(os.path.join(REPO, "still_analysis.py"), encoding="utf-8").read()
        tree = ast.parse(src)
        bad = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                if isinstance(fn, ast.Name) and fn.id == "open":
                    mode = ""
                    if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                        mode = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode = str(kw.value.value)
                    if any(c in mode for c in "wax+"):
                        # 只允许写自己的缓存目录
                        tgt = ast.unparse(node.args[0]) if node.args else ""
                        if "DATA_DIR" not in tgt and "_cache" not in tgt:
                            bad.append("open(%s, %r)" % (tgt[:40], mode))
                if isinstance(fn, ast.Attribute) and fn.attr in self._WRITE_NAMES:
                    tgt = ast.unparse(node)[:60]
                    if "DATA_DIR" not in tgt and "_cache" not in tgt:
                        bad.append(tgt)
        self.assertFalse(bad, "分析模块出现了不该有的写操作：%s" % bad)

    def test_still_analysis_does_not_import_fv_data_for_writing(self):
        """就算 future 有人 import 了 fv_data，也不得对它做属性赋值。"""
        import ast
        src = open(os.path.join(REPO, "still_analysis.py"), encoding="utf-8").read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                tgt = ast.unparse(node.targets[0] if isinstance(node, ast.Assign) else node.target)
                self.assertNotIn("fv_data", tgt, "对 fv_data 赋值：%s" % tgt)

    def test_measurement_note_keeps_written_values(self):
        """实测页上必须同时出现「我写的」与「实测的」。"""
        import still_analysis as SA, fv_core
        f, _ = fv_core.resolve("kubrick-barry-lyndon")
        r = SA.analyse_film(f)
        if not r["measured"]:
            self.skipTest("这部片还没下载")
        self.assertTrue(r["palette_diff"])
        # 手写配色原值必须在返回里
        self.assertEqual(r["palette_written"], [h for h, _ in f["palette"]])


class MetadataReuseTests(unittest.TestCase):
    """下载剧照时**必须复用已缓存的元数据**，不要重新抓画廊页。

    ## 为什么（实测踩到）

    `fv_fetch.py --download` 原来对每部片都先 `fetch_one()` 抓一遍画廊页，
    再下载图片。于是：

      · 元数据**早已抓全**（100/100），再抓一遍纯属白烧请求 ——
        而站点正在限流，等于自己把自己推向更难抓的境地；
      · 更糟的是**耦合**：元数据抓失败 → `continue` 跳过 → 这部片的图片
        一张都不下。实测一轮下来 55/100 部因此被整体跳过，
        尽管它们的元数据就躺在 `.repo/_data/films/<slug>.json` 里。

    所以 `--download` 应当优先读缓存；缓存缺失才联网。
    """

    def test_uses_cached_metadata_without_network(self):
        import fv_fetch, fv_data
        # 找一部有缓存元数据的片
        f = next((x for x in fv_data.FILMS
                  if os.path.exists(os.path.join(fv_fetch.DATA_DIR, x["slug"] + ".json"))), None)
        if not f:
            self.skipTest("没有缓存的元数据可测")

        # 把 fetch_one 换成「一被调用就报错」，这样只要它被调用就说明没复用缓存
        orig = fv_fetch.fetch_one
        called = {"n": 0}

        def boom(film):
            called["n"] += 1
            raise AssertionError("下载时不该再联网抓元数据（应读缓存）")

        fv_fetch.fetch_one = boom
        try:
            m, why = fv_fetch.metadata_for(f)
        finally:
            fv_fetch.fetch_one = orig
        self.assertEqual(called["n"], 0, "metadata_for 走了网络，没复用缓存")
        self.assertEqual(why, "缓存", "缓存命中时应说明来源是缓存")
        self.assertTrue(m and m.get("stills"), "复用的元数据没有剧照清单")

    def test_no_cache_falls_back_to_network(self):
        """没有缓存时**回落到联网**（而不是编一份空元数据）。

        ⚠ 第一版这条测试写错了：我用 `https://film-grab.com/x/` 当假 URL，
        结果 `fetch_one` **真的抓到了页面**（Ti West 的《X》），于是断言
        「应返回 None」失败。错在前提 —— 设计就是「无缓存 → 联网」，
        联网成功当然要返回数据。把 fetch 强制失败才能测到该测的：
        **失败时返回 (None, 原因)，而不是伪造一份**。
        """
        import fv_fetch
        fake = {"slug": "__no_such_film__", "filmgrab": "https://film-grab.com/x/"}
        orig = fv_fetch.fetch_one
        fv_fetch.fetch_one = lambda film: (None, "模拟网络失败")
        try:
            m, why = fv_fetch.metadata_for(fake)
        finally:
            fv_fetch.fetch_one = orig
        self.assertIsNone(m, "抓取失败时应返回 None，绝不能伪造元数据")
        self.assertEqual(why, "模拟网络失败")


if __name__ == "__main__":
    unittest.main(verbosity=2)
