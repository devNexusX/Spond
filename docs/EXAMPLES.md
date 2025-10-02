# Usage Examples

## Basic Usage

### Export All Groups
```bash
# Simple group export
python groups.py
```
**Output**: JSON files in `./exports/` directory, one per group.

### Export Attendance Data
```bash
# All events (may be a lot!)
python attendance.py

# Events in date range
python attendance.py --from 2025-01-01 --to 2025-12-31

# Include all member responses (accepted, declined, etc.)
python attendance.py --from 2025-01-01 --to 2025-12-31 -a

# Last 30 days with all responses
python attendance.py --from 2025-09-01 -a
```

## Common Workflows

### Weekly Data Export
```bash
#!/bin/bash
# weekly_export.sh

echo "Extracting weekly Spond data..."

# Export all groups (structure changes infrequently)
python groups.py

# Export recent attendance (last 7 days with all responses)
python attendance.py --from $(date -d '7 days ago' +%Y-%m-%d) -a

echo "Export complete! Check ./exports/ directory"
```

### Monthly Reports
```bash
# Get current month attendance
python attendance.py --from 2025-10-01 --to 2025-11-01 -a

# Previous month
python attendance.py --from 2025-09-01 --to 2025-10-01 -a
```

### Event Analysis
```bash
# Get detailed attendance for specific period
python attendance.py --from 2025-09-01 --to 2025-09-30 -a

# Then analyze the CSV files:
# - Event participation rates  
# - Member attendance patterns
# - Response time analysis
```

## Authentication Examples

### First-Time Setup
```bash
# 1. Get web token (safest)
python web_token_extractor.py
# Follow prompts to extract from browser

# 2. Test with groups (should work without 2FA)
python groups.py

# 3. Test attendance export
python attendance.py --help
```

### When Token Expires
```bash
# You'll see warnings like:
# "⚠️ Found token but it expired at 2025-10-15T10:30:00"

# Solution: Get fresh token
python web_token_extractor.py
# Extract new token from browser session
```

### Emergency API Login
```bash
# If web token extraction fails, scripts will offer:
# "Choose (1=extract token, 2=risky login, 3=abort): 2"

# This triggers 2FA flow:
# 📱 SMS code has been sent to: ****41
# Enter SMS verification code: 123456
```

## Output Examples

### Groups Export Structure
```
./exports/
├── Viking_håndball_G2015.json
├── Black_Monkeys.json  
├── Vaulen_IL_G2013.json
└── ...
```

Each JSON contains complete group data:
```json
{
    "id": "group-id-here",
    "name": "Viking håndball G2015",
    "members": [...],
    "admins": [...],
    "settings": {...}
}
```

### Attendance Export Structure
```
./exports/
├── 2025-09-02T164500Z-Training_Session.csv
├── 2025-09-05T180000Z-Match_vs_Rivals.csv
└── ...
```

CSV format:
```csv
Start,End,Description,Name,Answer,Organizer
2025-09-02T16:45:00Z,2025-09-02T18:00:00Z,Training Session,John Doe,accepted,
2025-09-02T16:45:00Z,2025-09-02T18:00:00Z,Training Session,Jane Smith,declined,
2025-09-02T16:45:00Z,2025-09-02T18:00:00Z,Training Session,Coach Mike,accepted,X
```

## Advanced Usage

### Automated Backups
```bash
#!/bin/bash
# backup_spond.sh - Run weekly via cron

DATE=$(date +%Y%m%d)
BACKUP_DIR="./backups/$DATE"

mkdir -p "$BACKUP_DIR"

# Export current data
python groups.py
python attendance.py --from $(date -d '30 days ago' +%Y-%m-%d) -a

# Move to dated backup
mv ./exports/* "$BACKUP_DIR/"

echo "Backup created: $BACKUP_DIR"
```

### Data Processing Pipeline
```python
# process_exports.py - Example processing script

import json
import csv
import os
from datetime import datetime

def analyze_attendance():
    """Analyze attendance patterns from exported CSV files"""
    
    attendance_files = [f for f in os.listdir('./exports') if f.endswith('.csv')]
    
    for file in attendance_files:
        print(f"Processing {file}...")
        
        with open(f'./exports/{file}', 'r') as f:
            reader = csv.DictReader(f)
            
            accepted = sum(1 for row in reader if row['Answer'] == 'accepted')
            declined = sum(1 for row in reader if row['Answer'] == 'declined')
            
            print(f"  Accepted: {accepted}, Declined: {declined}")

def analyze_groups():
    """Analyze group membership from exported JSON files"""
    
    group_files = [f for f in os.listdir('./exports') if f.endswith('.json')]
    
    total_members = 0
    for file in group_files:
        with open(f'./exports/{file}', 'r') as f:
            group_data = json.load(f)
            members = len(group_data.get('members', []))
            total_members += members
            
            print(f"{group_data['name']}: {members} members")
    
    print(f"Total members across all groups: {total_members}")

if __name__ == "__main__":
    analyze_groups()
    analyze_attendance()
```

## Tips & Best Practices

### 🔒 Security
- Always use web tokens when possible
- Don't commit `config.py` or `web_token.json` to version control
- Refresh tokens before they expire
- Monitor for authentication warnings

### 📊 Data Management  
- Export regularly to avoid large datasets
- Use date ranges for attendance exports
- Keep backups of important exports
- Process data incrementally for better performance

### 🚀 Performance
- Web tokens are much faster than API login
- Use specific date ranges instead of "all time"
- Consider parallel processing for multiple groups
- Cache results when possible

### 🐛 Troubleshooting
- Check exports directory permissions
- Verify network connectivity
- Monitor rate limiting warnings  
- Keep dependencies updated