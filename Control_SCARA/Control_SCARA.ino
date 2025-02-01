/*---------------------------------------------------------------------------------------------------------------------------------------------
| Código para el movimiento de un motor paso a paso y un servo motor los cuales estan conectados a una tarjeta de control de motores para CNC |
| la tarjeta a utilizar corresponde a una ramps 1.4, con driver de motores paso a paso DVR8825, el motor paso a paso utilizado es un NEMA17   |
| con una resolución de 200 pasos por revolución y una corriente de 2.5A. Además, se implementan finales de carrera como interrupciones en el |
| script. El código se enlaza con matlab mediante el puerto serial para la recepción de la posición en grados a la que debe moverse el motor  |
| paso a paso.                                                                                                                                |
-----------------------------------------------------------------------------------------------------------------------------------------------*/

#include <AccelStepper.h>  //Libreria que controla la velocidad y aceleración de los motores paso a paso
#include <Servo.h>         // Libreria para control de Servomotor

//Definición de variables y pines a utilizar
// Variables de recepcion de datos seriales-------------------------------
String dataString = "";
bool dataComplete = false;
const char separator = ',';  // Los datos deben separarse por comas
const int datalength = 7;    // cantidad de datos a recibir
int datos[datalength];
//------------------------------------------------------------------------

//Pines de control motor x o q1-------------------------------------------
#define X_ENABLE_PIN 38//24//38
#define X_DIR_PIN 55//26//28//55
#define X_STEP_PIN 54//28//26//54
#define X_Stop_PIN 3//2//6//15//3
//------------------------------------------------------------------------
//Pines de control motor y o q2-------------------------------------------
#define Y_ENABLE_PIN 56//30//34//56
#define Y_DIR_PIN 61//32//36//61
#define Y_STEP_PIN 60//34//30//60
#define Y_Stop_PIN 2//18//16//2
//-----------------------------------------------------------------------
//Pines de control motor Z o q3------------------------------------------
#define Z_ENABLE_PIN 24//36//24
#define Z_DIR_PIN 28//38//42//28
#define Z_STEP_PIN 26//40//40//26
#define Z_stop_PIN 19//17//19
//-----------------------------------------------------------------------
// Declaración de variables de control de los motores q1,q2,q3,q4---------
float q1;
float q2;
float q3;
float q4;
int  q5;
long pasosq1 = 0;
float torqueq1 = 6.1; // tolerancia de +- 0.5°
int torqueq2 = 6.1;
long pasosq2 = 0;
long pasosq4 = 0;
long pasosq3 = 0;  //altura maxima 207mm
//------------------------------------------------------------------------

// Declaración del objeto stepper corresponde al motor paso a paso------
// Parametros (modo de paso, pin de pulsos, pin de dirección)
AccelStepper stepperX(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper steppery(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperz(1, Z_STEP_PIN, Z_DIR_PIN);
//-----------------------------------------------------------------------

// variables necesarias para control de servomotor de pinza-------------------------
#define Servopin 4//22   // Pin de control ServoMotor
Servo servo1;         // Creación de objeto Servo para control de Servomotor
int pulsomin = 544;   // Pulso minimo en microsegundos para control de Servo
int pulsomax = 2400;  // Pulso Maximo "                                    "
//---------------------------------------------------------------------------------

// variables para control de motor paso a paso 28BYJ-48----------------------------
int Paso[8][4] =  // matriz de control para trabajar a 1/2 paso
  { { 1, 0, 0, 0 },
    { 1, 1, 0, 0 },
    { 0, 1, 0, 0 },
    { 0, 1, 1, 0 },
    { 0, 0, 1, 0 },
    { 0, 0, 1, 1 },
    { 0, 0, 0, 1 },
    { 1, 0, 0, 1 } };

#define IN1 32//11//39//32
#define IN2 47//10//41//47
#define IN3 45//9//43//45
#define IN4 43//8//45//43
#define pinza_stop_PIN 18//3//18
int steps_left = 0;
boolean Direction = true;
int Steps = 0;
float ob = 0;
float home = 0;
//-----------------------------------------------------------------------------------

void setup() {
  // Definición de los pines como salidas----------------------------
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);

  pinMode(X_Stop_PIN, INPUT_PULLUP);
  pinMode(Y_Stop_PIN, INPUT_PULLUP);
  pinMode(Z_stop_PIN, INPUT_PULLUP);
  pinMode(pinza_stop_PIN, INPUT_PULLUP);

  pinMode(Servopin, OUTPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  //-----------------------------------------------------------------

  //Pines de interrupcion en funcion de los finales de carrera-----------
  // xstop en final de carrera 1
  // ystop en final de carrera 2
  // zstop en final de carrera 6
  // pinzastop en final de carrera 5
  //---------------------------------------------------------------------

  // incialización de Servomotor
  servo1.attach(Servopin);

  // Inicialización del puerto Serial
  Serial.begin(115200);

  // Deshabilitación del motor paso a paso a mover----------------------
  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);
  //---------------------------------------------------------------------

  // velocidad maxima y aceleración de los motores paso a paso-----------
  stepperX.setMaxSpeed(5000);
  steppery.setMaxSpeed(5000);
  stepperz.setMaxSpeed(5000);
  stepperX.setAcceleration(2500);
  steppery.setAcceleration(2500);
  stepperz.setAcceleration(2500);
  //---------------------------------------------------------------------

  //modohome();

  attachInterrupt(digitalPinToInterrupt(X_Stop_PIN), detenerx, CHANGE);
  attachInterrupt(digitalPinToInterrupt(Y_Stop_PIN), detenery, CHANGE);
  attachInterrupt(digitalPinToInterrupt(Z_stop_PIN), detenerz, CHANGE);
  attachInterrupt(digitalPinToInterrupt(pinza_stop_PIN), detenerpinza, CHANGE);
}

void loop() {
  // Las acciones se ejecutan si hay información disponible en el puerto serial
  // Verificación de informacion en el puerto serial
  if (dataComplete) {
    // toma los datos recibidos por el puerto serial y los guarda en el array datos
    for (int i = 0; i < datalength; i++) {
      int index = dataString.indexOf(separator);
      datos[i] = dataString.substring(0, index).toFloat();
      dataString = dataString.substring(index + 1);
    }

    // se pasan los datos a las diferentes variables-----------------------------------
    q1 = datos[0];
    q2 = datos[1];
    q3 = datos[2];
    q4 = datos[3];
    q5 = datos[4];
    ob = datos[5];
    home = datos[6];
    
    if (home == 1)
    {
      detachInterrupt(digitalPinToInterrupt(X_Stop_PIN));
      detachInterrupt(digitalPinToInterrupt(Y_Stop_PIN));
      detachInterrupt(digitalPinToInterrupt(Z_stop_PIN));
      detachInterrupt(digitalPinToInterrupt(pinza_stop_PIN));
      modohome();
      home = 0;
      attachInterrupt(digitalPinToInterrupt(X_Stop_PIN), detenerx, CHANGE);
      attachInterrupt(digitalPinToInterrupt(Y_Stop_PIN), detenery, CHANGE);
      attachInterrupt(digitalPinToInterrupt(Z_stop_PIN), detenerz, CHANGE);
      attachInterrupt(digitalPinToInterrupt(pinza_stop_PIN), detenerpinza, CHANGE);      
    }
    //----------------------------------------------------------------------------------
    // se reenvian los datos por el puerto serial para verificar la conexion y recepcion
    //Serial.println(q1);
    //Serial.println(q2);
    //Serial.println(q3);
    //Serial.println(q4);
    //Serial.println(ob);
    //---------------------------------------------------------------------------------
    // Habilitación de motor paso a paso-------------------------------------------------------------------------
    digitalWrite(X_ENABLE_PIN, LOW);
    digitalWrite(Y_ENABLE_PIN, LOW);
    digitalWrite(Z_ENABLE_PIN, LOW);
    //-----------------------------------------------------------------------------------------------------------

    // Cálculo de pasos a realizar por el motor teniendo en cuenta la resolucion de paso 200/360 = 1.8° por paso
    // q3 se calcula teniendo en cuenta la relación de avance de la varilla roscada 8mm por revolución
    pasosq1 = (q1 * (3200 / 360.00)) * torqueq1;
    pasosq2 = (q2 * (3200 / 360.00)) * torqueq2;
    pasosq3 = -q3 * (3200 / 8.00);  //altura maxima +-10.1cm o 101mm
    //------------------------------------------------------------------------------------------------------------
    // Carga de pasos a realizar por los motores q1,q2,q3---------------------------------------------------------
    stepperX.move(pasosq1);
    steppery.move(pasosq2);
    stepperz.move(pasosq3);
    //------------------------------------------------------------------------------------------------------------

    while (stepperX.distanceToGo() != 0 || steppery.distanceToGo() != 0 || stepperz.distanceToGo() != 0) {  // verificacion de que el motor se ha movido los pasos indicados de lo contrario puede seguir moviendose
      stepperX.run();
      steppery.run();
      stepperz.run();
    }

    digitalWrite(X_ENABLE_PIN, HIGH);
    digitalWrite(Y_ENABLE_PIN, HIGH);
    digitalWrite(Z_ENABLE_PIN, HIGH);

    moverpinza(q4);

    if (ob == 1){
      if (q5 == 0){servo1.write(21);}else if (q5==2){delay(10);}else {servo1.write(105);}
    }
    else if (ob == 2){
      if (q5 == 0){servo1.write(43);}else if (q5==2){delay(10);}else {servo1.write(105);}
    }
    else if(ob == 3){
      if (q5 == 0){servo1.write(70);}else if (q5==2){delay(10);}else {servo1.write(105);
    }}
    else if (ob == 4){
     if (q5 == 0){servo1.write(50);}else if (q5==2){delay(10);}else {servo1.write(105);
    }
    }
    else {
      servo1.write(105);
      delay(10);
    }
    // Movimiento de motor 28BYJ-48-------------------------------------------------

    // agarrar cosas 1 
    // soltar cosas 0
  
    // Deshabilitacion del motor con el fin de disminuir la carga de corriente

    //-------------------------------------------------------------------------------
    // Se reinicia el datastring y el data complete para una proxima recepcion
    dataString = "";
    dataComplete = false;
    Serial.println("A");  // Envio de accion realizada a matlab y de que puede enviar mas instrucciones
  
  }
}


// Funciones adicionales creadas y necesarias para el control de cada uno de los mototes

// Recepción de datos Seriales----------------------------------------------------------
void serialEvent() {
  while (Serial.available()) {
    //Serial.println("Recibiendo datos...");
    // lee los datos y los guarda en la tabla
    char inChar = (char)Serial.read();
    // los datos se agregan a la variable dataString
    dataString += inChar;
    // cuando recibe el salto de linea detiene la lectura
    if (inChar == '\n') {
      dataComplete = true;
    }
  }
}
//----------------------------------------------------------------------------------------

// Control de pasos y direccion de motor 28BYJ-48----------------------------------------
void stepper()  //Avanza un paso
{
  digitalWrite(IN1, Paso[Steps][0]);
  digitalWrite(IN2, Paso[Steps][1]);
  digitalWrite(IN3, Paso[Steps][2]);
  digitalWrite(IN4, Paso[Steps][3]);

  SetDirection();
}
void SetDirection() {
  if (Direction)
    Steps++;
  else
    Steps--;

  Steps = (Steps + 8) % 8;
}
void moverpinza(float q4) {
  // este motor posee una resolucion de paso de 2048 pasos por revolucion
  // por configuracion a 1/2 paso aumenta a 4096
  if (q4 < 0) {
    Direction = false;
    q4 = q4 * -1;
  } else {
    Direction = true;
  }
  pasosq4 = q4 * (4096 / 360);
  while (pasosq4 > 0) {
    stepper();  // Avanza un paso
    pasosq4--;  // Un paso menos
    delayMicroseconds(1200);
  }
}
//---------------------------------------------------------------------------------------------
void modohome() {
  // se deshabilitan las interrupciones para este modo
  // nueva asignacion de valores para las variables q1,q2,q3,q4
  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);

  q1 = 360;
  q2 = -360;
  q3 = 210;

  pasosq1 = (q1 * (3200 / 360.00)) * torqueq1;
  pasosq2 = (q2 * (3200 / 360.00)) * torqueq2;
  pasosq3 = -q3 * (3200 / 8.00);

  stepperX.move(pasosq1);
  steppery.move(pasosq2);
  stepperz.move(pasosq3);

  while (digitalRead(X_Stop_PIN) || digitalRead(Y_Stop_PIN) || digitalRead(Z_stop_PIN))
  {
    while (digitalRead(Z_stop_PIN))
    {
      stepperz.run();
      if (digitalRead(Z_stop_PIN) == 0)
      {
        stepperz.stop();
        break;
      }
    }
    while (digitalRead(X_Stop_PIN))
    {
      stepperX.run();
      if (digitalRead(X_Stop_PIN) == 0)
      {
        stepperX.stop();
        break;
      }
    }
    while (digitalRead(Y_Stop_PIN))
    {
      steppery.run();
      if (digitalRead(Y_Stop_PIN) == 0)
      {
        steppery.stop();
        break;
      }
    }
    /*  
    if (digitalRead(X_Stop_PIN))
      stepperX.run();
    else
     stepperX.stop();

    if (digitalRead(Y_Stop_PIN))
      steppery.run();
    else
     steppery.stop();
    */ 
  }

  stepperX.stop();
  steppery.stop();
  stepperz.stop();

  stepperX.setCurrentPosition(stepperX.currentPosition()); 
  steppery.setCurrentPosition(steppery.currentPosition());
  stepperz.setCurrentPosition(stepperz.currentPosition());

  delay(2000);

  q1 = -134;
  q2 = 136;
  q3 = -106;

  pasosq1 = (q1 * (3200 / 360.00)) * torqueq1;
  pasosq2 = (q2 * (3200 / 360.00)) * torqueq2;
  pasosq3 = -q3 * (3200 / 8.00);

  stepperX.move(pasosq1);
  steppery.move(pasosq2);
  stepperz.move(pasosq3);

  while (stepperX.distanceToGo() != 0 || steppery.distanceToGo() != 0 || stepperz.distanceToGo() != 0) {  // verificacion de que el motor se ha movido los pasos indicados de lo contrario puede seguir moviendose
    //stepperX.run();
    //steppery.run();
    //stepperz.run();
    while (steppery.distanceToGo() != 0)
    {
      steppery.run();
      if (steppery.distanceToGo() == 0)
      {
        steppery.stop();
        break;
      }
    }
    while (stepperz.distanceToGo() != 0)
    {
      stepperz.run();
      if (stepperz.distanceToGo() == 0)
      {
        stepperz.stop();
        break;
      }
    }
    while (stepperX.distanceToGo() != 0)
    {
      stepperX.run();
      if (stepperX.distanceToGo() == 0)
      {
        stepperX.stop();
        break;
      }
    }

  }

  stepperX.stop();
  steppery.stop();
  stepperz.stop();

  digitalWrite(X_ENABLE_PIN, HIGH);
  digitalWrite(Y_ENABLE_PIN, HIGH);
  digitalWrite(Z_ENABLE_PIN, HIGH);

  delay(10);
  
  q4 = 360;
  Direction = true;
  pasosq4 = q4 * (4096 / 360);
  
  while (digitalRead(pinza_stop_PIN)) {
    stepper();  // Avanza un paso
    pasosq4--;  // Un paso menos
    delayMicroseconds(1200);
  }

  q4 = 270;
  Direction = false;
  pasosq4 = q4 * (4096 / 360);
  
  while (pasosq4 > 0) {
    stepper();  // Avanza un paso
    pasosq4--;  // Un paso menos
    delayMicroseconds(1200);
  }

  q1 = 0;
  q2 = 0;
  q3 = 0;
  q4 = 0;
}

// interrupciones para finales de carrera de motor q1 y q2------------------------------------
void detenerx() {
  //int signo = (pasosq1 >= 0) ? -1 : 1;
  stepperX.stop();
  stepperX.setCurrentPosition(stepperX.currentPosition());
  stepperX.move(10 * -torqueq1 );
  stepperX.run();
  Serial.println("presionado x");
}
void detenery() {
  //int signo = (pasosq2 >= 0) ? -1 : 1;
  steppery.stop();
  steppery.setCurrentPosition(stepperz.currentPosition());
  steppery.move(10 * torqueq2);
  steppery.run();
  Serial.println("presionado y");
}
void detenerz() {
  //int signo = (pasosq3 >= 0) ? -1 : 1;
  stepperz.stop();
  stepperz.setCurrentPosition(stepperz.currentPosition());
  stepperz.move(250);
  stepperz.run();
  Serial.println("presionado z");
}

void detenerpinza() {
  Direction = false;
  //Serial.println("activado final de carrera");
  // verificar que se devuelva el motor de la pinza 
  pasosq4 = 114;
  while (pasosq4 > 0) {
    stepper();  // Avanza un paso
    pasosq4--;  // Un paso menos
    delayMicroseconds(800);
  }
  Serial.println("presionado p");
}
//-----------------------------------------------------------------------------------------------
