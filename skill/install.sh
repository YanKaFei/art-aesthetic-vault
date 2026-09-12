#!/usr/bin/env bash
# 安装本仓库提供的 AI skill 到本机所有可用的 skill 目录。
#
#   ./install.sh              软链安装（推荐，仓库移动也能自动找到）
#   ./install.sh --copy       复制安装（不依赖软链，但仓库移动后失效）
#   ./install.sh --uninstall  卸载
#   ./install.sh --dry-run    只显示会做什么
#
# 装两个 skill：
#   art-aesthetic-vault       查库：检索流派、取七层提示词、跨流派拼提示词
#   build-art-aesthetic-vault 建库：从零建一套新的（数据取自本仓库，不自带副本）
#
# 支持的目录（存在才装）：
#   ~/.agents/skills   DSH / Codex / 通用
#   ~/.claude/skills   Claude Code
#   ~/.codex/skills    Codex
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(dirname "$SKILL_DIR")"

# 名称:源目录
SKILLS=(
  "art-aesthetic-vault:$SKILL_DIR"
  "build-art-aesthetic-vault:$SKILL_DIR/build"
)

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
  [ -d "$base" ] && TARGETS+=("$base")
done
[ -d "$HOME/.agents/skills" ] || TARGETS+=("$HOME/.agents/skills")

if [ ${#TARGETS[@]} -eq 0 ]; then
  echo "✗ 没找到任何可用的 skill 目录"; exit 1
fi

echo "仓库根目录: $REPO_ROOT"
echo "模式:       $MODE"
echo

for base in "${TARGETS[@]}"; do
  for entry in "${SKILLS[@]}"; do
    name="${entry%%:*}"; src="${entry#*:}"
    dest="$base/$name"
    case "$MODE" in
      remove)
        if [ -e "$dest" ] || [ -L "$dest" ]; then
          echo "  卸载 $dest"
          [ "$DRY" = 0 ] && rm -rf "$dest"
        else
          echo "  跳过 $name（未安装）"
        fi
        ;;
      link|copy)
        [ -d "$src" ] || { echo "  ✗ 源目录不存在: $src"; continue; }
        echo "  安装 $name → $dest"
        [ "$DRY" = 1 ] && continue
        mkdir -p "$base"
        if [ -L "$dest" ]; then
          rm -f "$dest"
        elif [ -e "$dest" ]; then
          # 已存在实体目录：如果是本仓库的旧副本就替换，
          # 否则备份，避免覆盖用户自己放的东西
          if [ -f "$dest/SKILL.md" ] && grep -q "艺术审美风格库\|art-aesthetic-vault" "$dest/SKILL.md" 2>/dev/null; then
            rm -rf "$dest"
          else
            bak="$dest.bak.$(date +%Y%m%d%H%M%S)"
            echo "    （已存在他人内容，备份到 $(basename "$bak")）"
            mv "$dest" "$bak"
          fi
        fi
        if [ "$MODE" = "link" ]; then
          ln -s "$src" "$dest"
        else
          cp -R "$src" "$dest"
        fi
        ;;
    esac
  done
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
