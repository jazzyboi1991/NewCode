"""Repository-root launcher for ``python -m goodthink``.

The reference implementation lives in ``Python/``.  This small launcher keeps
the command independent of whether the user is currently in the repository
root or in the implementation directory.
"""

from pathlib import Path
import sys


PYTHON_DIR = Path(__file__).resolve().parent / "Python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from newcode.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
