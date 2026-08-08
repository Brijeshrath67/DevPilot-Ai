"""Rule-based repository security scanner.

Maintains an updated dictionary of secret/credential leak signatures, insecure
function names, and injection/traversal patterns. Scans the repository's real
files (including ``.ipynb`` code cells) and returns findings with severity
grades, plus scan metadata (files scanned / patterns checked) so results are
verifiably grounded in the repository.
"""

import json
import re
from pathlib import Path
from typing import Any

# File extensions scanned for secrets and unsafe patterns. Notebooks (.ipynb)
# are JSON containers whose code cells are scanned line by line.
SCANNED_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".java",
    ".go",
    ".php",
    ".rb",
    ".cs",
    ".kt",
    ".swift",
    ".sh",
    ".bash",
    ".sql",
    ".ipynb",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".env",
    ".example",
}

# Directories that are never scanned (virtual envs, build output, SCM internals).
IGNORED_DIRS = {"venv", ".venv", "node_modules", ".git", "__pycache__", "dist", "build"}


def _iter_targets(root: Path, files: list[Path] | None = None):
    if files:
        yield from files
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix in SCANNED_EXTENSIONS:
            yield path


def _read_lines(path: Path) -> list[str]:
    if path.suffix == ".ipynb":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cells = data.get("cells", []) if isinstance(data, dict) else []
            text = ""
            for cell in cells:
                source = cell.get("source", []) if isinstance(cell, dict) else []
                if isinstance(source, list):
                    text += "".join(source)
                elif isinstance(source, str):
                    text += source
            return text.splitlines()
        except Exception:  # malformed notebooks are skipped
            return []
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:  # unreadable files are skipped
        return []


class SecuritySkill:
    def __init__(self) -> None:
        # (regex, title, severity, description, recommendation)
        self.secret_patterns = [
            (
                re.compile(
                    r"(?i)\b(?:api[_-]?key|client[_-]?secret|secret[_-]?key|access[_-]?key|"
                    r"auth[_-]?token|jwt[_-]?secret|private[_-]?key|aws[_-]?secret[_-]?access[_-]?key)"
                    r"\s*[=:]\s*['\"][^'\"]{12,}['\"]"
                ),
                "Hardcoded Secret Token",
                "CRITICAL",
                "A secret-looking value is assigned to a credential variable.",
                "Move secrets and credentials to secure environment variables (.env) or a secret manager.",
            ),
            (
                re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
                "AWS Access Key Leak",
                "CRITICAL",
                "An AWS access key identifier is committed to the repository.",
                "Rotate the key immediately and remove it from history; load credentials from env/IRSA instead.",
            ),
            (
                re.compile(r"(?i)\b(?:password|passwd|pwd|db_password)\s*[=:]\s*['\"][^'\"]{6,}['\"]"),
                "Hardcoded Password",
                "CRITICAL",
                "A password is assigned a literal string value.",
                "Read credentials from environment variables or a secret manager at runtime.",
            ),
            (
                re.compile(r"(?i)\b(?:mysql|postgres|postgresql|mongodb(?:\+srv)?|redis|amqp)://[^/\s:@]+:[^@\s/]+@"),
                "Credential in Connection String",
                "CRITICAL",
                "A URI connection string embeds username and password credentials.",
                "Move credentials to environment variables; never embed them in source code.",
            ),
            (
                re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.\=\+]{24,}"),
                "Bearer Token Exposure",
                "CRITICAL",
                "An inline bearer token is hardcoded in the repository.",
                "Inject the token via an environment variable or secret store instead of hardcoding it.",
            ),
        ]

        self.unsafe_patterns = [
            (
                re.compile(r"\beval\s*\("),
                "Unsafe Function: eval()",
                "MEDIUM",
                "Executing arbitrary text strings as code.",
                "Use safer parsing methods instead of executing arbitrary text strings.",
            ),
            (
                re.compile(r"\bexec\s*\("),
                "Unsafe Function: exec()",
                "MEDIUM",
                "Dynamic code execution.",
                "Avoid dynamic execution of code strings.",
            ),
            (
                re.compile(r"\bos\.system\s*\("),
                "Command Injection Risk: os.system()",
                "MEDIUM",
                "Invokes the shell with a command string.",
                "Use the subprocess module with shell=False.",
            ),
            (
                re.compile(r"\bos\.popen\s*\("),
                "Command Injection Risk: os.popen()",
                "MEDIUM",
                "Invokes the shell with a command string.",
                "Use the subprocess module with shell=False.",
            ),
            (
                re.compile(r"\bsubprocess\.(?:run|Popen|call|check_call|check_output)\s*\([^)]*shell\s*=\s*True"),
                "Shell Injection Risk: subprocess shell=True",
                "HIGH",
                "subprocess is invoked with the shell, allowing shell metacharacter injection.",
                "Pass an argument list to subprocess with shell=False.",
            ),
            (
                re.compile(r"execute\s*\(\s*['\"].*%\s*[\w_]+"),
                "Potential SQL Injection",
                "HIGH",
                "SQL query built with string modulation.",
                "Use parameterized SQL queries instead of string modulation.",
            ),
            (
                re.compile(r"execute\s*\(\s*['\"].*\+\s*[\w_]+"),
                "Potential SQL Injection",
                "HIGH",
                "SQL query built with string concatenation.",
                "Use parameterized queries instead of string concatenation.",
            ),
            (
                re.compile(r"execute\s*\(\s*f['\"].*\{[\w_\.]+\}"),
                "Potential SQL Injection",
                "HIGH",
                "SQL query built with f-string interpolation.",
                "Use parameterized queries instead of f-string interpolation.",
            ),
            (
                re.compile(r"\btext\s*\(\s*f['\"].*\{[\w_\.]+\}"),
                "Potential SQL Injection",
                "HIGH",
                "Raw SQL built with f-string interpolation.",
                "Use parameterized queries instead of f-string interpolation.",
            ),
            (
                re.compile(r"\b(?:pickle|cPickle|joblib)\.(?:load|loads)\s*\("),
                "Insecure Deserialization: pickle",
                "HIGH",
                "Unpickling untrusted data can execute arbitrary code.",
                "Never unpickle untrusted data; use safe formats like JSON or validate the source.",
            ),
            (
                re.compile(r"\byaml\.load\s*\("),
                "Unsafe YAML Deserialization",
                "MEDIUM",
                "yaml.load() can construct arbitrary Python objects.",
                "Use yaml.safe_load() unless you trust the input source.",
            ),
            (
                re.compile(r"\bmd5\s*\("),
                "Weak Hash: MD5",
                "MEDIUM",
                "MD5 is cryptographically broken and unsafe for security contexts.",
                "Use a strong algorithm such as SHA-256 for integrity and password hashing.",
            ),
            (
                re.compile(r"\bsha1\s*\("),
                "Weak Hash: SHA-1",
                "MEDIUM",
                "SHA-1 is deprecated for security-sensitive hashing.",
                "Use a strong algorithm such as SHA-256 for security-sensitive hashing.",
            ),
            (
                re.compile(r"verify\s*=\s*False"),
                "TLS Verification Disabled",
                "HIGH",
                "Certificate verification is disabled for an outbound connection.",
                "Keep verify=True unless working against a pinned, trusted test endpoint.",
            ),
            (
                re.compile(r"\bssl\._create_unverified_context\s*\("),
                "TLS Verification Disabled",
                "HIGH",
                "An unverified SSL context disables certificate checks.",
                "Use a verified SSL context; do not disable certificate validation.",
            ),
        ]

        self.path_traversal_patterns = [
            (
                re.compile(
                    r"(?:open|os\.open|Path)\s*\(\s*[^)]*\b"
                    r"(?:request\.(?:args|form|values|json|files)|user_input|filename|file_path|path_param)\b[^)]*\)"
                ),
                "Path Traversal Risk",
                "HIGH",
                "A user-controlled value is used to open a file path.",
                "Validate and canonicalize user-supplied paths; reject traversal sequences like ../.",
            ),
            (
                re.compile(r"os\.path\.join\s*\([^)]*\b(?:request|user_input|filename|file_path)\b"),
                "Path Traversal Risk",
                "HIGH",
                "A user-controlled value is joined into a filesystem path.",
                "Validate and canonicalize user-supplied paths before joining them to a base directory.",
            ),
            (
                re.compile(r"\.\./\.\./"),
                "Path Traversal Pattern",
                "MEDIUM",
                "Parent-directory navigation sequence detected.",
                "Ensure the path cannot be reached from user input without validation.",
            ),
        ]

    def scan_repository(
        self, repository_path: str, files: list[str] | None = None, root: Path | None = None
    ) -> list[dict[str, Any]]:
        """Scan a repository (or a subset of files) for security findings.

        ``files`` optionally restricts the scan to specific relative paths; when
        omitted every supported file under the root is scanned.
        """
        return self.scan_repository_with_meta(repository_path, files=files, root=root)["findings"]

    def scan_repository_with_meta(
        self, repository_path: str, files: list[str] | None = None, root: Path | None = None
    ) -> dict[str, Any]:
        """Like :meth:`scan_repository` but also returns scan metadata."""
        repo_root = root or Path(repository_path)
        if not repo_root.exists() or not repo_root.is_dir():
            return {"findings": [], "files_scanned": 0, "patterns_checked": self.patterns_checked}

        targets = None
        if files:
            targets = []
            for f in files:
                candidate = (repo_root / f).resolve()
                if candidate.is_relative_to(repo_root) and candidate.is_file():
                    targets.append(candidate)

        findings: list[dict[str, Any]] = []
        files_scanned = 0
        for path in _iter_targets(repo_root, targets):
            if any(part in path.parts for part in IGNORED_DIRS):
                continue
            files_scanned += 1
            rel_path = str(path.relative_to(repo_root)).replace("\\", "/")

            for line_num, line in enumerate(_read_lines(path), start=1):
                for regex, title, severity, description, rec in (
                    *self.secret_patterns,
                    *self.unsafe_patterns,
                    *self.path_traversal_patterns,
                ):
                    if regex.search(line):
                        findings.append(
                            {
                                "file": rel_path,
                                "line": line_num,
                                "severity": severity,
                                "vulnerability": title,
                                "description": f"{description} Detected: `{line.strip()[:60]}`",
                                "recommendation": rec,
                            }
                        )

        return {
            "findings": findings,
            "files_scanned": files_scanned,
            "patterns_checked": self.patterns_checked,
        }

    @property
    def patterns_checked(self) -> int:
        return len(self.secret_patterns) + len(self.unsafe_patterns) + len(self.path_traversal_patterns)
