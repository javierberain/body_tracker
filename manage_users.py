"""
User management script for Body Tracker

Usage:
    python manage_users.py list                    # List all users
    python manage_users.py create <username>       # Create new user (prompts for password)
    python manage_users.py password <username>     # Change user password
    python manage_users.py delete <username>       # Delete user
    python manage_users.py admin <username>        # Make user admin
"""

import sys
import getpass
from app import app, db, User

def list_users():
    """List all users"""
    with app.app_context():
        users = User.query.all()
        print("\nAll Users:")
        print("-" * 50)
        for user in users:
            role = "Admin" if user.is_admin else "User"
            measurements = len(user.measurements)
            print(f"{user.id}. {user.username} [{role}] - {measurements} measurements")
        print("-" * 50)

def create_user(username):
    """Create a new user"""
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists!")
            return
        
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("Error: Passwords don't match!")
            return
        
        is_admin = input("Make admin? (y/n): ").lower() == 'y'
        
        user = User(username=username, is_admin=is_admin)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        role = "admin" if is_admin else "user"
        print(f"✓ Created {role} '{username}' successfully!")

def change_password(username):
    """Change user password"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found!")
            return
        
        password = getpass.getpass("Enter new password: ")
        password_confirm = getpass.getpass("Confirm new password: ")
        
        if password != password_confirm:
            print("Error: Passwords don't match!")
            return
        
        user.set_password(password)
        db.session.commit()
        print(f"✓ Password changed for '{username}'!")

def delete_user(username):
    """Delete a user and all their measurements"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found!")
            return
        
        measurements = len(user.measurements)
        confirm = input(f"Delete '{username}' and {measurements} measurements? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
        
        db.session.delete(user)
        db.session.commit()
        print(f"✓ Deleted user '{username}' and all measurements!")

def make_admin(username):
    """Make a user an admin"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found!")
            return
        
        if user.is_admin:
            print(f"'{username}' is already an admin!")
            return
        
        user.is_admin = True
        db.session.commit()
        print(f"✓ '{username}' is now an admin!")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        list_users()
    elif command == 'create' and len(sys.argv) == 3:
        create_user(sys.argv[2])
    elif command == 'password' and len(sys.argv) == 3:
        change_password(sys.argv[2])
    elif command == 'delete' and len(sys.argv) == 3:
        delete_user(sys.argv[2])
    elif command == 'admin' and len(sys.argv) == 3:
        make_admin(sys.argv[2])
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
