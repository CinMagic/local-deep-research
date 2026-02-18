import os
import csv
import re
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
app = Flask(__name__)
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. Load Prompt
with open("prompts/health-clinics/lead_qualifier_v1.md", "r") as f:
    system_prompt = f.read()

LOG_FILE = "live_lead_log.csv"

# 3. Helper Function: Extract Score from AI Response
def extract_score(text):
    """Looks for patterns like '9/10' or 'Fit Score: 9/10'"""
    match = re.search(r"(\d+)/10", text)
    return match.group(1) if match else "N/A"

# 4. API Endpoint: Triage a Lead
@app.route('/triage', methods=['POST'])
def triage_lead():
    data = request.json
    inquiry = data.get('inquiry', '')
    
    if not inquiry:
        return jsonify({"error": "No inquiry provided"}), 400

    # Run AI Logic
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": inquiry}
        ]
    )
    
    verdict = response.choices[0].message.content
    score = extract_score(verdict)

    # Log to CSV with Structured Columns
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Score", "Inquiry", "Full Verdict"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            score,
            inquiry,
            verdict
        ])

    return jsonify({"score": score, "verdict": verdict})

# 5. Run the Server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)