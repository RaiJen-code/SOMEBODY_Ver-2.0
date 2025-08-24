# enhanced_brain_module_with_movement_complete.py - Complete brain dengan semua methods
"""
Enhanced Brain Module untuk Robot Ellee dengan Movement Integration - COMPLETE VERSION
Integrates movement commands dengan existing conversation dan project management
Fixed all missing methods dan improved AI responsiveness
"""

import threading
import time
import queue
from enum import Enum
import cv2
import numpy as np
from datetime import datetime

# Import existing modules
from fixed_speech_module import FixedSpeechListener, ConversationManager
from vision_module import VisionSystem
from openai_wrapper import OpenAIClient
from tts_wrapper import TTSEngine
from smart_electronics_analyzer import SmartElectronicsAnalyzer
from memory_system import ElleeBrainMemory

# Import new movement modules
from enhanced_motor_control import ElleeMotorController
from movement_commands import MovementCommandProcessor

class RobotState(Enum):
    IDLE = "idle"
    LISTENING = "listening"  
    THINKING = "thinking"
    SPEAKING = "speaking"
    ENGAGING = "engaging"
    LEARNING = "learning"
    MOVING = "moving"  # New state untuk movement

class EnhancedElleeBrainWithMovement:
    def __init__(self, config):
        self.config = config
        self.state = RobotState.IDLE
        
        # Initialize existing core components
        print("🧠 Initializing Enhanced Ellee's brain with movement capabilities...")
        self.speech_listener = FixedSpeechListener(config)
        self.vision_system = VisionSystem(config)
        self.smart_analyzer = SmartElectronicsAnalyzer(config)
        self.openai_client = OpenAIClient(config.OPENAI_API_KEY)
        self.tts_engine = TTSEngine(config)
        self.conversation_manager = ConversationManager(config)
        
        # Initialize memory system
        self.memory = ElleeBrainMemory(config)
        
        # Initialize NEW movement system
        try:
            self.motor_controller = ElleeMotorController(config)
            self.movement_processor = MovementCommandProcessor(self.motor_controller)
            self.movement_enabled = True
            print("✅ Movement system initialized successfully!")
        except Exception as e:
            print(f"⚠️ Movement system initialization failed: {e}")
            print("   Robot will work without movement capabilities")
            self.motor_controller = None
            self.movement_processor = None
            self.movement_enabled = False
        
        # Enhanced state management
        self.is_running = False
        self.main_thread = None
        
        # Person detection and recognition
        self.person_detected = False
        self.current_person_id = None
        self.last_person_detection = 0
        self.person_timeout = 10
        
        # Current conversation tracking
        self.current_conversation = {
            'start_time': None,
            'messages': [],
            'topics': [],
            'electronics_analyses': [],
            'movement_commands': []  # Track movement commands
        }
        
        # Project tracking
        self.current_project_id = None
        self.project_mode = False
        
        # Learning metrics
        self.interaction_count = 0
        self.successful_teachings = 0
        
        # Conversation settings
        self.conversation_active = False
        self.last_speech_time = 0
        self.speech_timeout = 15
        self.conversation_cooldown = 3
        self.last_greeting_time = 0
        
        # Movement integration settings
        self.movement_during_conversation = True
        self.movement_timeout = 30
        
        # Thread safety
        self.state_lock = threading.Lock()
        
        # AI Response enhancement
        self.ai_response_timeout = 10  # 10 seconds max untuk AI response
        self.last_ai_response_time = 0
        self.ai_fallback_responses = [
            "That's an interesting question! Let me think about that and get back to you with more details.",
            "Great topic! I'd love to explore that with you. What specific aspect interests you most?",
            "Excellent question! That's something I find fascinating too. Tell me more about what you'd like to know.",
            "That's a really good point! I'm always learning about these topics. What's your experience with it?",
            "Interesting! I enjoy discussing topics like this. What got you interested in this subject?"
        ]
        
        print("✅ Enhanced Ellee's brain with movement initialized successfully!")
    
    def start(self):
        """Start the enhanced robot brain dengan movement"""
        if not self.is_running:
            self.is_running = True
            
            # Start vision system
            self.vision_system.start_capture()
            
            # Start main brain loop
            self.main_thread = threading.Thread(target=self._enhanced_main_loop_with_movement)
            self.main_thread.daemon = True
            self.main_thread.start()
            
            # Load memory context
            self._load_startup_context()
            
            print("🤖 Enhanced Ellee with movement is now awake and ready!")
            
            # Enhanced greeting dengan movement capabilities
            greeting = self._generate_personalized_greeting_with_movement()
            self._speak(greeting)
    
    def _generate_personalized_greeting_with_movement(self):
        """Generate greeting yang mentions movement capabilities"""
        try:
            stats = self.memory.get_memory_stats()
            
            base_greeting = self._generate_personalized_greeting()
            
            if self.movement_enabled:
                movement_addition = " I can also move around now - just ask me to move forward, turn, or even dance! I'm your smart electronics assistant who can walk and talk!"
                return base_greeting + movement_addition
            else:
                return base_greeting
                
        except Exception as e:
            if self.movement_enabled:
                return "Hello! I'm Ellee, your smart electronics assistant robot. I can help with projects, analyze components, and move around! I'm ready to be your personal electronics companion. What would you like to explore today?"
            else:
                return "Hello! I'm Ellee, your smart electronics assistant robot. I can help with projects and analyze components! What would you like to learn about?"
    
    def _enhanced_main_loop_with_movement(self):
        """Enhanced main loop dengan movement state management"""
        print("🧠 Enhanced consciousness with movement started")
        
        while self.is_running:
            try:
                # Update person detection
                self._update_person_detection()
                
                current_time = time.time()
                
                # Enhanced state machine dengan MOVING state
                if self.state == RobotState.IDLE:
                    if self.person_detected:
                        if not self.conversation_active:
                            if current_time - self.last_greeting_time > self.conversation_cooldown:
                                self._transition_to_engaging()
                                self.last_greeting_time = current_time
                                self._start_new_conversation()
                            else:
                                self._transition_to_listening()
                                if not hasattr(self, 'conversation_started') or not self.conversation_started:
                                    self._start_new_conversation()
                        else:
                            self._transition_to_listening()
                
                elif self.state == RobotState.ENGAGING:
                    if self.person_detected:
                        self._greet_person_with_memory()
                        self._transition_to_listening()
                        self.conversation_active = True
                    else:
                        self._transition_to_idle()
                
                elif self.state == RobotState.LISTENING:
                    if not self.person_detected:
                        self._handle_person_left()
                    else:
                        # Check for speech input
                        speech = self.speech_listener.get_speech()
                        if speech:
                            self.last_speech_time = current_time
                            self._process_speech_with_movement(speech)
                        else:
                            self._check_conversation_timeout(current_time)
                
                elif self.state == RobotState.THINKING:
                    time.sleep(1)
                    if current_time - getattr(self, 'thinking_start_time', current_time) > 5:
                        if self.person_detected:
                            self._transition_to_listening()
                        else:
                            self._transition_to_idle()
                
                elif self.state == RobotState.MOVING:
                    self._handle_movement_state()
                
                elif self.state == RobotState.LEARNING:
                    self._handle_learning_state()
                
                elif self.state == RobotState.SPEAKING:
                    if not self.tts_engine.is_speaking():
                        if self.person_detected:
                            self._transition_to_listening()
                        else:
                            self._handle_person_left()
                
                time.sleep(0.1)
                
            except Exception as e:
                print("⚠ Error in enhanced main loop with movement: {}".format(e))
                import traceback
                print(traceback.format_exc())
                time.sleep(1)
    
    def _check_conversation_timeout(self, current_time):
        """Check if we should prompt for more conversation - FIXED MISSING METHOD"""
        if self.conversation_active and self.last_speech_time > 0:
            time_since_speech = current_time - self.last_speech_time
            
            # Offer help after period of silence
            if time_since_speech > self.speech_timeout:
                self.last_speech_time = current_time  # Reset to avoid repeated prompts
                
                help_messages = [
                    "Is there anything else you'd like to know about electronics?",
                    "Feel free to ask me more questions or show me your components!",
                    "Would you like to work on a project or learn about specific components?",
                    "I'm here to help with any electronics questions you have!",
                    "Want to try some movement commands? Just say 'move forward' or 'dance'!",
                    "Tell me about any electronics topic - Arduino, ESP32, sensors, anything!"
                ]
                
                import random
                help_message = random.choice(help_messages)
                self._speak(help_message)
    
    def _handle_movement_state(self):
        """Handle movement state transitions"""
        if self.movement_enabled and self.motor_controller:
            status = self.motor_controller.get_movement_status()
            
            if not status['is_moving']:
                # Movement completed, return to appropriate state
                if self.person_detected:
                    self._transition_to_listening()
                else:
                    self._transition_to_idle()
            else:
                # Still moving, check for safety timeout
                if status['movement_duration'] > self.movement_timeout:
                    print("⏰ Movement timeout - stopping for safety")
                    self.motor_controller.stop_all_safe()
        else:
            # No movement capability, return to listening
            self._transition_to_listening()
    
    def _process_speech_with_movement(self, speech_text):
        """Process speech dengan movement command detection - ENHANCED"""
        print("👂 Processing with movement support: '{}'".format(speech_text))
        
        # Check for movement commands first
        if self.movement_enabled and self.movement_processor.is_movement_command(speech_text):
            self._process_movement_command(speech_text)
            return
        
        # Check for memory/project commands
        if self._handle_memory_commands(speech_text):
            return
        
        if self._handle_project_commands(speech_text):
            return
        
        # Check for electronics analysis commands
        if self._is_electronics_command(speech_text):
            self._process_electronics_with_memory(speech_text)
        else:
            # Regular conversation - ENHANCED dengan better AI
            self._process_regular_conversation_enhanced(speech_text)
    
    def _process_regular_conversation_enhanced(self, speech_text):
        """Enhanced regular conversation processing dengan better AI responsiveness"""
        print("💬 Processing enhanced conversation: '{}'".format(speech_text))
        
        with self.state_lock:
            self._transition_to_thinking()
            self.thinking_start_time = time.time()
        
        # Add user message to conversation
        self.conversation_manager.add_message("user", speech_text)
        
        # Add to current conversation tracking
        self.current_conversation['messages'].append({
            'role': 'user',
            'content': speech_text,
            'timestamp': datetime.now().isoformat(),
            'type': 'regular_conversation'
        })
        
        # Get memory context
        memory_context = self.memory.get_conversation_context(self.current_person_id, limit=3)
        
        # Generate AI response dengan timeout dan fallback
        threading.Thread(target=self._generate_enhanced_ai_response, args=(memory_context, speech_text), daemon=True).start()
    
    def _generate_enhanced_ai_response(self, memory_context, original_speech):
        """Generate AI response dengan enhanced fallback dan faster response"""
        try:
            start_time = time.time()
            
            # Get conversation for AI dengan memory context
            messages = self.conversation_manager.get_conversation_for_ai()
            
            # Enhanced system message untuk lebih personal dan responsive
            enhanced_system = """You are Ellee, a brilliant and enthusiastic electronics assistant robot. You are:
- Extremely knowledgeable about electronics, Arduino, ESP32, sensors, circuits, programming
- Friendly, conversational, and encouraging
- Quick to respond with helpful, practical information
- Able to explain complex topics in simple terms
- Enthusiastic about helping people learn and build projects
- Capable of movement and always ready to help

IMPORTANT: Keep responses conversational and engaging (2-4 sentences). Always sound excited about electronics!"""
            
            if memory_context and memory_context != "This is a new conversation.":
                enhanced_system += f"\n\nContext from previous conversations: {memory_context}"
            
            # Special handling untuk electronics topics
            electronics_topics = ['esp32', 'arduino', 'sensor', 'resistor', 'led', 'circuit', 'programming', 'microcontroller']
            if any(topic in original_speech.lower() for topic in electronics_topics):
                enhanced_system += "\n\nThe user is asking about electronics. Provide detailed, educational, and practical information. Be specific about how things work and give real examples."
            
            messages[0]['content'] = enhanced_system
            
            # Try AI response dengan timeout
            response = None
            try:
                response = self.openai_client.chat_completion(
                    messages=messages,
                    max_tokens=250,  # Increased untuk detailed responses
                    temperature=0.8  # Slightly higher untuk more personality
                )
            except Exception as e:
                print(f"⚠ AI API error: {e}")
                response = None
            
            response_time = time.time() - start_time
            
            if response and len(response.strip()) > 10:
                print(f"🧠 AI Response generated in {response_time:.2f}s: {response}")
                
                # Add conversation-encouraging ending jika belum ada
                if not any(end in response.lower() for end in ['?', 'would you', 'do you', 'what', 'how', 'tell me']):
                    encouragements = [
                        " What else would you like to explore?",
                        " Any other questions about this topic?",
                        " Want to dive deeper into this?",
                        " What's your next electronics adventure?",
                        " Anything else I can help you build or learn?"
                    ]
                    import random
                    response += random.choice(encouragements)
                
                # Add to conversation managers
                self.conversation_manager.add_message("assistant", response)
                self.current_conversation['messages'].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                self._speak(response)
            else:
                # Enhanced fallback responses berdasarkan topic
                self._provide_enhanced_fallback_response(original_speech)
                
        except Exception as e:
            print(f"⚠ Error generating enhanced AI response: {e}")
            self._provide_enhanced_fallback_response(original_speech)
        
        finally:
            # Always return to listening to continue conversation
            self._transition_to_listening()
    
    def _provide_enhanced_fallback_response(self, original_speech):
        """Provide enhanced fallback response berdasarkan topic"""
        
        speech_lower = original_speech.lower()
        
        # Topic-specific fallback responses
        if 'esp32' in speech_lower:
            fallback = "The ESP32 is an amazing microcontroller! It's incredibly powerful with built-in WiFi and Bluetooth, perfect for IoT projects. It's more powerful than Arduino Uno and great for web servers, sensor networks, and wireless communication. You can program it with Arduino IDE too! What specific ESP32 project are you thinking about?"
        
        elif 'arduino' in speech_lower:
            fallback = "Arduino is fantastic for learning electronics! It's beginner-friendly but powerful enough for complex projects. The Arduino Uno is perfect to start with - you can control LEDs, sensors, motors, and build amazing projects. I love helping people with Arduino! What would you like to build?"
        
        elif any(word in speech_lower for word in ['sensor', 'temperature', 'ultrasonic', 'pressure']):
            fallback = "Sensors are so exciting! They're like giving your projects the ability to sense the world - temperature, distance, light, pressure, motion, and so much more. Each sensor opens up new project possibilities. What kind of sensor project interests you? I can help you get started!"
        
        elif any(word in speech_lower for word in ['led', 'light', 'rgb']):
            fallback = "LEDs are perfect for starting electronics! They're simple but you can create amazing effects - blinking patterns, RGB color mixing, LED strips, matrices. Always remember to use a current-limiting resistor to protect them. Want to learn about LED projects or how to calculate the right resistor?"
        
        elif any(word in speech_lower for word in ['circuit', 'breadboard', 'wiring']):
            fallback = "Circuit building is the heart of electronics! Breadboards are perfect for prototyping - no soldering needed. Start with simple circuits and work your way up. Good connections, proper power distribution, and understanding current flow are key. Need help with a specific circuit?"
        
        elif any(word in speech_lower for word in ['programming', 'code', 'sketch']):
            fallback = "Programming microcontrollers is incredibly rewarding! Start with simple sketches - blink an LED, read a sensor, control a servo. The Arduino language is based on C++ but much simpler. Practice with small projects and gradually add complexity. What programming challenge are you working on?"
        
        elif any(word in speech_lower for word in ['project', 'build', 'make']):
            fallback = "I love helping with electronics projects! Start with something that excites you - maybe a smart home device, robot, weather station, or game controller. Break big projects into smaller steps. What kind of project sparks your imagination? I'm here to guide you through it!"
        
        else:
            # General electronics enthusiasm
            fallback = "That's a great topic! I'm passionate about electronics and love sharing knowledge. Whether it's basic components, complex circuits, programming, or project ideas - I'm here to help you learn and build amazing things. What specific aspect interests you most?"
        
        # Add conversation encouragement
        fallback += " I'm always excited to dive deep into electronics topics!"
        
        self._speak(fallback)
    
    def _process_movement_command(self, speech_text):
        """Process movement commands"""
        with self.state_lock:
            self._transition_to_moving()
        
        # Add to current conversation
        self.current_conversation['messages'].append({
            'role': 'user',
            'content': speech_text,
            'timestamp': datetime.now().isoformat(),
            'type': 'movement_command'
        })
        
        # Process command
        result = self.movement_processor.process_voice_command(speech_text)
        
        if result['success']:
            # Record movement command
            self.current_conversation['movement_commands'].append({
                'command': speech_text,
                'command_type': result.get('command_type'),
                'success': True,
                'timestamp': datetime.now().isoformat()
            })
            
            # Speak response
            self._speak(result['response'])
            
            # Update memory if in project mode
            if self.project_mode and self.current_project_id:
                self.memory.update_project_progress(
                    self.current_project_id,
                    {'learned_lessons': [f"Movement: {result.get('command_type', 'unknown')}"]},
                    None
                )
        else:
            # Failed movement command
            self._speak(f"Sorry, I couldn't execute that movement command: {result['response']}")
            self._transition_to_listening()
    
    def _handle_person_left(self):
        """Handle when person leaves conversation"""
        if self.conversation_active:
            # Add a longer delay before ending conversation
            time.sleep(5)  # Increased delay
            
            # Double check they're really gone
            if not self.person_detected:
                self._end_current_conversation()
                self.conversation_active = False
                goodbye_messages = [
                    "Thanks for the great conversation! Feel free to come back anytime for more electronics help!",
                    "See you later! I'll be here whenever you need electronics assistance!",
                    "Goodbye! Come back soon - I love talking about electronics and helping with projects!",
                    "Take care! I'm always ready to help with your next electronics adventure!"
                ]
                import random
                self._speak(random.choice(goodbye_messages))
                self._transition_to_idle()
    
    def _handle_memory_commands(self, speech_text):
        """Handle memory-related commands"""
        text_lower = speech_text.lower()
        
        if 'remember this project' in text_lower or 'save this project' in text_lower:
            self._handle_save_project_command(speech_text)
            return True
        
        elif 'what projects' in text_lower or 'my projects' in text_lower:
            self._handle_list_projects_command()
            return True
        
        elif 'continue project' in text_lower or 'resume project' in text_lower:
            self._handle_continue_project_command(speech_text)
            return True
        
        elif 'memory stats' in text_lower or 'what do you remember' in text_lower:
            self._handle_memory_stats_command()
            return True
        
        return False
    
    def _handle_project_commands(self, speech_text):
        """Handle project management commands"""
        text_lower = speech_text.lower()
        
        if 'what projects' in text_lower or 'my projects' in text_lower or 'list projects' in text_lower:
            self._handle_list_projects_command()
            return True
        
        elif 'continue project' in text_lower or 'resume project' in text_lower:
            self._handle_continue_project_command(speech_text)
            return True
        
        elif 'new project' in text_lower or 'start project' in text_lower or 'create project' in text_lower:
            self._handle_create_project_command(speech_text)
            return True
        
        elif 'project status' in text_lower or 'project progress' in text_lower:
            self._handle_project_status_command()
            return True
        
        return False
    
    def _is_electronics_command(self, text):
        """Check if speech contains electronics-related commands"""
        text_lower = text.lower()
        
        commands = {
            "photo_analysis": ["take a photo", "analyze this", "analyze components", "scan this"],
            "project_suggestions": ["project suggestion", "what can I build", "project ideas"],
            "component_identification": ["what do you see", "identify components", "what components"],
            "circuit_check": ["check my circuit", "verify circuit", "is this correct"],
            "troubleshooting": ["troubleshoot", "what's wrong", "not working", "debug"],
            "quick_check": ["quick look", "quick check", "brief analysis"]
        }
        
        for command_type, keywords in commands.items():
            if any(keyword in text_lower for keyword in keywords):
                return command_type
        
        return None
    
    # Implement all missing methods that were referenced
    def _load_startup_context(self):
        """Load context from memory at startup"""
        try:
            stats = self.memory.get_memory_stats()
            
            active_projects = [p for p in self.memory.project_cache.values() 
                             if p['status'] in ['planning', 'in_progress']]
            
            if active_projects:
                print("📋 Found {} active projects in memory".format(len(active_projects)))
                
            recent_context = self.memory.get_conversation_context(limit=3)
            if recent_context and recent_context != "This is a new conversation.":
                print("🧠 Loaded context: {}".format(recent_context))
                
        except Exception as e:
            print("⚠ Could not load startup context: {}".format(e))
    
    def _generate_personalized_greeting(self):
        """Generate personalized greeting based on memory"""
        try:
            stats = self.memory.get_memory_stats()
            
            if stats['total_conversations'] == 0:
                return "Hello! I'm Ellee, your brilliant electronics assistant robot. I'm incredibly excited to help you learn about electronics, build amazing projects, and explore the world of Arduino, ESP32, sensors, and circuits!"
            
            elif stats['total_conversations'] < 5:
                return "Hi there! Great to see you again! We've had {} fascinating conversations about electronics. I'm always thrilled to help with more projects and answer your questions! What exciting topic shall we explore today?".format(stats['total_conversations'])
            
            else:
                active_projects = len([p for p in self.memory.project_cache.values() 
                                     if p['status'] in ['planning', 'in_progress']])
                
                if active_projects > 0:
                    return "Welcome back, my electronics friend! I see we have {} active projects. I remember all our previous conversations and I'm energized to continue our electronics journey! What shall we work on today?".format(active_projects)
                else:
                    return "Hello again! We've shared {} amazing conversations about electronics. You've been learning so much, and I love being part of your electronics journey! What new adventure shall we start today?".format(stats['total_conversations'])
                    
        except Exception as e:
            return "Hello! I'm Ellee, your enthusiastic electronics assistant robot. I'm absolutely passionate about helping you with electronics projects and questions! Let's explore something amazing together!"
    
    def _start_new_conversation(self):
        """Start tracking a new conversation"""
        self.current_conversation = {
            'start_time': datetime.now(),
            'messages': [],
            'topics': [],
            'electronics_analyses': [],
            'movement_commands': [],
            'person_id': self.current_person_id
        }
        self.conversation_active = True
        self.conversation_started = True
        self.last_speech_time = time.time()
        print("💬 Started new conversation tracking")
    
    def _greet_person_with_memory(self):
        """Greet person using memory context"""
        try:
            if self.current_person_id and self.current_person_id in self.memory.person_cache:
                person_data = self.memory.person_cache[self.current_person_id]
                name = person_data.get('name', 'friend')
                
                recent_context = self.memory.get_conversation_context(self.current_person_id, limit=2)
                
                if 'electronics' in recent_context.lower():
                    greeting = "Hello {}! Ready to dive into more electronics? I remember our fantastic discussions about circuits and components. I'm excited to explore more with you today! What's on your electronics mind?".format(name)
                elif 'project' in recent_context.lower():
                    greeting = "Hi {}! How's your project progressing? I've been thinking about our previous conversations. I'm here and ready to help you build something amazing! What's the next step?".format(name)
                else:
                    greeting = "Great to see you again, {}! I'm energized and ready for another exciting electronics conversation. What fascinating topic should we explore today?".format(name)
                    
            else:
                greetings = [
                    "Hello! I'm Ellee, your passionate electronics assistant robot. I absolutely love helping with Arduino projects, teaching about circuits, and building amazing things together! What brings you here today?",
                    "Hi there! I'm thrilled to meet you! I'm incredibly knowledgeable about electronics and genuinely excited to help with any projects or questions you have. What would you like to explore?",
                    "Welcome! I specialize in electronics education and I'm genuinely enthusiastic about helping people learn and build. From basic LEDs to complex ESP32 projects - I'm here for it all! What interests you?"
                ]
                
                import random
                greeting = random.choice(greetings)
            
            self._speak(greeting)
            
        except Exception as e:
            print("⚠ Error in personalized greeting: {}".format(e))
            self._speak("Hello! I'm Ellee, your enthusiastic electronics assistant robot! I'm absolutely passionate about electronics and ready to help you build amazing projects! What would you like to explore today?")
    
    # Add all other missing methods with proper implementation
    def _handle_save_project_command(self, speech_text):
        """Handle saving current setup as a project"""
        try:
            current_frame = self.vision_system.get_current_frame()
            
            if current_frame is not None:
                analysis = self.smart_analyzer.analyze_components(current_frame, "comprehensive")
                
                if analysis['success']:
                    project_data = self._extract_project_from_analysis(analysis, speech_text)
                    project_id = self.memory.remember_project(project_data)
                    
                    if project_id:
                        self.current_project_id = project_id
                        self.project_mode = True
                        
                        self.memory.update_project_progress(project_id, {}, current_frame)
                        
                        response = "Perfect! I've saved this as a new project called '{}'. I can see the components and I'll help you track your progress. What would you like to work on next?".format(project_data['name'])
                    else:
                        response = "I had trouble saving the project, but I can still help you with your electronics work! What would you like to do next?"
                        
                else:
                    response = "I can save this as a project, but I'm having trouble seeing the components clearly. Could you describe what you're building or adjust the camera angle?"
            else:
                response = "I'd love to save your project! Could you make sure I can see your components clearly with my camera?"
            
            self._speak(response)
            
        except Exception as e:
            print("⚠ Error handling save project: {}".format(e))
            self._speak("I'd love to help save your project! Let me try to see what you're working on.")
        
        finally:
            self._transition_to_listening()
    
    def _handle_list_projects_command(self):
        """List user's projects from memory"""
        try:
            projects = list(self.memory.project_cache.values())
            
            if not projects:
                response = "You don't have any saved projects yet. Would you like to save your current setup as a project or start a new one? I'm excited to help you build something amazing!"
            else:
                active_projects = [p for p in projects if p['status'] in ['planning', 'in_progress']]
                completed_projects = [p for p in projects if p['status'] == 'completed']
                
                response = "Here are your exciting projects: "
                
                if active_projects:
                    names = [p['name'] for p in active_projects[:3]]
                    response += "You have {} active projects: {}. ".format(len(active_projects), ', '.join(names))
                
                if completed_projects:
                    response += "You've completed {} projects - that's awesome! ".format(len(completed_projects))
                
                response += "I'm thrilled to help you continue any of these, start something new, or answer any questions you have!"
            
            self._speak(response)
            
        except Exception as e:
            print("⚠ Error listing projects: {}".format(e))
            self._speak("Let me check your projects... I'm having trouble accessing my memory right now, but I'm still here to help with electronics!")
        
        finally:
            self._transition_to_listening()
    
    def _handle_continue_project_command(self, speech_text):
        """Handle continuing an existing project"""
        try:
            projects = [p for p in self.memory.project_cache.values() 
                       if p['status'] in ['planning', 'in_progress']]
            
            if not projects:
                response = "I don't see any active projects to continue. Would you like to start a new exciting project or need help with something else?"
            elif len(projects) == 1:
                project = projects[0]
                self.current_project_id = project['project_id']
                self.project_mode = True
                
                next_steps = project.get('next_steps', [])
                if next_steps:
                    response = "Great! Let's continue with '{}'. Your next steps were: {}. I'm excited to help you progress! How's it going?".format(project['name'], ', '.join(next_steps[:2]))
                else:
                    response = "Perfect! Let's continue with '{}'. Show me your current progress and I'll help you figure out the exciting next steps.".format(project['name'])
            else:
                project_names = [p['name'] for p in projects[:3]]
                response = "You have multiple active projects: {}. Which one would you like to continue with? I'm ready to dive in!".format(', '.join(project_names))
            
            self._speak(response)
            
        except Exception as e:
            print("⚠ Error handling continue project: {}".format(e))
            self._speak("I'd love to help you continue your project! Let me see what you're working on or tell me more about it.")
        
        finally:
            self._transition_to_listening()
    
    def _handle_create_project_command(self, speech_text):
        """Handle creating a new project"""
        try:
            current_frame = self.vision_system.get_current_frame()
            
            if current_frame is not None:
                self._speak("Let me analyze your components and suggest some exciting projects...")
                
                analysis = self.smart_analyzer.analyze_components(current_frame, "project_suggestion")
                
                if analysis['success']:
                    response = "Fantastic! Based on what I can see, here are some exciting project ideas: {}. I'm thrilled to help you build any of these! Which one sparks your interest?".format(analysis['message'][:200])
                    self._speak(response)
                else:
                    self._speak("I can help you start an amazing project! What components do you have available? You can show them to my camera or just tell me about them.")
            else:
                self._speak("I'd love to help you create an exciting project! Could you show me your components with the camera or describe what you have?")
                
        except Exception as e:
            print("Error handling create project: {}".format(e))
            self._speak("I'd be thrilled to help you start a new electronics project! What are you interested in building?")
        
        finally:
            self._transition_to_listening()
    
    def _handle_project_status_command(self):
        """Handle project status command"""
        try:
            if self.current_project_id and self.current_project_id in self.memory.project_cache:
                project = self.memory.project_cache[self.current_project_id]
                response = "Your current project '{}' is in {} status. ".format(project['name'], project['status'])
                
                if 'next_steps' in project and project['next_steps']:
                    response += "Next steps: {}. I'm excited to help you with whatever comes next! What would you like to work on?".format(', '.join(project['next_steps'][:2]))
                else:
                    response += "What would you like to work on next? I'm here to help guide you!"
            else:
                response = "You don't have an active project selected. Would you like to continue an existing project, start a new exciting one, or need help with something else?"
            
            self._speak(response)
            
        except Exception as e:
            print("⚠ Error getting project status: {}".format(e))
            self._speak("Let me check your project status... What would you like to work on?")
        
        finally:
            self._transition_to_listening()
    
    def _handle_memory_stats_command(self):
        """Handle memory statistics command"""
        try:
            stats = self.memory.get_memory_stats()
            
            response = "Here's what I remember about our journey: I've had {} conversations with you, ".format(stats['total_conversations'])
            response += "you have {} active projects and {} completed ones. ".format(stats['active_projects'], stats['completed_projects'])
            response += "I'm storing about {} megabytes of memories about our interactions. ".format(stats['memory_size_mb'])
            response += "I absolutely love learning about your electronics journey! What specific topic would you like to explore today?"
            
            self._speak(response)
            
        except Exception as e:
            print("⚠ Error getting memory stats: {}".format(e))
            self._speak("I remember lots about our electronics adventures together! I'm always learning more about your projects and preferences. What would you like to explore today?")
        
        finally:
            self._transition_to_listening()
    
    def _extract_project_from_analysis(self, analysis, speech_text):
        """Extract project data from vision analysis and speech"""
        
        # Try to extract project name from speech
        project_name = "Electronics Project"
        if "call it" in speech_text.lower() or "name it" in speech_text.lower():
            words = speech_text.split()
            try:
                name_start = None
                for i, word in enumerate(words):
                    if word.lower() in ["call", "name"]:
                        name_start = i + 2  # Skip "call it" or "name it"
                        break
                
                if name_start and name_start < len(words):
                    project_name = " ".join(words[name_start:name_start+3])  # Take next 3 words
            except:
                pass
        
        # Extract components from analysis
        components = []
        try:
            analysis_text = analysis.get('analysis', '').lower()
            common_components = ['arduino', 'led', 'resistor', 'breadboard', 'sensor', 'wire', 'capacitor', 'button']
            for component in common_components:
                if component in analysis_text:
                    components.append(component.title())
        except:
            pass
        
        # Determine difficulty
        difficulty = "beginner"
        if len(components) > 5:
            difficulty = "intermediate"
        if any(word in analysis.get('analysis', '').lower() for word in ['complex', 'advanced', 'programming']):
            difficulty = "advanced"
        
        return {
            'name': project_name,
            'description': "Project involving {} and other components".format(', '.join(components[:3])),
            'components': components,
            'difficulty': difficulty,
            'next_steps': ['Connect components', 'Test circuit', 'Upload code']
        }
    
    def _process_electronics_with_memory(self, speech_text):
        """Process electronics commands with memory context"""
        print("🔍 Processing electronics command with memory context...")
        
        try:
            current_frame = self.vision_system.get_current_frame()
            
            if current_frame is None:
                self._speak("I'm having trouble with my vision right now. Could you make sure my camera is working? In the meantime, feel free to ask me about electronics concepts!")
                self._transition_to_listening()
                return
            
            context = self.memory.get_conversation_context(self.current_person_id, limit=3)
            teaching_approach = self.memory.get_personalized_teaching_approach(self.current_person_id, "electronics")
            
            command_type = self._is_electronics_command(speech_text)
            
            self._speak("Let me analyze this with what I know about your projects and preferences...")
            
            result = self.smart_analyzer.analyze_components(current_frame, command_type)
            
            if result["success"]:
                enhanced_response = self._enhance_response_with_memory(result, context, teaching_approach)
                
                # Add follow-up question to encourage more interaction
                enhanced_response += " Is there anything specific you'd like to know about these components or any other questions?"
                
                self.current_conversation['electronics_analyses'].append({
                    'timestamp': datetime.now().isoformat(),
                    'command_type': command_type,
                    'analysis': result['analysis'],
                    'success': True
                })
                
                self.current_conversation['messages'].append({
                    'role': 'assistant',
                    'content': enhanced_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                if self.project_mode and self.current_project_id:
                    self.memory.update_project_progress(
                        self.current_project_id,
                        {'learned_lessons': ["Analysis: {}".format(command_type)]},
                        current_frame
                    )
                
                self._speak(enhanced_response)
                
            else:
                error_response = self._get_contextual_error_response(context)
                error_response += " What else would you like to explore or learn about?"
                self._speak(error_response)
                
        except Exception as e:
            print("❌ Electronics analysis error: {}".format(e))
            self._speak("I'm having trouble with my analysis right now, but I'm here to help however I can! What would you like to know about electronics?")
        
        finally:
            self._transition_to_listening()
    
    def _enhance_response_with_memory(self, analysis_result, context, teaching_approach):
        """Enhance analysis response with memory context"""
        
        base_response = analysis_result['message']
        
        # Add context-aware introduction
        if 'Recent topic: electronics' in context:
            intro = "Building on our previous electronics discussions, "
        elif 'Current projects:' in context:
            intro = "Looking at this in the context of your ongoing projects, "
        else:
            intro = "Based on what I can see here, "
        
        # Adjust detail level based on teaching approach
        if teaching_approach.get('detail_level') == 'simple':
            intro += "let me explain this in a straightforward way: "
        elif teaching_approach.get('detail_level') == 'high':
            intro += "here's a detailed technical analysis: "
        else:
            intro += ""
        
        # Add memory-based suggestions
        memory_suggestions = ""
        if self.project_mode and self.current_project_id:
            memory_suggestions = " This fits well with your current project progress!"
        
        return intro + base_response + memory_suggestions
    
    def _get_contextual_error_response(self, context):
        """Get contextual error response based on memory"""
        
        if 'electronics' in context.lower():
            return "I'm having trouble with my vision analysis right now, but based on our previous electronics discussions, I can still help guide you through your project!"
        else:
            return "I can't see clearly right now, but I'm here to help with your electronics questions!"
    
    def _handle_learning_state(self):
        """Handle learning state - transition back to listening after a timeout"""
        time.sleep(3)  # Give time for learning processes
        if self.person_detected:
            self._transition_to_listening()
        else:
            self._transition_to_idle()
    
    def _end_current_conversation(self):
        """Enhanced conversation ending dengan movement data"""
        if self.current_conversation.get('messages'):
            try:
                # Calculate duration
                if self.current_conversation.get('start_time'):
                    duration = (datetime.now() - self.current_conversation['start_time']).total_seconds()
                else:
                    duration = 0
                
                # Prepare conversation data dengan movement info
                conversation_data = {
                    'messages': self.current_conversation['messages'],
                    'topics': self.current_conversation['topics'],
                    'duration': duration,
                    'electronics_analyses': self.current_conversation['electronics_analyses'],
                    'movement_commands': self.current_conversation['movement_commands']  # Include movement data
                }
                
                # Save to memory
                conv_id = self.memory.remember_conversation(
                    conversation_data, 
                    person_id=self.current_person_id
                )
                
                movement_count = len(self.current_conversation['movement_commands'])
                print("💾 Conversation saved to memory (ID: {}, Duration: {:.1f}s, Movements: {})".format(
                    conv_id, duration, movement_count))
                
                # Learn from this interaction
                self._learn_from_conversation(conversation_data)
                
            except Exception as e:
                print("⚠ Error saving conversation with movement data: {}".format(e))
        
        # Reset conversation tracking
        self.current_conversation = {
            'start_time': None,
            'messages': [],
            'topics': [],
            'electronics_analyses': [],
            'movement_commands': []
        }
        self.conversation_started = False
    
    def _learn_from_conversation(self, conversation_data):
        """Learn patterns from the conversation"""
        try:
            # Analyze for learning signals
            learning_signals = {
                'electronics_focus': len(conversation_data.get('electronics_analyses', [])) > 0,
                'question_count': len([m for m in conversation_data['messages'] if '?' in m.get('content', '')]),
                'positive_feedback': any(word in ' '.join([m.get('content', '') for m in conversation_data['messages']]).lower() 
                                       for word in ['great', 'perfect', 'excellent', 'awesome', 'thanks']),
                'confusion_indicators': any(word in ' '.join([m.get('content', '') for m in conversation_data['messages']]).lower() 
                                          for word in ['confused', 'don\'t understand', 'what', 'huh'])
            }
            
            # Update interaction metrics
            self.interaction_count += 1
            if learning_signals['positive_feedback']:
                self.successful_teachings += 1
            
            # Save learning data to memory
            self.memory.learn_from_interaction({
                'conversation_data': conversation_data,
                'learning_signals': learning_signals,
                'success_indicators': learning_signals['positive_feedback'],
                'confusion_indicators': learning_signals['confusion_indicators']
            })
            
            print("📚 Learned from conversation (Success rate: {}/{})".format(self.successful_teachings, self.interaction_count))
            
        except Exception as e:
            print("⚠ Error in learning process: {}".format(e))
    
    def get_enhanced_status(self):
        """Get enhanced robot status with memory info"""
        base_status = {
            "state": self.state.value,
            "person_detected": self.person_detected,
            "is_speaking": self.tts_engine.is_speaking(),
            "conversation_length": len(self.conversation_manager.conversation_history),
            "conversation_active": self.conversation_active
        }
        
        # Add memory information
        try:
            memory_stats = self.memory.get_memory_stats()
        except:
            memory_stats = {}
        
        # Add movement information
        movement_status = {}
        movement_history = ""
        if self.movement_enabled and self.motor_controller:
            try:
                movement_status = self.motor_controller.get_movement_status()
                movement_history = self.motor_controller.get_movement_history_summary()
            except:
                movement_status = {'movement_enabled': True, 'error': 'Status unavailable'}
                movement_history = 'History unavailable'
        else:
            movement_status = {'movement_enabled': False}
            movement_history = 'Movement not available'
        
        enhanced_status = {
            **base_status,
            "memory_stats": memory_stats,
            "current_project": self.current_project_id,
            "project_mode": self.project_mode,
            "interaction_count": self.interaction_count,
            "teaching_success_rate": "{}/{}".format(self.successful_teachings, self.interaction_count) if self.interaction_count > 0 else "0/0",
            "movement_enabled": self.movement_enabled,
            "movement_status": movement_status,
            "movement_history": movement_history
        }
        
        return enhanced_status
    
    def stop(self):
        """Enhanced stop dengan movement cleanup"""
        if self.is_running:
            self.is_running = False
            
            # Stop movement first
            if self.movement_enabled and self.motor_controller:
                try:
                    self.motor_controller.stop_all_safe()
                    print("🛑 Movement stopped")
                except Exception as e:
                    print(f"⚠ Error stopping movement: {e}")
            
            # Save ongoing conversation
            if self.conversation_active and self.current_conversation.get('messages'):
                try:
                    self._end_current_conversation()
                    print("💾 Saved final conversation with movement data")
                except Exception as e:
                    print("⚠ Could not save final conversation: {}".format(e))
            
            if self.main_thread:
                self.main_thread.join(timeout=3)
            
            self.speech_listener.stop_listening()
            self.vision_system.stop_capture()
            
            # Cleanup movement system
            if self.movement_enabled and self.motor_controller:
                try:
                    self.motor_controller.cleanup_enhanced()
                    print("🧹 Movement system cleaned up")
                except Exception as e:
                    print(f"⚠ Error cleaning up movement: {e}")
            
            print("😴 Enhanced Ellee with movement is going to sleep...")
    
    # Helper methods untuk movement integration dan state transitions
    def _update_person_detection(self):
        """Update person detection status (same as original)"""
        motion_detected = self.vision_system.detect_motion()
        person_detected, bbox = self.vision_system.detect_person_simple()
        
        if motion_detected or person_detected:
            self.person_detected = True
            self.last_person_detection = time.time()
        else:
            if time.time() - self.last_person_detection > self.person_timeout:
                self.person_detected = False
    
    def _transition_to_idle(self):
        if self.state != RobotState.IDLE:
            print("💤 Transitioning to IDLE")
            self.state = RobotState.IDLE
            self.speech_listener.stop_listening()
    
    def _transition_to_engaging(self):
        print("👋 Transitioning to ENGAGING")
        self.state = RobotState.ENGAGING
    
    def _transition_to_listening(self):
        """Transition to listening with improved thread management"""
        if self.state != RobotState.LISTENING:
            print("👂 Transitioning to LISTENING")
            self.state = RobotState.LISTENING
            
            # Ensure clean transition by stopping any existing listening
            try:
                self.speech_listener.stop_listening()
                time.sleep(0.1)  # Brief pause to ensure clean stop
            except:
                pass
            
            # Start listening
            self.speech_listener.start_listening()
        else:
            # Already in listening state, just ensure we're actually listening
            if not self.speech_listener.is_listening:
                self.speech_listener.start_listening()
    
    def _transition_to_thinking(self):
        print("🤔 Transitioning to THINKING")
        self.state = RobotState.THINKING
        self.speech_listener.stop_listening()
    
    def _transition_to_speaking(self):
        print("🗣 Transitioning to SPEAKING")
        self.state = RobotState.SPEAKING
        self.speech_listener.stop_listening()
    
    def _transition_to_learning(self):
        print("📚 Transitioning to LEARNING")
        self.state = RobotState.LEARNING
        self.speech_listener.stop_listening()
    
    def _transition_to_moving(self):
        """Transition to moving state"""
        if self.state != RobotState.MOVING:
            print("🚶 Transitioning to MOVING")
            self.state = RobotState.MOVING
            # Keep speech listener active untuk stop commands
    
    def _speak(self, text):
        """Enhanced speak dengan movement awareness"""
        print("🗣 Enhanced Ellee: {}".format(text))
        
        # Don't transition to speaking if currently moving (allow movement + speech)
        if self.state != RobotState.MOVING:
            self._transition_to_speaking()
        
        # Use a thread to handle TTS without blocking
        def speak_and_return():
            self.tts_engine.speak(text)
            # After speaking, return to appropriate state
            if self.state == RobotState.SPEAKING:  # Only if we were in speaking state
                if self.conversation_active and self.person_detected:
                    self._transition_to_listening()
                elif not self.person_detected:
                    self._transition_to_idle()
        
        threading.Thread(target=speak_and_return, daemon=True).start()

# Test function
def test_enhanced_brain_with_movement():
    """Test enhanced brain dengan movement capabilities"""
    from config import Config
    
    print("Testing Enhanced Ellee Brain with Movement...")
    print("This will test the full robot with movement capabilities")
    print("Try commands like:")
    print("- 'Move forward'")
    print("- 'Turn left'") 
    print("- 'Dance'")
    print("- 'Tell me about ESP32'")
    print("- 'How does Arduino work?'")
    print("- 'Stop'")
    
    try:
        brain = EnhancedElleeBrainWithMovement(Config)
        brain.start()
        
        # Run for 60 seconds to test movement integration
        start_time = time.time()
        while time.time() - start_time < 60:
            status = brain.get_enhanced_status()
            print("Status: {} | Person: {} | Moving: {} | Movement Enabled: {}".format(
                status['state'], 
                status['person_detected'],
                status.get('movement_status', {}).get('is_moving', False),
                status['movement_enabled']
            ))
            time.sleep(3)
        
        brain.stop()
        print("✅ Enhanced brain with movement test completed!")
        return True
        
    except Exception as e:
        print("❌ Enhanced brain with movement test failed: {}".format(e))
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_enhanced_brain_with_movement()