# workers/worker_main.py
import os
import sys
import logging
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.application.task_service import TaskService
from core.messaging.consumer import RabbitMQConsumer
from core.messaging.message import Message

# Импорты для AI и БД (заглушки пока)
from ai.service import AIProcessingService
from ai.interfaces.ai_client import IAIClient
from ai.interfaces.prompt_repository import IPromptRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StubComponentRepository:
    """Заглушка репозитория для тестирования"""
    def find(self, component_filter):
        logger.info(f"Searching with filter: {component_filter}")
        # Возвращаем заглушечные данные
        return [
            {"article": "TEST001", "name": "Тестовый фитинг", "price": 100.0},
            {"article": "TEST002", "name": "Тестовый адаптер", "price": 150.0},
        ]

class SearchWorker:
    def __init__(self, task_service, ai_service, repository):
        self._task_service = task_service
        self._ai_service = ai_service
        self._repository = repository
    
    def handle_message(self, message: Message):
        task_id = message.task_id
        query = message.payload.get("query", "")
        
        logger.info(f"Processing task {task_id}: {query}")
        
        try:
            # 1. Обновляем статус
            self._task_service.update_status(task_id, "IN_PROGRESS")
            
            # 2. Обрабатываем через AI
            ai_result = self._ai_service.process(query)
            logger.info(f"AI result: {ai_result}")
            
            # 3. Ищем в БД (заглушка)
            components = self._repository.find(ai_result)
            
            # 4. Сохраняем результат
            from core.application.dto import QueryResultDTO, MatchDTO
            
            matches = [
                MatchDTO(
                    article=comp["article"],
                    name=comp["name"],
                    price=comp.get("price")
                )
                for comp in components
            ]
            
            result = QueryResultDTO(
                original_query=query,
                component_type=ai_result.get("component_type"),
                parameters=ai_result.get("data", {}),
                quantity=1,
                matches=matches
            )
            
            self._task_service.save_result(task_id, [result])
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            self._task_service.update_status(task_id, "FAILED", str(e))

def main():
    """Точка входа для worker процесса"""
    
    # Конфигурация
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "search_tasks")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    
    logger.info(f"Starting worker. Connecting to {RABBITMQ_HOST}, queue: {RABBITMQ_QUEUE}")
    
    # Инициализация зависимостей
    task_service = TaskService()
    
    # TODO: Заменить на реальные реализации
    from ai.models.OpenRouterClient import OpenRouterClient
    from ai.prompts.repository import PromptRepository
    
    ai_client = OpenRouterClient()
    prompt_repo = PromptRepository()
    ai_service = AIProcessingService(ai_client, prompt_repo)
    
    repository = StubComponentRepository()
    
    # Создаем worker
    worker = SearchWorker(task_service, ai_service, repository)
    
    # Запускаем consumer
    consumer = RabbitMQConsumer(
        host=RABBITMQ_HOST,
        queue_name=RABBITMQ_QUEUE,
        callback=worker.handle_message,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASS
    )
    
    try:
        consumer.start()
    except KeyboardInterrupt:
        logger.info("Worker shutting down...")
        consumer.stop()
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()