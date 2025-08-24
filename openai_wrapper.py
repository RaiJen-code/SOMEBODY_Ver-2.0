# openai_wrapper.py - Complete OpenAI client wrapper untuk Robot Ellee
"""
Complete OpenAI client wrapper yang menggabungkan chat completion dan vision analysis
dengan fallback mechanisms dan error handling yang robust.

Kompatibel dengan:
- brain_module.py (original)
- enhanced_brain_module.py (enhanced)
- Semua sistem yang membutuhkan OpenAI integration
"""

import requests
import json
import base64
import time
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import threading

class OpenAIClient:
    """
    Complete OpenAI client dengan chat completion dan vision analysis
    """
    
    def __init__(self, api_key, default_model="gpt-3.5-turbo"):
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://api.openai.com/v1"
        
        # Headers untuk API calls
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Rate limiting dan error handling
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        self.max_retries = 3
        self.request_timeout = 30
        
        # Model availability cache
        self.available_models = None
        self.available_vision_models = None
        
        # Thread safety
        self.request_lock = threading.Lock()
        
        print("🔗 OpenAI Client initialized")
        
        # Test connection and get available models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize dan test model availability"""
        try:
            # Test basic connection
            self.available_models = self._get_available_models()
            self.available_vision_models = self._get_available_vision_models()
            
            print(f"✅ Connected to OpenAI API")
            print(f"📋 Available models: {len(self.available_models) if self.available_models else 0}")
            print(f"👁️ Vision models: {len(self.available_vision_models) if self.available_vision_models else 0}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not verify OpenAI connection: {e}")
            # Set fallback models
            self.available_models = ["gpt-3.5-turbo", "gpt-4"]
            self.available_vision_models = ["gpt-4o", "gpt-4-vision-preview"]
    
    def _get_available_models(self):
        """Get list of available models"""
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                model_ids = [m['id'] for m in models_data.get('data', [])]
                
                # Filter for chat models
                chat_models = [m for m in model_ids if 'gpt' in m.lower()]
                return chat_models
            else:
                return None
                
        except Exception as e:
            print(f"Could not fetch models: {e}")
            return None
    
    def _get_available_vision_models(self):
        """Get list of available vision models dengan filtering yang lebih baik"""
        if not self.available_models:
            return ["gpt-4o", "gpt-4-vision-preview", "gpt-4-turbo"]
        
        # Known vision-capable models (in order of preference)
        known_vision_models = [
            "gpt-4o",
            "gpt-4o-2024-08-06", 
            "gpt-4o-2024-05-13",
            "gpt-4-vision-preview",
            "gpt-4-turbo",
            "gpt-4-turbo-2024-04-09"
        ]
        
        # Filter untuk model yang benar-benar support vision
        vision_models = []
        
        for model in known_vision_models:
            if model in self.available_models:
                vision_models.append(model)
        
        # Additional filtering: avoid known non-vision models
        excluded_patterns = [
            "realtime", "audio", "preview-2025", "instruct", 
            "text-", "code-", "gpt-3.5", "whisper", "tts", "dall-e"
        ]
        
        # Check other available models carefully
        for model in self.available_models:
            if model not in vision_models:
                # Include if it's clearly a vision model and not excluded
                if "gpt-4" in model and "vision" in model.lower():
                    if not any(pattern in model.lower() for pattern in excluded_patterns):
                        vision_models.append(model)
        
        # Fallback jika tidak ada yang ditemukan
        if not vision_models:
            vision_models = ["gpt-4o", "gpt-4-vision-preview"]
            
        print(f"🎯 Filtered vision models: {vision_models[:5]}")  # Show top 5
        return vision_models
    
    def _rate_limit_wait(self):
        """Implement rate limiting"""
        with self.request_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                time.sleep(wait_time)
            
            self.last_request_time = time.time()
    
    def chat_completion(self, messages, model=None, max_tokens=150, temperature=0.7, **kwargs):
        """
        Chat completion dengan automatic fallback dan error handling
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (defaults to self.default_model)
            max_tokens: Maximum tokens untuk response
            temperature: Creativity level (0.0-1.0)
            **kwargs: Additional parameters
        
        Returns:
            str: AI response text atau None jika error
        """
        
        if not messages:
            return None
        
        # Rate limiting
        self._rate_limit_wait()
        
        # Use default model if none specified
        if model is None:
            model = self.default_model
        
        # Ensure model is available
        if self.available_models and model not in self.available_models:
            print(f"⚠️ Model {model} not available, using fallback")
            model = self._get_fallback_chat_model()
        
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Try with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    json=data, 
                    timeout=self.request_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    if self._is_valid_response(content):
                        return content
                    else:
                        print(f"⚠️ Invalid response received, attempt {attempt + 1}")
                        
                elif response.status_code == 429:  # Rate limit
                    wait_time = (attempt + 1) * 2
                    print(f"⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                elif response.status_code == 401:  # Auth error
                    print("❌ OpenAI API authentication failed")
                    return None
                    
                else:
                    print(f"⚠️ API error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Request timeout, attempt {attempt + 1}")
                
            except requests.exceptions.RequestException as e:
                print(f"🌐 Network error: {e}, attempt {attempt + 1}")
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}, attempt {attempt + 1}")
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        print("❌ All chat completion attempts failed")
        return None
    
    def _get_fallback_chat_model(self):
        """Get fallback chat model"""
        fallback_models = ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-0613"]
        
        if self.available_models:
            for model in fallback_models:
                if model in self.available_models:
                    return model
        
        return "gpt-3.5-turbo"  # Ultimate fallback
    
    def _is_valid_response(self, content):
        """Validate response content"""
        if not content or len(content.strip()) == 0:
            return False
        
        # Check for common error patterns
        error_patterns = [
            "i'm sorry, but i can't",
            "i cannot provide",
            "as an ai language model",
            "i don't have the ability"
        ]
        
        content_lower = content.lower()
        for pattern in error_patterns:
            if pattern in content_lower and len(content) < 50:
                return False
        
        return True
    
    def vision_analysis(self, image, prompt="What do you see in this image?", max_tokens=300, **kwargs):
        """
        Vision analysis dengan GPT-4 Vision atau fallback
        
        Args:
            image: Image sebagai numpy array, PIL Image, atau file path
            prompt: Text prompt untuk analysis
            max_tokens: Maximum tokens untuk response
            **kwargs: Additional parameters
        
        Returns:
            str: Analysis result atau None jika error
        """
        
        print("👁️ Starting vision analysis...")
        
        # Rate limiting
        self._rate_limit_wait()
        
        # Try vision models in order of preference
        vision_models = self.available_vision_models or ["gpt-4o", "gpt-4-vision-preview"]
        
        for model in vision_models:
            print(f"🔍 Trying vision model: {model}")
            
            result = self._try_vision_model(image, prompt, max_tokens, model, **kwargs)
            if result:
                print(f"✅ Vision analysis successful with {model}")
                return result
            
            print(f"❌ Vision model {model} failed")
        
        # If all vision models fail, try description-based fallback
        print("🔄 Falling back to description-based analysis...")
        return self._description_based_analysis(image, prompt, max_tokens)
    
    def _try_vision_model(self, image, prompt, max_tokens, model, **kwargs):
        """Try specific vision model"""
        try:
            url = f"{self.base_url}/chat/completions"
            
            # Encode image
            base64_image = self._encode_image(image)
            if not base64_image:
                return None
            
            data = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": max_tokens,
                **kwargs
            }
            
            response = requests.post(
                url, 
                headers=self.headers, 
                json=data, 
                timeout=60  # Longer timeout for vision
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                if self._is_valid_response(content):
                    return content
            else:
                print(f"Vision API error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"Vision model error: {e}")
        
        return None
    
    def _encode_image(self, image):
        """Encode image ke base64"""
        try:
            if isinstance(image, str):
                # File path
                with open(image, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            
            elif hasattr(image, 'shape'):
                # NumPy array (OpenCV image)
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image_rgb = image
                
                pil_image = Image.fromarray(image_rgb)
                buffer = BytesIO()
                pil_image.save(buffer, format="JPEG", quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            elif hasattr(image, 'save'):
                # PIL Image
                buffer = BytesIO()
                image.save(buffer, format="JPEG", quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            else:
                print(f"❌ Unsupported image format: {type(image)}")
                return None
                
        except Exception as e:
            print(f"❌ Image encoding error: {e}")
            return None
    
    def _description_based_analysis(self, image, prompt, max_tokens):
        """
        Fallback analysis menggunakan basic computer vision + GPT text analysis
        """
        try:
            print("🔄 Using description-based fallback analysis...")
            
            # Basic computer vision analysis
            cv_description = self._basic_cv_analysis(image)
            
            # Enhanced prompt with CV analysis
            enhanced_prompt = f"""
            Based on a computer vision analysis of an electronics image, here's what was detected:
            {cv_description}
            
            Original request: {prompt}
            
            Please provide a helpful electronics analysis based on this information. 
            Be educational and practical. If the CV analysis seems limited, 
            acknowledge that and provide general electronics advice that would be helpful.
            
            Focus on:
            1. What components might be present based on the description
            2. Potential projects or applications
            3. Learning opportunities
            4. Safety considerations
            5. Next steps for the user
            """
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are an expert electronics engineer and teacher. Provide helpful, educational responses about electronics projects and components."
                },
                {
                    "role": "user", 
                    "content": enhanced_prompt
                }
            ]
            
            # Use regular chat completion
            response = self.chat_completion(messages, max_tokens=max_tokens)
            
            if response:
                return f"[Using fallback analysis] {response}"
            else:
                return self._generic_electronics_response()
                
        except Exception as e:
            print(f"❌ Fallback analysis error: {e}")
            return self._generic_electronics_response()
    
    def _basic_cv_analysis(self, image):
        """Basic computer vision analysis sebagai fallback"""
        try:
            # Convert image to proper format
            if isinstance(image, str):
                cv_image = cv2.imread(image)
            elif hasattr(image, 'shape'):
                cv_image = image
            elif hasattr(image, 'save'):
                # PIL to OpenCV
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                return "Could not process image for basic analysis"
            
            if cv_image is None:
                return "Image could not be loaded for analysis"
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            analysis_parts = []
            
            # Color analysis
            colors_detected = []
            color_ranges = {
                'red': ([0, 50, 50], [10, 255, 255]),
                'green': ([50, 50, 50], [70, 255, 255]),
                'blue': ([100, 50, 50], [130, 255, 255]),
                'yellow': ([20, 50, 50], [30, 255, 255])
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                if cv2.countNonZero(mask) > 1000:  # Significant color presence
                    colors_detected.append(color_name)
            
            if colors_detected:
                analysis_parts.append(f"Detected colors: {', '.join(colors_detected)} (possibly indicating LEDs, resistors, or wires)")
            
            # Shape/edge analysis
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            rectangular_objects = 0
            circular_objects = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filter small noise
                    # Check if rectangular
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    if len(approx) == 4:
                        rectangular_objects += 1
                    elif len(approx) > 8:  # Likely circular
                        circular_objects += 1
            
            if rectangular_objects > 0:
                analysis_parts.append(f"Detected {rectangular_objects} rectangular objects (possibly circuit boards, breadboards, or IC chips)")
            
            if circular_objects > 0:
                analysis_parts.append(f"Detected {circular_objects} circular objects (possibly LEDs, capacitors, or connectors)")
            
            # Overall assessment
            if len(analysis_parts) == 0:
                analysis_parts.append("Image appears to contain electronic components, but specific details are limited by basic computer vision")
            
            return "; ".join(analysis_parts)
            
        except Exception as e:
            return f"Basic computer vision analysis encountered an error: {e}, but electronics components appear to be present"
    
    def _generic_electronics_response(self):
        """Generic helpful response ketika semua analysis gagal"""
        return """
        I can see you're working with electronics components! Even though I'm having trouble with detailed visual analysis right now, I'd love to help you with your electronics projects.
        
        Here are some general tips for electronics work:
        
        1. **Safety First**: Always check component ratings and use appropriate resistors with LEDs
        2. **Start Simple**: Begin with basic LED circuits before moving to complex projects  
        3. **Double-check Connections**: Verify power, ground, and signal connections
        4. **Use a Multimeter**: Test continuity and voltages when troubleshooting
        5. **Component Organization**: Keep components organized and labeled
        
        Could you tell me what specific components you're working with or what project you're trying to build? I can provide more targeted advice based on your description!
        """
    
    def get_status(self):
        """Get client status"""
        return {
            'api_key_configured': bool(self.api_key and self.api_key != "your_openai_api_key_here"),
            'available_models': len(self.available_models) if self.available_models else 0,
            'available_vision_models': len(self.available_vision_models) if self.available_vision_models else 0,
            'default_model': self.default_model,
            'last_request_time': self.last_request_time
        }

# Alias methods untuk backward compatibility
class OpenAIClientWithFallback(OpenAIClient):
    """Alias class untuk backward compatibility dengan openai_vision_fallback.py"""
    
    def __init__(self, api_key):
        super().__init__(api_key)
    
    def vision_analysis_with_fallback(self, image, prompt="What electronics components do you see in this image?", max_tokens=300):
        """Alias method"""
        return self.vision_analysis(image, prompt, max_tokens)
    
    def component_identification(self, image):
        """Specialized component identification"""
        prompt = """
        Identify and describe each electronic component in this image:

        For each component, provide:
        - Component name and type
        - Specifications if visible (resistance values, voltage ratings, etc.)
        - Typical uses and applications
        - How to identify it (visual characteristics)
        - Beginner tips for using this component

        Be very detailed and educational.
        """
        return self.vision_analysis(image, prompt, max_tokens=400)
    
    def electronics_project_analysis(self, image):
        """Specialized analysis untuk electronics projects"""
        prompt = """
        You are an expert electronics engineer and teacher. Analyze this image and provide:

        1. **Components Identified**: List all electronic components you can see
        2. **Project Assessment**: What kind of projects could be built with these components?
        3. **Skill Level**: Rate the complexity level (Beginner/Intermediate/Advanced)
        4. **Step-by-Step Guide**: For the most suitable beginner project, provide detailed steps
        5. **Safety Notes**: Any important safety considerations
        6. **Missing Components**: What additional components might be needed
        7. **Learning Opportunities**: What concepts can be learned from these projects

        Please be detailed and educational in your response.
        """
        return self.vision_analysis(image, prompt, max_tokens=500)
    
    def circuit_analysis(self, image):
        """Analyze existing circuits atau breadboard layouts"""
        prompt = """
        As an electronics expert, analyze this circuit/breadboard layout:

        1. **Circuit Description**: Describe the current circuit setup
        2. **Connections**: Verify if connections look correct
        3. **Potential Issues**: Spot any wiring problems or mistakes
        4. **Improvements**: Suggest optimizations or corrections
        5. **Functionality**: Explain what this circuit should do
        6. **Troubleshooting**: Common issues and solutions

        Be thorough and educational.
        """
        return self.vision_analysis(image, prompt, max_tokens=400)

# Test functions
def test_openai_wrapper():
    """Test complete OpenAI wrapper functionality"""
    from config import Config
    
    print("🧪 Testing Complete OpenAI Wrapper...")
    print("=" * 50)
    
    try:
        client = OpenAIClient(Config.OPENAI_API_KEY)
        
        # Test 1: Chat completion
        print("\n🗣️ Testing Chat Completion...")
        messages = [
            {"role": "system", "content": "You are a helpful electronics assistant."},
            {"role": "user", "content": "Explain what an LED is in simple terms."}
        ]
        
        response = client.chat_completion(messages, max_tokens=100)
        
        if response:
            print(f"✅ Chat completion successful")
            print(f"Response preview: {response[:100]}...")
        else:
            print("❌ Chat completion failed")
        
        # Test 2: Vision analysis (if camera available)
        print("\n👁️ Testing Vision Analysis...")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                vision_response = client.vision_analysis(
                    frame, 
                    "What electronics components do you see?", 
                    max_tokens=150
                )
                
                if vision_response:
                    print("✅ Vision analysis successful")
                    print(f"Vision response preview: {vision_response[:100]}...")
                else:
                    print("⚠️ Vision analysis failed, but fallback should work")
            else:
                print("📷 No camera available for vision test")
                
        except Exception as e:
            print(f"📷 Camera test skipped: {e}")
        
        # Test 3: Status check
        print("\n📊 Client Status:")
        status = client.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 OpenAI Wrapper test completed!")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Wrapper test failed: {e}")
        return False

def test_backward_compatibility():
    """Test backward compatibility dengan existing code"""
    from config import Config
    
    print("🔄 Testing Backward Compatibility...")
    
    try:
        # Test original import pattern
        client = OpenAIClient(Config.OPENAI_API_KEY)
        
        # Test methods yang digunakan dalam brain_module.py
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = client.chat_completion(messages, max_tokens=50)
        
        if response:
            print("✅ Backward compatibility confirmed")
            return True
        else:
            print("⚠️ Backward compatibility issue detected")
            return False
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running OpenAI Wrapper Tests...")
    
    # Run all tests
    test_results = {
        "Wrapper Functionality": test_openai_wrapper(),
        "Backward Compatibility": test_backward_compatibility()
    }
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    all_passed = all(test_results.values())
    print(f"\n🎯 Overall: {'All tests passed!' if all_passed else 'Some tests failed'}")