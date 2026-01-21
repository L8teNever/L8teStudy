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


# --- Drive Integration Models ---

class DriveFolder(db.Model):
    """Represents a linked Google Drive folder"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    folder_id = db.Column(db.String(256), nullable=False)  # Google Drive folder ID
    folder_name = db.Column(db.String(256), nullable=False)
    privacy_level = db.Column(db.String(20), default='private')  # 'private' or 'public'
    is_root = db.Column(db.Boolean, default=False)  # Admin-added root source
    parent_id = db.Column(db.Integer, db.ForeignKey('drive_folder.id'), nullable=True)
    sync_enabled = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    sync_status = db.Column(db.String(50), default='pending')
    sync_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='drive_folders')
    files = db.relationship('DriveFile', backref='folder', lazy='dynamic', cascade='all, delete-orphan')
    subfolders = db.relationship('DriveFolder', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    # Ensure unique folder per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'folder_id', name='_user_folder_uc'),
    )


class DriveFile(db.Model):
    """Represents a file synced from Google Drive"""
    id = db.Column(db.Integer, primary_key=True)
    drive_folder_id = db.Column(db.Integer, db.ForeignKey('drive_folder.id'), nullable=False)
    file_id = db.Column(db.String(256), nullable=False)  # Google Drive file ID
    filename = db.Column(db.String(512), nullable=False)
    encrypted_path = db.Column(db.String(512), nullable=False)  # Path to encrypted file on disk
    file_hash = db.Column(db.String(64), nullable=False)  # SHA-256 hash for change detection
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(128), nullable=False)
    
    # Subject mapping (can be auto-detected or manually set)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    auto_mapped = db.Column(db.Boolean, default=False)  # True if auto-detected
    
    # OCR status
    ocr_completed = db.Column(db.Boolean, default=False)
    ocr_error = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='drive_files')
    content = db.relationship('DriveFileContent', backref='file', uselist=False, cascade='all, delete-orphan')
    
    # Ensure unique file per folder
    __table_args__ = (
        db.UniqueConstraint('drive_folder_id', 'file_id', name='_folder_file_uc'),
    )


class DriveFileContent(db.Model):
    """Stores OCR-extracted text content for full-text search"""
    id = db.Column(db.Integer, primary_key=True)
    drive_file_id = db.Column(db.Integer, db.ForeignKey('drive_file.id'), nullable=False, unique=True)
    content_text = db.Column(db.Text, nullable=False)  # Extracted text
    page_count = db.Column(db.Integer, default=0)
    ocr_completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For FTS5 search, we'll create a virtual table separately
    # This model just stores the raw content
