# project_manager.py - Advanced project management untuk Ellee (Python 3.6 Compatible)
import json
import os
import cv2
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import threading

# Python 3.6 compatible classes (mengganti dataclasses)
class ProjectStep(object):
    """Individual step dalam project"""
    def __init__(self, step_id, title, description, estimated_time_minutes, difficulty, 
                 required_components, safety_notes, completion_criteria, is_completed=False, 
                 completion_time=None, actual_time_minutes=None, notes=None, images=None):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.estimated_time_minutes = estimated_time_minutes
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.required_components = required_components
        self.safety_notes = safety_notes
        self.completion_criteria = completion_criteria
        self.is_completed = is_completed
        self.completion_time = completion_time
        self.actual_time_minutes = actual_time_minutes
        self.notes = notes or []
        self.images = images or []
    
    def to_dict(self):
        return {
            'step_id': self.step_id,
            'title': self.title,
            'description': self.description,
            'estimated_time_minutes': self.estimated_time_minutes,
            'difficulty': self.difficulty,
            'required_components': self.required_components,
            'safety_notes': self.safety_notes,
            'completion_criteria': self.completion_criteria,
            'is_completed': self.is_completed,
            'completion_time': self.completion_time,
            'actual_time_minutes': self.actual_time_minutes,
            'notes': self.notes,
            'images': self.images
        }

class ProjectTemplate(object):
    """Template untuk common projects"""
    def __init__(self, template_id, name, description, category, estimated_total_time_hours,
                 required_components, optional_components, learning_objectives, 
                 prerequisite_knowledge, steps, variations):
        self.template_id = template_id
        self.name = name
        self.description = description
        self.category = category  # "beginner", "intermediate", "advanced"
        self.estimated_total_time_hours = estimated_total_time_hours
        self.required_components = required_components
        self.optional_components = optional_components
        self.learning_objectives = learning_objectives
        self.prerequisite_knowledge = prerequisite_knowledge
        self.steps = steps
        self.variations = variations
    
    def to_dict(self):
        return {
            'template_id': self.template_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'estimated_total_time_hours': self.estimated_total_time_hours,
            'required_components': self.required_components,
            'optional_components': self.optional_components,
            'learning_objectives': self.learning_objectives,
            'prerequisite_knowledge': self.prerequisite_knowledge,
            'steps': [step.to_dict() if hasattr(step, 'to_dict') else step for step in self.steps],
            'variations': self.variations
        }

class AdvancedProjectManager:
    """Advanced project management system untuk robot Ellee"""
    
    def __init__(self, config, memory_system):
        self.config = config
        self.memory = memory_system
        self.projects_dir = os.path.join("ellee_memory", "projects")
        self.templates_dir = os.path.join("ellee_memory", "templates")
        self.images_dir = os.path.join("ellee_memory", "project_images")
        
        # Create directories
        for directory in [self.projects_dir, self.templates_dir, self.images_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Load project templates
        self.project_templates = {}
        self._load_builtin_templates()
        
        # Active project tracking
        self.active_projects = {}
        self.current_step_tracking = {}
        
        # Progress tracking
        self.progress_lock = threading.Lock()
        
        print("📋 Advanced Project Manager initialized")
    
    def _load_builtin_templates(self):
        """Load built-in project templates"""
        
        # LED Blink Project Template
        led_blink_steps = [
            ProjectStep(
                step_id="led_blink_01",
                title="Gather Components",
                description="Collect Arduino Uno, LED, 220Ω resistor, breadboard, and jumper wires",
                estimated_time_minutes=5,
                difficulty="easy",
                required_components=["Arduino Uno", "LED", "220Ω Resistor", "Breadboard", "Jumper Wires"],
                safety_notes=["Check component values before connecting"],
                completion_criteria="All components are ready and organized"
            ),
            ProjectStep(
                step_id="led_blink_02", 
                title="Build Circuit",
                description="Connect LED to pin 13 through resistor, with cathode to ground",
                estimated_time_minutes=10,
                difficulty="easy",
                required_components=["All previous components"],
                safety_notes=["Ensure Arduino is unpowered while building", "Check LED polarity"],
                completion_criteria="Circuit is properly connected and double-checked"
            ),
            ProjectStep(
                step_id="led_blink_03",
                title="Upload Code",
                description="Open Arduino IDE, load Blink example, and upload to board",
                estimated_time_minutes=15,
                difficulty="medium",
                required_components=["USB Cable", "Computer with Arduino IDE"],
                safety_notes=["Use proper USB cable", "Select correct board and port"],
                completion_criteria="Code uploads successfully without errors"
            ),
            ProjectStep(
                step_id="led_blink_04",
                title="Test and Verify",
                description="Verify LED blinks every second, troubleshoot if needed",
                estimated_time_minutes=10,
                difficulty="easy",
                required_components=[],
                safety_notes=["Don't touch circuits while powered"],
                completion_criteria="LED blinks consistently at 1-second intervals"
            )
        ]
        
        led_blink_template = ProjectTemplate(
            template_id="led_blink_basic",
            name="LED Blink Circuit",
            description="Learn Arduino basics by making an LED blink",
            category="beginner",
            estimated_total_time_hours=0.75,
            required_components=["Arduino Uno", "LED", "220Ω Resistor", "Breadboard", "Jumper Wires", "USB Cable"],
            optional_components=["Multimeter for testing"],
            learning_objectives=[
                "Understanding Arduino pin configuration",
                "Basic circuit building on breadboard", 
                "Using Arduino IDE",
                "LED polarity and current limiting"
            ],
            prerequisite_knowledge=["Basic understanding of electricity"],
            steps=led_blink_steps,
            variations=[
                {"name": "Multiple LEDs", "description": "Add more LEDs in different patterns"},
                {"name": "Variable Speed", "description": "Use potentiometer to control blink speed"},
                {"name": "RGB LED", "description": "Use RGB LED for color changing effects"}
            ]
        )
        
        # Traffic Light Project Template
        traffic_light_steps = [
            ProjectStep(
                step_id="traffic_01",
                title="Component Setup",
                description="Gather Arduino, 3 LEDs (Red, Yellow, Green), 3x 220Ω resistors, breadboard",
                estimated_time_minutes=10,
                difficulty="easy",
                required_components=["Arduino Uno", "Red LED", "Yellow LED", "Green LED", "3x 220Ω Resistor", "Breadboard", "Jumper Wires"],
                safety_notes=["Organize components to avoid confusion"],
                completion_criteria="All components identified and ready"
            ),
            ProjectStep(
                step_id="traffic_02",
                title="Circuit Construction", 
                description="Wire LEDs to pins 12, 11, 10 with current limiting resistors",
                estimated_time_minutes=20,
                difficulty="medium",
                required_components=["All components from step 1"],
                safety_notes=["Double-check LED polarity", "Verify resistor values", "Keep Arduino unpowered"],
                completion_criteria="All three LEDs properly connected and circuit verified"
            ),
            ProjectStep(
                step_id="traffic_03",
                title="Programming",
                description="Write Arduino code for traffic light sequence timing",
                estimated_time_minutes=30,
                difficulty="medium",
                required_components=["Computer with Arduino IDE"],
                safety_notes=["Save code before uploading", "Test compilation first"],
                completion_criteria="Code compiles without errors and logic is correct"
            ),
            ProjectStep(
                step_id="traffic_04",
                title="Testing & Enhancement",
                description="Test sequence, adjust timing, add button for pedestrian crossing",
                estimated_time_minutes=25,
                difficulty="hard",
                required_components=["Push button", "10kΩ pull-up resistor"],
                safety_notes=["Test button wiring separately first"],
                completion_criteria="Traffic light cycles correctly with pedestrian button working"
            )
        ]
        
        traffic_light_template = ProjectTemplate(
            template_id="traffic_light_system",
            name="Traffic Light Controller",
            description="Build a realistic traffic light system with pedestrian crossing",
            category="intermediate",
            estimated_total_time_hours=1.5,
            required_components=["Arduino Uno", "3x LEDs (R,Y,G)", "3x 220Ω Resistor", "Push Button", "10kΩ Resistor", "Breadboard", "Jumper Wires"],
            optional_components=["LCD Display for countdown", "Buzzer for pedestrian signal"],
            learning_objectives=[
                "Sequential LED control",
                "Timing and delays in programming",
                "Button input handling",
                "State machine programming",
                "Real-world system modeling"
            ],
            prerequisite_knowledge=["Basic Arduino programming", "LED Blink project completion"],
            steps=traffic_light_steps,
            variations=[
                {"name": "Smart Traffic Light", "description": "Add vehicle detection sensors"},
                {"name": "Network Connected", "description": "Connect multiple intersections"},
                {"name": "LCD Integration", "description": "Add countdown display"}
            ]
        )
        
        # Temperature Monitor Project
        temp_monitor_steps = [
            ProjectStep(
                step_id="temp_01",
                title="Sensor Setup",
                description="Connect DS18B20 temperature sensor with pull-up resistor",
                estimated_time_minutes=15,
                difficulty="medium",
                required_components=["Arduino Uno", "DS18B20 Temperature Sensor", "4.7kΩ Resistor", "Breadboard"],
                safety_notes=["Check sensor pinout diagram", "Ensure proper power connections"],
                completion_criteria="Sensor properly wired and power verified"
            ),
            ProjectStep(
                step_id="temp_02",
                title="Library Installation",
                description="Install OneWire and DallasTemperature libraries in Arduino IDE",
                estimated_time_minutes=10,
                difficulty="easy",
                required_components=["Computer with Arduino IDE"],
                safety_notes=["Download libraries from official sources"],
                completion_criteria="Libraries installed and accessible in IDE"
            ),
            ProjectStep(
                step_id="temp_03",
                title="Basic Reading",
                description="Program Arduino to read and display temperature via Serial Monitor",
                estimated_time_minutes=20,
                difficulty="medium",
                required_components=[],
                safety_notes=["Set correct baud rate", "Handle sensor errors"],
                completion_criteria="Temperature readings display correctly in Serial Monitor"
            ),
            ProjectStep(
                step_id="temp_04",
                title="Alert System",
                description="Add LED alerts for temperature thresholds and optional buzzer",
                estimated_time_minutes=25,
                difficulty="medium",
                required_components=["2x LEDs", "2x 220Ω Resistors", "Buzzer (optional)"],
                safety_notes=["Test threshold values", "Avoid continuous buzzer operation"],
                completion_criteria="System properly alerts for high/low temperatures"
            )
        ]
        
        temp_monitor_template = ProjectTemplate(
            template_id="temperature_monitor",
            name="Temperature Monitoring System",
            description="Build a temperature monitor with alerts and data logging",
            category="intermediate",
            estimated_total_time_hours=1.25,
            required_components=["Arduino Uno", "DS18B20 Sensor", "4.7kΩ Resistor", "2x LEDs", "2x 220Ω Resistors", "Breadboard", "Jumper Wires"],
            optional_components=["LCD Display", "SD Card Module", "Buzzer", "Real Time Clock"],
            learning_objectives=[
                "Digital sensor interfacing",
                "Library usage in Arduino",
                "Serial communication",
                "Threshold monitoring",
                "Data logging concepts"
            ],
            prerequisite_knowledge=["Arduino basics", "Serial Monitor usage"],
            steps=temp_monitor_steps,
            variations=[
                {"name": "Data Logger", "description": "Add SD card for data storage"},
                {"name": "LCD Display", "description": "Show readings on LCD screen"},
                {"name": "WiFi Connected", "description": "Send data to cloud services"}
            ]
        )
        
        # Store templates
        self.project_templates = {
            "led_blink_basic": led_blink_template,
            "traffic_light_system": traffic_light_template,
            "temperature_monitor": temp_monitor_template
        }
        
        print("📚 Loaded {} project templates".format(len(self.project_templates)))
    
    def suggest_projects_for_components(self, detected_components, skill_level="beginner"):
        """Suggest projects based on detected components and skill level"""
        
        suggestions = []
        
        for template_id, template in self.project_templates.items():
            # Check if user has required components
            required_count = 0
            total_required = len(template.required_components)
            
            for required_comp in template.required_components:
                for detected_comp in detected_components:
                    if self._components_match(required_comp, detected_comp):
                        required_count += 1
                        break
            
            # Calculate compatibility score
            compatibility_score = required_count / total_required if total_required > 0 else 0
            
            # Filter by skill level
            skill_match = True
            if skill_level == "beginner" and template.category == "advanced":
                skill_match = False
            elif skill_level == "advanced" and template.category == "beginner":
                compatibility_score *= 0.7  # Reduce score but don't eliminate
            
            if compatibility_score > 0.3 and skill_match:  # At least 30% component match
                missing_components = []
                for req_comp in template.required_components:
                    found = False
                    for det_comp in detected_components:
                        if self._components_match(req_comp, det_comp):
                            found = True
                            break
                    if not found:
                        missing_components.append(req_comp)
                
                suggestions.append({
                    'template_id': template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category,
                    'compatibility_score': compatibility_score,
                    'estimated_time_hours': template.estimated_total_time_hours,
                    'missing_components': missing_components,
                    'learning_objectives': template.learning_objectives[:3],  # Top 3
                    'variations': template.variations
                })
        
        # Sort by compatibility score
        suggestions.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _components_match(self, required: str, detected: str) -> bool:
        """Check if detected component matches required component"""
        
        # Normalize strings
        req_lower = required.lower().strip()
        det_lower = detected.lower().strip()
        
        # Direct match
        if req_lower == det_lower:
            return True
        
        # Partial matches for common components
        component_mappings = {
            'arduino': ['arduino', 'uno', 'nano', 'micro'],
            'led': ['led', 'light', 'diode'],
            'resistor': ['resistor', 'resistance', 'ohm'],
            'breadboard': ['breadboard', 'protoboard'],
            'wire': ['wire', 'jumper', 'cable'],
            'button': ['button', 'switch', 'push'],
            'sensor': ['sensor', 'temperature', 'humidity', 'light']
        }
        
        for category, synonyms in component_mappings.items():
            if any(synonym in req_lower for synonym in synonyms) and any(synonym in det_lower for synonym in synonyms):
                return True
        
        return False
    
    def create_project_from_template(self, template_id, project_name, person_id=None):
        """Create new project from template"""
        
        try:
            if template_id not in self.project_templates:
                return None
            
            template = self.project_templates[template_id]
            
            # Generate unique project ID
            import hashlib
            project_id = hashlib.md5("{}{}".format(project_name, datetime.now().isoformat()).encode()).hexdigest()[:12]
            
            # Create project from template
            project_data = {
                'project_id': project_id,
                'name': project_name,
                'template_id': template_id,
                'description': template.description,
                'category': template.category,
                'person_id': person_id,
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'status': 'planning',
                'current_step_index': 0,
                'completion_percentage': 0.0,
                'estimated_total_time_hours': template.estimated_total_time_hours,
                'actual_time_minutes': 0,
                'steps': [step.to_dict() for step in template.steps],
                'required_components': template.required_components,
                'learning_objectives': template.learning_objectives,
                'notes': [],
                'images': [],
                'variations_explored': []
            }
            
            # Save to memory system with compatible format
            project_data_for_memory = {
                'project_id': project_id,
                'name': project_name,
                'description': template.description,
                'components': template.required_components,
                'difficulty_level': template.category,  # Use difficulty_level for memory_system compatibility
                'start_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'status': 'planning',
                'progress_images': [],
                'conversations': [],
                'learned_lessons': [],
                'next_steps': []
            }
            self.memory.project_cache[project_id] = project_data_for_memory
            
            # Save to file
            project_file = os.path.join(self.projects_dir, "{}.json".format(project_id))
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            # Add to active projects
            self.active_projects[project_id] = project_data
            
            print("📋 Created project '{}' from template '{}'".format(project_name, template_id))
            return project_id
            
        except Exception as e:
            print("Error creating project: {}".format(e))
            return None
    
    def get_current_step(self, project_id):
        """Get current step for project"""
        
        if project_id not in self.active_projects:
            return None
        
        project = self.active_projects[project_id]
        current_index = project['current_step_index']
        
        if current_index < len(project['steps']):
            return project['steps'][current_index]
        
        return None
    
    def complete_step(self, project_id, notes="", image=None):
        """Mark current step as completed"""
        
        with self.progress_lock:
            if project_id not in self.active_projects:
                return False
            
            project = self.active_projects[project_id]
            current_index = project['current_step_index']
            
            if current_index >= len(project['steps']):
                return False  # Project already completed
            
            # Mark step as completed
            step = project['steps'][current_index]
            step['is_completed'] = True
            step['completion_time'] = datetime.now().isoformat()
            
            if notes:
                if step['notes'] is None:
                    step['notes'] = []
                step['notes'].append(notes)
            
            # Save step image if provided
            if image is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = "{}step{}_{}.jpg".format(project_id, current_index, timestamp)
                image_path = os.path.join(self.images_dir, image_filename)
                cv2.imwrite(image_path, image)
                
                if step['images'] is None:
                    step['images'] = []
                step['images'].append(image_filename)
            
            # Move to next step
            project['current_step_index'] += 1
            project['last_modified'] = datetime.now().isoformat()
            
            # Update completion percentage
            completed_steps = sum(1 for s in project['steps'] if s['is_completed'])
            total_steps = len(project['steps'])
            project['completion_percentage'] = (completed_steps / total_steps) * 100
            
            # Check if project is completed
            if project['current_step_index'] >= len(project['steps']):
                project['status'] = 'completed'
                print("🎉 Project '{}' completed!".format(project['name']))
            else:
                project['status'] = 'in_progress'
            
            # Save updated project
            self._save_project(project_id)
            
            return True
    
    def get_project_progress(self, project_id):
        """Get detailed project progress"""
        
        if project_id not in self.active_projects:
            return {}
        
        project = self.active_projects[project_id]
        
        completed_steps = [s for s in project['steps'] if s['is_completed']]
        remaining_steps = [s for s in project['steps'] if not s['is_completed']]
        
        # Calculate time estimates
        total_estimated_minutes = sum(s['estimated_time_minutes'] for s in project['steps'])
        completed_estimated_minutes = sum(s['estimated_time_minutes'] for s in completed_steps)
        remaining_estimated_minutes = sum(s['estimated_time_minutes'] for s in remaining_steps)
        
        progress = {
            'project_id': project_id,
            'name': project['name'],
            'status': project['status'],
            'completion_percentage': project['completion_percentage'],
            'current_step_index': project['current_step_index'],
            'total_steps': len(project['steps']),
            'completed_steps': len(completed_steps),
            'remaining_steps': len(remaining_steps),
            'estimated_time_remaining_minutes': remaining_estimated_minutes,
            'estimated_completion_date': self._estimate_completion_date(remaining_estimated_minutes),
            'current_step': self.get_current_step(project_id),
            'next_steps': remaining_steps[:3],  # Next 3 steps
            'learning_progress': self._assess_learning_progress(project)
        }
        
        return progress
    
    def _estimate_completion_date(self, remaining_minutes):
        """Estimate when project will be completed"""
        
        # Assume 1-2 hours of work per day on average
        work_minutes_per_day = 90
        days_remaining = max(1, remaining_minutes / work_minutes_per_day)
        
        completion_date = datetime.now() + timedelta(days=days_remaining)
        return completion_date.strftime("%Y-%m-%d")
    
    def _assess_learning_progress(self, project):
        """Assess learning progress for project"""
        
        completed_steps = [s for s in project['steps'] if s['is_completed']]
        
        # Count different difficulty levels completed
        difficulty_progress = {
            'easy': len([s for s in completed_steps if s['difficulty'] == 'easy']),
            'medium': len([s for s in completed_steps if s['difficulty'] == 'medium']), 
            'hard': len([s for s in completed_steps if s['difficulty'] == 'hard'])
        }
        
        # Calculate learning objectives achieved
        objectives_count = len(project['learning_objectives'])
        completion_rate = project['completion_percentage'] / 100
        objectives_achieved = int(objectives_count * completion_rate)
        
        return {
            'difficulty_progress': difficulty_progress,
            'learning_objectives_achieved': objectives_achieved,
            'total_learning_objectives': objectives_count,
            'skill_development_areas': project['learning_objectives'][:objectives_achieved]
        }
    
    def get_project_recommendations(self, project_id):
        """Get recommendations for project improvement or next steps"""
        
        if project_id not in self.active_projects:
            return {}
        
        project = self.active_projects[project_id]
        template = self.project_templates.get(project['template_id'])
        
        recommendations = {
            'variations_to_try': [],
            'skill_building_suggestions': [],
            'component_upgrades': [],
            'next_project_suggestions': []
        }
        
        if template:
            # Suggest variations not yet explored
            explored_variations = project.get('variations_explored', [])
            available_variations = [v for v in template.variations if v['name'] not in explored_variations]
            recommendations['variations_to_try'] = available_variations[:3]
            
            # Suggest skill building based on difficulty progression
            if project['completion_percentage'] > 70:
                recommendations['skill_building_suggestions'] = [
                    "Try adding sensor inputs to your project",
                    "Experiment with different timing patterns",
                    "Add user interface elements like buttons or displays"
                ]
        
        # Suggest component upgrades
        if 'led' in str(project['required_components']).lower():
            recommendations['component_upgrades'].append("Upgrade to RGB LEDs for color effects")
        
        if 'arduino uno' in str(project['required_components']).lower():
            recommendations['component_upgrades'].append("Try Arduino Nano for compact projects")
        
        return recommendations
    
    def _save_project(self, project_id):
        """Save project to file and memory"""
        
        if project_id in self.active_projects:
            project = self.active_projects[project_id]
            
            # Update memory cache
            self.memory.project_cache[project_id] = project
            
            # Save to file
            project_file = os.path.join(self.projects_dir, "{}.json".format(project_id))
            with open(project_file, 'w') as f:
                json.dump(project, f, indent=2)
    
    def get_all_projects_summary(self, person_id=None):
        """Get summary of all projects"""
        
        all_projects = list(self.memory.project_cache.values())
        
        if person_id:
            all_projects = [p for p in all_projects if p.get('person_id') == person_id]
        
        summary = {
            'total_projects': len(all_projects),
            'completed_projects': len([p for p in all_projects if p['status'] == 'completed']),
            'active_projects': len([p for p in all_projects if p['status'] in ['planning', 'in_progress']]),
            'average_completion_rate': 0,
            'total_learning_time_hours': 0,
            'skill_progression': {
                'beginner_projects': len([p for p in all_projects if p.get('category', p.get('difficulty_level', 'beginner')) == 'beginner']),
                'intermediate_projects': len([p for p in all_projects if p.get('category', p.get('difficulty_level', 'beginner')) == 'intermediate']),
                'advanced_projects': len([p for p in all_projects if p.get('category', p.get('difficulty_level', 'beginner')) == 'advanced'])
            },
            'recent_activity': []
        }
        
        if all_projects:
            total_completion = sum(p.get('completion_percentage', 0) for p in all_projects)
            summary['average_completion_rate'] = total_completion / len(all_projects)
            
            # Calculate total learning time - handle both field names for compatibility
            summary['total_learning_time_hours'] = sum(p.get('actual_time_minutes', 0) for p in all_projects) / 60
            
            # Get recent activity - handle both timestamp field names
            recent_projects = sorted(all_projects, key=lambda x: x.get('last_modified', x.get('start_date', '')), reverse=True)[:5]
            for project in recent_projects:
                summary['recent_activity'].append({
                    'name': project.get('name', 'Unnamed Project'),
                    'last_modified': project.get('last_modified', project.get('start_date', '')),
                    'status': project.get('status', 'unknown'),
                    'completion_percentage': project.get('completion_percentage', 0)
                })
        
        return summary

# Test function
def test_project_manager():
    """Test advanced project manager"""
    from config import Config
    from memory_system import ElleeBrainMemory
    
    print("Testing Advanced Project Manager...")
    
    # Initialize memory system first
    memory = ElleeBrainMemory(Config)
    
    # Initialize project manager
    pm = AdvancedProjectManager(Config, memory)
    
    # Test component-based project suggestions
    detected_components = ["Arduino Uno", "LED", "Resistor", "Breadboard"]
    suggestions = pm.suggest_projects_for_components(detected_components, "beginner")
    
    print("✅ Found {} project suggestions for components".format(len(suggestions)))
    for suggestion in suggestions[:2]:
        print("  - {}: {:.2f} compatibility".format(suggestion['name'], suggestion['compatibility_score']))
    
    # Test creating project from template
    project_id = pm.create_project_from_template("led_blink_basic", "My First LED Blink", "test_user")
    
    if project_id:
        print("✅ Created project with ID: {}".format(project_id))
        
        # Test getting current step
        current_step = pm.get_current_step(project_id)
        print("✅ Current step: {}".format(current_step['title']))
        
        # Test completing a step
        success = pm.complete_step(project_id, "Gathered all components successfully!")
        print("✅ Step completion: {}".format(success))
        
        # Test project progress
        progress = pm.get_project_progress(project_id)
        print("✅ Project progress: {:.1f}%".format(progress['completion_percentage']))
        
        # Test recommendations
        recommendations = pm.get_project_recommendations(project_id)
        print("✅ Got {} variation suggestions".format(len(recommendations['variations_to_try'])))
    
    # Test project summary
    summary = pm.get_all_projects_summary()
    print("✅ Projects summary: {} total, {} active".format(summary['total_projects'], summary['active_projects']))
    
    print("🎉 Project Manager test completed!")
    return True

if __name__ == "__main__":
    test_project_manager()