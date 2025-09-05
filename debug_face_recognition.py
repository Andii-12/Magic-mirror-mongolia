#!/usr/bin/env python3
"""
Debug script to monitor face recognition status file
"""

import json
import time
import os
from datetime import datetime

def monitor_status_file():
    """Monitor the status file for changes"""
    status_file = "/tmp/magicmirror_face_status.json"
    
    print("🔍 Face Recognition Status File Monitor")
    print("=" * 50)
    print("Press Ctrl+C to stop monitoring")
    print()
    
    last_data = None
    
    try:
        while True:
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r') as f:
                        data = json.load(f)
                    
                    # Only print if data has changed
                    if data != last_data:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] Status Update:")
                        print(f"  Person: {data.get('person', 'None')}")
                        print(f"  Distance: {data.get('distance', 'N/A')} cm")
                        print(f"  Active: {data.get('active', False)}")
                        print(f"  Status: {data.get('status', 'unknown')}")
                        print()
                        last_data = data.copy()
                except Exception as e:
                    print(f"Error reading status file: {e}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status file not found")
            
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    monitor_status_file()
