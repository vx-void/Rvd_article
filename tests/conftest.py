# tests/conftest.py

import pytest
from unittest.mock import Mock, patch
from openai import OpenAI


@pytest.fixture
def mock_openai_client():
    """Мок OpenAI-клиента с контролируемым ответом."""
    mock = Mock(spec=OpenAI)
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='"fittings"'))]
    )
    return mock


@pytest.fixture
def mock_empty_response():
    mock = Mock(spec=OpenAI)
    mock.chat.completions.create.return_value = Mock(choices=[])
    return mock