import os

from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.skills.reporting_skill import ReportingSkill


class ProjectHealthAgent(BaseAgent):
    def __init__(self, database_service: DatabaseService) -> None:
        self.reporting_skill = ReportingSkill()
        self.database_service = database_service

    def handle(self, payload: dict) -> dict:
        repository_id = payload.get("repository_id")
        if not repository_id:
            return {"error": "Missing repository_id"}

        repo = self.database_service.get_repository(int(repository_id))
        if not repo:
            return {"error": "Repository not found"}

        # Dynamic calculations based on files
        files = self.database_service.get_repository_files(repo.id)
        file_count = len(files)

        # 1. Documentation score
        has_readme = False
        has_contrib = False
        has_arch = False
        if repo.root_path and os.path.exists(repo.root_path):
            for entry in os.listdir(repo.root_path):
                lower_entry = entry.lower()
                if "readme" in lower_entry:
                    has_readme = True
                elif "contributing" in lower_entry:
                    has_contrib = True
                elif "architecture" in lower_entry or "docs" in lower_entry:
                    has_arch = True

        doc_score = 40.0
        if has_readme:
            doc_score += 30.0
        if has_contrib:
            doc_score += 15.0
        if has_arch:
            doc_score += 15.0

        # 2. Testing score
        test_file_count = 0
        for f in files:
            path_lower = f.file_path.lower()
            if "test" in path_lower or "spec" in path_lower:
                test_file_count += 1

        test_score = 30.0
        if test_file_count > 0:
            test_score = min(100.0, 40.0 + test_file_count * 15.0)

        # 3. Security score
        # Retrieve existing security score from health metric if saved by SecurityAgent, else default to 85.0
        existing_health = self.database_service.get_health_metrics(repo.id)
        security_score = existing_health.security_score if existing_health else 85.0

        # 4. Maintainability score
        # Base it on number of files and presence of good layout
        maintainability_score = 80.0
        if file_count > 100:
            maintainability_score = 60.0
        elif file_count > 50:
            maintainability_score = 70.0
        elif file_count < 3:
            maintainability_score = 65.0

        # 5. Complexity score
        # Base it on file count and test/code ratio
        complexity_score = 75.0
        if file_count > 80:
            complexity_score = 55.0
        elif file_count < 10:
            complexity_score = 85.0

        metrics = {
            "documentation": doc_score,
            "testing": test_score,
            "security": security_score,
            "maintainability": maintainability_score,
            "complexity": complexity_score,
        }

        scores = self.reporting_skill.compute_health_scores(metrics)
        self.database_service.save_health_metrics(repo.id, scores)

        recommendations = []
        if not has_readme:
            recommendations.append("HIGH: Add a README.md file to document project purpose and setup.")
        if test_score < 50.0:
            recommendations.append("HIGH: Write unit tests; test file count is low.")
        if security_score < 80.0:
            recommendations.append("CRITICAL: Resolve outstanding security vulnerabilities immediately.")
        if doc_score < 70.0:
            recommendations.append("MEDIUM: Create contributing guidelines and architecture overview diagrams.")
        if maintainability_score < 70.0:
            recommendations.append("MEDIUM: Consider refactoring code structure into modular folder hierarchies.")

        if not recommendations:
            recommendations.append("All metrics are green! The repository shows excellent code hygiene.")

        return {
            **scores,
            "recommendations": recommendations,
        }
