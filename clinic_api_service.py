import os
import csv
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

with open("prompts/health-clinics/lead_qualifier_v1.md", "r") as f:
    system_prompt = f.read()

LOG_FILE = "live_lead_log.csv"

def get_field(text, field):
    field = field.lower()
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith(field + ":"):
            return line.split(":", 1)[1].strip()
    return "N/A"

def parse_response(text):
    return {
        "score": get_field(text, "Score"),
        "action": get_field(text, "Action"),
        "reasoning": get_field(text, "Reasoning"),
        "draft": get_field(text, "DraftMessage"),
        "full": text
    }

@app.route("/triage", methods=["POST"])
def triage():
    data = request.json or {}
    inquiry = data.get("inquiry", "").strip()

    if not inquiry:
        return jsonify({"error": "No inquiry provided"}), 400

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": inquiry}
        ]
    )

    full_text = resp.choices[0].message.content
    parsed = parse_response(full_text)

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Score", "Action",
                "Reasoning", "DraftMessage",
                "Inquiry", "FullResponse"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            parsed["score"],
            parsed["action"],
            parsed["reasoning"],
            parsed["draft"],
            inquiry,
            parsed["full"]
        ])

    return jsonify(parsed)

@app.route("/dashboard")
def dashboard():
    rows = []
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    rows.reverse()

    html = """
    <html>
    <head>
        <title>Clinic Triage Dashboard</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; }
            .card { background: #fff; padding: 20px; border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 1400px; margin: 0 auto; }
            h1 { margin-top: 0; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th { background: #4CAF50; color: white; padding: 10px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; vertical-align: top; }
            tr.urgent { background: #fff9c4; }
            .small { font-size: 12px; color: #555; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🏥 Clinic Triage Dashboard</h1>
            <table>
                <tr><th>Time</th><th>Score</th><th>Action</th><th>Reasoning</th><th>Draft Message</th><th>Inquiry</th></tr>
                {% for r in rows %}
                <tr class="{% if '9' in r.Score or '10' in r.Score %}urgent{% endif %}">
                    <td>{{ r.Timestamp }}</td>
                    <td>{{ r.Score }}</td>
                    <td>{{ r.Action }}</td>
                    <td class="small">{{ r.Reasoning }}</td>
                    <td class="small">{{ r.DraftMessage }}</td>
                    <td>{{ r.Inquiry[:80] }}{% if r.Inquiry|length > 80 %}...{% endif %}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, rows=rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)