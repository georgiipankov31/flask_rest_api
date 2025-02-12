import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    DATABASE_URI = os.environ.get('SANDBOX_BASE_URL') or 'postgresql://username:password@localhost/dbname'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=3600) 
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=86400)
