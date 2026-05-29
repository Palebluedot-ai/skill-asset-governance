import subprocess
import sys
from pathlib import Path


def test_build_report_uses_registry_when_root_has_no_skill_files(tmp_path):
    repo_root = tmp_path
    registry = repo_root / "registry" / "skill-index.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        """
skills:
  - name: alpha-skill
    domain: demo
    status: active
    version: 1.2.3
    owner: curator
    canonical: true
    source_path: /external/alpha/SKILL.md
  - name: beta-skill
    domain: demo
    status: active
    version: 0.0.0
    owner: curator
    canonical: true
    source_path: /external/beta/SKILL.md
""".lstrip(),
        encoding="utf-8",
    )

    script = Path(__file__).resolve().parents[1] / "scripts" / "build_skill_report.py"
    out = repo_root / "reports" / "skill-report.md"

    result = subprocess.run(
        [sys.executable, str(script), "--root", str(repo_root), "--out", "reports/skill-report.md"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    report = out.read_text(encoding="utf-8")
    assert "Source: `registry/skill-index.yaml`" in report
    assert "Total skills: 2" in report
    assert "| alpha-skill | demo | active | 1.2.3 | `/external/alpha/SKILL.md` |" in report
    assert "| beta-skill | demo | active | 0.0.0 | `/external/beta/SKILL.md` |" in report
