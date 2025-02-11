# Timetable Project

This is a Flask-based timetabling system for a tutoring company. It features:
- Tutor and admin dashboards
- Database models for Tutors, Rooms, and Sessions
- Blueprint-based project structure

## Setup

1. Create a virtual environment:
   \`\`\`bash
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`

2. Install dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Initialize the database (with Flask-Migrate):
   \`\`\`bash
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   \`\`\`

4. Run the application:
   \`\`\`bash
   python app.py
   \`\`\`

Happy coding!
