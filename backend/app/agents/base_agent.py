from abc import ABC, abstractmethod


class BaseAgent(ABC):
    @abstractmethod
    def handle(self, payload: dict) -> dict:
        raise NotImplementedError
