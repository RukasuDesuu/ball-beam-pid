#ball-beam-pid/telemetrix_backend.py
from flask import Flask, jsonify
from telemetrix import telemetrix
import threading
import time

TRIGGER_PIN = 10
ECHO_PIN = 11

app = Flask(__name__)
distance_lock = threading.Lock()
latest_distance = 0

setpoint_lock = threading.Lock()
setpoint = 15  # valor inicial do setpoint

pid_lock = threading.Lock()
pid_params = {"kp": 1.0, "ki": 0.0, "kd": 0.0}

def sonar_callback(data):
    global latest_distance
    with distance_lock:
        latest_distance = data[2]

def telemetrix_thread():
    board = telemetrix.Telemetrix()
    board.set_pin_mode_sonar(TRIGGER_PIN, ECHO_PIN, sonar_callback)
    SERVO_PIN = 9
    board.set_pin_mode_servo(SERVO_PIN)
    # PID state
    integral = 0.0
    last_error = 0.0
    last_time = time.time()
    try:
        while True:
            # Leitura atual
            with distance_lock:
                current_distance = latest_distance
            with setpoint_lock:
                current_setpoint = setpoint
            with pid_lock:
                kp = pid_params["kp"]
                ki = pid_params["ki"]
                kd = pid_params["kd"]
            # PID cálculo
            error = current_setpoint - current_distance
            now = time.time()
            dt = now - last_time if last_time else 0.01
            integral += error * dt
            derivative = (error - last_error) / dt if dt > 0 else 0.0
            output = kp * error + ki * integral + kd * derivative
            # Saturação do sinal de controle para ângulo do servo (0-180)
            servo_angle = int(max(0, min(180, 90 + output)))
            board.servo_write(SERVO_PIN, servo_angle)
            # Atualiza estado PID
            last_error = error
            last_time = now
            time.sleep(0.05)
    finally:
        board.shutdown()

@app.route('/distance')
def get_distance():
    with distance_lock:
        current_distance = latest_distance
    return jsonify({'distance': current_distance})

@app.route('/status')
def get_status():
    with distance_lock:
        current_distance = latest_distance
    with setpoint_lock:
        current_setpoint = setpoint
    with pid_lock:
        current_pid = pid_params.copy()
    # Calcula erro e sinal de controle aproximados (para exibição)
    error = current_setpoint - current_distance
    # O sinal de controle (output) é calculado no loop PID, mas aqui vamos replicar o cálculo para exibir
    # Para manter consistência, você pode compartilhar o valor real via variável global se desejar
    # Aqui, apenas para exibição:
    kp = current_pid["kp"]
    ki = current_pid["ki"]
    kd = current_pid["kd"]
    # Para evitar inconsistência, não acumulamos integral/derivada aqui, apenas mostramos o erro e PID
    return jsonify({
        'distance': current_distance,
        'setpoint': current_setpoint,
        'kp': kp,
        'ki': ki,
        'kd': kd,
        'error': error,
        # 'output': output, # Se quiser, pode compartilhar o valor real do output do loop PID via variável global
    })

@app.route('/setpoint', methods=['POST'])
def set_setpoint():
    from flask import request
    data = request.get_json()
    if not data or 'setpoint' not in data:
        return jsonify({'error': 'setpoint not provided'}), 400
    try:
        new_setpoint = float(data['setpoint'])
    except Exception:
        return jsonify({'error': 'invalid setpoint value'}), 400
    global setpoint
    with setpoint_lock:
        setpoint = new_setpoint
    return jsonify({'setpoint': setpoint}), 200

@app.route('/pid', methods=['POST'])
def set_pid():
    from flask import request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    try:
        kp = float(data.get('kp', pid_params["kp"]))
        ki = float(data.get('ki', pid_params["ki"]))
        kd = float(data.get('kd', pid_params["kd"]))
    except Exception:
        return jsonify({'error': 'Invalid PID values'}), 400
    with pid_lock:
        pid_params["kp"] = kp
        pid_params["ki"] = ki
        pid_params["kd"] = kd
    return jsonify({'kp': kp, 'ki': ki, 'kd': kd}), 200

if __name__ == '__main__':
    t = threading.Thread(target=telemetrix_thread, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=5000)
