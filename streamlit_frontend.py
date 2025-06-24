import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="BALL-BEAM PID", layout="centered", page_icon="⚙️")
st.title("🎯 BALL-BEAM Controller")
st.caption("Controle PID em tempo real com Arduino e Streamlit")

STATUS_URL = "http://localhost:5000/status"
SETPOINT_URL = "http://localhost:5000/setpoint"
PID_URL = "http://localhost:5000/pid"

# Inicialização
if 'pid_loaded' not in st.session_state:
    try:
        resp = requests.get(STATUS_URL, timeout=2).json()
        st.session_state['kp_input'] = resp.get('kp', 1.0)
        st.session_state['ki_input'] = resp.get('ki', 0.0)
        st.session_state['kd_input'] = resp.get('kd', 0.0)
    except:
        st.session_state['kp_input'] = 1.0
        st.session_state['ki_input'] = 0.0
        st.session_state['kd_input'] = 0.0
    st.session_state['pid_loaded'] = True

if 'log' not in st.session_state:
    st.session_state['log'] = []

def check_backend_status():
    try:
        requests.get("http://localhost:5000/status", timeout=1)
        return True
    except:
        return False

def render_backend_led(status):
    led = "🟢" if status else "🔴"
    msg = "Backend Online" if status else "Backend Offline"
    st.markdown(
        f"""
        <style>
        .backend-led-corner {{
            position: fixed;
            top: 5rem;
            right: 1.5rem;
            z-index: 9999;
        }}
        </style>
        <div class="backend-led-corner">
            <span style="background-color:{'#d4edda' if status else '#f8d7da'};
                         color:{'#155724' if status else '#721c24'};
                         padding:0.5rem 1rem;
                         border-radius:1rem;
                         font-weight:600;
                         display:inline-block;
                         box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                {led} {msg}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


tab1, tab2, tab3 = st.tabs(["🎯 Setpoint", "⚙️ PID", "📊 Monitoramento"])

with tab1:
    backend_ok = check_backend_status()
    render_backend_led(backend_ok)

    st.subheader("Ajuste de Setpoint")
    setpoint_input = st.slider("Setpoint (cm)", 0.0, 100.0, 15.0, 0.1)
    if st.button("📤 Enviar Setpoint"):
        try:
            requests.post(SETPOINT_URL, json={"setpoint": setpoint_input}, timeout=2)
            st.success(f"Setpoint atualizado para {setpoint_input} cm")
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")

with tab2:
    backend_ok = check_backend_status()
    render_backend_led(backend_ok)

    st.subheader("Configuração PID")
    col1, col2, col3 = st.columns(3)
    with col1:
        kp = st.number_input("Kp", 0.0, 100.0, st.session_state['kp_input'], 0.01)
    with col2:
        ki = st.number_input("Ki", 0.0, 100.0, st.session_state['ki_input'], 0.01)
    with col3:
        kd = st.number_input("Kd", 0.0, 100.0, st.session_state['kd_input'], 0.01)
    if st.button("📤 Enviar PID"):
        try:
            requests.post(PID_URL, json={"kp": kp, "ki": ki, "kd": kd}, timeout=2)
            st.success(f"PID atualizado: Kp={kp}, Ki={ki}, Kd={kd}")
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")

with tab3:
    backend_ok = check_backend_status()
    render_backend_led(backend_ok)

    st.subheader("Monitoramento em Tempo Real")
    refresh_rate = st.slider("🔄 Atualização (s)", 0.2, 2.0, 1.0, 0.1)
    run = st.toggle("Ativar Monitoramento", value=True)

    if run:
        st_autorefresh(interval=int(refresh_rate * 1000), key="auto_refresh")

        try:
            data = requests.get(STATUS_URL, timeout=2).json()

            # Salvar histórico no log
            st.session_state['log'].append({
                "timestamp": pd.Timestamp.now(),
                "distance": data['distance'],
                "setpoint": data['setpoint'],
                "error": data['error']
            })

            # Exibir métricas
            col1, col2 = st.columns(2)
            col1.metric("📏 Distância (cm)", f"{data['distance']:.2f}", f"Setpoint: {data['setpoint']}")
            col2.metric("❌ Erro (cm)", f"{data['error']:.2f}")

            with st.expander("🔧 PID atual"):
                st.write(f"Kp: {data['kp']}  \nKi: {data['ki']}  \nKd: {data['kd']}")

            # Gráfico
            df_log = pd.DataFrame(st.session_state['log']).set_index("timestamp")
            st.line_chart(df_log[["distance", "setpoint"]], use_container_width=True)

            # Download CSV
            csv = df_log.reset_index().to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV", data=csv, file_name="ball_beam_log.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Erro ao conectar: {e}")
