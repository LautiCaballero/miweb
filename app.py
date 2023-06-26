from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib 
from datetime import datetime 

app = Flask(__name__)
app.config.from_pyfile('config.py')

from model import db, Preceptor, Padre, Curso, Estudiante, Asistencia



@app.route('/',methods=['GET', 'POST'])
def login():
    app.logger.debug("Login")
    if request.method == 'POST':
      if not request.form.get('correo'):
        app.logger.debug("Login primer if")
        return render_template('login.html')
      else:
        app.logger.debug("Login else")
        correo = request.form['correo']
        clave = request.form['clave']
        rol = request.form['rol']
        result = hashlib.md5(clave.encode('utf-8')).hexdigest()
        app.logger.debug("Login else final")
        if rol == 'preceptor':
          actual = Preceptor.query.filter_by(correo=correo).first()
          #actual = db.session.query(Preceptor).filter(Preceptor.correo==correo).first()
          if actual is not None and actual.clave == result:
            session['user_id'] = actual.id
            session['user_type'] = 'Preceptor'
            app.logger.debug("Login antes de redireccion")
            return redirect(url_for('home'))
        elif rol == 'padre':
          usuario = Padre.query.filter(Padre.correo==correo).first()
          if usuario.clave == result:
            session['user_id'] = usuario.id
            session['user_type'] = 'Padre'
            return redirect(url_for('home'))
      flash('Credenciales inválidas. Por favor, inténtelo nuevamente.')
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('user_id', None)
   session.pop('user_type', None)
   return redirect(url_for('login'))

@app.route('/home', methods = ['GET', 'POST'])
def home():
  if not 'user_type' in session:
    return redirect(url_for('login'))
  return render_template('menu.html',tipo=session['user_type'])

@app.route('/cursos', methods=['GET', 'POST'])
def reg_asist():
    if request.method == 'POST':
        if "cursos" not in request.form:
            return render_template('asistencia.html', cursos=Curso.query.filter_by(idpreceptor=session.get('user_id')), curso_selec=None)
        else:
            c = Curso.query.filter_by(id=request.form['cursos']).first()
            clase = int(request.form['clase'])
            fecha = datetime.strptime(request.form['fecha'], "%Y-%m-%d").date()
            c.estudiantes.sort()
            for estudiante in c.estudiantes:
                if request.form['asistencia']:
                    if request.form['asistencia'] == 'n':
                        asistencia = 'n'
                    else:
                        asistencia = 's'
                    justificacion = request.form['justificacion']
                    registro_asistencia = Asistencia(
                        fecha=datetime.strptime(fecha, "%Y-%m-%d").date(),
                        codigoclase=clase,
                        asistio=asistencia,
                        justificacion=justificacion if asistencia == False else '',
                        idestudiante=estudiante.id
                    )
                    db.session.add(registro_asistencia)
                    db.session.commit()
        return render_template('asistencia.html')
            
    else:
       return render_template('asistencia.html', cursos=Curso.query.filter_by(idpreceptor=session.get('user_id')), curso_selec=None)



@app.route('/list_curso',methods=['GET','POST'])
def list_curso():
  if request.method=='POST':
    if not request.form['cursos'] :
      return render_template('list_date_asis.html',cursos=Curso.query.filter_by(idpreceptor==session.get('user_id')))
    else:
      fecha= datetime.strptime(request.form['fecha'], "%Y-%m-%d").date()
      curso=Curso.query.filter_by(id=request.form['cursos']).first()
      curso.estudiantes.sort()
      lista=[]
      for e in curso.estudiantes:
        id=e.id
        a=Asistencia.query.filter_by(fecha=fecha,codigoclase=int(request.form['clase']),idestudiante=id).first()
        if a:
          lista.append({
            'apellido':e.apellido,
            'nombre': e.nombre,
            'asistencia': a.asistio
          })
      return render_template('list_date_asis.html',lista=lista,cursos=None)
  else:
    return render_template('list_date_asis.html',cursos=Curso.query.filter_by(idpreceptor=session.get('user_id')))
  

@app.route('/list_detalle', methods = ['GET', 'POST'])
def list_detalle():
  if request.method == 'POST':
    if not request.form['curso_id']:
      return render_template('list_detalle.html', cursos = Curso.query.filter_by(idpreceptor==session.get('user_id')), curso = None)
    else:
      curso = Curso.query.get(request.form['curso_id'])
      curso.estudiantes.sort()
      lista = []
      for estudiante in curso.estudiantes:
        id = estudiante.id
        asistencia = Asistencia.query.filter_by(idestudiante = id)
        if asistencia:
          aulaP = 0
          aulaJ = 0
          aulaI = 0
          efP = 0
          efJ = 0
          efI = 0
          for a in  asistencia:
            if a.codigoclase == 1:
              if a.asistio == 's':
                aulaP += 1
              elif a.asistio == 'n':
                if a.justificacion is not None:
                  aulaJ += 1
                else:
                  aulaI += 1
            elif a.codigoclase == 2:
              if a.asistio == True:
                efP += 1
              elif a.asistio == False:
                if a.justificacion is not None:
                  efJ += 1
                else:
                  efI += 1
            total = aulaI + aulaJ +(efI / 2) + (efJ/2)
          lista.append({
            'apellido':estudiante.apellido,
            'nombre': estudiante.nombre,
            'aulaP': aulaP,
            'aulaJ': aulaJ,
            'aulaI': aulaI,
            'efP': efP,
            'efJ': efJ,
            'efI': efI,
            'total': total
          })
      return render_template('list_detalle.html', cursos = None, curso = curso, preceptor = session.get('user_id'), lista = lista)

  else:
    return render_template('list_detalle.html', cursos = Curso.query.all(), curso = None, preceptor = session.get('user_id'))

@app.route('/inasis_estudiante', methods = ['GET', 'POST'])
def inasis_estudiante():
  if request.method == 'POST':
    if not request.form['dni']:
      return render_template('inasis_estudiante.html', estudiantes = Estudiante.query.all(), estudiante = None, lista = None)
    else:
      lista = []
      estudiante = Estudiante.query.filter_by(dni = request.form['dni']).first()
      if estudiante is not None:
        asistencias = Asistencia.query.filter(Asistencia.idestudiante == estudiante.id)
        total = 0
        
        for a in asistencias:
          if a.asistio=='n':
            just = a.justificacion 
            if a.codigoclase == 1:
              total += 1
            elif a.codigoclase == 2:
              total += 0.5
            app.logger.debug(f'Fecha: {a.fecha}')
            app.logger.debug(f'Tipo de clase: {a.codigoclase}')
            app.logger.debug(f'Justificación: {just}')
              
            lista.append({
              'fecha': a.fecha,
              'tipo': a.codigoclase,
              'justificacion': just,
            })
        lista.append({
           'fecha': 'total de Inasistencias',
           'tipo': '',
           'justificacion': total,
        })
      
      return render_template('inasis_estudiante.html', estudiantes = None, estudiante = Estudiante.query.filter_by(dni = request.form['dni']).first(), lista = lista)
  else:
    return render_template('inasis_estudiante.html', estudiantes = Estudiante.query.all(), estudiante = None, lista = None)

if __name__ == "__main__":
  with app.app_context():
    db.create_all()
    app.run(host='0.0.0.0', port=8080, debug = True)

