from flask import Flask, render_template, jsonify, abort, redirect, request, url_for
from flask_mysqldb import MySQL
import os
import geocoder

app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'usuarios'
mysql = MySQL(app)

@app.route('/crear',methods=['POST'])
def crear():
    data = request.get_json()
    if data['nombre'] is None or data['apellido'] is None or data['direccion'] is None or data['ciudad'] is None:
        return  abort(400)
    nombre = data['nombre']
    apellido = data['apellido']
    direccion = data['direccion']
    ciudad = data['ciudad']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO `usuarios` (`nombre`, `apellido`, `direccion`, `ciudad`) VALUES ('"+nombre+"', '"+apellido+"', '"+direccion+"', '"+ciudad+"')")
    mysql.connection.commit()
    respuesta = {
        "error": False,
        "code": 200,
        "usuario": data
    }
    return jsonify(respuesta)

@app.route("/lista",methods=['GET'])
def lista():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `usuarios`")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    respuesta = {
        "error": False,
        "code": 200,
        "usuarios": json_data
    }
    return jsonify(respuesta)

@app.route("/usuario",methods=['GET'])
def usuario():
    data = request.get_json()
    idusuario = data['id'] 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `usuarios` WHERE (`id` = '"+idusuario+"')")
    row_headers=[x[0] for x in cur.description]    
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    respuesta = {
        "error": False,
        "code": 200,
        "usuario": json_data
    }
    return jsonify(respuesta)

@app.route('/eliminar/<idusuario>',methods=['DELETE'])
def eliminar(idusuario):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = '"+idusuario+"'")
    mysql.connection.commit()
    respuesta = {
        "error": False,
        "code": 200,
        "respuesta": "usuario con el id "+idusuario+" eliminado"
    }
    return jsonify(respuesta)

@app.route("/geocodificar_base",methods=['GET'])
def geocodificar_base():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios where longitud is NULL and latitud is NULL;")
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    os.environ["GOOGLE_API_KEY"] = "AIzaSyAYVHSbEo-Rh1qBeOOk_BKiXns7bzVniyQ"
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
        direccion = result[3]
        ciudad = result[4]
        idusuario = result[0]
        geo = geocoder.google('{} , {}'.format(direccion, ciudad),key='AIzaSyAYVHSbEo-Rh1qBeOOk_BKiXns7bzVniyQ')
        if(geo.latlng is "ZERO_RESULTS"):
            geo.latlng[0]= 0
            geo.latlng[1]= 0
            cur.execute("UPDATE usuarios SET `longitud` = '"+str(geo.latlng[0])+"', `latitud` = '"+str(geo.latlng[1])+"' WHERE (`id` = '"+str(idusuario)+"')") 
        else:
            cur.execute("UPDATE usuarios SET `longitud` = '"+str(geo.latlng[0])+"', `latitud` = '"+str(geo.latlng[1])+"' WHERE (`id` = '"+str(idusuario)+"')")
        mysql.connection.commit()

    respuesta = {
        "error": False,
        "code": 200,
        "respuesta": "ok"
    }
    return jsonify(respuesta)


if __name__ == '__main__':
    app.run(debug=True)

