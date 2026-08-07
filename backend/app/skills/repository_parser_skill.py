from typing import Any


class RepositoryParserSkill:
    def parse_structure(self, repository_path: str) -> dict[str, Any]:
        return {"files": [], "languages": [], "frameworks": [], "dependencies": []}

    def summarize_architecture(self, parsed_data: dict[str, Any]) -> str:
        return "Architecture summary"
