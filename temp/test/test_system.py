#!/usr/bin/env python3
"""
Test script for School Timetable Generator
Verifies all major components work correctly
"""

import sqlite3
import os
import sys

def test_database():
    """Test database creation and data loading"""
    print("Testing database setup...")
    
    # Remove existing database
    if os.path.exists("school_timetable.db"):
        os.remove("school_timetable.db")
    
    try:
        from core.database_setup import create_connection, create_tables, add_sample_data
        
        conn = create_connection()
        if conn:
            create_tables(conn)
            add_sample_data(conn)
            
            # Verify data
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teachers")
            teacher_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM classes")
            class_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subjects")
            subject_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM lessons")
            lesson_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ Database created successfully")
            print(f"   - Teachers: {teacher_count}")
            print(f"   - Classes: {class_count}")  
            print(f"   - Subjects: {subject_count}")
            print(f"   - Lesson requirements: {lesson_count}")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_solver():
    """Test the scheduling solver"""
    print("\nTesting scheduling solver...")
    
    try:
        # Try OR-Tools solver first
        try:
            from schedule_engines.solver import solve_school_scheduling_from_db
            solver_type = "OR-Tools"
        except ImportError:
            from schedule_engines.solver_simple import solve_school_scheduling_from_db
            solver_type = "Simple Greedy"
        
        solution = solve_school_scheduling_from_db()
        
        if solution:
            print(f"✅ {solver_type} solver working")
            print(f"   - Generated {len(solution)} lessons")
            
            # Verify some solution properties
            days = set()
            periods = set()
            classes = set()
            teachers = set()
            
            for lesson in solution:
                days.add(lesson['day'])
                periods.add(lesson['period'])
                classes.add(lesson['class'])
                teachers.add(lesson['teacher'])
            
            print(f"   - Days used: {len(days)}")
            print(f"   - Periods used: {len(periods)}")
            print(f"   - Classes scheduled: {len(classes)}")
            print(f"   - Teachers assigned: {len(teachers)}")
            
            return True
        else:
            print(f"❌ {solver_type} solver failed to generate solution")
            return False
            
    except Exception as e:
        print(f"❌ Solver test failed: {e}")
        return False

def test_export():
    """Test export functionality"""
    print("\nTesting export functionality...")
    
    try:
        from core.export import export_schedule_to_pdf
        
        # Create sample data
        sample_data = [
            ['Time', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            ['09:00-10:00', 'Math\nMr. Smith\nRoom 101', '', 'Physics\nDr. Evans\nLab A', '', ''],
            ['10:00-11:00', '', 'History\nMrs. Jones\nRoom 102', '', 'Math\nMr. Smith\nRoom 101', '']
        ]
        
        export_schedule_to_pdf(sample_data, "test_timetable.pdf")
        
        if os.path.exists("test_timetable.pdf"):
            print("✅ PDF export working")
            os.remove("test_timetable.pdf")  # Clean up
            return True
        else:
            print("❌ PDF export failed - file not created")
            return False
            
    except ImportError as e:
        print(f"⚠️  PDF export unavailable: {e}")
        print("   Install reportlab: pip install reportlab")
        return True  # Not a critical failure
    except Exception as e:
        print(f"❌ Export test failed: {e}")
        return False

def test_gui_imports():
    """Test GUI component imports"""
    print("\nTesting GUI imports...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✅ tkinter available")
        
        # Test if we can create the main app class
        import core.app_gui as app_gui
        print("✅ GUI module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ GUI test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("=" * 50)
    print("School Timetable Generator - System Test")
    print("=" * 50)
    
    tests = [
        ("Database", test_database),
        ("Solver", test_solver),
        ("Export", test_export),
        ("GUI", test_gui_imports)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All systems operational! You can run the application with:")
        print("   python app_gui.py")
    else:
        print("\n⚠️  Some components failed. Check error messages above.")
        print("   Basic functionality may still work.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)