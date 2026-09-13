#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""clihelp.py —— 所有脚本共用的 `--help` 闸门。

为什么需要这一个模块：本仓库早期几个脚本用「argv 里不是 -- 开头的东西就是
流派名」这种手写解析，于是**不认识 `--help`，把它当成普通参数往下走**：

    python3 build_vault.py --help   →  真的重建了整个仓库（141 张卡片全部重写）
    python3 fetch_art.py --help     →  真的开始联网抓图
    python3 mcp_server.py --help    →  真的起了一个 stdio MCP 服务，卡住不返回
    python3 video_prompt.py --help  →  报「未知流派: --help」

帮助是最没有破坏性的一个参数，在这里却成了最有破坏性的一个。读者拿到一个
陌生仓库，第一个会试的就是 `--help`；所以每个有副作用的入口都必须先过这道闸。

用法（放在 `if __name__ == "__main__":` 的第一行）：

    from clihelp import guard
    guard(sys.argv[1:], "fetch_art.py",
          "python3 fetch_art.py [流派…] [--per N] [--refresh]",
          ["不给流派名就补抓所有还没有图的流派。"])

只认 `-h` / `--help` 两种写法 —— 不认裸 `help`，因为那在某些脚本里是合法的
流派名/子命令（例如 `artvault.py help`）。
"""

import sys

HELP_FLAGS = ("-h", "--help")


def wants_help(argv):
    """argv 里是否出现了帮助标志。"""
    return any(a in HELP_FLAGS for a in argv)


def guard(argv, usage, notes=()):
    """出现帮助标志就打印用法并以 0 退出；否则什么都不做。

    参数顺序刻意是 (argv, usage, notes) —— usage 是必填的，忘了写会直接
    TypeError，不会静默退化成一个什么都不打印的 `--help`。
    """
    if not wants_help(argv):
        return False
    print("用法：%s" % usage)
    for n in notes:
        print("  %s" % n)
    print("\n不认识的参数不会被忽略：本脚本只认上面列出的选项。")
    sys.exit(0)
