-- ============================================================
-- SmartAttend Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_attendance
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_attendance;


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('admin', 'teacher') NOT NULL DEFAULT 'admin',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- STUDENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS students (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    roll_number VARCHAR(30) NOT NULL UNIQUE,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) UNIQUE,

    phone VARCHAR(20),

    department VARCHAR(100),

    semester TINYINT UNSIGNED,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_students_name (name),

    INDEX idx_students_department (department)
);


-- ============================================================
-- SUBJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS subjects (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    subject_code VARCHAR(30) NOT NULL UNIQUE,

    subject_name VARCHAR(100) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- CLASS SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS class_sessions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    subject_id INT UNSIGNED NOT NULL,

    session_date DATE NOT NULL,

    start_time TIME NOT NULL,

    end_time TIME NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    attendance_finalized BOOLEAN NOT NULL DEFAULT FALSE,

    finalized_at DATETIME NULL,

    CONSTRAINT fk_class_sessions_subject
        FOREIGN KEY (subject_id)
        REFERENCES subjects(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_class_sessions_date (session_date),

    INDEX idx_class_sessions_subject (subject_id)
);


-- ============================================================
-- FACE ENCODINGS
-- ============================================================

CREATE TABLE IF NOT EXISTS face_encodings (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    student_id INT UNSIGNED NOT NULL,

    encoding LONGTEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_face_encodings_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE KEY uq_face_encoding_student (student_id)
);


-- ============================================================
-- ATTENDANCE
-- ============================================================

CREATE TABLE IF NOT EXISTS attendance (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    student_id INT UNSIGNED NOT NULL,

    session_id INT UNSIGNED NOT NULL,

    status ENUM('present', 'late', 'absent') NOT NULL DEFAULT 'present',

    marked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    confidence DECIMAL(5,4),

    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_attendance_session
        FOREIGN KEY (session_id)
        REFERENCES class_sessions(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE KEY uq_student_session (student_id, session_id),

    INDEX idx_attendance_student (student_id),

    INDEX idx_attendance_session (session_id),

    INDEX idx_attendance_date (marked_at)
);

