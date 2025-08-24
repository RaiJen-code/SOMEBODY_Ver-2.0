#!/usr/bin/env python3
"""
SOMEBODY 4 Motor Control - Complete Version
Control 4 omni wheels with IBT_2 drivers
"""

import Jetson.GPIO as GPIO
import time
import threading

class SOMEBODY4MotorController:
    def __init__(self):
        # Cleanup any previous GPIO state
        GPIO.cleanup()
        
        # GPIO Mode
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Motor Pin Configuration
        self.motors = {
            'FL': {  # Front Left - TESTED WORKING!
                'RPWM': 11,  # Pin 11 (GPIO17)
                'LPWM': 13,  # Pin 13 (GPIO27)
                'speed_f': 0,
                'speed_r': 0
            },
            'FR': {  # Front Right
                'RPWM': 15,  # Pin 15 (GPIO22)
                'LPWM': 16,  # Pin 16 (GPIO23)
                'speed_f': 0,
                'speed_r': 0
            },
            'BR': {  # Back Right
                'RPWM': 18,  # Pin 18 (GPIO24)
                'LPWM': 22,  # Pin 22 (GPIO25)
                'speed_f': 0,
                'speed_r': 0
            },
            'BL': {  # Back Left
                'RPWM': 29,  # Pin 29 (GPIO5)
                'LPWM': 31,  # Pin 31 (GPIO6)
                'speed_f': 0,
                'speed_r': 0
            }
        }
        
        # PWM thread control
        self.pwm_running = True
        self.pwm_frequency = 100  # 100Hz software PWM
        
        # Initialize pins
        self._setup_pins()
        
        # Start PWM thread
        self.pwm_thread = threading.Thread(target=self._pwm_loop)
        self.pwm_thread.daemon = True
        self.pwm_thread.start()
        
        print("="*50)
        print("✅ SOMEBODY 4 MOTOR CONTROLLER READY!")
        print("="*50)
        print("Motors:")
        for name, motor in self.motors.items():
            print(f"  {name}: RPWM={motor['RPWM']}, LPWM={motor['LPWM']}")
        print("="*50)
        
    def _setup_pins(self):
        """Setup GPIO pins as output"""
        for motor_name, motor in self.motors.items():
            GPIO.setup(motor['RPWM'], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(motor['LPWM'], GPIO.OUT, initial=GPIO.LOW)
            print(f"✓ Motor {motor_name} initialized")
            
    def _pwm_loop(self):
        """Software PWM implementation"""
        period = 1.0 / self.pwm_frequency
        
        while self.pwm_running:
            start_time = time.time()
            
            # PWM on phase
            for motor_name, motor in self.motors.items():
                if motor['speed_f'] > 0:
                    GPIO.output(motor['RPWM'], GPIO.HIGH)
                if motor['speed_r'] > 0:
                    GPIO.output(motor['LPWM'], GPIO.HIGH)
                    
            # Duty cycle timing
            time.sleep(period * 0.01)
            
            # PWM off phase based on duty cycle
            for motor_name, motor in self.motors.items():
                current_duty = (time.time() - start_time) * 100 / period
                
                if current_duty > motor['speed_f']:
                    GPIO.output(motor['RPWM'], GPIO.LOW)
                if current_duty > motor['speed_r']:
                    GPIO.output(motor['LPWM'], GPIO.LOW)
                    
            # Complete period
            elapsed = time.time() - start_time
            if elapsed < period:
                time.sleep(period - elapsed)
                
    def set_motor_speed(self, motor_name, speed):
        """Set individual motor speed (-100 to 100)"""
        if motor_name not in self.motors:
            return
            
        motor = self.motors[motor_name]
        speed = max(-100, min(100, speed))
        
        if speed > 0:
            motor['speed_f'] = abs(speed)
            motor['speed_r'] = 0
        elif speed < 0:
            motor['speed_f'] = 0
            motor['speed_r'] = abs(speed)
        else:
            motor['speed_f'] = 0
            motor['speed_r'] = 0
            GPIO.output(motor['RPWM'], GPIO.LOW)
            GPIO.output(motor['LPWM'], GPIO.LOW)
            
    def stop_all(self):
        """Stop all motors"""
        for motor_name in self.motors:
            self.set_motor_speed(motor_name, 0)
        print("🛑 All motors stopped")
        
    def move_forward(self, speed=50):
        """Move robot forward"""
        print(f"⬆️ Moving FORWARD at speed {speed}")
        self.set_motor_speed('FL', speed)
        self.set_motor_speed('FR', speed)
        self.set_motor_speed('BL', speed)
        self.set_motor_speed('BR', speed)
        
    def move_backward(self, speed=50):
        """Move robot backward"""
        print(f"⬇️ Moving BACKWARD at speed {speed}")
        self.set_motor_speed('FL', -speed)
        self.set_motor_speed('FR', -speed)
        self.set_motor_speed('BL', -speed)
        self.set_motor_speed('BR', -speed)
        
    def turn_left(self, speed=50):
        """Turn robot left (tank turn)"""
        print(f"↰ Turning LEFT at speed {speed}")
        self.set_motor_speed('FL', -speed)
        self.set_motor_speed('FR', speed)
        self.set_motor_speed('BL', -speed)
        self.set_motor_speed('BR', speed)
        
    def turn_right(self, speed=50):
        """Turn robot right (tank turn)"""
        print(f"↱ Turning RIGHT at speed {speed}")
        self.set_motor_speed('FL', speed)
        self.set_motor_speed('FR', -speed)
        self.set_motor_speed('BL', speed)
        self.set_motor_speed('BR', -speed)
        
    def strafe_left(self, speed=50):
        """Strafe left (sideways) - omni movement"""
        print(f"← Strafing LEFT at speed {speed}")
        self.set_motor_speed('FL', -speed)
        self.set_motor_speed('FR', speed)
        self.set_motor_speed('BL', speed)
        self.set_motor_speed('BR', -speed)
        
    def strafe_right(self, speed=50):
        """Strafe right (sideways) - omni movement"""
        print(f"→ Strafing RIGHT at speed {speed}")
        self.set_motor_speed('FL', speed)
        self.set_motor_speed('FR', -speed)
        self.set_motor_speed('BL', -speed)
        self.set_motor_speed('BR', speed)
        
    def diagonal_forward_left(self, speed=50):
        """Move diagonal forward-left"""
        print(f"↖️ Moving DIAGONAL FL at speed {speed}")
        self.set_motor_speed('FL', 0)
        self.set_motor_speed('FR', speed)
        self.set_motor_speed('BL', speed)
        self.set_motor_speed('BR', 0)
        
    def diagonal_forward_right(self, speed=50):
        """Move diagonal forward-right"""
        print(f"↗️ Moving DIAGONAL FR at speed {speed}")
        self.set_motor_speed('FL', speed)
        self.set_motor_speed('FR', 0)
        self.set_motor_speed('BL', 0)
        self.set_motor_speed('BR', speed)
        
    def spin_clockwise(self, speed=50):
        """Spin in place clockwise"""
        print(f"🔄 Spinning CLOCKWISE at speed {speed}")
        self.set_motor_speed('FL', speed)
        self.set_motor_speed('FR', -speed)
        self.set_motor_speed('BL', speed)
        self.set_motor_speed('BR', -speed)
        
    def set_omni_movement(self, vx, vy, omega):
        """
        Advanced omni-directional movement
        vx: forward/backward (-100 to 100)
        vy: left/right (-100 to 100)
        omega: rotation (-100 to 100)
        """
        # Omni wheel kinematics
        fl = vx - vy - omega
        fr = vx + vy + omega
        bl = vx + vy - omega
        br = vx - vy + omega
        
        # Normalize
        max_val = max(abs(fl), abs(fr), abs(bl), abs(br))
        if max_val > 100:
            fl = (fl / max_val) * 100
            fr = (fr / max_val) * 100
            bl = (bl / max_val) * 100
            br = (br / max_val) * 100
            
        self.set_motor_speed('FL', fl)
        self.set_motor_speed('FR', fr)
        self.set_motor_speed('BL', bl)
        self.set_motor_speed('BR', br)
        
    def dance_demo(self):
        """Fun dance demonstration"""
        print("\n🕺 SOMEBODY DANCE MODE! 🕺")
        
        moves = [
            ("Forward", self.move_forward, 1),
            ("Backward", self.move_backward, 1),
            ("Spin Right", self.spin_clockwise, 2),
            ("Strafe Left", self.strafe_left, 1),
            ("Strafe Right", self.strafe_right, 1),
            ("Diagonal", lambda: self.diagonal_forward_left(40), 1),
            ("Spin Left", lambda: self.turn_left(60), 2),
        ]
        
        for name, action, duration in moves:
            print(f"\n🎵 {name}...")
            action()
            time.sleep(duration)
            
        self.stop_all()
        print("\n🎉 Dance complete!")
        
    def cleanup(self):
        """Cleanup GPIO"""
        self.pwm_running = False
        time.sleep(0.1)
        self.stop_all()
        GPIO.cleanup()
        print("✅ GPIO cleaned up")

# Test functions
def test_individual_motors(controller):
    """Test each motor individually"""
    print("\n🔧 TESTING INDIVIDUAL MOTORS")
    print("="*50)
    
    for motor in ['FL', 'FR', 'BL', 'BR']:
        print(f"\nTesting {motor} motor:")
        
        print(f"  {motor} Forward...")
        controller.set_motor_speed(motor, 50)
        time.sleep(1)
        
        print(f"  {motor} Reverse...")
        controller.set_motor_speed(motor, -50)
        time.sleep(1)
        
        controller.set_motor_speed(motor, 0)
        time.sleep(0.5)

def test_basic_movements(controller):
    """Test basic movement patterns"""
    print("\n🚗 TESTING BASIC MOVEMENTS")
    print("="*50)
    
    movements = [
        ("Forward", controller.move_forward),
        ("Backward", controller.move_backward),
        ("Turn Left", controller.turn_left),
        ("Turn Right", controller.turn_right),
        ("Strafe Left", controller.strafe_left),
        ("Strafe Right", controller.strafe_right),
    ]
    
    for name, action in movements:
        print(f"\nTesting: {name}")
        action(40)  # 40% speed
        time.sleep(2)
        controller.stop_all()
        time.sleep(0.5)

def manual_control(controller):
    """Manual control mode"""
    print("\n🎮 MANUAL CONTROL MODE")
    print("="*50)
    print("Commands:")
    print("  w/s     - Forward/Backward")
    print("  a/d     - Strafe Left/Right")
    print("  q/e     - Turn Left/Right")
    print("  z/c     - Diagonal FL/FR")
    print("  space   - Stop")
    print("  t       - Test all motors")
    print("  dance   - Dance demo")
    print("  x       - Exit")
    print("="*50)
    
    while True:
        cmd = input("\nCommand: ").lower().strip()
        
        if cmd == 'w':
            controller.move_forward(50)
        elif cmd == 's':
            controller.move_backward(50)
        elif cmd == 'a':
            controller.strafe_left(50)
        elif cmd == 'd':
            controller.strafe_right(50)
        elif cmd == 'q':
            controller.turn_left(50)
        elif cmd == 'e':
            controller.turn_right(50)
        elif cmd == 'z':
            controller.diagonal_forward_left(50)
        elif cmd == 'c':
            controller.diagonal_forward_right(50)
        elif cmd == ' ':
            controller.stop_all()
        elif cmd == 't':
            test_individual_motors(controller)
        elif cmd == 'dance':
            controller.dance_demo()
        elif cmd == 'x':
            break
        else:
            print("Invalid command!")

if __name__ == "__main__":
    import sys
    
    controller = SOMEBODY4MotorController()
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "test":
                test_individual_motors(controller)
                test_basic_movements(controller)
            elif sys.argv[1] == "manual":
                manual_control(controller)
            elif sys.argv[1] == "dance":
                controller.dance_demo()
        else:
            print("\nUsage:")
            print("  python3 jetson_4motor_control.py test    # Test all motors")
            print("  python3 jetson_4motor_control.py manual  # Manual control")
            print("  python3 jetson_4motor_control.py dance   # Dance demo")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted!")
        
    finally:
        controller.cleanup()