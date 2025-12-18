import ast
import json
from typing import List, Optional


def _normalize_level_grid(
    grid: List[List[int]],
    *,
    expected_width: Optional[int],
    expected_height: Optional[int],
    fill: int = 0,
) -> List[List[int]]:
    if expected_width is None or expected_height is None:
        return grid

    normalized: List[List[int]] = []
    for y in range(expected_height):
        if y < len(grid) and isinstance(grid[y], list):
            row = grid[y]
        else:
            row = []

        new_row = [fill for _ in range(expected_width)]
        for x in range(min(expected_width, len(row))):
            cell = row[x]
            new_row[x] = cell if isinstance(cell, int) else fill
        normalized.append(new_row)

    return normalized


def load_level_from_txt(
    path: str,
    *,
    fallback: List[List[int]],
    expected_width: Optional[int] = None,
    expected_height: Optional[int] = None,
) -> List[List[int]]:
    """Load a level grid from a Python-style `level.txt` file.

    The file is expected to contain an assignment like:
        level = [[...], [...], ...]

    Returns `fallback` if the file is missing, invalid, or mismatched size.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            source = file.read()
        tree = ast.parse(source, filename=path)

        level_node = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "level":
                        level_node = node.value
                        break
            if level_node is not None:
                break

        if level_node is None:
            return fallback

        loaded = ast.literal_eval(level_node)
        if not isinstance(loaded, list) or not loaded:
            return fallback
        if not all(isinstance(row, list) for row in loaded):
            return fallback
        if not all(all(isinstance(cell, int) for cell in row) for row in loaded):
            return fallback

        height = len(loaded)
        width = len(loaded[0])
        if any(len(row) != width for row in loaded):
            return fallback

        if expected_height is not None and height != expected_height:
            return fallback
        if expected_width is not None and width != expected_width:
            return fallback

        return loaded
    except FileNotFoundError:
        return fallback


def load_level_from_json(
    path: str,
    *,
    fallback: List[List[int]],
    expected_width: Optional[int] = None,
    expected_height: Optional[int] = None,
    normalize_to_expected: bool = True,
    fill: int = 0,
) -> List[List[int]]:
    """Load a level grid from a JSON file.

    Expected JSON format is a list of rows, where each row is a list of ints.
    Returns `fallback` if missing/invalid.

    If normalize_to_expected is True and expected sizes are provided, the grid
    will be padded/cropped to match those dimensions.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            loaded = json.load(file)

        if not isinstance(loaded, list) or not loaded:
            return fallback
        if not all(isinstance(row, list) for row in loaded):
            return fallback

        # Validate ints (best-effort; normalization can also coerce non-ints)
        if not all(all(isinstance(cell, int) for cell in row) for row in loaded):
            if not normalize_to_expected:
                return fallback

        if normalize_to_expected and expected_width is not None and expected_height is not None:
            return _normalize_level_grid(
                loaded,
                expected_width=expected_width,
                expected_height=expected_height,
                fill=fill,
            )

        height = len(loaded)
        width = len(loaded[0])
        if any(len(row) != width for row in loaded):
            return fallback

        if expected_height is not None and height != expected_height:
            return fallback
        if expected_width is not None and width != expected_width:
            return fallback

        return loaded
    except FileNotFoundError:
        return fallback
    except Exception:
        return fallback
    except Exception:
        return fallback


def save_level_to_txt(path: str, level: List[List[int]]) -> None:
    """Save a level grid to a Python-style `level.txt` file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write("level = [\n")
        for row in level:
            file.write(f"    {row},\n")
        file.write("]\n")
