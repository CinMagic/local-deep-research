import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load your RouteLLM Keys from the .env file
load_dotenv()
client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 2. Load your Proprietary Clinic Prompt
prompt_path = "prompts/health-clinics/lead_qualifier_v1.md"

if os.path.exists(prompt_path):
    with open(prompt_path, "r") as f:
        system_prompt = f.read()
    print(f"Successfully loaded prompt from: {prompt_path}")
else:
    print(f"ERROR: {prompt_path} not found!")
    exit()

# 3. Run a Test Lead (Simulating a real clinic inquiry)
test_inquiry = "Inquiry: I have chronic back pain for 3 years. I've tried everything. I'm ready to start treatment immediately and have insurance."

print("Sending inquiry to AI...")

try:
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": test_inquiry}
        ]
    )
    print("\n" + "="*30)
    print("--- CLINIC AUDIT RESULT ---")
    print("="*30)
    print(response.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {e}")