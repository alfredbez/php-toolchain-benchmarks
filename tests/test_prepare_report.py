import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_report.py"


class PrepareReportTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "results").mkdir()
        (self.root / "workspace" / "psl").mkdir(parents=True)
        (self.root / ".benchmark-versions.json").write_text("[]")
        subprocess.run(["git", "init", "-q", "workspace/psl"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "-C", "workspace/psl", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "--allow-empty", "-qm", "fixture"],
            cwd=self.root,
            check=True,
        )

    def write_report(self, folder, project="psl", stamped=False):
        directory = self.root / "results" / folder
        directory.mkdir()
        report = {"generated": folder, "projects": {project: {"Cold": []}}}
        if stamped:
            report["environment"] = {"workflow_run": "old"}
        (directory / "report.json").write_text(json.dumps(report))

    def capture(self):
        env = os.environ | {"GITHUB_RUN_ID": "new", "GITHUB_SHA": "suite"}
        return subprocess.run(
            [sys.executable, str(SCRIPT), "psl"],
            cwd=self.root,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
        )

    def test_selects_new_report_beside_published_history(self):
        for project in ("psl", "wordpress", "magento"):
            self.write_report(f"36554743847-{project}", project, stamped=True)
        self.write_report("20261004-123000")
        self.write_report("20261004-123100", "wordpress")

        result = self.capture()

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.root / "artifact" / "report.json").read_text())
        self.assertEqual(report["generated"], "20261004-123000")
        self.assertEqual(report["environment"]["workflow_run"], "new")

    def test_rejects_multiple_new_reports(self):
        self.write_report("20261004-123000")
        self.write_report("20261004-123100")

        result = self.capture()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Expected one unstamped psl report, found 2", result.stderr)

    def test_rejects_only_published_history(self):
        self.write_report("36554743847-psl", stamped=True)

        result = self.capture()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Expected one unstamped psl report, found 0", result.stderr)


if __name__ == "__main__":
    unittest.main()
