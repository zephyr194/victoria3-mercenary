"""Build explicitly experimental, version-specific mod archives."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("1.13", "1.14"), required=True)
    parser.add_argument("--experimental", action="store_true")
    args = parser.parse_args()
    status = json.loads((ROOT / "compatibility.json").read_text())
    if not args.experimental:
        parser.error("Military backend and game compatibility unverified; use --experimental only")
    subprocess.run([sys.executable, str(ROOT / "tools/validate.py")], check=True)
    descriptor = f'''name="Mercenary Contracts {args.target} (Sandbox Development Preview)"
version="{status['version']}"
supported_version="{args.target}.*"
tags={{ "Gameplay" "Military" }}
'''
    output = ROOT / f"dist/mc-mercenary-{args.target}-experimental.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("mc_mercenary.mod", descriptor + 'path="mod/mc_mercenary"\n')
        archive.writestr("mc_mercenary/descriptor.mod", descriptor)
        for path in sorted((ROOT / "mod").rglob("*")):
            if path.is_file():
                archive.write(path, Path("mc_mercenary") / path.relative_to(ROOT / "mod"))
        archive.write(ROOT / "docs/INSTALL_TEST.zh-CN.md", "INSTALL_TEST.zh-CN.md")
    print(output)


if __name__ == "__main__":
    main()
