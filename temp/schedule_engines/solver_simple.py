import collections
import sqlite3
import json
import random

def load_data_from_database(db_file="school_timetable.db"):
    """Load all scheduling data from the database"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Load teachers
    cursor.execute("SELECT id, name, availability_json FROM teachers")
    teachers_data = cursor.fetchall()
    teachers = {row[0]: row[1] for row in teachers_data}
    teacher_availability = {}
    for row in teachers_data:
        if row[2]:  # availability_json is not empty
            avail_data = json.loads(row[2])
            for day_str, periods in avail_data.items():
                day = int(day_str)
                for period in periods:
                    teacher_availability[(row[0] - 1, day, period)] = 0  # 0 means unavailable
    
    # Load classes
    cursor.execute("SELECT id, name FROM classes")
    classes_data = cursor.fetchall()
    classes = {row[0]: row[1] for row in classes_data}
    
    # Load subjects
    cursor.execute("SELECT id, name, needs_lab FROM subjects")
    subjects_data = cursor.fetchall()
    subjects = {row[0]: row[1] for row in subjects_data}
    subject_needs_lab = {row[0]: bool(row[2]) for row in subjects_data}
    
    # Load rooms
    cursor.execute("SELECT id, name, is_lab FROM rooms")
    rooms_data = cursor.fetchall()
    rooms = {row[0]: row[1] for row in rooms_data}
    room_is_lab = {row[0]: bool(row[2]) for row in rooms_data}
    
    # Load lessons requirements
    cursor.execute("SELECT class_id, subject_id, lessons_per_week FROM lessons")
    lessons_data = cursor.fetchall()
    lessons = {(row[0] - 1, row[1] - 1): row[2] for row in lessons_data}  # Convert to 0-based indexing
    
    # Load teacher preferences
    cursor.execute("SELECT teacher_id, class_id, preference_score FROM teacher_preferences")
    preferences_data = cursor.fetchall()
    teacher_preferences = {(row[0] - 1, row[1] - 1): row[2] for row in preferences_data}  # Convert to 0-based indexing
    
    conn.close()
    
    return {
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects,
        'rooms': rooms,
        'lessons': lessons,
        'teacher_availability': teacher_availability,
        'teacher_preferences': teacher_preferences,
        'subject_needs_lab': subject_needs_lab,
        'room_is_lab': room_is_lab
    }

def save_solution_to_database(solution, data, db_file="school_timetable.db"):
    """Save the generated solution to the database"""
    if not solution:
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Clear existing schedules (except locked ones)
    cursor.execute("DELETE FROM schedules WHERE is_locked = 0")
    
    # Save new schedule
    for item in solution:
        # Find the appropriate room for this lesson
        subject_id = None
        teacher_id = None
        class_id = None
        
        # Find IDs by names
        for sid, sname in data['subjects'].items():
            if sname == item['subject']:
                subject_id = sid
                break
        
        for tid, tname in data['teachers'].items():
            if tname == item['teacher']:
                teacher_id = tid
                break
                
        for cid, cname in data['classes'].items():
            if cname == item['class']:
                class_id = cid
                break
        
        # Select appropriate room
        room_id = 1  # Default room
        needs_lab = data['subject_needs_lab'].get(subject_id, False)
        
        if needs_lab:
            # Find a lab room
            for rid, is_lab in data['room_is_lab'].items():
                if is_lab:
                    room_id = rid
                    break
        else:
            # Find a regular room
            for rid, is_lab in data['room_is_lab'].items():
                if not is_lab:
                    room_id = rid
                    break
        
        cursor.execute("""
            INSERT INTO schedules (class_id, teacher_id, subject_id, room_id, day_of_week, timeslot, is_locked)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (class_id, teacher_id, subject_id, room_id, item['day'], item['period']))
    
    conn.commit()
    conn.close()

def solve_school_scheduling_from_db(db_file="school_timetable.db"):
    """
    Simple greedy algorithm to solve school scheduling (alternative to OR-Tools)
    """
    # Load data from database
    data = load_data_from_database(db_file)
    
    # Convert to lists for processing (0-based indexing)
    teachers = [data['teachers'][i+1] for i in range(len(data['teachers']))]
    classes = [data['classes'][i+1] for i in range(len(data['classes']))]
    subjects = [data['subjects'][i+1] for i in range(len(data['subjects']))]
    rooms = [data['rooms'][i+1] for i in range(len(data['rooms']))]
    
    num_days = 5
    num_periods = 8
    
    # Initialize schedule tracking
    teacher_schedule = {}  # (teacher_id, day, period) -> True if busy
    class_schedule = {}    # (class_id, day, period) -> True if busy
    room_schedule = {}     # (room_id, day, period) -> True if busy
    
    # Create lesson requirements list
    lesson_requirements = []
    for (class_idx, subject_idx), count in data['lessons'].items():
        for _ in range(count):
            lesson_requirements.append((class_idx, subject_idx))
    
    # Shuffle for randomness
    random.shuffle(lesson_requirements)
    
    timetable = []
    failed_assignments = []
    
    for class_idx, subject_idx in lesson_requirements:
        assigned = False
        
        # Try to find a suitable time slot
        for day in range(num_days):
            for period in range(num_periods):
                # Check if class is available
                if (class_idx, day, period) in class_schedule:
                    continue
                    
                # Find a suitable teacher for this subject
                suitable_teacher = None
                for teacher_idx in range(len(teachers)):
                    # Check if teacher is available
                    if (teacher_idx, day, period) in teacher_schedule:
                        continue
                    
                    # Check teacher availability constraints
                    if (teacher_idx, day, period) in data['teacher_availability']:
                        if data['teacher_availability'][(teacher_idx, day, period)] == 0:
                            continue
                    
                    # Found a suitable teacher
                    suitable_teacher = teacher_idx
                    break
                
                if suitable_teacher is None:
                    continue
                
                # Find a suitable room
                suitable_room = None
                subject_id = subject_idx + 1  # Convert to 1-based for lookup
                needs_lab = data['subject_needs_lab'].get(subject_id, False)
                
                for room_idx in range(len(rooms)):
                    # Check if room is available
                    if (room_idx, day, period) in room_schedule:
                        continue
                    
                    room_id = room_idx + 1  # Convert to 1-based for lookup
                    is_lab = data['room_is_lab'].get(room_id, False)
                    
                    # Check room-subject compatibility
                    if needs_lab and not is_lab:
                        continue
                    if not needs_lab and is_lab:
                        # Allow regular subjects in labs if no regular rooms available
                        pass
                    
                    suitable_room = room_idx
                    break
                
                if suitable_room is None:
                    continue
                
                # Assign the lesson
                teacher_schedule[(suitable_teacher, day, period)] = True
                class_schedule[(class_idx, day, period)] = True
                room_schedule[(suitable_room, day, period)] = True
                
                timetable.append({
                    "day": day,
                    "period": period,
                    "class": classes[class_idx],
                    "teacher": teachers[suitable_teacher],
                    "subject": subjects[subject_idx],
                    "room": rooms[suitable_room]
                })
                
                assigned = True
                break
                
            if assigned:
                break
        
        if not assigned:
            failed_assignments.append((classes[class_idx], subjects[subject_idx]))
    
    if failed_assignments:
        print(f"Warning: Could not assign {len(failed_assignments)} lessons:")
        for class_name, subject_name in failed_assignments:
            print(f"  - {class_name}: {subject_name}")
    
    print(f"Successfully scheduled {len(timetable)} lessons")
    
    # Save solution to database
    save_solution_to_database(timetable, data, db_file)
    return timetable

if __name__ == '__main__':
    # Test the solver with database data
    print("Testing school scheduling solver (simple greedy algorithm)...")
    solution = solve_school_scheduling_from_db()
    if solution:
        # Sort for readability
        solution.sort(key=lambda x: (x['day'], x['period'], x['class']))
        for item in solution:
            print(f"Day {item['day']}, Period {item['period']}: Class {item['class']} has {item['subject']} with {item['teacher']} in {item['room']}")
    else:
        print("No solution found. Check constraints and data.")