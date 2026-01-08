"""
Migration script to add hip_circumference column to existing database

Run this ONCE after updating the code:
python migrate_add_hip.py
"""

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column already exists
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(measurement)"))
            columns = [row[1] for row in result]
            
            if 'hip_circumference' in columns:
                print("✓ hip_circumference column already exists!")
            else:
                # Add the column with default value 0
                conn.execute(text("ALTER TABLE measurement ADD COLUMN hip_circumference FLOAT NOT NULL DEFAULT 0"))
                conn.commit()
                print("✓ Successfully added hip_circumference column!")
                print("Note: Existing measurements have hip_circumference set to 0")
                print("You can update these manually or re-import your data")
    except Exception as e:
        print(f"Error during migration: {e}")
