from flask import Flask, jsonify, request
from telemetrix import telemetrix
import threading
import time

# Definições de pinos
TRIGGER_PIN = 10
ECHO_PIN = 11
SERVO_PIN = 9
DEBUG_LED_PIN = 13

# App Flask
app = Flask(__name__)

# Locks e estados globais
distance_lock = threading.Lock()
setpoint_lock = threading.Lock()
pid_lock = threading.Lock()
latest_distance = 0
setpoint = 15
pid_params = {"kp": 1.0, "ki": 0.0, "kd": 0.0}


def sonar_callback(data):
    global latest_distance
    with distance_lock:
        latest_distance = data[2]


class BallBeamController:
    def __init__(self):
        self.board = None
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        self.running = True
        # Filtro para leitura do sensor
        self.filtered_distance = 0.0
        self.filter_initialized = False

    def _initialize_board(self):
        # Desliga a placa anterior se necessário
        if self.board:
            try:
                self.board.shutdown()
                print("[INFO] Shutdown da placa anterior.")
            except Exception:
                print("[WARN] Falha ao desligar placa anterior.")
            time.sleep(1)

        # Tenta criar nova instância
        self.board = telemetrix.Telemetrix()
        self.board.set_pin_mode_sonar(TRIGGER_PIN, ECHO_PIN, sonar_callback)
        self.board.set_pin_mode_servo(SERVO_PIN, 100, 3000)
        print("[INFO] Placa (re)inicializada.")

        # Reseta estado PID
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()

    def start(self):
        try:
            self._initialize_board()
        except Exception as e:
            print(f"[ERROR] Falha na inicialização inicial: {e}")
            return

        while self.running:
            try:
                self.control_loop()
            except Exception as e:
                print(f"[WARN] Falha no loop de controle: {e}")
                time.sleep(2)
                try:
                    self._initialize_board()
                except Exception as e:
                    print(f"[ERROR] Falha na tentativa de reconexão: {e}")
                    continue
            time.sleep(0.1)

    def control_loop(self):
        global latest_distance, setpoint, pid_params

        with distance_lock:
            current_distance = max(2, min(65, latest_distance))
            print(f"Raw: {current_distance:.1f}")
        with setpoint_lock:
            current_setpoint = setpoint
        with pid_lock:
            kp = pid_params["kp"]
            ki = pid_params["ki"]
            kd = pid_params["kd"]

        error = current_distance - current_setpoint
        now = time.time()
        dt = now - self.last_time if self.last_time else 0.01
        self.integral += error * dt
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        output = kp * error + ki * self.integral + kd * derivative
        #
        # Controle do ângulo do servo:
        # - Ângulo < 135: bola se distancia do sensor (distância diminui)
        # - Ângulo > 135: bola se aproxima do sensor (distância aumenta)
        # O cálculo abaixo garante esse comportamento:
        angle = int(max(90, min(180, 135 + output)))

        print(angle);

        self.board.servo_write(SERVO_PIN, angle)


        self.last_error = error
        self.last_time = now


# Instancia o controlador
controller = BallBeamController()
controller_thread = threading.Thread(target=controller.start, daemon=True)
controller_thread.start()

# Rotas Flask
@app.route('/distance')
def get_distance():
    # Retorna o valor filtrado da distância
    d = controller.filtered_distance if hasattr(controller, "filtered_distance") else latest_distance
    return jsonify({'distance': d})


@app.route('/status')
def get_status():
    # Retorna o valor filtrado da distância
    d = controller.filtered_distance if hasattr(controller, "filtered_distance") else latest_distance
    with setpoint_lock:
        s = setpoint
    with pid_lock:
        p = pid_params.copy()
    error = d - s
    return jsonify({
        'distance': d,
        'setpoint': s,
        'kp': p['kp'],
        'ki': p['ki'],
        'kd': p['kd'],
        'error': error,
    })


@app.route('/setpoint', methods=['POST'])
def set_setpoint():
    data = request.get_json()
    if not data or 'setpoint' not in data:
        return jsonify({'error': 'setpoint not provided'}), 400
    try:
        new_value = float(data['setpoint'])
    except Exception:
        return jsonify({'error': 'invalid setpoint value'}), 400
    global setpoint
    with setpoint_lock:
        setpoint = new_value
    return jsonify({'setpoint': setpoint}), 200


@app.route('/pid', methods=['POST'])
def set_pid():
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
        pid_params.update({"kp": kp, "ki": ki, "kd": kd})
    return jsonify({'kp': kp, 'ki': ki, 'kd': kd}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
