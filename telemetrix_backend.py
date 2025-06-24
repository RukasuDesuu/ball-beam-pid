#ball-beam-pid/telemetrix_backend.py
from flask import Flask, jsonify
from telemetrix import telemetrix
import threading
import time

# Setting HC-SR04 ports
TRIGGER_PIN = 10
ECHO_PIN = 11

# Setting Servo ports
SERVO_PIN = 9

# Setting Debug LED
DEBUG_LED_PIN = 13


# Setting Flask app
app = Flask(__name__)
distance_lock = threading.Lock()
latest_distance = 0

# Setting setpoint
setpoint_lock = threading.Lock()
setpoint = 15  # valor inicial do setpoint

# Setting PID parameters
pid_lock = threading.Lock()
pid_params = {"kp": 1.0, "ki": 0.0, "kd": 0.0} # valor inicial dos parametros PID

def sonar_callback(data):
    global latest_distance
    with distance_lock:
        latest_distance = data[2]

## Arduino Controlling
# control diagram:
#
#
# SetPoint----(-+)--->PID---->Servo----> Output (cm)
#              /\                   |
#              |                    |
#              ----------HC-SR04----
#
#
def telemetrix_thread():
    board = telemetrix.Telemetrix()
    board.set_pin_mode_sonar(TRIGGER_PIN, ECHO_PIN, sonar_callback)
    board.set_pin_mode_servo(SERVO_PIN)
    # PID state
    integral = 0.0
    last_error = 0.0
    last_time = time.time()
    try:
        while True:
            # Current distance
            with distance_lock:
                current_distance = latest_distance
            with setpoint_lock:
                current_setpoint = setpoint
            with pid_lock:
                kp = pid_params["kp"]
                ki = pid_params["ki"]
                kd = pid_params["kd"]
            # PID calculation
            error = current_setpoint - current_distance
            now = time.time()
            dt = now - last_time if last_time else 0.01
            integral += error * dt
            derivative = (error - last_error) / dt if dt > 0 else 0.0
            output = kp * error + ki * integral + kd * derivative
            # Servo angle saturation (0<=angle<=180)
            servo_angle = int(max(0, min(180, 90 + output)))
            board.servo_write(SERVO_PIN, servo_angle)
            # Atualiza estado PID
            last_error = error
            last_time = now
            time.sleep(0.05)
    finally:
        board.shutdown()

## API CONFIGURATIONS [distance, status, pid, setpoint]
# http://localhost:5000/distance
@app.route('/distance')
def get_distance():
    with distance_lock:
        current_distance = latest_distance
    return jsonify({'distance': current_distance})

# http://localhost:5000/status
@app.route('/status')
def get_status():
    with distance_lock:
        current_distance = latest_distance
    with setpoint_lock:
        current_setpoint = setpoint
    with pid_lock:
        current_pid = pid_params.copy()
    # Calculate error and approximate control signal (for display)
    error = current_setpoint - current_distance
    # The control signal (output) is calculated in the PID loop, but here we replicate the calculation for display
    # To maintain consistency, you can share the real value via a global variable if desired
    # only for exhibition:
    kp = current_pid["kp"]
    ki = current_pid["ki"]
    kd = current_pid["kd"]
    # To avoid inconsistency, we don't accumulate integral/derivative here, just show the error and PID
    return jsonify({
        'distance': current_distance,
        'setpoint': current_setpoint,
        'kp': kp,
        'ki': ki,
        'kd': kd,
        'error': error,
    })

# http://localhost:5000/setpoint
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

# http://localhost:5000/pid
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
