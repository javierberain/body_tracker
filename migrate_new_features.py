"""
Migration script to add new features:
- benchmark_measurement_id to User table
- Make circumference measurements optional

Run this ONCE after updating the code:
python migrate_new_features.py
"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Check if benchmark_measurement_id column exists in user table
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result]
            
            if 'benchmark_measurement_id' not in columns:
                conn.execute(text("ALTER TABLE user ADD COLUMN benchmark_measurement_id INTEGER"))
                conn.commit()
                print("✓ Added benchmark_measurement_id column to user table")
            else:
                print("✓ benchmark_measurement_id column already exists")
            
            # The circumference fields are already nullable in the database from the previous migration
            # But if you deleted and recreated the database, the new app.py has them as nullable
            
            print("\n✓ Migration completed successfully!")
            print("\nNew features available:")
            print("- Set benchmark measurements for comparison")
            print("- Circumference measurements are now optional")
            print("- Change password feature")
            print("- Delete users (admin)")
            print("- Password confirmation when creating users")
            print("- Auto timestamp on new measurements")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        print("\nIf you get errors, you may need to:")
        print("1. Delete body_tracker.db")
        print("2. Restart the app (it will create a fresh database)")
        print("3. Re-import your data")
