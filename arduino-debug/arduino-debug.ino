#include <Servo.h>

// Pin definitions
const int TRIGGER_PIN = 10;
const int ECHO_PIN = 11;
const int SERVO_PIN = 9;

// PID constants
const double Kp = 0.7;
const double Ki = 0.7;
const double Kd = 0.6;

// Control parameters
const double setpoint = 28.0; // Target distance in cm

// Servo object
Servo beam_servo;

// PID state variables
double integral = 0.0;
double last_error = 0.0;
unsigned long last_time = 0;

void setup() {
  Serial.begin(115200);

  // Initialize servo
  beam_servo.attach(SERVO_PIN);
  beam_servo.write(135); // Start at a neutral angle

  // Initialize sonar pins
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  last_time = millis();
  Serial.println("Arduino setup complete. Starting control loop.");
}

void loop() {
  // 1. Read distance from sonar
  double current_distance = read_distance();

  // 2. Calculate PID
  unsigned long now = millis();
  double dt = (double)(now - last_time) / 1000.0; // Time difference in seconds
  if (dt == 0) {
    // Avoid division by zero on the first loop or very fast loops
    delay(10); 
    return;
  }

  double error = current_distance - setpoint;
  integral += error * dt;
  double derivative = (error - last_error) / dt;
  double output = Kp * error + Ki * integral + Kd * derivative;

  // 3. Calculate servo angle
  // The base angle is 90. The output adjusts it.
  // Angle < 90: moves the ball away from the sensor
  // Angle > 90: brings the ball closer to the sensor
  int angle = 90 + output;
  angle = constrain(angle, 0, 180); // Limit angle to servo's safe range

  // 4. Command the servo
  beam_servo.write(angle);

  // 5. Update state for next iteration
  last_error = error;
  last_time = now;

  // 6. Print debug information
  Serial.print("Dist: ");
  Serial.print(current_distance, 1);
  Serial.print("cm, Err: ");
  Serial.print(error, 1);
  Serial.print(", Out: ");
  Serial.print(output, 1);
  Serial.print(", Angle: ");
  Serial.println(angle);

  // Control loop frequency
  delay(300);
}

// Function to read distance from HC-SR04 sonar
double read_distance() {
  // Send a 10us pulse to trigger the sensor
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  // Read the echo pin, which returns the sound wave travel time in microseconds
  long duration = pulseIn(ECHO_PIN, HIGH);

  // Calculate the distance in cm
  // Speed of sound = 343 m/s = 0.0343 cm/us
  // Distance = (travel time / 2) * speed of sound
  double distance = (duration * 0.0343) / 2.0;

  // Basic filtering for invalid readings
  if (distance <= 2 || distance >= 65) {
      // If out of range, return the last valid error's implied distance
      // to avoid sudden jumps. This is a simple way to handle noise.
      return setpoint + last_error;
  }

  return distance;
}
