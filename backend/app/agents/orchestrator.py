from app.agents.base_agent import BaseAgent
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService
from app.services.vector_service import VectorService


class AgentOrchestrator:
    def __init__(
        self,
        llm_service: LLMService,
        parser_service: ParserService,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
        github_service: GitHubService,
        database_service: DatabaseService,
    ):
        self.services = {
            "llm": llm_service,
            "parser": parser_service,
            "embedding": embedding_service,
            "vector": vector_service,
            "github": github_service,
            "database": database_service,
        }
        self.agents: dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        self.agents[name] = agent

    def route(self, task_type: str, payload: dict) -> dict:
        agent = self.agents.get(task_type)
        if not agent:
            raise ValueError(f"No registered agent for task: {task_type}")
        return agent.handle(payload)
