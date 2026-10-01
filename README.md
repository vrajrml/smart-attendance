# SmartAttend

SmartAttend is a smart attendance management system built using Python, Flask, MySQL, and OpenCV-based face recognition.

The system provides a centralized platform for managing students, subjects, class sessions, attendance records, face registration, attendance verification, and attendance reports.

---

## Features

### Authentication

- Secure user login
- Password hashing
- Role-based user structure
- Protected application routes
- Session-based authentication using Flask-Login

### Student Management

- Add students
- View student records
- Edit student information
- Delete students
- Store:
  - Roll number
  - Name
  - Email
  - Phone
  - Department
  - Semester

### Face Recognition

- Register a student's face
- Verify a registered face
- Detect faces using OpenCV YuNet
- Generate face embeddings using OpenCV SFace
- Compare detected faces with registered face data
- Store face embeddings in MySQL

### Subject Management

- Add subjects
- Edit subjects
- Delete subjects
- Store subject code and subject name

### Class Session Management

- Create class sessions
- Select subject
- Set session date
- Set start and end times
- Prevent invalid session timings
- Track session status automatically

Session states:

- Upcoming
- Ongoing
- Ended

### Attendance Management

- Face-based attendance scanning
- Manual attendance management
- Present status
- Late status
- Absent status
- Duplicate attendance prevention
- Attendance history
- Session-based attendance records

### Attendance Finalization

Attendance sessions can be finalized after the class ends.

When a session is finalized:

- Students without attendance records are automatically marked absent
- The session becomes read-only
- Attendance can no longer be modified
- Finalization time is recorded
- Reports include the session in attendance calculations

### Reports

Reports support date-range filtering and provide:

- Total students
- Finalized sessions
- Pending sessions
- Overall attendance percentage
- Student-wise attendance
- Subject-wise attendance
- Present/late records
- Absent records
- Attendance charts

### Export

Reports can be exported as:

- Excel
- PDF

---

## Technology Stack

| Technology       | Purpose                          |
| ---------------- | -------------------------------- |
| Python           | Application programming language |
| Flask            | Web application framework        |
| Flask-Login      | Authentication                   |
| Flask-WTF        | Forms and CSRF protection        |
| Flask-SQLAlchemy | Database ORM                     |
| MySQL            | Relational database              |
| PyMySQL          | MySQL database driver            |
| OpenCV           | Face detection and recognition   |
| YuNet            | Face detection                   |
| SFace            | Face recognition                 |
| NumPy            | Numerical processing             |
| Pandas           | Report data processing           |
| OpenPyXL         | Excel report generation          |
| ReportLab        | PDF report generation            |
| HTML/CSS         | User interface                   |
| Bootstrap        | UI components                    |
| Chart.js         | Attendance charts                |

---

## System Architecture

````text
                    ┌─────────────────────┐
                    │      Browser        │
                    │   HTML / Bootstrap  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Flask App      │
                    │                     │
                    │  Routes / Forms     │
                    │  Authentication     │
                    │  Business Logic     │
                    └───────┬─────┬───────┘
                            │     │
                ┌───────────┘     └────────────┐
                ▼                              ▼
      ┌──────────────────┐           ┌──────────────────┐
      │     MySQL        │           │   Face Service   │
      │                  │           │                  │
      │ Students         │           │ YuNet            │
      │ Subjects         │           │ SFace            │
      │ Sessions         │           │ OpenCV           │
      │ Attendance       │           └──────────────────┘
      │ Face Encodings   │
      └──────────────────┘


smart-attendance/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── forms/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── student.py
│   │   ├── subject.py
│   │   └── class_session.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── student.py
│   │   ├── subject.py
│   │   ├── class_session.py
│   │   ├── face_encoding.py
│   │   └── attendance.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── students.py
│   │   ├── subjects.py
│   │   ├── class_sessions.py
│   │   ├── attendance.py
│   │   └── reports.py
│   │
│   ├── services/
│   │   └── face_recognition.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── students/
│   │   ├── subjects/
│   │   ├── class_sessions/
│   │   ├── attendance/
│   │   └── reports/
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── database/
│   └── schema.sql
│
├── face_data/
│
├── models/
│   ├── face_detection_yunet_2023mar.onnx
│   └── face_recognition_sface_2021dec.onnx
│
├── reports/
│
├── scripts/
│   ├── __init__.py
│   └── create_admin.py
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── run.py

Requirements

Before installing SmartAttend, make sure the following are available:

Windows 11 or Linux
WSL2 with Ubuntu (recommended for the development environment)
Python 3.12+
MySQL 8+
Git
A modern web browser

Installation
1. Clone the repository
    git clone <repository-url>
    cd smart-attendance

2. Create a virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

3. Install dependencies
    pip install -r requirements.txt

 4. Start MySQL

    On Ubuntu/WSL:

    sudo service mysql start

    Verify MySQL:

    sudo service mysql status

4. Start MySQL

On Ubuntu/WSL:

sudo service mysql start

Verify MySQL:

sudo service mysql status
Database Setup

The database schema is available at:

database/schema.sql

The schema creates:

users
students
subjects
class_sessions
face_encodings
attendance

To create the database from the schema:

sudo mysql < database/schema.sql

The application expects the database:

smart_attendance
Environment Configuration

Create a .env file in the project root.

Example:

SECRET_KEY=your-secret-key

DATABASE_URL=mysql+pymysql://username:password@localhost/smart_attendance

Do not commit .env to Git.

Creating the Admin User

The project includes an admin creation utility:

python scripts/create_admin.py

Follow the prompts to create the initial application user.

Running the Application

Activate the virtual environment:

source .venv/bin/activate

Start MySQL:

sudo service mysql start

Start SmartAttend:

python run.py

Open the application:

http://127.0.0.1:5000
Application Workflow

The normal SmartAttend workflow is:

Login
   │
   ▼
Dashboard
   │
   ├── Manage Students
   │      │
   │      └── Register Face
   │
   ├── Manage Subjects
   │
   └── Manage Class Sessions
              │
              ▼
        Start Attendance
              │
              ▼
        Face Recognition
              │
              ▼
       Attendance Recorded
              │
              ▼
       Manage Attendance
              │
              ▼
       Finalize Attendance
              │
              ▼
            Reports
           /       \
          ▼         ▼
       Excel       PDF
Face Recognition Workflow

SmartAttend uses OpenCV's YuNet and SFace models.

Face Detection

YuNet detects faces from the camera image.

Camera Frame
     │
     ▼
YuNet Face Detector
     │
     ▼
Detected Face
Face Recognition

The detected face is aligned and converted into a numerical feature representation using SFace.

Detected Face
     │
     ▼
Face Alignment
     │
     ▼
SFace Feature Extraction
     │
     ▼
Face Embedding
     │
     ▼
Compare With Registered Embedding
     │
     ▼
Student Identified

The registered face embedding is stored in the face_encodings table.

Attendance Finalization

Attendance is handled using class-session states.

Upcoming

The session has not started yet.

Attendance cannot be marked.

Ongoing

The class is currently running.

Face scanning and attendance management are available.

Ended

The scheduled class has finished.

Attendance can be reviewed and finalized.

Finalized

The attendance session has been completed.

All students without an attendance record are automatically marked absent.

The session becomes read-only.

Attendance Calculation

Only finalized sessions are included in attendance reports.

The overall attendance percentage is calculated from:

Present + Late
--------------------------- × 100
Total Possible Attendance

Where:

Total Possible Attendance
=
Number of Students × Finalized Sessions

Pending sessions are excluded from attendance calculations.

Reports

The Reports section supports a selectable date range.

It provides:

Overall Statistics
Total Students
Finalized Sessions
Pending Sessions
Overall Attendance
Student Reports
Student name
Roll number
Department
Classes attended
Classes absent
Classes conducted
Attendance percentage
Subject Reports
Subject code
Subject name
Classes conducted
Attendance records
Absent records
Attendance percentage
Visual Reports
Overall attendance doughnut chart
Subject-wise attendance chart
Student-wise attendance chart
Exporting Reports

SmartAttend supports two report formats.

Excel

Generated using OpenPyXL.

The Excel report contains:

Summary
Student-wise attendance
Subject-wise attendance
PDF

Generated using ReportLab.

The PDF report contains:

Report date range
Summary statistics
Student attendance
Subject attendance
Health Check

SmartAttend provides a health endpoint:

http://127.0.0.1:5000/health

A healthy application returns information similar to:

{
    "status": "ok",
    "application": "SmartAttend",
    "database": "connected"
}
Security

The application includes:

Password hashing
Login protection
CSRF protection
Environment-based configuration
Protected application routes
Database constraints
Unique attendance records
Session finalization controls

Sensitive configuration should be stored in .env and must not be committed to Git.

Database Relationships

The main relationships are:

User

Student
   │
   ├──────── FaceEncoding
   │
   └──────── Attendance
                    │
                    ▼
              ClassSession
                    │
                    ▼
                 Subject

A student can have one registered face encoding.

A student can have multiple attendance records.

A subject can have multiple class sessions.

A class session can have multiple attendance records.

Each student can have only one attendance record per class session.

Development

Compile-check the application:

python -m compileall -q app scripts run.py

Start the development server:

python run.py

Check the Git working tree:

git status
Future Enhancements

Possible future improvements include:

Multiple face samples per student
Improved recognition confidence handling
Email notifications
Attendance percentage alerts
Teacher-specific dashboards
Advanced analytics
Mobile-friendly attendance scanning
Cloud deployment
REST API integration
Automated database backups
Multi-classroom support
Project Status

SmartAttend currently provides a complete working attendance-management workflow including:

Student management
Subject management
Class-session management
Face registration
Face verification
Face-based attendance
Manual attendance management
Attendance finalization
Attendance history
Attendance reports
Excel export
PDF export
License

This project was developed as an academic MCA project.


### Step 2 — Save it

In nano:

```text
Ctrl + O
Enter
Ctrl + X
````
