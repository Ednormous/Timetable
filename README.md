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

---

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/scheduling-software.git
   ```
2. **Install Backend Dependencies** (assuming a Node.js/Express app):
   ```bash
   cd scheduling-software/backend
   npm install
   ```
3. **Install Frontend Dependencies** (if using a separate frontend directory):
   ```bash
   cd scheduling-software/frontend
   npm install
   ```
4. **Set up your database**:
   - Create a new MySQL/PostgreSQL database.
   - Import the initial schema (if provided in `scripts` or `migrations` folder) or run migrations.

---

## Configuration

1. **Backend Environment Variables** (for example in a `.env` file):
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=your_db_user
   DB_PASS=your_db_pass
   DB_NAME=your_db_name

   # Email/SMS service credentials
   SENDGRID_API_KEY=your_sendgrid_api_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   ```

2. **Frontend Environment Variables** (e.g., `.env` in React):
   ```env
   REACT_APP_API_URL=http://localhost:3000
   ```

3. Ensure you do **not** commit your `.env` files to version control.

---

## Running the Application

### 1. Running the Backend

From the backend directory:
```bash
npm run start
```
This will:
- Start the server on the specified port (e.g., `http://localhost:3000`).
- Connect to the database.
- Expose REST endpoints for classes, rooms, users, etc.

### 2. Running the Frontend

From the frontend directory:
```bash
npm run serve
```
or if using Create React App:
```bash
npm start
```
Then open `http://localhost:8080` (Vue) or `http://localhost:3000` (React) in your browser to access the frontend.

---

## Notification Scheduling

A **cron job** (or equivalent) runs daily to send email/SMS reminders:

- **Example** (using Node-Cron in Node.js/Express):
  ```js
  const cron = require("node-cron");
  const moment = require("moment");
  const { sendEmail } = require("./notificationService"); // custom function

  cron.schedule("0 18 * * *", async () => {
    // Runs at 6 PM daily
    const tomorrow = moment().add(1, "day").format("YYYY-MM-DD");

    // Example query to find tomorrow's classes
    // Then send an email to each tutor and parent
  });
  ```

- This job:
  1. Identifies classes scheduled for **tomorrow**.
  2. Sends each tutor a reminder email/SMS with class details.
  3. Sends each parent a reminder about their child’s class.

---

## Deployment

### 1. Dockerize (Optional but Recommended)
- Create a `Dockerfile` for your backend:
  ```dockerfile
  FROM node:16
  WORKDIR /app
  COPY package*.json ./
  RUN npm install
  COPY . .
  EXPOSE 3000
  CMD ["npm", "start"]
  ```
- Repeat for the frontend if needed.

### 2. Deploy to Cloud
- **AWS** (EC2, ECS, EKS) or **Azure** or **Heroku**.
- Use a managed database service (AWS RDS, Azure Database, etc.).
- Configure environment variables in the hosting platform.

### 3. Set Up SSL/HTTPS
- Use **Let’s Encrypt** or your provider’s certificates for secure HTTPS traffic.

---

## Future Enhancements

1. **Automated Conflict Detection**  
   - Prevent double-booking of tutors or rooms.
2. **Calendar Integration**  
   - Sync with Google Calendar or iCal for tutors/parents.
3. **Mobile App**  
   - A React Native or Flutter app for easy attendance and notifications on mobile.
4. **Analytics & Reporting**  
   - Track class occupancy, tutor loads, and generate usage statistics.
5. **Role-Based Access Control (RBAC)**  
   - Fine-grained permissions for different roles and sub-roles.
6. **Internationalization (i18n)**  
   - Support for multiple languages in the UI and notifications.

---

## License

This project is licensed under the [MIT License](LICENSE), allowing free and open usage, modification, and distribution.

---

### Questions or Feedback?

Please [open an issue](https://github.com/your-username/scheduling-software/issues) or contact the repository owner for further assistance.
```
