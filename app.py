from flask import Flask, make_response, request, jsonify, render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, json, os
from models import db, Candidate
# from behavioral_analyzer import BehavioralAnalyzer
from flask import Flask, jsonify, render_template
from flask import Flask, send_file, render_template
import sqlite3
from report_generator import generate_candidate_report,get_latest_candidate
from flask import send_file
from send_email import send_candidate_report_to_hr
from flask import send_from_directory
import os
import io
import subprocess
import re


app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend'
)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    os.makedirs('video_storage', exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        candidate = Candidate(
            email=data['email'],
            password=data['password']
        ) 
        db.session.add(candidate)
        db.session.commit()
        return jsonify({'message': 'Registered successfully', 'id': candidate.id})
    except Exception as e:
        db.session.rollback()
        if 'UNIQUE constraint failed: candidate.email' in str(e):
            return jsonify({'message': 'Email already exists. Please use a different email or try logging in.'}), 400
        else:
            return jsonify({'message': 'Registration failed. Please try again.'}), 500

@app.route('/details/<int:id>', methods=['POST'])
def save_details(id):
    data = request.json
    candidate = Candidate.query.get(id)
    candidate.name = data['name']
    candidate.mobile = data['mobile']
    candidate.skills = data['skills']
    db.session.commit()

    # Notify HR
    return jsonify({'message': 'Details saved successfully'})

@app.route('/get_questions', methods=['GET'])
def get_questions():
    with open('questions.json') as f:
        data = json.load(f)
        questions = data.get('questions', data)
    selected = random.sample(questions, min(3, len(questions)))
    return jsonify({ 'questions': selected })

@app.route('/submit_aptitude/<int:id>', methods=['POST'])
def submit_aptitude(id):
    try:
        data = request.json
        score = data['score']
        print(f"Received score: {score} for candidate ID: {id}")
        
        candidate = Candidate.query.get(id)
        if not candidate:
            print(f"Candidate with ID {id} not found")
            return jsonify({'error': 'Candidate not found'}), 404
            
        candidate.aptitude_score = score
        candidate.aptitude_completed = True
        db.session.commit()
        
        print(f"Successfully saved score {score} for candidate {candidate.name}")
        return jsonify({'message': 'Aptitude score recorded successfully!', 'score': score})
        
    except Exception as e:
        print(f"Error in submit_aptitude: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@app.route('/candidate-form')
def candidate_form():
    return app.send_static_file('candidate_form.html')

@app.route('/instructions')
def instructions():
    return render_template('Instruction.html')  # note: file inside templates folder

@app.route('/aptitude-test')
def aptitude_test():
    return  app.send_static_file('aptitude_test.html')

@app.route('/track_tab_switch/<int:id>', methods=['POST'])
def track_tab_switch(id):
    """Track tab switching for security"""
    try:
        candidate = Candidate.query.get(id)
        if candidate:
            candidate.tab_switches += 1
            db.session.commit()
            print(f"Tab switch detected for candidate {id}. Total switches: {candidate.tab_switches}")
            return jsonify({'message': 'Tab switch recorded', 'total_switches': candidate.tab_switches})
        return jsonify({'error': 'Candidate not found'}), 404
    except Exception as e:
        print(f"Error tracking tab switch: {e}")
        return jsonify({'error': 'Failed to track tab switch'}), 500

@app.route('/next-round')
def next_round():
    return render_template('next_round.html')

# Coding Round Routes
@app.route('/coding-round')
def coding_round():
    return app.send_static_file('coding_questions.html')

@app.route('/get_coding_questions', methods=['GET'])
def get_coding_questions():
    with open('coding_questions.json') as f:
        data = json.load(f)
        # data is already a list, not a dict with 'questions' key
        all_questions = data if isinstance(data, list) else data.get('questions', [])
        # Select 3 random questions for each candidate
        selected_questions = random.sample(all_questions, min(3, len(all_questions)))
    return jsonify({'questions': selected_questions})

@app.route('/submit_coding/<int:id>', methods=['POST'])
def submit_coding(id):
    try:
        data = request.json
        score = data['score']
        print(f"Received coding score: {score} for candidate ID: {id}")
        
        candidate = Candidate.query.get(id)
        if not candidate:
            print(f"Candidate with ID {id} not found")
            return jsonify({'error': 'Candidate not found'}), 404
            
        candidate.coding_score = score
        candidate.coding_completed = True
        db.session.commit()
        
        print(f"Successfully saved coding score {score} for candidate {candidate.name}")
        return jsonify({'message': 'Coding score recorded successfully!', 'score': score})
        
    except Exception as e:
        print(f"Error in submit_coding: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/coding-round-completed')
def coding_round_completed():
    return render_template('coding_round_completed.html')

# Behavioral Round Routes
@app.route('/behavioral-round')
def behavioral_round():
    return app.send_static_file('behavioral_assessment.html')

@app.route('/get_behavioral_questions', methods=['GET'])
def get_behavioral_questions():
    with open('behavioral_questions.json') as f:
        data = json.load(f)
        # Return all 15 questions (5 MCQ + 10 written)
        return jsonify({'questions': data})

@app.route('/submit_behavioral/<int:id>', methods=['POST'])
def submit_behavioral(id):
    try:
        data = request.json
        responses = data['responses']
        print(f"Received behavioral responses for candidate ID: {id}")
        
        candidate = Candidate.query.get(id)
        if not candidate:
            print(f"Candidate with ID {id} not found")
            return jsonify({'error': 'Candidate not found'}), 404
        
        # Analyze responses using AI
        # analyzer = BehavioralAnalyzer()
        
        # Separate MCQ and written responses
        mcq_responses = {}
        written_responses = {}
        
        with open('behavioral_questions.json') as f:
            questions = json.load(f)
        
        for question in questions:
            q_id = str(question['id'])
            if q_id in responses:
                if question['type'] == 'mcq':
                    mcq_responses[q_id] = responses[q_id]
                else:
                    written_responses[q_id] = responses[q_id]
        
        # Perform AI analysis
        # score, analysis = analyzer.analyze_responses(mcq_responses, written_responses)
        score, analysis = 85, "Demo analysis - AI integration pending"
        
        # Save to database
        candidate.behavioral_score = score
        candidate.behavioral_completed = True
        candidate.behavioral_analysis = analysis
        db.session.commit()
        
        print(f"Successfully saved behavioral score {score} for candidate {candidate.name}")
        print(f"Analysis: {analysis[:100]}...")
        
        return jsonify({
            'message': 'Behavioral assessment completed successfully!', 
            'score': score,
            'analysis': analysis
        })
        
    except Exception as e:
        print(f"Error in submit_behavioral: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
# ----------------- Helper Function -----------------
def parse_candidate_output(output):
    """
    Parse console output of view_database.py into structured data.
    """
    candidates = []
    pattern = re.compile(
        r"CANDIDATE ID[:：]\s*(\d+).*?Email[:：]\s*(.*?)\n.*?Aptitude Score[:：]\s*(.*?)\n.*?Coding Score[:：]\s*(.*?)\n.*?Behavioral Score[:：]\s*(.*?)\n.*?Status[:：]\s*(.*?)\n",
        re.DOTALL
    )
    for match in pattern.finditer(output):
        id_val, email, aptitude_score, coding_score, behavioral_score, status = match.groups()
        candidates.append({
            "id": int(id_val),
            "email": email.strip(),
            "aptitude_score": aptitude_score.strip(),
            "coding_score": coding_score.strip(),
            "behavioral_score": behavioral_score.strip(),
            "status": status.strip()
        })
    return candidates
    

# --- Behavioral Assessment Completed: show HR Dashboard ---    
@app.route('/hr_dashboard')
def hr_dashboard():
    return  app.send_static_file('hr_dashboard.html')

# --- DEBUG: Check if view_database.py runs ---
result = subprocess.run(["python", "view_database.py"], capture_output=True, text=True)
print("STDOUT:\n", result.stdout)
print("STDERR:\n", result.stderr)
# -------------------------------------------

# ----------------- API Route -----------------
@app.route("/api/candidates")
def api_candidates():
    """
    Run view_database.py and return structured candidate data (including name, mobile, skills)
    """
    import subprocess, re, json

    try:
        # Run your existing view_database.py script
        result = subprocess.run(
            ["python", "view_database.py"],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout

        # Updated regex to also capture Name, Mobile, Skills
        pattern = re.compile(
            r"CANDIDATE ID:\s*(\d+)\s*"
            r"Email:\s*(.*?)\s*"
            r"Name:\s*(.*?)\s*"
            r"Mobile:\s*(.*?)\s*"
            r"Skills:\s*(.*?)\s*"
            r"Aptitude Score:\s*(.*?)\s*"
            r"Coding Score:\s*(.*?)\s*"
            r"Behavioral Score:\s*(.*?)\s*"
            r"Status:\s*(.*?)\s*"
            r"=+",
            re.DOTALL
        )

        candidates = []
        for m in pattern.finditer(output):
            groups = [g.strip() for g in m.groups()]
            candidates.append({
                "id": groups[0],
                "email": groups[1],
                "name": groups[2],
                "mobile": groups[3],
                "skills": groups[4],
                "aptitude_score": groups[5],
                "coding_score": groups[6],
                "behavioral_score": groups[7],
                "status": groups[8],
            })

        return json.dumps(candidates), 200, {"Content-Type": "application/json"}

    except subprocess.CalledProcessError as e:
        print("❌ Error running view_database.py:", e)
        return json.dumps({"error": "Failed to run view_database.py"}), 500, {"Content-Type": "application/json"}
    
@app.route("/send_report", methods=["GET", "POST"])
def send_report():
    candidate = get_latest_candidate()
    if candidate is None:
        return jsonify({"status": "error", "message": "No candidate found"}), 404

    # 1️⃣ Map DB keys to front-end/report keys (same as in your __main__)
    candidate_data_mapped = {
        "Candidate ID": candidate["id"],
        "Email": candidate["email"],
        "Password": candidate["password"],
        "Name": candidate["name"],
        "Mobile": candidate["mobile"],
        "Skills": candidate["skills"],
        "Aptitude Score": candidate["aptitude_score"],
        "Aptitude Completed": candidate["aptitude_completed"],
        "Coding Score": candidate["coding_score"],
        "Coding Completed": candidate["coding_completed"],
        "Behavioral Score": candidate["behavioral_score"],
        "Behavioral Completed": candidate["behavioral_completed"],
        "Behavioral Analysis": candidate["behavioral_analysis"],
        "Tab Switches": candidate["tab_switches"],
        "Registered": candidate["created_at"]
    }

    # 2️⃣ Prepare PDF filename
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = os.path.join(reports_dir, f"Candidate_Report_{candidate_data_mapped['Candidate ID']}.pdf")

    # 3️⃣ Generate PDF report
    generate_candidate_report(candidate_data_mapped, filename)

    # 4️⃣ Send report via email
    success = send_candidate_report_to_hr(
        candidate_name=candidate_data_mapped["Name"],
        candidate_email=candidate_data_mapped["Email"],
        report_link=filename
    )

    if success:
        return jsonify({"status": "success", "message": f"Report sent to HR for {candidate_data_mapped['Name']}"})
    else:
        return jsonify({"status": "error", "message": "Failed to send report"}), 500
    
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
    
@app.route('/assessment-completed')
def assessment_completed():
    return render_template('assessment_completed.html')

@app.route('/generate_latest_report')
def generate_latest_report():
    candidate_data = get_latest_candidate()
    if not candidate_data:
        return "⚠️ No candidate data found.", 404

    # Map DB keys to report keys
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

    filename = f"Candidate_Report_{candidate_data_mapped['Candidate ID']}.pdf"
    generate_candidate_report(candidate_data_mapped, filename)

    # Send the PDF file as browser download
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
