from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Task, TaskImage, Event, Grade, db
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
from . import login_manager, limiter, csrf

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Main Routes ---
@main_bp.route('/service-worker.js')
def sw():
    return current_app.send_static_file('sw.js')

@main_bp.route('/manifest.json')
def manifest():
    return current_app.send_static_file('manifest.json')

@main_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@main_bp.route('/<path:path>')
@login_required
def catch_all(path):
    return render_template('index.html', user=current_user)

# --- Auth Routes ---
@auth_bp.route('/login', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def login():
    from flask import session
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session.permanent = True
        login_user(user, remember=True)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login_page')) # Assuming we have a standalone login page or handle it via index

@auth_bp.route('/login-page') 
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')

# --- API Routes ---

# Tasks
@api_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    try:
        # Return ALL tasks that represent shared homework
        # Filter by user_id only if we wanted private tasks, but user requested all tasks be shared.
        tasks = Task.query.filter(Task.deleted_at.is_(None)).order_by(Task.due_date).all()
        
        from .models import TaskCompletion
        
        results = []
        for t in tasks:
            # Check completion status for THIS user
            completion = TaskCompletion.query.filter_by(user_id=current_user.id, task_id=t.id).first()
            is_done = completion.is_done if completion else False
            
            results.append({
                'id': t.id,
                'title': t.title,
                'subject': t.subject,
                'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
                'description': t.description,
                'is_done': is_done,
                # Updated to use secure route /uploads/<filename>
                'images': [{'id': img.id, 'url': f"/uploads/{img.filename}"} for img in t.images]
            })
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in get_tasks: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    # Handle both JSON and FormData
    data = request.get_json() if request.is_json else request.form
    
    try:
        from datetime import datetime
        due_date = None
        date_str = data.get('due_date')
        if date_str and date_str != 'null' and date_str != 'undefined':
            due_date = datetime.strptime(date_str, '%Y-%m-%d')
            
        new_task = Task(
            user_id=current_user.id,
            title=data['title'],
            subject=data.get('subject', 'Allgemein'),
            due_date=due_date,
            description=data.get('description', '')
        )
        db.session.add(new_task)
        db.session.flush() # get ID

        # Handle Images
        if request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    
                    img = TaskImage(task_id=new_task.id, filename=filename)
                    db.session.add(img)
        
        # Audit Log
        from .models import AuditLog
        log = AuditLog(user_id=current_user.id, action=f"Created task: {new_task.title}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True, 'id': new_task.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    # Handle JSON (toggle status) or FormData (edit content)
    data = request.get_json() if request.is_json else request.form
    
    # Handle Completion Status (Per User) - usually JSON
    if 'is_done' in data:
        from .models import TaskCompletion
        completion = TaskCompletion.query.filter_by(user_id=current_user.id, task_id=task.id).first()
        if not completion:
            completion = TaskCompletion(user_id=current_user.id, task_id=task.id)
            db.session.add(completion)
        # Handle string 'true'/'false' from FormData or boolean from JSON
        is_done_val = data['is_done']
        if isinstance(is_done_val, str):
            is_done_val = is_done_val.lower() == 'true'
        completion.is_done = bool(is_done_val)
    
    # Handle Content Updates (Only Author or Admin)
    # Note: Logic here implies if you send 'title', you are editing content.
    if task.user_id == current_user.id or current_user.is_admin:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        
        # Handle Deleted Images
        if 'deleted_images' in data:
            # Expecting comma-separated string if from FormData, or list if JSON (but we use FormData for edit)
            del_ids = data['deleted_images']
            if isinstance(del_ids, str) and del_ids:
                del_ids = [int(x) for x in del_ids.split(',')]
            
            if del_ids:
                imgs_to_del = TaskImage.query.filter(TaskImage.id.in_(del_ids), TaskImage.task_id == task.id).all()
                for img in imgs_to_del:
                    # Remove from FS
                    path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
                    if os.path.exists(path):
                        try:
                            os.remove(path)
                        except:
                            pass
                    db.session.delete(img)

        # Handle New Images
        if request.files:
            files = request.files.getlist('images')
            from datetime import datetime
            for file in files:
                if file and file.filename:
                    filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    
                    img = TaskImage(task_id=task.id, filename=filename)
                    db.session.add(img)
    
    db.session.commit()
    return jsonify({'success': True})
    # All changes committed at block end already
    pass

@api_bp.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return jsonify({'success': False}), 403
        
    from datetime import datetime
    task.deleted_at = datetime.utcnow()
    
    # Audit Log
    from .models import AuditLog
    log = AuditLog(user_id=current_user.id, action=f"Deleted task: {task.id}")
    db.session.add(log)

    db.session.commit()
    return jsonify({'success': True})

# Events
@api_bp.route('/events', methods=['GET'])
@login_required
def get_events():
    # Make events shared for everyone
    events = Event.query.filter(Event.deleted_at == None).order_by(Event.date).all()
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'date': e.date.strftime('%Y-%m-%d'),
        'description': e.description
    } for e in events])

@api_bp.route('/events', methods=['POST'])
@login_required
def create_event():
    data = request.json
    try:
        from datetime import datetime
        event_date = datetime.utcnow()
        if data.get('date'):
            event_date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        new_event = Event(
            user_id=current_user.id,
            title=data['title'],
            date=event_date,
            description=data.get('description', '')
        )
        db.session.add(new_event)
        
        # Audit Log
        from .models import AuditLog
        log = AuditLog(user_id=current_user.id, action=f"Created event: {new_event.title}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True, 'id': new_event.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/events/<int:id>', methods=['PUT'])
@login_required
def update_event(id):
    event = Event.query.get_or_404(id)
    # Events are shared, so allow edit if user is author OR admin, OR maybe everyone?
    # Requirement: "everyone can see created events". "one wants to edit them".
    # Assuming everyone can edit shared events for now to keep it simple and collaborative.
    # Or restrict to author/admin. Let's restrict to author/admin for safety unless specified otherwise.
    # Actually, user said "mann soll auch die funktion haben die termine ... zu bearbeiten". "man" implies the user.
    # If the user created it, yes. If shared, maybe collaborative?
    # Let's stick to: Author or Admin can edit content.
    if event.user_id != current_user.id and not current_user.is_admin:
         return jsonify({'success': False, 'message': 'Not authorized'}), 403

    data = request.json
    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'date' in data:
            from datetime import datetime
            event.date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        # Audit Log
        from .models import AuditLog
        log = AuditLog(user_id=current_user.id, action=f"Updated event: {event.title}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/events/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    if event.user_id != current_user.id:
        return jsonify({'success': False}), 403
        
    from datetime import datetime
    event.deleted_at = datetime.utcnow()
    
    # Audit Log
    from .models import AuditLog
    log = AuditLog(user_id=current_user.id, action=f"Deleted event: {event.id}")
    db.session.add(log)
    
    db.session.commit()
    return jsonify({'success': True})

# Grades
@api_bp.route('/grades', methods=['GET'])
@login_required
def get_grades():
    grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.date.desc()).all()
    return jsonify([{
        'id': g.id,
        'subject': g.subject,
        'value': g.value,
        'weight': g.weight,
        'title': g.title,
        'date': g.date.strftime('%Y-%m-%d'),
        'description': g.description
    } for g in grades])

@api_bp.route('/grades', methods=['POST'])
@login_required
def create_grade():
    data = request.json
    try:
        from datetime import datetime
        grade_date = datetime.utcnow()
        if data.get('date'):
            grade_date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        new_grade = Grade(
            user_id=current_user.id,
            subject=data['subject'],
            value=float(data['value']),
            weight=float(data.get('weight', 1.0)),
            title=data.get('title', 'Note'),
            date=grade_date,
            description=data.get('description', '')
        )
        db.session.add(new_grade)
        
        # Audit Log
        from .models import AuditLog
        log = AuditLog(user_id=current_user.id, action=f"Created grade: {new_grade.subject} {new_grade.value}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True, 'id': new_grade.id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/grades/<int:id>', methods=['PUT'])
@login_required
def update_grade(id):
    grade = Grade.query.get_or_404(id)
    if grade.user_id != current_user.id:
        return jsonify({'success': False}), 403

    data = request.json
    try:
        if 'subject' in data:
            grade.subject = data['subject']
        if 'value' in data:
            grade.value = float(data['value'])
        if 'title' in data:
            grade.title = data['title']
        if 'date' in data:
            from datetime import datetime
            grade.date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        # Audit Log
        from .models import AuditLog
        log = AuditLog(user_id=current_user.id, action=f"Updated grade: {grade.id}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/grades/<int:id>', methods=['DELETE'])
@login_required
def delete_grade(id):
    grade = Grade.query.get_or_404(id)
    if grade.user_id != current_user.id:
        return jsonify({'success': False}), 403
        
    db.session.delete(grade)
    
    # Audit Log
    from .models import AuditLog
    log = AuditLog(user_id=current_user.id, action=f"Deleted grade: {grade.id}")
    db.session.add(log)
    
    db.session.commit()
    return jsonify({'success': True})

# --- Settings ---

@api_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    current_pw = data.get('current_password')
    new_pw = data.get('new_password')
    
    if not current_pw or not new_pw:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    if not current_user.check_password(current_pw):
        return jsonify({'success': False, 'message': 'Aktuelles Passwort falsch'}), 400
        
    current_user.set_password(new_pw)
    db.session.commit()
    
    return jsonify({'success': True})

@api_bp.route('/settings/theme', methods=['POST'])
@login_required
def update_theme():
    data = request.json
    dark_mode = data.get('dark_mode')
    if dark_mode is not None:
        current_user.dark_mode = bool(dark_mode)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Missing dark_mode value'}), 400

# --- Admin Routes ---
@api_bp.route('/admin/users', methods=['GET'])
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username, 'is_admin': u.is_admin} for u in users])

@api_bp.route('/admin/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'User exists'}), 400
        
    new_user = User(username=username, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/admin/users/<int:id>/reset_password', methods=['POST'])
@login_required
def reset_user_password(id):
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
        
    user = User.query.get_or_404(id)
    data = request.json
    new_pw = data.get('password')
    
    if not new_pw:
        return jsonify({'success': False, 'message': 'Missing password'}), 400
        
    user.set_password(new_pw)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/admin/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
    if id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete self'}), 400
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})



