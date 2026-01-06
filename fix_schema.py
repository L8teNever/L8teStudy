import sqlite3
import os

DB_PATH = os.path.join('instance', 'l8testudy.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Migrating Task table...")
        # 1. Rename old table
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("ALTER TABLE task RENAME TO task_old")

        # 2. Create new table
        cursor.execute("""
            CREATE TABLE task (
                id INTEGER NOT NULL, 
                user_id INTEGER NOT NULL, 
                class_id INTEGER, 
                subject_id INTEGER, 
                is_shared BOOLEAN, 
                title VARCHAR(128) NOT NULL, 
                subject VARCHAR(64), 
                due_date DATETIME, 
                description TEXT, 
                is_done BOOLEAN, 
                deleted_at DATETIME, 
                PRIMARY KEY (id), 
                FOREIGN KEY(user_id) REFERENCES user (id), 
                FOREIGN KEY(class_id) REFERENCES school_class (id), 
                FOREIGN KEY(subject_id) REFERENCES subject (id)
            )
        """)

        # 3. Copy data
        cursor.execute("""
            INSERT INTO task (id, user_id, class_id, subject_id, is_shared, title, subject, due_date, description, is_done, deleted_at)
            SELECT id, user_id, class_id, subject_id, is_shared, title, subject, due_date, description, is_done, deleted_at
            FROM task_old
        """)

        # 4. Drop old table
        cursor.execute("DROP TABLE task_old")
        
        print("Migrating AuditLog table...")
        cursor.execute("ALTER TABLE audit_log RENAME TO audit_log_old")
        cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER NOT NULL, 
                user_id INTEGER NOT NULL, 
                class_id INTEGER, 
                action VARCHAR(256) NOT NULL, 
                timestamp DATETIME, 
                PRIMARY KEY (id), 
                FOREIGN KEY(user_id) REFERENCES user (id), 
                FOREIGN KEY(class_id) REFERENCES school_class (id)
            )
        """)
        cursor.execute("""
            INSERT INTO audit_log (id, user_id, class_id, action, timestamp)
            SELECT id, user_id, class_id, action, timestamp FROM audit_log_old
        """)
        cursor.execute("DROP TABLE audit_log_old")

        print("Migrating Event table...")
        cursor.execute("ALTER TABLE event RENAME TO event_old")
        cursor.execute("""
            CREATE TABLE event (
                id INTEGER NOT NULL, 
                user_id INTEGER NOT NULL, 
                class_id INTEGER, 
                subject_id INTEGER, 
                is_shared BOOLEAN, 
                title VARCHAR(128) NOT NULL, 
                date DATETIME NOT NULL, 
                description TEXT, 
                PRIMARY KEY (id), 
                FOREIGN KEY(user_id) REFERENCES user (id), 
                FOREIGN KEY(class_id) REFERENCES school_class (id), 
                FOREIGN KEY(subject_id) REFERENCES subject (id)
            )
        """)
        cursor.execute("""
            INSERT INTO event (id, user_id, class_id, subject_id, is_shared, title, date, description)
            SELECT id, user_id, class_id, subject_id, is_shared, title, date, description FROM event_old
        """)
        cursor.execute("DROP TABLE event_old")

        cursor.execute("PRAGMA foreign_keys=ON")
        conn.commit()
        print("Migration successful!")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
