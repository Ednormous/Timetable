# app/admin/routes.py
from functools import wraps
from flask import render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import login_required, current_user
from app.admin import admin
from app.models import Session, Room, Tutor, Centre, SchoolClass, User
from app.extensions import db
import json
from datetime import datetime, timedelta

# Custom decorator to require a specific role
def roles_required(role):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role != role:
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

def generate_time_slots(start="07:00", end="22:00"):
    start_dt = datetime.strptime(start, "%H:%M")
    end_dt = datetime.strptime(end, "%H:%M")
    slots = []
    current = start_dt
    while current < end_dt:
        next_time = current + timedelta(minutes=30)
        slot = f"{current.strftime('%I:%M %p')} - {next_time.strftime('%I:%M %p')}"
        slots.append(slot)
        current = next_time
    return slots

@admin.route('/', methods=['GET'])
@login_required
@roles_required('admin')
def dashboard():
    # Generate half-hour time slots from 7:00 AM to 10:00 PM.
    time_slots = generate_time_slots("07:00", "22:00")
    
    # Define days of the week.
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Get all centres from the database (sorted by name).
    centres = Centre.query.order_by(Centre.name).all()
    
    # Build the timetable grid for each centre and day.
    timetable_by_centre = {}
    for centre in centres:
        timetable_by_day = {}
        rooms = sorted(centre.rooms, key=lambda r: r.name)
        header = ["Time"] + [f"{r.name} ({r.capacity})" for r in rooms]
        for day in days:
            grid = [header.copy()]
            for slot in time_slots:
                row = [slot] + ["" for _ in rooms]
                grid.append(row)
            timetable_by_day[day] = grid
        timetable_by_centre[centre.name] = timetable_by_day

    # Merge in existing session data from the database.
    for centre in centres:
        centre_name = centre.name
        rooms = sorted(centre.rooms, key=lambda r: r.name)
        for day in days:
            grid = timetable_by_centre[centre_name][day]
            sessions = Session.query.join(Room).filter(Room.centre_id == centre.id).all()
            sessions = [s for s in sessions if s.day_of_week == day]
            for s in sessions:
                slot_str = f"{s.start_time.strftime('%I:%M %p')} - {s.end_time.strftime('%I:%M %p')}"
                for i in range(1, len(grid)):  # Skip header row.
                    if grid[i][0] == slot_str:
                        room_index = None
                        for idx, r in enumerate(rooms):
                            if r.id == s.room_id:
                                room_index = idx + 1
                                break
                        if room_index is not None and grid[i][room_index] == "":
                            details = f"{s.tutor.email if s.tutor else 'N/A'}, " \
                                      f"{s.student_number if s.student_number is not None else 'N/A'}, " \
                                      f"{s.student_names if s.student_names else ''}"
                            grid[i][room_index] = details
                        break

    tutors = Tutor.query.order_by(Tutor.name).all()
    
    # Import and query the SchoolClass table to pass classes to the template.
    classes = SchoolClass.query.order_by(SchoolClass.name_key).all()
    
    return render_template('admin.html', 
                           timetable_by_centre=json.dumps(timetable_by_centre),
                           centres=[centre.name for centre in centres],
                           days=days,
                           tutors=tutors,
                           classes=classes)


@admin.route('/add_room', methods=['POST'])
@login_required
@roles_required('admin')
def add_room():
    room_name = request.form.get('room_name')
    capacity = request.form.get('capacity')
    if room_name and capacity:
        try:
            capacity_int = int(capacity)
        except ValueError:
            flash("Capacity must be a number.", "danger")
            return redirect(url_for('admin.dashboard'))
        new_room = Room(name=room_name, capacity=capacity_int)
        db.session.add(new_room)
        db.session.commit()
        flash("Room added successfully.", "success")
    else:
        flash("Please provide both room name and capacity.", "danger")
    return redirect(url_for('admin.dashboard'))

@admin.route('/add_session', methods=['POST'])
@login_required
@roles_required('admin')
def add_session():
    tutor_id = request.form.get('tutor_id')
    room_id = request.form.get('room_id')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    try:
        tutor_id = int(tutor_id)
        room_id = int(room_id)
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except ValueError:
        flash("Invalid input. Please ensure all fields are filled correctly.", "danger")
        return redirect(url_for('admin.dashboard'))
    new_session = Session(tutor_id=tutor_id, room_id=room_id, start_time=start_dt, end_time=end_dt)
    db.session.add(new_session)
    db.session.commit()
    flash("Session added successfully.", "success")
    return redirect(url_for('admin.dashboard'))

@admin.route('/save_timetable', methods=['POST'])
@login_required
@roles_required('admin')
def save_timetable():
    from flask import jsonify
    data = request.get_json()
    centre_name = data.get('centre')
    day = data.get('day')
    grid = data.get('data')
    
    # Helper: Compute start and end datetime for a given slot.
    def get_datetimes_for_slot(day, slot):
        today = datetime.today().date()
        days_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
                    "Friday": 4, "Saturday": 5, "Sunday": 6}
        target_weekday = days_map.get(day, 0)
        diff = target_weekday - today.weekday()
        target_date = today + timedelta(days=diff)
        start_str, end_str = slot.split(" - ")
        start_dt = datetime.strptime(f"{target_date} {start_str}", "%Y-%m-%d %I:%M %p")
        end_dt = datetime.strptime(f"{target_date} {end_str}", "%Y-%m-%d %I:%M %p")
        return start_dt, end_dt

    # Helper: Parse a cell value that is expected to be in CSV format:
    # "tutor_id, student_count, student_names"
    def parse_cell(cell_text):
        parts = [p.strip() for p in cell_text.split(',')]
        if len(parts) < 3:
            return None
        try:
            tutor_id = int(parts[0])
        except ValueError:
            return None
        try:
            student_num = int(parts[1])
        except ValueError:
            student_num = None
        student_names = ", ".join(parts[2:]) if len(parts) > 2 else ""
        return tutor_id, student_num, student_names

    try:
        # Find the centre.
        centre_obj = Centre.query.filter_by(name=centre_name).first()
        if not centre_obj:
            return jsonify({'status': 'error', 'message': 'Centre not found'}), 400
        
        # Delete existing sessions for this centre and day.
        sessions_to_delete = [s for s in Session.query.join(Room).filter(Room.centre_id == centre_obj.id).all() if s.day_of_week == day]
        for s in sessions_to_delete:
            db.session.delete(s)
        db.session.commit()
        
        # Get the sorted list of rooms for the centre (in the same order as used when rendering the timetable).
        rooms = sorted(centre_obj.rooms, key=lambda r: r.name)
        
        # Iterate over each row (skip the header row).
        for row in grid[1:]:
            slot = row[0]
            try:
                start_dt, end_dt = get_datetimes_for_slot(day, slot)
            except Exception as e:
                continue
            # For each cell in the row (columns 1 onward) – the column index corresponds to the room.
            for idx, cell_value in enumerate(row[1:], start=1):
                if cell_value.strip():
                    parsed = parse_cell(cell_value)
                    if not parsed:
                        continue
                    tutor_id, student_num, student_names = parsed
                    tutor_obj = Tutor.query.get(tutor_id)
                    if not tutor_obj:
                        flash(f"Tutor with id {tutor_id} not found; skipping.", "warning")
                        continue
                    # Map column idx (starting at 1) to a room from the sorted list.
                    room_id = None
                    if idx-1 < len(rooms):
                        room_id = rooms[idx-1].id
                    new_session = Session(
                        tutor_id=tutor_obj.id,
                        room_id=room_id,
                        start_time=start_dt,
                        end_time=end_dt,
                        student_number=student_num,
                        student_names=student_names
                    )
                    db.session.add(new_session)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@admin.route('/classes', methods=['GET'])
@login_required
@roles_required('admin')
def view_classes():
    classes = SchoolClass.query.order_by(SchoolClass.name_key).all()
    return render_template('admin_classes.html', classes=classes)

@admin.route('/classes/add', methods=['POST'])
@login_required
@roles_required('admin')
def add_class():
    name_key = request.form.get('name_key').strip()
    full_name = request.form.get('full_name').strip()
    if not name_key or not full_name:
        flash("Please provide both a class key and a full name.", "danger")
        return redirect(url_for('admin.view_classes'))
    existing = SchoolClass.query.filter_by(name_key=name_key).first()
    if existing:
        flash("A class with that key already exists.", "warning")
        return redirect(url_for('admin.view_classes'))
    new_class = SchoolClass(name_key=name_key, full_name=full_name)
    db.session.add(new_class)
    db.session.commit()
    flash("New class added successfully.", "success")
    return redirect(url_for('admin.view_classes'))

@admin.route('/manage_rooms', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def manage_rooms():
    from app.models import Centre
    if request.method == 'POST':
        centre_id = request.form.get('centre_id')
        if not centre_id:
            flash("No centre selected.", "danger")
            return redirect(url_for('admin.manage_rooms'))
        centre_obj = Centre.query.get(centre_id)
        if not centre_obj:
            flash("Centre not found.", "danger")
            return redirect(url_for('admin.manage_rooms'))
        
        update_occurred = False
        for room in centre_obj.rooms:
            new_capacity_str = request.form.get(f'capacity_{room.id}')
            if new_capacity_str:
                try:
                    new_capacity = int(new_capacity_str)
                except ValueError:
                    flash(f"Invalid capacity value for room {room.name}.", "danger")
                    continue
                if room.sessions:
                    flash(f"Room {room.name} already has sessions assigned. Changing capacity may affect scheduled classes.", "warning")
                if room.capacity != new_capacity:
                    room.capacity = new_capacity
                    update_occurred = True
        if update_occurred:
            try:
                db.session.commit()
                flash("Room capacities updated successfully.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error updating capacities: {str(e)}", "danger")
        else:
            flash("No changes were made.", "info")
        return redirect(url_for('admin.manage_rooms'))
    else:
        from app.models import Centre
        centres = Centre.query.order_by(Centre.name).all()
        return render_template('admin_rooms.html', centres=centres)

@admin.route('/manage_centres', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def manage_centres():
    from app.models import Centre
    if request.method == 'POST':
        centre_name = request.form.get('centre_name')
        if not centre_name or centre_name.strip() == "":
            flash("Centre name cannot be empty.", "danger")
            return redirect(url_for('admin.manage_centres'))
        centre_name = centre_name.strip()
        existing = Centre.query.filter_by(name=centre_name).first()
        if existing:
            flash("A centre with that name already exists.", "warning")
            return redirect(url_for('admin.manage_centres'))
        new_centre = Centre(name=centre_name)
        db.session.add(new_centre)
        db.session.commit()
        flash("Centre added successfully.", "success")
        return redirect(url_for('admin.manage_centres'))
    centres = Centre.query.order_by(Centre.name).all()
    return render_template('admin_centres.html', centres=centres)

@admin.route('/view_rooms/<int:centre_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def view_rooms(centre_id):
    from app.models import Centre, Room
    centre = Centre.query.get(centre_id)
    if not centre:
        flash("Centre not found.", "danger")
        return redirect(url_for('admin.manage_centres'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_room':
            room_number = request.form.get('room_number').strip()
            room_name = request.form.get('room_name').strip()
            capacity_str = request.form.get('capacity').strip()
            if not room_number or not room_name or not capacity_str:
                flash("Please fill in all fields for the new room.", "danger")
                return redirect(url_for('admin.view_rooms', centre_id=centre_id))
            try:
                capacity_int = int(capacity_str)
            except ValueError:
                flash("Capacity must be a number.", "danger")
                return redirect(url_for('admin.view_rooms', centre_id=centre_id))
            full_room_name = f"{room_number} - {room_name}"
            existing_room = Room.query.filter_by(name=full_room_name, centre_id=centre.id).first()
            if existing_room:
                flash("A room with that number and name already exists in this centre.", "warning")
                return redirect(url_for('admin.view_rooms', centre_id=centre_id))
            new_room = Room(name=full_room_name, capacity=capacity_int, centre_id=centre.id)
            db.session.add(new_room)
            db.session.commit()
            flash("New room added successfully.", "success")
            return redirect(url_for('admin.view_rooms', centre_id=centre_id))
        else:
            update_occurred = False
            for room in centre.rooms:
                new_capacity_str = request.form.get(f'capacity_{room.id}')
                if new_capacity_str:
                    try:
                        new_capacity = int(new_capacity_str)
                    except ValueError:
                        flash(f"Invalid capacity value for room {room.name}.", "danger")
                        continue
                    if room.capacity != new_capacity:
                        if room.sessions:
                            flash(f"Room {room.name} already has sessions assigned. Changing capacity may affect scheduled classes.", "warning")
                        room.capacity = new_capacity
                        update_occurred = True
            if update_occurred:
                try:
                    db.session.commit()
                    flash("Room capacities updated successfully.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error updating capacities: {str(e)}", "danger")
            else:
                flash("No changes were made.", "info")
            return redirect(url_for('admin.view_rooms', centre_id=centre_id))
    
    return render_template('admin_rooms_for_centre.html', centre=centre)

@admin.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_room(room_id):
    from app.models import Room
    room = Room.query.get(room_id)
    if not room:
        flash("Room not found.", "danger")
        return redirect(url_for('admin.manage_centres'))
    centre_id = room.centre_id
    if room.sessions:
        flash("Room has sessions assigned and cannot be deleted.", "danger")
        return redirect(url_for('admin.view_rooms', centre_id=centre_id))
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted successfully.", "success")
    return redirect(url_for('admin.view_rooms', centre_id=centre_id))

@admin.route('/manage_users', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def manage_users():
    from app.models import User, Tutor
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                user.first_name = request.form.get('first_name').strip()
                user.last_name = request.form.get('last_name').strip()
                user.email = request.form.get('email').strip()
                user.role = request.form.get('role')
                new_password = request.form.get('password')
                if new_password:
                    user.set_password(new_password)
                # If the user is assigned the tutor role, ensure a corresponding Tutor record exists.
                if user.role == 'tutor':
                    tutor_obj = Tutor.query.filter_by(email=user.email).first()
                    if not tutor_obj:
                        tutor_obj = Tutor(name=f"{user.first_name} {user.last_name}", email=user.email)
                        db.session.add(tutor_obj)
                try:
                    db.session.commit()
                    flash("User updated successfully.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error updating user: {e}", "danger")
            else:
                flash("User not found.", "danger")
        else:
            flash("No user ID provided.", "danger")
        return redirect(url_for('admin.manage_users'))
    
    users = User.query.order_by(User.role, User.last_name).all()
    user_groups = {}
    for user in users:
        user_groups.setdefault(user.role, []).append(user)
    
    return render_template('admin_manage_users.html', user_groups=user_groups)

