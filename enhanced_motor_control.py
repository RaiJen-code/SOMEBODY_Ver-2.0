# enhanced_motor_control.py - Enhanced motor control untuk Robot Ellee
"""
Enhanced Motor Control System untuk Robot Ellee
Extends SOMEBODY4MotorController dengan voice integration dan safety features
"""

import Jetson.GPIO as GPIO
import time
import threading
from datetime import datetime
from motor import SOMEBODY4MotorController

class ElleeMotorController(SOMEBODY4MotorController):
    """Enhanced motor controller untuk Robot Ellee dengan voice commands"""
    
    def __init__(self, config=None):
        # Initialize parent motor controller
        super().__init__()
        
        self.config = config
        
        # Movement settings
        self.default_speed = 50  # Default 50%
        self.max_safe_speed = 70  # Maximum 70%
        self.current_speed = 50
        
        # Movement state
        self.is_moving = False
        self.current_action = "stopped"
        self.movement_start_time = None
        self.emergency_stop_active = False
        
        # Safety features
        self.movement_timeout = 10  # Auto-stop after 10 seconds
        self.safety_lock = threading.Lock()
        
        # Movement history untuk memory integration
        self.movement_history = []
        self.total_movements = 0
        
        print("🤖 Enhanced Ellee Motor Controller initialized!")
        print(f"   Default Speed: {self.default_speed}%")
        print(f"   Max Safe Speed: {self.max_safe_speed}%")
        print(f"   Movement Timeout: {self.movement_timeout}s")
    
    def set_speed_limit(self, speed):
        """Set current speed dengan safety limit"""
        speed = max(0, min(self.max_safe_speed, speed))
        self.current_speed = speed
        return speed
    
    def _start_movement(self, action_name):
        """Start movement tracking"""
        with self.safety_lock:
            if self.emergency_stop_active:
                print("🚨 Emergency stop active! Cannot move.")
                return False
            
            self.is_moving = True
            self.current_action = action_name
            self.movement_start_time = time.time()
            self.total_movements += 1
            
            # Start safety timeout thread
            threading.Thread(target=self._movement_timeout_check, daemon=True).start()
            
            print(f"🚀 Starting movement: {action_name}")
            return True
    
    def _end_movement(self):
        """End movement tracking"""
        with self.safety_lock:
            if self.is_moving:
                duration = time.time() - self.movement_start_time if self.movement_start_time else 0
                
                # Record movement history
                self.movement_history.append({
                    'action': self.current_action,
                    'duration': duration,
                    'speed': self.current_speed,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep only last 50 movements
                if len(self.movement_history) > 50:
                    self.movement_history = self.movement_history[-50:]
                
                print(f"✅ Completed movement: {self.current_action} ({duration:.1f}s)")
                
            self.is_moving = False
            self.current_action = "stopped"
            self.movement_start_time = None
    
    def _movement_timeout_check(self):
        """Safety timeout untuk auto-stop movement"""
        time.sleep(self.movement_timeout)
        
        if self.is_moving:
            print(f"⏰ Movement timeout after {self.movement_timeout}s - Auto stopping")
            self.stop_all_safe()
    
    def stop_all_safe(self):
        """Enhanced stop dengan safety dan state management"""
        super().stop_all()
        self._end_movement()
        print("🛑 All motors stopped safely")
    
    def emergency_stop(self):
        """Emergency stop - immediate halt"""
        with self.safety_lock:
            self.emergency_stop_active = True
            super().stop_all()
            self._end_movement()
            
            # Clear emergency stop after 2 seconds
            threading.Thread(target=self._clear_emergency_stop, daemon=True).start()
            
            print("🚨 EMERGENCY STOP ACTIVATED!")
            return "Emergency stop activated! All movement halted."
    
    def _clear_emergency_stop(self):
        """Clear emergency stop after safety delay"""
        time.sleep(2)
        with self.safety_lock:
            self.emergency_stop_active = False
        print("✅ Emergency stop cleared - Ready to move")
    
    # Enhanced movement methods dengan voice integration
    def voice_move_forward(self, speed=None, duration=None):
        """Voice command: Move forward"""
        if not self._start_movement("moving forward"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.move_forward(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Moving forward at {speed}% speed for {duration} seconds"
        else:
            return f"Moving forward at {speed}% speed"
    
    def voice_move_backward(self, speed=None, duration=None):
        """Voice command: Move backward"""
        if not self._start_movement("moving backward"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.move_backward(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Moving backward at {speed}% speed for {duration} seconds"
        else:
            return f"Moving backward at {speed}% speed"
    
    def voice_turn_left(self, speed=None, duration=None):
        """Voice command: Turn left"""
        if not self._start_movement("turning left"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.turn_left(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Turning left at {speed}% speed for {duration} seconds"
        else:
            return f"Turning left at {speed}% speed"
    
    def voice_turn_right(self, speed=None, duration=None):
        """Voice command: Turn right"""
        if not self._start_movement("turning right"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.turn_right(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Turning right at {speed}% speed for {duration} seconds"
        else:
            return f"Turning right at {speed}% speed"
    
    def voice_strafe_left(self, speed=None, duration=None):
        """Voice command: Strafe left (sideways)"""
        if not self._start_movement("strafing left"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.strafe_left(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Moving left sideways at {speed}% speed for {duration} seconds"
        else:
            return f"Moving left sideways at {speed}% speed"
    
    def voice_strafe_right(self, speed=None, duration=None):
        """Voice command: Strafe right (sideways)"""
        if not self._start_movement("strafing right"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or self.current_speed)
        self.strafe_right(speed)
        
        if duration:
            threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
            return f"Moving right sideways at {speed}% speed for {duration} seconds"
        else:
            return f"Moving right sideways at {speed}% speed"
    
    def voice_spin_around(self, speed=None, duration=2):
        """Voice command: Spin around"""
        if not self._start_movement("spinning around"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(speed or (self.current_speed - 10))  # Slower for spinning
        self.spin_clockwise(speed)
        
        # Auto-stop after duration
        threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
        return f"Spinning around at {speed}% speed for {duration} seconds"
    
    def voice_dance_mode(self):
        """Voice command: Dance mode"""
        if not self._start_movement("dancing"):
            return "Cannot move - emergency stop active"
        
        # Start dance in background thread
        threading.Thread(target=self._enhanced_dance, daemon=True).start()
        return "Let me show you my moves! Starting dance mode!"
    
    def voice_come_here(self, duration=2):
        """Voice command: Come here (move forward towards user)"""
        if not self._start_movement("coming to you"):
            return "Cannot move - emergency stop active"
        
        speed = self.set_speed_limit(30)  # Slower for safety when approaching
        self.move_forward(speed)
        
        # Auto-stop after duration
        threading.Thread(target=self._timed_movement, args=(duration,), daemon=True).start()
        return f"Coming to you at safe speed for {duration} seconds"
    
    def _timed_movement(self, duration):
        """Execute movement for specific duration then stop"""
        time.sleep(duration)
        self.stop_all_safe()
    
    def _enhanced_dance(self):
        """Enhanced dance mode dengan voice integration"""
        print("\n🕺 Ellee Enhanced Dance Mode! 🕺")
        
        dance_moves = [
            ("forward wiggle", lambda: self.move_forward(40), 1),
            ("backward wiggle", lambda: self.move_backward(40), 1),
            ("left slide", lambda: self.strafe_left(35), 1.5),
            ("right slide", lambda: self.strafe_right(35), 1.5),
            ("spin left", lambda: self.turn_left(45), 2),
            ("spin right", lambda: self.turn_right(45), 2),
            ("diagonal move", lambda: self.diagonal_forward_left(30), 1),
            ("final spin", lambda: self.spin_clockwise(50), 3),
        ]
        
        for move_name, action, duration in dance_moves:
            if not self.is_moving:  # Check if stopped during dance
                break
                
            print(f"🎵 {move_name}...")
            action()
            time.sleep(duration)
        
        self.stop_all_safe()
        print("🎉 Dance complete! That was fun!")
    
    def get_movement_status(self):
        """Get current movement status"""
        return {
            'is_moving': self.is_moving,
            'current_action': self.current_action,
            'current_speed': self.current_speed,
            'emergency_stop_active': self.emergency_stop_active,
            'total_movements': self.total_movements,
            'movement_duration': time.time() - self.movement_start_time if self.movement_start_time else 0
        }
    
    def get_movement_history_summary(self):
        """Get movement history summary untuk memory system"""
        if not self.movement_history:
            return "No movement history yet"
        
        total_time = sum(m['duration'] for m in self.movement_history)
        most_common = {}
        
        for movement in self.movement_history:
            action = movement['action']
            most_common[action] = most_common.get(action, 0) + 1
        
        favorite_move = max(most_common, key=most_common.get) if most_common else "none"
        
        return f"Total movements: {self.total_movements}, " \
               f"Total time: {total_time:.1f}s, " \
               f"Favorite move: {favorite_move}, " \
               f"Recent moves: {len(self.movement_history)}"
    
    def set_movement_preferences(self, preferences):
        """Set movement preferences dari memory system"""
        if 'default_speed' in preferences:
            self.current_speed = self.set_speed_limit(preferences['default_speed'])
        
        if 'movement_timeout' in preferences:
            self.movement_timeout = max(5, min(30, preferences['movement_timeout']))
        
        print(f"✅ Movement preferences updated: speed={self.current_speed}%, timeout={self.movement_timeout}s")
    
    def cleanup_enhanced(self):
        """Enhanced cleanup dengan state management"""
        if self.is_moving:
            self.stop_all_safe()
        
        super().cleanup()
        print("🧹 Enhanced motor controller cleaned up")

# Test functions untuk development
def test_voice_commands():
    """Test voice commands"""
    print("🧪 Testing Enhanced Motor Controller Voice Commands...")
    
    try:
        controller = ElleeMotorController()
        
        print("\n✅ Testing voice command responses:")
        
        # Test command responses
        commands = [
            ("forward", controller.voice_move_forward),
            ("backward", controller.voice_move_backward),
            ("left turn", controller.voice_turn_left),
            ("right turn", controller.voice_turn_right),
            ("strafe left", controller.voice_strafe_left),
            ("strafe right", controller.voice_strafe_right),
            ("spin", controller.voice_spin_around),
            ("come here", controller.voice_come_here),
        ]
        
        for name, command in commands:
            response = command(duration=1)  # 1 second test
            print(f"  {name}: {response}")
            time.sleep(1.5)
        
        # Test emergency stop
        print("\n🚨 Testing emergency stop:")
        emergency_response = controller.emergency_stop()
        print(f"  Emergency stop: {emergency_response}")
        
        time.sleep(3)
        
        # Test status
        print("\n📊 Movement status:")
        status = controller.get_movement_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n📈 Movement history:")
        history = controller.get_movement_history_summary()
        print(f"  {history}")
        
        print("\n✅ Voice commands test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Voice commands test failed: {e}")
        return False
    
    finally:
        if 'controller' in locals():
            controller.cleanup_enhanced()

if __name__ == "__main__":
    test_voice_commands()