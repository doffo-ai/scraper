import json
from datetime import datetime

# Read the current database
with open('database.json', 'r') as f:
    database = json.load(f)

# Get current timestamp
current_time = datetime.now().isoformat()

# Add timestamp to each entry
for entry in database:
    entry['features']['extraction_timestamp'] = current_time

# Save updated database
with open('database.json', 'w') as f:
    json.dump(database, f, indent=2)

print(f"Added timestamp {current_time} to {len(database)} entries") 