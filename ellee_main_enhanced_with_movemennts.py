# ellee_main_enhanced_with_movement.py - Main application dengan movement integration
"""
Enhanced Ellee Robot - Electronics Assistant with Movement

Features:
- Advanced memory system with conversation tracking
- Project management with step-by-step guidance  
- Smart electronics analysis with GPT Vision
- Personalized learning and teaching approaches
- Face recognition and person tracking
- Voice commands and natural conversation
- MOVEMENT CONTROL with voice commands (NEW!)
- Progress tracking and skill development
- Improved error handling and recovery
- Better system monitoring and diagnostics

Usage:
    python ellee_main_enhanced_with_movement.py [--test-mode] [--debug] [--memory-stats]
"""

import sys
import os
import time
import argparse
import signal
import threading
import logging
import json
from datetime import datetime, timedelta
import cv2
import traceback
import psutil

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import all enhanced modules with error handling
try:
    from config import Config
    # Import movement-enabled brain module
    from enhanced_brain_module_with_movement import EnhancedElleeBrainWithMovement
    from memory_system import ElleeBrainMemory
    from project_manager import AdvancedProjectManager
    from smart_electronics_analyzer import SmartElectronicsAnalyzer
    from vision_module import VisionSystem
    from fixed_speech_module import test_fixed_speech
    from tts_wrapper import test_tts_wrapper
    from openai_vision_fallback import test_vision_fallback
    
    # Import movement modules
    from enhanced_motor_control import ElleeMotorController
    from movement_commands import MovementCommandProcessor
    
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("💡 Make sure all dependencies are installed and modules are available")
    sys.exit(1)

# Setup logging
def setup_logging(debug_mode=False):
    """Setup comprehensive logging system"""
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging configuration
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/ellee_movement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

class SystemHealthMonitor:
    """Monitor system health and performance"""
    
    def __init__(self):
        self.start_time = time.time()
        self.cpu_threshold = 85.0  # %
        self.memory_threshold = 85.0  # %
        self.disk_threshold = 90.0  # %
        
    def get_system_stats(self):
        """Get current system statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'uptime_hours': (time.time() - self.start_time) / 3600
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_system_health(self):
        """Check if system is healthy"""
        stats = self.get_system_stats()
        
        if 'error' in stats:
            return False, f"System monitoring error: {stats['error']}"
        
        warnings = []
        
        if stats['cpu_percent'] > self.cpu_threshold:
            warnings.append(f"High CPU usage: {stats['cpu_percent']:.1f}%")
        
        if stats['memory_percent'] > self.memory_threshold:
            warnings.append(f"High memory usage: {stats['memory_percent']:.1f}%")
        
        if stats['disk_percent'] > self.disk_threshold:
            warnings.append(f"Low disk space: {stats['disk_percent']:.1f}% used")
        
        return len(warnings) == 0, warnings

class EnhancedElleeRobotWithMovement:
    """Main Enhanced Ellee Robot Application with Movement Capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.debug_mode = False
        self.test_mode = False
        
        # Setup logging
        self.logger = setup_logging(self.debug_mode)
        
        # Core systems
        self.brain = None
        self.memory = None
        self.project_manager = None
        
        # System monitoring
        self.health_monitor = SystemHealthMonitor()
        
        # Status tracking
        self.startup_time = None
        self.total_interactions = 0
        self.total_movements = 0  # Track movement commands
        self.last_interaction_time = None
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        
        # Error tracking
        self.error_count = 0
        self.last_errors = []
        self.max_error_history = 10
        
        # Recovery mechanisms
        self.max_recovery_attempts = 3
        self.recovery_attempts = 0
        
        self.logger.info("🤖 Enhanced Ellee Robot with Movement Initializing...")
    
    def initialize_systems(self):
        """Initialize all robot systems including movement"""
        
        self.logger.info("🔧 Initializing Enhanced Ellee systems with movement...")
        
        initialization_steps = [
            ("Memory System", self._init_memory_system),
            ("Project Manager", self._init_project_manager),
            ("Enhanced Brain with Movement", self._init_enhanced_brain_with_movement)
        ]
        
        for step_name, init_func in initialization_steps:
            try:
                self.logger.info(f"🚀 Starting {step_name}...")
                success = init_func()
                
                if not success:
                    self.logger.error(f"❌ {step_name} initialization failed")
                    return False
                    
                self.logger.info(f"✅ {step_name} initialized successfully")
                
            except Exception as e:
                self.logger.error(f"💥 {step_name} initialization error: {e}")
                if self.debug_mode:
                    self.logger.debug(traceback.format_exc())
                return False
        
        # Post-initialization setup
        try:
            self._connect_systems()
            self.logger.info("✅ All systems initialized and connected successfully!")
            return True
        except Exception as e:
            self.logger.error(f"❌ System connection failed: {e}")
            return False
    
    def _init_memory_system(self):
        """Initialize memory system"""
        try:
            self.memory = ElleeBrainMemory(self.config)
            return True
        except Exception as e:
            self.logger.error(f"Memory system error: {e}")
            return False
    
    def _init_project_manager(self):
        """Initialize project manager"""
        try:
            if not self.memory:
                raise RuntimeError("Memory system must be initialized first")
            
            self.project_manager = AdvancedProjectManager(self.config, self.memory)
            return True
        except Exception as e:
            self.logger.error(f"Project manager error: {e}")
            return False
    
    def _init_enhanced_brain_with_movement(self):
        """Initialize enhanced brain with movement capabilities"""
        try:
            self.brain = EnhancedElleeBrainWithMovement(self.config)
            return True
        except Exception as e:
            self.logger.error(f"Enhanced brain with movement error: {e}")
            return False
    
    def _connect_systems(self):
        """Connect all systems together"""
        if self.brain and self.project_manager:
            self.brain.project_manager = self.project_manager
            self.logger.info("🔗 Systems connected successfully")
    
    def start(self, test_mode=False, debug_mode=False):
        """Start the Enhanced Ellee Robot with Movement"""
        
        self.test_mode = test_mode
        self.debug_mode = debug_mode
        
        # Update logging level if debug mode
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
        
        self.logger.info(f"🚀 Starting Enhanced Ellee Robot with Movement (Test: {test_mode}, Debug: {debug_mode})")
        
        # Check system health before starting
        healthy, issues = self.health_monitor.check_system_health()
        if not healthy:
            self.logger.warning(f"⚠️ System health issues detected: {issues}")
            if not self._confirm_start_with_issues():
                return False
        
        # Initialize systems
        if not self.initialize_systems():
            self.logger.error("❌ System initialization failed")
            return False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.is_running = True
        self.startup_time = datetime.now()
        
        # Start brain with error recovery
        try:
            self.brain.start()
        except Exception as e:
            self.logger.error(f"❌ Brain startup failed: {e}")
            return False
        
        # Print startup information
        self._print_startup_info_with_movement()
        
        # Run appropriate mode
        try:
            if test_mode:
                return self._run_test_mode_with_movement()
            else:
                return self._run_normal_mode_with_movement()
        except Exception as e:
            self.logger.error(f"❌ Runtime error: {e}")
            if self.debug_mode:
                self.logger.debug(traceback.format_exc())
            return False
    
    def _confirm_start_with_issues(self):
        """Ask user if they want to start despite system issues"""
        if self.test_mode:
            return True  # Auto-continue in test mode
        
        try:
            response = input("⚠️ System health issues detected. Continue anyway? (y/N): ")
            return response.lower().startswith('y')
        except KeyboardInterrupt:
            return False
    
    def _print_startup_info_with_movement(self):
        """Print enhanced startup information including movement capabilities"""
        
        print("\n" + "="*70)
        print("🤖 ENHANCED ELLEE ROBOT - ELECTRONICS ASSISTANT WITH MOVEMENT v3.0")
        print("="*70)
        print(f"🕒 Started: {self.startup_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Mode: {'Test Mode (120s)' if self.test_mode else 'Normal Operation'}")
        print(f"🔧 Debug: {'Enabled' if self.debug_mode else 'Disabled'}")
        
        # Movement system status
        if self.brain and hasattr(self.brain, 'movement_enabled'):
            movement_status = "✅ ENABLED" if self.brain.movement_enabled else "❌ DISABLED"
            print(f"🚶 Movement System: {movement_status}")
        
        # System health info
        stats = self.health_monitor.get_system_stats()
        if 'error' not in stats:
            print(f"💻 CPU: {stats['cpu_percent']:.1f}% | RAM: {stats['memory_percent']:.1f}% | Disk: {stats['disk_percent']:.1f}%")
        
        # Memory system info
        if self.memory:
            try:
                memory_stats = self.memory.get_memory_stats()
                print(f"🧠 Memory: {memory_stats['total_conversations']} conversations, {memory_stats['active_projects']} active projects")
            except Exception as e:
                print(f"🧠 Memory: Status unavailable ({e})")
        
        # Project manager info
        if self.project_manager:
            try:
                template_count = len(self.project_manager.project_templates)
                print(f"📋 Projects: {template_count} templates available")
            except Exception as e:
                print(f"📋 Projects: Status unavailable ({e})")
        
        print("\n🗣️  ENHANCED VOICE COMMANDS:")
        print("   📷 Vision Analysis:")
        print("     • 'Analyze these components' - Computer vision analysis")
        print("     • 'What do you see?' - Component identification")
        print("     • 'Check my circuit' - Circuit verification")
        
        print("   📋 Project Management:")
        print("     • 'Save this project as [name]' - Save current setup")
        print("     • 'What projects do I have?' - List your projects")
        print("     • 'Continue project [name]' - Resume working on project")
        print("     • 'Create new project' - Start new project")
        
        print("   🚶 MOVEMENT COMMANDS (NEW!):")
        print("     • 'Move forward' / 'Go forward' - Move robot forward")
        print("     • 'Move backward' / 'Go back' - Move robot backward")
        print("     • 'Turn left' / 'Turn right' - Rotate robot")
        print("     • 'Move left' / 'Move right' - Strafe sideways")
        print("     • 'Spin around' - Rotate in place")
        print("     • 'Dance' / 'Show me your moves' - Dance mode")
        print("     • 'Come here' - Approach user")
        print("     • 'Stop' / 'Emergency stop' - Stop all movement")
        
        print("   🧠 Memory & Learning:")
        print("     • 'What do you remember?' - Memory statistics")
        print("     • 'What have we learned?' - Learning progress")
        
        print("   📚 Educational Conversations:")
        print("     • 'Tell me about Arduino' - Electronics education")
        print("     • 'How does a buzzer work?' - Component explanations")
        print("     • 'What can I build?' - Project suggestions")
        
        print("\n📷 CAMERA FEATURES:")
        print("   • Automatic component detection and analysis")
        print("   • Project documentation with photos")
        print("   • Person detection for conversation management")
        
        print("\n⌨️  KEYBOARD COMMANDS (while running):")
        print("   • 's' - Show detailed status (including movement)")
        print("   • 'm' - Memory statistics") 
        print("   • 'p' - Project summary")
        print("   • 'h' - System health check")
        print("   • 'v' - Vision preview (10 seconds)")
        print("   • 'r' - Recovery/restart systems")
        print("   • 'o' - Movement status and commands")
        print("   • 'q' - Quit gracefully")
        
        print("\n🛡️  SYSTEM FEATURES:")
        print("   • Automatic error recovery")
        print("   • System health monitoring")
        print("   • Conversation memory backup")
        print("   • Performance optimization")
        print("   • Movement safety controls")
        
        print("="*70)
        print("✅ Ellee is ready with MOVEMENT! Start talking or show electronics!")
        print("💡 Say 'Hello Ellee' to begin, or 'Move forward' to test movement!")
        print("🚶 Try: 'Move forward', 'Turn left', 'Dance', or 'Come here'")
        print("="*70 + "\n")
    
    def _run_normal_mode_with_movement(self):
        """Run in normal operational mode with movement monitoring"""
        
        self.logger.info("🤖 Enhanced Ellee with movement is now running in normal mode...")
        
        # Start monitoring threads
        threads = [
            threading.Thread(target=self._status_monitor_with_movement, daemon=True),
            threading.Thread(target=self._keyboard_monitor_with_movement, daemon=True),
            threading.Thread(target=self._health_monitor_loop, daemon=True),
            threading.Thread(target=self._error_recovery_monitor, daemon=True),
            threading.Thread(target=self._movement_monitor, daemon=True)  # New movement monitor
        ]
        
        for thread in threads:
            thread.start()
        
        try:
            # Main run loop
            while self.is_running:
                time.sleep(1)
                
                # Update interaction and movement tracking
                if self.brain:
                    try:
                        status = self.brain.get_enhanced_status()
                        
                        # Track interactions
                        if status['conversation_length'] > 0:
                            self.total_interactions = status['conversation_length']
                            self.last_interaction_time = datetime.now()
                        
                        # Track movements
                        if status.get('movement_status', {}).get('total_movements', 0) > 0:
                            self.total_movements = status['movement_status']['total_movements']
                            
                    except Exception as e:
                        self._handle_error(f"Status update error: {e}")
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested via keyboard interrupt")
        except Exception as e:
            self.logger.error(f"❌ Runtime error in main loop: {e}")
            if self.debug_mode:
                self.logger.debug(traceback.format_exc())
        
        finally:
            self._shutdown_with_movement()
        
        return True
    
    def _run_test_mode_with_movement(self):
        """Run in test mode with movement capabilities"""
        
        self.logger.info("🧪 Running in enhanced test mode with movement for 120 seconds...")
        print("📸 Camera preview will be shown")
        print("🎤 Try voice commands")
        print("📋 Try project management features")
        print("🧠 Memory and learning features active")
        print("🚶 MOVEMENT COMMANDS ACTIVE - Try 'move forward', 'dance', etc!")
        
        start_time = time.time()
        test_duration = 120  # Extended test time
        
        try:
            while self.is_running and (time.time() - start_time) < test_duration:
                # Show vision preview if available
                if self.brain and self.brain.vision_system:
                    remaining_time = test_duration - (time.time() - start_time)
                    window_title = f"Enhanced Ellee with Movement - {remaining_time:.0f}s remaining"
                    
                    key = self.brain.vision_system.show_preview(window_title)
                    
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        self._print_detailed_status_with_movement()
                    elif key == ord('m'):
                        self._print_memory_stats()
                    elif key == ord('p'):
                        self._print_project_summary()
                    elif key == ord('h'):
                        self._print_health_status()
                    elif key == ord('o'):
                        self._print_movement_status()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Test mode interrupted")
        except Exception as e:
            self.logger.error(f"❌ Test mode error: {e}")
        
        finally:
            self._shutdown_with_movement()
        
        self.logger.info("✅ Enhanced test mode with movement completed")
        return True
    
    def _movement_monitor(self):
        """Monitor movement system continuously"""
        while self.is_running:
            try:
                if self.brain and hasattr(self.brain, 'motor_controller') and self.brain.motor_controller:
                    status = self.brain.motor_controller.get_movement_status()
                    
                    # Log movement activity
                    if status.get('is_moving'):
                        self.logger.debug(f"Movement active: {status.get('current_action')} at {status.get('current_speed')}%")
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Movement monitor error: {e}")
                time.sleep(10)
    
    def _status_monitor_with_movement(self):
        """Enhanced status monitor including movement info"""
        
        last_status_time = time.time()
        
        while self.is_running:
            current_time = time.time()
            
            # Print status every 60 seconds in debug mode, 300 seconds in normal mode
            interval = 60 if self.debug_mode else 300
            
            if not self.test_mode and (current_time - last_status_time) > interval:
                if self.debug_mode:
                    self._print_detailed_status_with_movement()
                else:
                    self._print_brief_status_with_movement()
                last_status_time = current_time
            
            time.sleep(5)
    
    def _keyboard_monitor_with_movement(self):
        """Enhanced keyboard monitor with movement commands"""
        
        try:
            while self.is_running:
                if not self.test_mode:
                    # In normal mode, check for input without blocking
                    try:
                        import select
                        import sys
                        
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            key = sys.stdin.read(1).lower()
                            self._handle_keyboard_command_with_movement(key)
                    except ImportError:
                        # Fallback for systems without select
                        time.sleep(1)
                    except Exception as e:
                        self.logger.debug(f"Keyboard monitor error: {e}")
                        time.sleep(1)
                else:
                    time.sleep(1)
        except Exception as e:
            self.logger.error(f"Keyboard monitor failed: {e}")
    
    def _handle_keyboard_command_with_movement(self, key):
        """Handle keyboard commands including movement"""
        
        try:
            if key == 's':
                self._print_detailed_status_with_movement()
            elif key == 'm':
                self._print_memory_stats()
            elif key == 'p':
                self._print_project_summary()
            elif key == 'h':
                self._print_health_status()
            elif key == 'v':
                self._toggle_vision_preview()
            elif key == 'r':
                self._manual_recovery()
            elif key == 'e':
                self._print_error_history()
            elif key == 'o':  # New: movement status
                self._print_movement_status()
            elif key == 'q':
                self.logger.info("🛑 Shutdown requested via keyboard")
                self.is_running = False
            else:
                # Show help for unknown keys
                self._print_keyboard_help_with_movement()
        except Exception as e:
            self.logger.error(f"Keyboard command error: {e}")
    
    def _print_keyboard_help_with_movement(self):
        """Print keyboard command help including movement"""
        print("\n⌨️  KEYBOARD COMMANDS:")
        print("  s - Detailed Status (including movement)")
        print("  m - Memory Statistics")
        print("  p - Project Summary")
        print("  h - System Health")
        print("  v - Vision Preview")
        print("  r - Manual Recovery")
        print("  e - Error History")
        print("  o - Movement Status")
        print("  q - Quit")
        print()
    
    def _print_brief_status_with_movement(self):
        """Print brief system status including movement"""
        if self.startup_time:
            uptime = datetime.now() - self.startup_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            status_line = f"🤖 Ellee Status: {uptime_str} uptime"
            
            if self.brain:
                try:
                    brain_status = self.brain.get_enhanced_status()
                    status_line += f" | State: {brain_status['state'].upper()}"
                    status_line += f" | Person: {'Yes' if brain_status['person_detected'] else 'No'}"
                    
                    # Add movement info
                    if brain_status.get('movement_enabled'):
                        movement_status = brain_status.get('movement_status', {})
                        if movement_status.get('is_moving'):
                            status_line += f" | Moving: {movement_status.get('current_action', 'unknown')}"
                        else:
                            status_line += " | Moving: No"
                    
                except:
                    status_line += " | Brain: Unknown"
            
            print(status_line)
    
    def _print_detailed_status_with_movement(self):
        """Print detailed system status including movement"""
        
        print("\n📊 ENHANCED ELLEE DETAILED STATUS WITH MOVEMENT")
        print("-" * 60)
        
        # Uptime and basic info
        if self.startup_time:
            uptime = datetime.now() - self.startup_time
            print(f"⏱️  Uptime: {uptime}")
        
        print(f"🤝 Total Interactions: {self.total_interactions}")
        print(f"🚶 Total Movements: {self.total_movements}")
        print(f"🔧 Debug Mode: {self.debug_mode}")
        print(f"❌ Error Count: {self.error_count}")
        
        if self.last_interaction_time:
            time_since = datetime.now() - self.last_interaction_time
            print(f"🕒 Last Interaction: {time_since.seconds}s ago")
        
        # Brain status
        if self.brain:
            try:
                status = self.brain.get_enhanced_status()
                print(f"🤖 Brain State: {status['state'].upper()}")
                print(f"👤 Person Detected: {status['person_detected']}")
                print(f"🗣️  Speaking: {status['is_speaking']}")
                print(f"💬 Conversation Active: {status.get('conversation_active', 'Unknown')}")
                print(f"📋 Project Mode: {status['project_mode']}")
                print(f"🎯 Current Project: {status['current_project'] or 'None'}")
                print(f"📈 Teaching Success: {status['teaching_success_rate']}")
                
                # Movement status
                print(f"🚶 Movement Enabled: {status['movement_enabled']}")
                if status['movement_enabled']:
                    mv_status = status.get('movement_status', {})
                    print(f"🚶 Currently Moving: {mv_status.get('is_moving', False)}")
                    if mv_status.get('is_moving'):
                        print(f"🚶 Current Action: {mv_status.get('current_action', 'unknown')}")
                        print(f"🚶 Current Speed: {mv_status.get('current_speed', 0)}%")
                    print(f"🚶 Emergency Stop: {mv_status.get('emergency_stop_active', False)}")
                    print(f"🚶 Total Movements: {mv_status.get('total_movements', 0)}")
                
            except Exception as e:
                print(f"🤖 Brain Status: Error ({e})")
        
        # System health
        stats = self.health_monitor.get_system_stats()
        if 'error' not in stats:
            print(f"💻 CPU: {stats['cpu_percent']:.1f}%")
            print(f"🧠 Memory: {stats['memory_percent']:.1f}% ({stats['memory_available_gb']:.1f}GB free)")
            print(f"💾 Disk: {stats['disk_percent']:.1f}% ({stats['disk_free_gb']:.1f}GB free)")
        
        print("-" * 60 + "\n")
    
    def _print_movement_status(self):
        """Print detailed movement system status"""
        
        print("\n🚶 MOVEMENT SYSTEM STATUS")
        print("-" * 50)
        
        if self.brain and hasattr(self.brain, 'movement_enabled'):
            if self.brain.movement_enabled:
                try:
                    if self.brain.motor_controller:
                        status = self.brain.motor_controller.get_movement_status()
                        history = self.brain.motor_controller.get_movement_history_summary()
                        
                        print("✅ Movement system is ENABLED")
                        print(f"🚶 Currently Moving: {status.get('is_moving', False)}")
                        print(f"🎯 Current Action: {status.get('current_action', 'stopped')}")
                        print(f"⚡ Current Speed: {status.get('current_speed', 0)}%")
                        print(f"🚨 Emergency Stop: {status.get('emergency_stop_active', False)}")
                        print(f"📊 Movement History: {history}")
                        
                        # Available commands
                        if self.brain.movement_processor:
                            commands = self.brain.movement_processor.get_available_commands()
                            print("\n📋 Available Voice Commands:")
                            for category, cmd_list in commands.items():
                                print(f"   {category}: {', '.join(cmd_list)}")
                    else:
                        print("❌ Movement controller not available")
                except Exception as e:
                    print(f"❌ Error getting movement status: {e}")
            else:
                print("❌ Movement system is DISABLED")
        else:
            print("❌ Movement system not available")
        
        print("-" * 50 + "\n")
    
    def _shutdown_with_movement(self):
        """Enhanced shutdown including movement system"""
        
        self.logger.info("🔄 Shutting down Enhanced Ellee with Movement...")
        
        shutdown_steps = [
            ("Movement System", self._shutdown_movement),
            ("Brain System", self._shutdown_brain),
            ("Memory Backup", self._backup_memory),
            ("System Cleanup", self._cleanup_resources)
        ]
        
        for step_name, shutdown_func in shutdown_steps:
            try:
                self.logger.info(f"🔄 {step_name}...")
                shutdown_func()
                self.logger.info(f"✅ {step_name} completed")
            except Exception as e:
                self.logger.error(f"❌ {step_name} failed: {e}")
        
        # Print shutdown summary
        self._print_shutdown_summary_with_movement()
        
        self.logger.info("😴 Enhanced Ellee with movement has shut down successfully")
    
    def _shutdown_movement(self):
        """Shutdown movement system safely"""
        if self.brain and hasattr(self.brain, 'motor_controller') and self.brain.motor_controller:
            try:
                self.brain.motor_controller.stop_all_safe()
                self.brain.motor_controller.cleanup_enhanced()
                print("🛑 Movement system stopped and cleaned up")
            except Exception as e:
                print(f"⚠️ Movement cleanup error: {e}")
    
    def _shutdown_brain(self):
        """Shutdown brain system"""
        if self.brain:
            self.brain.stop()
    
    def _backup_memory(self):
        """Backup memory data"""
        if self.memory:
            try:
                backup_file = f"logs/ellee_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.memory.export_memories(backup_file)
                self.logger.info(f"💾 Memory exported to {backup_file}")
            except Exception as e:
                self.logger.error(f"⚠️ Could not export memory: {e}")
    
    def _cleanup_resources(self):
        """Cleanup system resources"""
        # Close any remaining windows
        cv2.destroyAllWindows()
        
        # Log final statistics
        if self.startup_time:
            total_runtime = datetime.now() - self.startup_time
            self.logger.info(f"⏱️ Total runtime: {total_runtime}")
    
    def _print_shutdown_summary_with_movement(self):
        """Print shutdown summary including movement stats"""
        
        print("\n📊 SHUTDOWN SUMMARY WITH MOVEMENT")
        print("-" * 50)
        
        if self.startup_time:
            total_runtime = datetime.now() - self.startup_time
            print(f"⏱️ Total runtime: {total_runtime}")
        
        print(f"🤝 Total interactions: {self.total_interactions}")
        print(f"🚶 Total movements: {self.total_movements}")
        print(f"❌ Total errors: {self.error_count}")
        print(f"🔄 Recovery attempts: {self.recovery_attempts}")
        
        # Memory stats
        if self.memory:
            try:
                stats = self.memory.get_memory_stats()
                print(f"💾 Final memory size: {stats['memory_size_mb']} MB")
                print(f"💬 Conversations saved: {stats['total_conversations']}")
            except:
                pass
        
        print("-" * 50)
    
    def _health_monitor_loop(self):
        """Continuous system health monitoring"""
        while self.is_running:
            try:
                current_time = time.time()
                
                if current_time - self.last_health_check > self.health_check_interval:
                    healthy, issues = self.health_monitor.check_system_health()
                    
                    if not healthy:
                        self.logger.warning(f"⚠️ System health issues: {', '.join(issues)}")
                    
                    self.last_health_check = current_time
                
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                time.sleep(10)
    
    def _error_recovery_monitor(self):
        """Monitor for errors and attempt recovery"""
        while self.is_running:
            try:
                time.sleep(30)  # Check every 30 seconds
                
                # Check if brain is responsive
                if self.brain and hasattr(self.brain, 'is_running'):
                    if not self.brain.is_running and self.recovery_attempts < self.max_recovery_attempts:
                        self.logger.warning("🔄 Attempting brain recovery...")
                        self._attempt_brain_recovery()
                
            except Exception as e:
                self.logger.error(f"Recovery monitor error: {e}")
                time.sleep(60)
    
    def _attempt_brain_recovery(self):
        """Attempt to recover brain system"""
        try:
            self.recovery_attempts += 1
            self.logger.info(f"🔄 Brain recovery attempt {self.recovery_attempts}/{self.max_recovery_attempts}")
            
            # Stop current brain
            if self.brain:
                self.brain.stop()
                time.sleep(2)
            
            # Reinitialize brain
            self.brain = EnhancedElleeBrainWithMovement(self.config)
            if self.project_manager:
                self.brain.project_manager = self.project_manager
            
            # Start brain
            self.brain.start()
            
            self.logger.info("✅ Brain recovery successful")
            self.recovery_attempts = 0  # Reset counter on success
            
        except Exception as e:
            self.logger.error(f"❌ Brain recovery failed: {e}")
            if self.recovery_attempts >= self.max_recovery_attempts:
                self.logger.error("❌ Maximum recovery attempts reached")
    
    def _handle_error(self, error_msg):
        """Handle and track errors"""
        self.error_count += 1
        self.last_errors.append({
            'timestamp': datetime.now().isoformat(),
            'message': error_msg
        })
        
        # Keep only recent errors
        if len(self.last_errors) > self.max_error_history:
            self.last_errors.pop(0)
        
        self.logger.error(error_msg)
    
    def _print_memory_stats(self):
        """Print enhanced memory system statistics"""
        
        print("\n🧠 ENHANCED MEMORY SYSTEM STATISTICS")
        print("-" * 50)
        
        if self.memory:
            try:
                stats = self.memory.get_memory_stats()
                
                print(f"💬 Total Conversations: {stats['total_conversations']}")
                print(f"👥 Known People: {stats['known_people']}")
                print(f"📋 Active Projects: {stats['active_projects']}")
                print(f"✅ Completed Projects: {stats['completed_projects']}")
                print(f"💾 Memory Size: {stats['memory_size_mb']} MB")
                print(f"🕒 Last Interaction: {stats['last_interaction']}")
                
                # Additional memory insights
                if stats['total_conversations'] > 0:
                    avg_projects = (stats['active_projects'] + stats['completed_projects']) / max(stats['known_people'], 1)
                    print(f"📊 Avg Projects per Person: {avg_projects:.1f}")
                
            except Exception as e:
                print(f"❌ Memory system error: {e}")
        else:
            print("❌ Memory system not available")
        
        print("-" * 50 + "\n")
    
    def _print_project_summary(self):
        """Print enhanced project management summary"""
        
        print("\n📋 ENHANCED PROJECT MANAGEMENT SUMMARY")
        print("-" * 50)
        
        if self.project_manager:
            try:
                summary = self.project_manager.get_all_projects_summary()
                
                print(f"📊 Total Projects: {summary['total_projects']}")
                print(f"✅ Completed: {summary['completed_projects']}")
                print(f"🔄 Active: {summary['active_projects']}")
                print(f"📈 Average Completion: {summary['average_completion_rate']:.1f}%")
                print(f"⏱️  Total Learning Time: {summary['total_learning_time_hours']:.1f} hours")
                
                skill_progression = summary['skill_progression']
                print(f"🎯 Skill Progression:")
                print(f"   • Beginner: {skill_progression['beginner_projects']}")
                print(f"   • Intermediate: {skill_progression['intermediate_projects']}")
                print(f"   • Advanced: {skill_progression['advanced_projects']}")
                
                if summary['recent_activity']:
                    print(f"📈 Recent Activity:")
                    for activity in summary['recent_activity'][:3]:
                        print(f"   • {activity['name']}: {activity['completion_percentage']:.0f}% ({activity['status']})")
                
                # Project templates info
                template_count = len(self.project_manager.project_templates)
                print(f"📚 Available Templates: {template_count}")
                
            except Exception as e:
                print(f"❌ Project manager error: {e}")
        else:
            print("❌ Project manager not available")
        
        print("-" * 50 + "\n")
    
    def _print_health_status(self):
        """Print system health status"""
        
        print("\n🛡️  SYSTEM HEALTH STATUS")
        print("-" * 50)
        
        healthy, issues = self.health_monitor.check_system_health()
        
        if healthy:
            print("✅ System is healthy")
        else:
            print("⚠️ System health issues detected:")
            for issue in issues:
                print(f"   • {issue}")
        
        # Detailed stats
        stats = self.health_monitor.get_system_stats()
        if 'error' not in stats:
            print(f"\n📊 Current Stats:")
            print(f"   CPU: {stats['cpu_percent']:.1f}%")
            print(f"   Memory: {stats['memory_percent']:.1f}%")
            print(f"   Disk: {stats['disk_percent']:.1f}%")
            print(f"   Uptime: {stats['uptime_hours']:.1f} hours")
        else:
            print(f"❌ Health monitoring error: {stats['error']}")
        
        print("-" * 50 + "\n")
    
    def _print_error_history(self):
        """Print recent error history"""
        
        print("\n❌ ERROR HISTORY")
        print("-" * 50)
        
        if self.last_errors:
            print(f"Total errors: {self.error_count}")
            print(f"Recent errors ({len(self.last_errors)}):")
            
            for error in self.last_errors[-5:]:  # Show last 5 errors
                timestamp = datetime.fromisoformat(error['timestamp']).strftime('%H:%M:%S')
                print(f"   {timestamp}: {error['message']}")
        else:
            print("✅ No recent errors")
        
        print("-" * 50 + "\n")
    
    def _manual_recovery(self):
        """Manual system recovery"""
        
        print("\n🔄 MANUAL SYSTEM RECOVERY")
        print("-" * 50)
        
        try:
            print("🔄 Attempting brain recovery...")
            self._attempt_brain_recovery()
            
            print("🔄 Clearing error history...")
            self.error_count = 0
            self.last_errors = []
            self.recovery_attempts = 0
            
            print("✅ Manual recovery completed")
            
        except Exception as e:
            print(f"❌ Manual recovery failed: {e}")
        
        print("-" * 50 + "\n")
    
    def _toggle_vision_preview(self):
        """Toggle vision preview window with enhanced features"""
        
        if self.brain and self.brain.vision_system:
            print("📷 Showing enhanced vision preview for 15 seconds...")
            print("   Press 'q' to exit early")
            print("   Press 's' for status overlay")
            
            start_time = time.time()
            duration = 15
            show_overlay = False
            
            while time.time() - start_time < duration:
                remaining = duration - (time.time() - start_time)
                
                if show_overlay:
                    # Create status overlay
                    frame = self.brain.vision_system.get_current_frame()
                    if frame is not None:
                        # Add text overlay
                        cv2.putText(frame, f"Time: {remaining:.1f}s", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.putText(frame, f"State: {self.brain.state.value}", (10, 70), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        # Add movement status if available
                        if hasattr(self.brain, 'motor_controller') and self.brain.motor_controller:
                            mv_status = self.brain.motor_controller.get_movement_status()
                            if mv_status.get('is_moving'):
                                cv2.putText(frame, f"Moving: {mv_status.get('current_action', 'unknown')}", 
                                          (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                        
                        cv2.imshow("Enhanced Ellee Vision Preview", frame)
                else:
                    window_title = f"Enhanced Ellee Vision Preview - {remaining:.1f}s"
                    key = self.brain.vision_system.show_preview(window_title)
                
                key = cv2.waitKey(30) & 0xFF
                
                if key == ord('q') or key == 27:  # ESC
                    break
                elif key == ord('s'):
                    show_overlay = not show_overlay
                
                time.sleep(0.033)
            
            cv2.destroyAllWindows()
            print("📷 Vision preview closed")
        else:
            print("❌ Vision system not available")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.is_running = False

def run_comprehensive_system_tests():
    """Run comprehensive system tests with enhanced diagnostics"""
    
    logger = logging.getLogger(__name__)
    logger.info("🧪 Running Enhanced Ellee Comprehensive System Tests with Movement...")
    print("=" * 60)
    
    tests = [
        ("Speech Recognition", test_fixed_speech),
        ("Text-to-Speech", test_tts_wrapper), 
        ("GPT Vision", test_vision_fallback),
    ]
    
    results = {}
    detailed_results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔬 Testing {test_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            results[test_name] = result
            detailed_results[test_name] = {
                'success': result,
                'duration': duration,
                'error': None
            }
            
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} {test_name} ({duration:.2f}s)")
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            results[test_name] = False
            detailed_results[test_name] = {
                'success': False,
                'duration': duration,
                'error': str(e)
            }
            
            print(f"❌ FAILED {test_name}: {e}")
    
    # Additional system checks
    print(f"\n🔍 Additional System Checks...")
    
    # Check dependencies
    try:
        import cv2, numpy, pygame, speech_recognition
        print("✅ Core dependencies available")
        results['Dependencies'] = True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        results['Dependencies'] = False
    
    # Check movement system
    try:
        from enhanced_motor_control import ElleeMotorController
        from movement_commands import MovementCommandProcessor
        print("✅ Movement system modules available")
        results['Movement_Modules'] = True
    except ImportError as e:
        print(f"❌ Movement modules missing: {e}")
        results['Movement_Modules'] = False
    
    # Check system resources
    try:
        import psutil
        stats = psutil.virtual_memory()
        if stats.available > 1024**3:  # At least 1GB available
            print("✅ Sufficient memory available")
            results['Memory'] = True
        else:
            print("⚠️ Low memory warning")
            results['Memory'] = False
    except:
        print("⚠️ Could not check system memory")
        results['Memory'] = False
    
    # Print comprehensive results
    print("\n" + "=" * 60)
    print("🧪 COMPREHENSIVE SYSTEM TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        
        if test_name in detailed_results:
            details = detailed_results[test_name]
            duration_str = f" ({details['duration']:.2f}s)"
            error_str = f" - {details['error']}" if details['error'] else ""
        else:
            duration_str = ""
            error_str = ""
        
        print(f"{status} {test_name}{duration_str}{error_str}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All systems operational including movement!")
        return True
    elif passed >= total * 0.7:  # 70% pass rate
        print("⚠️ Most systems operational with some issues")
        return True
    else:
        print("❌ Multiple system failures detected")
        return False

def main():
    """Enhanced main entry point with movement capabilities"""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Ellee Robot with Movement - Electronics Assistant v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ellee_main_enhanced_with_movement.py                    # Normal operation with movement
  python ellee_main_enhanced_with_movement.py --test-mode        # Test mode (120 seconds)
  python ellee_main_enhanced_with_movement.py --debug           # Debug mode with verbose logging
  python ellee_main_enhanced_with_movement.py --system-test     # Comprehensive system tests
  
Voice Commands Available:
  Movement: "move forward", "turn left", "dance", "stop"
  Electronics: "analyze components", "what do you see"
  Projects: "save project", "what projects do I have"
        """
    )
    
    parser.add_argument("--test-mode", action="store_true", 
                       help="Run in test mode for 120 seconds with preview and movement")
    parser.add_argument("--debug", action="store_true", 
                       help="Enable debug mode with verbose output and logging")
    parser.add_argument("--memory-stats", action="store_true", 
                       help="Show memory statistics and exit")
    parser.add_argument("--system-test", action="store_true", 
                       help="Run comprehensive system tests and exit")
    parser.add_argument("--movement-test", action="store_true", 
                       help="Run movement system tests and exit")
    parser.add_argument("--health-check", action="store_true",
                       help="Run system health check and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.debug)
    
    try:
        # Handle special modes
        if args.system_test:
            return run_comprehensive_system_tests()
        
        if args.movement_test:
            # Run movement tests
            import subprocess
            result = subprocess.run([sys.executable, "test_movement_system.py", "--quick"], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return result.returncode == 0
        
        if args.health_check:
            monitor = SystemHealthMonitor()
            healthy, issues = monitor.check_system_health()
            stats = monitor.get_system_stats()
            
            print("🛡️ SYSTEM HEALTH CHECK")
            print("=" * 40)
            
            if healthy:
                print("✅ System is healthy")
            else:
                print("⚠️ Issues detected:")
                for issue in issues:
                    print(f"  • {issue}")
            
            if 'error' not in stats:
                print(f"\n📊 System Stats:")
                print(f"CPU: {stats['cpu_percent']:.1f}%")
                print(f"Memory: {stats['memory_percent']:.1f}%")
                print(f"Disk: {stats['disk_percent']:.1f}%")
            
            return healthy
        
        if args.memory_stats:
            try:
                memory = ElleeBrainMemory(Config)
                stats = memory.get_memory_stats()
                
                print("🧠 ENHANCED ELLEE MEMORY STATISTICS")
                print("=" * 50)
                for key, value in stats.items():
                    print(f"{key}: {value}")
                
                return True
            except Exception as e:
                logger.error(f"❌ Could not load memory stats: {e}")
                return False
        
        # Run main application with movement
        logger.info("🚀 Starting Enhanced Ellee Robot with Movement v3.0")
        
        robot = EnhancedElleeRobotWithMovement(Config)
        return robot.start(test_mode=args.test_mode, debug_mode=args.debug)
        
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        return True
    except Exception as e:
        logger.error(f"❌ Enhanced Ellee with movement failed to start: {e}")
        if args.debug:
            logger.debug(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)