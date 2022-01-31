
from flask import render_template,redirect, request,session,flash
from muro import app
from muro.models.model_mensaje import Mensaje
from muro.models.model_usuario import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def load_page():
    return render_template('index.html')

@app.route('/dashboard')
def load_dashboard():
    if 'id' in session:
        data = {
            "id" : session["id"]
        }
        usuarios = User.othersUsers(data)
        mensajes = User.getMessages(data)
        user = {
            "email" : session["email"]
        }
        data = User.getUserxEmail(user)
        print(data.mensajes_enviados)
        return render_template('dashboard.html',usuarios=usuarios,mensajes=mensajes,mensajes_enviados=data.mensajes_enviados)
    else:
        return redirect('/')

@app.route('/login',methods=["POST"])
def login():
    user = {
        "email" : request.form["input_email_login"],
        "password" : request.form["input_password_login"]
    }
    password = request.form["input_password_login"]
    if(User.verifyDataUserLogin(user)):
        resultado = User.getUserxEmail(user)
        if(resultado != None):
            if not (bcrypt.check_password_hash(resultado.password,password)):
                flash("Invalid credentials","login")
                return redirect("/")
            else:
                session["name"] = resultado.nombres
                session["id"] = resultado.id
                session["email"] = resultado.email
                return redirect("/dashboard")
        else:
            flash("Invalid credentials","login")
            return redirect('/') 
    else:
        return redirect('/')

@app.route('/register',methods=["POST"])
def register():
    user = {
        "nombres" : request.form["input_first_name"], 
        "apellidos" : request.form["input_last_name"],
        "email" : request.form["input_email"],
        "password" : request.form["input_password"],
        "confirm_password" : request.form["input_confirm_password"]
    }
    if(User.verifyDataUserRegister(user)):
        user["password"] = bcrypt.generate_password_hash(request.form["input_password"])
        result = User.addUser(user)
        if(result > 0):
            session["name"] = request.form["input_first_name"]
            session["id"] = result
            session["email"] = request.form["input_email"]
            return redirect('/dashboard')
        else:
            flash("An error occurred while trying to save the data","register")
            return redirect('/')
    else:
        return redirect('/')


@app.route('/logout',methods=["POST"])
def logout():
    session.clear()
    return redirect('/')