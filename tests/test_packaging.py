from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseGate(unittest.TestCase):
    def test_unverified_build_cannot_be_packaged_as_stable(self):
        for target in ("1.13", "1.14"):
            with self.subTest(target=target):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/package.py"), "--target", target],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("unverified", result.stderr)


if __name__ == "__main__":
    unittest.main()
