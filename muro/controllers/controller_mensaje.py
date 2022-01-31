
from flask import render_template,redirect, request,session,flash
from muro import app
from muro.models.model_mensaje import Mensaje

@app.route('/send_message',methods=["POST"])
def send_message():
    data = {
        "contenido" : request.form["mensaje"], 
        "usuario_emisor_id" : session["id"], 
        "usuario_receptor_id" : request.form["id"]
    }
    verifica = Mensaje.verifyDataMenssage(data)
    if(verifica):
        resultado = Mensaje.sendMessage(data)
        if not (resultado > 0):
            flash("Error trying to send the message","message")
    return redirect('/dashboard')


@app.route('/delete_message',methods=["POST"])
def delete_message():
    data = {
        "id" : request.form["id_mensaje"]
    }
    Mensaje.deleteMessage(data)
    return redirect('/dashboard')