# smart_electronics_analyzer.py - Advanced electronics analysis dengan GPT Vision
import cv2
import numpy as np
from datetime import datetime
import json
import os
from openai_vision_fallback import OpenAIClientWithFallback

class SmartElectronicsAnalyzer:
    def __init__(self, config):
        self.config = config
        self.openai_client = OpenAIClientWithFallback(config.OPENAI_API_KEY)
        
        # Analysis history untuk memory system nanti
        self.analysis_history = []
        self.current_project_context = None
        
        print("🔬 Smart Electronics Analyzer initialized with GPT Vision")
    
    def analyze_components(self, image, analysis_type="comprehensive"):
        """
        Main analysis function dengan berbagai jenis analysis
        """
        print(f"🔍 Starting {analysis_type} analysis...")
        
        try:
            if analysis_type == "comprehensive":
                result = self._comprehensive_analysis(image)
            elif analysis_type == "project_suggestion":
                result = self._project_suggestion_analysis(image)
            elif analysis_type == "circuit_check":
                result = self._circuit_analysis(image)
            elif analysis_type == "component_identification":
                result = self._component_identification(image)
            elif analysis_type == "troubleshooting":
                result = self._troubleshooting_analysis(image)
            else:
                result = self._comprehensive_analysis(image)
            
            # Save to history
            self._save_analysis_to_history(result, analysis_type, image)
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble analyzing the image right now. Could you try again?"
            }
    
    def _comprehensive_analysis(self, image):
        """Comprehensive analysis untuk general electronics"""
        
        prompt = """
        You are an expert electronics engineer and teacher. Analyze this image and provide:

        1. **Components Identified**: List all electronic components you can see (be specific about types, colors, models if visible)

        2. **Project Assessment**: What kind of projects could be built with these components?

        3. **Skill Level**: Rate the complexity level (Beginner/Intermediate/Advanced) for each suggested project

        4. **Step-by-Step Guide**: For the most suitable beginner project, provide detailed steps

        5. **Safety Notes**: Any important safety considerations

        6. **Missing Components**: What additional components might be needed

        7. **Learning Opportunities**: What concepts can be learned from these projects

        Please be detailed and educational in your response. Assume the person is learning electronics and wants practical, actionable advice.
        """
        
        response = self.openai_client.vision_analysis_with_fallback(image, prompt, max_tokens=500)
        
        if response:
            return {
                "success": True,
                "type": "comprehensive",
                "analysis": response,
                "message": self._create_conversational_response(response),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "I couldn't analyze the image right now. Please make sure I can see the components clearly and try again."
            }
    
    def _project_suggestion_analysis(self, image):
        """Fokus pada project suggestions"""
        
        prompt = """
        As an enthusiastic electronics teacher, look at these components and suggest 3 exciting projects:

        For each project, provide:
        1. **Project Name** and brief description
        2. **Difficulty Level** (Beginner/Intermediate/Advanced)
        3. **What You'll Learn** - key concepts and skills
        4. **Required Components** - what's needed
        5. **Time Estimate** - how long it might take
        6. **Cool Factor** - why this project is fun/useful

        Then recommend which project to start with and explain why. Be encouraging and enthusiastic!
        """
        
        response = self.openai_client.vision_analysis(image, prompt, max_tokens=400)
        
        if response:
            return {
                "success": True,
                "type": "project_suggestion",
                "analysis": response,
                "message": f"I can see some great components here! {response}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "message": "Could not generate project suggestions right now."}
    
    def _circuit_analysis(self, image):
        """Analyze existing circuit untuk verification"""
        
        response = self.openai_client.circuit_analysis(image)
        
        if response:
            return {
                "success": True,
                "type": "circuit_analysis",
                "analysis": response,
                "message": f"Let me check your circuit... {response}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "message": "I couldn't analyze the circuit layout clearly."}
    
    def _component_identification(self, image):
        """Detailed component identification"""
        
        response = self.openai_client.component_identification(image)
        
        if response:
            return {
                "success": True,
                "type": "component_identification",
                "analysis": response,
                "message": f"Here's what I can identify in your components: {response}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "message": "I couldn't identify the components clearly."}
    
    def _troubleshooting_analysis(self, image):
        """Troubleshooting assistance"""
        
        prompt = """
        Help troubleshoot this electronics setup:

        1. **Visual Inspection**: Check for obvious issues (loose connections, wrong polarity, etc.)
        2. **Common Problems**: What typically goes wrong with this type of setup?
        3. **Testing Steps**: How to systematically test and debug
        4. **Safety Check**: Any safety concerns visible?
        5. **Quick Fixes**: Simple solutions to try first
        6. **When to Ask for Help**: Signs that professional help might be needed

        Be practical and safety-focused.
        """
        
        response = self.openai_client.vision_analysis(image, prompt, max_tokens=350)
        
        if response:
            return {
                "success": True,
                "type": "troubleshooting",
                "analysis": response,
                "message": f"Let me help troubleshoot this setup... {response}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "message": "I couldn't provide troubleshooting advice right now."}
    
    def _create_conversational_response(self, gpt_response):
        """Convert GPT analysis ke conversational response"""
        
        # Add natural conversational flow
        intro_phrases = [
            "Fantastic! I can see some really interesting electronics here. ",
            "Great setup! Let me tell you what I'm seeing. ",
            "Excellent components! Here's my analysis: ",
            "Perfect! I love working with electronics like this. "
        ]
        
        import random
        intro = random.choice(intro_phrases)
        
        # Process GPT response untuk make it more conversational
        if gpt_response:
            # Trim if too long untuk speech
            if len(gpt_response) > 800:
                sentences = gpt_response.split('. ')
                # Take first few sentences untuk initial response
                short_response = '. '.join(sentences[:4]) + "."
                return intro + short_response + " Would you like me to continue with more details?"
            else:
                return intro + gpt_response
        
        return intro + "I can see your electronics setup, but I'd love to know more about what you're trying to build!"
    
    def analyze_project_progress(self, image, project_name=None):
        """
        Analyze project progress untuk memory system
        """
        
        if project_name:
            prompt = f"""
            This person is working on a project called "{project_name}". 
            Analyze the current progress:

            1. **Current State**: What stage of the project is this?
            2. **Completed Steps**: What has been done correctly?
            3. **Next Steps**: What should be done next?
            4. **Issues**: Any problems or mistakes visible?
            5. **Encouragement**: Positive feedback on progress
            6. **Guidance**: Specific next action to take

            Be encouraging and specific about next steps.
            """
        else:
            prompt = """
            Analyze the current state of this electronics project:

            1. **Project Type**: What kind of project does this appear to be?
            2. **Completion Status**: How far along is it?
            3. **Next Logical Steps**: What should happen next?
            4. **Potential Issues**: Any concerns or problems?
            5. **Suggestions**: How to improve or continue

            Be helpful and encouraging.
            """
        
        response = self.openai_client.vision_analysis(image, prompt, max_tokens=300)
        
        if response:
            return {
                "success": True,
                "type": "progress_analysis",
                "project_name": project_name,
                "analysis": response,
                "message": f"Looking at your project progress... {response}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"success": False, "message": "I couldn't analyze the project progress clearly."}
    
    def quick_component_check(self, image):
        """Quick check untuk real-time feedback"""
        
        prompt = """
        Quick electronics check - in 2-3 sentences tell me:
        1. Main components you see
        2. One interesting project possibility
        3. One quick tip or observation

        Keep it brief and encouraging!
        """
        
        response = self.openai_client.vision_analysis(image, prompt, max_tokens=150)
        
        if response:
            return {
                "success": True,
                "type": "quick_check",
                "analysis": response,
                "message": response,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "I can see some electronics components, but I'd love a clearer view to give you better advice!"
            }
    
    def _save_analysis_to_history(self, result, analysis_type, image=None):
        """Save analysis untuk memory system"""
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": analysis_type,
            "success": result.get("success", False),
            "analysis": result.get("analysis", ""),
            "message_length": len(result.get("message", "")),
            "has_image": image is not None
        }
        
        self.analysis_history.append(history_entry)
        
        # Keep only last 50 analyses untuk memory
        if len(self.analysis_history) > 50:
            self.analysis_history = self.analysis_history[-50:]
        
        # Save to file untuk persistent memory
        try:
            with open("analysis_history.json", "w") as f:
                json.dump(self.analysis_history, f, indent=2)
        except Exception as e:
            print(f"Could not save analysis history: {e}")
    
    def get_analysis_summary(self):
        """Get summary of recent analyses untuk conversation context"""
        
        if not self.analysis_history:
            return "This is our first analysis session."
        
        recent = self.analysis_history[-5:]  # Last 5 analyses
        
        summary = f"In our recent sessions, we've done {len(recent)} analyses. "
        
        analysis_types = [entry["analysis_type"] for entry in recent]
        type_counts = {}
        for t in analysis_types:
            type_counts[t] = type_counts.get(t, 0) + 1
        
        if type_counts:
            most_common = max(type_counts, key=type_counts.get)
            summary += f"You've been mostly interested in {most_common.replace('_', ' ')} lately. "
        
        return summary

# Test function
def test_smart_analyzer():
    """Test smart electronics analyzer"""
    from config import Config
    
    print("Testing Smart Electronics Analyzer with GPT Vision...")
    analyzer = SmartElectronicsAnalyzer(Config)
    
    # Test with camera
    cap = cv2.VideoCapture(0)
    
    print("\nCommands:")
    print("'c' - Comprehensive analysis")
    print("'p' - Project suggestions")
    print("'i' - Component identification")
    print("'t' - Troubleshooting")
    print("'q' - Quick check")
    print("'x' - Quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow("Smart Electronics Analyzer", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('x') or key == 27:  # 'x' or ESC key
            print("👋 Exiting...")
            break
        elif key == ord('c'):
            print("\n🔍 Comprehensive Analysis...")
            result = analyzer.analyze_components(frame, "comprehensive")
            print(f"Result: {result['message']}")
        elif key == ord('p'):
            print("\n💡 Project Suggestions...")
            result = analyzer.analyze_components(frame, "project_suggestion")
            print(f"Result: {result['message']}")
        elif key == ord('i'):
            print("\n🔬 Component Identification...")
            result = analyzer.analyze_components(frame, "component_identification")
            print(f"Result: {result['message']}")
        elif key == ord('t'):
            print("\n🛠 Troubleshooting...")
            result = analyzer.analyze_components(frame, "troubleshooting")
            print(f"Result: {result['message']}")
        elif key == ord('q'):
            print("\n⚡ Quick Check...")
            result = analyzer.quick_component_check(frame)
            print(f"Result: {result['message']}")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_smart_analyzer()