"""Shared application constants."""

from pathlib import Path

APP_NAME = "DevPilot AI"
APP_VERSION = "1.0.0"

DEFAULT_USER_ID = 1

REPOSITORY_STATUS_CREATED = "created"
REPOSITORY_STATUS_INGESTED = "ingested"
REPOSITORY_STATUS_ANALYZED = "analyzed"

HEALTH_METRIC_KEYS = [
    "documentation_score",
    "testing_score",
    "security_score",
    "maintainability_score",
    "complexity_score",
    "overall_score",
]

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
}

SOURCE_CODE_EXTENSIONS = {ext for ext in LANGUAGE_EXTENSIONS if ext not in {".md", ".txt"}}
DOCUMENTATION_EXTENSIONS = {".md", ".txt"}

FRAMEWORK_KEYWORDS = {
    "fastapi": "FastAPI",
    "django": "Django",
    "react": "React",
    "next": "Next.js",
    "vue": "Vue.js",
    "flask": "Flask",
    "express": "Express",
}

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
REPOSITORIES_DIR = DATA_DIR / "repositories"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
CACHE_DIR = DATA_DIR / "cache"
