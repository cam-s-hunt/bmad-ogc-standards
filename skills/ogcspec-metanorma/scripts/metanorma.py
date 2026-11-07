#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""metanorma: compile an AsciiDoc file with a pinned local Docker image. Never pulls.

The image must already exist locally and be named by digest (repo@sha256:...). Pulling is a network
call and is a deliberate human step, so a missing image is an error here, not something to fix.

Usage:
  metanorma.py --image <repo@sha256:...> --adoc <file.adoc> [--formats xml,html]

Exit codes: 0 compiled; 2 usage error; 3 docker or the image is unavailable; otherwise the
compiler's own exit code. Stdout is one JSON object with the command, exit code and the raw log (also
for exit 3). Before compiling, the previous <stem>.xml, <stem>.xml.abort and <stem>.err.html are deleted so
a failed compile cannot be mistaken for an earlier success. The container runs with --network none unless
--network says otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DIGEST_RE = re.compile(r"^[\w./-]+@sha256:[0-9a-f]{64}$")


def image_present(image: str) -> bool:
    try:
        return subprocess.run(["docker", "image", "inspect", image], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def build_command(image: str, adoc: Path, formats: str, network: str = "none", root: Path | None = None) -> list[str]:
    """`root` is the directory mounted into the container and used as the compiler's working directory.
    Asciidoctor refuses includes that climb above that directory ("illegal reference to ancestor of jail"),
    so a document that includes files from outside its own folder must be compiled with `root` set to a
    directory containing them all. Default: the document's own folder."""
    mount = (root or adoc.parent).resolve()
    target = adoc.resolve().relative_to(mount).as_posix()
    return [
        "docker", "run", "--rm", "--network", network, "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
        "-v", f"{mount}:/work", "-w", "/work", image,
        "metanorma", "compile", "--agree-to-terms", "-t", "ogc", "-x", formats, target,
    ]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Compile with a pinned local Metanorma image.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--adoc", required=True, type=Path)
    parser.add_argument("--formats", default="xml")
    parser.add_argument("--root", type=Path, help="directory to mount (default: the document's folder); needed when the "
                        "document includes files from outside its own folder")
    parser.add_argument("--network", default="none", help="docker network mode (default none: compiles offline)")
    args = parser.parse_args(argv)
    if not DIGEST_RE.match(args.image):
        print("--image must be pinned by digest: repo@sha256:<64 hex>", file=sys.stderr)
        return 2
    if not args.adoc.is_file():
        print(f"not found: {args.adoc}", file=sys.stderr)
        return 2
    if args.root is not None:
        try:
            args.adoc.resolve().relative_to(args.root.resolve())
        except ValueError:
            print(f"--root {args.root} does not contain {args.adoc}", file=sys.stderr)
            return 2
    if not image_present(args.image):
        message = f"image not available locally (this script never pulls): {args.image}"
        print(message, file=sys.stderr)
        print(json.dumps({"command": [], "exit": 3, "stdout": "", "stderr": message}, indent=2))
        return 3
    for suffix in (".xml", ".xml.abort", ".err.html"):  # a failed compile must not leave last build's output behind
        args.adoc.with_suffix(suffix).unlink(missing_ok=True)
    command = build_command(args.image, args.adoc, args.formats, args.network, args.root)
    result = subprocess.run(command, capture_output=True, text=True)
    print(json.dumps({"command": command, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, indent=2))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
