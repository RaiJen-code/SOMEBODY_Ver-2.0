# movement_commands.py - Voice command processor untuk movement
"""
Movement Commands Processor untuk Robot Ellee
Processes voice commands dan converts ke motor actions
"""

import re
import threading
import time
from datetime import datetime

class MovementCommandProcessor:
    """Process voice commands untuk movement control"""
    
    def __init__(self, motor_controller):
        self.motor_controller = motor_controller
        
        # Command patterns dengan variations
        self.command_patterns = {
            # Basic movement
            'move_forward': [
                r'\b(move|go|walk)\s+(forward|ahead|straight)\b',
                r'\bforward\b',
                r'\bgo\s+forward\b',
                r'\bmove\s+ahead\b'
            ],
            'move_backward': [
                r'\b(move|go|walk)\s+(backward|back|backwards)\b',
                r'\bbackward\b',
                r'\bgo\s+back\b',
                r'\bmove\s+back\b',
                r'\breverse\b'
            ],
            'turn_left': [
                r'\bturn\s+left\b',
                r'\bgo\s+left\b',
                r'\bleft\s+turn\b',
                r'\brotate\s+left\b'
            ],
            'turn_right': [
                r'\bturn\s+right\b',
                r'\bgo\s+right\b',
                r'\bright\s+turn\b',
                r'\brotate\s+right\b'
            ],
            'strafe_left': [
                r'\b(move|strafe|slide)\s+left\b',
                r'\bsideway\s+left\b',
                r'\bstep\s+left\b'
            ],
            'strafe_right': [
                r'\b(move|strafe|slide)\s+right\b',
                r'\bsideway\s+right\b',
                r'\bstep\s+right\b'
            ],
            'spin_around': [
                r'\bspin\s+(around|clockwise)\b',
                r'\bturn\s+around\b',
                r'\brotate\s+(around|full)\b',
                r'\bspin\b'
            ],
            'dance': [
                r'\bdance\b',
                r'\bshow\s+me\s+your\s+moves\b',
                r'\bdance\s+mode\b',
                r'\blet\'s\s+dance\b'
            ],
            'come_here': [
                r'\bcome\s+here\b',
                r'\bcome\s+to\s+me\b',
                r'\bcome\s+over\b',
                r'\bapproach\b'
            ],
            'stop': [
                r'\bstop\b',
                r'\bhalt\b',
                r'\bstop\s+moving\b',
                r'\bfreeze\b'
            ],
            'emergency_stop': [
                r'\bemergency\s+stop\b',
                r'\bstop\s+now\b',
                r'\bstop\s+immediately\b',
                r'\bE\s*STOP\b'
            ]
        }
        
        # Speed keywords
        self.speed_patterns = {
            'slow': [r'\bslow\b', r'\bslowly\b', r'\bcarefully\b'],
            'fast': [r'\bfast\b', r'\bquick\b', r'\bquickly\b', r'\brapid\b'],
            'normal': [r'\bnormal\b', r'\bregular\b', r'\bmedium\b']
        }
        
        # Duration keywords
        self.duration_patterns = {
            r'\bfor\s+(\d+)\s+seconds?\b': lambda m: int(m.group(1)),
            r'\bfor\s+(\d+)\s+sec\b': lambda m: int(m.group(1)),
            r'\b(\d+)\s+seconds?\b': lambda m: int(m.group(1)),
            r'\ba\s+bit\b': lambda m: 1,
            r'\ba\s+little\b': lambda m: 1,
            r'\ba\s+while\b': lambda m: 3,
            r'\ba\s+moment\b': lambda m: 2
        }
        
        # Command history
        self.command_history = []
        self.last_command_time = 0
        
        print("🎮 Movement Command Processor initialized")
    
    def process_voice_command(self, voice_text):
        """
        Process voice command dan return response
        
        Args:
            voice_text (str): Voice input text
            
        Returns:
            dict: Command result dengan response text
        """
        
        if not voice_text:
            return {"success": False, "response": "No voice input received"}
        
        # Normalize text
        text = voice_text.lower().strip()
        
        # Record command
        self.command_history.append({
            'text': text,
            'timestamp': datetime.now().isoformat(),
            'processed': False
        })
        
        # Keep only last 20 commands
        if len(self.command_history) > 20:
            self.command_history = self.command_history[-20:]
        
        print(f"🎤 Processing movement command: '{voice_text}'")
        
        # Check for emergency stop first (highest priority)
        if self._match_command(text, 'emergency_stop'):
            response = self.motor_controller.emergency_stop()
            self._record_success('emergency_stop')
            return {"success": True, "response": response, "command_type": "emergency_stop"}
        
        # Check for stop command
        if self._match_command(text, 'stop'):
            self.motor_controller.stop_all_safe()
            self._record_success('stop')
            return {"success": True, "response": "Stopping all movement", "command_type": "stop"}
        
        # Extract speed and duration modifiers
        speed = self._extract_speed(text)
        duration = self._extract_duration(text)
        
        # Process movement commands
        for command_type, patterns in self.command_patterns.items():
            if command_type in ['stop', 'emergency_stop']:
                continue  # Already handled above
                
            if self._match_command(text, command_type):
                return self._execute_movement_command(command_type, speed, duration, text)
        
        # No movement command found
        return {"success": False, "response": "I didn't understand that movement command"}
    
    def _match_command(self, text, command_type):
        """Check if text matches command pattern"""
        patterns = self.command_patterns.get(command_type, [])
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_speed(self, text):
        """Extract speed modifier from text"""
        for speed_type, patterns in self.speed_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    if speed_type == 'slow':
                        return 30
                    elif speed_type == 'fast':
                        return 65  # Within safe limit
                    elif speed_type == 'normal':
                        return 50
        return None  # Use default
    
    def _extract_duration(self, text):
        """Extract duration from text"""
        for pattern, converter in self.duration_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return converter(match)
                except:
                    continue
        return None  # No duration specified
    
    def _execute_movement_command(self, command_type, speed, duration, original_text):
        """Execute movement command dengan appropriate method"""
        
        try:
            # Map command types to motor controller methods
            command_map = {
                'move_forward': self.motor_controller.voice_move_forward,
                'move_backward': self.motor_controller.voice_move_backward,
                'turn_left': self.motor_controller.voice_turn_left,
                'turn_right': self.motor_controller.voice_turn_right,
                'strafe_left': self.motor_controller.voice_strafe_left,
                'strafe_right': self.motor_controller.voice_strafe_right,
                'spin_around': self.motor_controller.voice_spin_around,
                'dance': self.motor_controller.voice_dance_mode,
                'come_here': self.motor_controller.voice_come_here
            }
            
            if command_type not in command_map:
                return {"success": False, "response": f"Unknown command type: {command_type}"}
            
            # Get method
            method = command_map[command_type]
            
            # Execute command dengan parameters
            if command_type == 'dance':
                # Dance doesn't take speed/duration parameters
                response = method()
            else:
                # Build parameters
                kwargs = {}
                if speed is not None:
                    kwargs['speed'] = speed
                if duration is not None:
                    kwargs['duration'] = duration
                
                response = method(**kwargs)
            
            # Record success
            self._record_success(command_type)
            
            # Add context to response
            context_response = self._add_conversational_context(response, command_type, speed, duration)
            
            return {
                "success": True, 
                "response": context_response,
                "command_type": command_type,
                "speed": speed,
                "duration": duration
            }
            
        except Exception as e:
            print(f"❌ Error executing movement command: {e}")
            return {"success": False, "response": f"Sorry, I couldn't execute that movement: {str(e)}"}
    
    def _add_conversational_context(self, base_response, command_type, speed, duration):
        """Add conversational context to response"""
        
        # Fun conversational additions
        conversation_starters = {
            'move_forward': ["Alright, ", "Sure thing! ", "Moving forward! ", "Here I go! "],
            'move_backward': ["Going back! ", "Backing up! ", "Reversing! ", "Moving backwards! "],
            'turn_left': ["Turning left! ", "Going left! ", "Left turn coming up! "],
            'turn_right': ["Turning right! ", "Going right! ", "Right turn! "],
            'strafe_left': ["Sliding left! ", "Strafing left! ", "Moving sideways! "],
            'strafe_right': ["Sliding right! ", "Strafing right! ", "Going sideways! "],
            'spin_around': ["Time to spin! ", "Here comes a spin! ", "Spinning around! "],
            'dance': ["Let's dance! ", "Time to boogie! ", "Dance time! "],
            'come_here': ["Coming to you! ", "On my way! ", "Approaching! "]
        }
        
        # Get random conversation starter
        import random
        starters = conversation_starters.get(command_type, [""])
        starter = random.choice(starters) if starters else ""
        
        # Add speed/duration context
        context_parts = []
        if speed:
            if speed <= 35:
                context_parts.append("taking it slow")
            elif speed >= 60:
                context_parts.append("moving quickly")
        
        if duration and duration <= 2:
            context_parts.append("just for a moment")
        elif duration and duration >= 5:
            context_parts.append("for a while")
        
        context = " and ".join(context_parts)
        if context:
            context = f" - {context}"
        
        return f"{starter}{base_response}{context}!"
    
    def _record_success(self, command_type):
        """Record successful command execution"""
        if self.command_history:
            self.command_history[-1]['processed'] = True
            self.command_history[-1]['command_type'] = command_type
            self.command_history[-1]['success'] = True
        
        self.last_command_time = time.time()
    
    def is_movement_command(self, voice_text):
        """Check if voice text contains movement command"""
        if not voice_text:
            return False
        
        text = voice_text.lower().strip()
        
        # Check all command patterns
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
        
        return False
    
    def get_available_commands(self):
        """Get list of available commands untuk help"""
        commands = {
            "Basic Movement": [
                "move forward", "move backward", "turn left", "turn right"
            ],
            "Advanced Movement": [
                "strafe left", "strafe right", "spin around"
            ],
            "Fun Commands": [
                "dance", "come here"
            ],
            "Control": [
                "stop", "emergency stop"
            ],
            "Speed Modifiers": [
                "slow", "fast", "normal"
            ],
            "Duration Examples": [
                "for 3 seconds", "for a moment", "a little bit"
            ]
        }
        return commands
    
    def get_command_history_summary(self):
        """Get command history summary"""
        if not self.command_history:
            return "No movement commands used yet"
        
        successful_commands = [cmd for cmd in self.command_history if cmd.get('processed', False)]
        success_rate = len(successful_commands) / len(self.command_history) * 100
        
        # Most used commands
        command_types = [cmd.get('command_type') for cmd in successful_commands if cmd.get('command_type')]
        most_used = {}
        for cmd_type in command_types:
            most_used[cmd_type] = most_used.get(cmd_type, 0) + 1
        
        popular_command = max(most_used, key=most_used.get) if most_used else "none"
        
        return f"Total commands: {len(self.command_history)}, " \
               f"Success rate: {success_rate:.1f}%, " \
               f"Most used: {popular_command.replace('_', ' ')}"

# Test function
def test_movement_commands():
    """Test movement command processor"""
    print("🧪 Testing Movement Command Processor...")
    
    # Mock motor controller untuk testing
    class MockMotorController:
        def voice_move_forward(self, speed=50, duration=None):
            return f"Moving forward at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_move_backward(self, speed=50, duration=None):
            return f"Moving backward at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_turn_left(self, speed=50, duration=None):
            return f"Turning left at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_turn_right(self, speed=50, duration=None):
            return f"Turning right at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_strafe_left(self, speed=50, duration=None):
            return f"Strafing left at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_strafe_right(self, speed=50, duration=None):
            return f"Strafing right at {speed}% speed" + (f" for {duration}s" if duration else "")
        
        def voice_spin_around(self, speed=50, duration=2):
            return f"Spinning around at {speed}% speed for {duration}s"
        
        def voice_dance_mode(self):
            return "Starting dance mode!"
        
        def voice_come_here(self, duration=2):
            return f"Coming to you for {duration}s"
        
        def stop_all_safe(self):
            return "Stopped safely"
        
        def emergency_stop(self):
            return "Emergency stop activated!"
    
    try:
        mock_controller = MockMotorController()
        processor = MovementCommandProcessor(mock_controller)
        
        print("\n✅ Testing voice command recognition:")
        
        test_commands = [
            "move forward",
            "go forward slowly",
            "move forward for 3 seconds",
            "turn left quickly",
            "strafe right for a moment",
            "dance",
            "come here",
            "spin around",
            "stop",
            "emergency stop",
            "move backward fast for 5 seconds",
            "hello how are you",  # Non-movement command
        ]
        
        for command in test_commands:
            result = processor.process_voice_command(command)
            print(f"  '{command}' -> {result['success']}: {result['response']}")
        
        print("\n📊 Available commands:")
        commands = processor.get_available_commands()
        for category, cmd_list in commands.items():
            print(f"  {category}: {', '.join(cmd_list)}")
        
        print("\n📈 Command history:")
        history = processor.get_command_history_summary()
        print(f"  {history}")
        
        print("\n✅ Movement command processor test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Movement command processor test failed: {e}")
        return False

if __name__ == "__main__":
    test_movement_commands()