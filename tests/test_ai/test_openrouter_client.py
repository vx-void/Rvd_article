# tests/test_ai/test_openrouter_client.py

import pytest
from unittest.mock import patch
from hydro_find.ai.openrouter_client import OpenRouterClient, ComponentClassifier
from hydro_find.ai.models.ai_models import get_api_key, get_default_model


def test_aiclient_initialization_uses_defaults():
    """Проверка, что AIClient инициализируется значениями из ai_models."""
    client = OpenRouterClient()
    assert client.api_key == get_api_key()
    assert client.model == get_default_model()


def test_aiclient_initialization_accepts_overrides():
    """Проверка переопределения ключа и модели."""
    custom_key = "test-key"
    custom_model = "test-model"
    client = OpenRouterClient(api_key=custom_key, model=custom_model)
    assert client.api_key == custom_key
    assert client.model == custom_model


@patch("hydro_find.ai.openrouter_client.OpenAI")
def test_aiclient_creates_openai_client(mock_openai_class):
    """Проверка, что OpenAI клиент создается с корректными параметрами."""
    client = OpenRouterClient()
    mock_openai_class.assert_called_with(
        base_url="https://openrouter.ai/api/v1",
        api_key=client.api_key,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Hydro-Search APP"
        }
    )


def test_classificator_initialization(mock_ai_client):
    """Проверка инициализации Classificator с AIClient."""
    classifier = ComponentClassifier(mock_ai_client)
    assert classifier.ai_client == mock_ai_client


@patch.object(ComponentClassifier, 'ai_client', create=True)
def test_classificator_classification_success(mock_ai_client, mock_valid_classification_response):
    """Успешная классификация — возвращается нормализованный тип."""
    mock_ai_client.client.chat.completions.create.return_value = mock_valid_classification_response
    classifier = ComponentClassifier(mock_ai_client)
    result = classifier.classification("Фитинг DKOL 12x1.5")
    assert result == "фитинг"


@patch.object(ComponentClassifier, 'ai_client', create=True)
def test_classificator_classification_empty_response(mock_ai_client, mock_empty_classification_response):
    """Пустой ответ от модели — возвращается None."""
    mock_ai_client.client.chat.completions.create.return_value = mock_empty_classification_response
    classifier = ComponentClassifier(mock_ai_client)
    result = classifier.classification("что-то неизвестное")
    assert result is None


@patch.object(ComponentClassifier, 'ai_client', create=True)
def test_classificator_classification_exception_handling(mock_ai_client):
    """Обработка исключения при вызове API."""
    mock_ai_client.client.chat.completions.create.side_effect = Exception("Network error")
    classifier = ComponentClassifier(mock_ai_client)
    result = classifier.classification("Фитинг DKOL 12x1.5")
    assert result is None