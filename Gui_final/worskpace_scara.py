# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 11:33:31 2024

@author: JUAN DAVID
"""

import numpy as np
import funciones as f
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.show()

nframes = 10
q1_rango = [-130, 130]
q2_rango = [-130, 130]
q3_rango = [-101, 101]
q4_rango = [0 , 270]


q1 = np.linspace(q1_rango[0], q1_rango[1],nframes)
q2 = np.linspace(q2_rango[0], q2_rango[1],nframes)
q3 = np.linspace(q3_rango[0], q3_rango[1],nframes)
q4 = np.linspace(q4_rango[0], q4_rango[1],nframes)

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
x_valores = []
y_valores = []
z_valores = []
    

for i in range(nframes):
    for j in range(nframes):
        for k in range(nframes):
            x,y,z = f.TCD(parametros, q1[j], q2[k], q3[i], q4[k])
            x_valores.append(x)
            y_valores.append(y)
            z_valores.append(z)
            
#ax.scatter(x_valores, y_valores, z_valores)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')




x,y = np.meshgrid(x_valores,y_valores)
z = np.gradient(z_valores)
ax.scatter(x, y, z)            
