# tts_wrapper.py - Text-to-Speech wrapper untuk Python 3.6
import requests
import os
import pygame
from gtts import gTTS
import tempfile
import time

class TTSEngine:
    def __init__(self, config):
        self.config = config
        pygame.mixer.init()
        
    def speak(self, text):
        """Konversi text ke speech dan play audio"""
        if self.config.TTS_ENGINE == "elevenlabs":
            return self._speak_elevenlabs(text)
        else:
            return self._speak_gtts(text)
    
    def _speak_elevenlabs(self, text):
        """Gunakan ElevenLabs API dengan HTTP requests"""
        if not self.config.ELEVENLABS_API_KEY or self.config.ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
            print("⚠ ElevenLabs API key not configured, falling back to gTTS")
            return self._speak_gtts(text)
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.config.ELEVENLABS_VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.config.ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name
            
            # Play audio
            self._play_audio(tmp_file_path)
            
            # Clean up
            os.unlink(tmp_file_path)
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"ElevenLabs API error: {e}, falling back to gTTS")
            return self._speak_gtts(text)
        except Exception as e:
            print(f"Error playing ElevenLabs audio: {e}, falling back to gTTS")
            return self._speak_gtts(text)
    
    def _speak_gtts(self, text):
        """Gunakan Google Text-to-Speech"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=self.config.GTTS_LANGUAGE, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file_path = tmp_file.name
            
            tts.save(tmp_file_path)
            
            # Play audio
            self._play_audio(tmp_file_path)
            
            # Clean up
            os.unlink(tmp_file_path)
            return True
            
        except Exception as e:
            print(f"gTTS error: {e}")
            return False
    
    def _play_audio(self, file_path):
        """Play audio file menggunakan pygame"""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def is_speaking(self):
        """Check apakah sedang berbicara"""
        return pygame.mixer.music.get_busy()

# Test function
def test_tts_wrapper():
    """Test TTS wrapper"""
    from config import Config
    
    print("Testing TTS Engine...")
    tts = TTSEngine(Config)
    
    test_text = "Hello, I am Ellee, your friendly robot assistant!"
    print(f"Speaking: {test_text}")
    
    success = tts.speak(test_text)
    
    if success:
        print("✅ TTS test successful!")
        return True
    else:
        print("❌ TTS test failed")
        return False

if __name__ == "__main__":
    test_tts_wrapper()