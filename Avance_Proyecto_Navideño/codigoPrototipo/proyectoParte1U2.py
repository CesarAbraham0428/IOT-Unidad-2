from machine import Pin, PWM
from time import sleep
import time
import _thread
from hcsr04 import HCSR04

# Configuración del motor paso a paso
IN1 = Pin(19, Pin.OUT)
IN2 = Pin(18, Pin.OUT)
IN3 = Pin(5, Pin.OUT)
IN4 = Pin(17, Pin.OUT)

sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Variable global para el estado del motor
motor_activado = True

# Función para mover el motor continuamente
def motor_pasos():
    global motor_activado
    while True:
        if motor_activado:
            for step in sequence:
                for i in range(4):
                    [IN1, IN2, IN3, IN4][i].value(step[i])
                sleep(0.002)
        else:
            for pin in [IN1, IN2, IN3, IN4]:
                pin.value(0)
            sleep(0.1)

# Configuración del sensor ultrasónico, LEDs y buzzer
sensor = HCSR04(trigger_pin=15, echo_pin=4)
ledR1 = Pin(26, Pin.OUT)
ledR2 = Pin(14, Pin.OUT)
buzzer = PWM(Pin(27))

# Frecuencias de las notas para el tema de Mario (Hz)
NOTAS = {
    'do4': 262, 'do#4': 277, 're4': 294, 're#4': 311,
    'mi4': 330, 'fa4': 349, 'fa#4': 370, 'sol4': 392,
    'sol#4': 415, 'la4': 440, 'la#4': 466, 'si4': 494,
    'do5': 523, 'silencio': 0
}

# Duraciones de las notas (ms)
DURACION = {
    'negra': 200, 'corchea': 100, 'semicorchea': 50,
    'sil': 30, 'silg': 500
}

def parpadear_leds():
    ledR1.value(not ledR1.value())
    ledR2.value(not ledR2.value())

def emitir_nota(frecuencia, duracion, volumen=512):
    try:
        if frecuencia == 0:
            buzzer.duty(0)
        else:
            buzzer.freq(frecuencia)
            buzzer.duty(volumen)
            parpadear_leds()
        time.sleep_ms(duracion)
    finally:
        buzzer.duty(0)
        time.sleep_ms(DURACION['sil'])

def tocar_tema_subterraneo():
    secuencia = [
        (NOTAS['do4'], DURACION['corchea']), (NOTAS['do5'], DURACION['corchea']),
        (NOTAS['la4'], DURACION['corchea']), (NOTAS['la4'], DURACION['corchea']),
        (NOTAS['la#4'], DURACION['corchea']), (NOTAS['la#4'], DURACION['corchea']),
        (NOTAS['la4'], DURACION['corchea']), (NOTAS['la4'], DURACION['corchea']),
        (NOTAS['sol4'], DURACION['corchea']), (NOTAS['sol4'], DURACION['corchea']),
        (NOTAS['fa4'], DURACION['corchea']), (NOTAS['fa4'], DURACION['corchea']),
        (NOTAS['sol4'], DURACION['corchea']), (NOTAS['silencio'], DURACION['corchea']),
        (NOTAS['do4'], DURACION['corchea']), (NOTAS['do4'], DURACION['corchea']),
    ]
    for nota, dur in secuencia:
        emitir_nota(nota, dur)
    time.sleep_ms(DURACION['silg'])

def tocar_en_loop(veces=2):
    try:
        for _ in range(veces):
            tocar_tema_subterraneo()
            time.sleep_ms(500)
    finally:
        buzzer.duty(0)
        ledR1.value(False)
        ledR2.value(False)

# Monitorear distancia y controlar motor y sonidos
def monitorear_distancia():
    global motor_activado
    
    while True:
        try:
            distancia = sensor.distance_cm()
            print(f"Distancia del Objeto: {distancia} cm")
            if distancia < 25:
                motor_activado = False
                tocar_en_loop()
                time.sleep(1)
            else:
                motor_activado = True
                buzzer.duty(0)
                ledR1.value(False)
                ledR2.value(False)
            sleep(0.1)
        except Exception as e:
            print("Error:", e)
            buzzer.duty(0)
            ledR1.value(False)
            ledR2.value(False)
            motor_activado = True
            sleep(0.1)

# Iniciar el motor en un hilo separado
_thread.start_new_thread(motor_pasos, ())

# Ejecutar la función de monitoreo de distancia en el hilo principal
monitorear_distancia()