# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:40:18 2024

@author: juand
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def eslabon(p0, p1, color, linewidth, ax):
    # Create a 3D figure and add a 3D subplot
    # Plot the link line in 3D
    ax.plot([p0[0], p1[0]],
            [p0[1], p1[1]],
            [p0[2], p1[2]],
            color=color, linewidth=linewidth)
    # Set aspect ratio to equal

def triedro(M, i, ax, scale):

  # Extract basis vectors from the transformation matrix
  n = np.array([fila[3] for fila in M])*scale
  o = np.array([fila[3] for fila in M])*scale
  a = np.array([fila[3] for fila in M])*scale
  p = np.array([fila[3] for fila in M])
 

  # Plot the axes with different colors and labels
  # ax.plot([p[0], p[0] + n[0]], [p[1], p[1] + n[1]], [p[2], p[2] + n[2]], 'red', label=f"X-{i}", linewidth=2)
  # ax.plot([p[0], p[0] + o[0]], [p[1], p[1] + o[1]], [p[2], p[2] + o[3]], 'green', label=f"Y-{i}", linewidth=2)
  # ax.plot([p[0], p[0] + a[0]], [p[1], p[1] + a[1]], [p[2], p[2] + a[2]], 'blue', label=f"Z-{i}", linewidth=2)

  # Plot the origin point as a black marker
  ax.plot(p[0], p[1], p[2], '.k', markersize=5)

def dibrobot(parameters,q1v,q2v,q3v,q4v,ax):
    #parametros
    escala=5
    L0=parameters[0] #base
    L1=parameters[1] #altura
    L2=parameters[2] #brazo 1 
    L3=parameters[3] #union brazo 1 y 2
    L4=parameters[4] #brazo 2
    L5=parameters[5] #pinza
    x0=parameters[6]
    y0=parameters[7]
    z0=parameters[8]
    #%3.c matrices inicial
    M0  =   [[1,0,0,x0],[0,1,0,y0],[0,0,1,z0],[0,0,0,1]]
    M01 =   trasy(M0,-L0)
    M02 =   trasy(M0,70)
    M03 =   trasz(M0,50)
    M033 =  trasz(M03,120)
    M1  =   trasz(M033,L1)
    M04 =   trasz(M1,48)
    M2  =   rotz(M033,q1v)
    M22 =   trasz(M2,138)
    M3  =   trasz(M22,q3v)
    M4  =   trasy(M3,L2)
    M5  =   rotz(M4,q2v)
    M6  =   trasz(M5,-L3)
    M7  =   trasy(M6,L4)
    M8  =   rotz(M7,q4v)
    M9  =   trasz(M8,-L5)
    
    #%3.d puntos de posicion cada matriz
    P0  = [fila[3] for fila in M0]
    P01 = [fila[3] for fila in M01]
    P02 = [fila[3] for fila in M02]
    P03 = [fila[3] for fila in M03]
    P033 = [fila[3] for fila in M033]
    P04 = [fila[3] for fila in M04]
    P1  = [fila[3] for fila in M1]
    P2  = [fila[3] for fila in M2]
    P3  = [fila[3] for fila in M3]
    P4  = [fila[3] for fila in M4]
    P5  = [fila[3] for fila in M5]
    P6  = [fila[3] for fila in M6]
    P7  = [fila[3] for fila in M7]
    P8  = [fila[3] for fila in M8]
    P9  = [fila[3] for fila in M9]
    
    #%3.f eslabones robot
    eslabon(P0,P01,"#121212",10,ax)#base
    eslabon(P0,P02,"#121212",10,ax)#base
    eslabon(P0,P03,"#121212",10,ax)#base traslacion
    eslabon(P03,P033,"#575A66",10,ax)
    eslabon(P033,P1,"#d6d9de",10,ax)#altura
    eslabon(P1,P04,"#575A66",10,ax)#base arriba traslacion
    #eslabon(P2,P3,"#1100DB",10,ax)
    eslabon(P3,P4,"#121212",10,ax) #brazo 1
    eslabon(P5,P6,"#575A66",10,ax) #union brazo 1 y 2 
    eslabon(P6,P7,"#121212",10,ax) #brazo 2 
    eslabon(P8,P9,"#575A66",5,ax) #pinza
    

    triedro(M3,3,ax,escala)
    triedro(M4,4,ax,escala)
    triedro(M5,5,ax,escala)
    triedro(M6,6,ax,escala)
    triedro(M7,7,ax,escala)
    triedro(M9,9,ax,escala)

def trayarticulacion (q0,qf,vmax,amax):
    
    if q0 > qf:
        vmax = -vmax
        amax = -amax

    if q0 == qf: 
        vmax = 1
        amax = 1

    t1 = vmax/amax
    s = qf-q0-((vmax**2)/amax)
    t2 = (s/vmax)+t1 #(qf-q0+(vmax**2/amax))/vmax
    t0 = 0
    tf = t1+t2   
    a0 = q0
    a1 = 0
    a2 = amax/2
    b0 = q0 - ((vmax**2)/(2*amax)) #q0 + (amax/2)*(t1**2)-vmax*t1
    b1 = vmax
    c2 = -a2#-amax/2 
    c1 = amax*tf
    c0 = qf - (amax*(tf**2))/2  #qf -c1*tf - c2*tf**2
    
    if q0 == qf: 
        a1 = 0
        a2 = 0
        c1 = 0
        c2 = 0
        b1 = 0

    t11 = np.linspace(t0,t1,100)
    t22 = np.linspace(t1,t2,100)
    t33 = np.linspace(t2,tf,100)
    

    t = np.concatenate((t11,t22,t33))

    q11 = a0 + a1*t11 + a2*(t11**2)
    q22 = b0 + b1*t22
    q33 = c0 + c1*t33 + c2*(t33**2)

    q = np.concatenate((q11,q22,q33))

    v11 = a1 + 2*a2*t11
    v22 = np.linspace(b1,b1,100)
    v33 = c1 + 2*c2*t33

    v = np.concatenate((v11,v22,v33))

    a11 = np.linspace(2*a2,2*a2,100)
    a22 = np.zeros(100)
    a33 = np.linspace(2*c2,2*c2,100)

    a = np.concatenate((a11,a22,a33))
    
    return q,v,a


def tray5orden(t0, t1, q0, q1, n_frames):
  """
  Generates a fifth-order polynomial trajectory for a robotic motion.

  Args:
      t0: Initial time (scalar)
      t1: Final time (scalar)
      q0: Initial position (scalar)
      q1: Final position (scalar)
      n_frames: Number of frames for the trajectory (scalar)

  Returns:
      q: A numpy array containing the trajectory positions for each frame (n_frames x 1)
  """

  # Time vector generation
  t = np.linspace(t0, t1, n_frames)

  # Motion profile definition
  M =[
      [t0**5, t0**4, t0**3, t0**2, t0, 1],
      [t1**5, t1**4, t1**3, t1**2, t1, 1],
      [5*t0**4, 4*t0**3, 3*t0**2, 2*t0, 1, 0],
      [5*t1**4, 4*t1**3, 3*t1**2, 2*t1, 1, 0],
      [20*t0**3, 12*t0**2, 6*t0, 2, 0, 0],
      [20*t1**3, 12*t1**2, 6*t1, 2, 0, 0]
  ]
  v = [q0, q1, 0, 0, 0, 0]

  # Coefficient calculation using numpy solve
  coeficientes = np.linalg.solve(M, v)

  # Extract coefficients
  a, b, c, d, e, f = coeficientes

  # Trajectory generation
  q = (a * t**5) + (b * t**4) + (c * t**3) + (d * t**2) + (e * t) + f

  return q

# funciones de animacion 
def rotx(M,theta):
    theta = theta * (np.pi / 180)
    rotx=[[1,         0,               0,         0],
          [0,   np.cos(theta),  -np.sin(theta),   0],
          [0,   np.sin(theta),   np.cos(theta),   0],
          [0,         0,               0,         1]]
    B=np.dot(M,rotx)
    return B

def roty(M,theta):
    theta = theta * (np.pi / 180)
    roty=[[np.cos(theta),   0,   np.sin(theta),   0],
          [      0,         1,         0,         0],
          [-np.sin(theta),  0,   np.cos(theta),   0],
          [       0,        0,         0,         1]]
    B=np.dot(M,roty)
    return B

def rotz(M,theta):
    
    theta = theta * (np.pi / 180)
    rotz=[[np.cos(theta),  -np.sin(theta),   0,   0],
          [np.sin(theta),   np.cos(theta),   0,   0],
          [      0,              0,          1,   0],
          [      0,              0,          0,   1]]
    B=np.dot(M,rotz)
    return B 

def trasx(M,A):

    trasx=[[1, 0, 0, A],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]]
    B=np.dot(M,trasx)
    return B
def trasy(M,A):

    trasy=[[1, 0, 0, 0],
           [0, 1, 0, A],
           [0, 0, 1, 0],
           [0, 0, 0, 1]]
    B=np.dot(M,trasy)
    return B

def trasz(M,A):

    trasz=[[1, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, A],
           [0, 0, 0, 1]]
    B=np.dot(M,trasz)
    return B

def TCD(parameters,q1,q2,q3,q4):
    
    L0=parameters[0] #base
    L1=parameters[1] #altura
    L2=parameters[2] #brazo 1 
    L3=parameters[3] #union brazo 1 y 2
    L4=parameters[4] #brazo 2
    L5=parameters[5] #pinza
    x0=parameters[6]
    y0=parameters[7]
    z0=parameters[8]
    #%3.c matrices inicial
    M0  =   [[1,0,0,x0],[0,1,0,y0],[0,0,1,z0],[0,0,0,1]]
    M01 =   trasy(M0,-L0)
    M02 =   trasy(M0,70)
    M03 =   trasz(M0,50)
    M033 =  trasz(M03,120)
    M1  =   trasz(M033,L1)
    M04 =   trasz(M1,48)
    M2  =   rotz(M033,q1)
    M22 =   trasz(M2,L1/2)
    M3  =   trasz(M22,q3)
    M4  =   trasy(M3,L2)
    M5  =   rotz(M4,q2)
    M6  =   trasz(M5,-L3)
    M7  =   trasy(M6,L4)
    M8  =   rotz(M7,q4)
    M9  =   trasz(M8,-L5)

    # 3.d puntos de posicion cada matriz
    P9 = [fila[3] for fila in M9]
    
    xe=P9[0]
    ye=P9[1]
    ze=P9[2]

    return [xe,ye,ze]

def TCI(parameters, xe, ye, ze, delta_e, q1ant, q2ant, q3ant, q4ant):

    L0=parameters[0] #base
    L1=parameters[1] #altura
    L2=parameters[2] #brazo 1 
    L3=parameters[3] #union brazo 1 y 2
    L4=parameters[4] #brazo 2
    L5=parameters[5] #pinza
    x0=parameters[6]
    y0=parameters[7]
    z0=parameters[8]
    corr_a = 0
    corr_b = 0
    corr = 0
    
    # Calculate the distance from the base to the end-effector (excluding Z)
    R = np.sqrt(xe**2 + ye**2)
    
    # Calculate angles alpha and beta using the law of cosines
    alpha = np.arccos(( R**2  + L2**2 - L4**2 ) / (2 * R * L2))* (180 / np.pi)
    beta  = np.arccos(( L2**2 + L4**2 - R**2 ) / (2 * L2 * L4))* (180 / np.pi)
    alpha1  = np.arctan2(xe,ye) * (180 / np.pi)
    
    #solucion codo arriba
    # Calculate joint angles q1, q2, and q3
    q1_A = alpha - alpha1
    q2_A = -(180 - beta)
    q3_A = ze + L5 + L3 - 170 - (L1/2)
    # Calculate joint angle q4 based on desired tool orientation and other joint angles
    q4_A = delta_e
    
    if q1_A > 130:
        q1_A = 130
        corr_a = 1
        print("q1_a corregido")
        
    elif q1_A < -130:
        
        q1_A = -130
        corr_a = 1
        print("q1_a corregido")
        
    if q2_A > 130:
        
        q2_A = 130
        corr_a = 1
        print("q2_a corregido")
        
    elif q2_A < -130:
        
        q2_A = -130
        corr_a = 1
        print("q2_a corregido")
        
    
    #solucion codo abajo 
    q1_B = -(alpha + alpha1)
    q2_B = (180 - beta)
    q3_B = ze + L5 + L3 - 170 - (L1/2)
    # Calculate joint angle q4 based on desired tool orientation and other joint angles
    q4_B = delta_e
    
    if q1_B > 130:
        q1_B = 130
        corr_b = 1
        print("q1_b corregido")
    elif q1_B < -130:
        q1_B = -130
        corr_b = 1
        print("q1_b corregido")

        
    if q2_B > 130:
        q2_B = 130
        corr_b = 1
        print("q2_b corregido")
    elif q2_B < -130:
        q2_B = -130
        corr_b = 1
        print("q2_b corregido")

    
    if corr_b == 1: 
        corr = 1
        
    elif corr_a == 1:
        corr = 1
    
    
    q1_c = q1_A - q1ant
    q2_c = q2_A - q2ant
    
    q1_d = q1_B - q1ant
    q2_d = q2_B - q2ant
    
    if corr_b == 1:
        
        q1 = q1_A
        q2 = q2_A
        q3 = q3_A
        q4 = q4_A
        print("codo arriba")
        corr = 0
        
    elif corr_a == 1:
        
        q1 = q1_B
        q2 = q2_B
        q3 = q3_B
        q4 = q4_B
        print("codo abajo")
        corr = 0 
    
    elif q1_c > q1_d : 
        q1 = q1_B
        q2 = q2_B
        q3 = q3_B
        q4 = q4_B
        print("codo abajo")
    else:
        q1 = q1_A
        q2 = q2_A
        q3 = q3_A
        q4 = q4_A
        print("codo arriba")
        
         
    return [q1, q2, q3, q4,corr]


