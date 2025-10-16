#!/usr/bin/env python3
"""
Non-interactive Database Viewer Script
View all candidate data in a clear, readable format
"""

import sqlite3
from datetime import datetime

def view_database():
    try:
        # Connect to database
        conn = sqlite3.connect('instance/database.db')
        cursor = conn.cursor()
        
        # Get all candidates
        cursor.execute('''
            SELECT id, email, password, name, mobile, skills,
                   aptitude_score, aptitude_completed, 
                   coding_score, coding_completed,
                   behavioral_score, behavioral_completed, behavioral_analysis,
                   tab_switches, created_at
            FROM candidate
            ORDER BY id
        ''')
        
        candidates = cursor.fetchall()
        
        if not candidates:
            print("No candidates found in database")
            return
        
        for candidate in candidates:
            id_val, email, password, name, mobile, skills, aptitude_score, aptitude_completed, coding_score, coding_completed, behavioral_score, behavioral_completed, behavioral_analysis, tab_switches, created_at = candidate
            
            print(f"CANDIDATE ID: {id_val}")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Mobile: {mobile}")
            print(f"Skills: {skills}")
            print(f"Aptitude Score: {aptitude_score if aptitude_score is not None else 'Not attempted'}")
            print(f"Coding Score: {coding_score if coding_score is not None else 'Not attempted'}")
            print(f"Behavioral Score: {behavioral_score if behavioral_score is not None else 'Not attempted'}")
            
            if aptitude_completed and coding_completed and behavioral_completed:
                status = "ALL ROUNDS COMPLETED"
            elif aptitude_completed and coding_completed:
                status = "APTITUDE + CODING COMPLETED"
            elif aptitude_completed:
                status = "APTITUDE COMPLETED"
            elif aptitude_score is None:
                status = "REGISTERED ONLY"
            else:
                status = "INCOMPLETE"
            
            print(f"Status: {status}")
            print("=" * 60)
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()




if __name__ == "__main__":
    # Directly run view_database without user interaction
    view_database()
    
