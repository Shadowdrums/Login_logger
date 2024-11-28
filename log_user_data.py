#!/usr/bin/env python3

import sqlite3
from datetime import datetime
import subprocess
import time

# Database location
db_path = "/var/log/user_login_logger/user_login_logger.db"

def create_table():
    """Create the database table if it doesn't already exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def log_user(username, ip_address):
    """Log user login details to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logins (username, ip_address) VALUES (?, ?)", (username, ip_address))
    conn.commit()
    conn.close()

def get_user_ip():
    """Get the list of logged-in users and their IPs."""
    try:
        output = subprocess.check_output(["who"]).decode("utf-8")
        lines = output.strip().split("\n")
        user_ips = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                username = parts[0]
                ip_address = parts[-1].strip("()") if "(" in parts[-1] else "127.0.0.1"
                user_ips.append((username, ip_address))
        return user_ips
    except Exception as e:
        print(f"Error retrieving user IPs: {e}")
        return []

def main():
    """Main loop for continuous logging."""
    print("Starting continuous login monitoring...")
    logged_users = set()  # To track users who have already been logged
    while True:
        try:
            current_users = set(get_user_ip())  # Get current logged-in users
            new_users = current_users - logged_users  # Identify new logins
            for username, ip in new_users:
                log_user(username, ip)
                print(f"Logged: {username} from {ip}")
            logged_users = current_users  # Update the tracked users
        except Exception as e:
            print(f"Error in main loop: {e}")
        time.sleep(10)  # Wait for 10 seconds before polling again

if __name__ == "__main__":
    create_table()
    main()
