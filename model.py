from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy(app)

class Preceptor(db.Model):
  __tablename__='preceptor'
  id=db.Column(db.Integer,primary_key=True)
  nombre=db.Column(db.String(100),nullable=False)
  apellido=db.Column(db.String(100),nullable=False)
  correo=db.Column(db.String(100), unique=True, nullable=False)
  clave=db.Column(db.String(100),nullable=False)
  cursos=db.relationship('Curso',backref='preceptor', cascade="all, delete-orphan")

class Curso(db.Model):
  __tablename__='curso'
  id=db.Column(db.Integer, primary_key=True)
  anio=db.Column(db.Integer, nullable=False)
  division=db.Column(db.Integer, nullable=False)
  estudiantes=db.relationship('Estudiante',backref='curso',cascade = "all, delete-orphan")
  idpreceptor=db.Column(db.Integer,db.ForeignKey('preceptor.id'))


class Estudiante(db.Model):
  __tablename__='estudiante'
  id=db.Column(db.Integer,primary_key=True)
  nombre=db.Column(db.String(100),nullable=False)
  apellido=db.Column(db.String(100),nullable=False)
  dni=db.Column(db.String(15),nullable=False)
  idcurso=db.Column(db.Integer,db.ForeignKey('curso.id'))
  idpadre=db.Column(db.Integer,db.ForeignKey('padre.id'))
  asistencias = db.relationship('Asistencia',backref='estudiante',cascade="all,delete-orphan")
  def __gt__(self,otro):
    if type(self)==type(otro):
      if self.apellido==otro.apellido:
        return self.nombre>otro.nombre
      else:
        return self.apellido>otro.apellido
    else:
      if otro==self.apellido:
        return self.nombre>otro
      else:
        return self.apellido>otro
  
class Padre(db.Model):
  __tablename__='padre'
  id=db.Column(db.Integer,primary_key=True)
  nombre=db.Column(db.String(100),nullable=False)
  apellido=db.Column(db.String(100),nullable=False)
  correo=db.Column(db.String(100), unique=True, nullable=False)
  clave=db.Column(db.String(100),nullable=False)
  estudiantes=db.relationship('Estudiante',backref='padre',cascade = "all, delete-orphan")

class Asistencia(db.Model):
  __tablename__='asistencia'
  id=db.Column(db.Integer,primary_key=True)
  fecha=db.Column(db.DateTime,nullable=False)
  codigoclase=db.Column(db.Integer,nullable=False)
  asistio=db.Column(db.Text, nullable=False)
  justificacion=db.Column(db.String(150),nullable=False)
  idestudiante=db.Column(db.Integer,db.ForeignKey('estudiante.id'))
  