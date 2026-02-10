# worker_main.py
if __name__ == "__main__":
    # Инициализация зависимостей
    task_service = TaskService()
    ai_service = AIProcessingService(...)  # Твой AI сервис
    repository = ComponentRepository(...)  # Реализация для БД
    
    start_worker(
        host="localhost",
        queue_name="search_tasks",
        task_service=task_service,
        ai_service=ai_service,
        repository=repository
    )