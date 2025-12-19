# tests/test_ai/test_service.py

from hydro_find.ai.service import AIProcessingService
from unittest.mock import patch, Mock


@patch("hydro_find.ai.service.OpenRouterClient")
def test_process_single_success(mock_client_class):
    mock_client = Mock()
    # Имитация: classify → fittings, extract → {"Dy": 12}, quantity → 50
    mock_client.generate.side_effect = ['"fittings"', "50"]
    mock_client.extract_json.return_value = {"Dy": 12}
    mock_client_class.return_value = mock_client

    service = AIProcessingService()
    result = service.process_single("Фитинг 12 DKOL 12x1.5 - 50шт")

    assert result["success"] is True
    assert result["component_type"] == "fittings"
    assert result["extracted_data"] == {"Dy": 12}
    assert result["quantity"] == 50


@patch("hydro_find.ai.service.OpenRouterClient")
def test_process_single_classification_failure(mock_client_class):
    mock_client = Mock()
    mock_client.generate.return_value = None  # не удалось классифицировать
    mock_client_class.return_value = mock_client

    service = AIProcessingService()
    result = service.process_single("непонятный запрос")

    assert result["success"] is False
    assert "Не удалось определить тип компонента" in result["error"]


@patch("hydro_find.ai.service.OpenRouterClient")
def test_process_batch(mock_client_class):
    mock_client = Mock()
    mock_client.generate.side_effect = [
        '"fittings"', "100",  # для первой строки
        '"adapters"', "200"   # для второй строки
    ]
    mock_client.extract_json.return_value = {"Dy": 12}
    mock_client_class.return_value = mock_client

    service = AIProcessingService()
    result = service.process_batch("Фитинг - 100шт\nАдаптер - 200шт")

    assert result["success"] is True
    assert result["batch"] is True
    assert result["total_items"] == 2
    assert len(result["results"]) == 2
    assert all(r["success"] for r in result["results"])