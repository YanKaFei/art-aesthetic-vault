#!/usr/bin/env bash
# 推送到 GitHub —— 已由 .repo/github_setup.py 取代。
#
# 这个文件只做**转发**，不再自己实现推送逻辑。原因：它原来写死了
#   REPO="SaltCoffee/art-aesthetic-vault"
# 而 SaltCoffee 是 GitHub 显示名、不是用户名 —— 实测该地址返回 404，
# 照着跑会推到不存在的仓库。同一份信息在两处各写一遍就会这样漂移。
# github_setup.py 的仓库地址是从 `git remote` 推导的（fork 后不用改），
# 并且 token 不进命令行参数、还顺带做 Template / topics / description。
#
# 用法：
#   ./push-to-github.sh              # 等价于 github_setup.py all
#   ./push-to-github.sh status       # 只看远程现状（不需要 token）
#   ./push-to-github.sh push         # 只推送
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="${1:-all}"
shift 2>/dev/null || true
exec python3 "$HERE/.repo/github_setup.py" "$CMD" "$@"
