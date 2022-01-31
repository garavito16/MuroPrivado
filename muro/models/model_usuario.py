
from muro.config.mysqlconnection import connectToMySQL
from flask import flash
from muro.models.model_mensaje import Mensaje
import re

NAMES_REGEX = re.compile(r'^[A-Z][a-zA-Z ]{1,80}$')
PASSWORD_REGEX = re.compile(r'^(.)*(?=\w*\d)(?=\w*[A-Z])\S{8,16}$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:
    name_db = "muro_privado"

    def __init__(self, id, nombres, apellidos, email, password, created_at,mensajes_enviados):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.email = email
        self.password= password
        self.created_at = created_at
        self.mensajes_recibidos = []
        self.mensajes_enviados = mensajes_enviados

    def addMensajes(self,mensaje):
        self.mensajes_recibidos.append(mensaje)

    @classmethod
    def addUser(cls,user):
        query = '''
                    INSERT INTO user (nombres, apellidos, password, email, created_at) 
                    VALUES (%(nombres)s, %(apellidos)s, %(password)s, %(email)s, now())
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,user)
        return resultado

    @classmethod
    def getMessages(cls,data):
        query = '''
                    SELECT m.*, CONCAT(u.nombres, ' ', u.apellidos) AS emisor, CONCAT(u2.nombres, ' ', u2.apellidos) AS receptor,
                    (CASE 
                    WHEN  (TIMESTAMPDIFF(YEAR,m.created_at,now()) > 0) THEN CONCAT(TIMESTAMPDIFF(YEAR,m.created_at,now()),' year(s) ago')
                    WHEN  (TIMESTAMPDIFF(MONTH,m.created_at,now()) > 0) THEN CONCAT(TIMESTAMPDIFF(MONTH,m.created_at,now()),' month(s) ago')
                    WHEN  (TIMESTAMPDIFF(DAY,m.created_at,now()) > 0) THEN CONCAT(TIMESTAMPDIFF(DAY,m.created_at,now()),' day(s) ago')
                    WHEN  (TIMESTAMPDIFF(HOUR,m.created_at,now()) > 0) THEN CONCAT(TIMESTAMPDIFF(HOUR,m.created_at,now()),' hour(s) ago')
                    WHEN  (TIMESTAMPDIFF(MINUTE,m.created_at,now()) > 0) THEN CONCAT(TIMESTAMPDIFF(MINUTE,m.created_at,now()),' minute(s) ago')
                    ELSE CONCAT(TIMESTAMPDIFF(SECOND,m.created_at,now()),' second(s) ago') END) AS created_at_diff
                    FROM mensaje m
                    INNER JOIN user u ON u.id = m.user_emisor_id
                    INNER JOIN user u2 ON u2.id = m.user_receptor_id
                    WHERE m.user_receptor_id = %(id)s
                    ORDER BY m.id DESC
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,data)
        mensajes = []
        for mensaje in resultado:
            mensajes.append(Mensaje(mensaje["id"],mensaje["contenido"],mensaje["user_emisor_id"],mensaje["emisor"],
                            mensaje["user_receptor_id"],mensaje["receptor"],mensaje["created_at_diff"]))
        return mensajes

    @classmethod
    def getUserxEmail(cls,user):
        query = '''
                    SELECT u.*, COUNT(m.id) AS cant_message
                    FROM user u
                    LEFT JOIN mensaje m ON m.user_emisor_id = u.id
                    WHERE u.email = %(email)s
                    GROUP BY u.id;
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,user)
        if(len(resultado) > 0):
            user = User(resultado[0]["id"],resultado[0]["nombres"],resultado[0]["apellidos"],resultado[0]["email"],resultado[0]["password"],resultado[0]["created_at"],resultado[0]["cant_message"])
            return user
        else:
            return None
    
    @classmethod
    def othersUsers(cls,data):
        query = '''
                    SELECT u.*
                    FROM user u
                    WHERE id != %(id)s
                    ORDER BY u.nombres, u.apellidos;
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,data)
        usuarios = []
        for usuario in resultado:
            user = User(usuario["id"],usuario["nombres"],usuario["apellidos"],usuario["email"],usuario["password"],usuario["created_at"],0)
            usuarios.append(user)
        return usuarios

    @classmethod
    def verifyDataUserRegister(cls,user):
        print(user)
        is_valid = True
        if not NAMES_REGEX.match(user["nombres"]):
            flash("Invalid first name. Must have at least 2 characters. First letter must be capitalized","register")
            is_valid = False
        if not NAMES_REGEX.match(user["apellidos"]):
            flash("Invalid last name. Must have at least 2 characters","register")
            is_valid = False
        if not EMAIL_REGEX.match(user["email"]):
            flash("Invalid email address","register")
            is_valid = False
        else:
            data = {
                "email" : user["email"]
            }
            if(cls.getUserxEmail(data)!= None):
                flash("There is already a user with the email entered","register")
                is_valid = False
        if not PASSWORD_REGEX.match(user["password"]):
            flash("Invalid password. Must contain at least one capital letter and one number. Minimum of 8 characters and a maximum of 16","register")
            is_valid = False
        if not (user["password"] == user["confirm_password"]):
            flash("The confirmation password is not valid","register")
            is_valid = False
        return is_valid

    @classmethod
    def verifyDataUserLogin(self,user):
        is_valid = True
        if not EMAIL_REGEX.match(user["email"]):
            flash("Invalid email address","login")
            is_valid = False
        if not PASSWORD_REGEX.match(user["password"]):
            flash("Invalid credentials","login")
            is_valid = False
        return is_valid