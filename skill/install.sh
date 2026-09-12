#!/usr/bin/env bash
# 把「艺术审美风格库」查询 skill 装到本机所有可用的 skill 目录。
#
#   ./install.sh              软链安装（推荐，仓库移动也能自动找到）
#   ./install.sh --copy       复制安装（不依赖软链，但仓库移动后失效）
#   ./install.sh --uninstall  卸载
#   ./install.sh --dry-run    只显示会做什么
#
# 支持的目录（存在才装）：
#   ~/.agents/skills   DSH / Codex / 通用
#   ~/.claude/skills   Claude Code
#   ~/.codex/skills    Codex
set -euo pipefail

SKILL_NAME="art-aesthetic-vault"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(dirname "$SKILL_DIR")"

MODE="link"; DRY=0
case "${1:-}" in
  --copy)      MODE="copy" ;;
  --uninstall) MODE="remove" ;;
  --dry-run)   DRY=1 ;;
  "") ;;
  *) echo "未知参数: $1"; exit 1 ;;
esac

# 自检：确认这真的在一个仓库里
if [ ! -f "$REPO_ROOT/_scripts/artvault.py" ]; then
  echo "✗ 找不到 $REPO_ROOT/_scripts/artvault.py"
  echo "  这个脚本应该放在仓库内的 skill/ 目录里运行。"
  exit 1
fi

TARGETS=()
for base in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  if [ -d "$base" ]; then TARGETS+=("$base"); fi
done
# ~/.agents/skills 即便不存在也建一个（那是通用位置）
if [ ! -d "$HOME/.agents/skills" ]; then
  TARGETS+=("$HOME/.agents/skills")
fi

if [ ${#TARGETS[@]} -eq 0 ]; then
  echo "✗ 没找到任何可用的 skill 目录"; exit 1
fi

echo "仓库根目录: $REPO_ROOT"
echo "skill 名称: $SKILL_NAME"
echo "模式:       $MODE"
echo

for base in "${TARGETS[@]}"; do
  dest="$base/$SKILL_NAME"
  case "$MODE" in
    remove)
      if [ -e "$dest" ] || [ -L "$dest" ]; then
        echo "  卸载 $dest"
        [ "$DRY" = 0 ] && rm -rf "$dest"
      else
        echo "  跳过 $dest（未安装）"
      fi
      ;;
    link|copy)
      echo "  安装 → $dest"
      if [ "$DRY" = 1 ]; then continue; fi
      mkdir -p "$base"
      # 已存在：先判断是不是指向本仓库的旧软链
      if [ -L "$dest" ]; then
        rm -f "$dest"
      elif [ -e "$dest" ]; then
        bak="$dest.bak.$(date +%Y%m%d%H%M%S)"
        echo "    （已存在，备份到 $(basename "$bak")）"
        mv "$dest" "$bak"
      fi
      if [ "$MODE" = "link" ]; then
        ln -s "$SKILL_DIR" "$dest"
      else
        cp -R "$SKILL_DIR" "$dest"
      fi
      ;;
  esac
done

echo
if [ "$MODE" = "remove" ]; then
  echo "✓ 已卸载"
else
  echo "✓ 完成。验证："
  echo "    bash \"$SKILL_DIR/locate.sh\"     # 应打印 $REPO_ROOT"
  echo
  echo "  新建一个 AI 会话后，skill 才会出现在可用列表里。"
  [ "$MODE" = "copy" ] && echo "  ⚠ 复制模式：仓库移动后需重跑本脚本。"
fi
