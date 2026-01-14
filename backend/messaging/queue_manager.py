# messaging/queue_manager.py
import pika
import json
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class QueueManager:
    """Управление очередями RabbitMQ"""

    def __init__(self, host='localhost', port=5672):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None

    def connect(self):
        """Подключение к RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.host, self.port)
        )
        self.channel = self.connection.channel()
        logger.info(f"Подключено к RabbitMQ {self.host}:{self.port}")

    def get_queue_stats(self, queue_name: str = 'search_queue') -> Dict[str, Any]:
        """Получение статистики очереди"""
        try:
            result = self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                passive=True  # Только получение статистики
            )

            return {
                'queue_name': queue_name,
                'message_count': result.method.message_count,
                'consumer_count': result.method.consumer_count,
                'ready_messages': getattr(result.method, 'messages_ready', 0),
                'unacked_messages': getattr(result.method, 'messages_unacknowledged', 0)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики очереди: {e}")
            return {}

    def peek_messages(self, queue_name: str = 'search_queue', count: int = 10) -> List[Dict[str, Any]]:
        """Просмотр сообщений в очереди без их удаления"""
        messages = []

        try:
            # Получаем сообщения с флагом no_ack=False (чтобы не удалять)
            for i in range(min(count, self.get_queue_stats(queue_name)['message_count'])):
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=queue_name,
                    auto_ack=False  # Не подтверждаем, чтобы не удалять
                )

                if method_frame:
                    try:
                        message = json.loads(body)
                        messages.append({
                            'delivery_tag': method_frame.delivery_tag,
                            'message': message,
                            'body_preview': body[:200] if body else ''
                        })
                    except json.JSONDecodeError:
                        messages.append({
                            'delivery_tag': method_frame.delivery_tag,
                            'error': 'Invalid JSON',
                            'body_preview': body[:200] if body else ''
                        })

                    # Возвращаем сообщение обратно в очередь
                    self.channel.basic_nack(method_frame.delivery_tag, requeue=True)
                else:
                    break

        except Exception as e:
            logger.error(f"Ошибка просмотра сообщений: {e}")

        return messages

    def purge_queue(self, queue_name: str = 'search_queue'):
        """Полная очистка очереди"""
        try:
            result = self.channel.queue_purge(queue=queue_name)
            logger.info(f"Очередь {queue_name} очищена. Удалено сообщений: {result.method.message_count}")
            return result.method.message_count
        except Exception as e:
            logger.error(f"Ошибка очистки очереди: {e}")
            return 0

    def remove_specific_messages(self, queue_name: str = 'search_queue',
                                 filter_func=None) -> int:
        """
        Удаление конкретных сообщений из очереди

        Args:
            queue_name: Имя очереди
            filter_func: Функция для фильтрации сообщений (возвращает True для удаления)

        Returns:
            int: Количество удаленных сообщений
        """
        removed_count = 0

        try:
            queue_stats = self.get_queue_stats(queue_name)
            total_messages = queue_stats['message_count']

            logger.info(f"Начало фильтрации очереди {queue_name} ({total_messages} сообщений)")

            for i in range(total_messages):
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=queue_name,
                    auto_ack=False
                )

                if not method_frame:
                    break

                should_remove = False

                if filter_func:
                    try:
                        message = json.loads(body) if body else {}
                        should_remove = filter_func(message)
                    except:
                        # Если не удалось распарсить JSON, удаляем как поврежденное
                        should_remove = True
                else:
                    # Без фильтра - удаляем все
                    should_remove = True

                if should_remove:
                    # Подтверждаем и удаляем
                    self.channel.basic_ack(method_frame.delivery_tag)
                    removed_count += 1
                    logger.debug(f"Удалено сообщение {i + 1}/{total_messages}")
                else:
                    # Возвращаем обратно в очередь
                    self.channel.basic_nack(method_frame.delivery_tag, requeue=True)

                # Чтобы не перегружать систему
                if i % 100 == 0:
                    time.sleep(0.1)

            logger.info(f"Фильтрация завершена. Удалено {removed_count} из {total_messages} сообщений")

        except Exception as e:
            logger.error(f"Ошибка фильтрации очереди: {e}")

        return removed_count

    def remove_ai_failed_messages(self, queue_name: str = 'search_queue') -> int:
        """Удаление сообщений, которые не смог обработать AI"""

        def ai_failed_filter(message: Dict[str, Any]) -> bool:
            # Проверяем, был ли уже неудачный AI запрос
            query = message.get('query', '').lower()

            # Ключевые фразы, которые указывают на проблемы с AI
            problematic_phrases = [
                'тест',
                'test',
                '123',
                'asdf',
                'qwerty',
                'проверка',
                'короткий запрос',
                'непонятно',
                '??',
                '!!!'
            ]

            # Если запрос слишком короткий
            if len(query) < 5:
                return True

            # Если содержит проблемные фразы
            for phrase in problematic_phrases:
                if phrase in query:
                    return True

            return False

        return self.remove_specific_messages(queue_name, ai_failed_filter)

    def close(self):
        """Закрытие соединения"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Соединение закрыто")


def main():
    """CLI для управления очередями"""
    import argparse

    parser = argparse.ArgumentParser(description='Управление очередями RabbitMQ')
    parser.add_argument('--host', default='localhost', help='Хост RabbitMQ')
    parser.add_argument('--port', type=int, default=5672, help='Порт RabbitMQ')
    parser.add_argument('--queue', default='search_queue', help='Имя очереди')

    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Статистика
    stats_parser = subparsers.add_parser('stats', help='Статистика очереди')

    # Просмотр
    peek_parser = subparsers.add_parser('peek', help='Просмотр сообщений')
    peek_parser.add_argument('--count', type=int, default=10, help='Количество сообщений')

    # Очистка
    purge_parser = subparsers.add_parser('purge', help='Полная очистка очереди')

    # Удаление проблемных
    clean_parser = subparsers.add_parser('clean', help='Удаление проблемных сообщений')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    manager = QueueManager(args.host, args.port)

    try:
        manager.connect()

        if args.command == 'stats':
            stats = manager.get_queue_stats(args.queue)
            print(f"\n📊 Статистика очереди '{args.queue}':")
            print(f"   Всего сообщений: {stats.get('message_count', 0)}")
            print(f"   Consumer'ов: {stats.get('consumer_count', 0)}")
            print(f"   Готовых сообщений: {stats.get('ready_messages', 0)}")
            print(f"   Неподтвержденных: {stats.get('unacked_messages', 0)}")

        elif args.command == 'peek':
            messages = manager.peek_messages(args.queue, args.count)
            print(f"\n👀 Просмотр сообщений в очереди '{args.queue}':")
            for i, msg in enumerate(messages, 1):
                print(f"\n--- Сообщение {i} ---")
                if 'error' in msg:
                    print(f"   Ошибка: {msg['error']}")
                    print(f"   Тело: {msg['body_preview']}")
                else:
                    print(f"   Task ID: {msg['message'].get('task_id', 'N/A')}")
                    print(f"   Query: {msg['message'].get('query', 'N/A')[:100]}")
                    print(f"   Приоритет: {msg['message'].get('priority', 'N/A')}")

        elif args.command == 'purge':
            confirm = input(f"⚠️  Вы уверены, что хотите полностью очистить очередь '{args.queue}'? (yes/no): ")
            if confirm.lower() == 'yes':
                count = manager.purge_queue(args.queue)
                print(f"✅ Очередь очищена. Удалено {count} сообщений.")
            else:
                print("❌ Операция отменена.")

        elif args.command == 'clean':
            confirm = input(f"⚠️  Удалить проблемные сообщения из очереди '{args.queue}'? (yes/no): ")
            if confirm.lower() == 'yes':
                count = manager.remove_ai_failed_messages(args.queue)
                print(f"Удалено {count} проблемных сообщений.")
            else:
                print("Операция отменена.")

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        manager.close()


if __name__ == "__main__":
    main()