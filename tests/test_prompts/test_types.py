# tests/test_prompts/test_types.py

from hydro_find.prompts.types import ComponentType, PreprocessingTask


def test_component_type_values():
    assert ComponentType.FITTINGS.value == "fittings"
    assert ComponentType.ADAPTERS.value == "adapters"
    assert str(ComponentType.FITTINGS) == "fittings"


def test_preprocessing_task_values():
    assert PreprocessingTask.CLASSIFY.value == "classify"
    assert PreprocessingTask.SPLIT.value == "split"