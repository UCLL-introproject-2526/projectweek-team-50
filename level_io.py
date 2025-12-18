import ast
from typing import List, Optional


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
    except Exception:
        return fallback


def save_level_to_txt(path: str, level: List[List[int]]) -> None:
    """Save a level grid to a Python-style `level.txt` file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write("level = [\n")
        for row in level:
            file.write(f"    {row},\n")
        file.write("]\n")
