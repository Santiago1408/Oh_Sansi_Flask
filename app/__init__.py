from flask import Flask
from flask_mysqldb import MySQL
from flask_session import Session
import os

app = Flask(__name__)
app.config.from_object('config.Config')

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'olimpiada'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Configuración para el manejo de sesiones
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Inicializar sesión
Session(app)

mysql = MySQL(app)

from app import routes