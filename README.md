# AI Care Documentation Demo

This Streamlit application demonstrates a basic OCR/NLP pipeline for processing healthcare documentation with AI analysis.

## Features

- 📄 Document scanning for PDF and images
- ✍️ Direct text input for care notes
- 💊 Medication detection
- 🩺 Care protocol identification
- ⚠️ Clinical warning flags
- 🤖 Optional OpenAI integration for enhanced analysis

## Setup

1. Install Tesseract OCR:
   - **Windows**: Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Mac**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\activate  # Windows