#include <AccelStepper.h>
#include <SoftwareSerial.h>

// Definir los pines de control
const int pinPasoX = 2;
const int pinDireccionX = 5;
const int pinPasoY = 3;
const int pinDireccionY = 6;

// Crear objetos AccelStepper para los motores X e Y
AccelStepper motorX(AccelStepper::DRIVER, pinPasoX, pinDireccionX);
AccelStepper motorY(AccelStepper::DRIVER, pinPasoY, pinDireccionY);

// Definir el módulo Bluetooth
SoftwareSerial bluetoothSerial(0, 1); // RX, TX

// Variables para la posición cero y las posiciones máximas
long posicionCeroX = 0;
long posicionCeroY = 0;
long posicionMaximaX = 0;
long posicionMaximaY = 0;

// Flags que indican si se han declarado límites con 'M'
bool limitesXEstablecidos = false;
bool limitesYEstablecidos = false;

// Variables para la velocidad de los motores
int velocidadX = 1000;
int velocidadY = 1000;

// Funciones auxiliares para validar límites
bool dentroLimiteX(long objetivo) {
  if (!limitesXEstablecidos) return true; // si no hay límites, permitir
  return (objetivo >= posicionCeroX && objetivo <= posicionMaximaX);
}

bool dentroLimiteY(long objetivo) {
  if (!limitesYEstablecidos) return true;
  return (objetivo >= posicionCeroY && objetivo <= posicionMaximaY);
}

void setup() {
  // Inicializar los motores
  motorX.setMaxSpeed(velocidadX);
  motorX.setAcceleration(500);
  motorY.setMaxSpeed(velocidadY);
  motorY.setAcceleration(500);

  // Inicializar el módulo Bluetooth
  bluetoothSerial.begin(9600);
}

void loop() {
  // Leer comandos del módulo Bluetooth
  if (bluetoothSerial.available() > 0) {
    char comando = bluetoothSerial.read();
    switch (comando) {
      case 'F': { // Mover motor X hacia adelante
        long objetivo = motorX.currentPosition() + 200;
        if (dentroLimiteX(objetivo)) {
          motorX.moveTo(objetivo);
        } else {
          bluetoothSerial.println("Movimiento X fuera de límites");
        }
        break;
      }
      case 'B': { // Mover motor X hacia atrás
        long objetivo = motorX.currentPosition() - 200;
        if (dentroLimiteX(objetivo)) {
          motorX.moveTo(objetivo);
        } else {
          bluetoothSerial.println("Movimiento X fuera de límites");
        }
        break;
      }
      case 'R': { // Mover motor Y hacia la derecha
        long objetivo = motorY.currentPosition() + 200;
        if (dentroLimiteY(objetivo)) {
          motorY.moveTo(objetivo);
        } else {
          bluetoothSerial.println("Movimiento Y fuera de límites");
        }
        break;
      }
      case 'L': { // Mover motor Y hacia la izquierda
        long objetivo = motorY.currentPosition() - 200;
        if (dentroLimiteY(objetivo)) {
          motorY.moveTo(objetivo);
        } else {
          bluetoothSerial.println("Movimiento Y fuera de límites");
        }
        break;
      }
      case 'Z': // Declarar posición cero
        if (bluetoothSerial.available() > 0) {
          String posicion = bluetoothSerial.readStringUntil('\n');
          posicionCeroX = posicion.substring(0, posicion.indexOf(',')).toInt();
          posicionCeroY = posicion.substring(posicion.indexOf(',') + 1).toInt();
          motorX.setCurrentPosition(posicionCeroX);
          motorY.setCurrentPosition(posicionCeroY);
        }
        break;
      case 'M': // Declarar posiciones máximas
        if (bluetoothSerial.available() > 0) {
          String posicion = bluetoothSerial.readStringUntil('\n');
          posicionMaximaX = posicion.substring(0, posicion.indexOf(',')).toInt();
          posicionMaximaY = posicion.substring(posicion.indexOf(',') + 1).toInt();
          limitesXEstablecidos = true;
          limitesYEstablecidos = true;
        }
        break;
      case 'P': { // Leer posición actual
        long posicionX = motorX.currentPosition();
        long posicionY = motorY.currentPosition();
        bool dentroX = !limitesXEstablecidos || (posicionX >= posicionCeroX && posicionX <= posicionMaximaX);
        bool dentroY = !limitesYEstablecidos || (posicionY >= posicionCeroY && posicionY <= posicionMaximaY);
        if (dentroX && dentroY) {
          String posicion = String(posicionX) + "," + String(posicionY);
          bluetoothSerial.println(posicion);
        } else {
          bluetoothSerial.println("Posición fuera de límites");
        }
        break;
      }
      case '+': // Aumentar velocidad
        velocidadX += 100;
        velocidadY += 100;
        motorX.setMaxSpeed(velocidadX);
        motorY.setMaxSpeed(velocidadY);
        break;
      case '-': // Disminuir velocidad
        velocidadX -= 100;
        velocidadY -= 100;
        if (velocidadX < 100) velocidadX = 100;
        if (velocidadY < 100) velocidadY = 100;
        motorX.setMaxSpeed(velocidadX);
        motorY.setMaxSpeed(velocidadY);
        break;
    }
  }

  // Actualizar la posición de los motores
  motorX.run();
  motorY.run();
}
