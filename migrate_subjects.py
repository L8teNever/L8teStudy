from app import create_app,db
from app.models import Subject

app = create_app()

with app.app_context():
    # Check if table exists
    inspector = db.inspect(db.engine)
    if 'subject' not in inspector.get_table_names():
        db.create_all() # This creates all missing tables, including subject
        print("Created Subject table.")
        
        # Add defaults if empty
        defaults = ['Mathematik', 'Deutsch', 'Englisch', 'Physik', 'Biologie', 
                   'Geschichte', 'Kunst', 'Sport', 'Chemie', 'Religion']
        
        if Subject.query.count() == 0:
            for name in defaults:
                db.session.add(Subject(name=name))
            db.session.commit()
            print("Added default subjects.")
    else:
        print("Subject table already exists.")
