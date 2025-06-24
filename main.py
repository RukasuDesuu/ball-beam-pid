import streamlit as st
import pyfirmata
import time

def getUltrassonic(trig, echo):
    pulse_start = None
    pulse_end = None

    trig.write(0)
    time.sleep(0.000002)  # 2 microseconds
    trig.write(1)
    time.sleep(0.000010)  # 10 microseconds
    trig.write(0)

    timeout = time.time() + 1  # 1-second timeout

    # Wait for echo to start
    while echo.read() == 0:
        if time.time() > timeout:
            return None
    pulse_start = time.time()

    # Wait for echo to end
    while echo.read() == 1:
        if time.time() > timeout:
            return None
    pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 0.0343 * 100, 2)  # convert to cm
    return distance


st.title("Controle Arduino com PyFirmata")

# Inicializa conexão persistente via session_state
if 'board' not in st.session_state:
    st.session_state.board = None

porta_serial = st.text_input("Porta serial", "/dev/ttyACM0")

# Botão conectar/desconectar
if st.session_state.board is None:
    if st.button("Conectar Arduino"):
        try:
            st.session_state.board = pyfirmata.Arduino(porta_serial)
            st.session_state.led = st.session_state.board.get_pin('d:13:o')
            st.session_state.sensor = st.session_state.board.get_pin('a:0:i')
            st.session_state.servo = st.session_state.board.get_pin('d:9:s')
            st.session_state.trig_pin = st.session_state.board.get_pin('d:10:o')
            st.session_state.echo_pin = st.session_state.board.get_pin('d:11:i')
            iterator = pyfirmata.util.Iterator(st.session_state.board)
            iterator.start()
            st.success("Arduino conectado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")
else:
    if st.button("Desconectar Arduino"):
        st.session_state.board.exit()
        st.session_state.board = None
        st.success("Arduino desconectado com sucesso!")

# Interface de controle
if st.session_state.board:
    if st.button("Ligar LED"):
        st.session_state.led.write(1)
    if st.button("Desligar LED"):
        st.session_state.led.write(0)
    servo_angle = st.text_input("Ângulo do servo", value="90")
    if st.button("acionar servo"):
        st.session_state.board.digital[9].write(int(servo_angle))

    # Atualiza a leitura do sensor ultrassônico a cada 200ms
    placeholder = st.empty()
    while True:
        leitura_sensor = getUltrassonic(st.session_state.trig_pin, st.session_state.echo_pin)
        if leitura_sensor is not None:
            placeholder.write(f"Leitura sensor ultrassônico (A0): {leitura_sensor:.3f}")
        else:
            placeholder.write("Aguardando leitura do sensor...")
        time.sleep(0.2)
        st.rerun()
