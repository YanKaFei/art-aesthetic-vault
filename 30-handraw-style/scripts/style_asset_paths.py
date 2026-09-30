"""Canonical paths for numbered style-generation assets."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDIVIDUAL_ROOT = ROOT / "images" / "individual"
BUCKET_SIZE = 200


def number_value(number: str | int) -> int:
    value = int(number)
    if value < 1:
        raise ValueError("Style number must be positive.")
    return value


def bucket_name(number: str | int) -> str:
    value = number_value(number)
    start = ((value - 1) // BUCKET_SIZE) * BUCKET_SIZE + 1
    return f"{start:03}-{start + BUCKET_SIZE - 1:03}"


def asset_dir(number: str | int) -> Path:
    return INDIVIDUAL_ROOT / bucket_name(number)


def single_path(number: str | int) -> Path:
    return asset_dir(number) / f"{number_value(number):03}.webp"


def grid_path(number: str | int) -> Path:
    return asset_dir(number) / f"{number_value(number):03}_grid.webp"
