import datetime
import os
import sqlite3
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QMainWindow
from PyQt5.QtGui import QPixmap

#los archivos de QT Designer deben estar en el mismo directorio que el presente archivo de tipo .py

id_sesion_activa = 0
nombre_cat_resena = list()
id_resena_especifica = list()

#Creacion de la base
if os.path.exists("Aplicacion_reseñas.db"):
    print("\nSe ha encontrado la base de datos en el directorio.\n")
else:
    print("No se ha encontrado una base de datos previa, se procede a crearla.\n")
    try:
        with sqlite3.connect("Aplicacion_reseñas.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""CREATE TABLE IF NOT EXISTS usuario(id_usuario INTEGER PRIMARY KEY autoincrement, 
                                nombre TEXT NOT NULL, 
                                apellido TEXT NOT NULL,
                                genero TEXT NOT NULL,
                                pais TEXT NOT NULL,
                                fecha_nacimiento TEXT NOT NULL,
                                correo TEXT NOT NULL, 
                                contraseña TEXT NOT NULL);""")
            
            mi_cursor.execute("""CREATE TABLE IF NOT EXISTS catalogo(id_catalogo INTEGER PRIMARY KEY autoincrement, 
                                nombre TEXT NOT NULL, 
                                tipo TEXT NOT NULL,
                                genero TEXT NOT NULL);""")
            
            mi_cursor.execute("""CREATE TABLE IF NOT EXISTS reseña(id_reseña INTEGER PRIMARY KEY autoincrement,
                                usuario INTEGER NOT NULL,
                                fecha_reseña timestamp, 
                                comentario TEXT NOT NULL,
                                catalogo INTEGER NOT NULL,
                                calificacion INTEGER NOT NULL, 
                                FOREIGN KEY (usuario) REFERENCES usuario(id_usuario), 
                                FOREIGN KEY(catalogo) REFERENCES catalogo(id_catalogo));""")
            
            print("Tablas creadas")
    except sqlite3.Error as e:
        print(e)
    except:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

#Pantalla de bienvenida
class Bienvenida(QDialog): #una clase que contiene la pantalla de bienvenida desde QT Designer
    def __init__(self):
        super(Bienvenida, self).__init__()
        loadUi("Welcome screen nueva.ui", self) #carga el archivo .ui correspondiente a la interfaz
        #breaking_bad = QPixmap("breaking bad poster.jpg")
        #self.label_9.setPixmap(breaking_bad)
        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

    def gotologin(self):
        ir_login = InicioSesion()
        widget.addWidget(ir_login)
        widget.setCurrentIndex(widget.currentIndex()+1) #para añadir la pantalla de inicio de sesión a los widgets

    def gotocreate(self):
        create = CrearCuenta()
        widget.addWidget(create)
        widget.setCurrentIndex(widget.currentIndex()+1)

#Pantalla de inicio de sesión
class InicioSesion(QMainWindow):
    def __init__(self):
        super(InicioSesion, self).__init__()
        loadUi("inicio_sesion.ui", self)
        self.campopassword.setEchoMode(QtWidgets.QLineEdit.Password) #para ocultar las letras ingresadas desde teclado
        self.login.clicked.connect(self.loginfunction)
        self.atras_inicio_sesion.clicked.connect(self.gotowelcome)
        

    def loginfunction(self):
        user = self.campousername.text()
        password = self.campopassword.text()

        if len(user)==0 or len(password)==0:
            self.error.setText("Por favor ingresa todos los campos.") #por si los campos de usuario y contraseña están vacíos
        else:
            try: 
                with sqlite3.connect("Aplicacion_reseñas.db") as conexion:
                    mi_cursor = conexion.cursor()
                    mi_cursor.execute("SELECT nombre, contraseña FROM usuario;")
                    usuarios_registrados = mi_cursor.fetchall()
            except sqlite3.Error as e:
                print(e)
            except:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            for usuario, contraseña in usuarios_registrados:
                if user == usuario:
                    if password == contraseña:
                        id_sesion_activa = usuario
                        self.go_to_catalog()
                        break
                    else:
                        self.error.setText("Contraseña incorrecta.")
                        break
            else:
                self.error.setText("Usuario no encontrado.")
        
    def go_to_catalog(self):
        catalogo = MostrarCatalogo()
        widget.addWidget(catalogo)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotowelcome(self):
        welcome = Bienvenida()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)


#Pantalla de crear cuenta
class CrearCuenta(QMainWindow):
    def __init__(self):
        super(CrearCuenta, self).__init__()
        loadUi("agregar_usuario.ui", self)
        self.campopassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.campopassword2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.create.clicked.connect(self.signupfunction)
        self.salir_crear_cuenta.clicked.connect(self.gotowelcome)

    def signupfunction(self):
        names = self.camponombres.text()
        lastnames = self.campoapellidos.text()
        gender = self.campogenero.text()
        country = self.campopais.text()
        nacimiento = self.camponacimiento.text()
        email = self.campocorreo.text()
        password = self.campopassword.text()
        confirmpassword = self.campopassword2.text()

        if len(gender)==0 or len(names)==0 or len(lastnames)==0 or len(country)==0 or len(email)==0 or len(password)==0 or len(confirmpassword)==0:
            self.error.setText("Por favor ingresa todos los campos.")
        elif password!=confirmpassword:
            self.error.setText("Las contraseñas no coinciden.")
        else:
            self.error.setText("")
            try: 
                with sqlite3.connect("Aplicacion_reseñas.db") as conexion:
                    mi_cursor = conexion.cursor()
                    dict_usuario_nuevo = {"nombre": names, "apellido": lastnames, "genero": gender, "pais": country, "fecha_nacimiento":nacimiento,"correo": email, "contraseña": confirmpassword}
                    mi_cursor.execute("INSERT INTO usuario (nombre, apellido, genero, pais, fecha_nacimiento, correo, contraseña) VALUES (:nombre, :apellido, :genero, :pais, :fecha_nacimiento,:correo, :contraseña);", dict_usuario_nuevo)
            except sqlite3.Error as e:
                print(e)
            except:
                print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            self.confirmacion.setText("Usuario creado.")

    def gotowelcome(self):
        welcome = Bienvenida()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)

#Pantalla de catálogo
class MostrarCatalogo(QMainWindow):
    def __init__(self):
        super(MostrarCatalogo, self).__init__()
        loadUi("catalogo_mejorado.ui", self)
        self.cargar_datos_catalogo()
        self.agregar_catalogo.clicked.connect(self.go_to_add_catalog)
        self.buscar_id.clicked.connect(self.resenas_consultas)
        self.salir_catalogo.clicked.connect(self.gotowelcome)

    def cargar_datos_catalogo(self):
        try: 
            with sqlite3.connect("Aplicacion_reseñas.db") as conexion:
                mi_cursor = conexion.cursor()
                mi_cursor.execute("SELECT * FROM catalogo;")
                datos_catalogo = mi_cursor.fetchall()
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        row=0
        self.muestra_datos.setRowCount(len(datos_catalogo))
        for elemento in datos_catalogo:
            self.muestra_datos.setItem(row,0, QtWidgets.QTableWidgetItem(elemento[0])) #ID
            self.muestra_datos.setItem(row,1, QtWidgets.QTableWidgetItem(elemento[1])) #Nombre
            self.muestra_datos.setItem(row,2, QtWidgets.QTableWidgetItem(elemento[2])) #Tipo
            self.muestra_datos.setItem(row,3, QtWidgets.QTableWidgetItem(elemento[3])) #Genero
            row=row+1
        
    def resenas_consultas(self):
        id_a_consultar = self.texto_id_deseado.text()
        try: 
            with sqlite3.connect("Aplicacion_reseñas.db") as conexion:
                mi_cursor = conexion.cursor()
                tupla_id_consultar = (int(id_a_consultar), )
                mi_cursor.execute("SELECT nombre FROM catalogo WHERE id_catalogo = ?;", tupla_id_consultar)
                nombre_resultado = mi_cursor.fetchall()
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        for name in nombre_resultado[0]:
            nombre_cat_resultado = name
        try: 
            with sqlite3.connect("Aplicacion_reseñas.db") as conexion:
                mi_cursor = conexion.cursor()
                tupla_cat_consultado = (nombre_cat_resultado, )
                mi_cursor.execute("SELECT id_reseña, fecha_reseña, comentario, catalogo, calificacion FROM reseña WHERE catalogo = ?;", tupla_cat_consultado)
                resenas_resultado = mi_cursor.fetchall()
                if resenas_resultado:
                    row=0
                    self.muestra_comentarios.setRowCount(len(resenas_resultado))
                    for comment in resenas_resultado:
                        self.muestra_comentarios.setItem(row,0, QtWidgets.QTableWidgetItem(comment[0])) #ID
                        self.muestra_comentarios.setItem(row,1, QtWidgets.QTableWidgetItem(comment[1])) #Fecha
                        self.muestra_comentarios.setItem(row,2, QtWidgets.QTableWidgetItem(comment[2])) #Comentario
                        self.muestra_comentarios.setItem(row,3, QtWidgets.QTableWidgetItem(comment[4])) #Calificación
                        row=row+1
                        nombre_cat_resena.append(comment[3])
                    self.agregar_resena.clicked.connect(self.go_to_add_resena)
                    self.editar_resena.clicked.connect(self.go_to_edit_resena)
                else:
                    self.error.setText("No hay reseñas para ese elemento.")
                    self.agregar_resena.clicked.connect(self.go_to_add_resena)
                    self.editar_resena.clicked.connect(self.go_to_edit_resena)
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")


    def go_to_add_catalog(self):
        agregar_catalogo_screen = Agregar_catalogo_pantalla()
        widget.addWidget(agregar_catalogo_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_add_resena(self):
        agregar_resena_screen = Agregar_resena_pantalla()
        widget.addWidget(agregar_resena_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotowelcome(self):
        welcome = Bienvenida()
        widget.addWidget(welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def go_to_edit_resena(self):
        edit_resena_screen = Editar_resena_pantalla()
        widget.addWidget(edit_resena_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)

#Pantalla de agregar a catalogo
class Agregar_catalogo_pantalla(QMainWindow):
    def __init__(self):
        super(Agregar_catalogo_pantalla, self).__init__()
        loadUi("Agregar_catalogo.ui", self)
        self.registrar_alcatalogo.clicked.connect(self.agregar_peli_serie)
        self.salir_add_catalogo.clicked.connect(self.go_to_catalogo)

    def agregar_peli_serie(self):
        nombre_peli_serie = self.texto_pelicula_serie.text()
        genero_peli_serie = self.texto_genero.text()
        tipo_peli_serie = self.texto_tipo.text()
        try:
            with sqlite3.connect("Aplicacion_reseñas.db") as conn:
                mi_cursor = conn.cursor()
                agregar_catalogo = (nombre_peli_serie, tipo_peli_serie, genero_peli_serie)
                mi_cursor.execute("INSERT INTO catalogo(nombre, tipo, genero) VALUES(?,?,?)", agregar_catalogo)
                self.confirmacion.setText("Agregado al catalogo.")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

    def go_to_catalogo(self):
        catalogo_screen = MostrarCatalogo()
        widget.addWidget(catalogo_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)

#Pantalla de agregar reseña
class Agregar_resena_pantalla(QMainWindow):
    def __init__(self):
        super(Agregar_resena_pantalla, self).__init__()
        loadUi("agregar_reseña.ui", self)
        self.boton_agregar_resena.clicked.connect(self.agregar_resena)
        self.salir_resena.clicked.connect(self.go_to_catalogo)
    
    def agregar_resena(self):
        nombre_reseña = self.texto_nombre_pelicula.text()
        calif_reseña = self.texto_calificacion.text()
        comentario = self.texto_comentario.text()
        try:
            with sqlite3.connect("Aplicacion_reseñas.db") as conn:
                mi_cursor = conn.cursor()
                insert_reseña= (id_sesion_activa, (datetime.datetime.now()), comentario, nombre_reseña, int(calif_reseña))
                mi_cursor.execute("INSERT INTO reseña(usuario, fecha_reseña, comentario, catalogo, calificacion) VALUES(?,?,?,?,?)", insert_reseña)
                self.confirmacion.setText("Reseña agregada.")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")

    def go_to_catalogo(self):
        catalogo_screen = MostrarCatalogo()
        widget.addWidget(catalogo_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)

#Pantalla de editar reseña
class Editar_resena_pantalla(QMainWindow):
    def __init__(self):
        super(Editar_resena_pantalla, self).__init__()
        loadUi("Eliminar_actualizar_reseña.ui", self)
        self.actualizar.clicked.connect(self.actualizar_resena)
        self.eliminar.clicked.connect(self.eliminar_resena)
        self.salir_eliminar_resena.clicked.connect(self.go_to_catalogo)

        try:
            with sqlite3.connect("Aplicacion_reseñas.db") as conn:
                mi_cursor = conn.cursor()
                nombre_cat = nombre_cat_resena[0]
                tupla_resena_especifica = (id_sesion_activa, nombre_cat)
                mi_cursor.execute("SELECT id_reseña, catalogo, comentario FROM reseña WHERE usuario = ? AND catalogo = ?", tupla_resena_especifica)
                resena_especifica = mi_cursor.fetchall()
                for review in resena_especifica:
                    self.nombre_en_catalogo.setText(review[1])
                    self.comentario_actual.setText(review[2])
                    id_resena_especifica.append(review[0])
                self.confirmacion.setText("Cambia o elimina el comentario.")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")   

    def actualizar_resena(self):
        comment_actualizado = self.comentario_editado.text()
        try:
            with sqlite3.connect("Aplicacion_reseñas.db") as conn:
                mi_cursor = conn.cursor()
                tupla_resena_actualizada = (comment_actualizado, id_resena_especifica[0])
                mi_cursor.execute("UPDATE reseña SET comentario = ? WHERE id_reseña = ?", tupla_resena_actualizada)
                self.confirmacion.setText("Reseña actualizada.")
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")    
        
    def eliminar_resena(self):
        try:
            with sqlite3.connect("Aplicacion_reseñas.db") as conn:
                mi_cursor = conn.cursor()
                tupla_reseña_eliminar = (self.resena_especifica[0])
                mi_cursor.execute("DELETE FROM reseña WHERE id_reseña = ?",  tupla_reseña_eliminar)    
        except sqlite3.Error as e:
            print(e)
        except:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        self.texto_nombre_catalogo.setText("")
        self.comentario_editado.setText("")
        self.confirmacion.setText("Reseña eliminada.")

    def go_to_catalogo(self):
        catalogo_screen = MostrarCatalogo()
        widget.addWidget(catalogo_screen)
        widget.setCurrentIndex(widget.currentIndex()+1)


#Ejecución del programa
app = QApplication(sys.argv) #la aplicación que realmente ejecuta la interfaz
pantalla_bienvenida = Bienvenida()
widget = QtWidgets.QStackedWidget() #para apilar las pantallas creadas para cada opción de la interfaz
widget.addWidget(pantalla_bienvenida)
widget.setFixedHeight(550)
widget.setFixedWidth(900)
widget.show()
try:
    sys.exit(app.exec_()) #para ejecutar la aplicación
except:
    print("Saliendo del programa.")