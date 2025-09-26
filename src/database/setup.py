import sqlite3

def create_connection(db_file="school_timetable.db"):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite version: {sqlite3.version}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create tables from the schema """
    sql_create_teachers_table = """
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        availability_json TEXT
    );"""

    sql_create_classes_table = """
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        grade_level INTEGER
    );"""

    sql_create_subjects_table = """
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        needs_lab BOOLEAN NOT NULL DEFAULT 0
    );"""

    sql_create_rooms_table = """
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        is_lab BOOLEAN NOT NULL DEFAULT 0
    );"""

    sql_create_lessons_table = """
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY,
        class_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        lessons_per_week INTEGER NOT NULL,
        FOREIGN KEY (class_id) REFERENCES classes (id),
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    );"""
    
    sql_create_teacher_preferences_table = """
    CREATE TABLE IF NOT EXISTS teacher_preferences (
        id INTEGER PRIMARY KEY,
        teacher_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        preference_score INTEGER NOT NULL DEFAULT 1, -- 1-5 scale
        FOREIGN KEY (teacher_id) REFERENCES teachers (id),
        FOREIGN KEY (class_id) REFERENCES classes (id)
    );
    """

    sql_create_schedule_table = """
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY,
        class_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        day_of_week INTEGER NOT NULL, -- 0=Monday, 1=Tuesday, ...
        timeslot INTEGER NOT NULL,    -- 0=9:00-10:00, 1=10:00-11:00, ...
        is_locked BOOLEAN NOT NULL DEFAULT 0, -- For manual overrides
        FOREIGN KEY (class_id) REFERENCES classes (id),
        FOREIGN KEY (teacher_id) REFERENCES teachers (id),
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    );
    """

    try:
        c = conn.cursor()
        c.execute(sql_create_teachers_table)
        c.execute(sql_create_classes_table)
        c.execute(sql_create_subjects_table)
        c.execute(sql_create_rooms_table)
        c.execute(sql_create_lessons_table)
        c.execute(sql_create_teacher_preferences_table)
        c.execute(sql_create_schedule_table)
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(e)

def add_sample_data(conn):
    """Add comprehensive sample data with 50 teachers, 20 classes, and 7 subjects"""
    cursor = conn.cursor()
    try:
        # Clear existing data to avoid duplicates on re-run
        cursor.execute("DELETE FROM schedules;")
        cursor.execute("DELETE FROM teacher_preferences;")
        cursor.execute("DELETE FROM lessons;")
        cursor.execute("DELETE FROM teachers;")
        cursor.execute("DELETE FROM classes;")
        cursor.execute("DELETE FROM subjects;")
        cursor.execute("DELETE FROM rooms;")

        print("Adding comprehensive data set...")

        # Add 50 Teachers with varied availability
        teacher_names = [
            # Core academic teachers
            'Mr. Anderson', 'Mrs. Baker', 'Dr. Clark', 'Ms. Davis', 'Mr. Evans',
            'Mrs. Foster', 'Dr. Garcia', 'Mr. Harris', 'Ms. Johnson', 'Mrs. Kumar',
            'Mr. Lee', 'Dr. Martinez', 'Ms. Nelson', 'Mr. O\'Brien', 'Mrs. Parker',
            'Dr. Quinn', 'Mr. Roberts', 'Ms. Smith', 'Mrs. Taylor', 'Mr. Wilson',
            'Mrs. Adams', 'Dr. Brown', 'Ms. Chen', 'Mr. Davidson', 'Mrs. Edwards',
            'Mr. Fisher', 'Dr. Green', 'Ms. Hall', 'Mrs. Jackson', 'Mr. King',
            'Ms. Lopez', 'Dr. Miller', 'Mrs. Newman', 'Mr. Owen', 'Ms. Phillips',
            'Dr. Rogers', 'Mrs. Scott', 'Mr. Thompson', 'Ms. Turner', 'Dr. Vaughn',
            'Mr. White', 'Mrs. Young', 'Dr. Zhang', 'Ms. Campbell', 'Mr. Cooper',
            'Mrs. Hughes', 'Dr. Morris', 'Ms. Powell', 'Mr. Reed', 'Mrs. Stewart'
        ]
        
        import random
        import json
        
        for i, name in enumerate(teacher_names):
            # Some teachers have availability restrictions
            availability = {}
            if random.random() < 0.3:  # 30% of teachers have some restrictions
                day = random.randint(0, 4)
                periods = random.sample(range(6), random.randint(1, 2))
                availability[str(day)] = periods
            
            cursor.execute("INSERT INTO teachers (name, availability_json) VALUES (?, ?)", 
                         (name, json.dumps(availability)))

        # Add 20 Classes (4 classes per grade, grades 9-13)
        class_names = []
        for grade in range(9, 14):  # Grades 9, 10, 11, 12, 13
            for section in ['A', 'B', 'C', 'D']:
                class_name = f'Grade {grade}{section}'
                class_names.append(class_name)
                cursor.execute("INSERT INTO classes (name, grade_level) VALUES (?, ?)", 
                             (class_name, grade))

        # Add 7 Subjects per grade level
        subjects_by_grade = {
            9: ['Mathematics', 'English', 'Science', 'History', 'Geography', 'Physical Education', 'Art'],
            10: ['Algebra', 'Literature', 'Biology', 'World History', 'Chemistry', 'Physical Education', 'Music'],
            11: ['Geometry', 'Advanced English', 'Physics', 'Modern History', 'Environmental Science', 'Health', 'Drama'],
            12: ['Calculus', 'Philosophy', 'Advanced Physics', 'Economics', 'Advanced Chemistry', 'Psychology', 'Computer Science'],
            13: ['Statistics', 'Creative Writing', 'Advanced Biology', 'Political Science', 'Organic Chemistry', 'Sociology', 'Engineering']
        }
        
        all_subjects = set()
        for grade_subjects in subjects_by_grade.values():
            all_subjects.update(grade_subjects)
        
        lab_subjects = {'Science', 'Biology', 'Chemistry', 'Physics', 'Advanced Physics', 
                       'Environmental Science', 'Advanced Chemistry', 'Advanced Biology', 
                       'Organic Chemistry', 'Computer Science', 'Engineering'}
        
        for subject in sorted(all_subjects):
            needs_lab = 1 if subject in lab_subjects else 0
            cursor.execute("INSERT INTO subjects (name, needs_lab) VALUES (?, ?)", 
                         (subject, needs_lab))

        # Add Rooms (30 regular rooms + 15 labs)
        for i in range(1, 31):
            cursor.execute("INSERT INTO rooms (name, is_lab) VALUES (?, ?)", 
                         (f'Room {100 + i}', 0))
        
        lab_names = ['Biology Lab', 'Chemistry Lab A', 'Chemistry Lab B', 'Physics Lab A', 
                    'Physics Lab B', 'Computer Lab A', 'Computer Lab B', 'Science Lab A',
                    'Science Lab B', 'Engineering Lab', 'Environmental Lab', 'Research Lab A',
                    'Research Lab B', 'Advanced Lab A', 'Advanced Lab B']
        
        for lab_name in lab_names:
            cursor.execute("INSERT INTO rooms (name, is_lab) VALUES (?, ?)", 
                         (lab_name, 1))

        # Add Lesson Requirements (each class needs lessons for their grade's subjects)
        lesson_counts = {
            'Mathematics': 5, 'Algebra': 5, 'Geometry': 4, 'Calculus': 4, 'Statistics': 3,
            'English': 4, 'Literature': 4, 'Advanced English': 3, 'Philosophy': 2, 'Creative Writing': 2,
            'Science': 4, 'Biology': 4, 'Physics': 4, 'Chemistry': 4, 'Advanced Physics': 3,
            'Advanced Biology': 3, 'Advanced Chemistry': 3, 'Environmental Science': 3, 'Organic Chemistry': 3,
            'History': 3, 'World History': 3, 'Modern History': 3, 'Economics': 3, 'Political Science': 2,
            'Geography': 3, 'Physical Education': 2, 'Health': 2, 'Psychology': 2, 'Sociology': 2,
            'Art': 2, 'Music': 2, 'Drama': 2, 'Computer Science': 3, 'Engineering': 3
        }

        # Get subject IDs
        cursor.execute("SELECT id, name FROM subjects")
        subject_id_map = {name: id for id, name in cursor.fetchall()}
        
        # Get class IDs
        cursor.execute("SELECT id, name, grade_level FROM classes")
        class_data = cursor.fetchall()
        
        for class_id, class_name, grade_level in class_data:
            grade_subjects = subjects_by_grade[grade_level]
            for subject_name in grade_subjects:
                if subject_name in subject_id_map:
                    subject_id = subject_id_map[subject_name]
                    lessons_per_week = lesson_counts.get(subject_name, 3)
                    cursor.execute("INSERT INTO lessons (class_id, subject_id, lessons_per_week) VALUES (?, ?, ?)", 
                                 (class_id, subject_id, lessons_per_week))

        # Add Teacher Preferences (random preferences for realistic data)
        cursor.execute("SELECT id FROM teachers")
        teacher_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM classes")
        class_ids = [row[0] for row in cursor.fetchall()]
        
        # Generate random preferences for about 40% of teacher-class combinations
        for teacher_id in teacher_ids:
            # Each teacher has preferences for 3-8 classes
            preferred_classes = random.sample(class_ids, random.randint(3, 8))
            for class_id in preferred_classes:
                preference_score = random.randint(1, 5)
                cursor.execute("INSERT INTO teacher_preferences (teacher_id, class_id, preference_score) VALUES (?, ?, ?)", 
                             (teacher_id, class_id, preference_score))

        conn.commit()
        print(f"Comprehensive data added successfully:")
        print(f"  - {len(teacher_names)} teachers")
        print(f"  - {len(class_names)} classes")
        print(f"  - {len(all_subjects)} subjects")
        print(f"  - 45 rooms (30 regular, 15 labs)")
        
    except sqlite3.IntegrityError as e:
        print(f"Data integrity error: {e}")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")


if __name__ == '__main__':
    connection = create_connection()
    if connection is not None:
        create_tables(connection)
        add_sample_data(connection)
        connection.close()
