import streamlit as st
import requests
import time

st.set_page_config(page_title="Ultrassônico com Telemetrix (API)", layout="centered")
st.title("Ultrassônico com Telemetrix + Streamlit (API)")

STATUS_URL = "http://localhost:5000/status"
SETPOINT_URL = "http://localhost:5000/setpoint"
PID_URL = "http://localhost:5000/pid"

distance = 0
setpoint = 0
kp = 1.0
ki = 0.0
kd = 0.0
error = 0.0
placeholder = st.empty()

# Inicializa widgets PID apenas na primeira renderização
if 'pid_loaded' not in st.session_state:
    try:
        resp = requests.get(STATUS_URL, timeout=2)
        if resp.ok:
            data = resp.json()
            st.session_state['kp_input'] = data.get('kp', 1.0)
            st.session_state['ki_input'] = data.get('ki', 0.0)
            st.session_state['kd_input'] = data.get('kd', 0.0)
        else:
            st.session_state['kp_input'] = 1.0
            st.session_state['ki_input'] = 0.0
            st.session_state['kd_input'] = 0.0
    except Exception:
        st.session_state['kp_input'] = 1.0
        st.session_state['ki_input'] = 0.0
        st.session_state['kd_input'] = 0.0
    st.session_state['pid_loaded'] = True

st.caption("Certifique-se de que o backend está rodando e o Arduino está conectado.")

refresh_rate = st.slider("Intervalo de atualização (segundos)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)

# Campo para ajuste do setpoint
setpoint_input = st.number_input("Setpoint (cm)", min_value=0.0, max_value=100.0, value=10.0, step=0.1, key="setpoint_input")
if st.button("Enviar Setpoint"):
    try:
        resp = requests.post(SETPOINT_URL, json={"setpoint": setpoint_input}, timeout=2)
        if resp.ok:
            st.success(f"Setpoint atualizado para {setpoint_input} cm")
        else:
            st.error("Erro ao atualizar o setpoint.")
    except Exception as e:
        st.error(f"Erro ao conectar ao backend: {e}")

# Campos para ajuste dos parâmetros PID
st.subheader("Parâmetros PID")
col1, col2, col3 = st.columns(3)
with col1:
    kp_input = st.number_input("Kp", min_value=0.0, max_value=100.0, value=st.session_state['kp_input'], step=0.01, key="kp_input")
with col2:
    ki_input = st.number_input("Ki", min_value=0.0, max_value=100.0, value=st.session_state['ki_input'], step=0.01, key="ki_input")
with col3:
    kd_input = st.number_input("Kd", min_value=0.0, max_value=100.0, value=st.session_state['kd_input'], step=0.01, key="kd_input")

if st.button("Enviar PID"):
    try:
        resp = requests.post(PID_URL, json={"kp": kp_input, "ki": ki_input, "kd": kd_input}, timeout=2)
        if resp.ok:
            st.success(f"PID atualizado: Kp={kp_input}, Ki={ki_input}, Kd={kd_input}")
        else:
            st.error("Erro ao atualizar os parâmetros PID.")
    except Exception as e:
        st.error(f"Erro ao conectar ao backend: {e}")

run = st.checkbox("Iniciar leitura", value=True)

while run:
    try:
        resp = requests.get(STATUS_URL, timeout=2)
        if resp.ok:
            data = resp.json()
            distance = data.get('distance', 0)
            setpoint = data.get('setpoint', 0)
            kp = data.get('kp', 1.0)
            ki = data.get('ki', 0.0)
            kd = data.get('kd', 0.0)
            error = data.get('error', 0.0)
            placeholder.metric("Distância (cm)", distance, delta=f"Setpoint: {setpoint}")
            st.write(f"Erro: {error:.2f} cm")
            st.write(f"Kp: {kp} | Ki: {ki} | Kd: {kd}")
        else:
            placeholder.error("Erro ao consultar o backend.")
    except Exception as e:
        placeholder.error(f"Erro ao conectar ao backend: {e}")
    time.sleep(refresh_rate)
    run = st.session_state.get('Iniciar leitura', True)
