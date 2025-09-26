---
noteId: "87b65c309b1111f0b7744fd593916b62"
tags: []
---

# School Timetable Generator

A comprehensive school timetable scheduling application built with Python, featuring automated schedule generation, manual editing capabilities, and export functionality.

## Features

### Core Functionality

- **Automated Schedule Generation**: Uses constraint satisfaction algorithms to generate optimal timetables
- **Manual Editing**: Click-to-edit interface with conflict detection
- **Database Storage**: SQLite database for persistent data storage
- **Multiple Views**: View schedules by class or teacher
- **Export Options**: Export to PDF and Excel formats

### Data Management

- **Teacher Management**: Add/edit teachers with availability constraints
- **Class Management**: Manage classes and grade levels
- **Subject Management**: Define subjects and lab requirements
- **Room Management**: Configure rooms and lab designations
- **Lesson Requirements**: Set weekly lesson counts per subject per class

### Scheduling Features

- **Hard Constraints**:
  - No teacher/class/room double-booking
  - Teacher availability restrictions
  - Lab requirements for science subjects
  - Exact lesson count requirements
- **Soft Constraints**:
  - Teacher preferences for classes
  - Optimized scheduling distribution

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages (install via pip):

```bash
pip install -r requirements.txt
```

### Optional Dependencies

- **OR-Tools**: For advanced constraint satisfaction (recommended)
- **reportlab**: For PDF export
- **openpyxl**: For Excel export

If OR-Tools is not available, the system will fall back to a simple greedy algorithm.

## Usage

### Starting the Application

```bash
python app_gui.py
```

### First Time Setup

1. The application will automatically create a sample database with test data
2. Use the "Data" menu to modify teachers, classes, subjects, and rooms
3. Set lesson requirements through the data management interface

### Generating Schedules

1. Click "Generate Schedule" to create an automatic timetable
2. Use the radio buttons to switch between Class and Teacher views
3. Select specific items from the dropdown to view individual schedules

### Manual Editing

1. Click on any time slot in the timetable
2. Use the edit dialog to:
   - Remove lessons
   - Move lessons to different time slots
   - System automatically checks for conflicts

### Exporting

- **PDF Export**: Export current view to a formatted PDF
- **Excel Export**: Export all class schedules to a multi-sheet Excel file

## File Structure

```
school_scheduler/
├── app_gui.py              # Main GUI application
├── database_setup.py       # Database schema and initialization
├── solver.py              # OR-Tools constraint solver
├── solver_simple.py       # Fallback greedy algorithm solver
├── export.py              # PDF export functionality
├── requirements.txt       # Python dependencies
├── PROJECT_DOC.md         # Original project documentation
└── README.md             # This file
```

## Database Schema

### Tables

- **teachers**: Teacher information and availability
- **classes**: Class definitions and grade levels
- **subjects**: Subject information and lab requirements
- **rooms**: Room information and lab designation
- **lessons**: Weekly lesson requirements per class/subject
- **teacher_preferences**: Teacher preferences for classes (1-5 scale)
- **schedules**: Generated timetable data

### Time Structure

- **Days**: Monday (0) through Friday (4)
- **Periods**: 6 periods per day (0-5)
- **Times**: 09:00-15:00 with 1-hour slots

## Scheduling Algorithm

### OR-Tools Solver (Primary)

Uses Google's OR-Tools constraint satisfaction library to find optimal solutions considering:

- All hard constraints
- Teacher preferences optimization
- Efficient time slot utilization

### Simple Greedy Algorithm (Fallback)

When OR-Tools is unavailable, uses a randomized greedy approach:

- Processes lessons in random order
- Finds first available slot meeting all constraints
- Reports any unscheduled lessons

## Customization

### Adding New Constraints

Modify the solver files to add new scheduling rules:

- Teacher workload limits
- Consecutive lesson restrictions
- Subject distribution requirements

### UI Customization

The GUI uses tkinter with ttk styling:

- Modify styles in `app_gui.py` `__init__` method
- Add new data management screens using the existing patterns
- Extend export functionality in respective functions

## Troubleshooting

### Common Issues

1. **OR-Tools Import Error**

   - Install OR-Tools: `pip install ortools`
   - System will use simple solver as fallback

2. **Database Errors**

   - Delete `school_timetable.db` to reset
   - Run `python database_setup.py` to recreate

3. **Export Errors**

   - Install required packages: `pip install reportlab openpyxl`
   - Check file permissions in working directory

4. **Scheduling Failures**
   - Reduce lesson requirements
   - Add more teachers or rooms
   - Check teacher availability settings

### Performance Notes

- OR-Tools solver: 30-second time limit (configurable)
- Recommended: <50 teachers, <30 classes for optimal performance
- Large datasets may require constraint relaxation

## Development

### Project Status

This implementation covers all features from the original PROJECT_DOC.md:

- ✅ Core Logic & Database (Phase 1)
- ✅ User Interface Development (Phase 2)
- ✅ Integration & Features (Phase 3)
- ✅ Basic Testing (Phase 4)

### Future Enhancements

- Web-based interface
- Multi-user support with authentication
- Advanced reporting and analytics
- Automated conflict resolution suggestions
- Mobile-responsive design

## License

This project is provided as-is for educational and institutional use.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the PROJECT_DOC.md for detailed requirements
3. Examine the database schema and sample data
4. Test with minimal data sets first

---

**Note**: This application is designed for medium-sized schools. Large institutions may require additional optimization and constraint tuning.
