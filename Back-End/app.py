import json
import os

from alchemyClasses import db
from alchemyClasses.Participante import Participante
from alchemyClasses.Administrador import Administrador
from CryptoUtils.CryptoUtils import validate
from flask import (
    Flask,
    render_template,
    request,
    flash,
    session,
    g,
    redirect,
    url_for,
    jsonify,
)
from flask_cors import CORS

from controllers.AdminController import admin
from controllers.TorneoController import torneo

from model.model_administrador import get_admin_by_email, get_all_admins, get_admin_by_id
from model.model_superadmin import get_superadmin_by_email
from model.model_participante import get_participante_by_email
 
from model.model_torneo import get_all_torneos, get_torneo_by_id,get_current_datetime

def get_user_by_email(email):
    participante_query = get_participante_by_email(email)
    administrador_query = get_admin_by_email(email)
    superadministrador_query = get_superadmin_by_email(email)

    if participante_query:
        return participante_query, "participante"
    elif administrador_query:
        return administrador_query, "administrador"
    elif superadministrador_query:
        return superadministrador_query, "superadmin"
    else:
        return None, "none"


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+pymysql://michigames:michigames123@localhost:3306/proyecto"
app.config.from_mapping(
    SECRET_KEY="dev",
)

#Agregamos controladores
app.register_blueprint(admin)
app.register_blueprint(torneo)

db.init_app(app)
CORS(app)


@app.route("/", methods=["GET", "POST"])
def main():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    return jsonify({"message": "registro con flask"})
    # if request.method == 'POST':
    #     nombre = request.form['nombre']
    #     apellido = request.form['apellido']
    #     correo = request.form['correo']
    #     psswd = request.form['password']
    #     try:
    #         participante = Participante(nombre, apellido, correo, psswd)
    #         db.session.add(participante)
    #         db.session.commit()
    #     except Exception as e:
    #         db.session.rollback()  # Revertir cambios en caso de error
    #         print(f"Error: {str(e)}")
    # #return render_template('register.html')
    # return jsonify({'message':'Registro exitoso'})


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user", None) is not None and request.method == "GET":
        return redirect(url_for("index"))
    if request.method == "POST":
        datos_json = request.get_json()
        try:
            email = datos_json["email"]
            password = datos_json["password"]
            user_query, tipo_usuario = get_user_by_email(email)
            if not (user_query):
                flash("Ese correo no existe.")
                return jsonify({"error": "Ese correo no existe"})
                # return render_template('login.html')
            user = user_query[0]
            if not validate(password, user.psswd):
                flash("Contraseña incorrecta")
                return jsonify({"error": "Contraseña incorrecta"})
                # return render_template('login.html')
            session.clear()
            session["nombre"] = user.nombre
            session["apellido"] = user.apellido
            session["email"] = user.correo
            session["tipo_usuario"] = tipo_usuario
            session.modified = True
            return jsonify(
                {
                    "error": "Ninguno",
                    "nombre": user.nombre,
                    "apellido": user.apellido,
                    "email": user.correo,
                    "tipo_usuario": tipo_usuario,
                }
            )
            # return render_template('index.html')
        except KeyError:
            flash("No fue enviado con éxito el correo y/o la contraseña")
            return render_template('login.html')
    return render_template('login.html')


@app.route("/index", methods=["GET", "POST"])
def index():
    if session.get("user", None) is None:
        flash("Por favor primero inicie sesión.")
        # return redirect(url_for('login'))
    # return render_template('index.html')


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    g.user = None
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run()
