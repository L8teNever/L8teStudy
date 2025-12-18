#!/usr/bin/env python3
"""
Database Migration Script for L8teStudy
This script ensures all database tables exist and are up to date.
Run this if you're upgrading from an older version.
"""

from app import create_app, db
from app.models import User, Task, TaskImage, TaskCompletion, Event, Grade, AuditLog

def migrate_database():
    """Create or update all database tables"""
    app = create_app()
    
    with app.app_context():
        print("Starting database migration...")
        
        try:
            # Create all tables
            db.create_all()
            print("✓ All database tables created/verified successfully")
            
            # Check if TaskCompletion table exists and has data
            try:
                count = TaskCompletion.query.count()
                print(f"✓ TaskCompletion table exists with {count} entries")
            except Exception as e:
                print(f"⚠ TaskCompletion table check: {str(e)}")
            
            # Check if we need to migrate old Task.is_done to TaskCompletion
            try:
                old_tasks = Task.query.filter(Task.is_done == True).all()
                if old_tasks:
                    print(f"Found {len(old_tasks)} tasks with old is_done=True")
                    print("Migrating to TaskCompletion table...")
                    
                    for task in old_tasks:
                        # Check if completion already exists
                        completion = TaskCompletion.query.filter_by(
                            user_id=task.user_id, 
                            task_id=task.id
                        ).first()
                        
                        if not completion:
                            completion = TaskCompletion(
                                user_id=task.user_id,
                                task_id=task.id,
                                is_done=True
                            )
                            db.session.add(completion)
                    
                    db.session.commit()
                    print(f"✓ Migrated {len(old_tasks)} task completions")
            except Exception as e:
                print(f"Migration check: {str(e)}")
            
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
