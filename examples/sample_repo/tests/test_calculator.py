import pytest

from src.calculator import Calculator


@pytest.fixture
def calc() -> Calculator:
    return Calculator()


def test_add(calc: Calculator) -> None:
    assert calc.add(2, 3) == 5


def test_subtract(calc: Calculator) -> None:
    assert calc.subtract(5, 3) == 2


def test_multiply(calc: Calculator) -> None:
    assert calc.multiply(4, 3) == 12
