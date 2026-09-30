#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""film_test.py —— 电影风格库的单元测试。纯标准库。

    python3 tests/film_test.py          # 全跑
    python3 tests/film_test.py -v

## 这一层测什么、不测什么

测的是**能被 AI 调取**这件事本身的契约：
数据完整性（七层齐、配色六色、slug 唯一）、检索能否命中、
与艺术流派库的七层词表是否真的共用（跨源混搭的前提）、
以及版权隔离是否真的生效（本地图被 gitignore、卡里不嵌本地路径）。

不测网络：抓取器单独测，且网络测试在无网时必须跳过并说明原因，
不能把「没网」伪装成「通过」——这是本仓库踩过的坑（README 声称 654 张图，
实际只有 442 张，而那 15 项验收全在比文件、没有一项真的去跑命令）。
"""

import glob
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
VAULT = os.path.dirname(REPO)
sys.path.insert(0, REPO)
import fv_merge  # noqa: E402


class DataContractTests(unittest.TestCase):
    """数据层契约：fv_core 能不能把 fv_data 正确读成一等公民。"""

    def test_imports(self):
        import fv_core

    def test_loads_all_films(self):
        import fv_core
        films = fv_core.films()
        import fv_data
        self.assertEqual(len(films), len(fv_data.FILMS),
                         "fv_core 读到的片数与 fv_data.FILMS 不一致")
        self.assertGreaterEqual(len(films), 100,
                                "完整片目标 100 部；现在只有 %d 部" % len(films))
        self.assertGreaterEqual(len(fv_core.directors()), 8)

    def test_seven_layers_shared_with_artvault(self):
        """电影卡必须和艺术流派卡共用同一套七层词表。

        这不是形式要求：artvault.py compose 的跨源混搭
        （「王家卫的光照 + 巴洛克的构图」）靠的就是两边层名一致。
        电影自己另造一套层名，compose 就拼不起来。
        """
        import artvault_core as A
        import fv_core
        self.assertEqual(sorted(fv_core.LAYERS), sorted(A.LAYERS))

    def test_every_film_has_seven_layers(self):
        import fv_core
        for f in fv_core.films():
            for layer in fv_core.LAYERS:
                self.assertTrue(f["layers"].get(layer, "").strip(),
                                "%s 缺层：%s" % (f["slug"], layer))

    def test_every_film_has_six_colors(self):
        import fv_core
        for f in fv_core.films():
            self.assertEqual(len(f["palette"]), 6,
                             "%s 配色应为 6 色" % f["slug"])
            for hexv, name in f["palette"]:
                self.assertRegex(hexv, r"^#[0-9A-Fa-f]{6}$")
                self.assertTrue(name.strip())

    def test_slugs_unique_and_url_safe(self):
        import fv_core
        seen = set()
        for f in fv_core.films():
            self.assertNotIn(f["slug"], seen, "slug 重复：%s" % f["slug"])
            seen.add(f["slug"])
            self.assertRegex(f["slug"], r"^[a-z0-9-]+$")

    def test_director_slug_unique_per_name(self):
        """导演 slug 不能一名对多 slug（否则目录会分裂成两个）。"""
        import fv_core
        m = {}
        for f in fv_core.films():
            m.setdefault(f["director_zh"], set()).add(f["director_slug"])
        for name, slugs in m.items():
            self.assertEqual(len(slugs), 1, "%s 对应多个 slug：%s" % (name, slugs))

    def test_positive_prompt_assembled(self):
        """没有手写 positive 时，由六层自动拼（不含镜头层）。"""
        import fv_core
        for f in fv_core.films():
            self.assertTrue(f["positive"].strip(), "%s 正向提示词为空" % f["slug"])
            self.assertGreater(len(f["positive"]), 60)

    def test_negative_prompt_present(self):
        import fv_core
        for f in fv_core.films():
            self.assertTrue(f["negative"].strip(), "%s 缺负向提示词" % f["slug"])

    def test_source_flagged(self):
        """证据强度必须标出来：curated / inferred 不能被含糊掉。"""
        import fv_core
        for f in fv_core.films():
            self.assertIn(f["source"], ("curated", "inferred"),
                          "%s 的 source 不合法：%r" % (f["slug"], f["source"]))


class LookupTests(unittest.TestCase):
    """检索与解析：AI 要能按导演、按片名、按风格描述找到片子。"""

    def test_resolve_by_slug(self):
        import fv_core
        f, hints = fv_core.resolve("wong-kar-wai-in-the-mood-for-love")
        self.assertIsNotNone(f)
        self.assertEqual(f["title_zh"], "花样年华")

    def test_resolve_by_chinese_title(self):
        import fv_core
        f, hints = fv_core.resolve("花样年华")
        self.assertIsNotNone(f)

    def test_resolve_by_english_title(self):
        import fv_core
        f, hints = fv_core.resolve("Chungking Express")
        self.assertIsNotNone(f)
        self.assertEqual(f["year"], 1994)

    def test_resolve_ignores_spaces_in_titles(self):
        """回归：片名里的空格是排版细节，不该决定查找成败。

        实际踩到 —— 文档里写的 `film layers 银翼杀手2049` 直接报「没找到」，
        因为库里的片名是「银翼杀手 2049」。同一部片，只差一个空格。
        空格、中点、连字符、全角括号都做归一化。
        """
        import fv_core
        # 只锁**空白/标点**的差异。简繁转换（銀翼殺手）不在本次范围内 ——
        # 那需要一张映射表，而这里不该假装已经支持了。
        for probe in ("银翼杀手2049", "银翼杀手 2049", "银翼杀手2049 ",
                      "BladeRunner2049", "blade runner 2049"):
            f, _ = fv_core.resolve(probe)
            self.assertIsNotNone(f, "解析不了：%r" % probe)
            self.assertEqual(f["slug"], "villeneuve-blade-runner-2049")

    def test_resolve_still_refuses_unknown_titles(self):
        """归一化不能把「找不到」变成「随便给一个」。"""
        import fv_core
        f, hints = fv_core.resolve("完全不存在的一部片子zzz")
        self.assertIsNone(f)

    def test_resolve_gives_hints_not_silent_wrong_answer(self):
        """问一个不存在的片子必须返回 None + 候选，不能静默给一张别的卡。

        本库踩过：search() 是全文检索，show 一个不存在的名字会命中
        某张卡正文里的那个词，于是「问 A 得到 B」。
        """
        import fv_core
        f, hints = fv_core.resolve("不存在的电影名xyz")
        self.assertIsNone(f)
        self.assertIsInstance(hints, list)

    def test_search_by_style_words(self):
        """描述性检索要能命中——这是「未来 AI 来调取风格」的主路径。"""
        import fv_core
        r = fv_core.search("霓虹 雨夜")
        self.assertTrue(r, "「霓虹 雨夜」应至少命中一部")
        slugs = [x["slug"] for x in r]
        self.assertIn("wong-kar-wai-chungking-express", slugs)

    def test_search_by_director(self):
        import fv_core
        r = fv_core.search("王家卫")
        self.assertEqual(len(r), 2)

    def test_search_by_technique(self):
        """技术词要能搜到片。

        ⚠ 断言「必须在结果里」而非「必须是第一名」：片子从 14 增到 100 后，
        `bleach bypass` 同时命中了《七宗罪》与《搏击俱乐部》（两部都真用了
        漂白工艺），第一名换了。断言具体名次会让测试随片库增长而假红 ——
        要守的是「搜得到」，不是「谁排第一」。
        """
        import fv_core
        r = fv_core.search("bleach bypass")
        slugs = [x["slug"] for x in r]
        self.assertIn("fincher-se7en", slugs,
                      "搜 bleach bypass 找不到用了漂白工艺的《七宗罪》：%s" % slugs[:5])

    def test_layers_only_returns_layers(self):
        import fv_core
        f, hints = fv_core.resolve("villeneuve-dune")
        L = fv_core.layers(f)
        self.assertEqual(set(L), set(fv_core.LAYERS))

    def test_related_movements_resolve_in_artvault(self):
        """电影卡里 see_also 引用的艺术流派 slug，必须在艺术库里真的存在。

        否则生成出来的 [[双链]] 是断链，verify_vault 会挂。
        """
        import artvault_core as A
        import fv_core
        for f in fv_core.films():
            for slug in f.get("see_also", []):
                self.assertIsNotNone(
                    A.by_slug().get(slug),
                    "%s 的关联流派 %s 在艺术库里不存在（会成为断链）"
                    % (f["slug"], slug))


class CopyrightIsolationTests(unittest.TestCase):
    """剧照的版权处理 —— 策略**已反转**，这里记录反转后的契约。

    ## 反转留档

    原来这一类的名字叫「版权隔离」，契约是：本地剧照 gitignore、卡片只记外链。
    用户要求「把画面放入卡片」后改成**本地嵌入**（Obsidian 的 `![[库内路径]]`
    只认本地文件，外链在库内不会渲染成图）。

    所以现在的契约变成三条：

      1. 剧照目录**不再 gitignore** —— 图必须随仓库走，否则别人 clone 全是断图
      2. 卡片必须带**版权声明**（版权属原片方，公开分发前自行判断）
      3. 嵌入的每一张**必须真实存在**，且外链仍保留以便回查来源
    """

    IMG_DIR = os.path.join(VAULT, "99-attachments", "images-films")

    def test_embedded_stills_are_tracked_and_corpus_is_ignored(self):
        """嵌入的剧照要在 **git 索引**里；语料目录要被忽略。

        ⚠ 契约换过一次方向，值得记下：
          旧写法断言「嵌入的图能被**普通** `git add` 加进去」（即不被忽略）。
          那对应「逐文件列出 797 条忽略」的方案。
          现在 `.gitignore` 瘦身成**整目录一行忽略** + 对嵌入的那批 `git add -f`，
          于是嵌入的图**是被忽略的**（普通 add 会报 ignored），但**已在索引里**。
          文件一旦被跟踪，gitignore 就管不着它 —— 所以真正要守的是
          「在索引里」，而不是「add 得进去」。
        """
        if not os.path.isdir(os.path.join(VAULT, ".git")):
            self.skipTest("不是 git 工作树")
        import fv_build, fv_core
        picked = []
        for slug in ("kubrick-the-shining", "villeneuve-dune", "fincher-se7en"):
            f, _ = fv_core.resolve(slug)
            md = fv_build.film_note(f)
            picked += [r for r in re.findall(r"!\[\[([^\]|]+\.(?:jpe?g|png|webp))", md, re.I)
                       if r.startswith("99-attachments/images-films/")]
        self.assertTrue(picked, "没有解析出嵌入的剧照")

        tracked = subprocess.run(["git", "ls-files", "--"] + sorted(set(picked)),
                                 cwd=VAULT, capture_output=True, text=True).stdout.split()
        missing = sorted(set(picked) - set(tracked))
        self.assertFalse(missing,
                         "这些嵌入的剧照不在 git 索引里（clone 后是断图）：%s\n"
                         "跑 `python3 .repo/build_vault.py` 会自动 git add -f" % missing[:3])

        # 语料（非嵌入的）必须被忽略，否则 160 MB 全进仓库
        corpus = [os.path.relpath(p, VAULT)
                  for p in glob.glob(os.path.join(self.IMG_DIR, "**", "*.jpg"), recursive=True)
                  if os.path.relpath(p, VAULT) not in set(picked)]
        if corpus:
            r = subprocess.run(["git", "add", "--dry-run"] + corpus[:20],
                               cwd=VAULT, capture_output=True, text=True)
            self.assertIn("ignored", (r.stderr + r.stdout).lower(),
                          "语料没被忽略 —— 160 MB 会全进仓库")

    def test_cards_embed_stills_with_copyright_notice(self):
        """嵌了版权图就必须声明 —— 反转策略的前提条件，不是可选装饰。"""
        import fv_build, fv_core
        f, _ = fv_core.resolve("kubrick-the-shining")
        md = fv_build.film_note(f)
        self.assertIn("![[99-attachments/images-films/", md)
        self.assertIn("版权属原片方", md)
        self.assertIn("商用", md)
        self.assertIn("commercial", md.lower())

    def test_every_embedded_still_exists(self):
        """嵌入的图必须真的在盘上 —— 否则 Obsidian 里是红叉，
        而所有「检查卡片文本」的测试都会照常通过（这条就是为它写的）。"""
        import fv_build, fv_core
        for slug in ("kubrick-the-shining", "villeneuve-dune", "fincher-se7en"):
            f, _ = fv_core.resolve(slug)
            md = fv_build.film_note(f)
            for rel in re.findall(r"!\[\[([^\]|]+\.(?:jpe?g|png|webp))", md, re.I):
                self.assertTrue(os.path.exists(os.path.join(VAULT, rel)),
                                "卡片嵌入了不存在的图：%s" % rel)

    def test_measurement_pages_do_not_embed(self):
        """实测页**不嵌图**（它是数字页，嵌图会把表格冲散）；卡片才是看图的地方。"""
        d = os.path.join(VAULT, "40-films")
        for p in glob.glob(os.path.join(d, "*", "*-实测.md")):
            t = open(p, encoding="utf-8").read()
            self.assertNotIn("![[99-attachments/images-films/", t,
                             "%s 嵌了剧照（实测页不嵌图）" % os.path.basename(p))


class GitignoreHygieneTests(unittest.TestCase):
    """`.gitignore` 要短，而卡片嵌入的剧照要**真的被跟踪**。

    ## 背景：为什么曾经膨胀到 900 行

    git 的规则是「父目录被排除时，无法再 `!` 重新包含其中的文件」。所以
    想「整目录忽略 + 只保留嵌入的那几张」时，`dir/*` + `!dir/file` 的写法
    **不生效**（实测 `git add` 报 "paths are ignored"）。当时我的解法是
    逐文件列出 797 条要忽略的路径 —— 能用，但：

      · `.gitignore` 涨到 900 行，人已经读不动
      · 那份清单依赖「当前嵌了哪 84 张」，换代表帧就会漂移

    更好的办法：**整目录一行忽略，嵌入的那几张用 `git add -f` 强制入库**。
    文件一旦被跟踪，gitignore 就管不着它了 —— 所以规则可以只有一行，
    且不需要随代表帧变化而改写。
    """

    def test_gitignore_stays_short(self):
        gi = os.path.join(VAULT, ".gitignore")
        lines = open(gi, encoding="utf-8").read().splitlines()
        self.assertLess(len(lines), 220,
                        ".gitignore 有 %d 行 —— 又膨胀了（应该只有一条剧照规则）" % len(lines))

    def test_embedded_frames_are_tracked(self):
        """嵌入的每一张都必须在 git 索引里，否则 clone 后是断图。"""
        if not os.path.isdir(os.path.join(VAULT, ".git")):
            self.skipTest("不是 git 工作树")
        emb = set()
        for p in glob.glob(os.path.join(VAULT, "40-films", "**", "*.md"), recursive=True):
            emb |= set(re.findall(r"!\[\[([^\]|]+\.(?:jpe?g|png|webp))",
                                  open(p, encoding="utf-8").read(), re.I))
        emb = {e for e in emb if e.startswith("99-attachments/images-films/")}
        if not emb:
            self.skipTest("还没有嵌入的剧照")
        tracked = subprocess.run(["git", "ls-files"] + sorted(emb),
                                 cwd=VAULT, capture_output=True, text=True).stdout.split()
        missing = sorted(emb - set(tracked))
        self.assertFalse(missing,
                         "这些嵌入的剧照没被 git 跟踪（clone 后是断图）：%s\n"
                         "跑 `python3 build_vault.py` 会自动 git add -f 它们" % missing[:4])

    def test_corpus_directory_is_ignored(self):
        """语料目录整体必须被忽略 —— 否则 160 MB 全进仓库。"""
        gi = open(os.path.join(VAULT, ".gitignore"), encoding="utf-8").read()
        active = [l.strip() for l in gi.splitlines()
                  if l.strip() and not l.strip().startswith("#")]
        self.assertIn("99-attachments/images-films/", active,
                      "语料目录没有被忽略")


class DirectorSlugUniquenessTests(unittest.TestCase):
    """一位导演只能有**一个** director_slug。

    实测踩到：`edward-yang` 与 `yang`、`kobayashi` 与 `masaki-kobayashi`、
    `antonioni` 与 `michelangelo-antonioni` 同时存在 —— 那是写片子时
    一会儿用全名、一会儿用简称造成的。后果是 `40-films/` 下同一位导演
    出现两个目录，卡片被拆开，导演索引页也只列到其中一半。

    这个错不会让任何检查变红：卡片照样生成、链接照样有效，只是**分散**了。
    所以必须专门守。
    """

    def test_one_slug_per_director(self):
        import fv_data
        import collections
        by = collections.defaultdict(set)
        for f in fv_data.FILMS:
            by[f["director_en"]].add(f["director_slug"])
        bad = {k: sorted(v) for k, v in by.items() if len(v) > 1}
        self.assertFalse(bad, "同一位导演有多个 director_slug（会拆目录）：%s" % bad)

    def test_director_count_matches_unique_names(self):
        """director_index() 的组数必须等于不同导演名的个数。"""
        import fv_data
        self.assertEqual(len(fv_data.director_index()),
                         len({f["director_en"] for f in fv_data.FILMS}),
                         "director_index 把同一位导演分成了多组")


class MergeIdempotencyTests(unittest.TestCase):
    """`fv_merge.py --merge` 必须**可重复**而不产生重复片。

    失败模式：如果合并是「往 FILMS 末尾追加」，第二次跑就会让每部片出现
    两遍 —— 而下游（卡片生成、检索、统计）全都会照常工作，只是数字悄悄翻倍。
    这类错最难查，所以这里用标记块 + 一条守门测试钉死。
    """

    def test_no_duplicate_slugs_in_films(self):
        import fv_data
        slugs = [f["slug"] for f in fv_data.FILMS]
        dup = sorted({x for x in slugs if slugs.count(x) > 1})
        self.assertFalse(dup, "fv_data.FILMS 里有重复 slug（合并被跑了两次？）：%s" % dup[:6])

    def test_films_have_unique_titles_per_director(self):
        """同一导演下不应有两部同名片 —— 那也是重复合并的症状。"""
        import fv_data
        seen = {}
        dup = []
        for f in fv_data.FILMS:
            k = (f["director_slug"], f["title_zh"])
            if k in seen:
                dup.append(k)
            seen[k] = 1
        self.assertFalse(dup, "同一导演下有重复片名：%s" % dup[:5])

    def test_merge_block_is_single_and_wellformed(self):
        """标记块只能有一个 BEGIN/END 对。"""
        src = open(os.path.join(REPO, "fv_data.py"), encoding="utf-8").read()
        self.assertEqual(src.count(fv_merge.BEGIN.strip()), 1,
                         "BEGIN 标记不是恰好一个 —— 合并块被写坏了")
        self.assertEqual(src.count(fv_merge.END.strip()), 1,
                         "END 标记不是恰好一个")

    def test_every_batch_film_is_present_in_films(self):
        """批次里的每一部都要真的进了 FILMS（不能漏）。"""
        import fv_data
        have = {f["slug"] for f in fv_data.FILMS}
        missing = [f["slug"] for _, f in fv_merge.all_new() if f["slug"] not in have]
        self.assertFalse(missing, "这些新片没合并进 FILMS：%s" % missing[:6])


if __name__ == "__main__":
    unittest.main(verbosity=2)
