# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 17:44:24 2024

@author: JUAN DAVID
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 15:50:13 2024

@author: juand
"""


# Definir la clase del hilo para la comunicación serial
import math
import funciones as f
import time
import serial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5 import QtWidgets, QtCore
from matplotlib.animation import FuncAnimation
import sys
import numpy as np
from  Gui_scara import Ui_MainWindow
import matplotlib.pyplot as plt


class SerialThread(QtCore.QThread):
    response_received = QtCore.pyqtSignal(str)

    def __init__(self, arduino, datos):
        super().__init__()
        self.arduino = arduino
        self.datos = datos
        self.response_receivedd = False

    def run(self):
        try:
            time.sleep(2)  # Esperar a que se establezca la conexión
            # Convertir los valores a una cadena separada por comas
            datos_str = ','.join(map(str, self.datos)) + '\n'
            # Enviar datos al Arduino
            self.arduino.write(datos_str.encode())
            print(f'Datos enviados: {datos_str.strip()}')
            time.sleep(0.1)
            # Esperar la respuesta del Arduino
            while True:
                if self.arduino.in_waiting > 0:
                    time.sleep(0.1)
                    respuesta = self.arduino.readline().decode().strip()
                    print(f'Respuesta de Arduino: {respuesta}')
                    if respuesta == 'A':
                        print('Confirmación recibida. Proceso completado en Arduino.')
                        self.response_receivedd = True
                        self.response_received.emit(respuesta)
                        break
        except Exception as e:
            print(f'Error al enviar o recibir datos: {str(e)}')
            self.arduino.close()
        finally:

            time.sleep(0.5)


class Miapp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.puerto = 'COM3'  # Reemplaza con el puerto serial donde está conectado tu Arduino
        # # Debe coincidir con la velocidad de comunicación serial en tu código de Arduino
        self.baudios = 115200
        self.q1 = 0  # base
        self.q1ant = 0  # qxant posicion anterior
        self.q2 = 0  # brazo 2
        self.q2ant = 0
        self.q3 = 0  # altura
        self.q3ant = 0
        self.q4 = 0  # rotacion pinza
        self.q4ant = 0
        self.q5 = 0  # accion pinza
        self.ob = 0  # tamaño objeto
        self.home = 0
        self.arduino = serial.Serial(self.puerto, self.baudios)
        self.x = 0
        self.y = 0
        self.z = 0
        
        # graficas de animacion del movimiento
        self.graficarobotdirecta = graficarobot()
        self.graficarobotdirecta_6 = graficarobot()
        self.graficarobotinversa = graficarobot()

        # graficas de posicion en los planos
        self.graficaplanoxy = graficas()
        self.graficaplanoxz = graficas()
        self.graficaplanoyz = graficas()

        # graficas velocidad en los planos
        self.velocidadx = graficas()
        self.velocidady = graficas()
        self.velocidadz = graficas()

        # grafica aceleracion en planos
        self.aceleracionx = graficas()
        self.aceleraciony = graficas()
        self.aceleracionz = graficas()

        # graficas velocidad aceleracion y posicion de articulacion q1
        self.graficaq1 = graficas()
        self.velq1 = graficas()
        self.accq1 = graficas()

        # mismas graficas para seccion de rutinas
        self.graficaq1_6 = graficas()
        self.velq1_6 = graficas()
        self.accq1_6 = graficas()

        # graficas velocidad aceleracion y posicion de articulacion q2
        self.graficaq2 = graficas()
        self.velq2 = graficas()
        self.accq2 = graficas()

        self.graficaq2_6 = graficas()
        self.velq2_6 = graficas()
        self.accq2_6 = graficas()

        # graficas velocidad aceleracion y posicion de articulacion q1
        self.graficaq3 = graficas()
        self.velq3 = graficas()
        self.accq3 = graficas()

        self.graficaq3_6 = graficas()
        self.velq3_6 = graficas()
        self.accq3_6 = graficas()

        # graficas velocidad aceleracion y posicion de articulacion q1
        self.graficaq4 = graficas()
        self.velq4 = graficas()
        self.accq4 = graficas()

        self.graficaq4_6 = graficas()
        self.velq4_6 = graficas()
        self.accq4_6 = graficas()

        # asignacion a espacio en interfaz de las graficas
        self.ui.graficamovimientodirecta.addWidget(self.graficarobotdirecta)
        self.ui.graficamovimientodirecta_6.addWidget(self.graficarobotdirecta_6)
        self.ui.graficamovimientoinversa.addWidget(self.graficarobotinversa)

        self.ui.planoxy.addWidget(self.graficaplanoxy)
        self.ui.planoxz.addWidget(self.graficaplanoxz)
        self.ui.planoyz.addWidget(self.graficaplanoyz)

        self.ui.velocidadX.addWidget(self.velocidadx)
        self.ui.velocidadY.addWidget(self.velocidady)
        self.ui.velocidadZ.addWidget(self.velocidadz)

        self.ui.aceleracionX.addWidget(self.aceleracionx)
        self.ui.aceleracionY.addWidget(self.aceleraciony)
        self.ui.aceleracionZ.addWidget(self.aceleracionz)

        self.ui.planoq1.addWidget(self.graficaq1)
        self.ui.velocidadq1.addWidget(self.velq1)
        self.ui.aceleracionq1.addWidget(self.accq1)

        self.ui.planoq1_6.addWidget(self.graficaq1_6)
        self.ui.velocidadq1_6.addWidget(self.velq1_6)
        self.ui.aceleracionq1_6.addWidget(self.accq1_6)

        self.ui.planoq2.addWidget(self.graficaq2)
        self.ui.velocidadq2.addWidget(self.velq2)
        self.ui.aceleracionq2.addWidget(self.accq2)

        self.ui.planoq2_6.addWidget(self.graficaq2_6)
        self.ui.velocidadq2_6.addWidget(self.velq2_6)
        self.ui.aceleracionq2_6.addWidget(self.accq2_6)

        self.ui.planoq3.addWidget(self.graficaq3)
        self.ui.velocidadq3.addWidget(self.velq3)
        self.ui.aceleracionq3.addWidget(self.accq3)

        self.ui.planoq3_6.addWidget(self.graficaq3_6)
        self.ui.velocidadq3_6.addWidget(self.velq3_6)
        self.ui.aceleracionq3_6.addWidget(self.accq3_6)

        self.ui.planoq4.addWidget(self.graficaq4)
        self.ui.velocidadq4.addWidget(self.velq4)
        self.ui.aceleracionq4.addWidget(self.accq4)

        self.ui.planoq4_6.addWidget(self.graficaq4_6)
        self.ui.velocidadq4_6.addWidget(self.velq4_6)
        self.ui.aceleracionq4_6.addWidget(self.accq4_6)

        # coordenadas cinematica inversa
        self.ui.coordenadaX.textChanged.connect(self.coordenadas)
        self.ui.coordenadaY.textChanged.connect(self.coordenadas)
        self.ui.CoordenadaZ.textChanged.connect(self.coordenadas)

        # coordenadas cinematica directa
        self.ui.coordenadaq1.textChanged.connect(self.coordenadaq1)
        self.ui.coordenadaq2.textChanged.connect(self.coordenadaq2)
        self.ui.Coordenadaq3.textChanged.connect(self.coordenadaq3)
        self.ui.coordenadaq4.textChanged.connect(self.coordenadaq4)

        # Asignacion de botones de interfaz

        # accion de objeto a agarrar
        self.ui.objeto_2.textChanged.connect(self.coordenadaobdir)
        self.ui.objeto.textChanged.connect(self.coordenadaobinv)

        # boton de envio de datos
        self.ui.botonenviar.clicked.connect(self.enviar)
        self.ui.botonenviar_2.clicked.connect(self.enviar_2)

        # boton modo home
        self.ui.botonhome.clicked.connect(self.modohome)
        self.ui.botonhome_2.clicked.connect(self.modohome)
        self.ui.botonhome_7.clicked.connect(self.modohome)

        # accion de agarrar o soltar objeto
        self.ui.botonsoltar_2.clicked.connect(self.coordenadaq5)
        self.ui.botonsoltar.clicked.connect(self.coordenadaq5)

        self.ui.botonagarrar.clicked.connect(self.coordenadaq5_2)
        self.ui.botonagarrar_2.clicked.connect(self.coordenadaq5_2)

        self.ui.botonborrar_2.clicked.connect(self.borrardatos)
        self.ui.botonborrar.clicked.connect(self.borrardatos)

        self.ui.botonrutina1.clicked.connect(self.rutina1)
        self.ui.botonrutina2.clicked.connect(self.rutina2)
        self.ui.botonrutina3.clicked.connect(self.rutina3)

    def closeEvent(self, event):
        #Cierra el puerto serial
        self.arduino.close()
        #Detiene el hilo de comunicación serial
        self.serial_thread.join()
        #Cierra la interfaz gráfica
        event.accept()
        
    def rutina1(self):
        # coordenadas x,y de los objetos
        objetivo_1 = [-115, 125]
        objetivo_2 = [-170, 50]
        objetivo_3 = [120, 125]

        pieza_1 = [90, 140]
        pieza_2 = [-195, -45]
        pieza_3 = [165, 65]
        
        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        # 3.a valores iniciales
        x0 = 0
        y0 = 0
        z0 = 0
        parametros = [float(L0), float(L1), float(L2), float(
            L3), float(L4), float(L5), float(x0), float(y0), float(z0)]

        # ciclo for de ejecucion de la rutina
        for i in range(18):

            # la rutina para cada objeto sigue los siguientes pasos:

            # 1. ubicarse en el plano xy
            # 2. descender y agarrar/soltar la pieza
            # 3. volver a subir el brazo a una altura optima

            # calculos de cinematica inversa de cada posicion a la que debe moverse el brazo

            # rutina pieza 1
            if i == 0:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_1[0], pieza_1[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 2
            elif i == 1:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_1[0], pieza_1[1], 40, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 0
            elif i == 2:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_1[0], pieza_1[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 2
            # rutina cinta roja
            elif i == 3:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_1[0], objetivo_1[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 2
            
            elif i == 4:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_1[0], objetivo_1[1], 50, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 1
            elif i == 5:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_1[0], objetivo_1[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 1
                self.q5 = 2
            # rutina pieza 2
            elif i == 6:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_2[0], pieza_2[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 2            
            elif i == 7:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_2[0], pieza_2[1], 40, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 0
            elif i == 8:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_2[0], pieza_2[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 2
            # rutina cinta verde
            elif i == 9:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_2[0], objetivo_2[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 2
            elif i == 10:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_2[0], objetivo_2[1], 50, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 1
            elif i == 11:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_2[0], objetivo_2[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 2
                self.q5 = 2
            # rutina pieza 3
            elif i == 12:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_3[0], pieza_3[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 3
                self.q5 = 2
            elif i == 13:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_3[0], pieza_3[1], 40, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 3
                self.q5 = 0
            elif i == 14:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, pieza_3[0], pieza_3[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 3
                self.q5 = 2
            # rutina cinta amarilla
            elif i == 15:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_3[0], objetivo_3[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 3
                self.q5 = 2
            
            elif i == 16:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_3[0], objetivo_3[1], 50, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)
                self.ob = 3
                self.q5 = 1
            elif i == 17:
                q1, q2, q3, q4, corr = f.TCI(
                    parametros, objetivo_3[0], objetivo_3[1], 120, 0, self.q1ant, self.q2ant, self.q3ant, self.q4ant)

            # envio de coordenadas a cada grafica a realizarse solo se grafican
            # lo referente a las articulaciones

            self.graficarobotdirecta_6.q1a(q1)
            self.graficaq1_6.q1b(q1)
            self.velq1_6.q1b(q1)
            self.accq1_6.q1b(q1)

            self.graficarobotdirecta_6.q2a(q2)
            self.graficaq2_6.q2b(q2)
            self.velq2_6.q2b(q2)
            self.accq2_6.q2b(q2)

            self.graficarobotdirecta_6.q3a(q3)
            self.graficaq3_6.q3b(q3)
            self.velq3_6.q3b(q3)
            self.accq3_6.q3b(q3)

            self.graficarobotdirecta_6.q4a(q4)
            self.graficaq4_6.q4b(q4)
            self.velq4_6.q4b(q4)
            self.accq4_6.q4b(q4)

            #activacion de funciones de graficacion
            self.graficarobotdirecta_6.grafica_datos()

            self.graficaq1_6.grafica_datos(10)
            self.graficaq2_6.grafica_datos(11)
            self.graficaq3_6.grafica_datos(12)
            self.graficaq4_6.grafica_datos(13)

            self.velq1_6.grafica_datos(14)
            self.velq2_6.grafica_datos(15)
            self.velq3_6.grafica_datos(16)
            self.velq4_6.grafica_datos(17)

            self.accq1_6.grafica_datos(18)
            self.accq2_6.grafica_datos(19)
            self.accq3_6.grafica_datos(20)
            self.accq4_6.grafica_datos(21)

            # forzar aparicion de las graficas en cada iteracion
            QApplication.processEvents()
            time.sleep(0.1)

            # calculo y envio de coordenadas a mover
            self.q1m = q1-self.q1ant
            self.q2m = q2-self.q2ant
            self.q3m = q3-self.q3ant
            self.q4m = q4-self.q4ant
            datos = [self.q1m, self.q2m, self.q3m,
                      self.q4m, self.q5, self.ob, self.home]

            # establecimiento de la comunicacion con el arduino
            self.serial_thread = SerialThread(self.arduino, datos)
            time.sleep(0.1)
            self.serial_thread.start()
            time.sleep(0.1)
            self.serial_thread.wait()  # esperar a recibir una respuesta de arduino "A"
            self.serial_thread.response_received.connect(
                self.proceso_completado)
            
            # actualizacion de variables anteriores para futuros calculos
            self.q1ant = q1
            self.q2ant = q2
            self.q3ant = q3
            self.q4ant = q4
            self.q5 = 2

    def rutina2(self):
        # coordenadas x,y de los objetos
        caja_p1 = [-175,35]
        caja_p2 = [-175,35]
        caja_p3 = [-175,35]
        
        pieza_1 = [-70,130]
        pieza_2 = [70,130]
        pieza_3 = [0,130]
        
        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        #3.a valores iniciales
        x0=0
        y0=0
        z0=0
        parametros = [float(L0), float(L1), float(L2), float(L3), float(L4), float(L5), float(x0), float(y0), float(z0)]
        
        
        for i in range(18):
            
            #rutina pieza 1
            if i == 0:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 1:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 0
            elif i == 2:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 2
            #rutina cinta roja
            elif i == 3:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 2
            elif i == 4:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],100,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 1
            elif i == 5:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 2
            #rutina pieza 2
            elif i == 6:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 2
            elif i == 7:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 0
            elif i == 8:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 2
            #rutina cinta verde
            elif i == 9:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 2
            elif i == 10:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],100,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 1
            elif i == 11:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 2
            #rutina pieza 3
            elif i == 12:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 2
            elif i == 13:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 0
            elif i == 14:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 2
            #rutina cinta amarilla
            elif i == 15:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 2
            elif i == 16:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],100,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 1
            elif i == 17:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                
            self.graficarobotdirecta_6.q1a(q1)
            self.graficaq1_6.q1b(q1)
            self.velq1_6.q1b(q1)
            self.accq1_6.q1b(q1)
            
            self.graficarobotdirecta_6.q2a(q2)
            self.graficaq2_6.q2b(q2)
            self.velq2_6.q2b(q2)
            self.accq2_6.q2b(q2)
            
            self.graficarobotdirecta_6.q3a(q3)
            self.graficaq3_6.q3b(q3)
            self.velq3_6.q3b(q3)
            self.accq3_6.q3b(q3)
            
            self.graficarobotdirecta_6.q4a(q4)
            self.graficaq4_6.q4b(q4)
            self.velq4_6.q4b(q4)
            self.accq4_6.q4b(q4)
            
            self.graficarobotdirecta_6.grafica_datos()
            self.graficaq1_6.grafica_datos(10)
            self.graficaq2_6.grafica_datos(11)
            self.graficaq3_6.grafica_datos(12)
            self.graficaq4_6.grafica_datos(13)

            self.velq1_6.grafica_datos(14)
            self.velq2_6.grafica_datos(15)
            self.velq3_6.grafica_datos(16)
            self.velq4_6.grafica_datos(17)

            self.accq1_6.grafica_datos(18)
            self.accq2_6.grafica_datos(19)
            self.accq3_6.grafica_datos(20)
            self.accq4_6.grafica_datos(21)
            
            QApplication.processEvents()
            time.sleep(0.1)
            
            self.q1m = q1-self.q1ant
            self.q2m = q2-self.q2ant
            self.q3m = q3-self.q3ant
            self.q4m = q4-self.q4ant        
            datos = [self.q1m, self.q2m, self.q3m, self.q4m, self.q5, self.ob, self.home]
            
            self.serial_thread = SerialThread(self.arduino, datos)
            time.sleep(0.1)
            self.serial_thread.start()
            time.sleep(0.1)
            self.serial_thread.wait()  # esperar a recibir una respuesta de arduino "A"
            self.serial_thread.response_received.connect(
                self.proceso_completado)
                   
            self.q1ant = q1
            self.q2ant = q2
            self.q3ant = q3
            self.q4ant = q4
            self.q5 = 2
            
    def rutina3(self):
        # coordenadas x,y de los objetos
        caja_p1 = [0,207]
        caja_p2 = [0,207]
        caja_p3 = [0,207]
        
        pieza_1 = [-200,0]
        pieza_2 = [200,0]
        pieza_3 = [0,135]
        
        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        #3.a valores iniciales
        x0=0
        y0=0
        z0=0
        parametros = [float(L0), float(L1), float(L2), float(L3), float(L4), float(L5), float(x0), float(y0), float(z0)]
        
        
        for i in range(18):
            
            #rutina pieza 1
            if i == 0:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 1:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 0
            elif i == 2:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_1[0],pieza_1[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            #rutina cinta roja
            elif i == 3:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            elif i == 4:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 1
            elif i == 5:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            #rutina pieza 2
            elif i == 6:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            elif i == 7:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 0
            elif i == 8:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            #rutina cinta verde
            elif i == 9:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            elif i == 10:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 1
            elif i == 11:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            #rutina pieza 3
            elif i == 12:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            elif i == 13:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 0
            elif i == 14:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            #rutina cinta amarilla
            elif i == 15:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            elif i == 16:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],80,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 1
            elif i == 17:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                
            self.graficarobotdirecta_6.q1a(q1)
            self.graficaq1_6.q1b(q1)
            self.velq1_6.q1b(q1)
            self.accq1_6.q1b(q1)
            
            self.graficarobotdirecta_6.q2a(q2)
            self.graficaq2_6.q2b(q2)
            self.velq2_6.q2b(q2)
            self.accq2_6.q2b(q2)
            
            self.graficarobotdirecta_6.q3a(q3)
            self.graficaq3_6.q3b(q3)
            self.velq3_6.q3b(q3)
            self.accq3_6.q3b(q3)
            
            self.graficarobotdirecta_6.q4a(q4)
            self.graficaq4_6.q4b(q4)
            self.velq4_6.q4b(q4)
            self.accq4_6.q4b(q4)
            
            self.graficarobotdirecta_6.grafica_datos()   
            self.graficaq1_6.grafica_datos(10)
            self.graficaq2_6.grafica_datos(11)
            self.graficaq3_6.grafica_datos(12)
            self.graficaq4_6.grafica_datos(13)
 
            self.velq1_6.grafica_datos(14)
            self.velq2_6.grafica_datos(15)
            self.velq3_6.grafica_datos(16)
            self.velq4_6.grafica_datos(17)
 
            self.accq1_6.grafica_datos(18)
            self.accq2_6.grafica_datos(19)
            self.accq3_6.grafica_datos(20)
            self.accq4_6.grafica_datos(21)
            
            QApplication.processEvents()
            time.sleep(0.1)
            
            self.q1m = q1-self.q1ant
            self.q2m = q2-self.q2ant
            self.q3m = q3-self.q3ant
            self.q4m = q4-self.q4ant        
            datos = [self.q1m, self.q2m, self.q3m, self.q4m, self.q5, self.ob, self.home]
            
            self.serial_thread = SerialThread(self.arduino, datos)
            self.serial_thread.response_received.connect(self.proceso_completado)
            self.serial_thread.start()
            self.serial_thread.wait()
                   
            self.q1ant = q1
            self.q2ant = q2
            self.q3ant = q3
            self.q4ant = q4
            self.q5 = 2

    def coordenadas(self):
        self.x = float(self.ui.coordenadaX.toPlainText())
        self.y = float(self.ui.coordenadaY.toPlainText())
        self.z = float(self.ui.CoordenadaZ.toPlainText())
        delta_e = 0

        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        # 3.a valores iniciales
        x0 = 0
        y0 = 0
        z0 = 0
        parametros = [float(L0), float(L1), float(L2), float(
            L3), float(L4), float(L5), float(x0), float(y0), float(z0)]

        q1, q2, q3, q4, corr = f.TCI(
            parametros, self.x, self.y, self.z, delta_e, self.q1ant, self.q2ant, self.q3ant, self.q4ant)

        if math.isnan(q1):
            self.q1 = self.q1ant
            self.q2 = self.q2ant
            q1 = self.q1ant
            q2 = self.q2ant
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del espacio de trabajo")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            self.q3 = q3
            self.q4 = q4

        elif math.isnan(q2):

            self.q1 = self.q1ant
            self.q2 = self.q2ant
            q1 = self.q1ant
            q2 = self.q2ant
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del espacio de trabajo")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            self.q3 = q3
            self.q4 = q4

        elif corr == 1:

            self.q1 = self.q1ant
            self.q2 = self.q2ant
            q1 = self.q1ant
            q2 = self.q2ant
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del espacio de trabajo")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            self.q3 = q3
            self.q4 = q4
        else:
            self.q1 = q1
            self.q2 = q2
            self.q3 = q3
            self.q4 = q4

        self.graficarobotinversa.q1a(q1)
        self.graficaplanoxy.q1b(q1)
        self.graficaplanoxz.q1b(q1)
        self.graficaplanoyz.q1b(q1)
        self.velocidadx.q1b(q1)
        self.velocidady.q1b(q1)
        self.velocidadz.q1b(q1)
        self.aceleracionx.q1b(q1)
        self.aceleraciony.q1b(q1)
        self.aceleracionz.q1b(q1)

        self.graficarobotinversa.q2a(q2)
        self.graficaplanoxy.q2b(q2)
        self.graficaplanoxz.q2b(q2)
        self.graficaplanoyz.q2b(q2)
        self.velocidadx.q2b(q2)
        self.velocidady.q2b(q2)
        self.velocidadz.q2b(q2)
        self.aceleracionx.q2b(q2)
        self.aceleraciony.q2b(q2)
        self.aceleracionz.q2b(q2)

        self.graficarobotinversa.q3a(q3)
        self.graficaplanoxy.q3b(q3)
        self.graficaplanoxz.q3b(q3)
        self.graficaplanoyz.q3b(q3)
        self.velocidadx.q3b(q3)
        self.velocidady.q3b(q3)
        self.velocidadz.q2b(q3)
        self.aceleracionx.q3b(q3)
        self.aceleraciony.q3b(q3)
        self.aceleracionz.q3b(q3)

        self.graficarobotinversa.q4a(q4)
        self.graficaplanoxy.q4b(q4)
        self.graficaplanoxz.q4b(q4)
        self.graficaplanoyz.q4b(q4)
        self.velocidadx.q4b(q4)
        self.velocidady.q4b(q4)
        self.velocidadz.q4b(q4)
        self.aceleracionx.q4b(q4)
        self.aceleraciony.q4b(q4)
        self.aceleracionz.q4b(q4)

    def borrardatos(self):
        self.q1 = 0  # base
        self.q2 = 0  # brazo 2
        self.q3 = 0  # altura
        self.q4 = 0  # rotacion pinza
        self.q5 = 0  # accion pinza
        self.ob = 0  # tamaño objeto
        self.home = 0
        self.graficarobotinversa.limpiar()
        self.graficarobotdirecta.limpiar()
        self.graficaplanoxy.limpiar()
        self.graficaplanoxz.limpiar()
        self.graficaplanoyz.limpiar()
        self.velocidadx.limpiar()
        self.velocidady.limpiar()
        self.velocidadz.limpiar()
        self.aceleracionx.limpiar()
        self.aceleraciony.limpiar()
        self.aceleracionz.limpiar()
        self.graficaq1.limpiar()
        self.velq1.limpiar()
        self.accq1.limpiar()
        self.graficaq2.limpiar()
        self.velq2.limpiar()
        self.accq2.limpiar()
        self.graficaq3.limpiar()
        self.velq3.limpiar()
        self.accq3.limpiar()
        self.graficaq4.limpiar()
        self.velq4.limpiar()
        self.accq4.limpiar()

    def coordenadaq1(self):
        # Access the text value directly from the sender (line edit)
        q1_text = float(self.ui.coordenadaq1.toPlainText())
        self.q1 = q1_text

        if abs(self.q1) > abs(130):
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            self.graficarobotdirecta.q1a(q1_text)
            self.graficarobotinversa.q1a(q1_text)
            self.graficaplanoxy.q1b(q1_text)
            self.graficaplanoxz.q1b(q1_text)
            self.graficaplanoyz.q1b(q1_text)
            self.velocidadx.q1b(q1_text)
            self.velocidady.q1b(q1_text)
            self.velocidadz.q1b(q1_text)
            self.aceleracionx.q1b(q1_text)
            self.aceleraciony.q1b(q1_text)
            self.aceleracionz.q1b(q1_text)
            self.graficaq1.q1b(q1_text)
            self.velq1.q1b(q1_text)
            self.accq1.q1b(q1_text)

    def coordenadaq2(self):
        q2_text = float(self.ui.coordenadaq2.toPlainText())
        self.q2 = q2_text

        if abs(self.q2) > abs(130):
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            self.graficarobotdirecta.q2a(q2_text)
            self.graficarobotinversa.q2a(q2_text)
            self.graficaplanoxy.q2b(q2_text)
            self.graficaplanoxz.q2b(q2_text)
            self.graficaplanoyz.q2b(q2_text)
            self.velocidadx.q2b(q2_text)
            self.velocidady.q2b(q2_text)
            self.velocidadz.q2b(q2_text)
            self.aceleracionx.q2b(q2_text)
            self.aceleraciony.q2b(q2_text)
            self.aceleracionz.q2b(q2_text)
            self.graficaq2.q2b(q2_text)
            self.velq2.q2b(q2_text)
            self.accq2.q2b(q2_text)

    def coordenadaq3(self):
        q3_text = float(self.ui.Coordenadaq3.toPlainText())
        self.q3 = q3_text

        if abs(self.q3) > abs(100):
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            self.graficarobotdirecta.q3a(q3_text)
            self.graficarobotinversa.q3a(q3_text)
            self.graficaplanoxy.q3b(q3_text)
            self.graficaplanoxz.q3b(q3_text)
            self.graficaplanoyz.q3b(q3_text)
            self.velocidadx.q3b(q3_text)
            self.velocidady.q3b(q3_text)
            self.velocidadz.q3b(q3_text)
            self.aceleracionx.q3b(q3_text)
            self.aceleraciony.q3b(q3_text)
            self.aceleracionz.q3b(q3_text)
            self.graficaq3.q3b(q3_text)
            self.velq3.q3b(q3_text)
            self.accq3.q3b(q3_text)

    def coordenadaq4(self):
        q4_text = float(self.ui.coordenadaq4.toPlainText())
        self.q4 = q4_text

        if self.q4 > 270:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif self.q4 < 0:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        else:
            self.graficarobotdirecta.q4a(q4_text)
            self.graficarobotinversa.q4a(q4_text)
            self.graficaplanoxy.q4b(q4_text)
            self.graficaplanoxz.q4b(q4_text)
            self.graficaplanoyz.q4b(q4_text)
            self.velocidadx.q4b(q4_text)
            self.velocidady.q4b(q4_text)
            self.velocidadz.q4b(q4_text)
            self.aceleracionx.q4b(q4_text)
            self.aceleraciony.q4b(q4_text)
            self.aceleracionz.q4b(q4_text)
            self.graficaq4.q4b(q4_text)
            self.velq4.q4b(q4_text)
            self.accq4.q4b(q4_text)

    def coordenadaobdir(self):
        ob_text = float(self.ui.objeto_2.toPlainText())
        self.ob = ob_text
        if self.ob > 3:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("Numero incorrecto de pieza")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif self.ob < 0:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("Numero incorrecto de pieza")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def coordenadaobinv(self):
        ob_text = float(self.ui.objeto.toPlainText())
        self.ob = ob_text
        if self.ob > 3:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("Numero incorrecto de pieza")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        elif self.ob < 0:
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("Numero incorrecto de pieza")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def coordenadaq5(self):
        self.q5 = 1

    def coordenadaq5_2(self):
        self.q5 = 0

    def modohome(self):
        self.home = 1
        self.q1 = 0  # base
        self.q1ant = 0
        self.q2 = 0  # brazo 2
        self.q2ant = 0
        self.q3 = 0  # altura
        self.q3ant = 0
        self.q4 = 0  # rotacion pinza
        self.q4ant = 0
        self.q5 = 0  # accion pinza
        self.ob = 0  # tamaño objeto
        self.enviar_2()

    def enviar(self):
        self.graficarobotinversa.grafica_datos()
        self.q1m = self.q1-self.q1ant
        self.q2m = self.q2-self.q2ant
        self.q3m = self.q3-self.q3ant
        self.q4m = self.q4-self.q4ant
        datos = [self.q1m, self.q2m, self.q3m,
                 self.q4m, self.q5, self.ob, self.home]
        self.serial_thread = SerialThread(self.arduino, datos)
        self.ok = 1

        self.graficaplanoxy.grafica_datos(1)
        self.graficaplanoxz.grafica_datos(2)
        self.graficaplanoyz.grafica_datos(3)

        self.velocidadx.grafica_datos(4)
        self.velocidady.grafica_datos(5)
        self.velocidadz.grafica_datos(6)

        self.aceleracionx.grafica_datos(7)
        self.aceleraciony.grafica_datos(8)
        self.aceleracionz.grafica_datos(9)

        self.serial_thread.response_received.connect(self.proceso_completado)
        self.serial_thread.start()

        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
        self.q5 = 2

    def enviar_2(self):
        self.graficarobotdirecta.grafica_datos()
        self.q1m = self.q1-self.q1ant
        self.q2m = self.q2-self.q2ant
        self.q3m = self.q3-self.q3ant
        self.q4m = self.q4-self.q4ant
        datos = [self.q1m, self.q2m, self.q3m,
                 self.q4m, self.q5, self.ob, self.home]
        self.serial_thread = SerialThread(self.arduino, datos)
        self.ok = 1

        self.graficaq1.grafica_datos(10)
        self.graficaq2.grafica_datos(11)
        self.graficaq3.grafica_datos(12)
        self.graficaq4.grafica_datos(13)

        self.velq1.grafica_datos(14)
        self.velq2.grafica_datos(15)
        self.velq3.grafica_datos(16)
        self.velq4.grafica_datos(17)

        self.accq1.grafica_datos(18)
        self.accq2.grafica_datos(19)
        self.accq3.grafica_datos(20)
        self.accq4.grafica_datos(21)

        self.serial_thread.response_received.connect(self.proceso_completado)
        self.serial_thread.start()
        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
        self.q5 = 2

    def proceso_completado(self):
        # Manejar la señal de respuesta recibida del hilo
        # Aquí puedes actualizar la interfaz gráfica o realizar otras acciones necesarias
        print('Proceso completado en la interfaz.')
        self.home = 0
        self.ok = 0


class graficarobot(FigureCanvas):

    # creacion de figura de grafica
    def __init__(self, parent=None):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        super().__init__(self.fig)
        self.ax.grid()

        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0
        self.q1ant = 0
        self.q2ant = 0
        self.q3ant = 0
        self.q4ant = 0

    def q1a(self, q1):
        self.q1 = q1

    def q2a(self, q2):
        self.q2 = q2

    def q3a(self, q3):
        self.q3 = q3

    def q4a(self, q4):
        self.q4 = q4

    def limpiar(self):
        self.ax.clear()

    def grafica_datos(self):
        # 1.Dimensiones del robot
        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        # 3.a valores iniciales
        x0 = 0
        y0 = 0
        z0 = 0
        parametros = [float(L0), float(L1), float(L2), float(
            L3), float(L4), float(L5), float(x0), float(y0), float(z0)]

        n_frames = 300

        self.q1v, v1, a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
        self.q2v, v2, a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
        self.q3v, v3, a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
        self.q4v, v4, a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

        def actualizar(i):
            self.ax.clear()
            
            self.ax.set_zlabel("Z")
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(-250, 250)
            self.ax.set_zlim(0, 400)
            f.dibrobot(
                parametros, self.q1v[i], self.q2v[i], self.q3v[i], self.q4v[i], self.ax)

        self.ani = FuncAnimation(self.fig, actualizar, range(
            n_frames), interval=3, repeat=False)
        self.draw()

        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
        plt.close(self.fig)

class graficas(FigureCanvas):

    # creacion de figura de grafica
    def __init__(self, parent=None):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        plt.grid(True)

        self.q1 = 0
        self.q2 = 0
        self.q3 = 0
        self.q4 = 0
        self.q1ant = 0
        self.q2ant = 0
        self.q3ant = 0
        self.q4ant = 0

    def q1b(self, q1):
        self.q1 = q1

    def q2b(self, q2):
        self.q2 = q2

    def q3b(self, q3):
        self.q3 = q3

    def q4b(self, q4):
        self.q4 = q4

    def limpiar(self):
        self.ax.clear()

    def grafica_datos(self, graf):
        # 1.Dimensiones del robot
        L0 = 145
        L1 = 277
        L2 = 123
        L3 = 72
        L4 = 84
        L5 = 111

        # 3.a valores iniciales
        x0 = 0
        y0 = 0
        z0 = 0
        parametros = [float(L0), float(L1), float(L2), float(
            L3), float(L4), float(L5), float(x0), float(y0), float(z0)]
        n_frames = 100
        t0 = 0
        t1 = 1
        

        q1v, v1, a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
        q2v, v2, a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
        q3v, v3, a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
        q4v, v4, a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)
        #print(len(q1v))
        t = np.linspace(t0, t1, len(q1v))
        xe = np.linspace(0, 0, len(q1v))
        ye = np.linspace(0, 0, len(q1v))
        ze = np.linspace(0, 0, len(q1v))


        for i in range(len(q1v)):
            xe[i], ye[i], ze[i] = f.TCD(
                parametros, q1v[i], q2v[i], q3v[i], q4v[i])

        if graf == 1:
            self.ax.set_title("PLANO XY")
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Y")
            self.ax.plot(xe, ye)
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(-250, 250)

        elif graf == 2:
            self.ax.set_title("PLANO XZ")
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Z")
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(0, 200)
            self.ax.plot(xe, ze)

        elif graf == 3:
            self.ax.set_title("PLANO YZ")
            self.ax.set_xlabel("Y")
            self.ax.set_ylabel("Z")
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(0, 200)
            self.ax.plot(ye, ze)

        elif graf == 4:
            self.ax.set_title("VELOCIDAD X")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("X'")
            velx = np.gradient(xe, t)
            self.ax.plot(t, velx)

        elif graf == 5:
            self.ax.set_title("VELOCIDAD Y")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("Y'")
            vely = np.gradient(ye, t)
            self.ax.plot(t, vely)

        elif graf == 6:
            self.ax.set_title("VELOCIDAD Z")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("Z'")
            velz = np.gradient(ze, t)
            self.ax.plot(t, velz)

        elif graf == 7:

            self.ax.set_title("ACELERACIÓN X")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("X''")
            velx = np.gradient(xe, t)
            acelx = np.gradient(velx, t)
            self.ax.plot(t, acelx)

        elif graf == 8:
            self.ax.set_title("ACELERACIÓN Y")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("Y''")
            vely = np.gradient(ye, t)
            acely = np.gradient(vely, t)
            self.ax.plot(t, acely)

        elif graf == 9:
            self.ax.set_title("ACELERACIÓN Z")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("Z''")
            velz = np.gradient(ze, t)
            acelz = np.gradient(velz, t)
            self.ax.plot(t, acelz)

        elif graf == 10:
            self.ax.set_title("POSICIÓN q1")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q1")
            self.ax.set_ylim(-140, 140)
            self.ax.plot(t, q1v)

        elif graf == 11:
            self.ax.set_title("POSICIÓN q2")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q2")
            self.ax.set_ylim(-140, 140)
            self.ax.plot(t, q2v)

        elif graf == 12:
            self.ax.set_title("POSICIÓN q3")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q3")
            self.ax.set_ylim(-140, 140)
            self.ax.plot(t, q3v)

        elif graf == 13:
            self.ax.set_title("POSICIÓN q4")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q4")
            self.ax.set_ylim(-140, 140)
            self.ax.plot(t, q4v)

        elif graf == 14:
            self.ax.set_title("VELOCIDAD q1")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q1'")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, v1)

        elif graf == 15:
            self.ax.set_title("VELOCIDAD q2")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q2'")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, v2)

        elif graf == 16:
            self.ax.set_title("VELOCIDAD q3")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q3'")
            self.ax.set_ylim(-18, 18)
            self.ax.plot(t, v3)

        elif graf == 17:
            self.ax.set_title("VELOCIDAD q4")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q4'")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, v4)

        elif graf == 18:
            self.ax.set_title("ACELERACIÓN q1")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q1''")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, a1)

        elif graf == 19:
            self.ax.set_title("ACELERACIÓN q2")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q2''")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, a2)

        elif graf == 20:
            self.ax.set_title("ACELERACIÓN q3")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q3''")
            self.ax.set_ylim(-7, 7)
            self.ax.plot(t, a3)

        elif graf == 21:
            
            self.ax.set_title("ACELERACIÓN q4")
            self.ax.set_xlabel("t")
            self.ax.set_ylabel("q4''")
            self.ax.set_ylim(-0.5, 0.5)
            self.ax.plot(t, a4)

        self.draw()
        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
        plt.close(self.fig)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mi_app = Miapp()
    mi_app.show()
    sys.exit(app.exec_())
