"""
 Copyright (c) 2020 Alan Yorinks All rights reserved.

 This program is free software; you can redistribute it and/or
 modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
 Version 3 as published by the Free Software Foundation; either
 or (at your option) any later version.
 This library is distributed in the hope that it will be useful,f
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

 You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
 along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

 DHT support courtesy of Martyn Wheeler
 Based on the DHTNew library - https://github.com/RobTillaart/DHTNew
"""

import time
from telemetrix import telemetrix

"""
Python version of Arduino Sweep example.
Moves a servo between 0, 90, and 180 degrees, printing the position.
"""

SERVO_PIN = 9

board = telemetrix.Telemetrix()
board.set_pin_mode_servo(SERVO_PIN, 100, 3000)
time.sleep(0.2)

try:
    while True:
        angle_input = input("Enter servo angle (0-180) or 'q' to quit: ")
        if angle_input.lower() == 'q':
            break
        try:
            angle = int(angle_input)
            if -900 <= angle <= 900:
                print(f"Moving to {angle}")
                board.servo_write(SERVO_PIN, angle)
            else:
                print("Please enter a value between 0 and 180.")
        except ValueError:
            print("Invalid input. Please enter a number between 0 and 180 or 'q' to quit.")
        time.sleep(1)
except KeyboardInterrupt:
    pass

board.servo_detach(SERVO_PIN)
time.sleep(0.2)
board.shutdown()
