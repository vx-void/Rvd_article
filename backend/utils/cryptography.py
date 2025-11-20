import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Union
import secrets
import string


class CryptographyService:
    """
    Сервис для криптографических операций: шифрование, дешифрование, хеширование паролей
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Инициализация сервиса криптографии

        Args:
            secret_key: Секретный ключ для шифрования. Если не указан, генерируется автоматически
        """
        self.secret_key = secret_key or os.environ.get('CRYPTO_SECRET_KEY')
        if not self.secret_key:
            raise ValueError("Секретный ключ не предоставлен и не найден в переменных окружения")

        # Генерируем ключ шифрования из секретного ключа
        self.fernet = self._generate_fernet_key(self.secret_key)

    @staticmethod
    def generate_secret_key(length: int = 32) -> str:
        """
        Генерирует случайный секретный ключ

        Args:
            length: Длина ключа в байтах

        Returns:
            Случайный ключ в base64
        """
        random_bytes = os.urandom(length)
        return base64.urlsafe_b64encode(random_bytes).decode()

    @staticmethod
    def generate_password(length: int = 16) -> str:
        """
        Генерирует случайный безопасный пароль

        Args:
            length: Длина пароля

        Returns:
            Случайный пароль
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _generate_fernet_key(self, password: str) -> Fernet:
        """
        Генерирует ключ Fernet из пароля

        Args:
            password: Пароль для генерации ключа

        Returns:
            Объект Fernet для шифрования/дешифрования
        """
        # Конвертируем пароль в байты
        password_bytes = password.encode()

        # Генерируем salt
        salt = b'hydro_search_salt_'  # В продакшене лучше использовать случайный salt

        # Используем PBKDF2 для генерации ключа
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Шифрует данные

        Args:
            data: Данные для шифрования (строка или байты)

        Returns:
            Зашифрованные данные в base64

        Raises:
            ValueError: Если данные пустые
        """
        if not data:
            raise ValueError("Данные для шифрования не могут быть пустыми")

        # Конвертируем строку в байты если нужно
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Шифруем данные
        encrypted_data = self.fernet.encrypt(data)

        # Кодируем в base64 для безопасного хранения
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Дешифрует данные

        Args:
            encrypted_data: Зашифрованные данные в base64

        Returns:
            Расшифрованная строка

        Raises:
            ValueError: Если данные повреждены или неверный ключ
        """
        if not encrypted_data:
            raise ValueError("Данные для дешифрования не могут быть пустыми")

        try:
            # Декодируем из base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())

            # Дешифруем
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)

            # Конвертируем в строку
            return decrypted_bytes.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Ошибка дешифрования: {str(e)}")

    def encrypt_dict(self, data_dict: dict) -> dict:
        """
        Шифрует все строковые значения в словаре

        Args:
            data_dict: Словарь с данными для шифрования

        Returns:
            Словарь с зашифрованными значениями
        """
        encrypted_dict = {}

        for key, value in data_dict.items():
            if isinstance(value, str):
                encrypted_dict[key] = self.encrypt(value)
            elif isinstance(value, dict):
                encrypted_dict[key] = self.encrypt_dict(value)
            elif isinstance(value, list):
                encrypted_dict[key] = [self.encrypt(item) if isinstance(item, str) else item
                                       for item in value]
            else:
                encrypted_dict[key] = value

        return encrypted_dict

    def decrypt_dict(self, encrypted_dict: dict) -> dict:
        """
        Дешифрует все строковые значения в словаре

        Args:
            encrypted_dict: Словарь с зашифрованными данными

        Returns:
            Словарь с расшифрованными значениями
        """
        decrypted_dict = {}

        for key, value in encrypted_dict.items():
            if isinstance(value, str):
                try:
                    decrypted_dict[key] = self.decrypt(value)
                except ValueError:
                    # Если не удалось дешифровать, оставляем как есть (может быть незашифрованным)
                    decrypted_dict[key] = value
            elif isinstance(value, dict):
                decrypted_dict[key] = self.decrypt_dict(value)
            elif isinstance(value, list):
                decrypted_dict[key] = [self.decrypt(item) if isinstance(item, str) else item
                                       for item in value]
            else:
                decrypted_dict[key] = value

        return decrypted_dict

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Создает безопасный хеш пароля

        Args:
            password: Пароль для хеширования
            salt: Соль для хеширования. Если не указана, генерируется случайная

        Returns:
            Кортеж (хеш, соль)
        """
        if not password:
            raise ValueError("Пароль не может быть пустым")

        # Генерируем случайную соль если не предоставлена
        if salt is None:
            salt = secrets.token_hex(16)

        # Создаем хеш с использованием соли
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Количество итераций
        )

        # Конвертируем хеш в hex строку
        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        Проверяет пароль против хеша

        Args:
            password: Пароль для проверки
            password_hash: Ожидаемый хеш пароля
            salt: Соль использованная при хешировании

        Returns:
            True если пароль верный, иначе False
        """
        try:
            # Создаем хеш из предоставленного пароля
            test_hash, _ = CryptographyService.hash_password(password, salt)

            # Сравниваем хеши безопасным способом (constant-time comparison)
            return secrets.compare_digest(test_hash, password_hash)

        except Exception:
            return False

    @staticmethod
    def generate_api_key(prefix: str = "hs") -> str:
        """
        Генерирует случайный API ключ

        Args:
            prefix: Префикс для ключа

        Returns:
            Случайный API ключ
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    def encrypt_file(self, input_file_path: str, output_file_path: str) -> bool:
        """
        Шифрует файл

        Args:
            input_file_path: Путь к исходному файлу
            output_file_path: Путь для сохранения зашифрованного файла

        Returns:
            True если успешно, иначе False
        """
        try:
            with open(input_file_path, 'rb') as file:
                file_data = file.read()

            encrypted_data = self.fernet.encrypt(file_data)

            with open(output_file_path, 'wb') as file:
                file.write(encrypted_data)

            return True

        except Exception as e:
            print(f"Ошибка шифрования файла: {e}")
            return False

    def decrypt_file(self, input_file_path: str, output_file_path: str) -> bool:
        """
        Дешифрует файл

        Args:
            input_file_path: Путь к зашифрованному файлу
            output_file_path: Путь для сохранения расшифрованного файла

        Returns:
            True если успешно, иначе False
        """
        try:
            with open(input_file_path, 'rb') as file:
                encrypted_data = file.read()

            decrypted_data = self.fernet.decrypt(encrypted_data)

            with open(output_file_path, 'wb') as file:
                file.write(decrypted_data)

            return True

        except Exception as e:
            print(f"Ошибка дешифрования файла: {e}")
            return False

    def get_key_fingerprint(self) -> str:
        """
        Получает отпечаток ключа шифрования

        Returns:
            Отпечаток ключа в виде hex строки
        """
        key_hash = hashlib.sha256(self.fernet._signing_key + self.fernet._encryption_key).hexdigest()
        return key_hash[:16]  # Первые 16 символов для краткости


# Утилиты для удобства
class CryptoUtils:
    """Утилиты для криптографии"""

    @staticmethod
    def init_crypto_service() -> CryptographyService:
        """
        Инициализирует сервис криптографии с ключом из переменных окружения
        или создает новый ключ при первом запуске
        """
        secret_key = os.environ.get('CRYPTO_SECRET_KEY')

        if not secret_key:
            # Генерируем новый ключ
            secret_key = CryptographyService.generate_secret_key()

            # Сохраняем в переменные окружения (для текущей сессии)
            os.environ['CRYPTO_SECRET_KEY'] = secret_key

            print("⚠️  Сгенерирован новый секретный ключ. Сохраните его в .env файл:")
            print(f"CRYPTO_SECRET_KEY={secret_key}")

        return CryptographyService(secret_key)

    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """
        Проверяет надежность пароля

        Args:
            password: Пароль для проверки

        Returns:
            Словарь с результатами проверки
        """
        result = {
            'is_strong': False,
            'length_ok': len(password) >= 8,
            'has_upper': any(c.isupper() for c in password),
            'has_lower': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'score': 0
        }

        # Подсчет очков
        result['score'] = sum([
            result['length_ok'],
            result['has_upper'],
            result['has_lower'],
            result['has_digit'],
            result['has_special']
        ])

        result['is_strong'] = result['score'] >= 4

        return result