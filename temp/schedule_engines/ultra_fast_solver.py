"""
Ultra-Fast Scheduling Engine
Optimized for speed with multiple fast algorithms
"""

import sqlite3
import json
import random
import time
from typing import Dict, List, Tuple
from collections import defaultdict

class UltraFastScheduler:
    def __init__(self, db_file="school_timetable.db"):
        self.db_file = db_file
        self.data = self.load_data_optimized()
        
        # Scheduling parameters
        self.num_days = 5
        self.num_periods = 8
        
    def load_data_optimized(self):
        """Load data with optimized structure for fast access"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        data = {
            'teachers': {},
            'teacher_unavailable': defaultdict(set),  # teacher_id -> {(day, period)}
            'classes': {},
            'subjects': {},
            'rooms': {'lab': [], 'regular': []},
            'lesson_requirements': [],
            'teacher_preferences': defaultdict(dict),  # teacher_id -> {class_id: score}
            'qualified_teachers': defaultdict(list)  # subject_id -> [teacher_ids]
        }
        
        # Load teachers
        cursor.execute("SELECT id, name, availability_json FROM teachers")
        for teacher_id, name, availability_json in cursor.fetchall():
            data['teachers'][teacher_id] = name
            if availability_json:
                avail_data = json.loads(availability_json)
                for day_str, periods in avail_data.items():
                    day = int(day_str)
                    for period in periods:
                        data['teacher_unavailable'][teacher_id].add((day, period))
        
        # Load classes
        cursor.execute("SELECT id, name, grade_level FROM classes")
        for class_id, name, grade in cursor.fetchall():
            data['classes'][class_id] = {'name': name, 'grade': grade}
        
        # Load subjects
        cursor.execute("SELECT id, name, needs_lab FROM subjects")
        for subject_id, name, needs_lab in cursor.fetchall():
            data['subjects'][subject_id] = {'name': name, 'needs_lab': bool(needs_lab)}
        
        # Load rooms
        cursor.execute("SELECT id, name, is_lab FROM rooms")
        for room_id, name, is_lab in cursor.fetchall():
            if is_lab:
                data['rooms']['lab'].append(room_id)
            else:
                data['rooms']['regular'].append(room_id)
        
        # Load lesson requirements
        cursor.execute("SELECT class_id, subject_id, lessons_per_week FROM lessons")
        data['lesson_requirements'] = cursor.fetchall()
        
        # Load teacher preferences
        cursor.execute("SELECT teacher_id, class_id, preference_score FROM teacher_preferences")
        for teacher_id, class_id, score in cursor.fetchall():
            data['teacher_preferences'][teacher_id][class_id] = score
        
        # Build qualified teachers map
        for teacher_id in data['teachers']:
            for class_id in data['classes']:
                pref_score = data['teacher_preferences'][teacher_id].get(class_id, 3)
                if pref_score >= 3:  # Minimum acceptable preference
                    # Find subjects for this class
                    for c_id, s_id, _ in data['lesson_requirements']:
                        if c_id == class_id:
                            if teacher_id not in data['qualified_teachers'][s_id]:
                                data['qualified_teachers'][s_id].append(teacher_id)
        
        conn.close()
        return data
    
    def is_available(self, teacher_id: int, class_id: int, room_id: int, 
                    day: int, period: int, schedule: Dict) -> bool:
        """Ultra-fast conflict checking"""
        # Check teacher availability
        if (day, period) in self.data['teacher_unavailable'][teacher_id]:
            return False
        
        # Check for conflicts in current schedule
        time_key = (day, period)
        if time_key in schedule:
            used_teachers, used_classes, used_rooms = schedule[time_key]
            if teacher_id in used_teachers or class_id in used_classes or room_id in used_rooms:
                return False
        
        return True
    
    def ultra_fast_greedy(self) -> Dict:
        """Ultra-fast greedy algorithm with optimized data structures"""
        # Use a different schedule structure for speed
        # schedule[time_key] = (set(teachers), set(classes), set(rooms))
        schedule_usage = {}
        final_schedule = {}
        
        # Create prioritized lesson list
        lessons = []
        for class_id, subject_id, lessons_per_week in self.data['lesson_requirements']:
            priority = lessons_per_week * 10 + (6 - (class_id % 5))  # Prefer more lessons and higher grades
            
            # Get best teachers for this combination
            qualified = self.data['qualified_teachers'].get(subject_id, list(self.data['teachers'].keys()))
            if not qualified:
                qualified = list(self.data['teachers'].keys())
            
            # Sort by preference
            qualified.sort(key=lambda t: self.data['teacher_preferences'][t].get(class_id, 3), reverse=True)
            
            for _ in range(lessons_per_week):
                lessons.append((priority, class_id, subject_id, qualified))
        
        # Sort by priority
        lessons.sort(reverse=True)
        
        # Schedule greedily
        for priority, class_id, subject_id, qualified_teachers in lessons:
            scheduled = False
            
            # Get appropriate rooms
            needs_lab = self.data['subjects'][subject_id]['needs_lab']
            preferred_rooms = self.data['rooms']['lab'] if needs_lab else self.data['rooms']['regular']
            if not preferred_rooms:
                preferred_rooms = self.data['rooms']['lab'] + self.data['rooms']['regular']
            
            # Try best teachers first
            for teacher_id in qualified_teachers[:3]:  # Only try top 3 teachers for speed
                if scheduled:
                    break
                
                # Try preferred rooms first
                for room_id in preferred_rooms:
                    if scheduled:
                        break
                    
                    # Try time slots (morning first for better quality)
                    time_slots = [(d, p) for d in range(self.num_days) for p in range(self.num_periods)]
                    
                    for day, period in time_slots:
                        time_key = (day, period)
                        
                        # Fast availability check
                        if (day, period) in self.data['teacher_unavailable'][teacher_id]:
                            continue
                        
                        # Check conflicts
                        if time_key in schedule_usage:
                            teachers, classes, rooms = schedule_usage[time_key]
                            if teacher_id in teachers or class_id in classes or room_id in rooms:
                                continue
                        else:
                            schedule_usage[time_key] = (set(), set(), set())
                        
                        # Make assignment
                        schedule_usage[time_key][0].add(teacher_id)
                        schedule_usage[time_key][1].add(class_id)
                        schedule_usage[time_key][2].add(room_id)
                        
                        final_schedule[(teacher_id, class_id, room_id, day, period)] = (subject_id, 1)
                        scheduled = True
                        break
        
        return final_schedule
    
    def smart_greedy(self) -> Dict:
        """Smart greedy with heuristics for better quality"""
        schedule = {}
        
        # Track usage per time slot
        time_usage = defaultdict(lambda: {'teachers': set(), 'classes': set(), 'rooms': set()})
        
        # Create weighted lesson list
        weighted_lessons = []
        for class_id, subject_id, lessons_per_week in self.data['lesson_requirements']:
            # Calculate base priority
            base_priority = lessons_per_week * 100
            
            # Subject-specific bonuses
            subject_name = self.data['subjects'][subject_id]['name'].lower()
            if any(word in subject_name for word in ['math', 'algebra', 'geometry', 'calculus']):
                base_priority += 50  # Math gets priority
            elif any(word in subject_name for word in ['physics', 'chemistry', 'biology']):
                base_priority += 40  # Science gets priority
            elif 'english' in subject_name or 'literature' in subject_name:
                base_priority += 30  # Language gets priority
            
            # Grade level bonus (higher grades get slight priority)
            grade = self.data['classes'][class_id]['grade']
            base_priority += grade * 2
            
            for lesson_num in range(lessons_per_week):
                weighted_lessons.append({
                    'priority': base_priority,
                    'class_id': class_id,
                    'subject_id': subject_id,
                    'lesson_num': lesson_num
                })
        
        # Sort by priority
        weighted_lessons.sort(key=lambda x: x['priority'], reverse=True)
        
        # Schedule each lesson
        for lesson in weighted_lessons:
            class_id = lesson['class_id']
            subject_id = lesson['subject_id']
            
            # Get qualified teachers
            qualified_teachers = self.data['qualified_teachers'].get(subject_id, list(self.data['teachers'].keys()))
            if not qualified_teachers:
                qualified_teachers = list(self.data['teachers'].keys())
            
            # Sort by preference for this class
            qualified_teachers.sort(
                key=lambda t: self.data['teacher_preferences'][t].get(class_id, 3), 
                reverse=True
            )
            
            # Get appropriate rooms
            needs_lab = self.data['subjects'][subject_id]['needs_lab']
            room_candidates = self.data['rooms']['lab'] if needs_lab else self.data['rooms']['regular']
            if not room_candidates:
                room_candidates = self.data['rooms']['lab'] + self.data['rooms']['regular']
            
            best_assignment = None
            best_score = -1
            
            # Try assignments and score them
            for teacher_id in qualified_teachers[:5]:  # Top 5 teachers
                for room_id in room_candidates[:3]:  # Top 3 rooms
                    for day in range(self.num_days):
                        for period in range(self.num_periods):
                            # Check availability
                            if (day, period) in self.data['teacher_unavailable'][teacher_id]:
                                continue
                            
                            # Check conflicts
                            usage = time_usage[(day, period)]
                            if (teacher_id in usage['teachers'] or 
                                class_id in usage['classes'] or 
                                room_id in usage['rooms']):
                                continue
                            
                            # Calculate score for this assignment
                            score = self.calculate_assignment_score(
                                teacher_id, class_id, subject_id, day, period, schedule)
                            
                            if score > best_score:
                                best_score = score
                                best_assignment = (teacher_id, class_id, room_id, day, period)
            
            # Make the best assignment
            if best_assignment:
                teacher_id, class_id, room_id, day, period = best_assignment
                
                # Update usage tracking
                usage = time_usage[(day, period)]
                usage['teachers'].add(teacher_id)
                usage['classes'].add(class_id)
                usage['rooms'].add(room_id)
                
                # Add to schedule
                schedule[best_assignment] = (subject_id, 1)
        
        return schedule
    
    def calculate_assignment_score(self, teacher_id: int, class_id: int, subject_id: int, 
                                 day: int, period: int, current_schedule: Dict) -> float:
        """Calculate score for assignment quality"""
        score = 0
        
        # Teacher preference bonus
        pref = self.data['teacher_preferences'][teacher_id].get(class_id, 3)
        score += pref * 10
        
        # Time-based bonuses
        subject_name = self.data['subjects'][subject_id]['name'].lower()
        
        # Math/Science morning bonus
        if any(word in subject_name for word in ['math', 'algebra', 'geometry', 'calculus', 'physics', 'chemistry']):
            if period < 4:  # Morning
                score += 20
            else:
                score -= 5
        
        # PE/Arts afternoon bonus
        if any(word in subject_name for word in ['physical', 'art', 'music', 'drama']):
            if period >= 4:  # Afternoon
                score += 15
            else:
                score -= 5
        
        # Avoid lunch time (period 4)
        if period == 4:
            score -= 10
        
        # Compact schedule bonus (less gaps)
        teacher_day_periods = []
        for (t_id, c_id, r_id, d, p), _ in current_schedule.items():
            if t_id == teacher_id and d == day:
                teacher_day_periods.append(p)
        
        if teacher_day_periods:
            teacher_day_periods.append(period)
            teacher_day_periods.sort()
            # Bonus for adjacent periods
            for i in range(len(teacher_day_periods) - 1):
                if teacher_day_periods[i + 1] - teacher_day_periods[i] == 1:
                    score += 5
        
        return score
    
    def save_schedule_to_db(self, schedule: Dict):
        """Save schedule to database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Clear existing non-locked schedules
        cursor.execute("DELETE FROM schedules WHERE is_locked = 0")
        
        # Insert new schedule
        for (teacher_id, class_id, room_id, day, period), (subject_id, _) in schedule.items():
            cursor.execute("""
                INSERT INTO schedules (class_id, teacher_id, subject_id, room_id, day_of_week, timeslot, is_locked)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            """, (class_id, teacher_id, subject_id, room_id, day, period))
        
        conn.commit()
        conn.close()

def solve_ultra_fast(method="ultra_fast", db_file="school_timetable.db"):
    """Solve with ultra-fast algorithms"""
    scheduler = UltraFastScheduler(db_file)
    
    start_time = time.time()
    
    if method == "ultra_fast":
        print("Running ultra-fast greedy algorithm...")
        schedule = scheduler.ultra_fast_greedy()
    elif method == "smart_greedy":
        print("Running smart greedy algorithm...")
        schedule = scheduler.smart_greedy()
    else:
        raise ValueError(f"Unknown method: {method}")
    
    end_time = time.time()
    
    print(f"Completed in {end_time - start_time:.3f} seconds")
    print(f"Generated {len(schedule)} lessons")
    
    if schedule:
        scheduler.save_schedule_to_db(schedule)
        return True
    else:
        print("No schedule generated")
        return False

if __name__ == "__main__":
    print("=== Ultra-Fast Scheduling Test ===")
    solve_ultra_fast("ultra_fast")
    
    print("\n=== Smart Greedy Test ===")
    solve_ultra_fast("smart_greedy")