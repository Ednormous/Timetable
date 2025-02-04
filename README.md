# Scheduling Software

This repository contains the source code and instructions for a scheduling software that manages classes, enforces classroom capacity, and sends daily notifications to tutors and parents. It includes a global timetable, individual tutor schedules, and automated reminder messages.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Data Model](#data-model)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Notification Scheduling](#notification-scheduling)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

This software provides:
- A **global timetable** of classes.
- **Individual tutor schedules** linked to the global timetable.
- **Capacity checks** to ensure classes and rooms do not exceed their limits.
- **Daily notifications** to tutors and parents about upcoming classes.

The system can be used by:
- **Administrators** to create and manage classes, rooms, tutors, and students.
- **Tutors** to view their upcoming classes.
- **Parents** to see their children’s schedules and receive reminders.

---

## Features

1. **User Roles & Permissions**  
   - Admin, Tutor, and Parent roles.
2. **Class Scheduling**  
   - Create, edit, and delete classes.
   - Assign tutors and students.
   - Link classes to a room.
3. **Capacity Enforcement**  
   - Restrict the maximum number of students per class based on room capacity.
4. **Notifications**  
   - Send daily email (or SMS) reminders to tutors and parents for the next day’s classes.
5. **Global Timetable & Individual Schedules**  
   - A global view of all upcoming classes.
   - Personalized view for each tutor or parent.

---

## Architecture

The system is split into three primary components:

1. **Frontend**  
   - A web-based user interface built with a modern JavaScript framework (React, Vue, or Angular).
   - Shows upcoming classes, enrollment forms, and management pages.

2. **Backend**  
   - A server-side application (Node.js/Express, Python/Django, or Ruby on Rails).
   - Exposes REST or GraphQL APIs for scheduling, user management, and notifications.
   - Houses the core logic for capacity checks and enrollment rules.

3. **Database**  
   - A relational database (e.g., MySQL, PostgreSQL) stores user data, classes, rooms, and enrollment info.
   - Includes a scheduled job for sending notifications.

### Typical Flow

1. **User requests** (create a class, enroll a student, etc.) come from the Frontend to the Backend API.
2. **Backend** validates the request, checks capacity, and updates the **Database**.
3. A **Cron/Scheduler** in the backend checks for tomorrow’s classes daily and sends notifications.

---

## Data Model

A simplified relational schema might look like this:

```sql
-- Users table (for tutors, parents, admins)
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  role ENUM('admin', 'tutor', 'parent'),
  phone VARCHAR(20)
);

-- Students table (linked to parents in users)
CREATE TABLE students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  parent_id INT,
  FOREIGN KEY (parent_id) REFERENCES users (id)
);

-- Rooms table
CREATE TABLE rooms (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  capacity INT
);

-- Classes table
CREATE TABLE classes (
  id INT PRIMARY KEY AUTO_INCREMENT,
  tutor_id INT,
  room_id INT,
  date DATE,
  start_time TIME,
  end_time TIME,
  subject VARCHAR(255),
  max_students INT,
  FOREIGN KEY (tutor_id) REFERENCES users (id),
  FOREIGN KEY (room_id) REFERENCES rooms (id)
);

-- Join table for class enrollments
CREATE TABLE class_students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  class_id INT,
  student_id INT,
  FOREIGN KEY (class_id) REFERENCES classes (id),
  FOREIGN KEY (student_id) REFERENCES students (id)
);
