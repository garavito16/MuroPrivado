
from muro.config.mysqlconnection import connectToMySQL
from flask import flash
import re

MENSAJE_REGEX = re.compile(r'^^(.){5,2000}$')


class Mensaje:
    name_db = "muro_privado"

    def __init__(self, id, contenido, usuario_emisor_id, usuario_emisor, usuario_receptor_id, usuario_receptor, created_at):
        self.id = id
        self.contenido = contenido
        self.usuario_emisor_id = usuario_emisor_id
        self.usuario_emisor = usuario_emisor
        self.usuario_receptor_id = usuario_receptor_id
        self.usuario_receptor = usuario_receptor
        self.created_at = created_at

    @classmethod
    def sendMessage(cls,data):
        query = '''
                    INSERT INTO mensaje (contenido, user_emisor_id, user_receptor_id, created_at)
                    VALUES (%(contenido)s, %(usuario_emisor_id)s, %(usuario_receptor_id)s, now())
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,data)
        return resultado
    
    @classmethod
    def verifyDataMenssage(cls,data):
        is_valid = True
        if not MENSAJE_REGEX.match(data["contenido"]):
            flash("Message content must contain at least 5 characters","message")
            is_valid = False
        return is_valid

    @classmethod
    def deleteMessage(cls,data):
        query = '''
                    DELETE FROM mensaje WHERE id = %(id)s
                '''
        resultado = connectToMySQL(cls.name_db).query_db(query,data)
        return resultado