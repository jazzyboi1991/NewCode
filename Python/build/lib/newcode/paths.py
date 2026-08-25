from pathlib import Path, PurePosixPath

from newcode.errors import fail


def safe_relative_path(raw, span):
    """Return a normalized Newcode-relative path or raise FILECRIME."""
    if not isinstance(raw, str) or not raw or "\\" in raw:
        raise fail("FILECRIME", "only safe relative paths are allowed", span)

    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts:
        raise fail("FILECRIME", "only safe relative paths are allowed", span)
    return "." if str(path) == "." else str(path)


def safe_file_path(root, raw, span):
    relative = safe_relative_path(raw, span)
    root = Path(root).resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise fail("FILECRIME", "only safe relative paths are allowed", span)
    return path
