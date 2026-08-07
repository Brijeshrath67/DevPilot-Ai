import json
import os
import re
import tomllib
from pathlib import Path
from typing import Any, Dict, List

from app.db.session import SessionLocal
from app.models.repository import Repository

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".php": "PHP",
}

FRAMEWORK_KEYWORDS = {
    "fastapi": "FastAPI",
    "django": "Django",
    "react": "React",
    "next": "Next.js",
    "vue": "Vue.js",
    "flask": "Flask",
    "express": "Express",
}

class ParserService:
    def analyze_repository(self, repository_id: str, scope: str = "full") -> dict:
        with SessionLocal() as session:
            repository = session.get(Repository, int(repository_id))
            if not repository:
                raise ValueError("Repository not found")

            root_path = repository.root_path
            if not root_path or not os.path.isdir(root_path):
                return {
                    "repository_id": repository_id,
                    "scope": scope,
                    "project_summary": "Repository metadata available, root path not configured.",
                    "architecture_summary": "No local repository path found for architecture analysis.",
                    "languages": [],
                    "frameworks": [],
                    "dependencies": [],
                }

            parsed = self._parse_repository(Path(root_path))
            summary = self._summarize_project(repository.name, parsed)
            architecture = self._summarize_architecture(parsed)
            return {
                "repository_id": repository_id,
                "scope": scope,
                "project_summary": summary,
                "architecture_summary": architecture,
                "languages": parsed["languages"],
                "frameworks": parsed["frameworks"],
                "dependencies": parsed["dependencies"],
            }

    def _parse_repository(self, root_path: Path) -> Dict[str, Any]:
        languages = set()
        frameworks = set()
        dependencies = set()
        file_count = 0

        for path in root_path.rglob("*"):
            if path.is_file():
                file_count += 1
                language = LANGUAGE_EXTENSIONS.get(path.suffix)
                if language:
                    languages.add(language)
                if path.name == "package.json":
                    self._collect_package_json(path, frameworks, dependencies)
                elif path.name in {"requirements.txt", "Pipfile", "pyproject.toml"}:
                    self._collect_python_dependencies(path, frameworks, dependencies)

        return {
            "file_count": file_count,
            "languages": sorted(languages),
            "frameworks": sorted(frameworks),
            "dependencies": sorted(dependencies),
        }

    def _collect_package_json(self, path: Path, frameworks: set, dependencies: set) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in ["dependencies", "devDependencies"]:
                packages = data.get(key, {}) or {}
                for package in packages:
                    dependencies.add(package)
                    for token, framework in FRAMEWORK_KEYWORDS.items():
                        if token in package.lower():
                            frameworks.add(framework)
        except Exception:
            pass

    def _collect_python_dependencies(self, path: Path, frameworks: set, dependencies: set) -> None:
        try:
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".toml":
                data = tomllib.loads(text)
                for section in ["project", "tool.poetry", "tool"]:
                    if section in data:
                        deps = data.get(section, {}).get("dependencies", {})
                        if isinstance(deps, dict):
                            for package in deps:
                                dependencies.add(package)
                                self._map_python_framework(package, frameworks)
            else:
                for line in text.splitlines():
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        match = re.split(r"[=<>!~]+", cleaned)[0].strip()
                        if match:
                            dependencies.add(match)
                            self._map_python_framework(match, frameworks)
        except Exception:
            pass

    def _map_python_framework(self, package_name: str, frameworks: set) -> None:
        lower = package_name.lower()
        if "fastapi" in lower:
            frameworks.add("FastAPI")
        elif "django" in lower:
            frameworks.add("Django")
        elif "flask" in lower:
            frameworks.add("Flask")

    def _summarize_project(self, name: str, parsed: Dict[str, Any]) -> str:
        return (
            f"{name} contains {parsed['file_count']} source files across {len(parsed['languages'])} languages. "
            f"Detected frameworks: {', '.join(parsed['frameworks']) or 'none'} and {len(parsed['dependencies'])} dependencies."
        )

    def _summarize_architecture(self, parsed: Dict[str, Any]) -> str:
        if parsed["frameworks"]:
            return f"Architecture relies on {', '.join(parsed['frameworks'])}." + "".join(
                [f" {lang} files are present." for lang in parsed["languages"]]
            )
        return "No major framework detected; architecture appears to be lightweight and file-based."
