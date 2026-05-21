#!/usr/bin/env python3
"""
Recursive converter: .ipynb -> .py (folder support)

Usage:
    python ipynb_to_py.py notebook.ipynb
    python ipynb_to_py.py /path/to/folder
"""

import json
import argparse
from pathlib import Path
import sys

def ipynb_to_py(ipynb_path: Path) -> str:
    data = json.loads(ipynb_path.read_text(encoding="utf-8"))
    cells = data.get("cells", [])
    lines = []
    for cell in cells:
        c_type = cell.get("cell_type", "")
        source = cell.get("source", [])
        src = "".join(source)
        if c_type == "markdown":
            for ln in src.splitlines():
                lines.append("# " + ln if ln.strip() else "#")
            lines.append("")  # blank line after cell
        elif c_type == "code":
            for ln in src.splitlines():
                if ln.startswith("%%") or ln.startswith("%"):
                    lines.append("# " + ln)
                else:
                    lines.append(ln)
            lines.append("")  # blank line after cell
        else:
            for ln in src.splitlines():
                lines.append("# " + ln)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def convert_ipynb_file(ipynb_path: Path):
    try:
        py_text = ipynb_to_py(ipynb_path)

        # Calculate the output path to retain the directory structure
        out_path = ipynb_path.with_suffix('.py')

        # Create any necessary directories for the output file
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the converted .py file
        out_path.write_text(py_text, encoding="utf-8")
        print(f"Wrote {out_path}")
        ipynb_path.unlink()  # Remove the original .ipynb file
    except Exception as e:
        print(f"Conversion failed for {ipynb_path}: {e}", file=sys.stderr)

def process_directory(directory: Path):
    for item in directory.rglob('*.ipynb'):
        convert_ipynb_file(item)

def main():
    p = argparse.ArgumentParser(description="Convert Jupyter .ipynb to .py")
    p.add_argument("path", type=Path, help="Input .ipynb file or folder")
    args = p.parse_args()

    input_path = args.path
    if not input_path.exists():
        print(f"Error: {input_path} not found.", file=sys.stderr)
        sys.exit(2)

    if input_path.is_file() and input_path.suffix == '.ipynb':
        convert_ipynb_file(input_path)
    elif input_path.is_dir():
        process_directory(input_path)
    else:
        print("Error: Input must be a .ipynb file or a directory containing .ipynb files.", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
