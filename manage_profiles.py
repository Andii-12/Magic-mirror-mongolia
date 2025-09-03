#!/usr/bin/env python3
"""
User Profile Management Script
Helps manage personal information for face recognition users
"""

import json
import os
import sys
from datetime import datetime

PROFILES_FILE = "user_profiles.json"

def load_profiles():
    """Load user profiles from JSON file"""
    try:
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Profiles file {PROFILES_FILE} not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing profiles file: {e}")
        return None

def save_profiles(profiles):
    """Save user profiles to JSON file"""
    try:
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
        print(f"✅ Profiles saved to {PROFILES_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error saving profiles: {e}")
        return False

def list_users(profiles):
    """List all users in the system"""
    print("\n👥 Current Users:")
    print("=" * 50)
    
    for username, profile in profiles.get("users", {}).items():
        print(f"📋 {username} ({profile.get('displayName', username)})")
        
        # Show enabled features
        features = []
        if profile.get("calendar", {}).get("enabled"):
            features.append("📅 Calendar")
        if profile.get("todo", {}).get("enabled"):
            features.append("📝 Todo")
        if profile.get("weather", {}).get("enabled"):
            features.append("🌤️ Weather")
        if profile.get("news", {}).get("enabled"):
            features.append("📰 News")
        
        if features:
            print(f"   Features: {', '.join(features)}")
        else:
            print("   Features: None enabled")
        print()

def add_user(profiles):
    """Add a new user to the system"""
    print("\n➕ Add New User")
    print("=" * 30)
    
    username = input("Enter username (must match face recognition name): ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return profiles
    
    if username in profiles.get("users", {}):
        print(f"❌ User '{username}' already exists!")
        return profiles
    
    display_name = input(f"Enter display name for {username} (optional): ").strip()
    if not display_name:
        display_name = username
    
    # Create new user profile
    new_user = {
        "name": username,
        "displayName": display_name,
        "calendar": {
            "enabled": False
        },
        "todo": {
            "enabled": False
        },
        "weather": {
            "enabled": True,
            "location": "Ulaanbaatar",
            "locationID": "2028462",
            "apiKey": "YOUR_WEATHER_API_KEY",
            "units": "metric",
            "language": "mn"
        },
        "news": {
            "enabled": True,
            "feeds": [
                {
                    "title": "Монголын мэдээ",
                    "url": "https://www.mongolnews.mn/rss.xml"
                }
            ],
            "showPublishDate": True,
            "showDescription": True,
            "wrapTitle": True,
            "animationSpeed": 300000
        },
        "greeting": {
            "morning": f"Өглөөний мэнд, {display_name}!",
            "afternoon": f"Өдрийн мэнд, {display_name}!",
            "evening": f"Оройн мэнд, {display_name}!",
            "night": f"Шөнийн мэнд, {display_name}!"
        }
    }
    
    # Ask about features
    print(f"\n🔧 Configure features for {username}:")
    
    # Calendar
    if input("Enable personal calendar? (y/n): ").lower() == 'y':
        new_user["calendar"]["enabled"] = True
        calendar_url = input("Enter Google Calendar ICS URL (optional): ").strip()
        if calendar_url:
            new_user["calendar"]["urls"] = [calendar_url]
        new_user["calendar"]["maxEntries"] = int(input("Max calendar entries (default 5): ") or "5")
    
    # Todo
    if input("Enable personal todo list? (y/n): ").lower() == 'y':
        new_user["todo"]["enabled"] = True
        print("Enter todo items (press Enter on empty line to finish):")
        todo_items = []
        while True:
            item = input("  Todo item: ").strip()
            if not item:
                break
            todo_items.append(item)
        new_user["todo"]["list"] = todo_items
    
    # Add user to profiles
    if "users" not in profiles:
        profiles["users"] = {}
    profiles["users"][username] = new_user
    
    print(f"✅ User '{username}' added successfully!")
    return profiles

def edit_user(profiles):
    """Edit an existing user"""
    print("\n✏️ Edit User")
    print("=" * 20)
    
    username = input("Enter username to edit: ").strip()
    if not username or username not in profiles.get("users", {}):
        print(f"❌ User '{username}' not found!")
        return profiles
    
    user = profiles["users"][username]
    print(f"\n📋 Editing user: {username}")
    
    # Edit display name
    new_display_name = input(f"Display name (current: {user.get('displayName', username)}): ").strip()
    if new_display_name:
        user["displayName"] = new_display_name
    
    # Edit features
    print("\n🔧 Edit features:")
    
    # Calendar
    current_calendar = user.get("calendar", {}).get("enabled", False)
    new_calendar = input(f"Enable calendar? (current: {current_calendar}) (y/n): ").lower() == 'y'
    user["calendar"]["enabled"] = new_calendar
    
    # Todo
    current_todo = user.get("todo", {}).get("enabled", False)
    new_todo = input(f"Enable todo list? (current: {current_todo}) (y/n): ").lower() == 'y'
    user["todo"]["enabled"] = new_todo
    
    if new_todo and user.get("todo", {}).get("list"):
        print("Current todo items:")
        for i, item in enumerate(user["todo"]["list"], 1):
            print(f"  {i}. {item}")
        
        if input("Edit todo items? (y/n): ").lower() == 'y':
            print("Enter new todo items (press Enter on empty line to finish):")
            todo_items = []
            while True:
                item = input("  Todo item: ").strip()
                if not item:
                    break
                todo_items.append(item)
            user["todo"]["list"] = todo_items
    
    print(f"✅ User '{username}' updated successfully!")
    return profiles

def delete_user(profiles):
    """Delete a user from the system"""
    print("\n🗑️ Delete User")
    print("=" * 20)
    
    username = input("Enter username to delete: ").strip()
    if not username or username not in profiles.get("users", {}):
        print(f"❌ User '{username}' not found!")
        return profiles
    
    confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        del profiles["users"][username]
        print(f"✅ User '{username}' deleted successfully!")
    else:
        print("❌ Deletion cancelled.")
    
    return profiles

def main():
    """Main menu"""
    print("🎭 MagicMirror² Personal Information Manager")
    print("=" * 50)
    
    # Load profiles
    profiles = load_profiles()
    if not profiles:
        return
    
    while True:
        print("\n📋 Main Menu:")
        print("1. List users")
        print("2. Add user")
        print("3. Edit user")
        print("4. Delete user")
        print("5. Save and exit")
        print("6. Exit without saving")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            list_users(profiles)
        elif choice == "2":
            profiles = add_user(profiles)
        elif choice == "3":
            profiles = edit_user(profiles)
        elif choice == "4":
            profiles = delete_user(profiles)
        elif choice == "5":
            if save_profiles(profiles):
                print("👋 Goodbye!")
                break
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-6.")

if __name__ == "__main__":
    main()
