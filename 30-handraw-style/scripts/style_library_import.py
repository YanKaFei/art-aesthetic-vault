#!/usr/bin/env python3
"""Shared helpers for adding a numbered style to the local style library."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from contact_sheet_registry import append_style
from style_asset_paths import ROOT, asset_dir, bucket_name, grid_path, single_path


SKILL_DIR = ROOT / "skills" / "handdraw-style-prompter"
SOURCE_MD = ROOT / "styles_200_reorganized.md"
MODEL_CAP = SKILL_DIR / "references" / "model_capabilities.json"
BUILD_SCRIPT = SKILL_DIR / "scripts" / "build_library.py"
VALIDATE_SCRIPT = SKILL_DIR / "scripts" / "validate_library.py"
ACTIVATIONS = {"strong", "weak", "none", "unknown"}


def get_next_style_number() -> str:
    """Return the next contiguous three-digit library number."""
    rows = re.findall(r"^\|\s*(\d{3})\s*·", SOURCE_MD.read_text(encoding="utf-8"), re.MULTILINE)
    return f"{max((int(row) for row in rows), default=0) + 1:03}"


def create_4grid_image(image_paths: list[Path], output_path: Path) -> None:
    """Write a 1024px 2×2 reference grid from two to four source images."""
    if len(image_paths) < 2:
        raise ValueError("A reference grid requires at least two source images.")
    selected = list(image_paths[:4])
    selected.extend([selected[-1]] * (4 - len(selected)))
    canvas = Image.new("RGB", (1024, 1024), (255, 255, 255))
    for path, position in zip(selected, ((0, 0), (512, 0), (0, 512), (512, 512))):
        with Image.open(path) as image:
            canvas.paste(image.convert("RGB").resize((512, 512), Image.Resampling.LANCZOS), position)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="WEBP", quality=90, method=6)


def create_numbered_tile(source_path: Path, number: str, output_path: Path, badge_label: str | None) -> None:
    """Write a 512px gallery tile with an optional top-left badge."""
    with Image.open(source_path) as source:
        image = source.convert("RGB").resize((512, 512), Image.Resampling.LANCZOS)
    if badge_label:
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
        except Exception:
            font = ImageFont.load_default()
        bbox = font.getbbox(badge_label)
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x, y = 14, 14
        draw.rounded_rectangle((x - 8, y - 4, x + width + 8, y + height + 8), radius=6,
                               fill=(255, 255, 255), outline=(200, 195, 185), width=1)
        draw.text((x, y - bbox[1]), badge_label, font=font, fill=(20, 20, 20))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="WEBP", quality=90, method=6)


def create_style_assets(number: str, source_images: list[Path], badge_label: str | None) -> dict[str, Path | None]:
    """Create per-style assets and append the resulting tile to the active sheet."""
    if not source_images:
        raise ValueError("At least one source image is required.")
    destination_dir = asset_dir(number)
    destination_dir.mkdir(parents=True, exist_ok=True)
    grid = grid_path(number)
    tile = single_path(number)
    if len(source_images) >= 2:
        create_4grid_image(source_images, grid)
    elif grid.exists():
        grid.unlink()
    create_numbered_tile(source_images[0], number, tile, badge_label)
    return {
        "directory": destination_dir,
        "grid": grid if len(source_images) >= 2 else None,
        "tile": tile,
        "sheet": append_style(int(number)),
    }


def update_markdown_source(number: str, source_name: str, generation_name: str, traits: str) -> None:
    content = SOURCE_MD.read_text(encoding="utf-8")
    if re.search(rf"^\|\s*{re.escape(number)}\s*·", content, re.MULTILINE):
        raise ValueError(f"Style #{number} already exists in styles_200_reorganized.md")
    content = re.sub(r"# \d+ 种人物 IP 手绘风格库", f"# {int(number)} 种人物 IP 手绘风格库", content, count=1)
    SOURCE_MD.write_text(content.rstrip() + f"\n\n| {number} · {source_name} | {generation_name} | {traits} |\n", encoding="utf-8")


def _sheet_lines(prefix: str) -> str:
    lines: list[str] = []
    for path in sorted((ROOT / "images").glob(f"{prefix}_*.webp")):
        match = re.match(rf"^{prefix}_(\d{{3}})(?:-(\d{{3}}))?\.webp$", path.name)
        if match:
            start, end = match.group(1), match.group(2) or match.group(1)
            label = f"{prefix} {start}–{end}" if start != end else f"{prefix} {start}"
            lines.append(f"![{label}](images/{path.name})")
    return "\n\n".join(lines)


def update_readme_and_skill(number: str) -> None:
    """Refresh mutable range labels and G/H board references."""
    readme_path = ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    content = re.sub(r"001–\d+ 种手绘风格", f"001–{number} 种手绘风格", content)
    content = re.sub(r"### G · 附件新增 / 中国当代插画补充（201–\d+）", "### G · 附件新增 / 中国当代插画补充（201–216）", content)
    content = re.sub(r"### H · 其他（217–\d+）", f"### H · 其他（217–{number}）", content)
    for prefix, title in (("G", "### G · 附件新增 / 中国当代插画补充"), ("H", "### H · 其他")):
        pattern = re.compile(rf"({re.escape(title)}[^\n]*\n\n)(?:!\[{prefix} [^\]]+\]\(images/{prefix}_[^)]+\.webp\)\n*\s*)+", re.MULTILINE)
        content = pattern.sub(r"\1" + _sheet_lines(prefix) + "\n\n", content)
    readme_path.write_text(content.strip() + "\n", encoding="utf-8")

    for path in (ROOT / "SKILL.md", SKILL_DIR / "SKILL.md"):
        content = path.read_text(encoding="utf-8")
        content = re.sub(r"001–\d+", f"001–{number}", content)
        content = re.sub(r"`001`–`\d+`", f"`001`–`{number}`", content)
        path.write_text(content, encoding="utf-8")


def update_manifest(number: str) -> None:
    """Keep the human-readable package manifest aligned with the current range."""
    path = ROOT / "MANIFEST.md"
    content = path.read_text(encoding="utf-8")
    content = re.sub(r"当前 \d+ 风格表", f"当前 {int(number)} 风格表", content)
    boards = [f"- `{entry.name}`" for entry in sorted((ROOT / "images").glob("[A-H]_*.webp"))]
    content = re.sub(r"(## 已收录图片\n\n).*?(\n\n## 单张图片)", r"\1" + "\n".join(boards) + r"\2", content, flags=re.DOTALL)
    bucket = bucket_name(number)
    content = re.sub(r"images/individual/201-400/201\.webp`–`images/individual/\d{3}-\d{3}/\d{3}\.webp`：201–\d+ 的编号单图",
                     f"images/individual/201-400/201.webp`–`images/individual/{bucket}/{number}.webp`：201–{number} 的编号单图", content)
    content = re.sub(r"H：217–\d+，完整（其他）", f"H：217–{number}，完整（其他）", content)
    content = re.sub(r"单图总数：\d+ 张", f"单图总数：{int(number)} 张", content)
    content = re.sub(r"风格编号覆盖：001–\d+", f"风格编号覆盖：001–{number}", content)
    path.write_text(content, encoding="utf-8")


def update_model_capabilities(number: str, *, name_activation: str, traits_activation: str) -> None:
    if name_activation not in ACTIVATIONS or traits_activation not in ACTIVATIONS:
        raise ValueError("Unsupported model activation value.")
    data = json.loads(MODEL_CAP.read_text(encoding="utf-8"))
    styles = data["models"]["gpt-image-2"].setdefault("styles", {})
    styles[number] = {"name_activation": name_activation, "traits_activation": traits_activation}
    MODEL_CAP.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def rebuild_and_validate() -> None:
    python = [sys.executable, "-X", "utf8"]
    subprocess.run(python + [str(BUILD_SCRIPT)], check=True)
    subprocess.run(python + [str(VALIDATE_SCRIPT)], check=True)
