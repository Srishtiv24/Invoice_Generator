import pdfplumber
import json
import glob
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found. Add it to your .env file.")

BASE_URL = "https://openrouter.ai/api/v1"

# List available models
def list_models():
    resp = requests.get(f"{BASE_URL}/models",
                        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"})
    if resp.status_code == 200:
        data = resp.json()
        return [m["id"] for m in data.get("data", [])]
    else:
        print("Error listing models:", resp.text)
        return []

# Pick a usable model
def pick_model(models):
    for candidate in ["openai/gpt-4o-mini", "google/gemini-pro", "anthropic/claude-3-opus"]:
        if candidate in models:
            return candidate
    return models[0] if models else None

# PDF loader
def load_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Clean text
def clean_text(raw_text):
    lines = raw_text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return " ".join(cleaned_lines)

# Build prompt
def build_prompt(cleaned_text):
    return f"""
You are an invoice data extractor.
Return ONLY valid JSON. Do not include explanations or text outside JSON.
The JSON must have these exact keys:

{{
  "invoice_number": null,
  "invoice_date": null,
  "due_date": null,
  "billed_by": null,
  "billed_to": null,
  "line_items": [],
  "subtotal": null,
  "discount": null,
  "tax_or_gst": null,
  "total_amount": null,
  "currency": null,
  "payment_method": null,
  "notes": null
}}

Invoice text:
{cleaned_text}
"""

# Call OpenRouter
def call_openrouter(prompt, model_name):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "response_format": {"type": "json_object"},  # enforce JSON output
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat/completions",
                             headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return None

# Parse JSON
def parse_json(response_text):
    try:
        return json.loads(response_text)
    except Exception:
        print("Error: Response was not valid JSON")
        return None

# Display
def display_output(data):
    if data:
        for key, value in data.items():
            print(f"{key}: {value}")

# Run pipeline
def run_pipeline(file_path, model_name):
    raw_text = load_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    prompt = build_prompt(cleaned_text)
    response_text = call_openrouter(prompt, model_name)
    data = parse_json(response_text)
    display_output(data)
    return data

# Batch process
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)

    models = list_models()
    print("Available models:", models)
    model_name = pick_model(models)
    print("Using model:", model_name)

    for file_path in glob.glob("invoices/*.pdf"):
        print(f"\nProcessing: {file_path}")
        result = run_pipeline(file_path, model_name)

        if result:
            base_name = os.path.basename(file_path).replace(".pdf", "")
            output_path = f"outputs/output_{base_name}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved extracted data to {output_path}")
