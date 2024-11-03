from machine import Pin, PWM, SoftI2C, ADC
import time
import ssd1306
import random

# Configuración del LED RGB
led_r = PWM(Pin(15), freq=1000)  # Pin para rojo
led_g = PWM(Pin(2), freq=1000)   # Pin para verde
led_b = PWM(Pin(4), freq=1000)   # Pin para azul

# Configuración del Joystick
joystick_x = ADC(Pin(32))  # Pin VRx del joystick
joystick_x.atten(ADC.ATTN_11DB)  # Rango completo: 3.3v
joystick_button = Pin(27, Pin.IN, Pin.PULL_UP)  # Pin del botón del joystick

# Configuración del buzzer
buzzer = PWM(Pin(13), freq=1000)
buzzer.duty(0)  # Aseguramos que el buzzer esté apagado al inicio

# Configuración de la pantalla OLED en I2C
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Variables globales
secuencia = []       # Secuencia de colores que el usuario debe recordar
input_secuencia = [] # Secuencia que el usuario introduce
puntaje = 0          # Puntaje del usuario
game_over = False    # Estado del juego

# Constantes de tiempo (en segundos)
TIEMPO_MOSTRAR_COLOR = 2.0
TIEMPO_ENTRE_COLORES = 1.0
TIEMPO_ESPERA_INPUT = 0.3
TIEMPO_PRESIONAR = 0.5
TIEMPO_NUEVA_RONDA = 2.0

# Constantes para el joystick
UMBRAL_JOYSTICK = 1000  # Valor para detectar movimiento del joystick
VALOR_MEDIO = 2048      # Valor medio del ADC (0-4095)

def color(r, g, b):
    """Configura el color del LED RGB."""
    led_r.duty(r)
    led_g.duty(g)
    led_b.duty(b)

def apagar_led():
    """Apaga el LED RGB."""
    color(0, 0, 0)

def mostrar_mensaje_inicio_secuencia():
    """Muestra mensaje de inicio de secuencia en la pantalla OLED."""
    oled.fill(0)
    oled.text("Observa la", 0, 0)
    oled.text("secuencia...", 0, 10)
    oled.show()
    time.sleep(1.5)

def mostrar_mensaje_tu_turno():
    """Muestra mensaje de turno del jugador en la pantalla OLED."""
    oled.fill(0)
    oled.text("Tu turno!", 0, 0)
    oled.text("Der: Rojo", 0, 20)
    oled.text("Izq: Verde", 0, 30)
    oled.text("Presionar: Azul", 0, 40)
    oled.text("Puntaje: {}".format(puntaje), 0, 50)
    oled.show()

def mostrar_secuencia(secuencia):
    """Muestra la secuencia de colores en el LED RGB."""
    mostrar_mensaje_inicio_secuencia()
    
    for color_code in secuencia:
        if color_code == 1:
            color(1023, 0, 0)  # Rojo
        elif color_code == 2:
            color(0, 1023, 0)  # Verde
        elif color_code == 3:
            color(0, 0, 1023)  # Azul
        time.sleep(TIEMPO_MOSTRAR_COLOR)
        apagar_led()
        time.sleep(TIEMPO_ENTRE_COLORES)
    
    mostrar_mensaje_tu_turno()

def leer_joystick():
    """Lee el estado del joystick y retorna el código del color seleccionado o Ninguno."""
    x_val = joystick_x.read()
    button_val = joystick_button.value()
    
    # Debounce para el botón
    if button_val == 0:  # Botón presionado (PULL_UP)
        time.sleep(0.05)
        if joystick_button.value() == 0:
            return 3  # Azul
    
    # Verificar posición del joystick
    if x_val > VALOR_MEDIO + UMBRAL_JOYSTICK:  # Derecha
        time.sleep(0.05)
        if joystick_x.read() > VALOR_MEDIO + UMBRAL_JOYSTICK:
            return 1  # Rojo
    elif x_val < VALOR_MEDIO - UMBRAL_JOYSTICK:  # Izquierda
        time.sleep(0.05)
        if joystick_x.read() < VALOR_MEDIO - UMBRAL_JOYSTICK:
            return 2  # Verde
    
    return None

def agregar_color():
    """Agrega un color aleatorio a la secuencia."""
    secuencia.append(random.randint(1, 3))

def verificar_respuesta():
    """Verifica si la secuencia del usuario es correcta."""
    global puntaje, game_over
    if input_secuencia == secuencia:
        puntaje += 1
        oled.fill(0)
        oled.text("¡Correcto!", 0, 0)
        oled.text("Puntaje: {}".format(puntaje), 0, 20)
        oled.show()
        input_secuencia.clear()
        time.sleep(1.5)
    else:
        game_over = True
        sonar_buzzer()
        oled.fill(0)
        oled.text("Game Over", 0, 0)
        oled.text("Puntaje: {}".format(puntaje), 0, 20)
        oled.text("Presiona para", 0, 40)
        oled.text("reiniciar", 0, 50)
        oled.show()
        time.sleep(2)

def sonar_buzzer():
    """Emite un sonido de error con el buzzer."""
    buzzer.duty(512)
    time.sleep(0.5)
    buzzer.duty(0)

def reset_game():
    """Reinicia el juego a su estado inicial."""
    global secuencia, input_secuencia, puntaje, game_over
    secuencia = []
    input_secuencia = []
    puntaje = 0
    game_over = False
    buzzer.duty(0)
    apagar_led()
    oled.fill(0)
    oled.text("Nuevo Juego", 0, 0)
    oled.text("Der: Rojo", 0, 20)
    oled.text("Izq: Verde", 0, 30)
    oled.text("Presionar: Azul", 0, 40)
    oled.show()
    time.sleep(2)

# Inicialización y bucle principal
try:
    reset_game()
    agregar_color()

    while True:
        if not game_over:
            mostrar_secuencia(secuencia)
            
            # Espera la entrada del usuario
            while len(input_secuencia) < len(secuencia) and not game_over:
                joystick_valor = leer_joystick()
                
                if joystick_valor is not None:
                    input_secuencia.append(joystick_valor)
                    
                    # Muestra el color correspondiente
                    if joystick_valor == 1:
                        color(1023, 0, 0)  # Rojo
                    elif joystick_valor == 2:
                        color(0, 1023, 0)  # Verde
                    elif joystick_valor == 3:
                        color(0, 0, 1023)  # Azul
                    
                    time.sleep(TIEMPO_PRESIONAR)
                    apagar_led()
                
                time.sleep(TIEMPO_ESPERA_INPUT)
            
            verificar_respuesta()
            
            if not game_over:
                time.sleep(TIEMPO_NUEVA_RONDA)
                agregar_color()
        else:
            # Espera a que el usuario presione el joystick para reiniciar
            if joystick_button.value() == 0:
                time.sleep(0.5)  # Debounce
                reset_game()
                agregar_color()
            time.sleep(TIEMPO_ESPERA_INPUT)

except Exception as e:
    print("Error:", e)
    buzzer.duty(0)
    apagar_led()