# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 17:34:30 2024

@author: juand
"""
import numpy as np
import funciones as f
import matplotlib.pyplot as plt 
L0 = 145
L1 = 314
L2 = 123
L3 = 72
L4 = 84
L5 = 111

#3.a valores iniciales
x0=0
y0=0
z0=0
parameters = [float(L0), float(L1), float(L2), float(L3), float(L4), float(L5), float(x0), float(y0), float(z0)]

xe = 100
ye = -180
ze = 30
delta_e = 0

L0=parameters[0] #base
L1=parameters[1] #altura
L2=parameters[2] #brazo 1 
L3=parameters[3] #union brazo 1 y 2
L4=parameters[4] #brazo 2
L5=parameters[5] #pinza
x0=parameters[6]
y0=parameters[7]
z0=parameters[8]

# Calculate the distance from the base to the end-effector (excluding Z)
R = np.sqrt(xe**2 + ye**2)

# Calculate angles alpha and beta using the law of cosines
alpha = np.arccos(( R**2  + L2**2 - L4**2 ) / (2 * R * L2))* (180 / np.pi)
beta  = np.arccos(( L2**2 + L4**2 - R**2 ) / (2 * L2 * L4))* (180 / np.pi)
alpha1  = np.arctan2(xe,ye) * (180 / np.pi)


#solucion codo arriba
# Calculate joint angles q1, q2, and q3
q1 = alpha - alpha1
q2 = -(180 - beta)
#q3 = -(170 + (L1/2) - L3 - L5 - ze)
q3 = ze + L5 + L3 - 170 - (L1/2)
# Calculate joint angle q4 based on desired tool orientation and other joint angles
q4 = delta_e



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_xlim(-250, 250)
ax.set_ylim(-250, 250)
ax.set_zlim(0, 600)


f.dibrobot(parameters, q1, q2, q3, q4, ax)
x,y,z = f.TCD(parameters, q1, q2, q3, q4)

#solucion codo abajo 
q1_2 = -(alpha + alpha1)
q2_2 = (180 - beta)
q3_2 = -(170 + 138 - L3 - L5 - ze)
# Calculate joint angle q4 based on desired tool orientation and other joint angles
q4_2 = delta_e


f.dibrobot(parameters, q1_2, q2_2, q3_2, q4_2, ax)
x_2,y_2,z_2 = f.TCD(parameters, q1_2, q2_2, q3_2, q4_2)
# q0 = 0
# qf = q3
# vmax = 16
# amax = 4


# if q0 > qf:
#     vmax = -vmax
#     amax = -amax

# t1 = vmax/amax
# s = qf-q0-((vmax**2)/amax)
# t2 = (s/vmax)+t1 #(qf-q0+(vmax**2/amax))/vmax
# t0 = 0
# tf = t1+t2   
# a0 = q0
# a1 = 0
# a2 = amax/2
# b0 = q0 - ((vmax**2)/(2*amax)) #q0 + (amax/2)*(t1**2)-vmax*t1
# b1 = vmax
# c2 = -a2#-amax/2 
# c1 = amax*tf
# c0 = qf - (amax*(tf**2))/2  #qf -c1*tf - c2*tf**2

# if q0 == qf: 
#     a1 = 0
#     a2 = 0
#     c1 = 0
#     c2 = 0
#     b1 = 0

# t11 = np.linspace(t0,t1,34)
# t22 = np.linspace(t1,t2,33)
# t33 = np.linspace(t2,tf,33)

# t = np.concatenate((t11,t22,t33))

# q11 = a0 + a1*t11 + a2*(t11**2)
# q22 = b0 + b1*t22
# q33 = c0 + c1*t33 + c2*(t33**2)

# q = np.concatenate((q11,q22,q33))

# v11 = a1 + 2*a2*t11
# v22 = np.linspace(b1,b1,33)
# v33 = c1 + 2*c2*t33

# v = np.concatenate((v11,v22,v33))

# a11 = np.linspace(2*a2,2*a2,34)
# a22 = np.zeros(33)
# a33 = np.linspace(2*c2,2*c2,33)

# a = np.concatenate((a11,a22,a33))

# fig2 = plt.figure()
# plt.plot(t,v) 
