from ai.providers.openrouter_client import ComponentModel


def extraction(prompt, query):
    return ComponentModel(system_prompt=prompt).answer(query)

def get_component_json(component, query):
    prompt = _get_prompts(component)
    if prompt:
        return extraction(prompt=prompt, query=query)
    else:
        return f"Тип компонента '{component}' не определяется."

def _get_prompts(component: str) -> str | None:
    COMPONENT_PROMPTS = {
        'fittings': FITTINGS,
        'adapter-tee': ADAPTER_TEE,
        'adapters': ADAPTERS,
        'plugs': PLUGS
        # TO DO
        #'banjo':BANJO,
        #'banjo-balt: BANJO_BALT,
        #'brs': BRS,
        #'coupling":COUPLING
    }
    return COMPONENT_PROMPTS.get(component)


