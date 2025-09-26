---
noteId: "ecdb6ca09b1f11f0b7744fd593916b62"
tags: []

---

# Project Plan: School Timetable Generator

## 1\. Project Overview

This document outlines the plan for developing a School Timetable Generator application. The goal is to create a robust and efficient tool that automates the scheduling process for a medium-sized school, while allowing for manual adjustments and offering export functionalities.

**Core Technologies:**

- **Backend Logic:** Python with Google's OR-Tools for constraint satisfaction.
- **User Interface:** Python with a modern GUI library like Tkinter (ttkbootstrap) or PyQt.
- **Database:** SQLite for local data storage.
- **Exporting:** Libraries like openpyxl for Excel and reportlab for PDF.

## 2\. Phase 1: Core Logic & Database (Weeks 1-2)

### **Objective:** Develop the foundational backend components

- **Task 2.1: Database Schema Design & Setup**
  - **Description:** Design and implement the SQLite database schema. This will be the single source of truth for all scheduling data.
  - **Tables:**
    - teachers (id, name, availability_json)
    - classes (id, name, grade_level)
    - subjects (id, name, needs_lab)
    - rooms (id, name, is_lab)
    - lessons (class_id, subject_id, lessons_per_week)
    - teacher_preferences (teacher_id, class_id, preference_score)
    - schedules (id, class_id, teacher_id, subject_id, room_id, day, timeslot, is_locked)
  - **Action:** Write a Python script (database_setup.py) to create and initialize the database and tables.
- **Task 2.2: Constraint Satisfaction Model**
  - **Description:** Use Python and OR-Tools to model the timetable problem. This is the heart of the automatic generation feature.
  - **Inputs:** Teacher availability, class lesson requirements, room specifications.
  - **Hard Constraints:**
    - A teacher can only be in one place at a time.
    - A class can only have one lesson at a time.
    - A room can only host one lesson at a time.
    - Assign the exact number of lessons per subject for each class per week.
    - Respect teacher availability.
    - Respect subject-specific room requirements (e.g., labs).
  - **Soft Constraints (Optimization Goals):**
    - Minimize gaps in teacher schedules.
    - Maximize teacher preferences for classes.
    - Ensure fair distribution of lessons for teachers throughout the week.
    - Avoid more than two consecutive lessons of the same subject for a class.
  - **Action:** Create a Python script (solver.py) that takes data as input and uses OR-Tools to find a valid or optimal solution.

## 3\. Phase 2: User Interface Development (Weeks 3-4)

### **Objective:** Build a functional and user-friendly interface

- **Task 3.1: Main Window and Timetable Display**
  - **Description:** Create the main application window that will display the timetable.
  - **Features:**
    - Grid layout (Days vs. Time Slots).
    - Color-coded entries for different subjects or teachers.
    - Buttons/widgets for different views (by class, by teacher, by room).
    - Modern look and feel (e.g., using ttkbootstrap for themed widgets).
  - **Action:** Develop the initial GUI script (app.py) focusing on displaying a static, hard-coded timetable.
- **Task 3.2: Data Management Screens**
  - **Description:** Create UI screens for managing teachers, classes, subjects, and rooms.
  - **Features:**
    - Forms to add, edit, and delete records.
    - UI for setting teacher availability (e.g., a clickable weekly grid).
    - Interface to define how many lessons of each subject a class needs.
  - **Action:** Implement CRUD (Create, Read, Update, Delete) functionalities in app.py, linking the UI to the SQLite database.

## 4\. Phase 3: Integration & Features (Weeks 5-6)

### **Objective:** Connect the UI and the solver, and add key features

- **Task 4.1: End-to-End Integration**
  - **Description:** Connect the UI to the OR-Tools solver.
  - **Workflow:**
    - User clicks a "Generate Timetable" button.
    - The application pulls the latest data from the SQLite database.
    - The data is fed into the solver.py script.
    - The solver runs and returns a solution.
    - The solution is saved to the schedules table in the database.
    - The UI automatically refreshes to display the newly generated timetable.
  - **Action:** Implement the data flow and communication between the GUI and the solver. Add a progress indicator for the solving process.
- **Task 4.2: Drag-and-Drop Editing**
  - **Description:** Allow users to manually modify the generated schedule.
  - **Features:**
    - Click and drag a lesson from one slot to another.
    - On drop, the application must run a conflict check.
    - If there's a hard conflict (e.g., teacher double-booked), the move is disallowed, and the user is notified.
    - If the move is valid, the schedules table is updated.
  - **Action:** Implement drag-and-drop logic within the timetable grid.
- **Task 4.3: Exporting Functionality**
  - **Description:** Implement the feature to export timetables.
  - **Formats:**
    - **Excel:** A separate sheet for each class and teacher.
    - **PDF:** A print-friendly, formatted report of the timetable for a selected class or teacher.
  - **Action:** Write functions to query the schedules table and generate files using openpyxl and reportlab.

## 5\. Phase 4: Testing & Deployment (Week 7)

### **Objective:** Ensure the application is stable and ready for use

- **Task 5.1: Testing and Bug Fixing**
  - **Description:** Thoroughly test all application features with realistic data (~50 teachers, 20 classes).
  - **Areas to Test:**
    - Performance of the solver.
    - Correctness of conflict detection.
    - Data integrity between UI and database.
    - Exported file accuracy.
  - **Action:** Create a test data set and run through all use cases.
- **Task 5.2: Packaging for Deployment**
  - **Description:** Package the Python application into a standalone executable for Windows.
  - **Tool:** Use a tool like PyInstaller or cx_Freeze.
  - **Action:** Create a build script and generate the executable. Test it on a clean Windows machine.

## 6\. Future Enhancements (Post-Launch)

- **Web-based Version:** Develop a web interface using a framework like Flask or Django.
- **Multi-User Support:** Add user roles and permissions for larger schools.
- **Advanced Reporting:** Generate more detailed reports and analytics on teacher workload and room utilization.
- **Automatic Conflict Resolution:** Suggest alternative slots when a manual edit creates a conflict.
