import os
'''
loads environment variables from a .env
'''
from dotenv import load_dotenv



load_dotenv()


class Config:
    ''' base configs'''
    SECRET_KEY = os.getenv('SECRET_KEY')
    LOCATIONS = os.getenv('LOCATIONS')
    LDAPs = os.getenv('LDAP')

    # Database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/inventory_management_db')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))

    #

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}