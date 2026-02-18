# 🏥 Health Clinic Lead Audit Engine (v1.0)

## 🎯 Purpose
To provide a "Strategic Operational Audit" for health and wellness clinics. This engine identifies high-value, urgent patient leads that are often missed or delayed by manual front-desk triage.

## 🧠 The Logic (The Brain)
- **File:** `prompts/health-clinics/lead_qualifier_v1.md`
- **Function:** Acts as a Senior Intake Specialist.
- **Criteria:** Grades leads on a 1-10 scale based on:
  1. **Clinical Fit:** Does the condition match clinic expertise?
  2. **Urgency:** Acute injury vs. chronic maintenance.
  3. **Financial Value:** Insurance status and readiness to start.

## ⚙️ The Components (The Machine)
1. **`test_clinic_logic.py`**: The "Single-Lead Tester." Used to refine the prompt logic without wasting API credits on large batches.
2. **`clinic_batch_audit.py`**: The "Production Engine." Reads a CSV of raw inquiries and outputs a structured Audit Report.
3. **`clinic_leads.csv`**: The raw data input (Patient inquiries).
4. **`clinic_audit_results.csv`**: The final product. A graded list of leads with "Recommended Actions" and "Draft Messages."

## 🛠️ Technical Stack
- **Language:** Python 3
- **API Gateway:** RouteLLM (via Abacus.AI)
- **Model:** GPT-4o (Configurable via script)
- **Environment:** GitHub Codespaces (Cloud-based dev environment)

## 🆘 Troubleshooting (The Kill Switch)
- **Port Hangs:** `lsof -i :5000` -> `kill -9 <PID>`
- **Process Reset:** `pkill -f python`
- **Environment Sync:** Always `git add -f <file>`, `Commit`, and `Sync` before closing.

## Quick Reference: Where Everything Lives

Root (top level of Codespace)

.env
Purpose: Stores RouteLLM keys.
Rule: Local only, never commit.
Content pattern:
OPENAI_API_KEY=...
OPENAI_API_BASE=https://routellm.abacus.ai/v1

test_clinic_logic.py
Role: Single-lead tester.
Use: Quickly check that your prompt + .env + RouteLLM all work.
Run:
python3 test_clinic_logic.py

clinic_leads.csv
Role: Batch input.
Use: Dump raw lead inquiries (from a clinic’s export, or sample data) to audit.

clinic_batch_audit.py
Role: Batch runner (the Engine).
Use: Reads clinic_leads.csv, applies your prompt to each row, writes results.
Run:
python3 clinic_batch_audit.py

clinic_audit_results.csv
Role: Batch output (the Product).
Use: Open in Excel / Sheets to show the clinic:
Fit Score / Urgency / Potential Value (inside the AI’s narrative)
Recommended Action
Draft Message

Repo (inside project folders)
prompts/health-clinics/lead_qualifier_v1.md
Role: Your clinic triage strategy (IP).
Use: Defines how the AI grades leads (Fit, Urgency, Value).
Used by both test_clinic_logic.py and clinic_batch_audit.py.
Rule: This is committed and versioned. Future versions become v2, v3, etc.


