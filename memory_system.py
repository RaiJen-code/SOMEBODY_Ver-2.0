# memory_system.py - Advanced memory and learning system for Ellee (Python 3.6 Compatible)
import json
import os
import sqlite3
import pickle
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import hashlib
import cv2
import numpy as np

# Python 3.6 compatible data classes using regular classes
class ConversationMemory(object):
    """Memory of a single conversation"""
    def __init__(self, timestamp=None, person_id=None, duration=0.0, messages=None, 
                 topics=None, sentiment="neutral", electronics_analysis=None, learned_preferences=None):
        self.timestamp = timestamp or datetime.now().isoformat()
        self.person_id = person_id
        self.duration = duration
        self.messages = messages or []
        self.topics = topics or []
        self.sentiment = sentiment
        self.electronics_analysis = electronics_analysis
        self.learned_preferences = learned_preferences or {}
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'person_id': self.person_id,
            'duration': self.duration,
            'messages': self.messages,
            'topics': self.topics,
            'sentiment': self.sentiment,
            'electronics_analysis': self.electronics_analysis,
            'learned_preferences': self.learned_preferences
        }

class ProjectMemory(object):
    """Memory of electronics projects"""
    def __init__(self, project_id, name, description="", components_used=None, difficulty_level="beginner",
                 start_date=None, last_modified=None, status="planning", progress_images=None, 
                 conversations=None, learned_lessons=None, next_steps=None):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.components_used = components_used or []
        self.difficulty_level = difficulty_level
        self.start_date = start_date or datetime.now().isoformat()
        self.last_modified = last_modified or datetime.now().isoformat()
        self.status = status  # "planning", "in_progress", "completed", "paused"
        self.progress_images = progress_images or []
        self.conversations = conversations or []  # conversation IDs related to this project
        self.learned_lessons = learned_lessons or []
        self.next_steps = next_steps or []
    
    def to_dict(self):
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'components_used': self.components_used,
            'difficulty_level': self.difficulty_level,
            'start_date': self.start_date,
            'last_modified': self.last_modified,
            'status': self.status,
            'progress_images': self.progress_images,
            'conversations': self.conversations,
            'learned_lessons': self.learned_lessons,
            'next_steps': self.next_steps
        }

class PersonMemory(object):
    """Memory about a specific person"""
    def __init__(self, person_id, name=None, first_met=None, last_interaction=None, 
                 total_interactions=0, skill_level="beginner", interests=None, current_projects=None,
                 preferred_topics=None, learning_style="visual", face_encodings=None):
        self.person_id = person_id
        self.name = name
        self.first_met = first_met or datetime.now().isoformat()
        self.last_interaction = last_interaction or datetime.now().isoformat()
        self.total_interactions = total_interactions
        self.skill_level = skill_level  # "beginner", "intermediate", "advanced"
        self.interests = interests or []
        self.current_projects = current_projects or []
        self.preferred_topics = preferred_topics or []
        self.learning_style = learning_style  # "visual", "hands-on", "theoretical"
        self.face_encodings = face_encodings or []  # For face recognition
    
    def to_dict(self):
        return {
            'person_id': self.person_id,
            'name': self.name,
            'first_met': self.first_met,
            'last_interaction': self.last_interaction,
            'total_interactions': self.total_interactions,
            'skill_level': self.skill_level,
            'interests': self.interests,
            'current_projects': self.current_projects,
            'preferred_topics': self.preferred_topics,
            'learning_style': self.learning_style,
            'face_encodings': [enc.decode('latin1') if isinstance(enc, bytes) else enc for enc in self.face_encodings]
        }

class ElleeBrainMemory:
    """Advanced memory and learning system for Ellee"""
    
    def __init__(self, config):
        self.config = config
        self.memory_dir = "ellee_memory"
        self.db_path = os.path.join(self.memory_dir, "ellee_brain.db")
        
        # In-memory caches
        self.conversation_cache = deque(maxlen=100)
        self.person_cache = {}
        self.project_cache = {}
        self.context_memory = {}
        
        # Learning metrics
        self.interaction_patterns = defaultdict(list)
        self.learning_progress = defaultdict(dict)
        
        # Thread safety
        self.memory_lock = threading.RLock()
        
        # Initialize memory system
        self._init_memory_system()
        
        print("🧠 Enhanced memory system initialized")
    
    def _init_memory_system(self):
        """Initialize memory database and directories"""
        
        # Create memory directory
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "conversations"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "projects"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "images"), exist_ok=True)
        os.makedirs(os.path.join(self.memory_dir, "faces"), exist_ok=True)
        
        # Initialize SQLite database
        self._init_database()
        
        # Load existing memories
        self._load_memories()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    person_id TEXT,
                    duration REAL,
                    message_count INTEGER,
                    topics TEXT,
                    sentiment TEXT,
                    electronics_involved BOOLEAN,
                    learning_occurred BOOLEAN
                )
            ''')
            
            # Projects table  
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    components TEXT,
                    difficulty_level TEXT,
                    start_date TEXT,
                    last_modified TEXT,
                    status TEXT,
                    completion_percentage REAL
                )
            ''')
            
            # People table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS people (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    first_met TEXT,
                    last_interaction TEXT,
                    total_interactions INTEGER,
                    skill_level TEXT,
                    interests TEXT,
                    learning_style TEXT
                )
            ''')
            
            # Learning progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id TEXT,
                    topic TEXT,
                    skill_level TEXT,
                    progress_date TEXT,
                    notes TEXT
                )
            ''')
            
            # Interaction patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interaction_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    frequency INTEGER,
                    last_seen TEXT
                )
            ''')
            
            conn.commit()
    
    def _load_memories(self):
        """Load existing memories from database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Load recent conversations
                cursor.execute('''
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                ''')
                
                for row in cursor.fetchall():
                    # Load conversation details from file
                    conv_file = os.path.join(self.memory_dir, "conversations", f"{row[0]}.json")
                    if os.path.exists(conv_file):
                        with open(conv_file, 'r') as f:
                            conv_data = json.load(f)
                            self.conversation_cache.append(conv_data)
                
                # Load people
                cursor.execute('SELECT * FROM people')
                for row in cursor.fetchall():
                    person_id = row[0]
                    person_file = os.path.join(self.memory_dir, "faces", f"{person_id}.pkl")
                    if os.path.exists(person_file):
                        with open(person_file, 'rb') as f:
                            person_data = pickle.load(f)
                            self.person_cache[person_id] = person_data
                
                # Load projects
                cursor.execute('SELECT * FROM projects')
                for row in cursor.fetchall():
                    project_id = row[0]
                    project_file = os.path.join(self.memory_dir, "projects", f"{project_id}.json")
                    if os.path.exists(project_file):
                        with open(project_file, 'r') as f:
                            project_data = json.load(f)
                            self.project_cache[project_id] = project_data
                            
        except Exception as e:
            print(f"Warning: Could not load some memories: {e}")
    
    def remember_conversation(self, conversation_data, person_id=None):
        """Remember a conversation with advanced analysis"""
        
        with self.memory_lock:
            try:
                # Generate conversation ID
                conv_id = hashlib.md5(f"{datetime.now().isoformat()}_{len(self.conversation_cache)}".encode()).hexdigest()[:12]
                
                # Analyze conversation
                analysis = self._analyze_conversation(conversation_data)
                
                # Create conversation memory
                conv_memory = ConversationMemory(
                    timestamp=datetime.now().isoformat(),
                    person_id=person_id,
                    duration=analysis.get('duration', 0),
                    messages=conversation_data.get('messages', []),
                    topics=analysis.get('topics', []),
                    sentiment=analysis.get('sentiment', 'neutral'),
                    electronics_analysis=analysis.get('electronics_analysis'),
                    learned_preferences=analysis.get('learned_preferences', {})
                )
                
                # Save to cache
                self.conversation_cache.append(conv_memory.to_dict())
                
                # Save to database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO conversations 
                        (id, timestamp, person_id, duration, message_count, topics, sentiment, electronics_involved, learning_occurred)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        conv_id,
                        conv_memory.timestamp,
                        conv_memory.person_id,
                        conv_memory.duration,
                        len(conv_memory.messages),
                        json.dumps(conv_memory.topics),
                        conv_memory.sentiment,
                        conv_memory.electronics_analysis is not None,
                        len(conv_memory.learned_preferences) > 0
                    ))
                    conn.commit()
                
                # Save detailed conversation to file
                conv_file = os.path.join(self.memory_dir, "conversations", "{}.json".format(conv_id))
                with open(conv_file, 'w') as f:
                    json.dump(conv_memory.to_dict(), f, indent=2)
                
                # Update person memory if person identified
                if person_id:
                    self._update_person_memory(person_id, conv_memory)
                
                return conv_id
                
            except Exception as e:
                print("Error remembering conversation: {}".format(e))
                return None
    
    def _update_person_memory(self, person_id, conv_memory):
        """Update person memory based on conversation"""
        try:
            if person_id not in self.person_cache:
                # Create new person memory
                person_data = PersonMemory(
                    person_id=person_id,
                    first_met=datetime.now().isoformat(),
                    last_interaction=datetime.now().isoformat(),
                    total_interactions=1
                )
                self.person_cache[person_id] = person_data.to_dict()
            else:
                # Update existing person
                person = self.person_cache[person_id]
                person['last_interaction'] = datetime.now().isoformat()
                person['total_interactions'] = person.get('total_interactions', 0) + 1
                
                # Update interests based on conversation topics
                for topic in conv_memory.topics:
                    if topic not in person.get('interests', []):
                        if 'interests' not in person:
                            person['interests'] = []
                        person['interests'].append(topic)
            
            # Save person to database
            self._save_person_to_db(person_id)
            
        except Exception as e:
            print("Error updating person memory: {}".format(e))
    
    def _save_person_to_db(self, person_id):
        """Save person data to database"""
        try:
            if person_id in self.person_cache:
                person = self.person_cache[person_id]
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Check if person exists
                    cursor.execute('SELECT id FROM people WHERE id = ?', (person_id,))
                    exists = cursor.fetchone()
                    
                    if exists:
                        # Update existing
                        cursor.execute('''
                            UPDATE people SET 
                            name = ?, last_interaction = ?, total_interactions = ?, 
                            skill_level = ?, interests = ?, learning_style = ?
                            WHERE id = ?
                        ''', (
                            person.get('name'),
                            person.get('last_interaction'),
                            person.get('total_interactions', 0),
                            person.get('skill_level', 'beginner'),
                            json.dumps(person.get('interests', [])),
                            person.get('learning_style', 'visual'),
                            person_id
                        ))
                    else:
                        # Insert new
                        cursor.execute('''
                            INSERT INTO people 
                            (id, name, first_met, last_interaction, total_interactions, skill_level, interests, learning_style)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            person_id,
                            person.get('name'),
                            person.get('first_met'),
                            person.get('last_interaction'),
                            person.get('total_interactions', 0),
                            person.get('skill_level', 'beginner'),
                            json.dumps(person.get('interests', [])),
                            person.get('learning_style', 'visual')
                        ))
                    
                    conn.commit()
        except Exception as e:
            print("Error saving person to database: {}".format(e))
    
    def _analyze_conversation(self, conversation_data):
        """Analyze conversation to extract insights"""
        """Analyze conversation to extract insights"""
        
        analysis = {
            'topics': [],
            'sentiment': 'neutral',
            'electronics_analysis': None,
            'learned_preferences': {},
            'duration': 0
        }
        
        messages = conversation_data.get('messages', [])
        if not messages:
            return analysis
        
        # Simple topic extraction
        electronics_keywords = [
            'arduino', 'led', 'resistor', 'circuit', 'breadboard', 'sensor',
            'programming', 'electronics', 'project', 'component', 'voltage'
        ]
        
        learning_keywords = [
            'how', 'what', 'why', 'explain', 'teach', 'learn', 'understand',
            'help', 'show', 'tutorial', 'guide'
        ]
        
        text_content = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Topic detection
        if any(keyword in text_content for keyword in electronics_keywords):
            analysis['topics'].append('electronics')
        
        if any(keyword in text_content for keyword in learning_keywords):
            analysis['topics'].append('learning')
        
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'awesome', 'excellent', 'amazing', 'perfect', 'love', 'like']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'difficult', 'confused', 'frustrated']
        
        positive_count = sum(1 for word in positive_words if word in text_content)
        negative_count = sum(1 for word in negative_words if word in text_content)
        
        if positive_count > negative_count:
            analysis['sentiment'] = 'positive'
        elif negative_count > positive_count:
            analysis['sentiment'] = 'negative'
        
        # Check for electronics analysis
        if 'vision_analysis' in conversation_data:
            analysis['electronics_analysis'] = conversation_data['vision_analysis']
        
        return analysis
    
    def remember_project(self, project_data):
        """Remember a new electronics project"""
        """Remember a new electronics project"""
        
        with self.memory_lock:
            try:
                # Generate project ID
                project_id = hashlib.md5(f"project_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
                
                # Create project memory
                project_memory = ProjectMemory(
                    project_id=project_id,
                    name=project_data.get('name', f"Project {project_id[:6]}"),
                    description=project_data.get('description', ''),
                    components_used=project_data.get('components', []),
                    difficulty_level=project_data.get('difficulty', 'beginner'),
                    start_date=datetime.now().isoformat(),
                    last_modified=datetime.now().isoformat(),
                    status='planning',
                    progress_images=[],
                    conversations=[],
                    learned_lessons=[],
                    next_steps=project_data.get('next_steps', [])
                )
                
                # Save to cache
                self.project_cache[project_id] = project_memory.to_dict()
                
                # Save to database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO projects 
                        (id, name, description, components, difficulty_level, start_date, last_modified, status, completion_percentage)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        project_id,
                        project_memory.name,
                        project_memory.description,
                        json.dumps(project_memory.components_used),
                        project_memory.difficulty_level,
                        project_memory.start_date,
                        project_memory.last_modified,
                        project_memory.status,
                        0.0
                    ))
                    conn.commit()
                
                # Save detailed project to file
                project_file = os.path.join(self.memory_dir, "projects", "{}.json".format(project_id))
                with open(project_file, 'w') as f:
                    json.dump(project_memory.to_dict(), f, indent=2)
                
                return project_id
                
            except Exception as e:
                print(f"Error remembering project: {e}")
                return None
    
    def update_project_progress(self, project_id, progress_data, image=None):
        """Update project progress with new information"""
        """Update project progress with new information"""
        
        with self.memory_lock:
            if project_id in self.project_cache:
                project = self.project_cache[project_id]
                
                # Update fields
                if 'status' in progress_data:
                    project['status'] = progress_data['status']
                
                if 'learned_lessons' in progress_data:
                    project['learned_lessons'].extend(progress_data['learned_lessons'])
                
                if 'next_steps' in progress_data:
                    project['next_steps'] = progress_data['next_steps']
                
                # Save progress image
                if image is not None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"{project_id}_{timestamp}.jpg"
                    image_path = os.path.join(self.memory_dir, "images", image_filename)
                    cv2.imwrite(image_path, image)
                    project['progress_images'].append(image_filename)
                
                project['last_modified'] = datetime.now().isoformat()
                
                # Save to file
                project_file = os.path.join(self.memory_dir, "projects", "{}.json".format(project_id))
                with open(project_file, 'w') as f:
                    json.dump(project, f, indent=2)
                
                print("📝 Updated project {} progress".format(project['name']))
    
    def get_conversation_context(self, person_id=None, limit=5):
        """Get conversation context for AI"""
        """Get conversation context for AI"""
        
        contexts = []
        
        # Recent conversations
        recent_convs = list(self.conversation_cache)[-limit:]
        if person_id:
            recent_convs = [c for c in recent_convs if c.get('person_id') == person_id]
        
        for conv in recent_convs:
            topics = ', '.join(conv.get('topics', []))
            if topics:
                contexts.append("Recent topic: {}".format(topics))
        
        # Active projects
        active_projects = [p for p in self.project_cache.values() if p['status'] in ['planning', 'in_progress']]
        if active_projects:
            project_names = [p['name'] for p in active_projects[:3]]
            contexts.append("Current projects: {}".format(', '.join(project_names)))
        
        # Person preferences
        if person_id and person_id in self.person_cache:
            person = self.person_cache[person_id]
            skill_level = person.get('skill_level', 'unknown')
            interests = person.get('interests', [])
            
            contexts.append("User skill level: {}".format(skill_level))
            if interests:
                contexts.append("User interests: {}".format(', '.join(interests[:3])))
        
        return "; ".join(contexts) if contexts else "This is a new conversation."
    
    def learn_from_interaction(self, interaction_data):
        """Learn patterns from user interactions"""
        """Learn patterns from user interactions"""
        
        # Extract learning signals
        if 'success_indicators' in interaction_data:
            # User showed understanding or satisfaction
            self._record_successful_teaching_pattern(interaction_data)
        
        if 'confusion_indicators' in interaction_data:
            # User seemed confused or asked for clarification
            self._record_teaching_improvement_opportunity(interaction_data)
        
        if 'preference_signals' in interaction_data:
            # User showed preferences for certain types of responses
            self._update_response_preferences(interaction_data)
    
    def _record_successful_teaching_pattern(self, interaction_data):
        """Record what teaching approaches work well"""
        """Record what teaching approaches work well"""
        
        pattern_key = f"success_{interaction_data.get('topic', 'general')}"
        self.interaction_patterns[pattern_key].append({
            'timestamp': datetime.now().isoformat(),
            'approach': interaction_data.get('teaching_approach'),
            'user_response': interaction_data.get('user_response'),
            'effectiveness': interaction_data.get('effectiveness_score', 1.0)
        })
    
    def get_personalized_teaching_approach(self, person_id, topic):
        """Get personalized teaching approach based on learned patterns"""
        """Get personalized teaching approach based on learned patterns"""
        
        recommendations = {
            'style': 'conversational',
            'detail_level': 'medium',
            'examples': True,
            'step_by_step': True
        }
        
        if person_id and person_id in self.person_cache:
            person = self.person_cache[person_id]
            
            # Adjust based on skill level
            skill_level = person.get('skill_level', 'beginner')
            if skill_level == 'advanced':
                recommendations['detail_level'] = 'high'
                recommendations['technical_terms'] = True
            elif skill_level == 'beginner':
                recommendations['detail_level'] = 'simple'
                recommendations['analogies'] = True
                recommendations['safety_reminders'] = True
        
        return recommendations
    
    def get_memory_stats(self):
        """Get memory system statistics"""
        """Get memory system statistics"""
        
        return {
            'total_conversations': len(self.conversation_cache),
            'known_people': len(self.person_cache),
            'active_projects': len([p for p in self.project_cache.values() if p['status'] in ['planning', 'in_progress']]),
            'completed_projects': len([p for p in self.project_cache.values() if p['status'] == 'completed']),
            'memory_size_mb': self._calculate_memory_size(),
            'last_interaction': max([c.get('timestamp', '') for c in self.conversation_cache]) if self.conversation_cache else 'Never'
        }
    
    def _calculate_memory_size(self):
        """Calculate approximate memory usage in MB"""
        """Calculate approximate memory usage in MB"""
        
        try:
            total_size = 0
            for root, dirs, files in os.walk(self.memory_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    def export_memories(self, export_path):
        """Export memories for backup or analysis"""
        """Export memories for backup or analysis"""
        
        export_data = {
            'conversations': list(self.conversation_cache),
            'projects': dict(self.project_cache),
            'people': dict(self.person_cache),
            'export_timestamp': datetime.now().isoformat(),
            'stats': self.get_memory_stats()
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print("💾 Memories exported to {}".format(export_path))
    
    def cleanup_old_memories(self, days_to_keep=30):
        """Clean up old memories to save space"""
        """Clean up old memories to save space"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()
        
        # Clean up old conversations
        self.conversation_cache = deque([
            c for c in self.conversation_cache 
            if c.get('timestamp', '') > cutoff_str
        ], maxlen=100)
        
        print("🧹 Cleaned up memories older than {} days".format(days_to_keep))

# Test function
def test_memory_system():
    """Test the enhanced memory system"""
    from config import Config
    
    print("Testing Enhanced Memory System...")
    
    memory = ElleeBrainMemory(Config)
    
    # Test conversation memory
    sample_conversation = {
        'messages': [
            {'role': 'user', 'content': 'Hello Ellee, can you help me with an Arduino project?'},
            {'role': 'assistant', 'content': 'Of course! I\'d love to help with your Arduino project. What are you trying to build?'},
            {'role': 'user', 'content': 'I want to make an LED blink circuit'},
            {'role': 'assistant', 'content': 'Great choice for a beginner project! You\'ll need an Arduino, LED, resistor, and breadboard...'}
        ]
    }
    
    conv_id = memory.remember_conversation(sample_conversation, person_id="test_user_001")
    print("✅ Conversation remembered with ID: {}".format(conv_id))
    
    # Test project memory
    sample_project = {
        'name': 'LED Blink Circuit',
        'description': 'Basic Arduino project to blink an LED',
        'components': ['Arduino Uno', 'LED', '220Ω Resistor', 'Breadboard', 'Jumper Wires'],
        'difficulty': 'beginner',
        'next_steps': ['Connect LED to pin 13', 'Upload blink sketch', 'Test circuit']
    }
    
    project_id = memory.remember_project(sample_project)
    print("✅ Project remembered with ID: {}".format(project_id))
    
    # Test context generation
    context = memory.get_conversation_context(person_id="test_user_001")
    print("✅ Generated context: {}".format(context))
    
    # Test memory stats
    stats = memory.get_memory_stats()
    print("✅ Memory stats: {}".format(stats))
    
    print("🎉 Memory system test completed successfully!")
    return True

if __name__ == "__main__":
    test_memory_system()