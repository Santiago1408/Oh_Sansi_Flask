import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tunari_tech_srl')