import traceback
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
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competencia"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    return render_template('admin-areas.html', data=data)

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
        try:
            nombres = request.form.get('nombres').strip()
            apellidos = request.form.get('apellidos').strip()
            fecha_nacimiento = request.form.get('fechaNacimiento')
            ci = request.form.get('ci').strip()
            email = request.form.get('email').strip()
            telefono = request.form.get('numCelular').strip()
            rol = request.form.get('rol').strip()
            contrasena = request.form.get('password').strip()


            cursor = mysql.connection.cursor()

            cursor.execute("SELECT MAX(id_usuario) FROM usuario")
            max_id_usuario = cursor.fetchone()['MAX(id_usuario)'] or 0
            new_id_usuario = max_id_usuario + 1

            query_usuario = """
                INSERT INTO usuario (id_usuario, nombre, apellido, email, telefono, contrasenia, rol)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_usuario, (new_id_usuario, nombres,
                           apellidos, email, telefono, contrasena, rol))
            mysql.connection.commit()

            if rol == 'cajero':
                cursor.execute("SELECT MAX(id_cajero) FROM cajero")
                max_id_cajero = cursor.fetchone()['MAX(id_cajero)'] or 0
                new_id_cajero = max_id_cajero + 1

                query_cajero = "INSERT INTO cajero (id_cajero, id_usuario) VALUES (%s, %s)"
                cursor.execute(query_cajero, (new_id_cajero, new_id_usuario))

            elif rol == 'tutor':
                cursor.execute("SELECT MAX(id_tutor) FROM tutor")
                max_id_tutor = cursor.fetchone()['MAX(id_tutor)'] or 0
                new_id_tutor = max_id_tutor + 1

                tipo_tutor = "profesor"  
                query_tutor = "INSERT INTO tutor (id_tutor, id_usuario, tipo_tutor) VALUES (%s, %s, %s)"
                cursor.execute(query_tutor, (new_id_tutor,
                               new_id_usuario, tipo_tutor))

            elif rol == 'administrador':
                cursor.execute(
                    "SELECT MAX(id_administrador) FROM administrador")
                max_id_administrador = cursor.fetchone()[
                    'MAX(id_administrador)'] or 0
                new_id_administrador = max_id_administrador + 1

                query_administrador = "INSERT INTO administrador (id_administrador, id_usuario) VALUES (%s, %s)"
                cursor.execute(query_administrador,
                               (new_id_administrador, new_id_usuario))

            mysql.connection.commit()
            cursor.close()

            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('registrarse'))

        except Exception as e:
            mysql.connection.rollback()
            flash(
                f'Ocurrió un error al registrar el usuario: {str(e)}', 'danger')
            return redirect(url_for('registrarse'))

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
        estado = 'pendiente'

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
            (ci, nombre, apellido, email, telefono, fecha_nacimiento, colegio, curso, departamento, provincia, estado) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (ci, nombre, apellido, email, telefono, fecha_nacimiento, colegio, curso, departamento, provincia, estado)
        )
        
        mysql.connection.commit()
        flash('Te has registrado como competidor correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return redirect(url_for('inscribirse'))

@app.route('/obtener_tutores')
def obtener_tutores():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id_usuario, nombre, apellido FROM Usuario WHERE rol = 'tutor'")
        tutores = cursor.fetchall()
        cursor.close()
        
        return jsonify(tutores)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
@app.route('/obtener_tutores_completos')
def obtener_tutores_completos():
    try:
        # Crear un cursor para ejecutar consultas SQL
        cursor = mysql.connection.cursor()
        
        # Consulta SQL para obtener todos los datos de los tutores
        cursor.execute("SELECT id_usuario, nombre, apellido, email, telefono FROM Usuario WHERE rol = 'tutor'")
        
        # Obtener los resultados
        tutores = cursor.fetchall()
        
        # Cerrar el cursor
        cursor.close()
        
        return jsonify(tutores)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    
@app.route('/registrar-area', methods=['POST'])
@admin_required
def registrar_area():
    data = {}
    data['curso'] = request.form['curso']
    data['area'] = request.form['area']
    data['categoria'] = request.form['categoria']

    cursor = mysql.connection.cursor()
    sql = "INSERT INTO competencia (area, categoria, grado) VALUES (%s, %s, %s)" 
    cursor.execute(sql, (data['area'], data['categoria'], data['curso']))
    mysql.connection.commit()
    cursor.close()
    flash('Área registrada correctamente', 'success')
    return redirect(url_for('adminareas'))

@app.route('/eliminar-comptencia', methods=['POST'])
@admin_required
def eliminar_competencia():
    data = {}
    data['id'] = request.form['id']
    
    cursor = mysql.connection.cursor()
    sql = "DELETE FROM competencia WHERE id_competencia = %s" 
    cursor.execute(sql, (data['id'],))
    mysql.connection.commit()
    cursor.close()
    flash('Competencia eliminada correctamente', 'success')
    return redirect(url_for('adminareas'))
