"""Static checks: syntax subset, generated artifacts, references and safety gates."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))
from script_runtime import definitions, parse
from generate import outputs


def main():
    for path in (ROOT / "mod").rglob("*.txt"):
        parse(path.read_text(encoding="utf-8-sig"))
    for name, content in outputs().items():
        if (ROOT / name).read_text(encoding="utf-8") != content:
            raise ValueError(f"Stale generated file: {name}; run tools/generate.py")
    categories = ("scripted_effects", "scripted_triggers", "script_values", "scripted_buttons", "journal_entries")
    groups = {name: definitions(name) for name in categories}
    if groups["scripted_triggers"]["mc_backend_ready"] != [("always", "=", "no")]:
        raise ValueError("Live backend must remain fail closed until implemented and game-tested")
    defined = {key for group in groups.values() for key in group}
    used = set()
    for path in (ROOT / "mod/common").rglob("*.txt"):
        text = re.sub(r"#[^\n]*", "", path.read_text())
        used.update(re.findall(r"\b(mc_[a-z0-9_]+)\s*=\s*yes\b", text))
    if used - defined:
        raise ValueError(f"Undefined script calls: {sorted(used - defined)}")
    expected_loc = {"mc_je", "mc_je_reason", "mc_je_status"}
    for button in groups["scripted_buttons"].values():
        expected_loc.update(v for k, _, v in button if k in ("name", "desc"))
    for path in (ROOT / "mod/localization").rglob("*.yml"):
        data = path.read_bytes()
        if not data.startswith(b"\xef\xbb\xbf"):
            raise ValueError(f"Missing UTF-8 BOM: {path}")
        keys = re.findall(r"^ (\w+):0 ", data.decode("utf-8-sig"), re.M)
        if len(keys) != len(set(keys)) or expected_loc - set(keys):
            raise ValueError(f"Duplicate or missing localization: {path}")
    for path in (ROOT / "mod").rglob("*.txt"):
        if re.search(r"\b(remove_building|kill_population|create_military_formation|destroy_container)\s*=", path.read_text()):
            raise ValueError(f"Destructive/unverified military operation in shipping sandbox: {path}")
    print(f"Validated {len(defined)} namespaced definitions, generated files, localization and closed military gate.")


if __name__ == "__main__":
    main()
