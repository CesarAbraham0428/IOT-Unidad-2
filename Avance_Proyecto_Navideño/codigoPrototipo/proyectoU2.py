from machine import Pin
from time import sleep
from servo import Servo
from hcsr04 import HCSR04  # Importa la librería del sensor ultrasónico

# Inicialización de los servos
ser = Servo(Pin(22))
ser2 = Servo(Pin(21))

# Configuración del sensor ultrasónico
sensor = HCSR04(trigger_pin=15, echo_pin=4)  # Ajusta los pines según tu conexión

# Bucle principal
while True:
    distancia = sensor.distance_cm()  # Obtiene la distancia en cm
    print("Distancia medida:", distancia, "cm")

    # Si la distancia es menor o igual a 15 cm, mueve los servos
    if distancia <= 15:
        ser.move(90)
        ser2.move(90)
        sleep(1)
        ser.move(0)
        ser2.move(0)
        sleep(1)
    else:
        sleep(0.1)  # Espera corta para la siguiente medición si no hay objeto cercano
