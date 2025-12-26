
import json
import os
import logging
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from app import db, scheduler
from app.models import User, PushSubscription, NotificationSetting, Task, Event
from pywebpush import webpush, WebPushException

def get_local_now():
    """Returns the current time in Europe/Berlin timezone"""
    return datetime.now(ZoneInfo("Europe/Berlin"))

logger = logging.getLogger(__name__)

import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Helper functions for key generation
def int_to_bytes(i, length):
    return i.to_bytes(length, byteorder='big')

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def get_or_create_vapid_keys():
    """
    Retrieves VAPID keys from env, or file, or generates them.
    Returns (private_key, public_key)
    """
    # 1. Check Environment
    priv = os.environ.get('VAPID_PRIVATE_KEY')
    pub = os.environ.get('VAPID_PUBLIC_KEY')
    if priv and pub:
        return priv, pub

    # 2. Check File in instance/data folder (secure storage)
    # Priority: Env Var > /data (Docker volume) > local instance folder
    key_file = os.environ.get('VAPID_KEY_PATH')
    if not key_file:
        if os.path.exists('/data'):
            key_file = '/data/vapid.json'
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            instance_dir = os.path.join(base_dir, 'instance')
            if not os.path.exists(instance_dir):
                os.makedirs(instance_dir, exist_ok=True)
            key_file = os.path.join(instance_dir, 'vapid.json')
    
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r') as f:
                data = json.load(f)
                logger.info(f"VAPID keys loaded from {key_file}")
                return data['private_key'], data['public_key']
        except Exception as e:
            logger.error(f"Failed to load VAPID keys from {key_file}: {e}")
    else:
        logger.info(f"VAPID key file not found at {key_file}, will generate new.")

    # 3. Generate New Keys
    try:
        logger.info("Generating new VAPID keys...")
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()

        # Private Key to Base64URL
        private_val = private_key.private_numbers().private_value
        private_bytes = int_to_bytes(private_val, 32)
        vapid_private = base64url_encode(private_bytes)

        # Public Key to Base64URL (Uncompressed Point)
        numbers = public_key.public_numbers()
        x = int_to_bytes(numbers.x, 32)
        y = int_to_bytes(numbers.y, 32)
        public_bytes = b'\x04' + x + y
        vapid_public = base64url_encode(public_bytes)
        
        # Save to file
        with open(key_file, 'w') as f:
            json.dump({'private_key': vapid_private, 'public_key': vapid_public}, f)
            
        logger.info(f"VAPID keys saved to {key_file}")
        return vapid_private, vapid_public
        
    except Exception as e:
        logger.error(f"Failed to generate VAPID keys: {e}")
        # Fallback (should not happen in prod ideally, but prevents crash)
        return None, None

VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY = get_or_create_vapid_keys()
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
        # If 410 Gone, remove subscription (expired/uninstalled)
        if ex.response and ex.response.status_code == 410:
            return False
        # Other errors (401, 403, 500 etc) are logged but we might keep the sub
    except Exception as e:
        logger.error(f"WebPush error: {e}")
    return True

def notify_user(user, title, body, url='/'):
    """Sends a notification to a specific user via all their subscriptions. Returns True if at least one sub exists."""
    subs = PushSubscription.query.filter_by(user_id=user.id).all()
    if not subs:
        logger.info(f"Notification skipped: User {user.username} has no push subscriptions.")
        return False

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
            logger.info(f"Removing invalid subscription for user {user.username}")
            db.session.delete(sub)
    db.session.commit()
    return True

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
        now = get_local_now()
        today = now.date()
        current_time_str = now.strftime("%H:%M")
        
        logger.debug(f"[Scheduler] Checking reminders at {current_time_str} ({now})")
        
        # 1. Check all users
        users = User.query.all()
        for user in users:
            settings = user.notification_settings
            if not settings: continue
            
            # Homework Reminder
            if settings.reminder_homework:
                logger.debug(f"[Scheduler] User {user.username} homework reminder set for {settings.reminder_homework}")
                # If we are at or past the set time AND haven't sent it today
                if current_time_str >= settings.reminder_homework and settings.last_homework_reminder_at != today:
                    logger.info(f"[Scheduler] Triggering homework reminder for {user.username}")
                    # Check ALL non-deleted tasks for this class
                    all_tasks = Task.query.filter(
                        Task.class_id == user.class_id,
                        Task.deleted_at.is_(None)
                    ).all()
                    
                    count = 0
                    for t in all_tasks:
                        # Check if user already finished it
                        from app.models import TaskCompletion
                        comp = TaskCompletion.query.filter_by(user_id=user.id, task_id=t.id).first()
                        if not comp or not comp.is_done:
                            count += 1
                    
                    if count > 0:
                        sent = notify_user(user, "Offene Aufgaben", f"Du hast noch {count} offene Aufgaben zu erledigen!", url='/tasks')
                        if sent:
                            settings.last_homework_reminder_at = today
                            db.session.add(settings)
                            db.session.commit()
                            logger.info(f"[Scheduler] Homework notification sent to {user.username} (Count: {count})")
                        else:
                            logger.info(f"[Scheduler] Could not send homework reminder to {user.username} (No subscriptions).")
                    else:
                        # We DON'T mark it as sent today if there were no tasks.
                        # This allows the user to add a task later and still get the reminder if it's past the time.
                        logger.debug(f"[Scheduler] No open tasks for {user.username}, skipping for now.")

            # Exam/Event Reminder
            if settings.reminder_exam:
                logger.debug(f"[Scheduler] User {user.username} event reminder set for {settings.reminder_exam}")
                if current_time_str >= settings.reminder_exam and settings.last_exam_reminder_at != today:
                    logger.info(f"[Scheduler] Triggering event reminder for {user.username}")
                    tomorrow = today + timedelta(days=1)
                    events = Event.query.filter(
                        db.func.date(Event.date) == tomorrow,
                        Event.class_id == user.class_id,
                        Event.deleted_at.is_(None)
                    ).all()
                    
                    if events:
                        sent = notify_user(user, "Termin/Klausur morgen", f"Morgen: {events[0].title}" + (f" und {len(events)-1} weitere" if len(events)>1 else ""), url='/calendar')
                        if sent:
                            settings.last_exam_reminder_at = today
                            db.session.add(settings)
                            db.session.commit()
                            logger.info(f"[Scheduler] Event notification sent to {user.username}")
                    else:
                        logger.debug(f"[Scheduler] No events tomorrow for {user.username}, skipping.")

