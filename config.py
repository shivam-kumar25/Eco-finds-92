
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'


    

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ecofinds.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Debug configuration
    DEBUG = True
    TESTING = False

