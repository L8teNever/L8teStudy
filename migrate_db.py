#!/usr/bin/env python3
"""
Database Migration Script for L8teStudy
This script ensures all database tables exist and are up to date.
Run this if you're upgrading from an older version.
"""

from app import create_app, db
from app.models import SchoolClass, User, Task, TaskImage, TaskCompletion, Event, Grade, AuditLog, Subject

def migrate_database():
    """Create or update all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Starting database migration...")
        
        try:
            # Create all tables (this creates new tables like SchoolClass)
            db.create_all()
            print("✓ All database tables created/verified successfully")
            
            # --- Column Migrations ---
            from sqlalchemy import text, inspect
            inspector = inspect(db.engine)
            
            # Helper to add column if it doesn't exist
            def add_column_if_missing(table_name, column_name, column_type):
                if table_name in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    if column_name not in columns:
                        print(f"⚠ Column '{column_name}' missing in '{table_name}' table. Adding it...")
                        with db.engine.connect() as conn:
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
                            conn.commit()
                        print(f"✓ Column '{column_name}' added successfully to '{table_name}'.")
                        return True
                return False

            add_column_if_missing('user', 'is_super_admin', 'BOOLEAN DEFAULT 0')
            add_column_if_missing('user', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('task', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('event', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('audit_log', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('subject', 'class_id', 'INTEGER REFERENCES school_class(id)')

            # --- Data Migration ---
            # 1. Ensure at least one class exists
            default_class = SchoolClass.query.first()
            if not default_class:
                print("Creating default class...")
                default_class = SchoolClass(name="Standardklasse", code="CLASS1")
                db.session.add(default_class)
                db.session.commit()
                print(f"✓ Default class created: {default_class.name} (Code: {default_class.code})")

            # 2. Assign all existing users to default class if they don't have one
            # EXCEPT super admin if we decide so, but let's keep it simple.
            users_to_fix = User.query.filter(User.class_id.is_(None), User.is_super_admin == False).all()
            if users_to_fix:
                print(f"Assigning {len(users_to_fix)} users to default class...")
                for u in users_to_fix:
                    u.class_id = default_class.id
                db.session.commit()

            # 3. Handle old 'admin' user - make it super admin maybe?
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user and not admin_user.is_super_admin:
                print("Setting 'admin' user as Super Admin...")
                admin_user.is_super_admin = True
                admin_user.class_id = None # Super admins are global
                db.session.commit()

            # 4. Assign shared content to default class
            tasks_to_fix = Task.query.filter(Task.class_id.is_(None)).all()
            if tasks_to_fix:
                print(f"Migrating {len(tasks_to_fix)} tasks to default class...")
                for t in tasks_to_fix:
                    t.class_id = default_class.id
                db.session.commit()

            events_to_fix = Event.query.filter(Event.class_id.is_(None)).all()
            if events_to_fix:
                print(f"Migrating {len(events_to_fix)} events to default class...")
                for e in events_to_fix:
                    e.class_id = default_class.id
                db.session.commit()

            subjects_to_fix = Subject.query.filter(Subject.class_id.is_(None)).all()
            if subjects_to_fix:
                print(f"Migrating {len(subjects_to_fix)} subjects to default class...")
                for s in subjects_to_fix:
                    s.class_id = default_class.id
                db.session.commit()
            
            logs_to_fix = AuditLog.query.filter(AuditLog.class_id.is_(None)).all()
            if logs_to_fix:
                print(f"Migrating {len(logs_to_fix)} audit logs to default class...")
                for l in logs_to_fix:
                    l.class_id = default_class.id
                db.session.commit()

            print("\n" + "="*60)
            print("Database migration completed successfully!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate_database()
    exit(0 if success else 1)
