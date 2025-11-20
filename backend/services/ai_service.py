from ai_provider.openrouter_client import Classificator
from backend.processing.extractors import get_component_json


def process_component_query(query: str):
    component_type = Classificator().classification(query)
    print(component_type)
    #print(Extraction(FITTINGS, query))
    extracted_data = get_component_json(component_type, query)
    print(extracted_data)


    # Запрос в базу данных
    # Форматирование результата для фронтенда
    return format_ai_results(component_type, extracted_data, query)


def format_ai_results(component_type, extracted_data, original_query):
   pass
