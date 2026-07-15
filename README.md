# EduTrack - Student Management System

A Professional Student Management System with MySQL Database Integration

---

## Overview

EduTrack-SMS is a complete Student Management System built with Python and Tkinter, featuring MySQL database integration. It provides role-based access control for Admin, Teacher, and Student with comprehensive features for managing students, courses, and grades.

### Key Features

- Secure Authentication - SHA-256 password hashing
- Role-Based Access - Admin, Teacher, Student roles
- Student Management - Add, remove, search students
- Course Management - Create and manage courses
- Grade Management - Assign and update grades
- MySQL Database - Reliable data storage
- Modern GUI - Professional Tkinter interface

### Benefits

- Easy to use interface
- Secure data storage
- Role-based security
- Quick student search
- Grade tracking
- Course management
- Teacher assignment

---

## System Architecture

### Architecture Diagram

+-----------------------------------------------------+
|                   EduTrack-SMS                      |
|                                                     |
|  +--------------------------------------------+    |
|  |          Tkinter GUI Interface             |    |
|  |  +----------+  +----------+  +--------+  |    |
|  |  |  Login   |  |Dashboard |  |  Forms |  |    |
|  |  +----------+  +----------+  +--------+  |    |
|  +--------------------------------------------+    |
|                      |                             |
|  +--------------------------------------------+    |
|  |         Business Logic Layer               |    |
|  |  +----------+  +----------+  +--------+  |    |
|  |  | Student  |  |  Course  |  | Grade  |  |    |
|  |  | Manager  |  | Manager  |  |Manager |  |    |
|  |  +----------+  +----------+  +--------+  |    |
|  +--------------------------------------------+    |
|                      |                             |
|  +--------------------------------------------+    |
|  |        Database Access Layer               |    |
|  |  +--------------------------------------+  |    |
|  |  |         PyMySQL Connector           |  |    |
|  |  +--------------------------------------+  |    |
|  +--------------------------------------------+    |
|                      |                             |
|  +--------------------------------------------+    |
|  |          MySQL Database                    |    |
|  |  +----------+  +----------+  +--------+  |    |
|  |  |  users   |  | student  |  |courses |  |    |
|  |  +----------+  +----------+  +--------+  |    |
|  |  +----------+                            |    |
|  |  |enrollments|                            |    |
|  |  +----------+                            |    |
|  +--------------------------------------------+    |
+-----------------------------------------------------+

### Database Schema

users (id, username, password_hash, role, created_at)
student (rollNo, name, fname, created_at)
courses (course_id, course_name, teacher, created_at)
enrollments (enroll_id, rollNo, course_id, grade, created_at)

### Table Relationships

users table
  |
  | (Role-based access control)
  |
student table <---> enrollments table <---> courses table
  |                      |                      |
  |(One-to-Many)         |(Many-to-Many)       |(One-to-Many)
  |                      |                      |
  v                      v                      v
Multiple Students    Student-Course        Multiple Courses
                     Enrollment Pair

### System Workflow

Login Process:
Start -> Enter Credentials -> Validate -> Dashboard -> Role-Based Access

Student Management:
Add Student -> Enter Details -> Validate -> Insert DB -> Success

Course Management:
Add Course -> Enter Details -> Validate -> Insert DB -> Success

Grade Management:
Select Student -> Select Course -> Enter Grade -> Validate -> Update DB

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Language | Python | 3.8+ | Core programming language |
| GUI Framework | Tkinter | Built-in | Graphical user interface |
| Database | MySQL | 8.0+ | Data storage and management |
| Database Driver | PyMySQL | 1.0.2+ | MySQL connector for Python |
| Security | hashlib | Built-in | Password hashing (SHA-256) |
| Platform | Cross-platform | - | Windows, Linux, macOS |

### Development Tools

- IDE: VS Code / PyCharm
- Database Management: MySQL Workbench / phpMyAdmin
- Version Control: Git / GitHub
- Documentation: Markdown
- Testing: Manual Testing

---

## Future Work

### Planned Features

1. Web Interface
   - Convert desktop application to web-based platform
   - Use Flask or Django framework
   - Responsive design for mobile devices

2. Advanced Reporting
   - Generate PDF reports
   - Student progress reports
   - Course completion certificates
   - Grade transcripts

3. Advanced Analytics
   - Student performance analytics
   - Course popularity analysis
   - Grade distribution charts
   - Teacher performance metrics

4. Additional Modules
   - Attendance tracking system
   - Fee management system
   - Exam scheduling module
   - Library management system
   - Hostel management system

5. Enhanced Security
   - Two-factor authentication
   - Password reset functionality
   - Activity logging
   - IP-based access control

6. API Development
   - RESTful API for external integration
   - Mobile app support
   - Third-party integration (payment gateways)
   - Data export/import APIs

7. Notifications System
   - Email notifications
   - SMS alerts
   - In-app notifications
   - Reminder system

8. Data Backup & Recovery
   - Automated database backup
   - Data recovery tools
   - Export/Import functionality
   - Cloud backup integration

9. User Experience Enhancements
   - Dark mode support
   - Multi-language support
   - Keyboard shortcuts
   - Drag-and-drop functionality
   - Advanced search filters

10. Mobile Application
    - Android app development
    - iOS app development
    - Cross-platform mobile app
    - Push notifications

11. Cloud Integration
    - AWS deployment
    - Google Cloud integration
    - Azure deployment
    - Containerization (Docker/Kubernetes)

12. Advanced Features
    - Batch student import (CSV/Excel)
    - Bulk grade updates
    - Automated report generation
    - Student portal
    - Parent portal

### Future Enhancements Roadmap

Phase 1 (Q3 2026):
- Web interface development
- API development
- Basic reporting

Phase 2 (Q4 2026):
- Mobile application
- Advanced analytics
- Notification system

Phase 3 (Q1 2027):
- Cloud deployment
- Advanced features
- Third-party integration

Phase 4 (Q2 2027):
- AI/ML features
- Predictive analytics
- Automated workflows

### Planned Technologies for Future

- Web Framework: Flask / Django
- Frontend: React.js / Vue.js
- Mobile: React Native / Flutter
- Cloud: AWS / Google Cloud
- DevOps: Docker / Kubernetes
- CI/CD: GitHub Actions / Jenkins
- Testing: PyTest / Selenium
- Analytics: Pandas / Matplotlib

---

## Installation Guide

### Prerequisites

Required Software:
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. Clone Repository
git clone https://github.com/tech-rakib/EduTrack-SMS.git
cd EduTrack-SMS

2. Install Dependencies
pip install pymysql

OR

pip install -r requirements.txt

3. Configure Database
Edit config.py file:

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "student_db",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

4. Start MySQL Server
XAMPP: Start MySQL from Control Panel
Linux: sudo systemctl start mysql
Windows: net start MySQL80

5. Run Application
python Student_Management.py

---

## Usage Guide

### Default Login Credentials

+----------+----------+-----------+
| Role     | Username | Password  |
+----------+----------+-----------+
| Admin    | admin    | admin123  |
| Teacher  | teacher  | teacher123|
| Student  | student  | student123|
+----------+----------+-----------+

### Role-Based Access Control

+----------------------+---------+---------+---------+
| Feature              | Admin   | Teacher | Student |
+----------------------+---------+---------+---------+
| Add Student          | Yes     | Yes     | No      |
| Remove Student       | Yes     | Yes     | No      |
| Add Course           | Yes     | No      | No      |
| Assign Courses       | Yes     | No      | No      |
| Update Grades        | Yes     | Yes     | No      |
| View Students        | Yes     | Yes     | Yes     |
| Search Student       | Yes     | Yes     | Yes     |
| View Courses         | Yes     | Yes     | Yes     |
| View Dashboard       | Yes     | Yes     | Yes     |
| Manage Teachers      | Yes     | No      | No      |
+----------------------+---------+---------+---------+

### How to Use

Admin Access:
- Login with admin credentials
- Full access to all features
- Can add/remove students and courses
- Can assign courses to students
- Can update grades
- Can manage teachers

Teacher Access:
- Login with teacher credentials
- Can add/remove students
- Can update grades
- Can view all students and courses
- Cannot add courses or assign courses

Student Access:
- Login with student credentials
- Can view dashboard
- Can search for students
- Can view courses and teachers
- No modification rights

---

## Project Structure

EduTrack-SMS/
+-- Student_Management.py    # Main application
+-- config.py                # Database configuration
+-- db_helper.py             # Database helper functions
+-- requirements.txt         # Python dependencies
+-- README.md               # Documentation
+-- LICENSE                 # MIT License
+-- .gitignore              # Git ignore rules
+-- CONTRIBUTING.md         # Contributing guidelines
+-- docs/                   # Documentation folder
|   +-- installation.md
|   +-- usage.md
|   +-- api.md
+-- tests/                  # Test files
|   +-- test_db.py
|   +-- test_app.py
+-- .github/                # GitHub configurations
    +-- workflows/
    |   +-- python-app.yml  # CI/CD Pipeline
    +-- ISSUE_TEMPLATE/
        +-- bug_report.md
        +-- feature_request.md

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
git checkout -b feature/AmazingFeature

3. Commit your changes
git commit -m 'Add some AmazingFeature'

4. Push to the branch
git push origin feature/AmazingFeature

5. Open a Pull Request

### Coding Guidelines

- Follow PEP 8 style guide
- Write clear comments and docstrings
- Test your changes thoroughly
- Update documentation accordingly
- Use meaningful variable names

---

## License

This project is licensed under the MIT License.

MIT License
Copyright (c) 2026 tech-rakib

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...

---

## Contact

GitHub: tech-rakib
Email: techrakib@email.com
Issues: https://github.com/tech-rakib/EduTrack-SMS/issues

---

## Acknowledgments

- Built with Python and Tkinter
- Powered by MySQL database
- Thanks to all contributors and users

---

If you find this project useful, please give it a star on GitHub!

Made with love by tech-rakib
