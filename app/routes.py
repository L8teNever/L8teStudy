from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_file, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from .models import (
    User, Task, TaskImage, Event, Grade, NotificationSetting, 
    PushSubscription, Subject, SubjectMapping, TaskMessage, TaskChatRead, 
    GlobalSetting, SchoolClass, TaskCompletion, UserRole,
    DriveFolder, DriveFile, DriveFileContent,
    subject_classes, db
)
from app.notifications import notify_new_task, notify_new_event
from werkzeug.utils import secure_filename
import os
import json
from io import BytesIO
from datetime import datetime, date, timedelta
import webuntis
try:
    import markdown as md_lib
except ImportError:
    md_lib = None
from . import login_manager, limiter, csrf

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/config', methods=['GET'])
@login_required
def get_config():
    chat_enabled = False
    if current_user.school_class:
        chat_enabled = current_user.school_class.chat_enabled
    elif current_user.is_super_admin:
        chat_enabled = True # Super admin always has it enabled for testing potentially, or strictly based on context
    
    return jsonify({
        'chat_enabled': chat_enabled,
        'user_id': current_user.id,
        'role': current_user.role
    })

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
def index():
    # Fresh Install Check
    from .models import User
    if not User.query.first():
        return redirect('/setup')

    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
    
    # First time setup check (no classes)
    from .models import SchoolClass
    if not SchoolClass.query.first():
         return redirect('/setup')
         
    # Redirect to user's class if student/admin
    if current_user.school_class:
        return redirect(f"/{current_user.school_class.name}/home")
        
    # If Super Admin and no class assigned/in context, goes to a class selection or default one?
    # For now, grab the first class or a special dashboard
    first_class = SchoolClass.query.first()
    if first_class:
        return redirect(f"/{first_class.name}/home")
        
    return render_template('index.html', user=current_user)

@main_bp.route('/setup')
def setup():
    # Allow if no users exist OR (logged in AND super admin AND no classes)
    from .models import User, SchoolClass
    has_users = User.query.first() is not None
    
    if not has_users:
        return render_template('setup.html')
        
    if current_user.is_authenticated and current_user.is_super_admin:
        if not SchoolClass.query.first():
             return render_template('setup.html')
             
    # If we are here, setup is not allowed
    return redirect('/')

@api_bp.route('/setup/create-admin', methods=['POST'])
def setup_create_admin():
    from .models import User, UserRole
    if User.query.first():
        return jsonify({'success': False, 'message': 'Setup already completed'}), 403
        
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    user = User(username=username, role=UserRole.SUPER_ADMIN, needs_password_change=False)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    return jsonify({'success': True})

@main_bp.route('/<class_name>/<path:subpath>')
def class_view(class_name, subpath):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    # Case insensitive lookup
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        # Invalid class in URL
        return redirect('/')
        
    # Permission Check
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            # Student accessing wrong class
            return "Access Denied: You do not belong to this class.", 403
            
    # Inject active class context into template
    return render_template('index.html', user=current_user, active_class=target_class)

@main_bp.route('/<path:path>')
def catch_all(path):
    if not current_user.is_authenticated:
        # Check if this path is a valid class code for a direct login link
        # We only do this for single-level paths (no extra slashes)
        clean_path = path.rstrip('/')
        if '/' not in clean_path:
            from .models import SchoolClass
            sc = SchoolClass.query.filter_by(code=clean_path.upper()).first()
            if sc:
                return redirect(url_for('auth.login_page', class_code=sc.code))
        return redirect(url_for('auth.login_page'))
    return render_template('index.html', user=current_user)

# --- Auth Routes ---
@main_bp.route('/privacy')
def privacy_policy():
    default_text = """# Datenschutzerklärung für L8teStudy

## 1. Datenschutz auf einen Blick

### Allgemeine Hinweise
Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Anwendung nutzen. Personenbezogene Daten sind alle Daten, mit denen Sie persönlich identifiziert werden können.

### Datenerfassung in dieser Anwendung
Die Datenverarbeitung in dieser Anwendung erfolgt durch den Betreiber der Instanz. L8teStudy ist eine **selbstgehostete Anwendung**. Das bedeutet, dass alle Daten auf dem Server verbleiben, auf dem die Anwendung installiert wurde. Es findet keine Übermittlung an die Entwickler von L8teStudy statt.

## 2. Allgemeine Hinweise und Pflichtinformationen

### Datenschutz
Der Betreiber dieser Anwendung nimmt den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln Ihre personenbezogenen Daten vertraulich und entsprechend den gesetzlichen Datenschutzvorschriften sowie dieser Datenschutzerklärung.

### Hinweis zur verantwortlichen Stelle
Die verantwortliche Stelle für die Datenverarbeitung ist die Person oder Organisation (z.B. Ihre Schule), die diese Instanz von L8teStudy betreibt.

## 3. Datenerfassung in L8teStudy

### Authentifizierung & Benutzerprofil
Für die Nutzung der App ist die Erstellung eines Benutzerkontos erforderlich. Dabei werden folgende Daten gespeichert:
*   Benutzername
*   Passwort (gehasht und verschlüsselt)
*   Zugehörige Schulklasse

### Nutzungsdaten (Aufgaben, Noten, Termine)
Alle von Ihnen eingegebenen Daten wie Hausaufgaben, Prüfungstermine, Noten und persönliche To-Dos werden ausschließlich in der lokalen Datenbank der Instanz gespeichert. Diese Daten dienen allein dem Zweck der persönlichen Organisation Ihres Schulalltags.

### WebUntis Integration
Sofern Sie die WebUntis-Synchronisierung aktivieren, werden Ihre WebUntis-Zugangsdaten (verschlüsselt) in der lokalen Datenbank gespeichert. Die App kommuniziert direkt mit dem offiziellen WebUntis-Server Ihrer Schule, um Stundenpläne und Vertretungsdaten abzurufen.

### Cookies & Lokale Speicherung
Diese Anwendung verwendet technisch notwendige Cookies und den LocalStorage Ihres Browsers, um:
1.  Sie angemeldet zu halten (Sitzungs-Management).
2.  Ihre Design-Einstellungen (z.B. Darkmode) zu speichern.
Diese Daten sind für den Betrieb der App zwingend erforderlich.

## 4. Hosting und Datensicherheit

### Lokales Hosting
Die Anwendung läuft auf der Infrastruktur des Betreibers. Es findet keine Cloud-Speicherung auf externen Systemen statt.

### SSL- bzw. TLS-Verschlüsselung
Diese Seite nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte eine SSL-bzw. TLS-Verschlüsselung.

## 5. Ihre Rechte

Sie haben jederzeit das Recht, unentgeltlich Auskunft über Herkunft, Empfänger und Zweck Ihrer gespeicherten personenbezogenen Daten zu erhalten. Sie haben außerdem ein Recht, die Berichtigung oder Löschung dieser Daten zu verlangen. Hierzu sowie zu weiteren Fragen zum Thema Datenschutz können Sie sich jederzeit an den Administrator Ihrer L8teStudy-Instanz wenden.
"""
    content = GlobalSetting.get('privacy_policy', default_text)
    
    if md_lib:
        html_content = md_lib.markdown(content)
    else:
        # Simple manual conversion if library is missing
        import re
        html = content
        html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.M)
        html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^\* (.*)$', r'<li>\1</li>', html, flags=re.M)
        html = html.replace('\n', '<br>')
        html_content = html
        
    return render_template('legal.html', title='Datenschutzerklärung', content=html_content)

@main_bp.route('/imprint')
def imprint():
    default_text = "Hinterlegen Sie hier Ihr Impressum im Admin-Bereich."
    content = GlobalSetting.get('imprint', default_text)
    
    if md_lib:
        html_content = md_lib.markdown(content)
    else:
        # Simple manual conversion if library is missing
        import re
        html = content
        html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.M)
        html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.M)
        html = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html, flags=re.M)
        html = re.sub(r'^\* (.*)$', r'<li>\1</li>', html, flags=re.M)
        html = html.replace('\n', '<br>')
        html_content = html
        
    return render_template('legal.html', title='Impressum', content=html_content)

login_manager.login_view = 'auth.login_page'
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
    return redirect('/login-page', code=302)

@auth_bp.route('/login-page')
@auth_bp.route('/<class_code>/login')
def login_page(class_code=None):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    class_name = None
    if class_code:
        from .models import SchoolClass
        sc = SchoolClass.query.filter_by(code=class_code.upper()).first()
        if sc:
            class_name = sc.name
            
    return render_template('login.html', prefilled_code=class_code, class_name=class_name)

# --- API Routes ---

# Tasks
@api_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    try:
        # Return tasks for the user's class
        target_class_id = request.args.get('class_id')
        if current_user.is_super_admin:
            if target_class_id:
                # Super admin viewing a specific class
                from .models import SchoolClass
                tasks = Task.query.filter(
                    Task.deleted_at.is_(None),
                    db.or_(
                        Task.class_id == target_class_id,
                         db.and_(
                            Task.is_shared == True,
                            Task.subject_id.in_(
                                db.session.query(Subject.id).join(Subject.classes).filter(SchoolClass.id == target_class_id)
                            )
                        )
                    )
                ).order_by(Task.due_date).all()
            else:
                # Super admin sees everything (default fallback)
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
                'subject_id': t.subject_id,
                'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
                'description': t.description,
                'is_done': is_done,
                # Updated to use secure route /uploads/<filename>
                'images': [{'id': img.id, 'url': f"/uploads/{img.filename}"} for img in t.images],
                'unread_chat_count': TaskMessage.query.filter(
                    TaskMessage.task_id == t.id,
                    TaskMessage.created_at > (
                        db.session.query(TaskChatRead.last_read_at)
                        .filter_by(user_id=current_user.id, task_id=t.id)
                        .scalar() or datetime(1970, 1, 1)
                    )
                ).count()
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
            
        target_class_id = current_user.class_id
        # Super Admins can optionally create tasks for a specific class
        class_id_val = data.get('class_id')
        if current_user.is_super_admin and class_id_val:
             if class_id_val not in ['null', 'undefined', '']:
                target_class_id = class_id_val

        sub_id_val = data.get('subject_id')
        if sub_id_val in ['null', 'undefined', '', 'None']:
            sub_id_val = None

        new_task = Task(
            user_id=current_user.id,
            class_id=target_class_id,
            title=data['title'],
            subject=data.get('subject', 'Allgemein'),
            subject_id=sub_id_val,
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
                sub_id_val = data['subject_id']
                if sub_id_val in ['null', 'undefined', '', 'None']:
                    sub_id_val = None
                task.subject_id = sub_id_val
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


@api_bp.route('/tasks/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_task(id):
    """Toggle task completion status for current user"""
    try:
        task = Task.query.get_or_404(id)
        
        # Check if user has access to this task
        if task.class_id != current_user.class_id and not current_user.is_super_admin:
            return jsonify({'success': False, 'message': 'No permission'}), 403
        
        from .models import TaskCompletion
        
        # Find or create completion record
        completion = TaskCompletion.query.filter_by(
            user_id=current_user.id,
            task_id=id
        ).first()
        
        if completion:
            # Toggle existing
            completion.is_done = not completion.is_done
        else:
            # Create new completion
            completion = TaskCompletion(
                user_id=current_user.id,
                task_id=id,
                is_done=True
            )
            db.session.add(completion)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_done': completion.is_done
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in toggle_task: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/tasks/<int:id>/chat', methods=['GET'])
@login_required
def get_task_chat(id):
    try:
        task = Task.query.get_or_404(id)
        from .models import SchoolClass
        sc = SchoolClass.query.get(current_user.class_id)
        # Only check chat_enabled if not super admin (assuming admin wants to test)
        # Note: sc might be None for superadmin if class_id is None
        chat_enabled = sc.chat_enabled if sc else False
        if not current_user.is_super_admin and not chat_enabled:
             return jsonify({'error': 'Chat disabled'}), 403

        messages = TaskMessage.query.filter_by(task_id=id).order_by(TaskMessage.created_at).all()
        results = [{
            'id': m.id,
            'user_id': m.user_id,
            'user_name': m.user.username,
            'content': m.content,
            'message_type': m.message_type,
            'file_url': m.file_url,
            'file_name': m.file_name,
            'created_at': m.created_at.isoformat(),
            'is_own': m.user_id == current_user.id,
            'parent_id': m.parent_id,
            'parent_user': m.parent.user.username if m.parent else None,
            'parent_content': m.parent.content if m.parent else (m.parent.file_name if m.parent and m.parent.file_name else None)
        } for m in messages]
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:id>/chat', methods=['POST'])
@login_required
def post_task_chat(id):
    try:
        task = Task.query.get_or_404(id)
        sc = SchoolClass.query.get(current_user.class_id) if current_user.class_id else None
        chat_enabled = sc.chat_enabled if sc else False
        
        if not current_user.is_super_admin and not chat_enabled:
             return jsonify({'error': 'Chat disabled'}), 403
             
        from datetime import datetime
        content = request.form.get('content')
        files = request.files.getlist('files')
        
        posted_msgs = []

        # 1. Text Message
        parent_id = request.form.get('parent_id')
        if parent_id == 'null' or not parent_id:
            parent_id = None
            
        if content and content.strip():
            msg = TaskMessage(task_id=id, user_id=current_user.id, content=content, message_type='text', parent_id=parent_id)
            db.session.add(msg)
            posted_msgs.append(msg)

        # 2. Files
        for file in files:
            if file and file.filename:
                filename = secure_filename(f"chat_{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                
                # Determine type
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                msg_type = 'image' if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp'] else 'file'
                
                msg = TaskMessage(
                    task_id=id, 
                    user_id=current_user.id, 
                    message_type=msg_type,
                    file_url=f"/uploads/{filename}",
                    file_name=file.filename
                )
                db.session.add(msg)
                posted_msgs.append(msg)

        db.session.commit()
        
        # Trigger notifications
        from app.notifications import notify_chat_message
        for m in posted_msgs:
            try:
                notify_chat_message(m)
            except Exception as e:
                current_app.logger.error(f"Failed to notify chat message: {e}")

        # Mark as read for sender
        read_stat = TaskChatRead.query.filter_by(user_id=current_user.id, task_id=id).first()
        if not read_stat:
            read_stat = TaskChatRead(user_id=current_user.id, task_id=id)
            db.session.add(read_stat)
        read_stat.last_read_at = datetime.utcnow()
        db.session.commit()

        return jsonify([{
            'id': m.id,
            'user_id': m.user_id,
            'user_name': current_user.username,
            'content': m.content,
            'message_type': m.message_type,
            'file_url': m.file_url,
            'file_name': m.file_name,
            'created_at': m.created_at.isoformat(),
            'is_own': True,
            'parent_id': m.parent_id,
            'parent_user': m.parent.user.username if m.parent else None,
            'parent_content': m.parent.content if m.parent else (m.parent.file_name if m.parent and m.parent.file_name else None)
        } for m in posted_msgs])

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Post chat error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/chat/message/<int:msg_id>', methods=['DELETE'])
@login_required
def delete_chat_message(msg_id):
    try:
        msg = TaskMessage.query.get_or_404(msg_id)
        # Auth: author or super admin
        if msg.user_id != current_user.id and not current_user.is_super_admin:
            return jsonify({'success': False, 'message': 'Nicht autorisiert'}), 403
            
        # Delete physical file if exists
        if msg.message_type in ['image', 'file'] and msg.file_url:
            try:
                # Extract filename from /uploads/filename
                filename = msg.file_url.split('/')[-1]
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                current_app.logger.error(f"Error deleting chat file: {e}")
        
        db.session.delete(msg)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_chat_message: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/class/members', methods=['GET'])
@login_required
def get_class_members():
    if not current_user.class_id:
        return jsonify([])
    members = User.query.filter_by(class_id=current_user.class_id).all()
    # Also include superadmins if needed? Let's stick to class members for now
    return jsonify([{
        'id': u.id,
        'username': u.username
    } for u in members])

@api_bp.route('/tasks/<int:id>/read', methods=['POST'])
@login_required
def mark_task_chat_read(id):
    try:
        from datetime import datetime
        read_stat = TaskChatRead.query.filter_by(user_id=current_user.id, task_id=id).first()
        if not read_stat:
            read_stat = TaskChatRead(user_id=current_user.id, task_id=id)
            db.session.add(read_stat)
        
        read_stat.last_read_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Events
@api_bp.route('/events', methods=['GET'])
@login_required
def get_events():
    try:
        # Filter events by class
        target_class_id = request.args.get('class_id')
        if current_user.is_super_admin:
            if target_class_id:
                 from .models import SchoolClass
                 events = Event.query.filter(
                    Event.deleted_at.is_(None),
                    db.or_(
                        Event.class_id == target_class_id,
                        db.and_(
                            Event.is_shared == True,
                            Event.subject_id.in_(
                                db.session.query(Subject.id).join(Subject.classes).filter(SchoolClass.id == target_class_id)
                            )
                        )
                    )
                ).order_by(Event.date).all()
            else:
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
            'subject_id': e.subject_id,
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
            
        target_class_id = current_user.class_id
        class_id_val = data.get('class_id')
        if current_user.is_super_admin and class_id_val:
             if class_id_val not in ['null', 'undefined', '']:
                target_class_id = class_id_val

        sub_id_val = data.get('subject_id')
        if sub_id_val in ['null', 'undefined', '', 'None']:
            sub_id_val = None

        new_event = Event(
            user_id=current_user.id,
            class_id=target_class_id,
            title=data['title'],
            date=event_date,
            description=data.get('description', ''),
            subject_id=sub_id_val,
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
        log = AuditLog(user_id=current_user.id, class_id=current_user.class_id, action=f"Created grade: {new_grade.subject} {new_grade.value}")
        db.session.add(log)
        
        db.session.commit()
        return jsonify({'success': True, 'id': new_grade.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_grade: {str(e)}")
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
        if 'weight' in data:
            grade.weight = float(data['weight'])
        if 'title' in data:
            grade.title = data['title']
        if 'date' in data:
            from datetime import datetime
            grade.date = datetime.strptime(data['date'], '%Y-%m-%d')
            
        # Audit Log
        from .models import AuditLog
        target_class_id = current_user.class_id
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
    target_class_id = current_user.class_id
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
    
    # Validation logic depends on context
    if not new_pw:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    # If the user is forced to change password (e.g. first login), we skip the current_password check
    # as per user request to make it smoother.
    if not current_user.needs_password_change:
        if not current_pw:
            return jsonify({'success': False, 'message': 'Missing data'}), 400
        if not current_user.check_password(current_pw):
            return jsonify({'success': False, 'message': 'Aktuelles Passwort falsch'}), 400

    # Complexity check
    import re
    if len(new_pw) < 7:
        return jsonify({'success': False, 'message': 'Passwort muss mindestens 7 Zeichen lang sein'}), 400
    if not re.search("[a-z]", new_pw) or not re.search("[A-Z]", new_pw) or not re.search("[0-9]", new_pw):
        return jsonify({'success': False, 'message': 'Passwort muss Groß-, Kleinschreibung und Zahlen enthalten'}), 400
        
    current_user.set_password(new_pw)
    current_user.needs_password_change = False
    db.session.commit()
    
    return jsonify({'success': True})
    
@api_bp.route('/settings/username', methods=['POST'])
@login_required
def update_own_username():
    data = request.json
    new_username = data.get('username')
    if not new_username or len(new_username.strip()) < 3:
        return jsonify({'success': False, 'message': 'Username too short'}), 400
    
    # Check if taken in class
    if User.query.filter_by(username=new_username.strip(), class_id=current_user.class_id).first():
        return jsonify({'success': False, 'message': 'Username already taken in your class'}), 400
        
    current_user.username = new_username.strip()
    db.session.commit()
    return jsonify({'success': True, 'new_username': current_user.username})



# --- Admin Routes ---
@api_bp.route('/tutorial/complete', methods=['POST'])
@login_required
def complete_tutorial():
    current_user.has_seen_tutorial = True
    db.session.commit()
    return jsonify({'success': True})

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
    return jsonify([{'id': u.id, 'username': u.username, 'role': u.role, 'is_admin': u.is_admin, 'class_name': u.school_class.name if u.school_class else 'Global'} for u in users])

@api_bp.route('/admin/users', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')
    # Legacy support
    if 'is_admin' in data and data['is_admin']:
        if role == 'student': role = 'admin'

    # Super admin can specify class_id, class admin is locked to their own class
    target_class_id = current_user.class_id
    if current_user.is_super_admin:
        target_class_id = data.get('class_id') # Can be None for global admin
    
    # Permission Validation
    if role == 'super_admin' and not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Nur Super Admins können Super Admins erstellen'}), 403
    
    # Check if role is valid
    if role not in ['student', 'admin', 'super_admin']:
        return jsonify({'success': False, 'message': 'Ungültige Rolle'}), 400

    if User.query.filter_by(username=username, class_id=target_class_id).first():
        return jsonify({'success': False, 'message': 'User exists in this class'}), 400
        
    new_user = User(username=username, role=role, class_id=target_class_id)
    new_user.set_password(password)
    new_user.needs_password_change = True
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
    user.needs_password_change = True
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/admin/users/<int:id>', methods=['PUT', 'PATCH'])
@login_required
def update_user(id):
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False}), 403
        
    user = User.query.get_or_404(id)
    
    # Class admins can only update users in their class
    if not current_user.is_super_admin and user.class_id != current_user.class_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.json
    if 'username' in data:
        new_name = data['username'].strip()
        if len(new_name) < 3:
            return jsonify({'success': False, 'message': 'Name too short'}), 400
            
        # Check collision
        existing = User.query.filter_by(username=new_name, class_id=user.class_id).first()
        if existing and existing.id != user.id:
            return jsonify({'success': False, 'message': 'Name already taken in this class'}), 400
            
        user.username = new_name
        
    if 'role' in data and current_user.is_super_admin:
        # Only superadmin should change roles generally, or at least be careful
        user.role = data['role']
        
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/admin/backup', methods=['GET'])
@login_required
def export_backup():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    def serialize(obj):
        data = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            if isinstance(val, (datetime, date)):
                data[col.name] = val.isoformat()
            else:
                data[col.name] = val
        return data

    backup_data = {
        'version': '1.0',
        'timestamp': datetime.utcnow().isoformat(),
        'school_classes': [serialize(c) for c in SchoolClass.query.all()],
        'users': [serialize(u) for u in User.query.all()],
        'subjects': [serialize(s) for s in Subject.query.all()],
        'subject_classes': [{'subject_id': a.subject_id, 'class_id': a.class_id} for a in db.session.query(subject_classes).all()],
        'tasks': [serialize(t) for t in Task.query.all()],
        'task_completions': [serialize(tc) for tc in TaskCompletion.query.all()],
        'events': [serialize(e) for e in Event.query.all()],
        'grades': [serialize(g) for g in Grade.query.all()],
        'global_settings': [serialize(gs) for gs in GlobalSetting.query.all()],
        'notification_settings': [serialize(ns) for ns in NotificationSetting.query.all()],
        'task_messages': [serialize(tm) for tm in TaskMessage.query.all()],
        'task_chat_reads': [serialize(tcr) for tcr in TaskChatRead.query.all()]
    }

    buffer = BytesIO()
    buffer.write(json.dumps(backup_data, indent=4).encode('utf-8'))
    buffer.seek(0)
    
    filename = f"l8testudy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/json')

@api_bp.route('/admin/restore', methods=['POST'])
@login_required
def import_restore():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    try:
        data = json.load(file)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Invalid JSON: {str(e)}'}), 400

    try:
        # Clear existing data in correct order to avoid FK issues
        db.session.query(TaskChatRead).delete()
        db.session.query(TaskMessage).delete()
        db.session.query(TaskCompletion).delete()
        db.session.query(Grade).delete()
        db.session.query(TaskImage).delete()
        db.session.query(Task).delete()
        db.session.query(Event).delete()
        db.session.query(NotificationSetting).delete()
        db.session.query(PushSubscription).delete()
        db.session.execute(subject_classes.delete())
        db.session.query(User).delete()
        db.session.query(Subject).delete()
        db.session.query(SchoolClass).delete()
        db.session.query(GlobalSetting).delete()
        db.session.commit()

        # Helper to parse dates
        def parse_val(val):
            if isinstance(val, str) and (len(val) >= 10):
                try: return datetime.fromisoformat(val)
                except: pass
            return val

        # Restore sequence
        for d in data.get('school_classes', []):
            sc = SchoolClass()
            for k, v in d.items(): setattr(sc, k, parse_val(v))
            db.session.add(sc)
        db.session.flush()

        for d in data.get('users', []):
            u = User()
            for k, v in d.items(): setattr(u, k, parse_val(v))
            db.session.add(u)
        db.session.flush()

        for d in data.get('subjects', []):
            s = Subject()
            for k, v in d.items(): setattr(s, k, parse_val(v))
            db.session.add(s)
        db.session.flush()

        for d in data.get('subject_classes', []):
            db.session.execute(subject_classes.insert().values(subject_id=d['subject_id'], class_id=d['class_id']))

        # Remaining models
        for d in data.get('tasks', []):
            t = Task(); [setattr(t, k, parse_val(v)) for k, v in d.items()]
            db.session.add(t)
        for d in data.get('task_completions', []):
            tc = TaskCompletion(); [setattr(tc, k, parse_val(v)) for k, v in d.items()]
            db.session.add(tc)
        for d in data.get('events', []):
            e = Event(); [setattr(e, k, parse_val(v)) for k, v in d.items()]
            db.session.add(e)
        for d in data.get('grades', []):
            g = Grade(); [setattr(g, k, parse_val(v)) for k, v in d.items()]
            db.session.add(g)
        for d in data.get('global_settings', []):
            gs = GlobalSetting(); [setattr(gs, k, parse_val(v)) for k, v in d.items()]
            db.session.add(gs)
        for d in data.get('notification_settings', []):
            ns = NotificationSetting(); [setattr(ns, k, parse_val(v)) for k, v in d.items()]
            db.session.add(ns)
        for d in data.get('task_messages', []):
            tm = TaskMessage(); [setattr(tm, k, parse_val(v)) for k, v in d.items()]
            db.session.add(tm)
        for d in data.get('task_chat_reads', []):
            tcr = TaskChatRead(); [setattr(tcr, k, parse_val(v)) for k, v in d.items()]
            db.session.add(tcr)

        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Restore failed: {str(e)}'}), 500

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

@api_bp.route('/admin/settings/global', methods=['GET'])
@login_required
def get_global_settings():
    if not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    privacy_default = """# Datenschutz & Sicherheit - L8teStudy

L8teStudy ist eine lokal gehostete Anwendung. Alle Daten verbleiben auf Ihrem eigenen Server.

## 1. Datenerhebung und -speicherung
Alle von Ihnen eingegebenen Daten (Benutzername, Aufgaben, Termine, Noten, Bilder) werden ausschließlich in einer lokalen Datenbank auf Ihrem Server gespeichert.

## 2. Keine Datenweitergabe
Es findet keine automatische Übertragung von Daten an externe Server statt (keine Cloud, kein Tracking, keine Analytics).

## 3. WebUntis Integration
Sollten Sie die WebUntis-Synchronisierung nutzen, werden Ihre Zugangsdaten (verschlüsselt) lokal gespeichert und nur zur Kommunikation mit dem offiziellen WebUntis-Server Ihrer Schule verwendet.

## 4. Cookies
Die Anwendung nutzt lediglich technisch notwendige Session-Cookies zur Authentifizierung und zur Speicherung Ihrer Design-Einstellungen (Dunkelmodus).
"""
    imprint_default = "Hinterlegen Sie hier Ihr Impressum im Admin-Bereich."
    
    return jsonify({
        'privacy_policy': GlobalSetting.get('privacy_policy', privacy_default),
        'imprint': GlobalSetting.get('imprint', imprint_default)
    })

@api_bp.route('/admin/settings/global', methods=['POST'])
@login_required
def update_global_settings():
    if not current_user.is_super_admin:
        return jsonify({'success': False}), 403
    
    data = request.json
    if 'privacy_policy' in data:
        GlobalSetting.set('privacy_policy', data['privacy_policy'])
    if 'imprint' in data:
        GlobalSetting.set('imprint', data['imprint'])
    
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
    
    from app.notifications import get_local_now
    from app import scheduler
    return jsonify({
        'notify_new_task': settings.notify_new_task,
        'notify_new_event': settings.notify_new_event,
        'notify_chat_message': settings.notify_chat_message,
        'reminder_homework': settings.reminder_homework,
        'reminder_exam': settings.reminder_exam,
        'server_time': get_local_now().strftime("%H:%M"),
        'scheduler_running': scheduler.running
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
    if 'notify_chat_message' in data:
        settings.notify_chat_message = bool(data['notify_chat_message'])
    
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
    class_id = request.args.get('class_id')
    if current_user.is_super_admin:
        if class_id:
            from .models import SchoolClass
            subjects = Subject.query.join(Subject.classes).filter(SchoolClass.id == class_id).order_by(Subject.name).all()
        else:
            subjects = Subject.query.order_by(Subject.name).all()
    else:
        from .models import SchoolClass
        if not current_user.class_id:
            subjects = Subject.query.filter(~Subject.classes.any()).order_by(Subject.name).all()
        else:
            subjects = Subject.query.filter(
                (Subject.classes.any(id=current_user.class_id)) | 
                (~Subject.classes.any())
            ).order_by(Subject.name).all()
        
    if not subjects and not class_id and current_user.is_super_admin:
       defaults = ['Mathematik', 'Deutsch', 'Englisch', 'Physik', 'Biologie', 'Geschichte', 'Kunst', 'Sport', 'Chemie', 'Religion']
       return jsonify([{'id': i, 'name': n, 'class_names': []} for i, n in enumerate(defaults)])
       
    return jsonify([{
        'id': s.id, 
        'name': s.name, 
        'class_names': [c.name for c in s.classes]
    } for s in subjects])

@api_bp.route('/subjects', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin and not current_user.is_super_admin:
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
        'user_count': c.users.count(),
        'chat_enabled': c.chat_enabled
    } for c in classes])

@api_bp.route('/admin/classes/<int:id>', methods=['GET'])
@login_required
def get_class(id):
    if not current_user.is_super_admin and current_user.class_id != id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    from .models import SchoolClass
    school_class = SchoolClass.query.get_or_404(id)
    return jsonify({
        'id': school_class.id,
        'name': school_class.name,
        'code': school_class.code,
        'chat_enabled': school_class.chat_enabled
    })

@api_bp.route('/admin/classes/<int:id>', methods=['PUT'])
@login_required
def update_class(id):
    if not current_user.is_super_admin:
        # Check if they are admin of this class
        if not (current_user.is_admin and current_user.class_id == id):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
            
    data = request.json
    from .models import SchoolClass
    school_class = SchoolClass.query.get_or_404(id)
    
    if 'name' in data and current_user.is_super_admin:
        school_class.name = data['name']
    if 'code' in data:
        new_code = data['code'].upper().strip()
        # Check if code already exists
        existing = SchoolClass.query.filter_by(code=new_code).first()
        if existing and existing.id != id:
            return jsonify({'success': False, 'message': 'Code bereits vergeben'}), 400
        school_class.code = new_code
    
    if 'chat_enabled' in data:
        school_class.chat_enabled = bool(data['chat_enabled'])
        
    db.session.commit()
    return jsonify({'success': True})

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

# --- Untis Routes ---
@api_bp.route('/untis/config', methods=['GET'])
@login_required
def get_untis_config():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    from .models import UntisCredential
    creds = UntisCredential.query.all()
    results = []
    for c in creds:
        results.append({
            'id': c.id,
            'class_id': c.class_id,
            'class_name': c.school_class.name,
            'server': c.server,
            'school': c.school,
            'username': c.username,
            'untis_class_name': c.untis_class_name
        })
    return jsonify(results)

@api_bp.route('/untis/config', methods=['POST'])
@login_required
def set_untis_config():
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.json
    class_id = data.get('class_id')
    server = data.get('server')
    school = data.get('school')
    username = data.get('username')
    password = data.get('password')
    untis_class_name = data.get('untis_class_name')
    
    if not all([class_id, server, school, username, password, untis_class_name]):
        return jsonify({'success': False, 'message': 'Missing data'}), 400
        
    from .models import UntisCredential
    creds = UntisCredential.query.filter_by(class_id=class_id).first()
    if not creds:
        creds = UntisCredential(class_id=class_id)
        db.session.add(creds)
        
    creds.server = server
    creds.school = school
    creds.username = username
    creds.set_password(password)
    creds.untis_class_name = untis_class_name
    
    db.session.commit()
    return jsonify({'success': True})

@api_bp.route('/untis/schedule', methods=['GET'])
@login_required
def get_untis_schedule():
    target_class_id = request.args.get('class_id') or current_user.class_id
    if not target_class_id:
        return jsonify({'success': False, 'message': 'No class selected'}), 400
        
    from .models import UntisCredential
    creds = UntisCredential.query.filter_by(class_id=target_class_id).first()
    if not creds:
        return jsonify({'success': False, 'message': 'Untis not configured for this class'}), 404
        
    try:
        # Clean server URL (remove https:// if present)
        server_url = creds.server.strip().replace('https://', '').replace('http://', '').split('/')[0]
        school_name = creds.school.strip()
        
        print(f"DEBUG: Attempting Untis login to {server_url} for school {school_name} with user {creds.username}")
        
        s = webuntis.Session(
            server=server_url,
            username=creds.username,
            password=creds.get_password(),
            school=school_name,
            useragent='L8teStudy'
        )
        
        try:
            s.login()
        except webuntis.errors.RemoteError as e:
            # Re-raise with more context
            error_text = str(e)
            if "Request ID" in error_text:
                return jsonify({'success': False, 'message': 'Untis-Fehler: Der Server hat ungültig geantwortet. Das passiert meistens, wenn der SCHULNAME oder der SERVER falsch ist (Groß-/Kleinschreibung prüfen!)'}), 500
            raise e
        
        # Find class
        untis_class = None
        all_klassen = s.klassen()
        for c in all_klassen:
            if c.name.lower() == creds.untis_class_name.lower():
                untis_class = c
                break
        
        if not untis_class:
            s.logout()
            # Show the first few available classes to help the user find the right name
            avail = ", ".join([k.name for k in all_klassen[:15]])
            return jsonify({'success': False, 'message': f'Klasse "{creds.untis_class_name}" nicht gefunden. Verfügbar sind z.B.: {avail}'}), 404
            
        # Target Date
        date_param = request.args.get('date')
        if date_param:
            try:
                base_date = date.fromisoformat(date_param.split('T')[0])
            except:
                base_date = date.today()
        else:
            base_date = date.today()

        monday = base_date - timedelta(days=base_date.weekday())
        friday = monday + timedelta(days=6)
        
        # Fetch timetable
        # The library expects 'klasse' (German) as the keyword for classes
        timetable_data = s.timetable(klasse=untis_class, start=monday, end=friday)
        
        results = []
        for period in timetable_data:
            results.append({
                'id': period.id,
                'start': period.start.isoformat(),
                'end': period.end.isoformat(),
                'subjects': [{'name': sub.name, 'long_name': sub.long_name} for sub in period.subjects],
                'teachers': [{'name': t.name, 'long_name': t.long_name} for t in period.teachers],
                'rooms': [{'name': r.name, 'long_name': r.long_name} for r in period.rooms],
                'code': period.code,
                'substText': getattr(period, 'substText', "")
            })
            
        s.logout()
        return jsonify({'success': True, 'timetable': results})
        
    except webuntis.errors.RemoteError as e:
        return jsonify({'success': False, 'message': f'Untis Remote-Fehler: {str(e)}'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Allgemeiner Fehler: {str(e)}'}), 500


@api_bp.route('/untis/import-subjects', methods=['POST'])
@login_required
def import_subjects_from_untis():
    """Import subjects from WebUntis timetable"""
    try:
        data = request.get_json()
        class_id = data.get('class_id')
        
        from .models import UntisCredential, SchoolClass
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Klassen-ID fehlt'}), 400
        
        # Check permissions
        if not current_user.is_super_admin and current_user.class_id != class_id:
            return jsonify({'success': False, 'message': 'Keine Berechtigung'}), 403
        
        # Get Untis credentials
        creds = UntisCredential.query.filter_by(class_id=class_id).first()
        if not creds:
            return jsonify({'success': False, 'message': 'Keine Untis-Konfiguration gefunden'}), 404
        
        # Clean server URL
        server = creds.server.replace('https://', '').replace('http://', '').strip('/')
        
        # Connect to WebUntis
        s = webuntis.Session(
            server=server,
            school=creds.school,
            username=creds.username,
            password=creds.get_password(),
            useragent='L8teStudy'
        )
        s.login()
        
        # Get all classes to find the correct one
        klassen = s.klassen()
        untis_class = None
        for k in klassen:
            if k.name.lower() == creds.untis_class_name.lower():
                untis_class = k
                break
        
        if not untis_class:
            s.logout()
            return jsonify({'success': False, 'message': f'Klasse "{creds.untis_class_name}" nicht gefunden'}), 404
        
        # Fetch timetable for current week and NEXT week to get all subjects
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        # End of next week (Friday of next week + some buffer)
        end_date = monday + timedelta(days=13) 
        
        timetable_data = s.timetable(klasse=untis_class, start=monday, end=end_date)
        
        # Extract unique subjects
        subject_names = set()
        for period in timetable_data:
            if hasattr(period, 'subjects') and period.subjects:
                for subj in period.subjects:
                    # Prefer long_name (full name) over short name
                    full_name = getattr(subj, 'long_name', None) or getattr(subj, 'name', None)
                    if full_name:
                        subject_names.add(full_name)
        
        s.logout()
        
        # Import subjects into database
        school_class = SchoolClass.query.get(class_id)
        if not school_class:
            return jsonify({'success': False, 'message': 'Klasse nicht gefunden'}), 404
        
        imported_count = 0
        skipped_count = 0
        
        for subject_name in subject_names:
            # Check if subject already exists for this class (via relationship)
            existing = Subject.query.filter(
                Subject.name == subject_name,
                Subject.classes.any(id=class_id)
            ).first()
            
            if not existing:
                # Check if subject already exists globally/for other class
                global_subject = Subject.query.filter_by(name=subject_name).first()
                if global_subject:
                    # Link existing subject to this class
                    global_subject.classes.append(school_class)
                    imported_count += 1
                else:
                    # Create new and link
                    new_subject = Subject(name=subject_name)
                    new_subject.classes.append(school_class)
                    db.session.add(new_subject)
                    imported_count += 1
            else:
                skipped_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'total': len(subject_names),
            'message': f'{imported_count} Fächer importiert, {skipped_count} bereits vorhanden'
        })
        
    except webuntis.errors.RemoteError as e:
        return jsonify({'success': False, 'message': f'Untis-Fehler: {str(e)}'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Fehler: {str(e)}'}), 500


@api_bp.route('/untis/current-subject', methods=['GET'])
@login_required
def get_current_subject_from_untis():
    """Get the current or last subject from WebUntis timetable"""
    try:
        class_id = request.args.get('class_id')
        
        from .models import UntisCredential
        
        if not class_id:
            return jsonify({'success': False, 'message': 'Klassen-ID fehlt'}), 400
        
        # Check permissions
        if not current_user.is_super_admin and current_user.class_id != int(class_id):
            return jsonify({'success': False, 'message': 'Keine Berechtigung'}), 403
        
        # Get Untis credentials
        creds = UntisCredential.query.filter_by(class_id=class_id).first()
        if not creds:
            return jsonify({'success': False, 'subject': None})
        
        # Clean server URL
        server = creds.server.replace('https://', '').replace('http://', '').strip('/')
        
        # Connect to WebUntis
        s = webuntis.Session(
            server=server,
            school=creds.school,
            username=creds.username,
            password=creds.get_password(),
            useragent='L8teStudy'
        )
        s.login()
        
        # Get class
        klassen = s.klassen()
        untis_class = None
        for k in klassen:
            if k.name.lower() == creds.untis_class_name.lower():
                untis_class = k
                break
        
        if not untis_class:
            s.logout()
            return jsonify({'success': False, 'subject': None})
        
        # Get today's timetable
        today = date.today()
        timetable_data = s.timetable(klasse=untis_class, start=today, end=today)
        
        s.logout()
        
        # Find current or last period
        from datetime import datetime
        now = datetime.now()
        current_time = now.time()
        
        current_subject_name = None
        last_subject_name = None
        last_end_time = None
        
        for period in timetable_data:
            if not hasattr(period, 'subjects') or not period.subjects:
                continue
            
            # Helper to safely get naive time from potentially aware datetime
            def get_naive_time(dt):
                if hasattr(dt, 'time'):
                    # If it has timezone info, convert to local first (conceptually) or just drop it if we assume local
                    # But if we assume standard WebUntis usage, it's often naive local. 
                    # If aware, we should be careful. 
                    # Assuming basic naive comparison is desired as per project scope.
                    # But let's strip tzinfo just in case to avoid type errors
                    return dt.time()
                return dt
            
            period_start = get_naive_time(period.start)
            period_end = get_naive_time(period.end)
            
            # Check if currently in this period
            if period_start <= current_time <= period_end:
                if period.subjects:
                    subj = period.subjects[0]
                    current_subject_name = getattr(subj, 'long_name', None) or getattr(subj, 'name', None)
                break
            
            # Track last completed period
            if period_end < current_time:
                if last_end_time is None or period_end > last_end_time:
                    last_end_time = period_end
                    if period.subjects:
                        subj = period.subjects[0]
                        last_subject_name = getattr(subj, 'long_name', None) or getattr(subj, 'name', None)
        
        # Return current subject or last subject
        suggested_name = current_subject_name or last_subject_name
        suggested_subject_data = None

        if suggested_name:
            # Try to find the subject in our database for this class
            subject_obj = Subject.query.filter(
                Subject.name == suggested_name,
                Subject.classes.any(id=class_id)
            ).first()
            
            if subject_obj:
                suggested_subject_data = {
                    'id': subject_obj.id,
                    'name': subject_obj.name
                }
            else:
                # If not found in DB, still return name but ID is None
                suggested_subject_data = {
                    'id': None,
                    'name': suggested_name
                }
        
        return jsonify({
            'success': True,
            'subject': suggested_subject_data,
            'is_current': current_subject_name is not None
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'subject': None})

# --- Subject Mapping Routes ---

@api_bp.route('/subject-mappings', methods=['GET'])
@login_required
def get_subject_mappings():
    """Get all subject mappings for the current user's class"""
    try:
        from .models import SubjectMapping
        
        # Get class-specific and global mappings
        mappings = SubjectMapping.query.filter(
            db.or_(
                db.and_(
                    SubjectMapping.class_id == current_user.class_id,
                    SubjectMapping.is_global == True
                ),
                db.and_(
                    SubjectMapping.user_id == current_user.id,
                    SubjectMapping.is_global == False
                )
            )
        ).all()
        
        results = []
        for m in mappings:
            results.append({
                'id': m.id,
                'informal_name': m.informal_name,
                'subject_id': m.subject_id,
                'subject_name': m.official_subject.name if m.official_subject else None,
                'is_global': m.is_global,
                'is_own': m.user_id == current_user.id,
                'created_at': m.created_at.isoformat()
            })
        
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in get_subject_mappings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/subject-mappings', methods=['POST'])
@login_required
def create_subject_mapping():
    """Create a new subject mapping"""
    try:
        from .models import SubjectMapping
        
        data = request.json
        informal_name = data.get('informal_name', '').strip()
        subject_id = data.get('subject_id')
        is_global = data.get('is_global', False)
        
        if not informal_name or not subject_id:
            return jsonify({'success': False, 'message': 'Informal name and subject are required'}), 400
        
        # Only admins can create global mappings
        if is_global and not current_user.is_admin:
            is_global = False
        
        # Check if mapping already exists
        existing = SubjectMapping.query.filter_by(
            informal_name=informal_name,
            class_id=current_user.class_id if is_global else None,
            user_id=None if is_global else current_user.id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Mapping already exists'}), 400
        
        # Create new mapping
        mapping = SubjectMapping(
            informal_name=informal_name,
            subject_id=subject_id,
            class_id=current_user.class_id if is_global else None,
            user_id=None if is_global else current_user.id,
            is_global=is_global
        )
        
        db.session.add(mapping)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': mapping.id,
            'informal_name': mapping.informal_name,
            'subject_id': mapping.subject_id,
            'subject_name': mapping.official_subject.name,
            'is_global': mapping.is_global
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/subject-mappings/<int:id>', methods=['PUT'])
@login_required
def update_subject_mapping(id):
    """Update an existing subject mapping"""
    try:
        from .models import SubjectMapping
        
        mapping = SubjectMapping.query.get_or_404(id)
        
        # Permission check
        if mapping.is_global and not current_user.is_admin:
            return jsonify({'success': False, 'message': 'No permission'}), 403
        if not mapping.is_global and mapping.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'No permission'}), 403
        
        data = request.json
        
        if 'informal_name' in data:
            mapping.informal_name = data['informal_name'].strip()
        if 'subject_id' in data:
            mapping.subject_id = data['subject_id']
        if 'is_global' in data and current_user.is_admin:
            mapping.is_global = data['is_global']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': mapping.id,
            'informal_name': mapping.informal_name,
            'subject_id': mapping.subject_id,
            'subject_name': mapping.official_subject.name,
            'is_global': mapping.is_global
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/subject-mappings/<int:id>', methods=['DELETE'])
@login_required
def delete_subject_mapping(id):
    """Delete a subject mapping"""
    try:
        from .models import SubjectMapping
        
        mapping = SubjectMapping.query.get_or_404(id)
        
        # Permission check
        if mapping.is_global and not current_user.is_admin:
            return jsonify({'success': False, 'message': 'No permission'}), 403
        if not mapping.is_global and mapping.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'No permission'}), 403
        
        db.session.delete(mapping)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/subject-mappings/resolve', methods=['POST'])
@login_required
def resolve_subject_mapping():
    """Resolve an informal folder name to an official subject"""
    try:
        from .models import SubjectMapping
        
        data = request.json
        informal_name = data.get('informal_name', '').strip()
        
        if not informal_name:
            return jsonify({'success': False, 'message': 'Informal name required'}), 400
        
        # Try exact match first (case-insensitive)
        mapping = SubjectMapping.query.filter(
            db.func.lower(SubjectMapping.informal_name) == informal_name.lower(),
            db.or_(
                db.and_(
                    SubjectMapping.class_id == current_user.class_id,
                    SubjectMapping.is_global == True
                ),
                db.and_(
                    SubjectMapping.user_id == current_user.id,
                    SubjectMapping.is_global == False
                )
            )
        ).first()
        
        if mapping:
            return jsonify({
                'success': True,
                'subject_id': mapping.subject_id,
                'subject_name': mapping.official_subject.name,
                'mapping_id': mapping.id,
                'match_type': 'exact'
            })
        
        # Try fuzzy matching with available subjects
        subjects = Subject.query.filter(
            Subject.classes.any(id=current_user.class_id)
        ).all()
        
        # Simple fuzzy matching based on substring and similarity
        best_match = None
        best_score = 0
        
        for subject in subjects:
            subject_name_lower = subject.name.lower()
            informal_lower = informal_name.lower()
            
            # Check if informal name is contained in subject name or vice versa
            if informal_lower in subject_name_lower or subject_name_lower in informal_lower:
                score = len(informal_lower) / max(len(subject_name_lower), 1)
                if score > best_score:
                    best_score = score
                    best_match = subject
        
        if best_match and best_score > 0.3:  # Threshold for suggestion
            return jsonify({
                'success': True,
                'subject_id': best_match.id,
                'subject_name': best_match.name,
                'match_type': 'fuzzy',
                'confidence': best_score
            })
        
        return jsonify({
            'success': False,
            'message': 'No matching subject found',
            'suggestions': [{'id': s.id, 'name': s.name} for s in subjects[:5]]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in resolve_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Drive Integration API ---

@api_bp.route('/drive/folders', methods=['GET'])
@login_required
def get_drive_folders():
    """Get relevant Drive folders based on role"""
    try:
        from .models import DriveFolder, User
        
        # Check if requesting admin view (for Admin Panel)
        is_admin_view = request.args.get('admin_view', 'false').lower() == 'true'
        
        if is_admin_view and (current_user.is_admin or current_user.is_super_admin):
            # Admin Panel View: See all relevant folders
            if current_user.is_super_admin:
                folders = DriveFolder.query.all()
            else:
                folders = DriveFolder.query.join(User).filter(User.class_id == current_user.class_id).all()
        else:
            # Personal Drive View: Only own folders or explicitly public/shared ones?
            # Currently L8teStudy logic seems to be: Drive Tab = Your synced folders.
            # Files Tab = All accessible files (yours + public).
            folders = DriveFolder.query.filter_by(user_id=current_user.id).all()
        
        results = []
        for folder in folders:
            # Determine subject name: folder.subject.name > folder.folder_name
            actual_subject_name = folder.subject.name if folder.subject else folder.folder_name
            
            results.append({
                'id': folder.id,
                'folder_id': folder.folder_id,
                'folder_name': folder.folder_name,
                'subject_id': folder.subject_id,
                'subject_name': actual_subject_name,
                'privacy_level': folder.privacy_level,
                'sync_enabled': folder.sync_enabled,
                'sync_status': folder.sync_status,
                'sync_error': folder.sync_error,
                'last_sync_at': folder.last_sync_at.isoformat() if folder.last_sync_at else None,
                'file_count': folder.files.count(),
                'owner_name': folder.user.username if folder.user else 'System',
                'is_root': folder.is_root,
                'parent_id': folder.parent_id
            })
        
        return jsonify(results)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_drive_folders: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/folders/<int:id>/children', methods=['GET'])
@login_required
def get_drive_folder_children(id):
    """List subfolders of a root folder from Google Drive (supports deep browsing)"""
    try:
        from .models import DriveFolder
        folder = DriveFolder.query.get_or_404(id)
        
        # Check permissions
        can_view = folder.user_id == current_user.id or current_user.is_super_admin
        if not can_view and current_user.is_admin:
            if folder.user and folder.user.class_id == current_user.class_id:
                can_view = True
        
        if not can_view:
            return jsonify({'error': 'Not authorized'}), 403
            
        target_folder_id = request.args.get('folder_id')

        from .drive_sync import get_drive_sync_service
        sync_service = get_drive_sync_service()
        children = sync_service.list_subfolders(id, google_folder_id=target_folder_id)
        return jsonify(children)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/folders/<int:id>/subfolders', methods=['POST'])
@login_required
def toggle_drive_subfolder(id):
    """Enable or disable sync for a subfolder of an authorized root"""
    try:
        from .models import DriveFolder
        root_folder = DriveFolder.query.get_or_404(id)
        
        # Check permissions
        can_manage = root_folder.user_id == current_user.id or current_user.is_super_admin
        if not can_manage and current_user.is_admin:
            if root_folder.user and root_folder.user.class_id == current_user.class_id:
                can_manage = True
        
        if not can_manage:
            return jsonify({'error': 'Not authorized'}), 403
            
        data = request.get_json()
        sub_folder_id = data.get('folder_id') # Google ID
        enabled = data.get('enabled', True)
        privacy = data.get('privacy_level', 'private')
        subject_id = data.get('subject_id')
        
        from .drive_sync import get_drive_sync_service
        sync_service = get_drive_sync_service()
        
        if enabled:
            # Create a sync target folder
            new_folder = sync_service.add_folder(
                user_id=root_folder.user_id,
                folder_id=sub_folder_id,
                privacy_level=privacy,
                is_root=False,
                parent_id=root_folder.id,
                subject_id=subject_id
            )
            return jsonify({'success': True, 'id': new_folder.id})
        else:
            # Find and delete the sync target
            target = DriveFolder.query.filter_by(
                user_id=root_folder.user_id, 
                folder_id=sub_folder_id,
                is_root=False
            ).first()
            if target:
                # Use common delete logic
                return delete_drive_folder(target.id)
            return jsonify({'success': True, 'message': 'Target not found or already deleted'})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/admin/users', methods=['GET'])
@login_required
def get_drive_admin_users():
    """Get all users for Drive folder assignment (Admin only)"""
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'error': 'Admin only'}), 403
        
    try:
        from .models import User
        # Filter by class if not super admin
        query = User.query
        if not current_user.is_super_admin:
            query = query.filter_by(class_id=current_user.class_id)
            
        users = query.all()
        return jsonify([{
            'id': u.id,
            'username': u.username,
            'display_name': u.display_name if hasattr(u, 'display_name') else u.username
        } for u in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/folders', methods=['POST'])
@login_required
def add_drive_folder():
    """Add a new Drive folder (Admin only)"""
    if not current_user.is_admin and not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Nur Administratoren können neue Ordner hinzufügen'}), 403
        
    try:
        data = request.get_json()
        
        if not data or not data.get('folder_id'):
            return jsonify({'success': False, 'message': 'folder_id is required'}), 400
        
        folder_id = data['folder_id'].strip()
        privacy_level = data.get('privacy_level', 'private')
        target_user_id = data.get('user_id', current_user.id)
        
        if privacy_level not in ['private', 'public']:
            return jsonify({'success': False, 'message': 'Invalid privacy_level'}), 400
            
        # Optional: Check if target user is in the same class (if not super admin)
        if not current_user.is_super_admin:
            from .models import User
            target_user = User.query.get(target_user_id)
            if not target_user or target_user.class_id != current_user.class_id:
                return jsonify({'success': False, 'message': 'Ungültiger Benutzer oder falsche Klasse'}), 400
        
        # Add folder as ROOT using sync service
        from .drive_sync import get_drive_sync_service
        
        sync_service = get_drive_sync_service()
        folder = sync_service.add_folder(
            user_id=target_user_id,
            folder_id=folder_id,
            privacy_level=privacy_level,
            is_root=True # Admins add sources/roots
        )
        
        return jsonify({
            'success': True,
            'folder': {
                'id': folder.id,
                'folder_id': folder.folder_id,
                'folder_name': folder.folder_name,
                'privacy_level': folder.privacy_level,
                'sync_status': folder.sync_status,
                'user_id': folder.user_id
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in add_drive_folder: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400


@api_bp.route('/drive/folders/<int:id>', methods=['PATCH'])
@login_required
def update_drive_folder(id):
    """Update Drive folder settings"""
    try:
        from .models import DriveFolder
        
        folder = DriveFolder.query.get_or_404(id)
        
        # Check permissions
        can_edit = folder.user_id == current_user.id or current_user.is_super_admin
        if not can_edit and current_user.is_admin:
            if folder.user and folder.user.class_id == current_user.class_id:
                can_edit = True
                
        if not can_edit:
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        data = request.get_json()
        
        if 'privacy_level' in data:
            if data['privacy_level'] not in ['private', 'public']:
                return jsonify({'success': False, 'message': 'Invalid privacy_level'}), 400
            folder.privacy_level = data['privacy_level']
        
        if 'sync_enabled' in data:
            folder.sync_enabled = bool(data['sync_enabled'])
            
        if 'folder_name' in data:
            folder.folder_name = data['folder_name']
            
        if 'subject_id' in data:
            folder.subject_id = data['subject_id']

        if 'user_id' in data:
            # Only admin/super_admin can reassign users
            if not current_user.is_admin and not current_user.is_super_admin:
                return jsonify({'success': False, 'message': 'Nur Administratoren können den Besitzer ändern'}), 403
            
            new_user_id = data['user_id']
            from .models import User
            new_user = User.query.get(new_user_id)
            
            if not new_user:
                 return jsonify({'success': False, 'message': 'Benutzer nicht gefunden'}), 404

            # Permission check: can I manage this new user?
            if not current_user.is_super_admin:
                 if new_user.class_id != current_user.class_id:
                      return jsonify({'success': False, 'message': 'Benutzer gehört nicht zu Ihrer Klasse'}), 403

            # Check for uniqueness violation
            existing = DriveFolder.query.filter_by(user_id=new_user_id, folder_id=folder.folder_id).first()
            if existing and existing.id != folder.id:
                 return jsonify({'success': False, 'message': 'Dieser Benutzer hat diesen Ordner bereits verknüpft'}), 400

            # Re-encrypt files if user changes
            if folder.user_id != new_user_id:
                old_user_id = folder.user_id
                try:
                    from .drive_encryption import get_drive_encryption_manager
                    encryption_manager = get_drive_encryption_manager()
                    
                    # Iterate through all files and re-encrypt
                    # Note: folder.files is dynamic lazy loader
                    files = folder.files.all() if hasattr(folder.files, 'all') else folder.files
                    
                    for file in files:
                        try:
                            # 1. Decrypt with OLD metadata
                            old_metadata = {
                                'file_id': file.file_id,
                                'filename': file.filename,
                                'user_id': old_user_id,
                                'folder_id': folder.folder_id,
                                'file_hash': file.file_hash
                            }
                            
                            plaintext = encryption_manager.decrypt_file_to_memory(
                                file.encrypted_path,
                                metadata=old_metadata
                            )
                            
                            # 2. Encrypt with NEW metadata
                            new_metadata = {
                                'file_id': file.file_id,
                                'filename': file.filename,
                                'user_id': new_user_id,
                                'folder_id': folder.folder_id,
                                'file_hash': file.file_hash
                            }
                            
                            # Overwrite file with new encryption
                            encryption_manager.encrypt_and_store_bytes(
                                plaintext,
                                file.file_id,
                                metadata=new_metadata
                            )
                        except Exception as e:
                            current_app.logger.error(f"Failed to re-encrypt file {file.id}: {e}")
                            # Continue with other files... 
                except Exception as e:
                     current_app.logger.error(f"Major error during folder transfer: {e}")

            folder.user_id = new_user_id
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in update_drive_folder: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400


@api_bp.route('/drive/folders/<int:id>', methods=['DELETE'])
@login_required
def delete_drive_folder(id):
    """Delete a Drive folder and all its files"""
    try:
        from .models import DriveFolder
        
        folder = DriveFolder.query.get_or_404(id)
        
        # Check permissions
        can_delete = folder.user_id == current_user.id or current_user.is_super_admin
        if not can_delete and current_user.is_admin:
            if folder.user and folder.user.class_id == current_user.class_id:
                can_delete = True
                
        if not can_delete:
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        # Delete encrypted files from disk
        from .drive_encryption import get_drive_encryption_manager
        encryption_manager = get_drive_encryption_manager()
        
        for file in folder.files:
            try:
                encryption_manager.delete_encrypted_file(file.encrypted_path)
            except:
                pass
        
        # Delete from database (cascade will handle files and content)
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_drive_folder: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/drive/folders/<int:id>/sync', methods=['POST'])
@login_required
def sync_drive_folder(id):
    """Manually trigger sync for a folder"""
    try:
        from .models import DriveFolder
        
        folder = DriveFolder.query.get_or_404(id)
        
        # Check permissions
        can_sync = folder.user_id == current_user.id or current_user.is_super_admin
        if not can_sync and current_user.is_admin:
            if folder.user and folder.user.class_id == current_user.class_id:
                can_sync = True
                
        if not can_sync:
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        # Trigger sync
        from .drive_sync import get_drive_sync_service
        
        sync_service = get_drive_sync_service()
        stats = sync_service.sync_folder(id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in sync_drive_folder: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


@api_bp.route('/drive/files', methods=['GET'])
@login_required
def get_drive_files():
    """Get Drive files with optional filters"""
    try:
        from .models import DriveFile, DriveFolder
        
        # Get query parameters
        folder_id = request.args.get('folder_id', type=int)
        subject_id = request.args.get('subject_id', type=int)
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = db.session.query(DriveFile).join(DriveFolder)
        
        # Filter by folder
        if folder_id:
            query = query.filter(DriveFile.drive_folder_id == folder_id)
        
        # Filter by subject
        if subject_id:
            query = query.filter(DriveFile.subject_id == subject_id)
        
        # Filter by user (folder owner)
        if user_id:
            query = query.filter(DriveFolder.user_id == user_id)
        else:
            # Default: show own files + public files from class
            query = query.filter(
                db.or_(
                    DriveFolder.user_id == current_user.id,
                    DriveFolder.privacy_level == 'public'
                )
            )
        
        # Order and paginate
        query = query.order_by(DriveFile.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        files = query.all()
        
        results = []
        for file in files:
            results.append({
                'id': file.id,
                'filename': file.filename,
                'file_size': file.file_size,
                'mime_type': file.mime_type,
                'subject_id': file.subject_id,
                'subject_name': file.subject.name if file.subject else None,
                'auto_mapped': file.auto_mapped,
                'ocr_completed': file.ocr_completed,
                'page_count': file.content.page_count if file.content else 0,
                'created_at': file.created_at.isoformat() if file.created_at else None,
                'folder_name': file.folder.folder_name,
                'parent_folder_name': file.parent_folder_name,
                'owner_username': file.folder.user.username,
                'owner_id': file.folder.user_id
            })
        
        return jsonify(results)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_drive_files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/files/<int:id>/download', methods=['GET'])
@login_required
def download_drive_file(id):
    """Download a Drive file (decrypted)"""
    try:
        from .models import DriveFile, DriveFolder
        
        file = DriveFile.query.get_or_404(id)
        folder = file.folder
        
        # Check permissions
        if folder.user_id != current_user.id:
            if folder.privacy_level != 'public':
                return jsonify({'error': 'Not authorized'}), 403
        
        # Decrypt file to memory
        from .drive_encryption import get_drive_encryption_manager
        
        encryption_manager = get_drive_encryption_manager()
        
        metadata = {
            'file_id': file.file_id,
            'filename': file.filename,
            'user_id': folder.user_id,
            'folder_id': folder.folder_id,
            'file_hash': file.file_hash
        }
        
        decrypted_bytes = encryption_manager.decrypt_file_to_memory(
            file.encrypted_path,
            metadata=metadata
        )
        
        # Send file
        inline = request.args.get('inline', 'false').lower() == 'true'
        return send_file(
            BytesIO(decrypted_bytes),
            mimetype=file.mime_type,
            as_attachment=not inline,
            download_name=file.filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in download_drive_file: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/search', methods=['GET'])
@login_required
def search_drive_files():
    """Search Drive files using FTS5"""
    try:
        query = request.args.get('q', '').strip()
        subject_id = request.args.get('subject_id', type=int)
        user_id = request.args.get('user_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if not query:
            return jsonify([])
        
        # Search using FTS5
        from .drive_search import get_drive_search_service
        
        search_service = get_drive_search_service(
            current_user_id=current_user.id,
            class_id=current_user.class_id
        )
        
        results = search_service.search(
            query=query,
            subject_id=subject_id,
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return jsonify(results)
        
    except Exception as e:
        current_app.logger.error(f"Error in search_drive_files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/search/suggestions', methods=['GET'])
@login_required
def get_drive_search_suggestions():
    """Get autocomplete suggestions for search"""
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify([])
        
        from .drive_search import get_drive_search_service
        
        search_service = get_drive_search_service(
            current_user_id=current_user.id
        )
        
        suggestions = search_service.get_suggestions(query, limit=limit)
        
        return jsonify(suggestions)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_drive_search_suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/stats', methods=['GET'])
@login_required
def get_drive_stats():
    """Get Drive statistics"""
    try:
        from .drive_search import get_drive_search_service
        
        search_service = get_drive_search_service(
            current_user_id=current_user.id,
            class_id=current_user.class_id
        )
        
        stats = search_service.get_file_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_drive_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/subject-mappings', methods=['GET'])
@login_required
def get_drive_subject_mappings():
    """Get all subject mappings for the user"""
    try:
        mappings = SubjectMapping.query.filter(
            db.or_(
                SubjectMapping.user_id == current_user.id,
                db.and_(
                    SubjectMapping.is_global == True,
                    SubjectMapping.class_id == current_user.class_id
                )
            )
        ).all()
        
        results = []
        for mapping in mappings:
            results.append({
                'id': mapping.id,
                'informal_name': mapping.informal_name,
                'subject_id': mapping.subject_id,
                'subject_name': mapping.official_subject.name,
                'is_global': mapping.is_global,
                'is_own': mapping.user_id == current_user.id
            })
        
        return jsonify(results)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_drive_subject_mappings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/drive/subject-mappings', methods=['POST'])
@login_required
def create_drive_subject_mapping():
    """Create a new subject mapping"""
    try:
        data = request.get_json()
        
        if not data or not data.get('informal_name') or not data.get('subject_id'):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        informal_name = data['informal_name'].strip()
        subject_id = data['subject_id']
        is_global = data.get('is_global', False)
        
        # Only admins can create global mappings
        if is_global and not current_user.is_admin:
            is_global = False
        
        # Create mapping
        from .subject_mapper import get_subject_mapper
        
        mapper = get_subject_mapper(
            class_id=current_user.class_id,
            user_id=current_user.id
        )
        
        mapping = mapper.create_mapping(
            informal_name=informal_name,
            subject_id=subject_id,
            is_global=is_global
        )
        
        return jsonify({
            'success': True,
            'mapping': {
                'id': mapping.id,
                'informal_name': mapping.informal_name,
                'subject_id': mapping.subject_id,
                'subject_name': mapping.official_subject.name,
                'is_global': mapping.is_global
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in create_drive_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 400


@api_bp.route('/drive/subject-mappings/<int:id>', methods=['DELETE'])
@login_required
def delete_drive_subject_mapping(id):
    """Delete a subject mapping"""
    try:
        mapping = SubjectMapping.query.get_or_404(id)
        
        # Check permissions
        if mapping.user_id != current_user.id and not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Not authorized'}), 403
        
        db.session.delete(mapping)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in delete_drive_subject_mapping: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


