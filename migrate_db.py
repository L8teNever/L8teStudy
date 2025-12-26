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
            add_column_if_missing('task', 'subject_id', 'INTEGER REFERENCES subject(id)')
            add_column_if_missing('task', 'is_shared', 'BOOLEAN DEFAULT 0')
            add_column_if_missing('event', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('event', 'subject_id', 'INTEGER REFERENCES subject(id)')
            add_column_if_missing('event', 'is_shared', 'BOOLEAN DEFAULT 0')
            add_column_if_missing('audit_log', 'class_id', 'INTEGER REFERENCES school_class(id)')
            add_column_if_missing('user', 'needs_password_change', 'BOOLEAN DEFAULT 0')
            add_column_if_missing('user', 'has_seen_tutorial', 'BOOLEAN DEFAULT 0')

            # --- Data Migration ---
            # 1. Ensure at least one class exists
            default_class = SchoolClass.query.first()
            if not default_class:
                print("Creating default class...")
                default_class = SchoolClass(name="Standardklasse", code="CLASS1")
                db.session.add(default_class)
                db.session.commit()
                print(f"✓ Default class created: {default_class.name} (Code: {default_class.code})")

            # 2. Migrate Subject-Class relationships to junction table
            if 'subject' in inspector.get_table_names():
                cols = [col['name'] for col in inspector.get_columns('subject')]
                if 'class_id' in cols:
                    print("Migrating subjects to junction table...")
                    with db.engine.connect() as conn:
                        res = conn.execute(text("SELECT id, class_id FROM subject WHERE class_id IS NOT NULL"))
                        for row in res:
                            conn.execute(text("INSERT OR IGNORE INTO subject_classes (subject_id, class_id) VALUES (:sid, :cid)"), {"sid": row[0], "cid": row[1]})
                        conn.commit()
                    print("✓ Subjects migrated to junction table.")

            # 3. Assign all existing users to default class if they don't have one
            users_to_fix = User.query.filter(User.class_id.is_(None), User.is_super_admin == False).all()
            if users_to_fix:
                print(f"Assigning {len(users_to_fix)} users to default class...")
                for u in users_to_fix:
                    u.class_id = default_class.id
                db.session.commit()

            # 4. Handle old 'admin' user
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user and not admin_user.is_super_admin:
                print("Setting 'admin' user as Super Admin...")
                admin_user.is_super_admin = True
                admin_user.class_id = None 
                db.session.commit()

            # 5. Assign shared content to default class
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
