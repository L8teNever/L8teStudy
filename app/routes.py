from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Task, TaskImage, Event, Grade, NotificationSetting, PushSubscription, Subject, db
from app.notifications import notify_new_task, notify_new_event
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
    class_code = data.get('class_code')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    user = None
    if class_code:
        from .models import SchoolClass
        school_class = SchoolClass.query.filter_by(code=class_code.upper()).first()
        if not school_class:
            return jsonify({'success': False, 'message': 'Invalid class code'}), 401
        user = User.query.filter_by(username=username, class_id=school_class.id).first()
    else:
        # Check for super admin without class code
        user = User.query.filter_by(username=username, class_id=None).first()
        if user and not user.is_super_admin:
            return jsonify({'success': False, 'message': 'Class code required for regular users'}), 401

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
        # Return tasks for the user's class
        if current_user.is_super_admin:
            # Super admin sees everything
            tasks = Task.query.filter(Task.deleted_at.is_(None)).order_by(Task.due_date).all()
        else:
            from .models import SchoolClass
            # Tasks for own class OR shared tasks for subjects linked to own class
            tasks = Task.query.filter(
                Task.deleted_at.is_(None),
                db.or_(
                    Task.class_id == current_user.class_id,
                    db.and_(
                        Task.is_shared == True,
                        Task.subject_id.in_(
                            db.session.query(Subject.id).join(Subject.classes).filter(SchoolClass.id == current_user.class_id)
                        )
                    )
                )
            ).order_by(Task.due_date).all()
        
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
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        from datetime import datetime
        due_date = None
        date_str = data.get('due_date')
        if date_str and date_str != 'null' and date_str != 'undefined':
            due_date = datetime.strptime(date_str, '%Y-%m-%d')
            
        new_task = Task(
            user_id=current_user.id,
            class_id=current_user.class_id,
            title=data['title'],
            subject=data.get('subject', 'Allgemein'),
            subject_id=data.get('subject_id'),
            is_shared=data.get('is_shared', 'false').lower() == 'true',
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
        target_class_id = current_user.class_id or new_task.class_id
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Created task: {new_task.title}")
        db.session.add(log)
        
        db.session.commit()
        
        # Trigger Notification
        notify_new_task(new_task)
        
        return jsonify({'success': True, 'id': new_task.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_task: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/tasks/<int:id>', methods=['PUT'])
@login_required
def update_task(id):
    try:
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
        
        # Handle Content Updates (Only Author or Class/Super Admin)
        if task.user_id == current_user.id or current_user.is_admin or current_user.is_super_admin:
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'subject_id' in data:
                task.subject_id = data['subject_id']
            if 'is_shared' in data:
                val = data['is_shared']
                if isinstance(val, str): val = val.lower() == 'true'
                task.is_shared = bool(val)
            
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
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_task: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/tasks/<int:id>', methods=['DELETE'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id and not current_user.is_super_admin:
        return jsonify({'success': False}), 403
        
    from datetime import datetime
    task.deleted_at = datetime.utcnow()
    
    # Audit Log
    from .models import AuditLog
    target_class_id = current_user.class_id or task.class_id
    log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Deleted task: {task.id}")
    db.session.add(log)

    db.session.commit()
    return jsonify({'success': True})

# Events
@api_bp.route('/events', methods=['GET'])
@login_required
def get_events():
    try:
        # Filter events by class
        if current_user.is_super_admin:
            events = Event.query.filter(Event.deleted_at.is_(None)).order_by(Event.date).all()
        else:
            from .models import SchoolClass
            events = Event.query.filter(
                Event.deleted_at.is_(None),
                db.or_(
                    Event.class_id == current_user.class_id,
                    db.and_(
                        Event.is_shared == True,
                        Event.subject_id.in_(
                            db.session.query(Subject.id).join(Subject.classes).filter(SchoolClass.id == current_user.class_id)
                        )
                    )
                )
            ).order_by(Event.date).all()
        return jsonify([{
            'id': e.id,
            'title': e.title,
            'date': e.date.strftime('%Y-%m-%d'),
            'description': e.description
        } for e in events])
    except Exception as e:
        current_app.logger.error(f"Error in get_events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/events', methods=['POST'])
@login_required
def create_event():
    data = request.json
    try:
        from datetime import datetime
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        event_date = datetime.utcnow()
        if data.get('date'):
            event_date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        new_event = Event(
            user_id=current_user.id,
            class_id=current_user.class_id,
            title=data['title'],
            date=event_date,
            description=data.get('description', ''),
            subject_id=data.get('subject_id'),
            is_shared=data.get('is_shared', False)
        )
        db.session.add(new_event)
        
        # Audit Log
        from .models import AuditLog
        target_class_id = current_user.class_id or new_event.class_id
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Created event: {new_event.title}")
        db.session.add(log)
        
        db.session.commit()
        
        # Trigger Notification
        notify_new_event(new_event)
        
        return jsonify({'success': True, 'id': new_event.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_event: {str(e)}")
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
    if event.user_id != current_user.id and not current_user.is_admin and not current_user.is_super_admin:
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
        if 'subject_id' in data:
            event.subject_id = data['subject_id']
        if 'is_shared' in data:
            event.is_shared = bool(data['is_shared'])
        # Audit Log
        from .models import AuditLog
        target_class_id = current_user.class_id or event.class_id
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Updated event: {event.title}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_event: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400

@api_bp.route('/events/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    try:
        event = Event.query.get_or_404(id)
        if event.user_id != current_user.id and not current_user.is_super_admin:
            return jsonify({'success': False}), 403
            
        from datetime import datetime
        event.deleted_at = datetime.utcnow()
        
        # Audit Log
        from .models import AuditLog
        target_class_id = current_user.class_id or event.class_id
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Deleted event: {event.id}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_event: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400

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
        target_class_id = current_user.class_id or (current_user.school_class.id if current_user.school_class else Grade.query.get(new_grade.id).author.class_id)
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Created grade: {new_grade.subject} {new_grade.value}")
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
        target_class_id = current_user.class_id or grade.author.class_id
        log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Updated grade: {grade.id}")
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
    target_class_id = current_user.class_id or grade.author.class_id
    log = AuditLog(user_id=current_user.id, class_id=target_class_id, action=f"Deleted grade: {grade.id}")
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



# --- Admin Routes ---
@api_bp.route('/admin/users', methods=['GET'])
@login_required
def get_users():
    class_id = request.args.get('class_id')
    if current_user.is_super_admin:
        if class_id:
            users = User.query.filter_by(class_id=class_id).all()
        else:
            users = User.query.all()
    elif current_user.is_admin:
        users = User.query.filter_by(class_id=current_user.class_id).all()
    else:
        return jsonify({'success': False}), 403
    return jsonify([{'id': u.id, 'username': u.username, 'is_admin': u.is_admin, 'class_name': u.school_class.name if u.school_class else 'Global'} for u in users])

@api_bp.route('/admin/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    data = request.json
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)
    
    # Super admin can specify class_id, class admin is locked to their own class
    target_class_id = current_user.class_id
    if current_user.is_super_admin:
        target_class_id = data.get('class_id') # Can be None for global admin

    if User.query.filter_by(username=username, class_id=target_class_id).first():
        return jsonify({'success': False, 'message': 'User exists in this class'}), 400
        
    new_user = User(username=username, is_admin=is_admin, class_id=target_class_id)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/admin/users/<int:id>/reset_password', methods=['POST'])
@login_required
def reset_user_password(id):
    if not current_user.is_admin and not current_user.is_super_admin:
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
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    user = User.query.get_or_404(id)
    
    # Class admins can only delete users in their class
    if not current_user.is_super_admin and user.class_id != current_user.class_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    if id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete self'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})

# --- Notification Routes ---

@api_bp.route('/notifications/subscribe', methods=['POST'])
@login_required
def subscribe_push():
    data = request.json
    try:
        # Check if already exists
        exists = PushSubscription.query.filter_by(endpoint=data['endpoint']).first()
        if not exists:
            sub = PushSubscription(
                user_id=current_user.id,
                endpoint=data['endpoint'],
                auth_key=data['keys']['auth'],
                p256dh_key=data['keys']['p256dh']
            )
            db.session.add(sub)
            db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/notifications/unsubscribe', methods=['POST'])
@login_required
def unsubscribe_push():
    data = request.json
    try:
        endpoint = data.get('endpoint')
        if endpoint:
            sub = PushSubscription.query.filter_by(endpoint=endpoint).first()
            if sub and sub.user_id == current_user.id:
                db.session.delete(sub)
                db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@api_bp.route('/settings/notifications', methods=['GET'])
@login_required
def get_notification_settings():
    settings = current_user.notification_settings
    if not settings:
        settings = NotificationSetting(user_id=current_user.id)
        db.session.add(settings)
        db.session.commit()
    
    return jsonify({
        'notify_new_task': settings.notify_new_task,
        'notify_new_event': settings.notify_new_event,
        'reminder_homework': settings.reminder_homework or "",
        'reminder_exam': settings.reminder_exam or ""
    })

@api_bp.route('/settings/theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    if data and 'dark_mode' in data:
        current_user.dark_mode = data['dark_mode']
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@api_bp.route('/settings/language', methods=['POST'])
@login_required
def update_language():
    data = request.get_json()
    if data and 'language' in data:
        lang = data['language']
        if lang in ['de', 'en']:
            current_user.language = lang
            db.session.commit()
            return jsonify({'success': True})
    return jsonify({'success': False}), 400

@api_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    data = request.json
    settings = current_user.notification_settings
    if not settings:
        settings = NotificationSetting(user_id=current_user.id)
        db.session.add(settings)
    
    if 'notify_new_task' in data:
        settings.notify_new_task = bool(data['notify_new_task'])
    if 'notify_new_event' in data:
        settings.notify_new_event = bool(data['notify_new_event'])
    
    if 'reminder_homework' in data:
        settings.reminder_homework = data['reminder_homework']
    if 'reminder_exam' in data:
        settings.reminder_exam = data['reminder_exam']
    
    if settings.reminder_homework == "": settings.reminder_homework = None
    if settings.reminder_exam == "": settings.reminder_exam = None
    
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/vapid_public_key')
def get_vapid_key():
    from app.notifications import VAPID_PUBLIC_KEY
    return jsonify({'publicKey': VAPID_PUBLIC_KEY})

@api_bp.route('/notifications/test', methods=['POST'])
@login_required
def send_test_notification():
    from app.notifications import notify_user
    try:
        notify_user(current_user, "Test-Benachrichtigung", "Dies ist ein Test! Wenn du das liest, funktioniert es.", url='/settings/notifications')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# --- Subject Routes ---

@api_bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    if current_user.is_super_admin:
        subjects = Subject.query.order_by(Subject.name).all()
    else:
        from .models import SchoolClass
        subjects = Subject.query.join(Subject.classes).filter(SchoolClass.id == current_user.class_id).order_by(Subject.name).all()
    # If empty (shouldn't happen due to migration), return defaults
    if not subjects:
       defaults = ['Mathematik', 'Deutsch', 'Englisch', 'Physik', 'Biologie', 'Geschichte', 'Kunst', 'Sport', 'Chemie', 'Religion']
       return jsonify([{'id': i, 'name': n} for i, n in enumerate(defaults)])
       
    return jsonify([{'id': s.id, 'name': s.name} for s in subjects])

@api_bp.route('/subjects', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.json
    name = data.get('name')
    class_ids = data.get('class_ids', []) # Super admin can specify multiple classes
    
    if not name:
        return jsonify({'success': False, 'message': 'Name required'}), 400
    
    from .models import SchoolClass
    new_sub = Subject(name=name)
    
    if current_user.is_super_admin and class_ids:
        new_sub.classes = SchoolClass.query.filter(SchoolClass.id.in_(class_ids)).all()
    elif current_user.class_id:
        new_sub.classes = [SchoolClass.query.get(current_user.class_id)]
    
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/subjects/<int:id>', methods=['DELETE'])
@login_required
def delete_subject(id):
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    subject = Subject.query.get_or_404(id)
    # Check access
    if not current_user.is_super_admin:
        if current_user.school_class not in subject.classes:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    db.session.delete(subject)
    db.session.commit()
    return jsonify({'success': True})



@api_bp.route('/admin/activity', methods=['GET'])
@login_required
def get_activity_log():
    if not current_user.is_admin:
        return jsonify({'success': False}), 403
    
    from .models import AuditLog
    class_id = request.args.get('class_id')
    
    # Filter log by class
    if current_user.is_super_admin:
        query = AuditLog.query
        if class_id:
            query = query.filter_by(class_id=class_id)
        logs = query.join(User).order_by(AuditLog.timestamp.desc()).limit(100).all()
    else:
        logs = AuditLog.query.filter_by(class_id=current_user.class_id).join(User).order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    
    return jsonify([{
        'id': l.id,
        'user': l.author.username,
        'action': l.action,
        'timestamp': l.timestamp.strftime('%d.%m.%Y %H:%M')
    } for l in logs])

# --- Super Admin Dashboard & Global Management ---

@api_bp.route('/admin/dashboard/stats', methods=['GET'])
@login_required
def get_admin_dashboard_stats():
    if not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    from .models import SchoolClass, Task, Event
    return jsonify({
        'class_count': SchoolClass.query.count(),
        'user_count': User.query.count(),
        'task_count': Task.query.filter_by(deleted_at=None).count(),
        'event_count': Event.query.filter_by(deleted_at=None).count(),
    })

@api_bp.route('/admin/shared-content', methods=['GET'])
@login_required
def get_shared_content():
    if not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    from .models import Task, Event
    tasks = Task.query.filter_by(is_shared=True, deleted_at=None).all()
    events = Event.query.filter_by(is_shared=True, deleted_at=None).all()
    
    return jsonify({
        'tasks': [{
            'id': t.id, 
            'title': t.title, 
            'subject': t.subject.name if t.subject else 'Kein Fach',
            'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
            'description': t.description,
            'is_shared': t.is_shared
        } for t in tasks],
        'events': [{
            'id': e.id, 
            'title': e.title, 
            'date': e.date.strftime('%Y-%m-%d'),
            'description': e.description,
            'is_shared': e.is_shared
        } for e in events]
    })

@api_bp.route('/subjects/<int:id>/classes', methods=['POST'])
@login_required
def update_subject_classes(id):
    if not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    data = request.json
    class_ids = data.get('class_ids', [])
    
    from .models import SchoolClass
    subject = Subject.query.get_or_404(id)
    subject.classes = SchoolClass.query.filter(SchoolClass.id.in_(class_ids)).all()
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/subjects/<int:id>', methods=['GET'])
@login_required
def get_subject_detail(id):
    subject = Subject.query.get_or_404(id)
    # Check if user has access to this subject
    if not current_user.is_super_admin:
        if current_user.school_class not in subject.classes:
            return jsonify({'success': False}), 403
            
    return jsonify({
        'id': subject.id,
        'name': subject.name,
        'class_ids': [c.id for c in subject.classes]
    })

# --- Super Admin Class Management ---

@api_bp.route('/admin/classes', methods=['GET'])
@login_required
def get_classes():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    from .models import SchoolClass
    classes = SchoolClass.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'code': c.code,
        'user_count': c.users.count()
    } for c in classes])

@api_bp.route('/admin/classes', methods=['POST'])
@login_required
def create_class():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'success': False, 'message': 'Name required'}), 400
    
    from .models import SchoolClass
    new_class = SchoolClass(name=name)
    # Code is auto-generated in model
    db.session.add(new_class)
    db.session.commit()
    
    return jsonify({'success': True, 'id': new_class.id, 'code': new_class.code})

@api_bp.route('/admin/classes/<int:id>', methods=['DELETE'])
@login_required
def delete_class(id):
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    from .models import SchoolClass
    c = SchoolClass.query.get_or_404(id)
    # Check if class has users
    if c.users.count() > 0:
        return jsonify({'success': False, 'message': 'Cannot delete class with users'}), 400
        
    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True})
