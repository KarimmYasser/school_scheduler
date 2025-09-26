"""
Machine Learning-Inspired Scheduler
Uses pattern recognition and heuristics learned from scheduling data
"""

import sqlite3
import json
import numpy as np
import random
import time
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set

class MLScheduler:
    def __init__(self, db_file="school_timetable.db"):
        self.db_file = db_file
        self.data = self.load_data()
        
        # Scheduling parameters
        self.num_days = 5
        self.num_periods = 8
        
        # ML-inspired components
        self.pattern_weights = self.learn_patterns()
        self.preference_matrix = self.build_preference_matrix()
        self.conflict_penalties = self.initialize_conflict_penalties()
        
    def load_data(self):
        """Load and preprocess data"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        data = {}
        
        # Load all entities
        cursor.execute("SELECT id, name, availability_json FROM teachers")
        teachers_data = cursor.fetchall()
        data['teachers'] = {row[0]: row[1] for row in teachers_data}
        data['teacher_availability'] = {}
        
        for row in teachers_data:
            teacher_id = row[0]
            data['teacher_availability'][teacher_id] = set()
            if row[2]:
                avail_data = json.loads(row[2])
                for day_str, periods in avail_data.items():
                    day = int(day_str)
                    for period in periods:
                        data['teacher_availability'][teacher_id].add((day, period))
        
        cursor.execute("SELECT id, name, grade_level FROM classes")
        data['classes'] = {row[0]: {'name': row[1], 'grade': row[2]} for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, name, needs_lab FROM subjects")
        data['subjects'] = {row[0]: {'name': row[1], 'needs_lab': bool(row[2])} for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, name, is_lab FROM rooms")
        data['rooms'] = {row[0]: {'name': row[1], 'is_lab': bool(row[2])} for row in cursor.fetchall()}
        
        cursor.execute("SELECT class_id, subject_id, lessons_per_week FROM lessons")
        data['lesson_requirements'] = cursor.fetchall()
        
        cursor.execute("SELECT teacher_id, class_id, preference_score FROM teacher_preferences")
        data['preferences'] = {}
        for teacher_id, class_id, score in cursor.fetchall():
            data['preferences'][(teacher_id, class_id)] = score
        
        # Load existing schedules to learn from
        cursor.execute("""
            SELECT class_id, teacher_id, subject_id, room_id, day_of_week, timeslot
            FROM schedules
        """)
        data['existing_schedules'] = cursor.fetchall()
        
        conn.close()
        return data
    
    def learn_patterns(self) -> Dict:
        """Learn scheduling patterns from existing data"""
        patterns = {
            'time_preferences': defaultdict(lambda: defaultdict(int)),
            'subject_time_affinity': defaultdict(lambda: defaultdict(int)),
            'teacher_time_patterns': defaultdict(lambda: defaultdict(int)),
            'consecutive_subjects': defaultdict(int),
            'daily_distribution': defaultdict(lambda: defaultdict(int))
        }
        
        # Analyze existing schedules
        for schedule_entry in self.data['existing_schedules']:
            class_id, teacher_id, subject_id, room_id, day, period = schedule_entry
            
            # Time preferences
            patterns['time_preferences'][subject_id][(day, period)] += 1
            patterns['teacher_time_patterns'][teacher_id][(day, period)] += 1
            
            # Subject-time affinity (some subjects work better at certain times)
            if subject_id in self.data['subjects']:
                subject_name = self.data['subjects'][subject_id]['name'].lower()
                if 'math' in subject_name or 'algebra' in subject_name:
                    if period < 4:  # Morning preference
                        patterns['subject_time_affinity'][subject_id][(day, period)] += 2
                elif 'physical' in subject_name or 'art' in subject_name:
                    if period >= 4:  # Afternoon preference
                        patterns['subject_time_affinity'][subject_id][(day, period)] += 2
        
        # Default patterns if no existing schedules
        if not self.data['existing_schedules']:
            for subject_id in self.data['subjects']:
                subject_name = self.data['subjects'][subject_id]['name'].lower()
                for day in range(self.num_days):
                    for period in range(self.num_periods):
                        base_weight = 1
                        
                        # Math/Science in morning
                        if any(keyword in subject_name for keyword in ['math', 'algebra', 'geometry', 'calculus', 'physics', 'chemistry']):
                            if period < 4:
                                base_weight = 3
                        
                        # Arts/PE in afternoon
                        elif any(keyword in subject_name for keyword in ['art', 'music', 'physical', 'drama']):
                            if period >= 4:
                                base_weight = 3
                        
                        # Languages throughout day
                        elif any(keyword in subject_name for keyword in ['english', 'literature', 'language']):
                            base_weight = 2
                        
                        patterns['subject_time_affinity'][subject_id][(day, period)] = base_weight
        
        return patterns
    
    def build_preference_matrix(self) -> np.ndarray:
        """Build a preference matrix for teacher-class assignments"""
        num_teachers = len(self.data['teachers'])
        num_classes = len(self.data['classes'])
        
        # Initialize with neutral preferences
        matrix = np.ones((num_teachers + 1, num_classes + 1)) * 3  # Default preference of 3
        
        # Fill with actual preferences
        for (teacher_id, class_id), score in self.data['preferences'].items():
            if teacher_id <= num_teachers and class_id <= num_classes:
                matrix[teacher_id, class_id] = score
        
        return matrix
    
    def initialize_conflict_penalties(self) -> Dict:
        """Initialize conflict penalty weights"""
        return {
            'teacher_conflict': -1000,
            'class_conflict': -1000,
            'room_conflict': -1000,
            'availability_violation': -500,
            'lab_mismatch': -200,
            'consecutive_same_subject': -50,
            'teacher_gap': -20,
            'afternoon_math': -10,  # Slight penalty for math in afternoon
            'morning_pe': -10       # Slight penalty for PE in morning
        }
    
    def calculate_assignment_score(self, teacher_id: int, class_id: int, subject_id: int, 
                                 room_id: int, day: int, period: int, current_schedule: Dict) -> float:
        """Calculate ML-inspired score for a potential assignment"""
        score = 0
        
        # Base preference score
        if teacher_id <= len(self.data['teachers']) and class_id <= len(self.data['classes']):
            score += self.preference_matrix[teacher_id, class_id] * 10
        
        # Time-based patterns
        time_key = (day, period)
        score += self.pattern_weights['subject_time_affinity'][subject_id][time_key] * 5
        score += self.pattern_weights['teacher_time_patterns'][teacher_id][time_key] * 2
        
        # Check for conflicts (hard constraints)
        conflicts = self.check_conflicts(teacher_id, class_id, room_id, day, period, current_schedule)
        for conflict_type in conflicts:
            score += self.conflict_penalties[conflict_type]
        
        # Soft constraint bonuses/penalties
        
        # Lab requirement matching
        needs_lab = self.data['subjects'][subject_id]['needs_lab']
        room_is_lab = self.data['rooms'][room_id]['is_lab']
        if needs_lab == room_is_lab:
            score += 20
        else:
            score += self.conflict_penalties['lab_mismatch']
        
        # Subject-specific time preferences
        subject_name = self.data['subjects'][subject_id]['name'].lower()
        
        # Math/Science morning bonus
        if any(keyword in subject_name for keyword in ['math', 'algebra', 'geometry', 'calculus', 'physics', 'chemistry']):
            if period < 4:
                score += 15
            else:
                score += self.conflict_penalties['afternoon_math']
        
        # PE afternoon bonus
        if 'physical' in subject_name:
            if period >= 4:
                score += 15
            else:
                score += self.conflict_penalties['morning_pe']
        
        # Consecutive same subject penalty
        consecutive_count = self.count_consecutive_same_subject(
            class_id, subject_id, day, period, current_schedule)
        if consecutive_count >= 2:
            score += self.conflict_penalties['consecutive_same_subject'] * consecutive_count
        
        # Teacher gap penalty (encourage compact schedules)
        gap_penalty = self.calculate_teacher_gap_penalty(teacher_id, day, period, current_schedule)
        score += gap_penalty
        
        return score
    
    def check_conflicts(self, teacher_id: int, class_id: int, room_id: int, 
                       day: int, period: int, current_schedule: Dict) -> List[str]:
        """Check for scheduling conflicts"""
        conflicts = []
        
        # Check existing assignments at this time
        for (t_id, c_id, r_id, d, p), _ in current_schedule.items():
            if d == day and p == period:
                if t_id == teacher_id:
                    conflicts.append('teacher_conflict')
                if c_id == class_id:
                    conflicts.append('class_conflict')
                if r_id == room_id:
                    conflicts.append('room_conflict')
        
        # Check teacher availability
        if (day, period) in self.data['teacher_availability'].get(teacher_id, set()):
            conflicts.append('availability_violation')
        
        return conflicts
    
    def count_consecutive_same_subject(self, class_id: int, subject_id: int, 
                                     day: int, period: int, current_schedule: Dict) -> int:
        """Count consecutive lessons of the same subject"""
        count = 1  # Current lesson
        
        # Check before
        for p in range(period - 1, -1, -1):
            found = False
            for (t_id, c_id, r_id, d, p_check), (subj_id, _) in current_schedule.items():
                if c_id == class_id and d == day and p_check == p and subj_id == subject_id:
                    count += 1
                    found = True
                    break
            if not found:
                break
        
        # Check after
        for p in range(period + 1, self.num_periods):
            found = False
            for (t_id, c_id, r_id, d, p_check), (subj_id, _) in current_schedule.items():
                if c_id == class_id and d == day and p_check == p and subj_id == subject_id:
                    count += 1
                    found = True
                    break
            if not found:
                break
        
        return count
    
    def calculate_teacher_gap_penalty(self, teacher_id: int, day: int, period: int, 
                                    current_schedule: Dict) -> float:
        """Calculate penalty for teacher gaps in schedule"""
        teacher_periods = []
        
        # Find all periods where teacher is scheduled on this day
        for (t_id, c_id, r_id, d, p), _ in current_schedule.items():
            if t_id == teacher_id and d == day:
                teacher_periods.append(p)
        
        # Add current period
        teacher_periods.append(period)
        teacher_periods.sort()
        
        # Calculate gaps
        if len(teacher_periods) <= 1:
            return 0
        
        gaps = 0
        for i in range(len(teacher_periods) - 1):
            gap = teacher_periods[i + 1] - teacher_periods[i] - 1
            gaps += gap
        
        return gaps * self.conflict_penalties['teacher_gap']
    
    def ml_schedule(self) -> Dict:
        """ML-inspired scheduling algorithm"""
        schedule = {}
        
        # Create prioritized lesson list
        lessons_to_schedule = []
        for class_id, subject_id, lessons_per_week in self.data['lesson_requirements']:
            for lesson_num in range(lessons_per_week):
                # Find best teachers for this subject-class combination
                candidate_teachers = []
                for teacher_id in self.data['teachers'].keys():
                    pref_score = self.data['preferences'].get((teacher_id, class_id), 3)
                    if pref_score >= 2:  # Minimum acceptable preference
                        candidate_teachers.append((teacher_id, pref_score))
                
                # Sort by preference
                candidate_teachers.sort(key=lambda x: x[1], reverse=True)
                
                if not candidate_teachers:
                    candidate_teachers = [(list(self.data['teachers'].keys())[0], 3)]
                
                lessons_to_schedule.append({
                    'class_id': class_id,
                    'subject_id': subject_id,
                    'candidate_teachers': candidate_teachers,
                    'priority': lessons_per_week + (5 - class_id % 5)  # Prefer higher grades and more lessons
                })
        
        # Sort by priority
        lessons_to_schedule.sort(key=lambda x: x['priority'], reverse=True)
        
        # Schedule each lesson using ML scoring
        for lesson in lessons_to_schedule:
            class_id = lesson['class_id']
            subject_id = lesson['subject_id']
            candidate_teachers = lesson['candidate_teachers']
            
            best_assignment = None
            best_score = -float('inf')
            
            # Try top teachers and rooms only for speed
            for teacher_id, _ in candidate_teachers[:3]:  # Only top 3 teachers
                # Get appropriate rooms
                needs_lab = self.data['subjects'][subject_id]['needs_lab']
                if needs_lab:
                    room_candidates = [rid for rid, room in self.data['rooms'].items() if room['is_lab']]
                else:
                    room_candidates = [rid for rid, room in self.data['rooms'].items() if not room['is_lab']]
                
                if not room_candidates:
                    room_candidates = list(self.data['rooms'].keys())
                
                for room_id in room_candidates[:2]:  # Only top 2 rooms
                    for day in range(self.num_days):
                        for period in range(self.num_periods):
                            score = self.calculate_assignment_score(
                                teacher_id, class_id, subject_id, room_id, day, period, schedule)
                            
                            if score > best_score:
                                best_score = score
                                best_assignment = (teacher_id, class_id, room_id, day, period)
            
            # Make the best assignment if it's conflict-free
            if best_assignment and best_score > -500:  # Threshold for acceptable assignments
                key = best_assignment
                schedule[key] = (subject_id, 1)
        
        return schedule
    
    def save_schedule_to_db(self, schedule: Dict):
        """Save schedule to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Clear existing schedules
        cursor.execute("DELETE FROM schedules WHERE is_locked = 0")
        
        # Insert new schedule
        for (teacher_id, class_id, room_id, day, period), (subject_id, lessons) in schedule.items():
            cursor.execute("""
                INSERT INTO schedules (class_id, teacher_id, subject_id, room_id, day_of_week, timeslot, is_locked)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (class_id, teacher_id, subject_id, room_id, day, period))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(schedule)} lessons to database")

def solve_with_ml_scheduler(db_file="school_timetable.db"):
    """Solve scheduling using ML-inspired approach"""
    scheduler = MLScheduler(db_file)
    
    print("Starting ML-inspired scheduling...")
    start_time = time.time()
    
    schedule = scheduler.ml_schedule()
    
    end_time = time.time()
    
    print(f"ML scheduling completed in {end_time - start_time:.2f} seconds")
    print(f"Generated {len(schedule)} lessons")
    
    if schedule:
        scheduler.save_schedule_to_db(schedule)
        return True
    else:
        print("No schedule generated")
        return False

if __name__ == "__main__":
    solve_with_ml_scheduler()