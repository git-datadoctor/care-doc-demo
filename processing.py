from pdf2image import convert_from_bytes
import pytesseract
import spacy
import re
import openai
import os
from PIL import Image
import io

# Initialize NLP model
nlp = spacy.load("en_core_web_sm")

def extract_text(uploaded_file):
    """Extract text from PDF or image using OCR"""
    try:
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read(), dpi=200)
            text = "\n".join([pytesseract.image_to_string(img) for img in images])
        else:
            image = Image.open(io.BytesIO(uploaded_file.read()))
            text = pytesseract.image_to_string(image)
        return clean_text(text)
    except Exception as e:
        return f"OCR Error: {str(e)}"

def clean_text(text):
    """Clean and preprocess OCR output"""
    # Remove excessive line breaks
    text = re.sub(r'(\n\s*)+\n+', '\n\n', text)
    # Remove non-printable characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text.strip()

def analyze_text(text):
    """Analyze text with spaCy NLP"""
    if not text or len(text) < 20:
        return {"error": "Insufficient text for analysis"}
    
    doc = nlp(text)
    
    # Extract medical entities
    medications = list(set([ent.text for ent in doc.ents if ent.label_ == "CHEMICAL"]))
    
    # Identify care protocols
    protocols = []
    protocol_triggers = {
        "Wound Care": r"(wound care|dressing change|ulcer|incision)",
        "Medication Administration": r"(medication|dose|administer|PRN)",
        "Fall Prevention": r"(fall risk|mobility|gait|balance)",
        "Infection Control": r"(infection|sterile|aseptic|sanitize)"
    }
    
    for protocol, regex in protocol_triggers.items():
        if re.search(regex, text, re.I):
            protocols.append(protocol + " Protocol")
    
    # Clinical warnings
    warnings = []
    if re.search(r"\ballerg", text, re.I) and not re.search(r"(no known allergies|nkda)", text, re.I):
        warnings.append("Allergy alert: Documented allergies need verification")
    
    if re.search(r"\bweight\b.*\bloss\b", text, re.I):
        warnings.append("Significant weight loss detected")
    
    # Critical terms
    critical_terms = []
    for term in ["critical", "urgent", "emergency", "stat", "crash"]:
        if re.search(rf"\b{term}\b", text, re.I):
            critical_terms.append(term.upper())
    
    return {
        "medications": medications,
        "protocols": protocols,
        "critical_terms": critical_terms,
        "warnings": warnings
    }

def enhanced_analysis(text):
    """Enhanced analysis using Azure OpenAI"""
    if not os.getenv("OPENAI_API_KEY"):
        return "OpenAI API key not configured"
    
    if not text or len(text) < 20:
        return "Insufficient text for analysis"
    
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a clinical documentation assistant. Analyze the following nursing note. Identify: "
                 "1. Key care protocols needed (bullet points) "
                 "2. Medications mentioned (comma separated) "
                 "3. Critical warnings (if any) "
                 "4. Potential documentation gaps. "
                 "Format using markdown. Be concise."},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI Error: {str(e)}"