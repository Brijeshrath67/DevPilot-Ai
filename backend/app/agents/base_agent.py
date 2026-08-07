from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract contract for all specialized agents."""

    @abstractmethod
    def handle(self, payload: dict) -> dict:
        raise NotImplementedError
