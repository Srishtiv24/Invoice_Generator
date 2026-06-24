
```markdown
# Invoice Generator

A Python tool to extract structured invoice data from PDF files using AI models via OpenRouter.  
It parses invoice details such as invoice number, dates, totals, line items, and outputs standardized JSON files.

---

## Features
- PDF parsing with `pdfplumber`
- AI‑powered extraction using OpenRouter models (GPT‑4o, Gemini, Claude)
- Structured JSON output
- Batch processing of multiple invoices

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Srishtiv24/Invoice_Generator.git
   cd Invoice_Generator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your OpenRouter API key in `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-your_api_key_here
   ```

4. Place invoice PDFs in the `invoices/` folder.

---

## Usage

Run the extractor:
```bash
python invoice_extractor.py
```
Outputs will be saved in the `outputs/` folder as JSON files.

---
