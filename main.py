import pyfirmata
import time

# Ajuste conforme sua porta serial
PORTA_SERIAL = '/dev/ttyACM0'  # Linux/Mac
# PORTA_SERIAL = 'COM3'        # Windows

board = pyfirmata.Arduino(PORTA_SERIAL)

# Exemplo: Controlar LED no pino 13
led_pin = board.get_pin('d:13:o')

# Exemplo: Ler um sensor analógico (A0)
sensor = board.get_pin('a:0:i')

# Inicializa um iterator para leitura contínua
it = pyfirmata.util.Iterator(board)
it.start()

try:
    while True:
        led_pin.write(1)  # Liga LED
        time.sleep(1)
        led_pin.write(0)  # Desliga LED
        time.sleep(1)

        leitura_sensor = sensor.read()
        if leitura_sensor:
            print(f"Sensor leitura: {leitura_sensor:.3f}")

except KeyboardInterrupt:
    board.exit()
