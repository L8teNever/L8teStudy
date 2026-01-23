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


# --- Paperless-NGX Integration Models ---

class PaperlessConfig(db.Model):
    """Stores Paperless-NGX connection configuration"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Per-user config
    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=True)  # Per-class config
    
    paperless_url = db.Column(db.String(500), nullable=False)  # Base URL of Paperless instance
    api_token = db.Column(db.String(500), nullable=False)  # Encrypted API token
    
    is_active = db.Column(db.Boolean, default=True)
    is_global = db.Column(db.Boolean, default=False)  # If true, applies to entire installation
    
    # Sync settings
    auto_sync_enabled = db.Column(db.Boolean, default=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='paperless_configs')
    school_class = db.relationship('SchoolClass', backref='paperless_config')
    documents = db.relationship('PaperlessDocument', backref='config', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_api_token(self, token_text):
        """Encrypt and store API token"""
        if not token_text:
            return
        from flask import current_app
        f = Fernet(current_app.config['UNTIS_FERNET_KEY'])  # Reuse existing encryption key
        self.api_token = f.encrypt(token_text.encode()).decode()
    
    def get_api_token(self):
        """Decrypt and return API token"""
        if not self.api_token:
            return ""
        try:
            from flask import current_app
            f = Fernet(current_app.config['UNTIS_FERNET_KEY'])
            return f.decrypt(self.api_token.encode()).decode()
        except Exception:
            return self.api_token  # Fallback for unencrypted tokens


class PaperlessDocument(db.Model):
    """Cached metadata for Paperless documents"""
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('paperless_config.id'), nullable=False)
    
    # Paperless document data
    paperless_id = db.Column(db.Integer, nullable=False)  # ID in Paperless
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=True)  # OCR-extracted text from Paperless
    
    # Metadata
    created = db.Column(db.DateTime, nullable=False)  # Document creation date
    modified = db.Column(db.DateTime, nullable=False)  # Last modification in Paperless
    added = db.Column(db.DateTime, nullable=False)  # When added to Paperless
    
    # File info
    original_filename = db.Column(db.String(500), nullable=True)
    archived_filename = db.Column(db.String(500), nullable=True)  # OCR'd version
    mime_type = db.Column(db.String(128), nullable=True)
    
    # Foreign keys to Paperless entities
    correspondent_id = db.Column(db.Integer, db.ForeignKey('paperless_correspondent.id'), nullable=True)
    document_type_id = db.Column(db.Integer, db.ForeignKey('paperless_document_type.id'), nullable=True)
    
    # Subject mapping (L8teStudy specific)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    
    # Cache metadata
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    subject = db.relationship('Subject', backref='paperless_documents')
    correspondent = db.relationship('PaperlessCorrespondent', backref='documents')
    document_type = db.relationship('PaperlessDocumentType', backref='documents')
    tags = db.relationship('PaperlessTag', secondary='paperless_document_tags', backref='documents')
    
    # Ensure unique document per config
    __table_args__ = (
        db.UniqueConstraint('config_id', 'paperless_id', name='_config_document_uc'),
    )


# Junction table for document-tag many-to-many relationship
paperless_document_tags = db.Table('paperless_document_tags',
    db.Column('document_id', db.Integer, db.ForeignKey('paperless_document.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('paperless_tag.id'), primary_key=True)
)


class PaperlessTag(db.Model):
    """Cached Paperless tags"""
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('paperless_config.id'), nullable=False)
    
    paperless_id = db.Column(db.Integer, nullable=False)  # ID in Paperless
    name = db.Column(db.String(128), nullable=False)
    color = db.Column(db.String(7), default='#a6cee3')  # Hex color
    is_inbox_tag = db.Column(db.Boolean, default=False)
    
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    config = db.relationship('PaperlessConfig', backref='tags')
    
    # Ensure unique tag per config
    __table_args__ = (
        db.UniqueConstraint('config_id', 'paperless_id', name='_config_tag_uc'),
    )


class PaperlessCorrespondent(db.Model):
    """Cached Paperless correspondents"""
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('paperless_config.id'), nullable=False)
    
    paperless_id = db.Column(db.Integer, nullable=False)  # ID in Paperless
    name = db.Column(db.String(128), nullable=False)
    
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    config = db.relationship('PaperlessConfig', backref='correspondents')
    
    # Ensure unique correspondent per config
    __table_args__ = (
        db.UniqueConstraint('config_id', 'paperless_id', name='_config_correspondent_uc'),
    )


class PaperlessDocumentType(db.Model):
    """Cached Paperless document types"""
    id = db.Column(db.Integer, primary_key=True)
    config_id = db.Column(db.Integer, db.ForeignKey('paperless_config.id'), nullable=False)
    
    paperless_id = db.Column(db.Integer, nullable=False)  # ID in Paperless
    name = db.Column(db.String(128), nullable=False)
    
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    config = db.relationship('PaperlessConfig', backref='document_types')
    
    # Ensure unique document type per config
    __table_args__ = (
        db.UniqueConstraint('config_id', 'paperless_id', name='_config_doctype_uc'),
    )
