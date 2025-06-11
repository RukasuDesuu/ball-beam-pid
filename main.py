import streamlit as st
import pyfirmata
import time

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

    leitura_sensor = st.session_state.sensor.read()
    if leitura_sensor is not None:
        st.write(f"Leitura sensor analógico (A0): {leitura_sensor:.3f}")
    else:
        st.write("Aguardando leitura do sensor...")
