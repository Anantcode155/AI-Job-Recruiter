# report_generator.py
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def get_latest_candidate():
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()

    # Correct table name
    table_name = "candidate"

    try:
        # Fetch latest candidate by created_at
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()

        if not row:
            print("⚠️ No candidate records found in database.")
            conn.close()
            return None

        # Map row to dictionary using actual columns
        columns = [
            "id", "email", "password", "name", "mobile", "skills",
                   "aptitude_score", "aptitude_completed", 
                   "coding_score", "coding_completed",
                   "behavioral_score", "behavioral_completed", "behavioral_analysis",
                   "tab_switches", "created_at"
        ]

        candidate_data = {columns[i]: row[i] for i in range(len(columns))}

        # ✅ Print latest candidate details
        print("\n==============================")
        print("🧾 Latest Candidate Record:")
        for key, value in candidate_data.items():
            print(f"{key}: {value}")
        print("==============================\n")

        conn.close()
        return candidate_data

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.close()
        return None
    

def generate_candidate_report(candidate_data, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Use front-end friendly keys
    elements.append(Paragraph(f"Candidate Report - ID: {candidate_data.get('Candidate ID', 'N/A')}", styles['Title']))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Email", candidate_data.get("Email", "N/A")],
        ["Password", candidate_data.get("Password", "N/A")],
        ["Name", candidate_data.get("Name", "N/A")],
        ["Mobile", candidate_data.get("Mobile", "N/A")],
        ["Skills", candidate_data.get("Skills", "N/A")],
        ["Aptitude Score", candidate_data.get("Aptitude Score", "N/A")],
        ["Aptitude Completed", candidate_data.get("Aptitude Completed", "N/A")],
        ["Coding Score", candidate_data.get("Coding Score", "N/A")],
        ["Coding Completed", candidate_data.get("Coding Completed", "N/A")],
        ["Behavioral Score", candidate_data.get("Behavioral Score", "N/A")],
        ["Behavioral Completed", candidate_data.get("Behavioral Completed", "N/A")],
        ["Behavioral Analysis", candidate_data.get("Behavioral Analysis", "N/A")],
        ["Tab Switches", candidate_data.get("Tab Switches", "N/A")],
        ["Registered", candidate_data.get("Registered", "N/A")],
    ]

    table = Table(table_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1,12))
    elements.append(Paragraph("Report generated automatically by Candidate Report System.", styles['Italic']))

    doc.build(elements)
    print(f"✅ Candidate report '{filename}' created successfully!")


if __name__ == "__main__":
    candidate_data = get_latest_candidate()

    if candidate_data:
        # Map DB keys to front-end/report keys
        candidate_data_mapped = {
            "Candidate ID": candidate_data["id"],
            "Email": candidate_data["email"],
            "Password": candidate_data["password"],
            "Name": candidate_data["name"],
            "Mobile": candidate_data["mobile"],
            "Skills": candidate_data["skills"],
            "Aptitude Score": candidate_data["aptitude_score"],
            "Aptitude Completed": candidate_data["aptitude_completed"],
            "Coding Score": candidate_data["coding_score"],
            "Coding Completed": candidate_data["coding_completed"],
            "Behavioral Score": candidate_data["behavioral_score"],
            "Behavioral Completed": candidate_data["behavioral_completed"],
            "Behavioral Analysis": candidate_data["behavioral_analysis"],
            "Tab Switches": candidate_data["tab_switches"],
            "Registered": candidate_data["created_at"]
        }

        # Save PDF in a folder (e.g., reports/)
        filename = f"reports/Candidate_Report_{candidate_data_mapped['Candidate ID']}.pdf"
        generate_candidate_report(candidate_data_mapped, filename)
    else:
        print("⚠️ No candidate data found for report generation.")
