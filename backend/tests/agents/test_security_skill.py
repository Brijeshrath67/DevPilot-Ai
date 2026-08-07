"""Unit tests for the custom SecuritySkill scanner."""

from pathlib import Path

from app.skills.security_skill import SecuritySkill


def test_scan_detects_secrets(tmp_path: Path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "app.py").write_text(
        "api_key = \"sk-super-secret-value-1234567890\"\naws_secret_access_key = 'AKIAIOSFODNN7EXAMPLE'\n",
        encoding="utf-8",
    )
    findings = SecuritySkill().scan_repository(str(target))

    secrets = [f for f in findings if f["severity"] == "CRITICAL"]
    assert len(secrets) >= 2
    assert all("Hardcoded Secret" in s["vulnerability"] for s in secrets)
    assert all(isinstance(s["line"], int) and s["line"] > 0 for s in secrets)


def test_scan_detects_unsafe_methods(tmp_path: Path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "app.py").write_text(
        'result = eval(user_input)\nos.system("rm -rf /tmp/x")\n',
        encoding="utf-8",
    )
    findings = SecuritySkill().scan_repository(str(target))

    titles = [f["vulnerability"] for f in findings]
    assert any("eval" in t for t in titles)
    assert any("os.system" in t for t in titles)


def test_scan_detects_sql_injection(tmp_path: Path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "db.py").write_text(
        'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")\n',
        encoding="utf-8",
    )
    findings = SecuritySkill().scan_repository(str(target))
    assert any("SQL Injection" in f["vulnerability"] for f in findings)


def test_scan_skips_node_modules_and_git(tmp_path: Path):
    target = tmp_path / "project"
    node_modules = target / "node_modules"
    node_modules.mkdir(parents=True)
    (node_modules / "leak.js").write_text('api_key = "sk-a-very-long-secret-value-9876543210"\n', encoding="utf-8")
    findings = SecuritySkill().scan_repository(str(target))
    assert findings == []


def test_scan_missing_directory_returns_empty():
    assert SecuritySkill().scan_repository("/definitely/not/a/real/path") == []


def test_scan_clean_file_produces_no_findings(tmp_path: Path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "clean.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    assert SecuritySkill().scan_repository(str(target)) == []
