from app import create_app, db
from app.models import User
import sys

app = create_app()

def create_admin(username, password):
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists.")
            return

        user = User(username=username, is_admin=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)
    
    create_admin(sys.argv[1], sys.argv[2])
