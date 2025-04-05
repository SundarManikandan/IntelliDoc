import os
import google.generativeai as genai
import docx
import PyPDF2
import pyttsx3
import configparser
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

config = configparser.ConfigParser()
config.read("config.ini")
api_key = config.get("API", "GEMINI_KEY", fallback=None)

if not api_key:
    raise ValueError("API key for Gemini is missing in config.ini")

genai.configure(api_key=api_key)

def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    elif file_path.endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    elif file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    elif file_path.endswith(".csv"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
    return text

def generate_summary_and_title(text):
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = f"""
    Analyze the following document text and provide a suitable title that describes its content.
    Then, summarize the document in 2-3 sentences.

    Text:
    {text[:1000]}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating summary and title: {e}"

#Flask API Endpoints

@app.route('/api/process_document', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            
            temp_file_path = "temp_" + file.filename
            file.save(temp_file_path)

            extracted_text = extract_text(temp_file_path)
            os.remove(temp_file_path)

            if not extracted_text.strip():
                return jsonify({'error': 'Could not extract text from the file'}), 400

            summary_and_title = generate_summary_and_title(extracted_text)

            return jsonify({'extracted_text': extracted_text, 'summary_and_title': summary_and_title})

        except Exception as e:
            return jsonify({'error': f'Error processing the file: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 