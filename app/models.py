from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Define an association table for the many-to-many relationship between Tutor and Centre.
tutor_centres = db.Table('tutor_centres',
    db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id'), primary_key=True),
    db.Column('centre_id', db.Integer, db.ForeignKey('centre.id'), primary_key=True)
)

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # A tutor may work at multiple centres.
    centres = db.relationship('Centre', secondary=tutor_centres,
                              backref=db.backref('tutors', lazy=True))
    
    def __repr__(self):
        return f'<Tutor {self.name}>'

class Centre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    # Each centre has many rooms.
    rooms = db.relationship('Room', backref='centre', lazy=True)
    
    def __repr__(self):
        return f'<Centre {self.name}>'

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    # Each room is linked to a Centre.
    centre_id = db.Column(db.Integer, db.ForeignKey('centre.id'), nullable=False)

    def __repr__(self):
        return f'<Room {self.name}>'

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    student_number = db.Column(db.Integer, nullable=True)
    student_names = db.Column(db.Text, nullable=True)
    
    tutor = db.relationship('Tutor', backref='sessions')
    room = db.relationship('Room', backref='sessions')

    @property
    def day_of_week(self):
        return self.start_time.strftime('%A')  # e.g., "Monday", "Tuesday"
    
    def __repr__(self):
        return f'<Session {self.id} - Tutor {self.tutor_id}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='default', nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_key = db.Column(db.String(64), unique=True, nullable=False)
    full_name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<SchoolClass {self.name_key}: {self.full_name}>'
