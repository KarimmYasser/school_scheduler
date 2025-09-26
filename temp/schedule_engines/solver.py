import collections
import sqlite3
import json
from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import CpModel, CpSolver

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
    Main function to solve school scheduling using database data
    """
    # Load data from database
    data = load_data_from_database(db_file)
    
    # Convert to lists for OR-Tools (0-based indexing)
    teachers = [data['teachers'][i+1] for i in range(len(data['teachers']))]
    classes = [data['classes'][i+1] for i in range(len(data['classes']))]
    subjects = [data['subjects'][i+1] for i in range(len(data['subjects']))]
    rooms = [data['rooms'][i+1] for i in range(len(data['rooms']))]
    
    # Model
    model = CpModel()

    # --- Data Structures ---
    num_days = 5
    num_periods = 6  # Reduced to 6 periods for more manageable scheduling
    all_days = range(num_days)
    all_periods = range(num_periods)
    
    all_teachers = range(len(teachers))
    all_classes = range(len(classes))
    all_subjects = range(len(subjects))
    all_rooms = range(len(rooms))

    # --- Variables ---
    # scheduled_lesson[(c, t, s, r, d, p)] is true if class 'c' has subject 's' with teacher 't' in room 'r' on day 'd' at period 'p'.
    scheduled_lesson = {}
    for c in all_classes:
        for t in all_teachers:
            for s in all_subjects:
                for r in all_rooms:
                    for d in all_days:
                        for p in all_periods:
                            scheduled_lesson[(c, t, s, r, d, p)] = model.NewBoolVar(f'scheduled_{c}_{t}_{s}_{r}_{d}_{p}')

    # --- Hard Constraints ---

    # 1. Each class has at most one lesson at a time
    for c in all_classes:
        for d in all_days:
            for p in all_periods:
                model.AddAtMostOne(scheduled_lesson[(c, t, s, r, d, p)] 
                                  for t in all_teachers for s in all_subjects for r in all_rooms)

    # 2. Each teacher teaches at most one class at a time
    for t in all_teachers:
        for d in all_days:
            for p in all_periods:
                model.AddAtMostOne(scheduled_lesson[(c, t, s, r, d, p)] 
                                  for c in all_classes for s in all_subjects for r in all_rooms)

    # 3. Each room hosts at most one lesson at a time
    for r in all_rooms:
        for d in all_days:
            for p in all_periods:
                model.AddAtMostOne(scheduled_lesson[(c, t, s, r, d, p)] 
                                  for c in all_classes for t in all_teachers for s in all_subjects)

    # 4. Assign the correct number of lessons per subject per week for each class
    for (c, s), num_lessons in data['lessons'].items():
        model.Add(sum(scheduled_lesson[(c, t, s, r, d, p)] 
                     for t in all_teachers for r in all_rooms for d in all_days for p in all_periods) == num_lessons)

    # 5. Respect teacher availability
    for (t, d, p), available in data['teacher_availability'].items():
        if not available:  # teacher is not available
            for c in all_classes:
                for s in all_subjects:
                    for r in all_rooms:
                        model.Add(scheduled_lesson[(c, t, s, r, d, p)] == 0)

    # 6. Subject-room compatibility (labs for lab subjects)
    for s in all_subjects:
        subject_id = s + 1  # Convert back to 1-based for lookup
        needs_lab = data['subject_needs_lab'].get(subject_id, False)
        for r in all_rooms:
            room_id = r + 1  # Convert back to 1-based for lookup
            is_lab = data['room_is_lab'].get(room_id, False)
            
            # If subject needs lab but room is not lab, or vice versa
            if needs_lab != is_lab:
                for c in all_classes:
                    for t in all_teachers:
                        for d in all_days:
                            for p in all_periods:
                                model.Add(scheduled_lesson[(c, t, s, r, d, p)] == 0)

    # --- Soft Constraints (Objective Function) ---
    # Maximize teacher preferences
    preference_score = model.NewIntVar(0, 1000, 'preference_score')
    model.Add(preference_score == sum(
        data['teacher_preferences'].get((t, c), 0) * scheduled_lesson[(c, t, s, r, d, p)]
        for c in all_classes for t in all_teachers for s in all_subjects 
        for r in all_rooms for d in all_days for p in all_periods
    ))
    model.Maximize(preference_score)

    # --- Solve ---
    solver = CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    # --- Extract Solution ---
    timetable = []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Solution found in {solver.WallTime()} seconds')
        for d in all_days:
            for p in all_periods:
                for c in all_classes:
                    for t in all_teachers:
                        for s in all_subjects:
                            for r in all_rooms:
                                if solver.Value(scheduled_lesson[(c, t, s, r, d, p)]):
                                    timetable.append({
                                        "day": d,
                                        "period": p,
                                        "class": classes[c],
                                        "teacher": teachers[t],
                                        "subject": subjects[s],
                                        "room": rooms[r]
                                    })
        
        # Save solution to database
        save_solution_to_database(timetable, data, db_file)
        return timetable
    else:
        print('No solution found.')
        return None

if __name__ == '__main__':
    # Test the solver with database data
    print("Testing school scheduling solver...")
    solution = solve_school_scheduling_from_db()
    if solution:
        # Sort for readability
        solution.sort(key=lambda x: (x['day'], x['period'], x['class']))
        for item in solution:
            print(f"Day {item['day']}, Period {item['period']}: Class {item['class']} has {item['subject']} with {item['teacher']} in {item['room']}")
    else:
        print("No solution found. Check constraints and data.")
