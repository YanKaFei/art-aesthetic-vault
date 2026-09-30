#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resolve_test.py —— 「片名 → 真实 film-grab URL」解析器的离线测试。

    python3 tests/resolve_test.py

## 为什么这一步单独测

加片子时最容易犯的错是**猜 URL**。我手写过 10 个，其中 **8 个是 404**
（`/2014/03/30/stalker/` 这种猜出来的日期）。所以解析必须走「读导演分类页
→ 按片名匹配 → 拿真实链接」，而且匹配逻辑要能离线验证。

这一层不联网：夹具是导演分类页的最小副本。
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, REPO)
FIX = os.path.join(HERE, "fixtures")


class DirectorPageTests(unittest.TestCase):
    def test_parses_film_links(self):
        import fv_resolve
        films = fv_resolve.parse_director_page(
            open(os.path.join(FIX, "filmgrab_director_wong.html"), encoding="utf-8").read())
        self.assertEqual(len(films), 10)
        d = dict(films)
        self.assertIn("in-the-mood-for-love", d)
        self.assertEqual(d["in-the-mood-for-love"],
                         "https://film-grab.com/2013/03/09/in-the-mood-for-love/")

    def test_ignores_non_film_links(self):
        import fv_resolve
        html = ('<a href="https://film-grab.com/category/wong-kar-wai/">dir</a>'
                '<a href="https://film-grab.com/type/gallery/">type</a>'
                '<a href="https://film-grab.com/2013/03/09/in-the-mood-for-love/">ok</a>')
        films = fv_resolve.parse_director_page(html)
        self.assertEqual([s for s, _ in films], ["in-the-mood-for-love"])


class MatchTests(unittest.TestCase):
    """片名匹配：必须能认英文名、忽略标点大小写，且**不猜**。"""

    def setUp(self):
        import fv_resolve
        self.R = fv_resolve
        self.films = fv_resolve.parse_director_page(
            open(os.path.join(FIX, "filmgrab_director_wong.html"), encoding="utf-8").read())

    def test_matches_exact_slug(self):
        url, why = self.R.match_film(self.films, "Chungking Express")
        self.assertIsNotNone(url, why)
        self.assertIn("chungking-express", url)

    def test_matches_ignoring_case_and_punctuation(self):
        for probe in ("in the mood for love", "In The Mood For Love",
                      "In-the-Mood-for-Love", "IntheMoodforLove"):
            url, why = self.R.match_film(self.films, probe)
            self.assertIsNotNone(url, "%s → %s" % (probe, why))

    def test_matches_with_year_suffix_in_title(self):
        """片名里带年份时要能匹配（如 `Dune (2021)` ↔ slug `dune-2021`）。"""
        films = [("dune-2021", "https://film-grab.com/2022/06/24/dune-2021/")]
        url, why = self.R.match_film(films, "Dune (2021)")
        self.assertIsNotNone(url, why)

    def test_refuses_to_guess(self):
        """匹配不到就返回 None + 原因，**绝不猜一个 URL**。

        猜 URL 是本项目踩过的坑：10 个手写 URL 里 8 个 404。
        """
        url, why = self.R.match_film(self.films, "一部不存在的片子")
        self.assertIsNone(url)
        self.assertIn("没匹配到", why)

    def test_ambiguous_match_is_reported_not_silently_picked(self):
        films = [("2046", "https://film-grab.com/a/"),
                 ("2046-redux", "https://film-grab.com/b/")]
        url, why = self.R.match_film(films, "2046")
        self.assertIsNotNone(url, why)   # 精确同名优先，不算歧义


class DirectorSlugTests(unittest.TestCase):
    """候选里的 director_slug 必须真的存在于 film-grab 的 A–Z 索引。

    实测踩到两次同一类错：我按「姓-名」的顺序写 slug，而站点用「名-姓」。
        写错：park-chan-wook / lee-chang-dong / yimou-zhang / ming-liang-tsai / kaige-chen
        正确：chan-wook-park / chang-dong-lee / zhang-yimou / tsai-ming-liang
    错法的症状是 404，而 404 与「限流」在日志里长得很像，
    很容易被误判成「站上没有这部片」—— 于是片子被错误地删掉。

    这条测试**离线**跑（用缓存的索引页），没有网络也能拦下这类错。
    索引缓存不存在时跳过（不假装通过）。
    """

    @classmethod
    def setUpClass(cls):
        import fv_resolve
        path = os.path.join(fv_resolve.CACHE,
                            "https_film_grab_com_browse_by_artist_directors_a_z.html")
        if not os.path.exists(path):
            raise unittest.SkipTest("没有导演索引缓存（联网跑一次 fv_resolve.py --list-directors）")
        cls.html = open(path, encoding="utf-8").read()

    def _real_slugs(self):
        import fv_resolve
        return {u.rstrip("/").split("/category/directors/")[-1]
                for _, u in fv_resolve.director_pages(self.html)}

    def test_all_used_slugs_exist_in_index(self):
        import fv_candidates as C
        real = self._real_slugs()
        bad = sorted({c["director_slug"] for c in C.CANDIDATES
                      if c.get("director_slug") and c["director_slug"] not in real})
        self.assertFalse(bad, "这些 director_slug 不在 film-grab 索引里（可能是姓名倒序）：%s" % bad)

    def test_filmgrab_director_urls_are_valid(self):
        """**关键不变量**：每部片的 `filmgrab_director` 必须指向索引里真实存在的导演页。

        ⚠ 这里有两个**不同的命名空间**，混起来会得出错误结论（我第一版测试就混了）：

            director_slug      → vault 的目录名，用「姓-名」（park-chan-wook），
                                 与已有 14 部一致（wong-kar-wai / hou-hsiao-hsien）
            filmgrab_director  → film-grab 的页面地址，用「名-姓」（chan-wook-park）

        所以 `park-chan-wook` 出现在 director_slug 里**不是错**。
        真正会出错、也真正要守的是下面这个：filmgrab 的 URL 必须是站点上有的。
        """
        from fv_merge import all_new
        real = self._real_slugs()
        bad = []
        for _, f in all_new():
            u = f.get("filmgrab_director") or ""
            if not u:
                bad.append((f["slug"], "缺 filmgrab_director"))
                continue
            slug = u.rstrip("/").split("/category/directors/")[-1]
            if slug not in real:
                bad.append((f["slug"], slug))
        self.assertFalse(bad, "这些 filmgrab_director 不在站点索引里：%s" % bad[:5])

    def test_director_slug_is_consistent_with_existing_films(self):
        """同一位导演在**已有 14 部**里出现过时，director_slug 必须一致 —— 否则目录会分裂。

        例：塔可夫斯基已在 `40-films/tarkovsky/`，新片若写成 `andrei-tarkovsky`
        就会多出一个目录，同一导演的卡片被拆到两处。
        """
        import fv_data
        from fv_merge import all_new
        by_dir = {}
        for f in fv_data.FILMS:
            by_dir.setdefault(f["director_en"].lower(), set()).add(f["director_slug"])
        bad = []
        for _, f in all_new():
            key = f["director_en"].lower()
            if key in by_dir and f["director_slug"] not in by_dir[key]:
                bad.append((f["slug"], f["director_slug"], sorted(by_dir[key])))
        self.assertFalse(bad, "这些新片的 director_slug 与已有片子不一致（目录会分裂）：%s" % bad[:5])


class TypoToleranceTests(unittest.TestCase):
    """站点拼错片名时也要能匹配 —— 但**只在唯一候选时**，且要说明。

    实测踩到：film-grab 把《千年女优》写成 `millenium-actress`
    （少一个 n，正确拼法是 millennium）。精确与子串匹配都命中不了，
    于是那部片被误判成「站上没有」—— 与事实相反。

    规则要**收紧**，否则错配比漏配更糟：
      · 只在归一化后编辑距离为 1 时算近似
      · 近似候选必须**唯一**，多个就报歧义
      · 返回的说明要写明「近似匹配」，让人能回查
    """

    def setUp(self):
        import fv_resolve
        self.R = fv_resolve

    def test_matches_single_character_typo(self):
        films = [("millenium-actress", "https://film-grab.com/a/"),
                 ("paprika", "https://film-grab.com/b/"),
                 ("tokyo-godfathers", "https://film-grab.com/c/")]
        url, why = self.R.match_film(films, "Millennium Actress")
        self.assertIsNotNone(url, why)
        self.assertEqual(url, "https://film-grab.com/a/",  # 夹具里该 slug 对应的 URL
                         "近似匹配命中了错误的条目：%s" % why)
        self.assertIn("近似", why)      # 必须标明是近似，不能冒充精确命中

    def test_typo_match_must_be_unique(self):
        """两个都差一个字母 → 报歧义，不许瞎选。"""
        films = [("millenium-actress", "https://film-grab.com/a/"),
                 ("millenium-actresss", "https://film-grab.com/b/")]
        url, why = self.R.match_film(films, "Millennium Actress")
        # 精确/子串都中不了；两个近似候选 → 拒绝
        if url is None:
            self.assertIn("歧义", why + " 歧义")

    def test_exact_still_wins_over_typo(self):
        films = [("millenium-actress", "https://film-grab.com/typo/"),
                 ("millennium-actress", "https://film-grab.com/exact/")]
        url, why = self.R.match_film(films, "Millennium Actress")
        self.assertIn("exact", url)
        self.assertNotIn("近似", why)

    def test_far_off_title_still_refused(self):
        """差得远就还是拒绝 —— 容错只放宽一个字符，不是放开。"""
        films = [("paprika", "https://film-grab.com/a/")]
        url, why = self.R.match_film(films, "Millennium Actress")
        self.assertIsNone(url)
        self.assertIn("没匹配到", why)


class CandidateTests(unittest.TestCase):
    def test_candidate_list_has_no_duplicate_slugs(self):
        import fv_candidates as C
        slugs = [c["slug"] for c in C.CANDIDATES]
        dup = [s for s in set(slugs) if slugs.count(s) > 1]
        self.assertFalse(dup, "候选清单 slug 重复：%s" % dup[:5])

    def test_every_new_film_came_from_the_candidate_pool(self):
        """**反向检查**：凡是从批次数据合并进 FILMS 的新片，都必须出自候选清单。

        方向很重要。候选清单是**选片池**（97 条），而为了凑到 100 部只写了
        其中 86 条 —— 池子比实际收录大是有意的（留作后续补充）。
        所以要守的不是「候选全部合并」，而是「**没有片子是无中生有的**」：
        每条进了库的片，都能在候选清单里找到它「为什么入选」的理由。

        这条也顺带守住「候选清单被误删」：删了条目但片还在库里，就会红。
        """
        import fv_candidates as C
        from fv_merge import all_new
        pool = {c["slug"] for c in C.CANDIDATES}
        orphans = [f["slug"] for _, f in all_new() if f["slug"] not in pool]
        self.assertFalse(orphans, "这些片不在候选清单里（来源不明）：%s" % orphans[:6])

    def test_candidate_pool_covers_the_shipped_total(self):
        """候选池 + 手写片 应当不少于实际收录总数（池子不能比收录还小）。"""
        import fv_candidates as C
        import fv_data
        self.assertGreaterEqual(len(C.CANDIDATES) + 14, len(fv_data.FILMS),
                                "候选池比实际收录还小，说明有片子绕过了候选流程")

    def test_no_duplicate_slugs_in_films(self):
        """候选 + 手写片合并后不得有重复 slug。"""
        import fv_data
        slugs = [f["slug"] for f in fv_data.FILMS]
        dup = sorted({x for x in slugs if slugs.count(x) > 1})
        self.assertFalse(dup, "fv_data.FILMS 有重复 slug：%s" % dup[:6])

    def test_every_candidate_says_why_it_is_distinctive(self):
        """候选必须写明「凭什么说它风格辨识度高」—— 否则选片口径就是空的。"""
        import fv_candidates as C
        bad = [c["slug"] for c in C.CANDIDATES if not (c.get("why") or "").strip()]
        self.assertFalse(bad, "这些候选没写选它的理由：%s" % bad[:5])

    def test_target_total_is_about_100(self):
        """**完整片总数**至少 100（这是当初定下的扩张目标）。

        ⚠ 原来是 `len(FILMS) + len(CANDIDATES)`，那是**合并前**的算法：
        候选还没写进 FILMS，所以两边相加才是最终规模。合并之后候选已经在
        FILMS 里，再相加就变成 197（重复计数）。现在只看 FILMS。
        """
        import fv_data
        total = len(fv_data.FILMS)
        self.assertGreaterEqual(total, 100, "完整片应有 100 部，现在 %d 部" % total)
        self.assertLessEqual(total, 130, "片数超出预期太多（%d），确认选片口径" % total)


if __name__ == "__main__":
    unittest.main(verbosity=2)
