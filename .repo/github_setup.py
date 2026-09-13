#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
github_setup.py —— 把仓库推送并配置到 GitHub 的一条龙脚本。

只用标准库（urllib / subprocess），不需要 requests 或 gh。

**token 不会出现在命令行参数里**（那会让 `ps` 看到），也不会写进任何文件：
    1. 优先读环境变量 GITHUB_TOKEN
    2. 否则交互式输入（getpass，不回显）
    推送时用临时 credential 文件（权限 600），用完立即覆写并删除。

用法
    python3 github_setup.py status            # 只读：看远程当前配置（不需要 token）
    python3 github_setup.py push              # 推送当前分支
    python3 github_setup.py template          # 设为 GitHub Template 仓库
    python3 github_setup.py topics            # 设置 topics
    python3 github_setup.py about             # 设置 description
    python3 github_setup.py all               # 以上全部

需要的 token 权限
    推送          Repository → Contents: Read and write
    设为 Template  Repository → Administration: Read and write
    topics/about  同上（Administration）

fine-grained token 建好后要到仓库的 Settings → Collaborators and teams
把该 token 所属的 app 加进去，或者直接用 classic token 勾 `repo`。
"""

import argparse
import getpass
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.dirname(HERE)

# 仓库地址优先从 git remote 推导 —— 别人 fork 之后不用改这个文件。
# 推不出来才回退到默认值（与 build_vault.py 的 REPO_SLUG 一致）。
DEFAULT_SLUG = "YanKaFei/art-aesthetic-vault"
API = "https://api.github.com"


def detect_slug():
    try:
        r = subprocess.run(["git", "-C", VAULT, "remote", "get-url", "origin"],
                           capture_output=True, text=True, timeout=15)
        url = (r.stdout or "").strip()
        if url:
            # https://github.com/owner/repo.git  或  git@github.com:owner/repo.git
            tail = url.split("github.com", 1)[-1].lstrip(":/")
            if tail.endswith(".git"):
                tail = tail[:-4]
            parts = [x for x in tail.split("/") if x]
            if len(parts) >= 2:
                return "%s/%s" % (parts[0], parts[1])
    except Exception:
        pass
    return DEFAULT_SLUG


REPO_SLUG = detect_slug()

def _n_movements():
    """流派数量**从数据里取**，不写死。

    这里原来写着 "141 art movements"，补到 147 张之后它就变成错的了 ——
    和 README 统计数字、冒烟里的「141 张卡」是同一类坑：写死的数字，
    唯一的作用就是某天变成错的。
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from movements import MOVEMENTS
        return len(MOVEMENTS)
    except Exception:
        return None


_N_MV = _n_movements()
DESCRIPTION = ("%s art movements decomposed into 7 swappable AI prompt layers — "
               "style, lighting, color, composition, medium, mood, camera. "
               "CLI + MCP server. Obsidian vault with public-domain artworks."
               % (_N_MV if _N_MV else "100+"))

# GitHub 限制：最多 20 个，小写字母/数字/连字符
TOPICS = [
    "aesthetics", "art", "art-history", "artificial-intelligence", "ai-art",
    "prompt-engineering", "text-to-image", "stable-diffusion", "concept-art",
    "digital-art", "style-reference", "public-domain", "image-analysis",
    "knowledge-base", "obsidian", "mcp", "claude", "design-tools",
    "creative-tools", "reference",
]


# ------------------------------------------------------------ token
def get_token(required=True):
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t.strip()
    if not required:
        return None
    if not sys.stdin.isatty():
        print("没有 GITHUB_TOKEN 环境变量，且当前不是交互式终端。")
        print("用法：GITHUB_TOKEN=xxx python3 github_setup.py push")
        return None
    print("粘贴 GitHub token（输入不回显）：")
    return getpass.getpass("token> ").strip() or None


# ------------------------------------------------------------ API
def api(method, path, token=None, payload=None):
    url = path if path.startswith("http") else API + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("User-Agent", "artvault-setup")
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return r.status, (json.loads(body) if body.strip() else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            msg = json.loads(body).get("message", body[:200])
        except Exception:
            msg = body[:200]
        return e.code, {"message": msg}
    except Exception as e:
        return 0, {"message": str(e)}


def _perm_hint(code, what):
    if code == 403:
        print("    → 权限不足。这个操作需要 Repository → Administration: Read and write。")
        print("      fine-grained token 还要到仓库 Settings → Collaborators and teams")
        print("      把 token 所属 app 加进去；或改用 classic token 勾 `repo`。")
    elif code == 401:
        print("    → token 无效或已过期。")
    elif code == 404:
        print("    → 仓库不存在，或 token 无权访问（私有/权限范围不对）。")
    return False


# ------------------------------------------------------------ 子命令
def cmd_status(_a):
    code, d = api("GET", "/repos/" + REPO_SLUG)
    if code != 200:
        print("查询失败（%s）：%s" % (code, d.get("message")))
        return 1
    print("仓库           %s" % d["full_name"])
    print("可见性         %s" % ("私有" if d["private"] else "公开"))
    print("默认分支       %s" % d["default_branch"])
    print("is_template    %s" % d["is_template"])
    print("description    %s" % (d.get("description") or "（空）"))
    print("topics (%d)     %s" % (len(d.get("topics") or []), ", ".join(d.get("topics") or [])))
    print("大小           %.0f MB" % (d["size"] / 1024))
    print("许可           %s" % ((d.get("license") or {}).get("spdx_id") or "未识别"))
    print()
    print("目标状态：")
    print("  is_template    True")
    print("  description    %s" % DESCRIPTION)
    print("  topics (%d)     %s" % (len(TOPICS), ", ".join(TOPICS)))
    return 0


def cmd_push(a):
    token = get_token()
    if not token:
        return 1
    user = REPO_SLUG.split("/")[0]
    force = bool(getattr(a, "force", False))
    # token 只写进临时文件（600），不进命令行参数 —— `ps` 看不到
    fd, path = tempfile.mkstemp(prefix=".gitcred-")
    os.close(fd)
    os.chmod(path, 0o600)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("https://%s:%s@github.com\n" % (user, token))
        cmd = ["git", "-C", VAULT, "-c", "credential.helper=store --file=%s" % path,
               "push", "origin", "main"]
        if force:
            # 历史被改写之后，远端那条线已经和本地没有共同后继，普通 push
            # 必然被拒。--force-with-lease 在这里不可用：它比对的
            # refs/remotes/origin/* 也一起被改写了，lease 一定不匹配。
            cmd.insert(-2, "--force")
        r = subprocess.run(cmd, text=True, capture_output=True)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        if r.returncode != 0 and not force and (
                "non-fast-forward" in r.stderr or "rejected" in r.stderr
                or "fetch first" in r.stderr):
            print()
            print("推送被拒：远端有本地没有的提交。常见原因有两个 ——")
            print("  1. 远程改过（别人推过 / 网页上编辑过）→ 先 `git fetch` 看看差异")
            print("  2. **本地历史被改写过**（filter-branch / rebase / 改过作者信息）")
            print("     → 此时远端那条线的提交在本地已经不存在，只能强制推送：")
            print("       python3 github_setup.py push --force")
            print("     强制推送会**覆盖远端历史**。若已经有人 clone 过，他们手上的")
            print("     旧历史不会自动更新；协作仓库请先和所有人确认。")
        return r.returncode
    finally:
        try:                       # 先覆写再删，避免残留在磁盘上
            with open(path, "wb") as f:
                f.write(b"\0" * 512)
            os.remove(path)
        except Exception:
            pass


def cmd_template(_a):
    token = get_token()
    if not token:
        return 1
    code, d = api("PATCH", "/repos/" + REPO_SLUG, token, {"is_template": True})
    if code == 200:
        print("  ✓ 已设为 Template 仓库（is_template=%s）" % d.get("is_template"))
        return 0
    print("  ✗ 设置失败（%s）：%s" % (code, d.get("message")))
    return _perm_hint(code, "template")


def cmd_topics(_a):
    token = get_token()
    if not token:
        return 1
    code, d = api("PUT", "/repos/%s/topics" % REPO_SLUG, token, {"names": TOPICS})
    if code == 200:
        got = d.get("names") or []
        print("  ✓ topics 已设为 %d 个：%s" % (len(got), ", ".join(got)))
        return 0
    print("  ✗ 设置失败（%s）：%s" % (code, d.get("message")))
    return _perm_hint(code, "topics")


def cmd_about(_a):
    token = get_token()
    if not token:
        return 1
    code, d = api("PATCH", "/repos/" + REPO_SLUG, token,
                  {"description": DESCRIPTION, "homepage": ""})
    if code == 200:
        print("  ✓ description 已更新：")
        print("      %s" % d.get("description"))
        return 0
    print("  ✗ 设置失败（%s）：%s" % (code, d.get("message")))
    return _perm_hint(code, "about")


def cmd_all(a):
    print("先看当前状态：")
    cmd_status(a)
    print()
    rc = 0
    for name, fn in (("推送", cmd_push), ("Template", cmd_template),
                     ("topics", cmd_topics), ("description", cmd_about)):
        print("── %s ──" % name)
        if fn(a) != 0:
            rc = 1
        print()
    if rc == 0:
        print("全部完成。仓库地址：https://github.com/%s" % REPO_SLUG)
    else:
        print("有步骤失败，上面每条都写了原因。")
    return rc


def main():
    ap = argparse.ArgumentParser(description="推送并配置 GitHub 仓库")
    sub = ap.add_subparsers(dest="cmd")
    for name, help_ in (("status", "只读：查看远程当前配置（不需要 token）"),
                        ("push", "推送当前分支到 origin/main"),
                        ("template", "设为 GitHub Template 仓库"),
                        ("topics", "设置 topics"),
                        ("about", "设置 description"),
                        ("all", "以上全部（推荐）")):
        sp = sub.add_parser(name, help=help_)
        if name in ("push", "all"):
            sp.add_argument("--force", action="store_true",
                            help="强制推送（**会覆盖远端历史**；"
                                 "本地历史被改写过后才需要）")
    a = ap.parse_args()
    fn = {"status": cmd_status, "push": cmd_push, "template": cmd_template,
          "topics": cmd_topics, "about": cmd_about, "all": cmd_all}.get(a.cmd)
    if not fn:
        ap.print_help()
        return 0
    return fn(a)


if __name__ == "__main__":
    sys.exit(main())
