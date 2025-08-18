import pytest
from services.llm_service import LLMService

class DummyConfig:
    OPENAI_API_KEY = "sk-test"
    MAX_MESSAGE_LENGTH = 1000
    MAX_RETRIES = 1
    API_TIMEOUT = 5
    @staticmethod
    def validate_config():
        return True
    @staticmethod
    def get_missing_config():
        return []

def test_estimate_cost(monkeypatch):
    monkeypatch.setattr("services.llm_service.Config", DummyConfig)
    llm = LLMService()
    cost = llm.estimate_cost("hello world", model="gpt-3.5-turbo")
    assert isinstance(cost, float)
    assert cost >= 0
