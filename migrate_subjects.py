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
            from app.models import SchoolClass
            default_class = SchoolClass.query.first()
            if not default_class:
                default_class = SchoolClass(name="Standardklasse", code="CLASS1")
                db.session.add(default_class)
                db.session.commit()

            for name in defaults:
                db.session.add(Subject(name=name, class_id=default_class.id))
            db.session.commit()
            print(f"Added default subjects to class: {default_class.name}")
    else:
        print("Subject table already exists.")
