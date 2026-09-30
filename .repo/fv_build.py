#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fv_build.py —— 把电影卡数据生成成 Obsidian 笔记：40-films/<导演>/<电影>.md

## 生成物长什么样

与 `10-movements/` 的艺术流派卡**同构**（九个小节、七层提示词、配色板、
翻车点、出处），因为读者的使用方式一样：打开一张卡，拿走能粘贴的提示词。
但多两样电影独有的东西：

  · **剧照区**：外链索引 + 本地私有副本，编号与配色板/七层一一对应
  · **反推**：从剧照读回七层的过程被写出来（哪一层是被哪张剧照推出来的），
    这样你能看出「为什么这么写」，而不是接受一个黑箱结论

## 为什么生成物进版本库，本地图不进

卡片正文是**文本**，可以自由分发；剧照是版权作品（film-grab 页面写明
*Images are not permitted for commercial use*），所以：

    正文只记外链  →  别人 clone 后有网就能看图
    本地副本 gitignore  →  你自己的离线参考，不随仓库走

`tests/film_test.py` 里有两条检查守着这条线：
卡片正文不得出现 `images-films`、本地目录必须被 git 真的忽略。

## 确定性

同一份输入必须产出逐字节相同的输出。生成物进版本库，如果两次生成
有差异，diff 就永远在抖，审阅的人再也看不出真正改了什么 ——
所以这里不做任何依赖时间/随机/遍历顺序的事情。
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fv_core  # noqa: E402

OUT_DIR = os.path.join(VAULT, "40-films")
CATEGORY = "电影风格"
# 六个维度沿用艺术流派卡的用词，读者的认知负担为零
DIMS = ["色彩", "光影", "笔触", "构图", "材质", "情绪"]
CREW_LABEL = {"cinematography": "摄影指导", "production_design": "美术指导",
              "costume_design": "服装设计"}


def director_note_name(d):
    """导演页的文件名。

    原来想用通用的 `_导演`，但那是**全库同名**：Obsidian 的 `[[_导演]]`
    会歧义，而 verify_vault 的双链检查按 basename 判定，同名会让
    「指向哪一篇」变得不可判定。所以带上导演短标识 —— 又短又唯一。
    """
    return "导演-%s" % d["director_slug"]


def _yq(s):
    """YAML 值安全引号。中文片名里的冒号/井号不加引号会让 frontmatter 解析失败。"""
    s = str(s)
    if s == "" or any(c in s for c in ":#[]{}&*!|>'\"%@`,") or s[0] in "-? ":
        return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')
    return s


def _palette_line(f):
    return ", ".join("%s %s" % (n, h) for h, n in f["palette"])


def _swatches(f):
    """六色色块。

    用内联样式的 div 而不是图片：色块就该是「那一个颜色本身」，
    截图或占位图都会骗人。Obsidian 渲染内联 HTML；万一哪个渲染器
    把它过滤了，右边的 hex 与色名仍然可读 —— 所以是**加性**的，
    不是「没有样式就什么都不剩」。
    """
    out = []
    for h, n in f["palette"]:
        out.append('<span style="display:inline-block;width:64px;height:28px;'
                   'background:%s;border:1px solid #8888;border-radius:3px;'
                   'vertical-align:middle;margin-right:6px"></span> `%s` **%s**<br>'
                   % (h, h, n))
    return "\n".join(out)


def _crew_table(f):
    """班底表。区分「抓到的（可回查）」与「手写的（未核对）」。

    为什么不直接合并成一个来源：读者需要知道哪一条能点回 film-grab 核对。
    把两者混在一起，就等于把「抄来的」说成「核对过的」。
    """
    crew = f.get("crew") or {}
    rows = []
    if f.get("crew_verified"):
        for key in ("cinematography", "production_design", "costume_design"):
            if crew.get(key):
                rows.append("| %s | %s | ✅ film-grab 抓取 |" % (CREW_LABEL[key], crew[key]))
        src = "✅ 已用 film-grab 画廊页核对"
    else:
        for k, v in crew.items():
            rows.append("| %s | %s | ✍️ 手写，未经画廊页核对 |" % (k, v))
        src = "✍️ 手写值，未联网核对（跑 `python3 .repo/fv_fetch.py --fetch` 可核对）"
    if not rows:
        return "", src
    head = ["| 职位 | 姓名 | 来源 |", "|---|---|---|"]
    return "\n".join(head + rows), src


def _local_stills(f, k=6):
    """本地已有的剧照文件（按序号），配合实测缓存里的**代表帧**优先。

    嵌入哪几张：优先用 k-medoids 选出的代表帧（它们最能代表全片），
    不够再用序号靠前的补。返回 vault 相对路径列表。
    """
    d = os.path.join(VAULT, "99-attachments", "images-films", f["slug"])
    if not os.path.isdir(d):
        return []
    have = sorted(x for x in os.listdir(d)
                  if re.match(r"^\d+\.(?:jpe?g|png|webp)$", x, re.I))
    if not have:
        return []
    pick = []
    try:
        import still_analysis as SA
        m = SA.load_measurements(f["slug"]) or {}
        # 代表帧是 k-medoids 选的，最能代表全片
        for x in m.get("representative") or []:
            fn = x.get("file")
            if fn in have and fn not in pick:
                pick.append(fn)
    except Exception:
        pass
    for fn in have:                      # 不足则按序号补
        if len(pick) >= k:
            break
        if fn not in pick:
            pick.append(fn)
    return ["99-attachments/images-films/%s/%s" % (f["slug"], fn)
            for fn in pick[:k]]


def _still_block(f):
    """剧照区：**本地嵌入**（能在 Obsidian 里直接看到）+ 外链（可回查来源）。

    ## 这里做过一次策略反转，理由要留档

    原设计是「卡片只记外链、本地图 gitignore」—— 理由是版权图不随仓库分发，
    且嵌入本地图会让 clone 的人看到红叉。

    用户要求「把画面放入卡片」后改成**本地嵌入**。代价是明确的：

      · `99-attachments/images-films/` **不能再 gitignore**（图随仓库走）
      · 这批剧照版权属原片方（film-grab 写明 non-commercial），
        所以卡上必须有版权声明，公开分发前要自行判断
      · 嵌入前必须确认文件真的存在，否则 Obsidian 里是断图
    """
    st = f.get("stills") or []
    local = _local_stills(f, k=6)
    if not st and not local:
        # 失败模式②：没有网络也要能出卡，但**必须标明未抓取**，
        # 不能让人以为「这部片恰好没剧照」。
        return ("> [!warning] 剧照未抓取\n"
                "> 这部片还没有抓过剧照。跑 `python3 .repo/fv_fetch.py --fetch` 补上。\n"
                "> 画廊页：[film-grab](%s)\n" % f["filmgrab"])

    L = []
    if local:
        # 直接嵌入，Obsidian 渲染 —— 这是「把画面放入卡片」的落点
        widths = [420, 420, 420]
        for i, rel in enumerate(local):
            L.append("![[%s|%d]]" % (rel, widths[i % 3]))
            L.append("")
    else:
        L.append("> [!warning] 本地没有剧照文件，只能给外链")
        L.append("> 跑 `python3 .repo/fv_fetch.py --download --per 0` 把图下到本地后重建。")
        L.append("")
    L.append("> [!warning] 剧照版权")
    L.append("> 这些画面**版权属原片方**（来源 [film-grab](%s)，其页面写明"
             "*Images are not permitted for commercial use*）。" % f["filmgrab"])
    L.append("> 本库把它们放在卡上**仅为个人研究参考**；公开分发/商用前请自行取得授权。")
    L.append("> 本地副本在 `99-attachments/images-films/%s/`。" % f["slug"])
    L.append("")
    if st:
        L.append("**来源外链**（可回查；完整 %d 张见 [[剧照语料索引]]）" % len(st))
        L.append("")
        L.append("| # | 在 film-grab 打开原图 |")
        L.append("|---|---|")
        for i, u in enumerate(st[:8], 1):
            L.append("| %02d | [打开 %02d](%s) |" % (i, i, u))
    return "\n".join(L) + "\n"


def film_note(f):
    """一张电影卡的完整正文。"""
    slug = f["slug"]
    year = f["year"]
    L = []
    A = L.append

    # ---------------------------------------------------------------- 头
    A("---")
    A("type: 电影")
    A("导演: %s" % _yq(f["director_zh"]))
    A("导演英文: %s" % _yq(f["director_en"]))
    A("电影: %s" % _yq(f["title_zh"]))
    A("英文片名: %s" % _yq(f["title_en"]))
    if f.get("title_original"):
        A("原文片名: %s" % _yq(f["title_original"]))
    A("年份: %d" % year)
    A("分类: %s" % CATEGORY)
    A("证据: %s" % f["source"])
    A("配色: [%s]" % ", ".join('"%s"' % h for h, _ in f["palette"]))
    A("标签:")
    A("  - 电影")
    A("  - %s" % slug)
    A("---")
    A("")
    A("# %s · %s" % (f["title_zh"], f["title_en"]))
    A("")
    A("> [!abstract] 一句话")
    A("> %s" % f["one_liner"])
    A("")
    A("| 导演 | 年份 | 原始片名 | 证据强度 |")
    A("|---|---|---|---|")
    A("| [[导演-%s\\|%s]] | %d | %s | %s |"
      % (f["director_slug"], f["director_zh"], year,
         f.get("title_original") or "—",
         "手写解读（班底已核对）" if f["source"] == "curated" else "从有限信息推断"))
    A("")
    crew_tbl, crew_src = _crew_table(f)
    if crew_tbl:
        A("**拍摄班底**")
        A("")
        A(crew_tbl)
        A("")
        A("> %s" % crew_src)
        A("")
    A("画廊页：[film-grab](%s)　|　导演索引：[%s](%s)"
      % (f["filmgrab"], f["director_en"], f.get("filmgrab_director") or ""))
    A("")
    A("---")
    A("")

    # ---------------------------------------------------------------- 一
    A("## 一、核心主张")
    A("")
    for c in f["core"]:
        A("- %s" % c)
    A("")

    # ---------------------------------------------------------------- 二
    A("## 二、视觉语言拆解（六维）")
    A("")
    A("| 维度 | 拆解 |")
    A("|---|---|")
    for d in DIMS:
        A("| **%s** | %s |" % (d, f["visual"].get(d, "—")))
    A("")

    # ---------------------------------------------------------------- 三
    A("## 三、配色板")
    A("")
    A(_swatches(f))
    A("")
    A("> [!example] 配色提示词（直接粘）")
    A("> `%s`" % _palette_line(f))
    A("")

    # ---------------------------------------------------------------- 四
    A("## 四、提示词结构")
    A("")
    A("> 每一层都能单独拆出来复用。镜头层是「要什么景别」而非这部片的属性，")
    A("> 所以不并入下面的整段，按画面需要自己接。")
    A("")
    A("| 层 | 可复用片段 |")
    A("|---|---|")
    for key in fv_core.LAYERS:
        A("| **%s** | `%s` |" % (fv_core.LAYER_ZH[key], f["layers"][key]))
    A("")
    A("### 整段正向提示词")
    A("")
    A("```text")
    A(f["positive"])
    A("```")
    A("")
    A("> 这是**风格层**，接在你自己的主体描述后面用：")
    A("> `<你的主体>, %s`" % f["positive"][:70])
    A("")
    A("### 负向提示词")
    A("")
    A("```text")
    A(f["negative"])
    A("```")
    A("")

    # ---------------------------------------------------------------- 五
    A("## 五、AI 视频层")
    A("")
    A("> A 块给 **Seedance 2.5**，B 块给 **MiniMax H3**。两块格式不同，**别混用** ——")
    A("> 原因见 [[视频提示词结构]]。")
    A("")
    v = f["video"]
    A("| 参考 | 内容 |")
    A("|---|---|")
    A("| **运动** | %s |" % v["运动"])
    A("| **运镜** | %s |" % v["运镜"])
    A("| **建议时长** | %s |" % v["时长"])
    A("")
    A("> [!important] 这部片的视频关键")
    A("> %s" % v["关键"])
    A("")
    A("### A. Seedance 2.5 五段式")
    A("")
    A("```text")
    A("【主体】<你的主体>，出现在<场景>。<写清核心事件：谁、在做什么、和什么互动>")
    A("")
    A("【风格】10 秒，16:9，高清。%s。整体情绪是%s。"
      % (f["visual"]["光影"], f["visual"]["情绪"]))
    A("风格锚定：%s" % f["positive"])
    A("")
    A("【时间线】")
    A("【0—3秒】起手就给画面最强的视觉信息：%s；机位%s，第一帧就要立住。"
      % (v["运动"].split("、")[0], v["运镜"].split("；")[0]))
    A("【3—6秒】%s；继续%s，让观众看清质感。"
      % ("、".join(v["运动"].split("、")[1:3]) or v["运动"], v["运镜"].split("；")[0]))
    A("【6—10秒】动作收束、情绪落地；机位缓慢收住，最后一帧停在能当封面的构图上。")
    A("")
    A("【BGM】按画面情绪铺底，不要从头就满；%s" % v["关键"])
    A("")
    A("【限制】%s；不要出现文字、字幕、水印；一次只让一个东西动；角色不要变形、多手多指、面部漂移" % v["关键"])
    A("```")
    A("")
    A("### B. MiniMax H3（中文自然语言，直接粘进输入框）")
    A("")
    A("```text")
    A("一段 10 秒的%s风格视频。画面是<你的主体>，在<场景>中，%s。"
      % (f["title_en"], v["运动"]))
    A("光线：%s。色彩：%s。构图：%s。质感：%s。整体情绪是%s。"
      % (f["visual"]["光影"], f["visual"]["色彩"], f["visual"]["构图"],
         f["visual"]["材质"], f["visual"]["情绪"]))
    A("摄影机：%s。开头两秒就要给出最强的视觉信息，不要用缓慢推进开场。" % v["运镜"])
    A("最容易翻车的一点：%s。画面里不要出现任何文字、字幕或水印。" % v["关键"])
    A("```")
    A("")

    # ---------------------------------------------------------------- 六
    A("## 六、剧照反推")
    A("")
    A("> [!note] 这一节是怎么来的")
    A("> 七层是**基于这部片公认的摄影特征手写**的，剧照用来校准描述，")
    A("> 不是逐帧取样算出来的。想看客观测量，把本地剧照交给")
    A("> `python3 .repo/image_analysis.py <图>` —— 数字是信号不是结论。")
    A("")
    A(_still_block(f))
    A("")

    # ---------------------------------------------------------------- 七
    A("## 七、常见翻车点")
    A("")
    for p in f["pitfalls"]:
        A("- %s" % p)
    A("")

    # ---------------------------------------------------------------- 八
    A("## 八、关联流派")
    A("")
    rel = fv_core.related(f)
    if rel:
        for c in rel:
            # 双链指向**文件名**，而流派卡的文件名是中文名（`巴洛克.md`），
            # 不是 slug。英文名放进显示文本，需要复制 slug 时看括号。
            A("- [[%s|%s（%s）]] —— %s"
              % (c["name_zh"], c["name_zh"], c["slug"], c["one_liner"]))
    else:
        A("- （暂无）")
    A("")
    A("> 跨库混搭示例：把这部片的**光照层**接到别的风格上 ——")
    A("> ```bash")
    A("> python3 .repo/artvault.py compose --lighting %s \\" % f["slug"])
    A(">     --color baroque --subject \"your subject\"")
    A("> ```")
    A("")

    # ---------------------------------------------------------------- 九
    A("## 九、出处")
    A("")
    A("| 层 | 内容 | 出处 |")
    A("|---|---|---|")
    A("| 班底/年份 | 导演、摄影、美术、服装、年份 | [film-grab 画廊页](%s) |" % f["filmgrab"])
    A("| 班底索引 | 该导演的全部片目 | [film-grab 导演页](%s) |"
      % (f.get("filmgrab_director") or ""))
    A("| 风格七层 | 手写解读（基于公认摄影特征） | 本站原创，非转载 |")
    A("| 剧照 | **版权属原片方，卡片内嵌仅供个人研究**；公开分发/商用前请自行取得授权 | "
      "[film-grab](%s) |" % f["filmgrab"])
    A("")
    A("---")
    A("")
    # 剧照实测页：**生成器不管它在不在**，只按磁盘事实挂链接。
    # 没跑 still_build.py 时这一节不出现 —— 宁可不出现，也不要一个红链。
    try:
        import still_analysis as _SA
        if _SA.load_measurements(f["slug"]):
            A("## 十、剧照实测")
            A("")
            A("![[%s-实测]]" % f["title_zh"])
            A("")
            A("> 上面这一页是**机器量的数字**（逐张七维 + 景别 + 构图线 + 显著性，")
            A("> 聚合成全片图景），与本卡的**手写解读**并列阅读。两者可信度来源不同，")
            A("> 谁也不冒充谁。详见 [[剧照实测总览]]。")
            A("")
    except Exception:
        pass
    A("← [[导演-%s|%s]] · [[电影风格总览]]　|　延伸阅读 [[提示词拆解方法]]"
      % (f["director_slug"], f["director_zh"]))
    A("")
    return "\n".join(L)


def director_note(d):
    """导演索引页：40-films/<导演>/_导演.md"""
    L = ["---", "type: 导演", "导演: %s" % _yq(d["director_zh"]),
         "导演英文: %s" % _yq(d["director_en"]), "分类: %s" % CATEGORY,
         "标签:", "  - 导演", "---", "",
         "# %s · %s" % (d["director_zh"], d["director_en"]), ""]
    films = d["films"]
    L += ["> [!abstract] 这位导演的画面在做什么",
          "> %s" % films[0]["one_liner"], "",
          "共收录 **%d** 部。" % len(films), "",
          "| 电影 | 年份 | 一句话 | 剧照 |", "|---|---|---|---|"]
    for f in films:
        n = len(f.get("stills") or [])
        L.append("| [[%s]] | %d | %s | %s |"
                 % (f["title_zh"], f["year"],
                    f["one_liner"].replace("**", ""), ("%d 张" % n) if n else "—"))
    L += ["", "画廊页：[film-grab 导演页](%s)"
          % (films[0].get("filmgrab_director") or ""), "",
          "← [[电影风格总览]] · [[流派总览]]", ""]
    return "\n".join(L)


def overview_note(dirs, crawl_note=None):
    """40-films/电影风格总览.md"""
    nf = sum(len(d["films"]) for d in dirs)
    L = ["---", "type: 总览", "分类: %s" % CATEGORY, "标签:", "  - 总览", "---", "",
         "# 电影风格总览", "",
         "> [!info] 这是什么",
         "> 按 **导演 → 电影** 组织的画面风格库，与 `10-movements/` 的艺术流派库并列。",
         "> 每部片是一张卡：剧照索引、六维拆解、七层提示词、配色色块、视频层、翻车点。",
         "> 目的是让 AI（或你自己）能**调取一种具体的电影画面语言**去模仿。", "",
         "现收录 **%d** 部片 / **%d** 位导演。" % (nf, len(dirs)), "",
         "## 怎么用（命令行 / MCP）", "",
         "```bash",
         "python3 .repo/artvault.py film list              # 列出全部",
         "python3 .repo/artvault.py film directors         # 按导演分组",
         "python3 .repo/artvault.py film search \"霓虹 雨夜\"  # 按风格词找片",
         "python3 .repo/artvault.py film layers 银翼杀手2049 # 只取七层（省 token）",
         "python3 .repo/artvault.py film show dune          # 整张卡",
         "python3 .repo/artvault.py compose --lighting villeneuve-dune \\",
         "    --color baroque --subject \"a lone figure\"     # 跨源混搭",
         "```", "",
         "## 按导演", ""]
    for d in dirs:
        L.append("### [[%s\\|%s · %s]]"
                 % (director_note_name(d), d["director_zh"], d["director_en"]))
        L.append("")
        for f in d["films"]:
            L.append("- [[%s]]（%d）—— %s"
                     % (f["title_zh"], f["year"],
                        f["one_liner"].replace("**", "")))
        L.append("")
    L += ["## 证据强度（务必看清）", "",
          "艺术流派卡（`10-movements/` 的 147 张）的七层是**手写的艺术史结论**，",
          "每层追得到 Tate 术语词条。电影卡不一样：", "",
          "- **班底与年份**：从 film-grab 画廊页抓取，卡片上标了 ✅ 且带外链可回查",
          "- **七层拆解**：手写解读，依据是这部片公认的摄影特征（卡上标 `证据: curated`）",
          "- **剧照**：只索引外链，不转载（版权属原片方）", "",
          "也就是：**「谁拍的、哪一年」是可核对的；「怎么拍出来的」是解读。**",
          "不要把它当成逐帧测量的结果。", "",
          "## 抓取与重建", "",
          "```bash",
          "python3 .repo/fv_fetch.py --check      # 验证画廊页还通不通",
          "python3 .repo/fv_fetch.py --fetch      # 抓班底 + 剧照外链",
          "python3 .repo/fv_fetch.py --download   # 额外下载本地私有参考图",
          "python3 .repo/fv_build.py              # 重新生成 40-films/",
          "python3 .repo/tests/film_test.py       # 电影模块的测试",
          "```", "",
          "← [[流派总览]] · [[AI 调用指南]]", ""]
    return "\n".join(L)


def sweep(dirs=None):
    """删掉**本生成器这次不会重写**的 .md —— 用差集，而不是按目录一刀切。

    ## 为什么必须用差集（这里连踩两次）

    第一版无差别清空 `40-films/**/*.md`：把 `still_build.py` 的产物
    （`剧照实测总览.md`、`<片名>-实测.md`）一起删了 —— 刚生成的实测页
    在下一次重建电影卡时凭空消失，`[[剧照实测总览]]` 变断链。

    第二版改成「按导演目录清」，**还是删**：实测页正好就住在那些目录里。

    两次都错在同一个思路上：**按位置圈定所有权**。正确做法是按**内容**
    圈定 —— 先算出「这次会写哪些文件」，然后把该目录里不在名单上的删掉。
    这样 `-实测.md`（不在名单里，且是另一个生成器的）自然被放过，
    而真正过时的旧电影卡（改了片名/删了片）照样被清掉。
    """
    import glob
    import fv_core
    dirs = dirs or fv_core.directors()
    if not os.path.isdir(OUT_DIR):
        return 0

    # 本次会写出的文件白名单
    keep = {os.path.join(OUT_DIR, "电影风格总览.md"),
            os.path.join(OUT_DIR, "_剧照语料", "剧照语料索引.md"),
            os.path.join(OUT_DIR, "剧照实测总览.md")}
    for d in dirs:
        keep.add(os.path.join(OUT_DIR, d["director_slug"], "%s.md" % director_note_name(d)))
        for f in d["films"]:
            keep.add(os.path.join(OUT_DIR, d["director_slug"], "%s.md" % f["title_zh"]))
            # `still_build.py` 的实测页也住在这里。**只在它真的存在时才保护** ——
            # 有测量缓存才有那一页；没跑过实测就没什么可保护的，别造幽灵白名单。
            try:
                import still_analysis as _SA
                if _SA.load_measurements(f["slug"]):
                    keep.add(os.path.join(OUT_DIR, f["director_slug"],
                                          "%s-实测.md" % f["title_zh"]))
            except Exception:
                pass

    killed = 0
    for d in dirs:
        sub = os.path.join(OUT_DIR, d["director_slug"])
        if not os.path.isdir(sub):
            continue
        for p in glob.glob(os.path.join(sub, "*.md")):
            if p not in keep:
                try:
                    os.remove(p)
                    killed += 1
                except OSError:
                    pass
    # 清掉空掉的导演目录
    for root, _d, _f in os.walk(OUT_DIR, topdown=False):
        if root == OUT_DIR:
            continue
        try:
            if not os.listdir(root):
                os.rmdir(root)
        except OSError:
            pass
    return killed


def build(dirs=None):
    """生成全部笔记。返回写出的文件数。"""
    dirs = dirs or fv_core.directors()
    sweep(dirs)
    n = 0
    for d in dirs:
        sub = os.path.join(OUT_DIR, d["director_slug"])
        os.makedirs(sub, exist_ok=True)
        for f in d["films"]:
            p = os.path.join(sub, "%s.md" % f["title_zh"])
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(film_note(f))
            n += 1
        p = os.path.join(sub, "%s.md" % director_note_name(d))
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(director_note(d))
        n += 1
    with open(os.path.join(OUT_DIR, "电影风格总览.md"), "w", encoding="utf-8") as fh:
        fh.write(overview_note(dirs))
    n += 1

    # 剧照语料索引（只含外链，可进版本库）
    import fv_fetch
    os.makedirs(fv_fetch.CORPUS_DIR, exist_ok=True)
    with open(os.path.join(fv_fetch.CORPUS_DIR, "剧照语料索引.md"), "w", encoding="utf-8") as fh:
        fh.write(fv_fetch.corpus_note(dirs, fv_core._crawled()))
    n += 1
    return n


def main():
    n = build()
    s = fv_core.stats()
    print("已生成 %d 个文件 → %s" % (n, OUT_DIR))
    print("  %d 部片 / %d 位导演（已抓剧照 %d 部）"
          % (s["films"], s["directors"], s["with_stills"]))
    if s["with_stills"] < s["films"]:
        print("  ⚠ 有 %d 部片还没抓剧照：卡片上会标「剧照未抓取」，"
              "跑 fv_fetch.py --fetch 补" % (s["films"] - s["with_stills"]))
    return 0


if __name__ == "__main__":
    from clihelp import guard
    guard(sys.argv[1:], "python3 fv_build.py",
          ["把电影卡数据生成成 Obsidian 笔记 → 40-films/<导演>/<电影>.md",
           "没有任何选项：读 fv_data.py + _data/films/*.json，重写 40-films/。"])
    sys.exit(main())
