"""
Script to import historical data from Google Sheets CSV export

Usage:
1. Export your Google Sheet as CSV
2. Make sure CSV has these columns (in any order):
   - timestamp (or date)
   - weight
   - bmi
   - body_fat_percentage (or body_fat)
   - visceral_fat_index (or visceral_fat)
   - lean_mass_percentage (or lean_mass)
   - waist_circumference (or waist)
   - bicep_circumference (or bicep)
   - thigh_circumference (or thigh)
   - chest_circumference (or chest)

3. Run: python import_data.py your_file.csv username
"""

import csv
import sys
from datetime import datetime
from app import app, db, User, Measurement

def parse_date(date_str):
    """Try multiple date formats"""
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d/%m/%Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")

def import_csv(csv_file, username):
    with app.app_context():
        # Find user
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User '{username}' not found!")
            print("Available users:")
            for u in User.query.all():
                print(f"  - {u.username}")
            return
        
        print(f"Importing data for user: {username}")
        
        # Read CSV with UTF-8-sig to handle BOM
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            imported = 0
            errors = 0
            
            for i, row in enumerate(reader, start=2):
                try:
                    # Normalize row keys
                    normalized_row = {k.lower().strip().replace(' ', '_'): v for k, v in row.items()}
                    
                    # Parse timestamp
                    timestamp_key = 'timestamp' if 'timestamp' in normalized_row else 'date'
                    timestamp = parse_date(normalized_row[timestamp_key])
                    
                    # Helper function to get optional float
                    def get_float(key, alt_key=None, default=None):
                        val = normalized_row.get(key, normalized_row.get(alt_key) if alt_key else None)
                        if val and val.strip():
                            return float(val)
                        return default
                    
                    # Create measurement
                    measurement = Measurement(
                        user_id=user.id,
                        timestamp=timestamp,
                        weight=float(normalized_row['weight']),
                        bmi=float(normalized_row['bmi']),
                        body_fat_percentage=float(normalized_row.get('body_fat_percentage', normalized_row.get('body_fat'))),
                        visceral_fat_index=float(normalized_row.get('visceral_fat_index', normalized_row.get('visceral_fat'))),
                        lean_mass_percentage=float(normalized_row.get('lean_mass_percentage', normalized_row.get('lean_mass'))),
                        waist_circumference=get_float('waist_circumference', 'waist'),
                        hip_circumference=get_float('hip_circumference', 'hip'),
                        bicep_circumference=get_float('bicep_circumference', 'bicep'),
                        thigh_circumference=get_float('thigh_circumference', 'thigh'),
                        chest_circumference=get_float('chest_circumference', 'chest')
                    )
                    
                    db.session.add(measurement)
                    imported += 1
                    
                except Exception as e:
                    errors += 1
                    print(f"Error on row {i}: {e}")
                    print(f"Row data: {row}")
            
            # Commit all at once
            db.session.commit()
            
            print(f"\nImport complete!")
            print(f"Successfully imported: {imported} measurements")
            print(f"Errors: {errors}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python import_data.py <csv_file> <username>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    username = sys.argv[2]
    
    import_csv(csv_file, username)
