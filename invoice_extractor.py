import pdfplumber
import json
import glob
import os
from dotenv import load_dotenv
import google.genai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)

# Load the PDF
def load_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Clean the text
def clean_text(raw_text):
    lines = raw_text.split("\n")
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return " ".join(cleaned_lines)

# Build the prompt
def build_prompt(cleaned_text):
    return f"""
You are an invoice data extractor.
Extract the following fields from the provided invoice text.
If a field is missing, return null.
Output must be valid JSON with these exact keys:

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

# Call Gemini
def call_gemini(prompt):
    # Use a supported model name from list_models()
    model = genai.GenerativeModel("models/gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# Parse JSON
def parse_json(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        print("Error: Response was not valid JSON")
        return None

# Display output
def display_output(data):
    if data:
        for key, value in data.items():
            print(f"{key}: {value}")

# Run pipeline
def run_pipeline(file_path):
    raw_text = load_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    prompt = build_prompt(cleaned_text)
    response_text = call_gemini(prompt)
    data = parse_json(response_text)
    display_output(data)
    return data

# Batch process
if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)

    for file_path in glob.glob("invoices/*.pdf"):
        print(f"\nProcessing: {file_path}")
        result = run_pipeline(file_path)

        if result:
            base_name = os.path.basename(file_path).replace(".pdf", "")
            output_path = f"outputs/output_{base_name}.json"

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"Saved extracted data to {output_path}")
