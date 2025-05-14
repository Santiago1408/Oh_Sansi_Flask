from datetime import date
import traceback
from app import app, mysql
from flask import render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.tables import TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from flask import make_response

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
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competidor WHERE estado = 'validado'"
    cursor.execute(sql)
    data = cursor.fetchall()
    return render_template('cajero.html', data=data)

@app.route('/confirmar-pago', methods=['POST'])
@cajero_required
def confirmar_pago():
    try:
        id_competidor = request.form['id_competidor']
        print("ID Competidor:", id_competidor)
        cursor = mysql.connection.cursor()
        sql = "UPDATE competidor SET estado = 'registrado' WHERE id_competidor = %s"
        cursor.execute(sql, (id_competidor,))
        mysql.connection.commit()
        
        flash('Pago confirmado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al confirmar el pago: {str(e)}', 'danger')
    
    return redirect(url_for('cajero'))

@app.route('/tutor')
@tutor_required
def tutor():
    # Obtener el ID del tutor de la sesión
    tutor_id = session.get('tutor_id')
    cursor = mysql.connection.cursor()
    sql = "SELECT * from competidor WHERE id_tutor = %s and estado = 'pendiente'"
    sql2 = "SELECT * from competidor WHERE id_tutor = %s and estado = 'registrado'"
    cursor.execute(sql, (tutor_id,))
    data = cursor.fetchall() 
    cursor.execute(sql2, (tutor_id,))
    data2 = cursor.fetchall()   
    return render_template('tutor.html', data=data, data2=data2)

@app.route('/validar-competidor', methods=['POST'])
@tutor_required
def validar_competidor():
    try:
        id_competidor = request.form['id_competidor']
        print("ID Competidor:", id_competidor)
        cursor = mysql.connection.cursor()
        sql = "UPDATE competidor SET estado = 'validado' WHERE id_competidor = %s"
        cursor.execute(sql, (id_competidor,))
        mysql.connection.commit()
        
        flash('Competidor validado correctamente', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al validar el competidor: {str(e)}', 'danger')
    
    return redirect(url_for('tutor'))

@app.route('/admin-reportes')
@admin_required
def adminreportes():
    cursor = mysql.connection.cursor()
    sql = "SELECT * FROM competidor WHERE estado = 'registrado'"
    cursor.execute(sql)
    data = cursor.fetchall()
    num_competidores = len(data)
    return render_template('admin-reportes.html', num_competidores=num_competidores)

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

# Ruta para obtener las competencias disponibles
@app.route('/obtener_competencias')
def obtener_competencias():
    try:
        cursor = mysql.connection.cursor()
        
        # Consulta SQL para obtener las competencias
        query = """
        SELECT id_competencia, area, categoria, grado
        FROM Competencia
        """
        
        cursor.execute(query)
        competencias = cursor.fetchall()
        cursor.close()
        
        # Convertir los resultados a una lista de diccionarios - VERSIÓN CORREGIDA
        resultado = []
        for comp in competencias:
            resultado.append({
                'id_competencia': comp['id_competencia'],
                'area': comp['area'],
                'categoria': comp['categoria'],
                'grado': comp['grado']
            })
        
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta para registrar un nuevo competidor
@app.route('/registrar_competidor', methods=['POST'])
def registrar_competidor():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        ci = request.form['ci']
        email = request.form['email']
        telefono = request.form['telefono']
        colegio = request.form['colegio']
        curso = request.form['curso']
        departamento = request.form['departamento']
        provincia = request.form['provincia']
        area = request.form['area']
        categoria = request.form['categoria']
        id_tutor = request.form['id_tutor']
        estado = 'pendiente'
        
        try:
            print(id_tutor)
            cursor = mysql.connection.cursor()
            
            # 1. Insertar el competidor en la tabla Competidor
            insert_competidor = """
            INSERT INTO Competidor (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombre, apellido, email, telefono, estado, id_tutor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_competidor, (ci, fecha_nacimiento, colegio, curso, departamento, provincia, nombre, apellido, email, telefono, estado, id_tutor))
            print("Competidor insertado correctamente")
            
            # Obtener el ID del competidor recién insertado
            id_competidor = cursor.lastrowid
            
            # 2. Crear una inscripción asociando el competidor con el tutor
            insert_inscripcion = """
            INSERT INTO Inscripcion (id_competidor, id_tutor, fecha_inscripcion)
            VALUES (%s, %s, %s)
            """
            fecha_actual = date.today()
            cursor.execute(insert_inscripcion, (id_competidor, id_tutor, fecha_actual))
            
            # 3. Obtener el ID de la competencia según el área, categoría y curso seleccionados
            query_competencia = """
            SELECT id_competencia FROM Competencia
            WHERE area = %s AND categoria = %s AND grado = %s
            """
            cursor.execute(query_competencia, (area, categoria, curso))
            competencia = cursor.fetchone()
            
            if competencia:
                id_competencia = competencia['id_competencia']
                
                # 4. Registrar la participación del competidor en la competencia
                insert_compite = """
                INSERT INTO compite (id_competencia, id_competidor)
                VALUES (%s, %s)
                """
                cursor.execute(insert_compite, (id_competencia, id_competidor))
            
            # 5. Establecer la relación entre el tutor y el competidor en la tabla "Puede tener"
            insert_puede_tener = """
            INSERT INTO puede_tener (id_tutor, id_competidor)
            VALUES (%s, %s)
            """
            cursor.execute(insert_puede_tener, (id_tutor, id_competidor))
            
            # Confirmar los cambios en la base de datos
            mysql.connection.commit()
            
            cursor.close()
            
            # Redirigir a una página de éxito o a la página principal
            return redirect(url_for('home'))
        
        except Exception as e:
            # En caso de error, devolver un mensaje o redirigir a una página de error
            print('error en el registro:', e)
            return str(e)
    
    # Si la solicitud no es POST, redirigir a la página principal
    return redirect(url_for('home'))

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
        # Ahora incluye el id_tutor de la tabla de tutores
        cursor.execute("""
            SELECT u.id_usuario, t.id_tutor, u.nombre, u.apellido, u.email, u.telefono 
            FROM Usuario u
            INNER JOIN tutor t ON u.id_usuario = t.id_usuario
            WHERE u.rol = 'tutor'
        """)
        
        # Obtener los resultados
        tutores_raw = cursor.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        tutores = []
        for tutor in tutores_raw:
            tutores.append({
                'id_usuario': tutor['id_usuario'],
                'id_tutor': tutor['id_tutor'],
                'nombre': tutor['nombre'],
                'apellido': tutor['apellido'],
                'email': tutor['email'],
                'telefono': tutor['telefono']
            })
        
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

@app.route('/generar-reporte-pdf', methods=['POST'])
@admin_required
def generar_reporte_pdf():
    grado = request.form['grado'].strip()
    print("Grado recibido:", grado)  

    cursor = mysql.connection.cursor()

    sql = """
        SELECT nombre, apellido, ci, colegio, curso, departamento, provincia, email, telefono
        FROM competidor
        WHERE LOWER(REPLACE(curso, ' ', '')) = LOWER(REPLACE(%s, ' ', '')) 
          AND estado = 'registrado'
    """
    cursor.execute(sql, (grado,))
    data = cursor.fetchall()
    cursor.close()

    print(f"Total filas recuperadas: {len(data)}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Reporte de Competidores - Nivel: {grado}", styles['Title']))
    elements.append(Spacer(1, 12))

    table_data = [[
        'Nombre', 'Apellido', 'CI', 'Colegio', 'Curso',
        'Departamento', 'Provincia', 'Email', 'Teléfono'
    ]]

    if data:
        for row in data:
            # Convertir cada celda a string, asegurando que no haya None
            # y reemplazando None por una cadena vacía
            table_data.append([
                str(row['nombre']) if row['nombre'] is not None else '',
                str(row['apellido']) if row['apellido'] is not None else '',
                str(row['ci']) if row['ci'] is not None else '',
                str(row['colegio']) if row['colegio'] is not None else '',
                str(row['curso']) if row['curso'] is not None else '',
                str(row['departamento']) if row['departamento'] is not None else '',
                str(row['provincia']) if row['provincia'] is not None else '',
                str(row['email']) if row['email'] is not None else '',
                str(row['telefono']) if row['telefono'] is not None else ''
            ])
            
    else:
        table_data.append(['No hay datos disponibles para este nivel'] + [''] * 8)

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Reporte_{grado.replace(" ", "_")}.pdf'

    return response