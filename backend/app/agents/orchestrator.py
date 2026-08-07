from app.agents.base_agent import BaseAgent
from app.agents.code_review import CodeReviewAgent
from app.agents.documentation import DocumentationAgent
from app.agents.project_health import ProjectHealthAgent
from app.agents.repository_analyzer import RepositoryAnalyzerAgent
from app.agents.repository_chat import RepositoryChatAgent
from app.agents.security_agent import SecurityAgent
from app.agents.testing import TestingAgent
from app.core.config import settings
from app.core.providers import LLMProviderRegistry
from app.services.database_service import DatabaseService
from app.services.documentation_service import DocumentationService
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.llm_service import LLMService
from app.services.parser_service import ParserService
from app.services.testing_service import TestingService
from app.services.vector_service import VectorService
from app.skills.rag_skill import RAGSkill


class AgentOrchestrator:
    """Routes task types to registered specialized agents.

    Each of the six AI agents is bound to a distinct LLM provider (Groq,
    Gemini, Mistral, NVIDIA, OpenRouter, Cerebras) resolved through
    :class:`LLMProviderRegistry`. The seventh (``security``) is rule-based.
    """

    def __init__(
        self,
        llm_service: LLMService | None = None,
        parser_service: ParserService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_service: VectorService | None = None,
        github_service: GitHubService | None = None,
        database_service: DatabaseService | None = None,
        provider_registry: LLMProviderRegistry | None = None,
    ) -> None:
        self.llm_service = llm_service or LLMService(api_key="", api_url="")
        self.provider_registry = provider_registry or LLMProviderRegistry(settings)
        self.parser_service = parser_service or ParserService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_service = vector_service or VectorService()
        self.github_service = github_service or GitHubService()
        self.database_service = database_service or DatabaseService()

        self.services = {
            "llm": self.llm_service,
            "parser": self.parser_service,
            "embedding": self.embedding_service,
            "vector": self.vector_service,
            "github": self.github_service,
            "database": self.database_service,
        }
        self.agents: dict[str, BaseAgent] = self._build_default_agents()

    def _build_default_agents(self) -> dict[str, BaseAgent]:
        llm_for = self.provider_registry.service_for_agent
        documentation_service = DocumentationService(llm_for("documentation"))
        testing_service = TestingService(llm_for("testing"))
        rag_skill = RAGSkill(self.vector_service, self.embedding_service, llm_for("repository_chat"))
        return {
            "repository_analyzer": RepositoryAnalyzerAgent(
                self.parser_service, self.database_service, llm=llm_for("repository_analyzer")
            ),
            "code_review": CodeReviewAgent(self.database_service, llm=llm_for("code_review")),
            "documentation": DocumentationAgent(documentation_service, self.database_service),
            "testing": TestingAgent(testing_service, self.database_service),
            "project_health": ProjectHealthAgent(self.database_service, llm=llm_for("project_health")),
            "repository_chat": RepositoryChatAgent(rag_skill),
            "security": SecurityAgent(self.database_service),
        }

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        self.agents[name] = agent

    def route(self, task_type: str, payload: dict) -> dict:
        agent = self.agents.get(task_type)
        if not agent:
            raise ValueError(f"No registered agent for task: {task_type}")
        return agent.handle(payload)
