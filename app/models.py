from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

def generate_class_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Junction table for subjects shared between classes
subject_classes = db.Table('subject_classes',
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('school_class.id'), primary_key=True)
)

class SchoolClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(6), unique=True, nullable=False, default=generate_class_code)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chat_enabled = db.Column(db.Boolean, default=False)

    users = db.relationship('User', backref='school_class', lazy='dynamic')
    tasks = db.relationship('Task', backref='school_class', lazy='dynamic')
    events = db.relationship('Event', backref='school_class', lazy='dynamic')
    # Use relationship through junction table for shared subjects
    audit_logs = db.relationship('AuditLog', backref='school_class', lazy='dynamic')



class UserRole:
    STUDENT = 'student'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default=UserRole.STUDENT)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True) # Super admins don't need a class
    dark_mode = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(5), default='de')
    needs_password_change = db.Column(db.Boolean, default=True) # Forced for new users
    has_seen_tutorial = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_admin(self):
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    tasks = db.relationship('Task', backref='author', lazy='dynamic')
    events = db.relationship('Event', backref='author', lazy='dynamic')
    grades = db.relationship('Grade', backref='author', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='author', lazy='dynamic')
    
    # Notification Settings Relation
    notification_settings = db.relationship('NotificationSetting', backref='user', uselist=False, cascade="all, delete-orphan")
    push_subscriptions = db.relationship('PushSubscription', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class NotificationSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Notify when OTHER users create new content
    notify_new_task = db.Column(db.Boolean, default=True)
    notify_new_event = db.Column(db.Boolean, default=True)
    notify_chat_message = db.Column(db.Boolean, default=True)
    
    # Daily Reminders (Time stored as string "HH:MM", null means deactivated)
    reminder_homework = db.Column(db.String(5), nullable=True) # e.g. "17:00" for tasks due tomorrow
    reminder_exam = db.Column(db.String(5), nullable=True) # e.g. "19:00" for exams due soon
    
    # Tracking to avoid double-sending
    last_homework_reminder_at = db.Column(db.Date, nullable=True)
    last_exam_reminder_at = db.Column(db.Date, nullable=True)

class PushSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    endpoint = db.Column(db.String(512), nullable=False, unique=True)
    auth_key = db.Column(db.String(128))
    p256dh_key = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    is_shared = db.Column(db.Boolean, default=False) # If true, visible to all classes linked to subject_id
    title = db.Column(db.String(128), nullable=False)
    subject = db.Column(db.String(64)) # Legacy/Cache
    due_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    # is_done on Task is deprecated in favor of TaskCompletion table for per-user status
    is_done = db.Column(db.Boolean, default=False) 
    deleted_at = db.Column(db.DateTime, nullable=True)
    images = db.relationship('TaskImage', backref='task', lazy='dynamic')

class TaskImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    filename = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TaskCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    is_done = db.Column(db.Boolean, default=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    is_shared = db.Column(db.Boolean, default=False) 
    title = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    deleted_at = db.Column(db.DateTime, nullable=True)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Note: Grade is private, but we might want to keep class_id here too just in case
    # However it is already linked via user_id -> User -> class_id
    subject = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, default=1.0) # e.g., 0.5 for written, 1.0 for exam
    title = db.Column(db.String(128))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)
    action = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    # New many-to-many relationship
    classes = db.relationship('SchoolClass', secondary=subject_classes, backref='subjects')
    
    tasks = db.relationship('Task', backref='subject_rel', lazy='dynamic')
    events = db.relationship('Event', backref='subject_rel', lazy='dynamic')
    mappings = db.relationship('SubjectMapping', backref='official_subject', lazy='dynamic')

class SubjectMapping(db.Model):
    """Maps informal/messy folder names to official subjects"""
    id = db.Column(db.Integer, primary_key=True)
    informal_name = db.Column(db.String(128), nullable=False)  # e.g., "Ph", "GdT", "Technik"
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)  # Optional: class-specific mapping
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who created this mapping
    is_global = db.Column(db.Boolean, default=False)  # If true, applies to all users in class
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique informal names per scope (global or per-user)
    __table_args__ = (
        db.UniqueConstraint('informal_name', 'class_id', 'user_id', name='_informal_name_scope_uc'),
    )

class TaskMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text)
    message_type = db.Column(db.String(20), default='text') # text, image, file
    file_url = db.Column(db.String(512))
    file_name = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('task_message.id'), nullable=True)

    user = db.relationship('User')
    task = db.relationship('Task', backref='messages')
    parent = db.relationship('TaskMessage', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))

class TaskChatRead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)

class GlobalSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)

    @staticmethod
    def get(key, default=None):
        setting = GlobalSetting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value):
        setting = GlobalSetting.query.filter_by(key=key).first()
        if not setting:
            setting = GlobalSetting(key=key)
            db.session.add(setting)
        setting.value = value
        db.session.commit()

from cryptography.fernet import Fernet
from flask import current_app

class UntisCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=False, unique=True)
    server = db.Column(db.String(256), nullable=False)
    school = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(512), nullable=False) # Increased size for encrypted data
    untis_class_name = db.Column(db.String(64), nullable=False)

    school_class = db.relationship('SchoolClass', backref=db.backref('untis_credentials', uselist=False))

    def set_password(self, password_text):
        if not password_text:
            return
        f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
        self.password = f.encrypt(password_text.encode()).decode()

    def get_password(self):
        if not self.password:
            return ""
        try:
            f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
            return f.decrypt(self.password.encode()).decode()
        except Exception:
            # Fallback for old plain text passwords if decryption fails
            # This is only useful during transition.
            return self.password


# --- Google Drive OAuth Integration Models ---

class DriveOAuthToken(db.Model):
    """Stores Google Drive OAuth tokens (global, shared by all users)"""
    id = db.Column(db.Integer, primary_key=True)
    
    # OAuth tokens (encrypted)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_access_token(self, token_text):
        """Encrypt and store access token"""
        if not token_text:
            return
        from flask import current_app
        f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
        self.access_token = f.encrypt(token_text.encode()).decode()
    
    def get_access_token(self):
        """Decrypt and return access token"""
        if not self.access_token:
            return ""
        try:
            from flask import current_app
            f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
            return f.decrypt(self.access_token.encode()).decode()
        except Exception:
            return self.access_token
    
    def set_refresh_token(self, token_text):
        """Encrypt and store refresh token"""
        if not token_text:
            return
        from flask import current_app
        f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
        self.refresh_token = f.encrypt(token_text.encode()).decode()
    
    def get_refresh_token(self):
        """Decrypt and return refresh token"""
        if not self.refresh_token:
            return ""
        try:
            from flask import current_app
            f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
            return f.decrypt(self.refresh_token.encode()).decode()
        except Exception:
            return self.refresh_token


class DriveFolder(db.Model):
    """Admin-selected folders to display from Google Drive"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Drive folder info
    drive_folder_id = db.Column(db.String(256), nullable=False, unique=True)
    folder_name = db.Column(db.String(500), nullable=False)
    folder_path = db.Column(db.String(1000), nullable=True)  # Full path for display
    
    # Ownership and Hierarchy
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_root = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('drive_folder.id'), nullable=True)
    
    # Subject mapping (optional)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    
    # Settings and Privacy
    privacy_level = db.Column(db.String(20), default='private')
    is_active = db.Column(db.Boolean, default=True) # Legacy UI
    sync_enabled = db.Column(db.Boolean, default=True)
    include_subfolders = db.Column(db.Boolean, default=True)
    
    # Sync Status
    last_sync_at = db.Column(db.DateTime)
    sync_status = db.Column(db.String(50), default='pending')
    sync_error = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Legacy UI
    
    # Relationships
    subject = db.relationship('Subject', backref='drive_folders')
    created_by = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_drive_folders')
    owner = db.relationship('User', foreign_keys=[user_id], backref='owned_drive_folders')
    parent = db.relationship('DriveFolder', remote_side=[id], backref='subfolders')


class DriveFile(db.Model):
    """Stores metadata for Drive files (sync/caching)"""
    id = db.Column(db.Integer, primary_key=True)
    drive_folder_id = db.Column(db.Integer, db.ForeignKey('drive_folder.id'), nullable=True)
    file_id = db.Column(db.String(256), nullable=False, unique=True)
    filename = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(128))
    file_size = db.Column(db.BigInteger)
    file_hash = db.Column(db.String(128))
    encrypted_path = db.Column(db.String(1000))
    parent_folder_name = db.Column(db.String(512))
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    auto_mapped = db.Column(db.Boolean, default=False)
    
    ocr_completed = db.Column(db.Boolean, default=False)
    ocr_error = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='drive_files')


class DriveFileContent(db.Model):
    """Stores OCR-extracted text for FTS search"""
    id = db.Column(db.Integer, primary_key=True)
    drive_file_id = db.Column(db.Integer, db.ForeignKey('drive_file.id'), nullable=False, unique=True)
    content_text = db.Column(db.Text)
    page_count = db.Column(db.Integer, default=0)
    ocr_completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    file = db.relationship('DriveFile', backref=db.backref('content', uselist=False))
