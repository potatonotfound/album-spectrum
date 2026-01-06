from PIL import Image
import numpy as np
from pathlib import Path
import colorsys
import math
import string
import json
import sys
from typing import List, Tuple, Optional, TypedDict


class Config(TypedDict):
    input_directory: str
    output_directory: str
    ordering_directory: str
    resolution: int
    ordered: bool


def resolve_path(path_str: str) -> Path:
    base_path: Path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    path: Path = Path(path_str)
    if path.is_absolute():
        return path
    return (base_path / path).resolve()


def load_config() -> Config:
    base_path: Path = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
    config_path: Path = base_path / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r") as f:
        config: Config = json.load(f)
    return config


def validate_config(config: Config) -> None:
    input_dir: Path = resolve_path(config["input_directory"])
    if not input_dir.is_dir():
        raise ValueError(f"input_directory '{input_dir}' does not exist or is not a directory")
    if config["resolution"] <= 0:
        raise ValueError("resolution must be positive")


def average_color(path: str) -> Tuple[int, int, int]:
    img: Image.Image = Image.open(path).convert("RGB")
    arr: np.ndarray = np.array(img)
    avg: np.ndarray = arr.mean(axis=(0, 1))
    return tuple(avg.astype(int))  # type: ignore


def rgb_to_hls(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    r, g, b = (x / 255.0 for x in rgb)
    return colorsys.rgb_to_hls(r, g, b)


def create_image_grid(
    grid: List[List[Optional[str]]],
    thumb_size: Tuple[int, int]
) -> Image.Image:
    N_rows: int = len(grid)
    N_cols: int = len(grid[0])
    out_img: Image.Image = Image.new(
        "RGB",
        (N_cols * thumb_size[0], N_rows * thumb_size[1])
    )
    for i, row in enumerate(grid):
        for j, img_path in enumerate(row):
            if img_path:
                img: Image.Image = Image.open(img_path).resize(thumb_size)
                out_img.paste(img, (j * thumb_size[0], i * thumb_size[1]))
    return out_img


def index_to_letters(idx: int) -> str:
    letters: str = string.ascii_lowercase
    result: str = ""
    while True:
        result = letters[idx % 26] + result
        idx = idx // 26 - 1
        if idx < 0:
            break
    return result


def main() -> None:
    config: Config = load_config()
    validate_config(config)

    folder_path: Path = resolve_path(config["input_directory"])
    output_dir: Path = resolve_path(config["output_directory"])
    ordering_dir: Path = resolve_path(config["ordering_directory"])

    resolution: int = config["resolution"]
    ordered: bool = config["ordered"]

    images: List[List[object]] = []

    for file in folder_path.iterdir():
        if file.is_file():
            file_path: str = str(file)
            avg_rgb: Tuple[int, int, int] = average_color(file_path)
            h, l, s = rgb_to_hls(avg_rgb)
            images.append([h, l, s, file_path])

    images.sort(key=lambda x: (x[0], -x[1]))

    N: int = int(math.ceil(len(images) ** 0.5))
    grid: List[List[Optional[str]]] = [[None for _ in range(N)] for _ in range(N)]

    for idx, img_data in enumerate(images):
        col: int = idx // N
        row: int = idx % N
        if col < N and row < N:
            grid[row][col] = img_data[3]  # type: ignore

    for c in range(N):
        column: List[str] = [grid[r][c] for r in range(N) if grid[r][c] is not None]
        column.sort(key=lambda path: -rgb_to_hls(average_color(path))[1])
        for r, img_path in enumerate(column):
            grid[r][c] = img_path

    out_img: Image.Image = create_image_grid(grid, (resolution, resolution))
    output_dir.mkdir(exist_ok=True)
    out_img.save(output_dir / "final.png")
    out_img.show()

    if ordered:
        ordering_dir.mkdir(exist_ok=True)
        for r, row in enumerate(grid):
            for c, img_path in enumerate(row):
                if img_path:
                    img: Image.Image = Image.open(img_path).convert("RGB")
                    new_name: str = f"{index_to_letters(r)}{index_to_letters(c)}.jpg"
                    img.save(ordering_dir / new_name, format="JPEG")


if __name__ == "__main__":
    main()
