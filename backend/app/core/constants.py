"""Shared application constants."""

from pathlib import Path

# Directories excluded from file indexing and security scans.
IGNORED_DIRECTORIES = {"venv", ".venv", "node_modules", ".git", "__pycache__", "dist", "build", ".ruff_cache"}

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
    ".md": "Markdown",
    ".json": "JSON",
    ".toml": "TOML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".html": "HTML",
    ".css": "CSS",
    ".ipynb": "Jupyter Notebook",
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

EMBEDDINGS_DIR = Path(__file__).resolve().parents[2] / "data" / "embeddings"
