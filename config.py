import os

class Config:
    """Configuración base para la aplicación Flask."""
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = True
    
    # Configuración de la base de datos MySQL
    MYSQL_HOST = '127.0.0.1'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'olimpiada'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Configuración de Flask-Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Carpetas de la aplicación
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}