# config.py - File konfigurasi untuk robot Ellee
import os

class Config:
    # OpenAI API Configuration
    OPENAI_API_KEY = "******************"
    
    # TTS Configuration
    TTS_ENGINE = "elevenlabs"  # Options: "gtts", "elevenlabs"
    
    # ElevenLabs API Configuration (optional)
    ELEVENLABS_API_KEY = "*******************"
    ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Default voice Rachel
    
    # gTTS Configuration
    GTTS_LANGUAGE = "en"  # Language code
    
    # Robot Configuration
    ROBOT_NAME = "Ellee"
    
    # Camera Configuration
    CAMERA_INDEX = 0  # Berdasarkan hasil test
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    
    # Audio Configuration
    SAMPLE_RATE = 48000  # Based on test results
    CHUNK_SIZE = 1024    # Based on test results  
    MICROPHONE_DEVICE_INDEX = 11  # C270 HD WEBCAM USB Audio
    
    # Vision Analysis Configuration
    VISION_ANALYSIS_ENABLED = True
    VISION_MAX_TOKENS = 400  # For GPT Vision responses
    VISION_IMAGE_QUALITY = "high"  # "low" or "high"
    
    # Electronics Analysis Settings
    SAVE_ANALYSIS_IMAGES = True  # Save images for memory system
    ANALYSIS_HISTORY_LIMIT = 50  # Number of analyses to remember
    
    # Conversation Settings
    MAX_CONVERSATION_HISTORY = 10
    LISTENING_TIMEOUT = 10  # seconds
    RESPONSE_TIMEOUT = 30   # seconds

# Untuk development, bisa override dari environment variables
if os.getenv('OPENAI_API_KEY'):
    Config.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
if os.getenv('ELEVENLABS_API_KEY'):
    Config.ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')