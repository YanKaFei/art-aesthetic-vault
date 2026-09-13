#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_test.py —— 端到端冒烟测试。纯标准库，不需要 pip 装任何东西。

    python3 tests/smoke_test.py            # 全部
    python3 tests/smoke_test.py -v         # 逐条
    python3 tests/smoke_test.py HelpSafety # 只跑某一类

## 为什么要有这一层（和 verify_vault.py 是什么关系）

两者查的东西**不重叠**：

    verify_vault.py   查内容一致性 —— 断链、重名、授权字段、README 数字、双链
    smoke_test.py     把命令**真的跑一遍** —— 退出码、输出结构、副作用、可复现性

分这层是因为踩过一个很贵的坑：README 声称「654 张公共领域实图」，克隆下来只有
442 张，而这个 bug 穿过了当时全部 15 项验收。原因是那 15 项**都在读文件**
（比 mtime、比引用、比数字），没有任何一项会问一句：

    把这些命令跑一遍，会不会出事？工作树会不会被弄脏？

所以这里的每条测试都必须**真的执行**命令，不能只 import 一下。宁可慢几秒。

## 三条设计约束

1. **零依赖**：只用标准库。CI 上不 pip install 任何东西，这样环境差异不会伪装成
   代码问题。（可选依赖缺失是合法状态，见 OptionalDegradationTests。）
2. **能本地跑，也能在 CI 跑**：CI 是干净的 checkout，本地可能是脏的工作树 ——
   涉及工作树的测试在脏树上**跳过并说明原因**，不假装通过。
3. **不制造垃圾**：所有命令都在临时目录或原地无副作用地跑；改工作树的测试
   跑完要能证明工作树回到原样。
"""

import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
SCRIPTS = os.path.join(VAULT, "_scripts")
PY = sys.executable or "python3"

# 单个命令的超时。--help 类的应当秒回；给足余量但不允许无限挂起。
TIMEOUT = 60


# --------------------------------------------------------------------- 工具

def run(args, timeout=TIMEOUT, stdin_text=None, cwd=None):
    """跑一个子进程，返回 (returncode, stdout, stderr)。"""
    try:
        p = subprocess.run([PY] + args, capture_output=True, text=True,
                           timeout=timeout, input=stdin_text,
                           cwd=cwd or SCRIPTS)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT after %ss" % timeout


def git_status():
    """工作树状态（不含未跟踪文件的噪音时也一并返回，交给调用方判断）。"""
    try:
        p = subprocess.run(["git", "-c", "core.quotepath=false",
                            "status", "--porcelain"],
                           capture_output=True, text=True, cwd=VAULT, timeout=60)
        return p.stdout
    except Exception as e:
        return "GIT-FAILED: %s" % e


def is_dirty(status_text):
    """把「已知的、与代码无关」的条目排除后，是否还有改动。"""
    for line in (status_text or "").splitlines():
        s = line.strip()
        if not s:
            continue
        # 用户自己放在仓库根的手写草稿，不属于生成物
        if s == "?? 此处放图.md":
            continue
        return True
    return False


def script_names():
    return sorted(f[:-3] for f in os.listdir(SCRIPTS)
                  if f.endswith(".py") and not f.startswith("_"))


def entry_scripts():
    """有 `if __name__ == "__main__":` 的脚本 —— 这些才谈得上「跑起来」。"""
    out = []
    for n in script_names():
        try:
            t = open(os.path.join(SCRIPTS, n + ".py"), encoding="utf-8").read()
        except Exception:
            continue
        if re.search(r'^if __name__ == "__main__":', t, re.M):
            out.append(n + ".py")
    return out


def has_module(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False


def a_real_image():
    """仓库里任意一张真图。

    不能用 README.md 冒充图片：脚本会先撞「不是图片」再撞「缺 Pillow」，
    测试就测错了东西（第一版就是这么写错的）。
    """
    root = os.path.join(VAULT, "99-附件", "images")
    for dirpath, _dirnames, filenames in os.walk(root):
        for f in sorted(filenames):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                return os.path.join(dirpath, f)
    return None


# ------------------------------------------------- 1. 入口安全：--help 不许出事

class HelpSafetyTests(unittest.TestCase):
    """每个入口的 `--help` 必须是安全的：退出 0、无 traceback、不动工作树。

    这条测试是有来历的 —— 修复前：

        python3 build_vault.py --help    → 真的重建了整个仓库
        python3 fetch_art.py --help      → 真的开始联网抓图
        python3 mcp_server.py --help     → 真的起了 stdio 服务，卡住不返回
        python3 image_analysis_ext.py --help → ModuleNotFoundError traceback

    帮助是最没有破坏性的参数，读者拿到陌生仓库第一个试的就是它。
    """

    def test_every_entry_help_is_safe(self):
        before = git_status()
        bad = []
        for name in entry_scripts():
            rc, out, err = run([name, "--help"], timeout=45)
            blob = out + err
            why = None
            if rc == 124:
                why = "挂起不返回（--help 触发了真实动作）"
            elif rc != 0:
                why = "退出码 %s" % rc
            elif "Traceback (most recent call last)" in blob:
                why = "抛了 traceback"
            elif not blob.strip():
                why = "什么都没打印"
            if why:
                bad.append("%s: %s" % (name, why))
        self.assertEqual([], bad, "这些入口的 --help 不安全：\n  " + "\n  ".join(bad))

    def test_help_does_not_touch_worktree(self):
        before = git_status()
        for name in entry_scripts():
            run([name, "--help"], timeout=45)
        after = git_status()
        self.assertEqual(before, after,
                         "有入口的 --help 改动了工作树 —— 帮助不该有副作用")


# --------------------------------------------------- 2. 核心检索：能跑、结构对

class CoreCommandTests(unittest.TestCase):
    """README 里承诺的命令得真的能跑，并给出承诺的结构。

    这些是使用者抄进终端的第一批命令，坏了整个产品就不成立。
    """

    def _json(self, args):
        rc, out, err = run(["artvault.py", "--json"] + args)
        self.assertEqual(0, rc, "artvault.py --json %s 失败：%s" % (args, err[-400:]))
        return json.loads(out)

    def test_categories(self):
        data = self._json(["categories"])
        self.assertTrue(isinstance(data, (list, dict)) and data)
        self.assertGreaterEqual(len(data), 6, "分类数不该少于 6")

    def test_search_finds_something(self):
        data = self._json(["search", "霓虹 雨夜"])
        self.assertTrue(data, "「霓虹 雨夜」不该一条都搜不到")

    def test_layers_has_seven(self):
        data = self._json(["layers", "巴洛克"])
        text = json.dumps(data, ensure_ascii=False)
        for layer in ("style", "lighting", "color"):
            self.assertIn(layer, text, "七层里缺 %s" % layer)

    def test_palette_six_colors(self):
        rc, out, _ = run(["artvault.py", "palette", "赛博朋克"])
        self.assertEqual(0, rc)
        self.assertEqual(6, len(re.findall(r"#[0-9A-Fa-f]{6}", out)),
                         "配色应当是六色")

    def test_show_and_related(self):
        for args in (["show", "浮世绘"], ["related", "立体主义"]):
            rc, out, err = run(["artvault.py"] + args)
            self.assertEqual(0, rc, "%s 失败：%s" % (args, err[-300:]))
            self.assertTrue(out.strip())

    def test_dump_is_valid_json(self):
        """dump 的条数必须等于 cards() 的条数 —— 而且**不写死数字**。

        第一版这里写死了 141。图谱对账补了 6 张卡之后它立刻失败 ——
        这正说明硬编码的数字会烂掉（README 的统计数字吃过同款亏）。
        改成跟数据源比，补卡时不会再假报错。
        """
        sys.path.insert(0, SCRIPTS)
        import artvault_core as A
        rc, out, err = run(["artvault.py", "dump", "--json"])
        self.assertEqual(0, rc, err[-300:])
        data = json.loads(out)
        self.assertEqual(len(A.cards()), len(data),
                         "dump 条数和 cards() 不一致")
        self.assertGreaterEqual(len(data), 141, "卡片数不该少于 141")

    def test_json_flag_works_on_both_sides_of_the_command(self):
        """`--json` 放命令前、放命令后都要能用。

        帮助里写的是「加 --json 到任意命令」，使用者自然会写在后面；
        而原来只在顶层 parser 定义了它，`artvault.py dump --json` 直接报
        「unrecognized arguments」。这条测试就是那次修复的守卫。
        """
        for args in (["--json", "categories"], ["categories", "--json"],
                     ["--json", "layers", "巴洛克"], ["layers", "巴洛克", "--json"]):
            rc, out, err = run(["artvault.py"] + args)
            self.assertEqual(0, rc, "`%s` 失败：%s" % (" ".join(args), err[-200:]))
            json.loads(out)          # 两处都必须是合法 JSON

    def test_json_absent_still_prints_human_text(self):
        rc, out, _ = run(["artvault.py", "categories"])
        self.assertEqual(0, rc)
        with self.assertRaises(Exception):
            json.loads(out)          # 不带 --json 时不该是 JSON


class SemanticSearchTests(unittest.TestCase):
    """中文语义检索：过桥要通，且**搜得到的时候不许动关键词的结果**。

    CLIP 文本塔是纯英文的，中文直接喂进去等于随机（实测「赛博朋克 霓虹 雨夜」
    命中的是工笔重彩）。所以中间必须有一座中文视觉词 → 英文短语的桥。
    """

    def test_lexicon_bridges_core_visual_terms(self):
        sys.path.insert(0, SCRIPTS)
        import visual_lexicon as VL
        for w in ("霓虹", "明暗对照", "留白", "水墨", "厚涂", "压抑"):
            en, matched, _ = VL.to_english(w)
            self.assertTrue(en, "词表没覆盖 %s" % w)
        # 无视觉内容的串不该被硬编成英文
        self.assertEqual("", VL.to_english("今天天气不错")[0])

    def test_lexicon_prefers_longer_terms(self):
        """长词优先：否则「不对称」会被「对称」先吃掉、「无阴影」被「阴影」吃掉。"""
        sys.path.insert(0, SCRIPTS)
        import visual_lexicon as VL
        _, matched, _ = VL.to_english("不对称构图")
        self.assertIn("不对称", matched, "长词没优先，被短词吃了")
        _, matched2, _ = VL.to_english("无阴影平面")
        self.assertIn("无阴影", matched2, "长词没优先，被短词吃了")

    def test_search_semantic_flag_never_crashes(self):
        """有没有下模型都必须能跑 —— 语义是不可选增量，不该让 search 也坏。"""
        for q in ("霓虹雨夜的城市", "巴洛克", "a serene japanese woodblock print"):
            rc, out, err = run(["artvault.py", "search", q, "--semantic"])
            self.assertEqual(0, rc, "`search %s --semantic` 失败：%s" % (q, err[-300:]))
            self.assertNotIn("Traceback (most recent call last)", out + err)

    def test_semantic_never_displaces_keyword_hits(self):
        """零损失不变量：关键词 top-1 搜对的，加语义之后必须还是它。

        这是设计方案的核心（分档接管，不是分数融合）。融合那版实测 A 组
        从 99.3% 掉到 78.7%，这条测试就是防守它再犯。
        """
        sys.path.insert(0, SCRIPTS)
        import artvault_core as A
        try:
            import clip_match as CM
            if CM.text_matrix() is None:
                self.skipTest("没有 CLIP 模型，语义不生效（此时行为等于纯关键词）")
        except Exception:
            self.skipTest("CLIP 不可用")
        cards = A.cards()
        sample = cards[:: max(1, len(cards) // 20)][:20]
        worse = []
        for c in sample:
            q = (c.get("one_liner") or "").strip()
            if len(q) < 6:
                continue
            kw = [x["slug"] for x in A.search(q, limit=1, semantic=False)]
            se = [x["slug"] for x in A.search(q, limit=1, semantic=True)]
            if kw == [c["slug"]] and se != [c["slug"]]:
                worse.append(c["slug"])
        self.assertEqual([], worse,
                         "加语义后这些流派的自身查询被挤下去了：%s" % worse)


class I2vTests(unittest.TestCase):
    """图生视频：一张图进去，占位符必须被**这张图的**测量填掉。

    i2v 的价值全在这个「填掉」上 —— 退化成流派通用版不会报错，
    只会让每张同流派的图拿到一模一样的视频提示词，而使用者手里正拿着那张图。
    """

    def _analysis(self):
        """拿一份真图的分析结果；拿不到（缺 Pillow）就 skip 并说明。

        刻意**不用** `has_module("PIL")` 判断：脚本会自己往
        `_scripts/vendor/libs` 找 Pillow，测试进程 import 失败不代表脚本用不了。
        第一版就是这么写的，结果本机明明能跑却跳过两条测试 —— 假阴性。
        改成看行为：真的调一次分析，只有当它说缺 Pillow 时才跳过。
        """
        img = a_real_image()
        if not img:
            self.skipTest("仓库里没有图片")
        sys.path.insert(0, SCRIPTS)
        import image_analysis as IA
        ana = IA.analyze(img)
        if ana.get("error"):
            if "Pillow" in str(ana["error"]):
                self.skipTest("缺 Pillow，图片分析不可用")
            self.fail("分析真图失败：%s" % ana["error"])
        return img, ana

    def test_i2v_fills_placeholders(self):
        img, ana = self._analysis()
        import i2v_prompt as I2V
        r = I2V.build(None, ana)          # 连流派都不给也要能用
        blob = r["seedance"] + r["h3"]
        self.assertNotIn("<你的主体>", blob, "占位符没被填掉")
        self.assertNotIn("<场景>", blob, "占位符没被填掉")
        self.assertTrue(r["image_subject"].strip(), "没推出主体描述")
        self.assertTrue(r["image_evidence"], "没留下推导依据")

    def test_generic_build_still_uses_placeholder(self):
        """没给图的那条路必须保持不变 —— 流派卡上放的是通用版。"""
        sys.path.insert(0, SCRIPTS)
        import video_prompt as VP
        from movements import MOVEMENTS
        mv = [m for m in MOVEMENTS if m["slug"] == "baroque"][0]
        r = VP.build(mv)
        self.assertIn("<你的主体>", r["seedance"], "通用版不该被 i2v 影响")

    def test_reverse_prompt_attaches_image_specific_video(self):
        img, ana = self._analysis()
        import reverse_prompt as RP
        from movements import MOVEMENTS
        rec = RP.record(img, ana, suggest=[{"slug": "baroque", "name": "巴洛克",
                                            "score": 0.9}], source="test")
        mv = [m for m in MOVEMENTS if m["slug"] == "baroque"][0]
        card = RP.compose(rec, mv, os.path.basename(img))
        # 断言必须**只看视频那一节**：卡里的七层提示词块本来就留着
        # `<你的主体>` —— 那是设计如此（「这张画的是什么」只能看图才知道，
        # 卡上不替你编，见 compose 里的说明）。第一版断言扫了整张卡，
        # 于是把正确行为报成了失败。
        self.assertIn("## 四、视频提示词", card, "卡里没有视频节")
        video = card.split("## 四、视频提示词", 1)[1]
        self.assertNotIn("<你的主体>", video,
                         "反推卡的视频块没走 i2v，退回了通用版")
        self.assertNotIn("<场景>", video, "视频块里还有未填的占位符")
        self.assertIn("这张图", card, "应当标明视频提示词来自这张图")


# ------------------------------------------------------- 3. 冲突消解的不变量

class ConflictTests(unittest.TestCase):
    """compose 的默认结果必须是**可直接使用**的，不能留自相矛盾的指令。

    不变量：被判定为冲突的负向词，不得出现在最终负向提示词里。
    """

    def _compose(self, extra=()):
        rc, out, err = run(["artvault.py", "--json", "compose",
                            "--style", "ukiyo-e", "--lighting", "baroque",
                            "--subject", "a lone samurai"] + list(extra))
        self.assertEqual(0, rc, err[-400:])
        return json.loads(out)

    def test_dropped_never_leaks_into_negative(self):
        r = self._compose()
        self.assertTrue(r["conflicts"], "浮世绘×巴洛克应当检出冲突")
        neg = {x.strip().lower() for x in r["negative"].split(",") if x.strip()}
        for d in r["dropped"]:
            self.assertNotIn(d["term"].lower(), neg,
                             "已消解的 `%s` 仍留在负向提示词里" % d["term"])

    def test_counts_match(self):
        r = self._compose()
        self.assertEqual(len(r["conflicts"]), len(r["dropped"]),
                         "检出数与消解数应当一致")

    def test_keep_conflicts_restores_raw_union(self):
        kept = self._compose(["--keep-conflicts"])
        self.assertEqual([], kept["dropped"],
                         "--keep-conflicts 不该消解任何东西")
        self.assertTrue(kept["conflicts"], "--keep-conflicts 仍应报告冲突")
        # 原样合集里那个词应当在
        neg = kept["negative"].lower()
        self.assertIn("cast shadows", neg,
                      "--keep-conflicts 应当保留被消解前的那句")


# ------------------------------------------------------- 4. 生成物的可复现性

class ReproducibilityTests(unittest.TestCase):
    """重新生成一遍，工作树必须**保持干净** —— 生成物必须是确定性的。

    这条同时守住两件事：
      · 生成器没有把时间戳、随机数、绝对路径写进产物
      · 提交上去的生成物 == 生成器现在会产出的一切（不会「本地和仓库不一致」）
    """

    def setUp(self):
        st = git_status()
        if "GIT-FAILED" in st:
            self.skipTest("不是 git 仓库，跳过")
        if is_dirty(st):
            self.skipTest("工作树有未提交改动，跳过（否则分不清是谁弄脏的）")

    def test_build_vault_is_deterministic(self):
        rc, out, err = run(["build_vault.py"], timeout=300)
        self.assertEqual(0, rc, "build_vault 失败：%s" % err[-600:])
        st = git_status()
        self.assertFalse(is_dirty(st),
                         "重新生成后有改动 —— 生成物不是确定性的：\n" + st)

    def test_verify_vault_passes(self):
        rc, out, err = run(["verify_vault.py", "--quick"], timeout=300)
        self.assertEqual(0, rc, "验收未通过：\n%s" % out[-1500:])


# --------------------------------------------------------------- 5. MCP 协议

class McpTests(unittest.TestCase):
    """MCP 服务要能完成一次真实握手 —— 不能只测「能 import」。"""

    def _rpc(self, *messages):
        stdin = "\n".join(json.dumps(m) for m in messages) + "\n"
        rc, out, err = run(["mcp_server.py"], stdin_text=stdin, timeout=60)
        self.assertEqual(0, rc, err[-400:])
        return [json.loads(l) for l in out.splitlines() if l.strip()]

    def test_initialize_and_tools_list(self):
        resp = self._rpc(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        )
        by_id = {r.get("id"): r for r in resp}
        self.assertIn(1, by_id, "initialize 没有返回")
        self.assertIn("protocolVersion", by_id[1]["result"])
        tools = [t["name"] for t in by_id[2]["result"]["tools"]]
        for expect in ("search_movements", "compose_prompt", "get_video_prompt"):
            self.assertIn(expect, tools)

    def test_tools_call_roundtrip(self):
        resp = self._rpc(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
             "params": {"name": "get_layers", "arguments": {"slug": "baroque"}}},
        )
        got = [r for r in resp if r.get("id") == 2]
        self.assertTrue(got, "tools/call 没有返回")
        self.assertIn("result", got[0], "tools/call 返回了错误：%s" % got[0])

    def test_unknown_tool_is_an_error_not_a_crash(self):
        resp = self._rpc(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
             "params": {"name": "不存在的工具", "arguments": {}}},
        )
        got = [r for r in resp if r.get("id") == 2]
        self.assertTrue(got, "不存在的工具应当返回一条错误，而不是让服务崩掉")


# ------------------------------------------- 6. 缺可选依赖时必须优雅降级

class OptionalDegradationTests(unittest.TestCase):
    """**本仓库的卖点之一是「核心只用标准库」**，所以缺可选依赖是合法状态。

    合法状态下的唯一要求：给一句人话，而不是一段 traceback。
    这条比它看起来重要 —— 上面第 1 类测试里的 image_analysis_ext 就是这么炸的。
    """

    def test_no_traceback_when_optional_deps_missing(self):
        img = a_real_image()
        if not img:
            self.skipTest("仓库里没有图片，跳过")
        cases = [
            (["image_analysis.py", img], "Pillow"),
            (["image_analysis_ext.py", img], "Pillow"),
            (["artvault_vision.py", "dups", "--thresh", "0.08"], "numpy"),
            (["clip_match.py", "match", img], "CLIP/numpy"),
        ]
        for args, what in cases:
            rc, out, err = run(args, timeout=120)
            self.assertNotIn("Traceback (most recent call last)", err + out,
                             "%s 缺依赖时抛了 traceback，应当给人话（%s）"
                             % (args[0], what))

    def test_image_analysis_degrades_or_works(self):
        """Pillow 要么可用、要么给出可读的提示 —— 两者都可以，traceback 不可以。

        这里**不去猜** Pillow 在不在：脚本会自己往 `_scripts/vendor/libs`
        里找（本仓库推荐装在那里），所以测试进程 `import PIL` 失败不代表
        脚本用不了。第一版测试用 `has_module("PIL")` 判断，结果本机有 vendor
        时误判成「应该失败」，是一条假阴性。改成只看**行为**。
        """
        img = a_real_image()
        if not img:
            self.skipTest("仓库里没有图片，跳过")
        rc, out, err = run(["image_analysis.py", img], timeout=120)
        blob = out + err
        self.assertNotIn("Traceback (most recent call last)", blob)
        if rc != 0:
            self.assertIn("Pillow", blob, "失败时必须明确说缺 Pillow")


# ------------------------------------------------------------ 7. 发布视图卫生

class PublishingTests(unittest.TestCase):
    """发布前最容易翻车的地方：仓库里混进不该发布的东西。

    这些是「一旦发生就很难挽回」的检查 —— 推上去就来不及了。
    """

    def test_no_personal_absolute_paths_in_tracked_files(self):
        p = subprocess.run(["git", "grep", "-nI", "-E", r"/Users/[a-zA-Z0-9_.-]+/",
                            "--", "."],
                           capture_output=True, text=True, cwd=VAULT)
        hits = [l for l in p.stdout.splitlines()
                if "_scripts/vendor" not in l]
        self.assertEqual([], hits, "已跟踪文件里有个人绝对路径：\n" + "\n".join(hits[:10]))

    def test_no_secrets_looking_strings(self):
        pat = r"(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})"
        p = subprocess.run(["git", "grep", "-nIE", pat, "--", "."],
                           capture_output=True, text=True, cwd=VAULT)
        self.assertEqual("", p.stdout, "疑似密钥进了仓库：\n" + p.stdout[:500])

    def test_readme_numbers_match_publish_view(self):
        """README 说的规模必须等于 clone 之后真拿到的规模。

        这个数字曾经是 654（实际 442），虚报 48%。见 verify_vault 第 16 项。
        """
        sys.path.insert(0, SCRIPTS)
        import build_vault as BV
        stats = BV.publish_stats()
        with open(os.path.join(VAULT, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        m = re.search(r"\*\*(\d+)\s*张\*\*（(\d+)\s*MB）", readme)
        self.assertTrue(m, "README 里没找到实图统计行")
        self.assertEqual(stats["n_img"], int(m.group(1)),
                         "README 实图数与发布视图不一致")


if __name__ == "__main__":
    # 让 `python3 tests/smoke_test.py -v` 和 `python3 tests/smoke_test.py Class` 都能用
    unittest.main(verbosity=2, argv=[sys.argv[0]] + sys.argv[1:])
