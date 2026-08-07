"""Calculator service with intentionally insecure patterns for demo scans."""

import os


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b


def load_config(expression: str) -> str:
    """Demo of an unsafe eval usage flagged by the SecuritySkill scanner."""
    return eval(expression)


def run_command(command: str) -> int:
    """Demo of os.system usage flagged by the SecuritySkill scanner."""
    return os.system(command)
