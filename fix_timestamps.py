import json
from datetime import datetime
import os

def fix_database_timestamps():
    """Add missing timestamps to database entries"""
    try:
        # Load the database
        with open('data/downloaded_database.json', 'r') as f:
            database = json.load(f)
        
        # Count entries before fixing
        total_entries = len(database)
        fixed_count = 0
        
        # Current timestamp for entries missing one
        default_timestamp = datetime.now().isoformat()
        
        # Fix missing timestamps
        for entry in database:
            if 'features' in entry:
                if 'extraction_timestamp' not in entry['features']:
                    entry['features']['extraction_timestamp'] = default_timestamp
                    fixed_count += 1
        
        # Save the updated database
        with open('data/downloaded_database.json', 'w') as f:
            json.dump(database, f, indent=2)
        
        print(f"Database processed:")
        print(f"Total entries: {total_entries}")
        print(f"Fixed entries: {fixed_count}")
        
    except FileNotFoundError:
        print("Error: database.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in database file")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fix_database_timestamps() 