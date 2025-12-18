
import json
import os
import logging
from datetime import datetime, timedelta
from app import db, scheduler
from app.models import User, PushSubscription, NotificationSetting, Task, Event
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

# Default VAPID keys (For testing only! In production, use .env)
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', 'nL5eQ8uX9yZ1...REPLACE_ME...')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', 'BMd...REPLACE_ME...')
VAPID_CLAIMS = {"sub": "mailto:admin@l8testudy.app"}

def send_web_push(subscription_info, message_body):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(message_body),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
    except WebPushException as ex:
        logger.error(f"WebPush failed: {ex}")
        # If 410 Gone, remove subscription
        if ex.response and ex.response.status_code == 410:
            return False
    except Exception as e:
        logger.error(f"WebPush error: {e}")
    return True

def notify_user(user, title, body, url='/'):
    """Sends a notification to a specific user via all their subscriptions"""
    subs = PushSubscription.query.filter_by(user_id=user.id).all()
    payload = {
        "title": title,
        "body": body,
        "icon": "/static/icon-192.png",
        "url": url
    }
    
    for sub in subs:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "p256dh": sub.p256dh_key,
                "auth": sub.auth_key
            }
        }
        success = send_web_push(sub_info, payload)
        if success is False:
            db.session.delete(sub)
    
    db.session.commit()

def notify_new_task(task):
    """Notify all users (except author) that a new task was created"""
    users = User.query.filter(User.id != task.user_id).all()
    for user in users:
        # Check settings
        if not user.notification_settings:
             # Create default settings if missing
             user.notification_settings = NotificationSetting(user_id=user.id)
             db.session.add(user.notification_settings)
             db.session.commit()
        
        if user.notification_settings.notify_new_task:
            notify_user(user, "Neue Aufgabe", f"{task.author.username} hat '{task.title}' erstellt.", url='/tasks')

def notify_new_event(event):
    """Notify all users (except author) that a new event was created"""
    users = User.query.filter(User.id != event.user_id).all()
    for user in users:
        if not user.notification_settings:
             user.notification_settings = NotificationSetting(user_id=user.id)
             db.session.add(user.notification_settings)
             db.session.commit()

        if user.notification_settings.notify_new_event:
            notify_user(user, "Neuer Termin", f"{event.author.username} hat '{event.title}' erstellt.", url='/calendar')

def check_reminders():
    """Scheduled job to check for due tasks and alarms"""
    with scheduler.app.app_context():
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        
        # 1. Check Homework Reminders (e.g. at 17:00 check for tasks due tomorrow)
        users = User.query.all()
        for user in users:
            settings = user.notification_settings
            if not settings: continue
            
            # Homework Reminder
            if settings.reminder_homework == current_time_str:
                tomorrow = (now + timedelta(days=1)).date()
                tasks_due = Task.query.filter(
                    db.func.date(Task.due_date) == tomorrow,
                    Task.deleted_at.is_(None)
                ).all()
                
                count = 0
                for t in tasks_due:
                    # Check if user has NOT finished it
                    # This requires checking TaskCompletion, which we haven't fully implemented in this loop yet
                    # For now just notify about due tasks
                    count += 1
                
                if count > 0:
                    notify_user(user, "Hausaufgaben morgen", f"Du hast {count} Aufgaben für morgen fällig!", url='/tasks')

            # Exam/Event Reminder (Simplification: Check events tomorrow)
            if settings.reminder_exam == current_time_str:
                tomorrow = (now + timedelta(days=1)).date()
                events = Event.query.filter(
                    db.func.date(Event.date) == tomorrow, 
                    Event.deleted_at.is_(None)
                ).all()
                if events:
                    notify_user(user, "Termin/Klausur morgen", f"Morgen: {events[0].title}" + (f" und {len(events)-1} weitere" if len(events)>1 else ""), url='/calendar')

