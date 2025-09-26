#!/usr/bin/env python3
"""
School Timetable Generator - Main Entry Point

A comprehensive school timetable generator with multiple scheduling algorithms,
professional GUI interface, and advanced features.

Author: School Scheduler Team
Version: 1.0.0
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main application entry point"""
    try:
        from src.gui.main_window import TimetableApp
        
        print("🎓 School Timetable Generator v1.0.0")
        print("=" * 50)
        print("Starting application...")
        
        app = TimetableApp()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()