"""Tests for the rule-based skills behind the code review agent."""

import json
from pathlib import Path

from app.skills.quality_skill import QualitySkill
from app.skills.security_skill import SecuritySkill


def _ipynb(cells: list[list[str]]) -> str:
    return json.dumps({"cells": [{"cell_type": "code", "source": source} for source in cells]})


def test_security_skill_scans_notebook_code_cells(tmp_path: Path):
    nb = tmp_path / "analysis.ipynb"
    nb.write_text(_ipynb([["import os\n"], ["result = os.system('ls')\n"]]), encoding="utf-8")

    findings = SecuritySkill().scan_repository(str(tmp_path))

    assert any(f["file"] == "analysis.ipynb" and "os.system" in f["vulnerability"] for f in findings)


def test_security_skill_ignores_malformed_notebook(tmp_path: Path):
    (tmp_path / "broken.ipynb").write_text("{not valid json", encoding="utf-8")

    assert SecuritySkill().scan_repository(str(tmp_path)) == []


def test_security_skill_skips_non_scanned_extensions(tmp_path: Path):
    (tmp_path / "notes.md").write_text('api_key = "sk-super-secret-value-1234567890"', encoding="utf-8")

    assert SecuritySkill().scan_repository(str(tmp_path)) == []


def test_security_skill_file_filter_restricts_scan(tmp_path: Path):
    (tmp_path / "app.py").write_text('api_key = "sk-super-secret-value-1234567890"\n', encoding="utf-8")
    (tmp_path / "other.py").write_text('api_key = "sk-super-secret-value-0987654321"\n', encoding="utf-8")

    findings = SecuritySkill().scan_repository(str(tmp_path), files=["app.py"])

    assert [f["file"] for f in findings] == ["app.py"]


def test_security_skill_reports_scan_metadata(tmp_path: Path):
    (tmp_path / "app.py").write_text('api_key = "sk-super-secret-value-1234567890"\n', encoding="utf-8")

    result = SecuritySkill().scan_repository_with_meta(str(tmp_path))

    assert result["files_scanned"] == 1
    assert result["patterns_checked"] > 5
    assert len(result["findings"]) == 1


def test_security_skill_detects_path_traversal(tmp_path: Path):
    (tmp_path / "views.py").write_text(
        "with open(request.files['upload'].filename) as fh:\n    pass\n", encoding="utf-8"
    )
    (tmp_path / "config.py").write_text("base = os.path.join('static', user_input, 'file')\n", encoding="utf-8")

    findings = SecuritySkill().scan_repository(str(tmp_path))

    assert all(f["vulnerability"] == "Path Traversal Risk" for f in findings)
    assert all(f["severity"] == "HIGH" for f in findings)


def test_security_skill_detects_shell_injection(tmp_path: Path):
    (tmp_path / "run.py").write_text("subprocess.run(cmd, shell=True)\n", encoding="utf-8")

    findings = SecuritySkill().scan_repository(str(tmp_path))

    assert any(f["vulnerability"] == "Shell Injection Risk: subprocess shell=True" for f in findings)
    assert any(f["severity"] == "HIGH" for f in findings)


def test_security_skill_detects_unsafe_deserialization(tmp_path: Path):
    (tmp_path / "data.py").write_text("obj = pickle.loads(raw)\ncfg = yaml.load(text)\n", encoding="utf-8")

    findings = SecuritySkill().scan_repository(str(tmp_path))
    titles = [f["vulnerability"] for f in findings]

    assert "Insecure Deserialization: pickle" in titles
    assert "Unsafe YAML Deserialization" in titles


def test_security_skill_detects_weak_hash_and_disabled_tls(tmp_path: Path):
    (tmp_path / "crypto.py").write_text(
        "h = hashlib.md5(data)\nsession = requests.get(url, verify=False)\n",
        encoding="utf-8",
    )

    findings = SecuritySkill().scan_repository(str(tmp_path))
    titles = [f["vulnerability"] for f in findings]

    assert "Weak Hash: MD5" in titles
    assert "TLS Verification Disabled" in titles


def test_security_skill_detects_hardcoded_credentials(tmp_path: Path):
    (tmp_path / "creds.py").write_text(
        "password = 'hunter2secret'\n"
        "aws_key = 'AKIAIOSFODNN7EXAMPLE'\n"
        "conn = 'postgres://admin:hunter2@db.example.com/prod'\n",
        encoding="utf-8",
    )

    findings = SecuritySkill().scan_repository(str(tmp_path))
    titles = [f["vulnerability"] for f in findings]

    assert "Hardcoded Password" in titles
    assert "AWS Access Key Leak" in titles
    assert "Credential in Connection String" in titles
    assert all(f["severity"] == "CRITICAL" for f in findings)


def test_quality_skill_flags_todo_bare_except_print_and_long_line(tmp_path: Path):
    (tmp_path / "app.py").write_text(
        "# TODO: handle pagination\n"
        "try:\n"
        "    do_work()\n"
        "except:\n"
        "    pass\n"
        "print('debug output')\n"
        f"x = '{'y' * 130}'\n",
        encoding="utf-8",
    )

    findings = QualitySkill().scan_repository(str(tmp_path))

    titles = [f["vulnerability"] for f in findings]
    assert "Outstanding TODO/FIXME" in titles
    assert "Bare except clause" in titles
    assert "Debug print() left in code" in titles
    assert "Line exceeds 120 characters" in titles


def test_quality_skill_ignores_venv_directories(tmp_path: Path):
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "dep.py").write_text("print('noise')\n", encoding="utf-8")

    assert QualitySkill().scan_repository(str(tmp_path)) == []


def test_quality_skill_does_not_flag_print_in_test_files(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("print('harness output')\n", encoding="utf-8")

    titles = [f["vulnerability"] for f in QualitySkill().scan_repository(str(tmp_path))]
    assert "Debug print() left in code" not in titles
