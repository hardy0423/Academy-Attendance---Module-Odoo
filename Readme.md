```markdown
# Academy Manager

Academy Manager is a comprehensive Odoo 19 module designed to manage courses, students, and attendance records. The module provides tree, form, kanban, and calendar views for efficient administration of educational activities.

## Features

- **Courses Management**

  - Create and track courses with code, name, teacher, dates, duration, and student count.
  - Course states: Draft, Confirmed, In Progress, Completed, Cancelled.
  - Kanban and calendar views for easy overview.

- **Students Management**

  - Add and manage student records with personal details, enrollment date, and attendance rate.
  - Automatically computed full name and attendance statistics.
  - Active/inactive student status.

- **Attendance Management**

  - Record attendance per course and per student.
  - Track attended and missed sessions.
  - Calendar view to visualize attendance easily.

- **Demo Data**
  - Includes demo students and sample courses for testing.

## Module Structure
```

academy_manager/
├── **manifest**.py
├── **init**.py
├── models/
│ ├── **init**.py
│ ├── course.py
│ ├── student.py
│ └── attendance.py
├── views/
│ ├── course_views.xml
│ ├── student_views.xml
│ ├── attendance_views.xml
│ ├── menu_views.xml
│ └── templates.xml
├── security/
│ └── ir.model.access.csv
├── data/
│ └── demo.xml
└── controllers/
└── main.py

```

## Installation

1. Place the `academy_manager` folder in your Odoo `addons` directory.
2. Update the app list from the Odoo Apps menu.
3. Install the `Academy Manager` module.
4. Optionally, load demo data for testing purposes.

## Usage

- Navigate to **Academy → Courses** to create and manage courses.
- Navigate to **Academy → Students** to manage student profiles.
- Navigate to **Academy → Attendance** to record and view attendance data.
```
