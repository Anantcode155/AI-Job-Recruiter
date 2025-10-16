from flask import Flask, render_template, request, jsonify
import json, sqlite3, os, urllib.request

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend")


def initialize_database_if_needed() -> None:
    """Ensure the SQLite database and required tables exist before handling requests."""
    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY,
            coding_score INTEGER DEFAULT 0
        )
        """
    )
    # Seed a default candidate so the flow works out-of-the-box
    cur.execute("INSERT OR IGNORE INTO candidates(id, coding_score) VALUES (1, 0)")
    conn.commit()
    conn.close()


initialize_database_if_needed()

@app.route("/next_round")
def next_round():
    return render_template("next_round.html")

@app.route("/coding_round")
def coding_round():
    # load coding questions from json
    json_path = os.path.join(os.path.dirname(__file__), "coding_questions.json")
    with open(json_path) as f:
        questions = json.load(f)
    return render_template("coding_questions.html", questions=questions)

@app.route("/submit_coding/<int:candidate_id>", methods=["POST"])
def submit_coding(candidate_id):
    data = request.get_json()
    score = data.get("score", 0)

    db_path = os.path.join(os.path.dirname(__file__), "database.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE candidates SET coding_score=? WHERE id=?", (score, candidate_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})


@app.route("/api/judge0/submit", methods=["POST"])
def judge0_submit():
    """Proxy endpoint to submit code to Judge0, avoiding exposing keys in the client."""
    payload = request.get_json(silent=True) or {}
    # Minimal validation
    source_code = payload.get("source_code", "")
    language_id = payload.get("language_id")
    stdin = payload.get("stdin", "")

    body = json.dumps({
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin
    }).encode("utf-8")

    rapidapi_key = os.environ.get("RAPIDAPI_KEY")
    if rapidapi_key:
        url = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        }
    else:
        # Public CE instance (no key) — CORS-friendly via server-side proxy
        url = "https://ce.judge0.com/submissions?base64_encoded=false&wait=true"
        headers = {
            "Content-Type": "application/json",
        }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return jsonify(json.loads(resp_body))
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == "__main__":
    app.run(debug=True, port=5001)