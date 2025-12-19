# tests/test_prompts/test_repository.py

from hydro_find.prompts import PromptRepository, ComponentType, PreprocessingTask


def test_get_component_prompt_valid():
    prompt = PromptRepository.get_component_prompt(ComponentType.FITTINGS)
    assert isinstance(prompt, str)
    assert "JSON" in prompt
    assert "fittings" not in prompt.lower()  # не должно быть упоминания типа


def test_get_component_prompt_invalid():
    from hydro_find.prompts.types import ComponentType
    fake_type = ComponentType("invalid")
    with pytest.raises(ValueError, match="Неизвестный тип компонента"):
        PromptRepository.get_component_prompt(fake_type)


def test_get_preprocessing_prompt_valid():
    prompt = PromptRepository.get_preprocessing_prompt(PreprocessingTask.CLASSIFY)
    assert isinstance(prompt, str)
    assert "Верни одно из:" in prompt
    assert "JSON" not in prompt  # preprocessing не использует JSON


def test_get_preprocessing_prompt_invalid():
    fake_task = PreprocessingTask("invalid")
    with pytest.raises(ValueError, match="Неизвестная задача предобработки"):
        PromptRepository.get_preprocessing_prompt(fake_task)