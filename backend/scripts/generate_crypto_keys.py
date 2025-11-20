#!/usr/bin/env python3
"""
Скрипт для генерации криптографических ключей
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from backend.utils import CryptographyService, CryptoUtils

def main():
    print("Генерация криптографических ключей")
    print("=" * 50)

    # Генерация секретного ключа
    secret_key = CryptographyService.generate_secret_key()
    print(f"Секретный ключ: {secret_key}")
    print()

    # Генерация API ключей
    for i in range(3):
        api_key = CryptographyService.generate_api_key()
        print(f"API Ключ {i + 1}: {api_key}")

    print()

    # Генерация паролей
    for i in range(3):
        password = CryptographyService.generate_password(16)
        strength = CryptoUtils.validate_password_strength(password)
        print(f"Пароль {i + 1}: {password} (сила: {strength['score']}/5)")

    print()
    print("Сохраните эти ключи в безопасном месте!")
    print("Добавьте секретный ключ в .env файл:")
    print(f'CRYPTO_SECRET_KEY="{secret_key}"')


if __name__ == '__main__':
    main()