"""Shared loader for the hyphenated CLI script `evaluate-qanary-system.py`,
which can't be imported with a normal `import` statement.
"""
import importlib.util
import os

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SCRIPT = os.path.join(_HERE, "evaluate-qanary-system.py")


def _load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluator", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def evaluator():
    return _load_evaluator()
