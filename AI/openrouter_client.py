from flask.cli import load_dotenv
from openai import OpenAI
from config import Config
import sys
import os

# Добавляем путь для импорта
current_dir = os.path.dirname(__file__)
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

class AIClient:
    def __init__(self):
        self.api_key = os.getenv('API_OPEN_ROUTER')
        self.model = os.getenv('DEFAULT_MODEL')
        self.client = OpenAI(
            base_url=os.getenv('OPEN_ROUTER'),
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Hydro-Search APP"
            }
        )
        print(f"AI Client создан с моделью: {self.model}")


class ComponentModel:
    def __init__(self, system_prompt: str):
        self.ai_client = AIClient()
        self.system_prompt = system_prompt

    def answer(self, question: str) -> str | None:
        try:
            response = self.ai_client.client.chat.completions.create(
                model=self.ai_client.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.2,
                timeout=120
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            return None
        except Exception as e:
            print(f"ComponentModel error: {e}")
            return None


class Classificator:
    def __init__(self):
        self.ai_client = AIClient()
        from hydro_find.prompts.component_prompts import CLASSIFICATION
        self.prompt = CLASSIFICATION

    def classification(self, question):
        try:
            response = self.ai_client.client.chat.completions.create(
                model=self.ai_client.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.2,
                timeout=120
            )
            if response.choices and response.choices[0].message.content:
                return str(response.choices[0].message.content.strip())
            return None
        except Exception as e:
            print(f"Classificator error: {e}")
            return None