# vision_module.py - Modul untuk computer vision
import cv2
import threading
import time
import numpy as np
from PIL import Image

class VisionSystem:
    def __init__(self, config):
        self.config = config
        self.camera = None
        self.is_running = False
        self.current_frame = None
        self.capture_thread = None
        self.frame_lock = threading.Lock()
        
        # Initialize camera
        self._init_camera()
    
    def _init_camera(self):
        """Initialize USB camera"""
        print(f"Initializing camera at index {self.config.CAMERA_INDEX}...")
        self.camera = cv2.VideoCapture(self.config.CAMERA_INDEX)
        
        if not self.camera.isOpened():
            raise RuntimeError(f"Could not open camera at index {self.config.CAMERA_INDEX}")
        
        # Set camera properties
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("✅ Camera initialized successfully!")
    
    def start_capture(self):
        """Mulai capture video"""
        if not self.is_running:
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_worker)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            print("📷 Camera capture started")
    
    def stop_capture(self):
        """Berhenti capture video"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        print("📷 Camera capture stopped")
    
    def _capture_worker(self):
        """Worker thread untuk capture frames"""
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                with self.frame_lock:
                    self.current_frame = frame.copy()
            time.sleep(0.033)  # ~30 FPS
    
    def get_current_frame(self):
        """Ambil frame saat ini"""
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
    
    def detect_motion(self, threshold=5000):
        """Deteksi gerakan sederhana"""
        if not hasattr(self, '_prev_frame'):
            self._prev_frame = None
            return False
        
        current = self.get_current_frame()
        if current is None:
            return False
        
        # Convert to grayscale
        current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        
        if self._prev_frame is not None:
            # Calculate difference
            diff = cv2.absdiff(self._prev_frame, current_gray)
            
            # Calculate amount of change
            change_amount = np.sum(diff)
            
            self._prev_frame = current_gray
            return change_amount > threshold
        
        self._prev_frame = current_gray
        return False
    
    def detect_person_simple(self):
        """Deteksi orang sederhana menggunakan background subtraction"""
        frame = self.get_current_frame()
        if frame is None:
            return False, None
        
        # Simple person detection using frame analysis
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define skin color range (simple approximation)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask for skin color
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find contours
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if we found significant contours (possible person)
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area threshold
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                return True, (x, y, w, h)
        
        return False, None
    
    def save_frame(self, filename):
        """Simpan frame saat ini"""
        frame = self.get_current_frame()
        if frame is not None:
            cv2.imwrite(filename, frame)
            return True
        return False
    
    def show_preview(self, window_name="Ellee Vision"):
        """Tampilkan preview camera"""
        frame = self.get_current_frame()
        if frame is not None:
            # Add info overlay
            info_text = f"Ellee Robot - Camera Active"
            cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Detect motion and show status
            motion_detected = self.detect_motion()
            motion_text = "Motion: YES" if motion_detected else "Motion: NO"
            color = (0, 255, 0) if motion_detected else (0, 0, 255)
            cv2.putText(frame, motion_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Detect person
            person_detected, bbox = self.detect_person_simple()
            if person_detected and bbox:
                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, "Person Detected", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            cv2.imshow(window_name, frame)
            return cv2.waitKey(1) & 0xFF
        return -1
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_capture()
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

# Test function
def test_vision_module():
    """Test vision module"""
    from config import Config
    
    print("Testing Vision Module...")
    print("Camera preview will open for 10 seconds")
    print("Press 'q' to quit early, or move in front of camera to test motion detection")
    
    try:
        vision = VisionSystem(Config)
        vision.start_capture()
        
        start_time = time.time()
        while time.time() - start_time < 10:
            key = vision.show_preview()
            if key == ord('q'):
                break
            time.sleep(0.033)
        
        vision.cleanup()
        print("✅ Vision module test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Vision module test failed: {e}")
        return False

if __name__ == "__main__":
    test_vision_module()