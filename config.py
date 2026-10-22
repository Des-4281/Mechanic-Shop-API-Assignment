import os
from dotenv import load_dotenv

load_dotenv()


class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'testing-secret'
    RATELIMIT_ENABLED = False
    TESTING = True



class ProductionConfig:
    pass
