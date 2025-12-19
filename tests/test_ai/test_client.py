# tests/test_ai/test_client.py

from hydro_find.ai.client import OpenRouterClient
from unittest.mock import patch


@patch("hydro_find.ai.client.OpenAI")
def test_generate_success(mock_openai_class, mock_openai_client):
    mock_openai_class.return_value = mock_openai_client
    client = OpenRouterClient()
    result = client.generate("system prompt", "user query")
    assert result == '"fittings"'


@patch("hydro_find.ai.client.OpenAI")
def test_generate_empty_response(mock_openai_class, mock_empty_response):
    mock_openai_class.return_value = mock_empty_response
    client = OpenRouterClient()
    result = client.generate("system prompt", "user query")
    assert result is None


@patch("hydro_find.ai.client.OpenAI")
def test_extract_json_valid(mock_openai_class):
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='{"Dy": 12}'))]
    )
    mock_openai_class.return_value = mock_client

    client = OpenRouterClient()
    result = client.extract_json("prompt", "query")
    assert result == {"Dy": 12}


@patch("hydro_find.ai.client.OpenAI")
def test_extract_json_invalid_json(mock_openai_class):
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='invalid json'))]
    )
    mock_openai_class.return_value = mock_client

    client = OpenRouterClient()
    result = client.extract_json("prompt", "query")
    assert result == {"raw_response": "invalid json"}