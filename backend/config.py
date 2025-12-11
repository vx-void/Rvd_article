import os
from dotenv import load_dotenv

class Config:

    # Supabase config
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_HOST = os.environ.get('SUPABASE_HOST')
    SUPABASE_DATABASE = os.environ.get('SUPABASE_DATABASE')
    SUPABASE_USER = os.environ.get('SUPABASE_USER')
    SUPABASE_PASSWORD = os.environ.get('SUPABASE_PASSWORD')
    SUPABASE_PORT = os.environ.get('SUPABASE_PORT')

    #Cryptography
    CRYPTO_SECRET_KEY = os.environ.get('CRYPTO_SECRET_KEY')

    # Password Policies
    MIN_PASSWORD_LENGTH = int(os.environ.get('MIN_PASSWORD_LENGTH', 8))
    REQUIRE_PASSWORD_COMPLEXITY = os.environ.get('REQUIRE_PASSWORD_COMPLEXITY', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False