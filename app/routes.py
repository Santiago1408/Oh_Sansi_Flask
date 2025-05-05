from app import app, mysql
from flask import render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
import re

# Decoradores para proteger rutas según el tipo de usuario
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Inicia sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'administrador':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def cajero_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'cajero':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def tutor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'tutor':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def competidor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session['rol'] != 'competidor':
            flash('No tienes permisos para acceder a esta página', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competencia"
    cursor.execute(sql)
    data = cursor.fetchall()
    print(data)
    return render_template('home.html')

@app.route('/admin-areas')
@admin_required
def adminareas():
    return render_template('admin-areas.html')

@app.route('/cajero')
@cajero_required
def cajero():
    return render_template('cajero.html')

@app.route('/tutor')
@tutor_required
def tutor():
    return render_template('tutor.html')

@app.route('/inscripcion')
@login_required
def inscripcion():
    return render_template('inscripcion.html')

@app.route('/admin-reportes')
@admin_required
def adminreportes():
    return render_template('admin-reportes.html')

@app.route('/admin-competencia')
@admin_required
def admincompetencia():
    return render_template('admin-competencia.html')

@app.route('/inscribirse')
def inscribirse():
    return render_template('form-competidor.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        
        # Validar formato de correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Formato de correo electrónico inválido', 'error')
            return render_template('login.html')
        
        # Verificar si el usuario existe en la base de datos
        cursor = mysql.connection.cursor()
        
        # Consultar la tabla de usuarios
        cursor.execute("SELECT * FROM usuario WHERE email = %s", [email])
        user = cursor.fetchone()
        
        if not user:
            flash('Usuario no encontrado', 'error')
            return render_template('login.html')
        
        # Verificar la contraseña
        contrasenia = request.form['password']
        if user['contrasenia'] != contrasenia:
            flash('Contraseña incorrecta', 'error')
            return render_template('login.html')

        # Guardar información básica del usuario en la sesión
        session['user_id'] = user['id_usuario']
        session['nombre'] = user['nombre']
        session['apellido'] = user['apellido']
        session['email'] = user['email']
        session['rol'] = user['rol']
        
        # Determinar el tipo específico de usuario y obtener su ID específico
        if user['rol'] == 'administrador':
            cursor.execute("SELECT id_administrador FROM administrador WHERE id_usuario = %s", [user['id_usuario']])
            admin = cursor.fetchone()
            if admin:
                session['admin_id'] = admin['id_administrador']
            return redirect(url_for('admincompetencia'))
            
        elif user['rol'] == 'cajero':
            cursor.execute("SELECT id_cajero FROM cajero WHERE id_usuario = %s", [user['id_usuario']])
            cajero = cursor.fetchone()
            if cajero:
                session['cajero_id'] = cajero['id_cajero']
            return redirect(url_for('cajero'))
            
        elif user['rol'] == 'tutor':
            cursor.execute("SELECT id_tutor FROM tutor WHERE id_usuario = %s", [user['id_usuario']])
            tutor = cursor.fetchone()
            if tutor:
                session['tutor_id'] = tutor['id_tutor']
                session['tipo_tutor'] = tutor['tipo_tutor']
            return redirect(url_for('tutor'))
            
        elif user['rol'] == 'competidor':
            # Para el competidor, se busca en la tabla de competidor por la relación con usuario
            # Esto depende de cómo esté estructurada tu base de datos
            cursor.execute("SELECT * FROM competidor WHERE email = %s", [user['email']])
            competidor = cursor.fetchone()
            if competidor:
                session['competidor_id'] = competidor['id_competidor']
            return redirect(url_for('inscripcion'))
        
        # Si no se identifica el rol específico
        flash('Tipo de usuario no identificado', 'error')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Eliminar todas las variables de sesión
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('home'))

@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        contrasenia = request.form['contrasenia']
        rol = request.form['rol']
        
        # Validar datos
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Formato de correo electrónico inválido', 'error')
            return render_template('registro.html')
        
        # Verificar si el correo ya está registrado
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = %s", [email])
        user_exists = cursor.fetchone()
        
        if user_exists:
            flash('Este correo ya está registrado', 'error')
            return render_template('registro.html')
        
        # Insertar nuevo usuario
        cursor.execute(
            "INSERT INTO usuario (nombre, apellido, email, telefono, contrasenia, rol) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, apellido, email, telefono, contrasenia, rol)
        )
        
        # Obtener el ID del usuario recién insertado
        user_id = cursor.lastrowid
        
        # Según el rol, insertar en la tabla correspondiente
        if rol == 'administrador':
            cursor.execute("INSERT INTO administrador (id_usuario) VALUES (%s)", [user_id])
        elif rol == 'cajero':
            cursor.execute("INSERT INTO cajero (id_usuario) VALUES (%s)", [user_id])
        elif rol == 'tutor':
            tipo_tutor = request.form.get('tipo_tutor', 'general')  # Por defecto 'general' si no se especifica
            cursor.execute("INSERT INTO tutor (id_usuario, tipo_tutor) VALUES (%s, %s)", (user_id, tipo_tutor))
        
        # Competidor se registra en un formulario separado, ya que requiere más datos
        
        mysql.connection.commit()
        flash('Te has registrado correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return render_template('registro.html')

@app.route('/registrar-competidor', methods=['POST'])
def registrar_competidor():
    if request.method == 'POST':
        # Obtener los datos del formulario
        ci = request.form['ci']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        fecha_nacimiento = request.form['fecha_nacimiento']
        colegio = request.form['colegio']
        curso = request.form['curso']
        departamento = request.form['departamento']
        provincia = request.form['provincia']
        
        # Validar datos
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Formato de correo electrónico inválido', 'error')
            return redirect(url_for('inscribirse'))
        
        # Verificar si el CI o correo ya están registrados
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM competidor WHERE ci = %s OR email = %s", (ci, email))
        competidor_exists = cursor.fetchone()
        
        if competidor_exists:
            flash('Este CI o correo ya está registrado', 'error')
            return redirect(url_for('inscribirse'))
        
        # Insertar nuevo competidor
        cursor.execute(
            """INSERT INTO competidor 
            (ci, nombre, apellido, email, telefono, fecha_nacimiento, colegio, curso, departamento, provincia) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (ci, nombre, apellido, email, telefono, fecha_nacimiento, colegio, curso, departamento, provincia)
        )
        
        mysql.connection.commit()
        flash('Te has registrado como competidor correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return redirect(url_for('inscribirse'))