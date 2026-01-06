import sys
from app import create_app, db
from app.models import User, UserRole

def create_admin(username, password, role='superadmin'):
    app = create_app()
    with app.app_context():
        # Check if user exists
        if User.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists.")
            return

        user_role = UserRole.STUDENT

        if role.lower() in ['super', 'superadmin', 'super_admin']:
            user_role = UserRole.SUPER_ADMIN
        elif role.lower() == 'admin':
            user_role = UserRole.ADMIN
        elif role.lower() == 'student':
            user_role = UserRole.STUDENT
        else:
            print(f"Error: Unknown role '{role}'. Use 'superadmin', 'admin', or 'student'.")
            return

        user = User(
            username=username, 
            role=user_role,
            needs_password_change=False # CLI created users usually trusted
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Successfully created {user_role} user '{username}'.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password> [role]")
        print("Roles: superadmin (default), admin, student")
        sys.exit(1)
        
    u = sys.argv[1]
    p = sys.argv[2]
    r = sys.argv[3] if len(sys.argv) > 3 else 'superadmin'
    
    create_admin(u, p, r)
