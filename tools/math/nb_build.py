"""Build Jupyter notebooks from Python cell descriptors.

A probe is a dict:
    {"kind": "markdown"|"code", "source": "..."}
Cell source can include newlines; final source ends with a trailing newline.

Build API:
    build_notebook(probes, path, title="...")
    execute_notebook(path)   # runs nbconvert --execute inplace, returns (rc, output)

CLI:
    python -m tools.math.nb_build <path/to/gen.py> <notebook.ipynb>
The gen.py module must define:
    PROBES: list[dict]   # cell descriptor list
    TITLE: str           # optional notebook title
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

KERNEL_SPEC = {
    "display_name": "Python 3 (ipykernel)",
    "language": "python",
    "name": "python3",
}
LANGUAGE_INFO = {
    "name": "python",
    "version": "3.10",
    "mimetype": "text/x-python",
    "file_extension": ".py",
    "pygments_lexer": "ipython3",
    "codemirror_mode": {"name": "ipython", "version": 3},
    "nbconvert_exporter": "python",
}


def build_notebook(probes, path, title=""):
    cells = []
    for p in probes:
        kind = p.get("kind", "markdown")
        source = p.get("source", "")
        if not source.endswith("\n"):
            source = source + "\n"
        if kind == "code":
            cells.append(new_code_cell(source))
        else:
            cells.append(new_markdown_cell(source))
    nb = new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": KERNEL_SPEC,
        "language_info": LANGUAGE_INFO,
        "title": title,
    }
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        nbformat.write(nb, fh, version=nbformat.NO_CONVERT)
    return out_path


def execute_notebook(path, timeout=600):
    """Run nbconvert --execute inplace; return (returncode, combined_output)."""
    cmd = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout={timeout}",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout + res.stderr


def _load_gen_module(gen_path):
    spec = importlib.util.spec_from_file_location("gen", gen_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python -m tools.math.nb_build <gen.py> <notebook.ipynb>",
            file=sys.stderr,
        )
        sys.exit(2)
    gen_path = Path(sys.argv[1]).resolve()
    out_path = sys.argv[2]
    mod = _load_gen_module(gen_path)
    probes = getattr(mod, "PROBES")
    title = getattr(mod, "TITLE", "")
    build_notebook(probes, out_path, title=title)
    print(f"Built {out_path}")


if __name__ == "__main__":
    main()