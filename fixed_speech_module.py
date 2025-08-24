# fixed_speech_module.py - Speech recognition dengan audio context fix
import speech_recognition as sr
import pyaudio
import threading
import time
import queue

class FixedSpeechListener:
    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.result_queue = queue.Queue()
        self.listen_thread = None
        self._audio_lock = threading.Lock()  # Add lock untuk prevent conflicts
        
        # Setup microphone dengan fallback options
        self._setup_microphone()
        
        # Optimize recognizer settings untuk conversation yang lebih natural
        self.recognizer.energy_threshold = 400  
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2   
        self.recognizer.phrase_threshold = 0.2  
        self.recognizer.non_speaking_duration = 0.8  
        
        print("🎤 Fixed speech recognition system initialized")
    
    def _setup_microphone(self):
        """Setup microphone dengan multiple fallback options"""
        print("Setting up microphone...")
        
        # Option 1: Use configured device index
        if hasattr(self.config, 'MICROPHONE_DEVICE_INDEX') and self.config.MICROPHONE_DEVICE_INDEX is not None:
            try:
                print(f"Trying configured device index: {self.config.MICROPHONE_DEVICE_INDEX}")
                sample_rate = getattr(self.config, 'SAMPLE_RATE', 44100)
                chunk_size = getattr(self.config, 'CHUNK_SIZE', 1024)
                
                self.microphone = sr.Microphone(
                    device_index=self.config.MICROPHONE_DEVICE_INDEX,
                    sample_rate=sample_rate,
                    chunk_size=chunk_size
                )
                
                # Test microphone dengan lock
                with self._audio_lock:
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print(f"✅ Using configured microphone (device {self.config.MICROPHONE_DEVICE_INDEX})")
                return
                
            except Exception as e:
                print(f"⚠ Configured microphone failed: {e}")
        
        # Option 2: Try PulseAudio default
        try:
            print("Trying PulseAudio default microphone...")
            self.microphone = sr.Microphone()
            
            # Test microphone dengan lock
            with self._audio_lock:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✅ Using PulseAudio default microphone")
            return
            
        except Exception as e:
            print(f"⚠ PulseAudio default failed: {e}")
            raise RuntimeError("No working microphone found")
    
    def start_listening(self):
        """Start listening asynchronously dengan improved thread management"""
        if not self.is_listening and self.microphone:
            self.is_listening = True
            
            # Stop previous thread if exists
            if self.listen_thread and self.listen_thread.is_alive():
                print("🔄 Stopping previous listening thread...")
                self.is_listening = False
                self.listen_thread.join(timeout=2)
            
            # Start new thread
            self.listen_thread = threading.Thread(target=self._listen_worker)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            print("🎤 Started listening...")
    
    def stop_listening(self):
        """Stop listening dengan proper cleanup"""
        if self.is_listening:
            self.is_listening = False
            if self.listen_thread and self.listen_thread.is_alive():
                self.listen_thread.join(timeout=3)
            print("🎤 Stopped listening")
    
    def get_speech(self, timeout=None):
        """Get speech recognition result"""
        try:
            if timeout:
                result = self.result_queue.get(timeout=timeout)
            else:
                result = self.result_queue.get_nowait()
            return result
        except queue.Empty:
            return None
    
    def _listen_worker(self):
        """Worker thread for continuous listening dengan improved error handling"""
        consecutive_errors = 0
        max_consecutive_errors = 3  # Reduced tolerance
        
        while self.is_listening:
            try:
                # Use audio lock untuk prevent context manager conflicts
                with self._audio_lock:
                    if not self.is_listening:  # Check again after acquiring lock
                        break
                        
                    # Listen for audio dengan proper timeout
                    with self.microphone as source:
                        audio = self.recognizer.listen(
                            source, 
                            timeout=2,        # Longer timeout untuk natural conversation
                            phrase_time_limit=8  # Allow longer phrases
                        )
                
                # Process audio in background tanpa lock
                threading.Thread(target=self._process_audio, args=(audio,), daemon=True).start()
                consecutive_errors = 0
                
            except sr.WaitTimeoutError:
                # Normal timeout, continue
                consecutive_errors = 0
                continue
                
            except Exception as e:
                consecutive_errors += 1
                error_msg = str(e)
                
                # Handle specific audio errors
                if "context manager" in error_msg:
                    print(f"⚠ Audio context conflict, retrying... ({consecutive_errors}/{max_consecutive_errors})")
                    time.sleep(0.5)
                elif "Device unavailable" in error_msg:
                    print(f"⚠ Audio device unavailable, retrying... ({consecutive_errors}/{max_consecutive_errors})")
                    time.sleep(1)
                else:
                    print(f"⚠ Listen error: {e} ({consecutive_errors}/{max_consecutive_errors})")
                
                if consecutive_errors >= max_consecutive_errors:
                    print("❌ Too many consecutive errors, stopping listener")
                    self.is_listening = False
                    break
                
                time.sleep(0.5)
    
    def _process_audio(self, audio):
        """Process audio for speech recognition"""
        try:
            # Try Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-US')
            if text.strip():
                print(f"👂 Heard: {text}")
                self.result_queue.put(text.strip())
                
        except sr.UnknownValueError:
            # Speech tidak bisa dipahami (normal)
            pass
        except sr.RequestError as e:
            print(f"⚠ Speech recognition service error: {e}")
        except Exception as e:
            print(f"⚠ Audio processing error: {e}")

class ConversationManager:
    def __init__(self, config):
        self.config = config
        self.conversation_history = []
        self.max_history = config.MAX_CONVERSATION_HISTORY
    
    def add_message(self, role, content):
        """Tambah pesan ke history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Limit history size
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
    
    def get_conversation_for_ai(self):
        """Format conversation untuk AI dengan personality yang lebih detailed"""
        # Enhanced system message untuk electronics assistant
        messages = [{
            "role": "system",
            "content": f"You are {self.config.ROBOT_NAME}, a friendly and knowledgeable electronics assistant robot. "
                      f"You are enthusiastic about electronics, Arduino projects, and helping people learn. "
                      f"You speak in a conversational, detailed way - not too brief or robotic. "
                      f"You love to explain things clearly and give practical examples. "
                      f"You can see through your camera and recognize electronic components. "
                      f"When discussing projects, be specific about steps, components, and safety tips. "
                      f"Always be encouraging and patient, especially with beginners. "
                      f"Your responses should be 2-4 sentences long to be more conversational and helpful."
        }]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        return messages
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧠 Conversation history cleared")

# Test function yang aman
def test_fixed_speech():
    """Test fixed speech recognition"""
    from config import Config
    
    print("Testing Fixed Speech Recognition...")
    print("This will test microphone with improved error handling")
    
    try:
        listener = FixedSpeechListener(Config)
        listener.start_listening()
        
        print("\n🎤 Microphone is ready!")
        print("Say something clearly... (listening for 15 seconds)")
        print("Try saying: 'Hello Ellee' or 'How are you?'")
        
        start_time = time.time()
        heard_anything = False
        
        while time.time() - start_time < 15:
            speech = listener.get_speech()
            if speech:
                print(f"✅ Successfully recognized: '{speech}'")
                heard_anything = True
                
                # Continue listening for more
                print("Great! Keep talking or wait for timeout...")
            
            time.sleep(0.1)
        
        listener.stop_listening()
        
        if heard_anything:
            print("\n🎉 Fixed speech recognition is working perfectly!")
            return True
        else:
            print("\n⚠ No speech was recognized")
            return False
            
    except Exception as e:
        print(f"\n❌ Speech recognition test failed: {e}")
        return False

if __name__ == "__main__":
    test_fixed_speech()