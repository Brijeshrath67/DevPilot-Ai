import re
from pathlib import Path
from typing import Any


class SecuritySkill:
    def __init__(self) -> None:
        self.secret_patterns = [
            (
                re.compile(
                    r"(?i)(api_key|client_secret|aws_secret\w*|private_key|jwt_secret)\s*=\s*['\"][a-zA-Z0-9_\-\.\=\+]{16,}['\"]"
                ),
                "Hardcoded Secret Token",
            ),
            (re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.\=\+]{24,}"), "Bearer Token Exposure"),
        ]
        self.unsafe_patterns = [
            (
                re.compile(r"\beval\s*\("),
                "Unsafe Function: eval()",
                "Use safer parsing methods instead of executing arbitrary text strings.",
            ),
            (re.compile(r"\bexec\s*\("), "Unsafe Function: exec()", "Avoid dynamic execution of code strings."),
            (
                re.compile(r"\bos\.system\s*\("),
                "Command Injection Risk: os.system()",
                "Use the subprocess module with shell=False.",
            ),
            (
                re.compile(r"execute\s*\(\s*['\"].*%\s*[\w_]+"),
                "Potential SQL Injection",
                "Use parameterized SQL queries instead of string modulation.",
            ),
            (
                re.compile(r"execute\s*\(\s*['\"].*\+\s*[\w_]+"),
                "Potential SQL Injection",
                "Use parameterized queries instead of string concatenation.",
            ),
            (
                re.compile(r"execute\s*\(\s*f['\"].*\{[\w_\.]+\}"),
                "Potential SQL Injection",
                "Use parameterized queries instead of f-string interpolation.",
            ),
        ]

    def scan_repository(self, repository_path: str) -> list[dict[str, Any]]:
        findings = []
        root = Path(repository_path)
        if not root.exists() or not root.is_dir():
            return findings

        # Scan files
        for path in root.rglob("*"):
            # Skip virtual environments, node_modules, and git directories
            if any(
                part in path.parts for part in ["venv", ".venv", "node_modules", ".git", "__pycache__", "dist", "build"]
            ):
                continue

            if path.is_file() and path.suffix in {".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".env", ".example"}:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.splitlines()

                    for line_num, line in enumerate(lines, start=1):
                        # 1. Scan secrets
                        for regex, title in self.secret_patterns:
                            if regex.search(line):
                                findings.append(
                                    {
                                        "file": str(path.relative_to(root)).replace("\\", "/"),
                                        "line": line_num,
                                        "severity": "CRITICAL",
                                        "vulnerability": title,
                                        "description": (
                                            f"Potential leak of confidential key or token: `{line.strip()[:40]}...`"
                                        ),
                                        "recommendation": (
                                            "Move secrets and credentials to secure environment variables "
                                            "(.env files) or secret managers."
                                        ),
                                    }
                                )

                        # 2. Scan unsafe function usages
                        for regex, title, rec in self.unsafe_patterns:
                            if regex.search(line):
                                findings.append(
                                    {
                                        "file": str(path.relative_to(root)).replace("\\", "/"),
                                        "line": line_num,
                                        "severity": "HIGH" if "SQL Injection" in title else "MEDIUM",
                                        "vulnerability": title,
                                        "description": f"Detected risky usage pattern: `{line.strip()}`",
                                        "recommendation": rec,
                                    }
                                )
                except Exception:  # noqa: S110  # unreadable binary files are skipped
                    pass

        return findings
