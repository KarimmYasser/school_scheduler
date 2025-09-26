"""
Fast Scheduling Engine with Multiple Optimization Strategies
Implements various fast scheduling algorithms including ML-inspired approaches
"""

import sqlite3
import json
import random
import time
from typing import Dict, List, Tuple, Set
import numpy as np

class FastScheduler:
    def __init__(self, db_file="school_timetable.db"):
        self.db_file = db_file
        self.data = self.load_data()
        self.schedule = {}
        self.conflicts = set()
        
        # Scheduling parameters
        self.num_days = 5
        self.num_periods = 8
        self.all_days = range(self.num_days)
        self.all_periods = range(self.num_periods)
        
    def load_data(self):
        """Load and preprocess data for fast access"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        data = {}
        
        # Load teachers with availability preprocessing
        cursor.execute("SELECT id, name, availability_json FROM teachers")
        teachers_data = cursor.fetchall()
        data['teachers'] = {row[0]: row[1] for row in teachers_data}
        data['teacher_availability'] = {}
        
        for row in teachers_data:
            teacher_id = row[0]
            # Initialize all slots as available
            data['teacher_availability'][teacher_id] = set()
            if row[2]:  # Parse unavailable times
                avail_data = json.loads(row[2])
                for day_str, periods in avail_data.items():
                    day = int(day_str)
                    for period in periods:
                        data['teacher_availability'][teacher_id].add((day, period))
        
        # Load classes
        cursor.execute("SELECT id, name, grade_level FROM classes")
        data['classes'] = {row[0]: {'name': row[1], 'grade': row[2]} for row in cursor.fetchall()}
        
        # Load subjects with lab requirements
        cursor.execute("SELECT id, name, needs_lab FROM subjects")
        data['subjects'] = {row[0]: {'name': row[1], 'needs_lab': bool(row[2])} for row in cursor.fetchall()}
        
        # Load rooms with lab flags
        cursor.execute("SELECT id, name, is_lab FROM rooms")
        data['rooms'] = {row[0]: {'name': row[1], 'is_lab': bool(row[2])} for row in cursor.fetchall()}
        
        # Precompute lab/regular room lists
        data['lab_rooms'] = [rid for rid, room in data['rooms'].items() if room['is_lab']]
        data['regular_rooms'] = [rid for rid, room in data['rooms'].items() if not room['is_lab']]
        
        # Load lesson requirements
        cursor.execute("SELECT class_id, subject_id, lessons_per_week FROM lessons")
        data['lesson_requirements'] = cursor.fetchall()
        
        # Load teacher preferences and preprocess
        cursor.execute("SELECT teacher_id, class_id, preference_score FROM teacher_preferences")
        data['preferences'] = {}
        for teacher_id, class_id, score in cursor.fetchall():
            data['preferences'][(teacher_id, class_id)] = score
        
        # Find qualified teachers for each subject (based on preferences)
        data['subject_teachers'] = {}
        for (teacher_id, class_id), score in data['preferences'].items():
            if score >= 3:  # Only consider teachers with decent preference
                for class_id2, subject_id, _ in data['lesson_requirements']:
                    if class_id2 == class_id:
                        if subject_id not in data['subject_teachers']:
                            data['subject_teachers'][subject_id] = []
                        if teacher_id not in data['subject_teachers'][subject_id]:
                            data['subject_teachers'][subject_id].append(teacher_id)
        
        conn.close()
        return data
    
    def is_teacher_available(self, teacher_id: int, day: int, period: int) -> bool:
        """Check if teacher is available at given time"""
        return (day, period) not in self.data['teacher_availability'].get(teacher_id, set())
    
    def is_time_slot_free(self, teacher_id: int, class_id: int, room_id: int, day: int, period: int) -> bool:
        """Check if time slot is free for all resources"""
        key = (day, period)
        
        # Check if teacher is already scheduled
        for (t, c, r, d, p) in self.schedule.keys():
            if d == day and p == period and t == teacher_id:
                return False
        
        # Check if class is already scheduled
        for (t, c, r, d, p) in self.schedule.keys():
            if d == day and p == period and c == class_id:
                return False
        
        # Check if room is already scheduled
        for (t, c, r, d, p) in self.schedule.keys():
            if d == day and p == period and r == room_id:
                return False
        
        # Check teacher availability
        return self.is_teacher_available(teacher_id, day, period)
    
    def get_best_room(self, subject_id: int) -> int:
        """Get the best room for a subject"""
        needs_lab = self.data['subjects'][subject_id]['needs_lab']
        
        if needs_lab:
            available_rooms = self.data['lab_rooms']
        else:
            available_rooms = self.data['regular_rooms']
        
        if not available_rooms:
            # Fallback to any room
            available_rooms = list(self.data['rooms'].keys())
        
        return available_rooms[0] if available_rooms else 1
    
    def calculate_fitness(self, schedule: Dict) -> float:
        """Calculate fitness score for a schedule (higher is better)"""
        score = 0
        
        # Reward completed lessons
        score += len(schedule) * 10
        
        # Reward teacher preferences
        for (teacher_id, class_id, room_id, day, period), (subj_id, lessons) in schedule.items():
            pref_score = self.data['preferences'].get((teacher_id, class_id), 3)
            score += pref_score * 2
        
        # Penalize teacher gaps (encourage compact schedules)
        teacher_schedules = {}
        for (teacher_id, class_id, room_id, day, period), _ in schedule.items():
            if teacher_id not in teacher_schedules:
                teacher_schedules[teacher_id] = {}
            if day not in teacher_schedules[teacher_id]:
                teacher_schedules[teacher_id][day] = []
            teacher_schedules[teacher_id][day].append(period)
        
        for teacher_id, days in teacher_schedules.items():
            for day, periods in days.items():
                if len(periods) > 1:
                    periods.sort()
                    gaps = sum(1 for i in range(len(periods)-1) if periods[i+1] - periods[i] > 1)
                    score -= gaps * 5
        
        return score
    
    def greedy_schedule(self) -> Dict:
        """Fast greedy scheduling algorithm"""
        schedule = {}
        
        # Create lesson list with priorities
        lessons_to_schedule = []
        for class_id, subject_id, lessons_per_week in self.data['lesson_requirements']:
            # Get qualified teachers for this subject
            qualified_teachers = self.data['subject_teachers'].get(subject_id, list(self.data['teachers'].keys()))
            if not qualified_teachers:
                qualified_teachers = list(self.data['teachers'].keys())
            
            # Sort teachers by preference for this class
            qualified_teachers.sort(key=lambda t: self.data['preferences'].get((t, class_id), 3), reverse=True)
            
            for lesson_num in range(lessons_per_week):
                lessons_to_schedule.append({
                    'class_id': class_id,
                    'subject_id': subject_id,
                    'qualified_teachers': qualified_teachers,
                    'priority': lessons_per_week  # Higher lessons per week = higher priority
                })
        
        # Sort by priority
        lessons_to_schedule.sort(key=lambda x: x['priority'], reverse=True)
        
        # Schedule lessons greedily
        for lesson in lessons_to_schedule:
            class_id = lesson['class_id']
            subject_id = lesson['subject_id']
            qualified_teachers = lesson['qualified_teachers']
            
            scheduled = False
            
            # Try each qualified teacher
            for teacher_id in qualified_teachers:
                if scheduled:
                    break
                
                # Get best room for this subject
                room_id = self.get_best_room(subject_id)
                
                # Try each time slot
                for day in self.all_days:
                    if scheduled:
                        break
                    for period in self.all_periods:
                        if self.is_time_slot_free(teacher_id, class_id, room_id, day, period):
                            key = (teacher_id, class_id, room_id, day, period)
                            schedule[key] = (subject_id, 1)
                            scheduled = True
                            break
                
                # If room not available, try other rooms
                if not scheduled:
                    all_rooms = list(self.data['rooms'].keys())
                    for room_id in all_rooms:
                        if scheduled:
                            break
                        for day in self.all_days:
                            if scheduled:
                                break
                            for period in self.all_periods:
                                if self.is_time_slot_free(teacher_id, class_id, room_id, day, period):
                                    key = (teacher_id, class_id, room_id, day, period)
                                    schedule[key] = (subject_id, 1)
                                    scheduled = True
                                    break
        
        return schedule
    
    def genetic_schedule(self, population_size: int = 20, generations: int = 50) -> Dict:
        """Genetic algorithm for scheduling optimization"""
        
        def create_random_schedule():
            """Create a random valid schedule"""
            schedule = {}
            lessons_to_schedule = []
            
            for class_id, subject_id, lessons_per_week in self.data['lesson_requirements']:
                qualified_teachers = self.data['subject_teachers'].get(subject_id, list(self.data['teachers'].keys()))
                if not qualified_teachers:
                    qualified_teachers = list(self.data['teachers'].keys())
                
                for _ in range(lessons_per_week):
                    lessons_to_schedule.append((class_id, subject_id, random.choice(qualified_teachers)))
            
            random.shuffle(lessons_to_schedule)
            
            for class_id, subject_id, teacher_id in lessons_to_schedule:
                room_id = self.get_best_room(subject_id)
                
                # Try random time slots
                attempts = 0
                max_attempts = 50
                while attempts < max_attempts:
                    day = random.randint(0, self.num_days - 1)
                    period = random.randint(0, self.num_periods - 1)
                    
                    if is_time_slot_free_for_schedule(schedule, teacher_id, class_id, room_id, day, period):
                        key = (teacher_id, class_id, room_id, day, period)
                        schedule[key] = (subject_id, 1)
                        break
                    attempts += 1
            
            return schedule
        
        def is_time_slot_free_for_schedule(schedule, teacher_id, class_id, room_id, day, period):
            """Check if time slot is free in given schedule"""
            for (t, c, r, d, p) in schedule.keys():
                if d == day and p == period:
                    if t == teacher_id or c == class_id or r == room_id:
                        return False
            # Check teacher availability
            return (day, period) not in self.data['teacher_availability'].get(teacher_id, set())
        
        def mutate_schedule(schedule):
            """Mutate a schedule by moving random lessons"""
            mutated = schedule.copy()
            
            if not mutated:
                return mutated
            
            # Move 1-3 random lessons
            num_mutations = random.randint(1, min(3, len(mutated)))
            keys = list(mutated.keys())
            
            for _ in range(num_mutations):
                if not keys:
                    break
                
                key = random.choice(keys)
                teacher_id, class_id, room_id, old_day, old_period = key
                subject_id, lessons = mutated[key]
                
                # Remove old assignment
                del mutated[key]
                keys.remove(key)
                
                # Try to place in new slot
                attempts = 0
                max_attempts = 20
                while attempts < max_attempts:
                    new_day = random.randint(0, self.num_days - 1)
                    new_period = random.randint(0, self.num_periods - 1)
                    
                    if is_time_slot_free_for_schedule(mutated, teacher_id, class_id, room_id, new_day, new_period):
                        new_key = (teacher_id, class_id, room_id, new_day, new_period)
                        mutated[new_key] = (subject_id, lessons)
                        break
                    attempts += 1
                else:
                    # Put it back if we can't find a new slot
                    mutated[key] = (subject_id, lessons)
            
            return mutated
        
        # Initialize population
        population = []
        for _ in range(population_size):
            population.append(create_random_schedule())
        
        best_schedule = None
        best_fitness = -float('inf')
        
        # Evolution
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for schedule in population:
                fitness = self.calculate_fitness(schedule)
                fitness_scores.append(fitness)
                
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_schedule = schedule.copy()
            
            # Selection and reproduction
            new_population = []
            
            # Keep best 20%
            elite_count = population_size // 5
            sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
            for i in range(elite_count):
                new_population.append(population[sorted_indices[i]])
            
            # Generate rest through mutation
            while len(new_population) < population_size:
                parent = random.choice(population[:elite_count * 2])  # Select from top performers
                child = mutate_schedule(parent)
                new_population.append(child)
            
            population = new_population
            
            if generation % 10 == 0:
                print(f"Generation {generation}: Best fitness = {best_fitness:.2f}, Lessons = {len(best_schedule)}")
        
        return best_schedule or {}
    
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

def solve_with_fast_scheduler(method="greedy", db_file="school_timetable.db"):
    """
    Main function to solve scheduling with fast algorithms
    
    Args:
        method: "greedy", "genetic", or "hybrid"
        db_file: Database file path
    """
    scheduler = FastScheduler(db_file)
    
    print(f"Starting {method} scheduling...")
    start_time = time.time()
    
    if method == "greedy":
        schedule = scheduler.greedy_schedule()
    elif method == "genetic":
        schedule = scheduler.genetic_schedule(population_size=30, generations=100)
    elif method == "hybrid":
        # Start with greedy, then optimize with genetic
        greedy_schedule = scheduler.greedy_schedule()
        scheduler.schedule = greedy_schedule
        schedule = scheduler.genetic_schedule(population_size=20, generations=50)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    end_time = time.time()
    
    print(f"Scheduling completed in {end_time - start_time:.2f} seconds")
    print(f"Generated {len(schedule)} lessons")
    
    if schedule:
        fitness = scheduler.calculate_fitness(schedule)
        print(f"Schedule fitness: {fitness:.2f}")
        scheduler.save_schedule_to_db(schedule)
        return True
    else:
        print("No schedule generated")
        return False

if __name__ == "__main__":
    # Test different methods
    print("=== Testing Greedy Algorithm ===")
    solve_with_fast_scheduler("greedy")
    
    print("\n=== Testing Genetic Algorithm ===")
    solve_with_fast_scheduler("genetic")
    
    print("\n=== Testing Hybrid Algorithm ===")
    solve_with_fast_scheduler("hybrid")