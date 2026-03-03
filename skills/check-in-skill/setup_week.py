#!/usr/bin/env python3
"""
Weekly checkin setup - Create new week entry on Monday 9:00 AM
"""
import os
import subprocess
from datetime import datetime, timedelta

CHECKIN_FILE = '/root/clawd/codes/my-ai-memory/memos/checkin.md'
REPO_PATH = '/root/clawd/codes/my-ai-memory'

def get_week_info(date=None):
    """Get ISO week number and date range"""
    if date is None:
        date = datetime.now()

    # Get ISO week number
    iso_week = date.isocalendar()
    week_str = f"{date.year}-W{iso_week[1]:02d}"

    # Calculate Monday and Sunday of the week
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)

    date_range = f"{monday.strftime('%Y-%m-%d')} to {sunday.strftime('%Y-%m-%d')}"

    return week_str, date_range

def check_week_exists(week_str):
    """Check if week already exists in checkin.md"""
    if not os.path.exists(CHECKIN_FILE):
        return False

    with open(CHECKIN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    return f"## {week_str}" in content

def create_new_week():
    """Add new week entry to checkin.md"""
    week_str, date_range = get_week_info()

    # Check if week already exists
    if check_week_exists(week_str):
        print(f"Week {week_str} already exists")
        return True

    # Read current content
    if not os.path.exists(CHECKIN_FILE):
        content = ""
    else:
        with open(CHECKIN_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

    # Add new week
    new_week = f"\n---\n\n## {week_str} ({date_range})"
    content += new_week

    # Write back
    with open(CHECKIN_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Created new week: {week_str} ({date_range})")

    # Git sync
    try:
        subprocess.run(['git', 'add', 'memos/checkin.md'], cwd=REPO_PATH, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Start new week: {week_str}'], cwd=REPO_PATH, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=REPO_PATH, check=True, capture_output=True)
        print(f"Git sync completed for {week_str}")
    except Exception as e:
        print(f"Git sync failed: {e}")
        return False

    return True

if __name__ == '__main__':
    success = create_new_week()
    if success:
        print("✅ New week created successfully")
    else:
        print("❌ Failed to create new week")