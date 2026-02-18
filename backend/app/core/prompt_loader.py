from pathlib import Path
from typing import Optional

_prompt_cache: dict[str, str] = {}


def load_prompt(name: str, **kwargs) -> str:
    if name not in _prompt_cache:
        path = Path(__file__).parent.parent / "prompts" / f"{name}.txt"

        if not path.exists():
            raise FileNotFoundError(f"Промпт не найден: {path}")

        _prompt_cache[name] = path.read_text(encoding="utf-8")

    prompt_template = _prompt_cache[name]

    if kwargs:
        return prompt_template.format(**kwargs)

    return prompt_template


def reload_prompt(name: str) -> str:
    if name in _prompt_cache:
        del _prompt_cache[name]
    return load_prompt(name)


def list_available_prompts() -> list[str]:

    prompts_dir = Path(__file__).parent.parent / "prompts"
    if not prompts_dir.exists():
        return []
    return [p.stem for p in prompts_dir.glob("*.txt")]