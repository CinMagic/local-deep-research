import os
import csv
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load your RouteLLM Keys
load_dotenv()
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. Load your Proprietary Clinic Prompt
prompt_path = "prompts/health-clinics/lead_qualifier_v1.md"
with open(prompt_path, "r") as f:
    system_prompt = f.read()

# 3. Prepare the Batch Processing
input_file = "clinic_leads.csv"
output_file = "clinic_audit_results.csv"

print(f"Starting Batch Audit on: {input_file}...")

results = []

# 4. Read the Input CSV
with open(input_file, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        lead_id = row['id']
        inquiry = row['inquiry']
        
        print(f"Processing Lead #{lead_id}...")
        
        # 5. Run the AI Logic
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": inquiry}
            ]
        )
        
        ai_verdict = response.choices[0].message.content
        
        # 6. Store the Result
        results.append({
            "id": lead_id,
            "inquiry": inquiry,
            "audit_result": ai_verdict
        })

# 7. Save the Results to a NEW CSV in the Root
with open(output_file, mode='w', newline='', encoding='utf-8') as f:
    fieldnames = ["id", "inquiry", "audit_result"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\nBatch Audit Complete! Results saved to: {output_file}")