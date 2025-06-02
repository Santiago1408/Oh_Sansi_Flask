import re
from datetime import datetime
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config.from_object('config.Config')

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '10734578'
app.config['MYSQL_DB'] = 'olimpiada'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

from app import routes

def validar_nombre(nombre: str) -> tuple[bool, str]:
    if not nombre:
        return False, "El nombre no puede estar vacío."
    if len(nombre) < 2 or len(nombre) > 30:
        return False, "El nombre debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", nombre):
        return False, "Solo debe contener letras y espacios."
    return True, "Nombre válido."


def validar_apellido(apellido: str) -> tuple[bool, str]:
    if not apellido:
        return False, "El apellido no puede estar vacío."
    if len(apellido) < 2 or len(apellido) > 30:
        return False, "El apellido debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", apellido):
        return False, "Solo debe contener letras y espacios."
    return True, "Apellido válido."
    
def validar_colegio(colegio: str) -> tuple[bool, str]:
    if not colegio:
        return False, "El campo no puede estar vacío."
    if len(colegio) <2 or len(colegio) > 30:
        return False, "El campo debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", colegio):
        return False, "Solo debe contener letras y espacios."
    
def validar_curso(curso: str) -> tuple[bool, str]:
    if not curso:
        return False, "El campo no puede estar vacío."
    if len(curso) <2 or len(curso) > 30:
        return False, "El campo debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", curso):
        return False, "Solo debe contener letras y espacios."
    
def validar_provincia(provincia: str) -> tuple[bool, str]:
    if not provincia:
        return False, "El campo no puede estar vacío."
    if len(provincia) <2 or len(provincia) > 30:
        return False, "El campo debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", provincia):
        return False, "Solo debe contener letras y espacios."

def validar_departamento(departamento: str) -> tuple[bool, str]:
    if not departamento:
        return False, "El campo no puede estar vacío."
    if len(departamento) <2 or len(departamento) > 30:
        return False, "El campo debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", departamento):
        return False, "Solo debe contener letras y espacios."
    
def validar_area(area: str) -> tuple[bool, str]:
    if not area:
        return False, "El campo no puede estar vacío."
    if len(area) <2 or len(area) > 30:
        return False, "El campo debe tener entre 2 y 30 caracteres."
    if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", area):
        return False, "Solo debe contener letras y espacios."

def validar_telefono(telefono: str) -> bool:
    return bool(re.fullmatch(r"\d{8}", telefono))

def validar_carnet(carnet: str) -> bool:
    return bool(re.fullmatch(r"\d{6,8}", carnet))

def validar_correo(correo: str) -> tuple[bool, str]:
    if not correo:
        return False, "El correo no puede estar vacío."

    patron = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    if not re.match(patron, correo):
        return False, "El correo electrónico no es válido."

    return True, "Correo electrónico válido."

#Fecha de nacimiento
def validar_fecha_nacimiento(fecha_str: str) -> tuple[bool, str]:
    try:
        fecha = datetime.strptime(fecha_str, "%d-%m-%Y")
    except ValueError:
        return False, "Formato de fecha inválido. Usa DD-MM-AAAA."

    hoy = datetime.today()
    edad = (hoy - fecha).days // 365

    if edad < 8:
        return False, "Debes tener al menos 8 años."
    if edad > 18:
        return False, "La edad no puede superar los 18 años."

    return True, "Fecha de nacimiento válida."


def validar_contrasenia(contra: str) -> tuple[bool, str]:
    if len(contra) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r'[A-Z]', contra):
        return False, "Debe contener al menos una letra mayúscula."
    if not re.search(r'[a-z]', contra):
        return False, "Debe contener al menos una letra minúscula."
    if not re.search(r'[0-9]', contra):
        return False, "Debe contener al menos un número."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contra):
        return False, "Debe contener al menos un carácter especial."

    return True, "Contraseña segura."

def verificar_contrasenias(contra: str, confirmar: str) -> tuple[bool, str]:
    if contra != confirmar:
        return False, "Las contraseñas no coinciden."
    return True, "Las contraseñas coinciden."

