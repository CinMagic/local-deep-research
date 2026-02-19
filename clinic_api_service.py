import os
import csv
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
app = Flask(__name__)
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

with open("prompts/health-clinics/lead_qualifier_v1.md", "r") as f:
    system_prompt = f.read()

LOG_FILE = "live_lead_log.csv"

def extract_score(text):
    match = re.search(r"(\d+)/10", text)
    return match.group(1) if match else "N/A"

@app.route('/triage', methods=['POST'])
def triage_lead():
    data = request.json
    inquiry = data.get('inquiry', '')
    
    if not inquiry:
        return jsonify({"error": "No inquiry provided"}), 400

    # 2. Run AI Logic
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": inquiry}]
    )
    
    verdict = response.choices[0].message.content
    score = extract_score(verdict)

    # 3. Log to CSV
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Score", "Inquiry", "Full Verdict"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, inquiry, verdict])

    # 4. High-Urgency Alert Trigger
    try:
        if score != "N/A" and int(score) >= 9:
            print("\n" + "!"*50)
            print("🚨 URGENT ALERT: HIGH-VALUE LEAD IDENTIFIED! 🚨")
            print(f"Score: {score}/10")
            print(f"Inquiry: {inquiry[:100]}...")
            print("ACTION: Notify Front Desk via SMS/Slack Immediately!")
            print("!"*50 + "\n")
    except ValueError:
        pass 

    return jsonify({"score": score, "verdict": verdict})

# 5. NEW: Dashboard Route
@app.route('/dashboard')
def dashboard():
    leads = []
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            leads = list(reader)
    
    # Reverse so newest leads appear first
    leads.reverse()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clinic Lead Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f4f4f4; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; background: white; }
            th { background: #4CAF50; color: white; padding: 12px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
            tr:hover { background: #f1f1f1; }
            .high-score { background: #ffeb3b; font-weight: bold; }
            .score { font-size: 18px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🏥 Clinic Lead Triage Dashboard</h1>
        <p>Total Leads: {{ total }}</p>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Score</th>
                    <th>Inquiry</th>
                    <th>Verdict (Preview)</th>
                </tr>
            </thead>
            <tbody>
                {% for lead in leads %}
                <tr class="{% if lead.Score|int >= 9 %}high-score{% endif %}">
                    <td>{{ lead.Timestamp }}</td>
                    <td class="score">{{ lead.Score }}/10</td>
                    <td>{{ lead.Inquiry[:100] }}...</td>
                    <td>{{ lead['Full Verdict'][:150] }}...</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """
    return render_template_string(html, leads=leads, total=len(leads))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)