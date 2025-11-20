import os
from dotenv import load_dotenv

class Config:

    # Supabase config
    SUPABASE_URL = load_dotenv('SUPABASE_URL')
    SUPABASE_KEY = load_dotenv('SUPABASE_HOST')
    SUPABASE_DATABASE = load_dotenv('SUPABASE_DATABASE')
    SUPABASE_USER = 'SUPABASE_USER'
    SUPABASE_PASSWORD = 'SUPABASE_PASSWORD'
    SUPABASE_PORT = 'SUPABASE_PORT'

    #Cryptography
    CRYPTO_SECRET_KEY = os.environ.get('CRYPTO_SECRET_KEY')

    # Password Policies
    MIN_PASSWORD_LENGTH = int(os.environ.get('MIN_PASSWORD_LENGTH', 8))
    REQUIRE_PASSWORD_COMPLEXITY = os.environ.get('REQUIRE_PASSWORD_COMPLEXITY', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False