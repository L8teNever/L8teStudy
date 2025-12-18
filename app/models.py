from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    dark_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
    # Daily Reminders (Time stored as string "HH:MM", null means deactivated)
    reminder_homework = db.Column(db.String(5), nullable=True) # e.g. "17:00" for tasks due tomorrow
    reminder_exam = db.Column(db.String(5), nullable=True) # e.g. "19:00" for exams due soon

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
    title = db.Column(db.String(128), nullable=False)
    subject = db.Column(db.String(64))
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
    title = db.Column(db.String(128), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    deleted_at = db.Column(db.DateTime, nullable=True)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, default=1.0) # e.g., 0.5 for written, 1.0 for exam
    title = db.Column(db.String(128))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(256), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
