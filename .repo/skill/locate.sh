#!/usr/bin/env bash
# 定位艺术审美风格库的根目录。找到就打印路径（退出码 0），否则退出码 1。
#
# 查找顺序：
#   1. $ARTVAULT 环境变量
#   2. 本脚本的真实位置（软链安装时，往上两级就是仓库根）
#   3. 当前目录或父目录里的 .repo/artvault.py
#   4. 常见 clone 位置
set -e

# 1) 环境变量
if [ -n "$ARTVAULT" ] && [ -f "$ARTVAULT/.repo/artvault.py" ]; then
  echo "$ARTVAULT"; exit 0
fi

# 2) 脚本自身位置（-P 解析软链，这是软链安装能自动工作的关键）
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
for cand in "$(dirname "$SELF")" "$(dirname "$(dirname "$SELF")")"; do
  if [ -f "$cand/.repo/artvault.py" ]; then echo "$cand"; exit 0; fi
done

# 3) 从当前目录往上找
d="$PWD"
while [ "$d" != "/" ]; do
  if [ -f "$d/.repo/artvault.py" ]; then echo "$d"; exit 0; fi
  d="$(dirname "$d")"
done

# 4) 常见位置
for cand in \
  "$HOME/Desktop/art-aesthetic-vault" \
  "$HOME/Desktop/艺术审美风格0912" \
  "$HOME/art-aesthetic-vault" \
  "$HOME/Documents/art-aesthetic-vault" \
  "$HOME/repos/art-aesthetic-vault" ; do
  if [ -f "$cand/.repo/artvault.py" ]; then echo "$cand"; exit 0; fi
done

exit 1
