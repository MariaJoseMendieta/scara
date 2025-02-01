# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 15:50:13 2024

@author: juand
"""
import sys
import numpy as np
from  Gui_scara import *
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import serial
import time
import funciones as f
import math



# Definir la clase del hilo para la comunicación serial
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
        self.baudios = 115200 # Debe coincidir con la velocidad de comunicación serial en tu código de Arduino
        self.q1 = 0 #base
        self.q1ant = 0
        self.q2 = 0 #brazo 2
        self.q2ant = 0
        self.q3 = 0 #altura
        self.q3ant = 0
        self.q4 = 0 #rotacion pinza
        self.q4ant = 0
        self.q5 = 0 #accion pinza
        self.ob = 0 #tamaño objeto
        self.home = 0 
        self.arduino = serial.Serial(self.puerto,self.baudios)
        self.x = 0
        self.y = 0
        self.z = 0
        self.ok = 0
        
        
        self.graficarobotdirecta = graficarobot()
        self.graficarobotdirecta_6 = graficarobot()
        self.graficarobotinversa = graficarobot_2()
        
        self.graficaplanoxy = graficaplanoxy()
        self.graficaplanoxz = graficaplanoxz()
        self.graficaplanoyz = graficaplanoyz()
        
        self.velocidadx = graficavelx()
        self.velocidady = graficavely()
        self.velocidadz = graficavelz()
        
        self.aceleracionx = graficaaccx()
        self.aceleraciony = graficaaccy()
        self.aceleracionz = graficaaccz()
            
        self.graficaq1 = graficaq1()
        self.velq1 = graficavelq1() 
        self.accq1 = graficaaccq1()
        
        self.graficaq1_6 = graficaq1()
        self.velq1_6 = graficavelq1() 
        self.accq1_6 = graficaaccq1()
                
        self.graficaq2 = graficaq2()
        self.velq2 = graficavelq2() 
        self.accq2 = graficaaccq2()
        
        self.graficaq2_6 = graficaq2()
        self.velq2_6 = graficavelq2() 
        self.accq2_6 = graficaaccq2()
        
        self.graficaq3 = graficaq3()
        self.velq3 = graficavelq3() 
        self.accq3 = graficaaccq3()
        
        self.graficaq3_6= graficaq3()
        self.velq3_6 = graficavelq3() 
        self.accq3_6 = graficaaccq3()
        
        self.graficaq4 = graficaq4()
        self.velq4 = graficavelq4() 
        self.accq4 = graficaaccq4()
        
        self.graficaq4_6 = graficaq4()
        self.velq4_6 = graficavelq4() 
        self.accq4_6 = graficaaccq4()
        
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
        
        self.ui.coordenadaX.textChanged.connect(self.coordenadas)
        self.ui.coordenadaY.textChanged.connect(self.coordenadas)
        self.ui.CoordenadaZ.textChanged.connect(self.coordenadas)
        
        
        # coordenadas cinematica directa         
        self.ui.coordenadaq1.textChanged.connect(self.coordenadaq1)
        self.ui.coordenadaq2.textChanged.connect(self.coordenadaq2)
        self.ui.Coordenadaq3.textChanged.connect(self.coordenadaq3)
        self.ui.coordenadaq4.textChanged.connect(self.coordenadaq4)
        
        self.ui.objeto_2.textChanged.connect(self.coordenadaobdir)
        self.ui.objeto.textChanged.connect(self.coordenadaobinv)
        
        self.ui.botonenviar.clicked.connect(self.enviar)
        self.ui.botonenviar_2.clicked.connect(self.enviar_2)
        
        self.ui.botonhome.clicked.connect(self.modohome)
        self.ui.botonhome_2.clicked.connect(self.modohome)
        self.ui.botonhome_7.clicked.connect(self.modohome)
        
        self.ui.botonsoltar_2.clicked.connect(self.coordenadaq5)
        self.ui.botonsoltar.clicked.connect(self.coordenadaq5)
        
        self.ui.botonagarrar.clicked.connect(self.coordenadaq5_2)
        self.ui.botonagarrar_2.clicked.connect(self.coordenadaq5_2)
        
        self.ui.botonborrar_2.clicked.connect(self.borrardatos)
        self.ui.botonborrar.clicked.connect(self.borrardatos)
        
        self.ui.botonrutina1.clicked.connect(self.rutina1)
        self.ui.botonrutina2.clicked.connect(self.rutina2)
        self.ui.botonrutina3.clicked.connect(self.rutina3)

    def rutina1(self):
        # coordenadas x,y de los objetos
        cinta_roja = [-115,125]
        cinta_verde = [-170,50]
        cinta_amarilla = [120,125]
        
        pieza_1 = [65,170]
        pieza_2 = [-190,-40]
        pieza_3 = [175,65]
        
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
           
            #rutina cinta roja
            elif i == 3:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_roja[0],cinta_roja[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 4:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_roja[0],cinta_roja[1],50,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 1
            elif i == 5:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_roja[0],cinta_roja[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            
            #rutina pieza 2
            elif i == 6:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 7:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 0
            elif i == 8:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
           
            #rutina cinta verde
            elif i == 9:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_verde[0],cinta_verde[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 10:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_verde[0],cinta_verde[1],50,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 1
            elif i == 11:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_verde[0],cinta_verde[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)

            #rutina pieza 3
            elif i == 12:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 13:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 0
            elif i == 14:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
           
            #rutina cinta amarilla
            elif i == 15:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_amarilla[0],cinta_amarilla[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            elif i == 16:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_amarilla[0],cinta_amarilla[1],50,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 1
            elif i == 17:
                q1,q2,q3,q4,corr = f.TCI(parametros,cinta_amarilla[0],cinta_amarilla[1],120,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
            
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
            self.graficaq1_6.grafica_datos_q1()
            self.velq1_6.grafica_datos_velq1()
            self.accq1_6.grafica_datos_accq1()
            self.graficaq2_6.grafica_datos_q2()
            self.velq2_6.grafica_datos_velq2()
            self.accq2_6.grafica_datos_accq2()
            self.graficaq3_6.grafica_datos_q3()
            self.velq3_6.grafica_datos_velq3()
            self.accq3_6.grafica_datos_accq3()
            self.graficaq4_6.grafica_datos_q4()
            self.velq4_6.grafica_datos_velq4()
            self.accq4_6.grafica_datos_accq4()
            
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
            #rutina cinta roja
            elif i == 3:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            elif i == 4:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],100,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
                self.q5 = 1
            elif i == 5:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p1[0],caja_p1[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            #rutina pieza 2
            elif i == 6:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 1
            elif i == 7:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 0
            elif i == 8:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_2[0],pieza_2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            #rutina cinta verde
            elif i == 9:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            elif i == 10:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],100,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
                self.q5 = 1
            elif i == 11:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p2[0],caja_p2[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 2
            #rutina pieza 3
            elif i == 12:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            elif i == 13:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],40,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
                self.q5 = 0
            elif i == 14:
                q1,q2,q3,q4,corr = f.TCI(parametros,pieza_3[0],pieza_3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
            #rutina cinta amarilla
            elif i == 15:
                q1,q2,q3,q4,corr = f.TCI(parametros,caja_p3[0],caja_p3[1],150,0,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
                self.ob = 3
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
            self.graficaq1_6.grafica_datos_q1()
            self.velq1_6.grafica_datos_velq1()
            self.accq1_6.grafica_datos_accq1()
            self.graficaq2_6.grafica_datos_q2()
            self.velq2_6.grafica_datos_velq2()
            self.accq2_6.grafica_datos_accq2()
            self.graficaq3_6.grafica_datos_q3()
            self.velq3_6.grafica_datos_velq3()
            self.accq3_6.grafica_datos_accq3()
            self.graficaq4_6.grafica_datos_q4()
            self.velq4_6.grafica_datos_velq4()
            self.accq4_6.grafica_datos_accq4()
            
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
            self.graficaq1_6.grafica_datos_q1()
            self.velq1_6.grafica_datos_velq1()
            self.accq1_6.grafica_datos_accq1()
            self.graficaq2_6.grafica_datos_q2()
            self.velq2_6.grafica_datos_velq2()
            self.accq2_6.grafica_datos_accq2()
            self.graficaq3_6.grafica_datos_q3()
            self.velq3_6.grafica_datos_velq3()
            self.accq3_6.grafica_datos_accq3()
            self.graficaq4_6.grafica_datos_q4()
            self.velq4_6.grafica_datos_velq4()
            self.accq4_6.grafica_datos_accq4()
            
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

        #3.a valores iniciales
        x0=0
        y0=0
        z0=0
        parametros = [float(L0), float(L1), float(L2), float(L3), float(L4), float(L5), float(x0), float(y0), float(z0)]
        
        q1,q2,q3,q4,corr = f.TCI(parametros,self.x,self.y,self.z,delta_e,self.q1ant,self.q2ant,self.q3ant,self.q4ant)
        
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
        self.q1 = 0 #base
        self.q2 = 0 #brazo 2
        self.q3 = 0 #altura
        self.q4 = 0 #rotacion pinza
        self.q5 = 0 #accion pinza
        self.ob = 0 #tamaño objeto
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
        q1_text=float(self.ui.coordenadaq1.toPlainText())
        self.q1 = q1_text
        
        if abs(self.q1) > abs(130):
            msg = QMessageBox()
            msg.setWindowTitle("Advertencia")
            msg.setText("El valor esta por fuera del rango")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
        
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
        q2_text= float(self.ui.coordenadaq2.toPlainText())
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
        q4_text= float(self.ui.coordenadaq4.toPlainText())
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
        self.q1 = 0 #base
        self.q1ant = 0
        self.q2 = 0 #brazo 2
        self.q2ant = 0
        self.q3 = 0 #altura
        self.q3ant = 0
        self.q4 = 0 #rotacion pinza
        self.q4ant = 0
        self.q5 = 0 #accion pinza
        self.ob = 0 #tamaño objeto 
        self.enviar_2()
        
    def enviar(self):
        self.graficarobotinversa.grafica_datos_2()
        self.q1m = self.q1-self.q1ant
        self.q2m = self.q2-self.q2ant
        self.q3m = self.q3-self.q3ant
        self.q4m = self.q4-self.q4ant        
        datos = [self.q1m, self.q2m, self.q3m, self.q4m, self.q5, self.ob, self.home]
        self.serial_thread = SerialThread(self.arduino, datos)
        self.ok = 1

        self.graficaplanoxy.grafica_datos_planoxy()
        self.graficaplanoxz.grafica_datos_planoxz()
        self.graficaplanoyz.grafica_datos_planoyz()
        self.velocidadx.grafica_datos_velx()
        self.velocidady.grafica_datos_vely()
        self.velocidadz.grafica_datos_velz()
        self.aceleracionx.grafica_datos_acelx()
        self.aceleraciony.grafica_datos_acely()
        self.aceleracionz.grafica_datos_acelz()
        
        
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
        datos = [self.q1m, self.q2m, self.q3m, self.q4m, self.q5, self.ob, self.home]
        self.serial_thread = SerialThread(self.arduino, datos)
        self.ok = 1
        
        self.graficaq1.grafica_datos_q1()
        self.velq1.grafica_datos_velq1()
        self.accq1.grafica_datos_accq1()
        self.graficaq2.grafica_datos_q2()
        self.velq2.grafica_datos_velq2()
        self.accq2.grafica_datos_accq2()
        self.graficaq3.grafica_datos_q3()
        self.velq3.grafica_datos_velq3()
        self.accq3.grafica_datos_accq3()
        self.graficaq4.grafica_datos_q4()
        self.velq4.grafica_datos_velq4()
        self.accq4.grafica_datos_accq4()

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
    
    #creacion de figura de grafica 
    def __init__(self , parent=None):
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
        #1.Dimensiones del robot
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
        
            
        n_frames = 100
        t0 = 0
        t1 = 5
        t =np.linspace(t0, t1,n_frames)
            
        self.q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
        self.q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
        self.q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
        self.q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)


        def actualizar(i):
            self.ax.clear()
            self.ax.set_title("Robot SCARA")
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Y")
            self.ax.set_zlabel("Z")
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(-250, 250)
            self.ax.set_zlim(0, 400)
            f.dibrobot(parametros,self.q1v[i],self.q2v[i],self.q3v[i],self.q4v[i], self.ax)
            
        self.ani = FuncAnimation(self.fig, actualizar, range(n_frames),interval =3, repeat=False)
        self.draw()

        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
         
         
class graficarobot_2(FigureCanvas):
    
    #creacion de figura de grafica 
    def __init__(self , parent=None):
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
   
    def grafica_datos_2(self):
        #1.Dimensiones del robot
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
        
            
        n_frames = 100
        t0 = 0
        t1 = 5
        t =np.linspace(t0, t1,n_frames)
            
        self.q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
        self.q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
        self.q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
        self.q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)


        def actualizar_2(i):
            self.ax.clear()
            self.ax.set_title("Robot SCARA")
            self.ax.set_xlabel("X")
            self.ax.set_ylabel("Y")
            self.ax.set_zlabel("Z")
            self.ax.set_xlim(-250, 250)
            self.ax.set_ylim(-250, 250)
            self.ax.set_zlim(0, 400)
            f.dibrobot(parametros,self.q1v[i],self.q2v[i],self.q3v[i],self.q4v[i], self.ax)
            
        self.ani_2 = FuncAnimation(self.fig, actualizar_2, range(n_frames),interval =3, repeat=False)
        self.draw()

        self.q1ant = self.q1
        self.q2ant = self.q2
        self.q3ant = self.q3
        self.q4ant = self.q4
        
        
class graficaplanoxy(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_planoxy(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t =np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)
         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("Plano XY")
         self.ax.set_xlabel("X")
         self.ax.set_ylabel("Y")
         self.ax.set_xlim(-250, 250)
         self.ax.set_ylim(-250, 250)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         self.ax.plot(xe,ye)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4 
        
class graficaplanoxz(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
     
     def grafica_datos_planoxz(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t =np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("Plano XZ")
         self.ax.set_xlabel("X")
         self.ax.set_ylabel("Z")
         self.ax.set_xlim(-250, 250)
         self.ax.set_ylim(0, 200)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         self.ax.plot(xe,ze)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficaplanoyz(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_planoyz(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t =np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)
         
         self.ax.set_title("Plano YZ")
         self.ax.set_xlabel("X")
         self.ax.set_ylabel("Z")
         self.ax.set_xlim(-250, 250)
         self.ax.set_ylim(0, 200)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         self.ax.plot(ye,ze)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4

class graficavelx(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_velx(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("Velocidad X")
         self.ax.set_xlabel("X")
         self.ax.set_ylabel("t")
         #self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         velx = np.gradient(xe,t)
         #3velx = np.concatenate(([0], velx))
         self.ax.plot(t,velx)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficavely(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_vely(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("velocidad Y")
         self.ax.set_xlabel("Y")
         self.ax.set_ylabel("t")
         self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         vely = np.gradient(ye,t)
         #vely = np.concatenate(([0], vely))
         self.ax.plot(t,vely)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficavelz(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_velz(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("velocidad Z")
         self.ax.set_xlabel("Z")
         self.ax.set_ylabel("t")
         self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         velz = np.gradient(ze,t)
         #velz = np.concatenate(([0], velz))
         self.ax.plot(t,velz)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficaaccx(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_acelx(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)

         self.ax.set_title("Aceleración X")
         self.ax.set_xlabel("X")
         self.ax.set_ylabel("t")
         #self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         velx = np.gradient(xe,t)#/np.diff(t)
         acelx = np.gradient(velx,t) 
         #acelx = np.concatenate(([0], acelx))
         #acelx = np.concatenate(([0], acelx))
         self.ax.plot(t,acelx)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficaaccy(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_acely(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
         
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)
         
         self.ax.set_title("Aceleración Y")
         self.ax.set_xlabel("Y")
         self.ax.set_ylabel("t")
         #self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         vely = np.gradient(ye,t)#/np.diff(t)
         acely = np.gradient(vely,t) 
         #acely = np.concatenate(([0], acely))
         #acely = np.concatenate(([0], acely))
         self.ax.plot(t,acely)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4

class graficaaccz(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_acelz(self):
         #1.Dimensiones del robot
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
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q1v,v1,a1 = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         q2v,v2,a2 = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         q3v,v3,a3 = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         q4v,v4,a4 = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)

         xe = np.linspace(0,0,n_frames)
         ye = np.linspace(0,0,n_frames)
         ze = np.linspace(0,0,n_frames)
         self.ax.set_title("Aceleración Z")
         self.ax.set_xlabel("Y")
         self.ax.set_ylabel("t")
         #self.ax.set_xlim(0, 5)
         #self.ax.set_ylim(-1, 1)
         for i in range(n_frames):
             xe[i],ye[i],ze[i] = f.TCD(parametros, q1v[i], q2v[i], q3v[i], q4v[i])
         velz = np.gradient(ze,t)#/np.diff(t)
         acelz = np.gradient(velz,t) 
         #acelz = np.concatenate(([0], acelz))
         #acelz = np.concatenate(([0], acelz))
         self.ax.plot(t,acelz)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4

class graficaq1(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_q1(self):
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q,v,a = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         
         self.ax.set_title("Trayectoria q1")
         self.ax.set_xlabel("q1")
         self.ax.set_ylabel("t")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-140, 140)
         self.ax.plot(t,q)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4

class graficavelq1(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_velq1(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q1")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("vq1")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         
         self.ax.plot(t,v)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4

class graficaaccq1(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def grafica_datos_accq1(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q1")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("vq1")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q1ant, self.q1, 0.36, 0.18)
         
         self.ax.plot(t,a)
         self.draw()
         self.q1ant = self.q1
         self.q2ant = self.q2
         self.q3ant = self.q3
         self.q4ant = self.q4
         
class graficaq2(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
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
         
     def q2b(self, q2):
         self.q2 = q2

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_q2(self):
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q,v,a = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         
         self.ax.set_title("Trayectoria q2")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("q2")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-140, 140)
         self.ax.plot(t,q)
         self.draw()
         self.q2ant = self.q2

class graficavelq2(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
         self.q2 = 0
         self.q2ant = 0
         
     def q2b(self, q2):
         self.q2 = q2

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_velq2(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q2")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("vq2")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         
         self.ax.plot(t,v)
         self.draw()
         self.q2ant = self.q2

class graficaaccq2(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
         self.q2 = 0
         self.q2ant = 0
         
     def q2b(self, q2):
         self.q2 = q2

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_accq2(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Aceleración q2")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("aq2")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q2ant, self.q2, 0.36, 0.18)
         
         self.ax.plot(t,a)
         self.draw()
         self.q2ant = self.q2
         
class graficaq3(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
         self.q3 = 0
         self.q3ant = 0  
         
     def q3b(self, q3):
         self.q3 = q3

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_q3(self):
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q,v,a = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         
         self.ax.set_title("Trayectoria q3")
         self.ax.set_xlabel("q3")
         self.ax.set_ylabel("t")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-140, 140)
         self.ax.plot(t,q)
         self.draw()
         self.q3ant = self.q3

class graficavelq3(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
         self.q3 = 0
         self.q3ant = 0  
         
     def q3b(self, q3):
         self.q3 = q3

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_velq3(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q3")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("vq3")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-18, 18)
         
         q,v,a = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         
         self.ax.plot(t,v)
         self.draw()
         self.q3ant = self.q3


class graficaaccq3(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)

         self.q3 = 0
         self.q3ant = 0   
         
     def q3b(self, q3):
         self.q3 = q3

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_accq3(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q3")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("aq3")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-7, 7)
         
         q,v,a = f.trayarticulacion(self.q3ant, self.q3, 12.5, 6.25)
         
         self.ax.plot(t,a)
         self.draw()
         self.q3ant = self.q3

class graficaq4(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
       
         self.q4 = 0
         self.q4ant = 0  
         
     def q4b(self, q4):
         self.q4 = q4

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_q4(self):
         n_frames = 100
         t0 = 0
         t1 = 5
         t  = np.linspace(t0, t1,n_frames)
             
         q,v,a = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)
         
         self.ax.set_title("Trayectoria q4")
         self.ax.set_xlabel("q4")
         self.ax.set_ylabel("t")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-140, 140)
         self.ax.plot(t,q)
         self.draw()
         self.q4ant = self.q4

class graficavelq4(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
        
         self.q4 = 0
         self.q4ant = 0  
         
     def q4b(self, q4):
         self.q4 = q4

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_velq4(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q4")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("vq4")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)
         
         self.ax.plot(t,v)
         self.draw()
         self.q4ant = self.q4

class graficaaccq4(FigureCanvas):
     
     #creacion de figura de grafica 
     def __init__(self , parent=None):
         self.fig = plt.figure()
         self.ax = self.fig.add_subplot(111)
         super().__init__(self.fig)
         plt.grid(True)
         
         self.q4 = 0
         self.q4ant = 0  
         
     def q4b(self, q4):
         self.q4 = q4

     def limpiar(self):
         self.ax.clear()    
         
     def grafica_datos_accq4(self):
         
         t0 = 0
         tf = 5
         n_frames = 100 
         t = np.linspace(t0,tf,n_frames)
         
         self.ax.set_title("Velocidad q4")
         self.ax.set_xlabel("t")
         self.ax.set_ylabel("aq4")
         plt.grid(True)
         #self.ax.set_xlim(0, 5)
         self.ax.set_ylim(-0.5, 0.5)
         
         q,v,a = f.trayarticulacion(self.q4ant, self.q4, 0.36, 0.18)
         
         self.ax.plot(t,a)
         self.draw()
         self.q4ant = self.q4

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mi_app = Miapp()
    mi_app.show()
    #plt.close('all')
    sys.exit(app.exec_())       
        
        
        
        
        
        
        