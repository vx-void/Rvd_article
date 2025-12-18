# tests/test_ai/test_classifiers.py

from unittest.mock import patch
from hydro_find.ai.classifiers import hydrofind
from hydro_find.ai.models.types import ComponentType


@patch("hydro_find.ai.classifiers.ComponentClassifier")
def test_hydrofind_success(mock_classifier_class):
    """Успешная классификация — возвращается ComponentType."""
    mock_instance = mock_classifier_class.return_value
    mock_instance.classify.return_value = ComponentType.FITTINGS
    result = hydrofind("Фитинг DKOL 12x1.5")
    assert result == ComponentType.FITTINGS
    mock_instance.classify.assert_called_once_with("Фитинг DKOL 12x1.5")


@patch("hydro_find.ai.classifiers.ComponentClassifier")
def test_hydrofind_exception_returns_none(mock_classifier_class):
    """Исключение в классификаторе — возвращается None."""
    mock_instance = mock_classifier_class.return_value
    mock_instance.classify.side_effect = Exception("API error")
    result = hydrofind("некорректный запрос")
    assert result is None


@patch("hydro_find.ai.classifiers.ComponentClassifier")
def test_hydrofind_empty_query(mock_classifier_class):
    """Пустой запрос — классификатор всё равно вызывается (поведение модели)."""
    mock_instance = mock_classifier_class.return_value
    mock_instance.classify.return_value = None
    result = hydrofind("")
    assert result is None