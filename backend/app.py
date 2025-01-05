from openai import OpenAI
from dotenv import load_dotenv
import os
import boto3
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables from the .env file
load_dotenv()

# OpenAI client initialization
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# AWS Clients
textract = boto3.client("textract", region_name="us-east-1")  # Adjust region if needed
s3 = boto3.client("s3", region_name="us-east-1")  # Adjust region if needed
S3_BUCKET = "insightdocuments-pdfs"  # Set this variable with your bucket name

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('documents.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parsed_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_name TEXT NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call the database initialization function
init_db()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to InsightDocuments Backend!"})

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Debug: Print the files sent in the request
        print("Request files:", request.files)

        # Ensure the request contains a file
        if 'file' not in request.files:
            print("No file part in the request")  # Debugging log
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == "":
            print("No file selected")  # Debugging log
            return jsonify({"error": "No file selected"}), 400

        # Save the file locally
        filepath = os.path.join(app.config.get("UPLOAD_FOLDER"), file.filename)
        file.save(filepath)

        # Parse the PDF with Amazon Textract and save to the database
        document_name = file.filename
        parse_and_store_with_textract(filepath, document_name)

        return jsonify({"message": "File uploaded and parsed successfully!", "filename": file.filename}), 200

    except Exception as e:
        print(f"Error: {str(e)}")  # Debugging log
        return jsonify({"error": str(e)}), 500

# Helper function to parse and store PDF content in the database using Textract
def parse_and_store_with_textract(filepath, document_name):
    conn = sqlite3.connect('documents.db')
    cursor = conn.cursor()

    try:
        with open(filepath, 'rb') as document:
            # Call Textract to extract text from the PDF
            response = textract.analyze_document(
                Document={'Bytes': document.read()},
                FeatureTypes=['TABLES', 'FORMS']  # Adjust features as needed
            )

        # Extract text blocks
        blocks = response.get('Blocks', [])
        page_texts = {}

        for block in blocks:
            if block['BlockType'] == 'LINE':
                page_number = block.get('Page', 1)  # Default to page 1 if not specified
                text = block.get('Text', '')

                if page_number not in page_texts:
                    page_texts[page_number] = []
                page_texts[page_number].append(text)

        # Insert extracted text into the database
        for page_number, lines in page_texts.items():
            content = ' '.join(lines)  # Combine lines into a single string
            cursor.execute('''
                INSERT INTO parsed_content (document_name, page_number, content)
                VALUES (?, ?, ?)
            ''', (document_name, page_number, content))

        conn.commit()
        print(f"Parsed and stored PDF: {document_name}")

    except Exception as e:
        print(f"Error parsing PDF with Textract: {str(e)}")
        raise e

    finally:
        conn.close()

# Query route to handle NLP-based questions
@app.route('/query', methods=['POST'])
def query_document():
    try:
        # Get the question from the request
        data = request.json
        question = data.get("question", "")

        # Call OpenAI ChatCompletion API
        response = client.chat.completions.create(
            model="gpt-4",  # Use the latest model
            messages=[
                {"role": "system", "content": "You are an assistant providing answers about documents."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7,
        )

        # Format the response
        answer = response.choices[0].message.content.strip()

        return jsonify({
            "answer": answer,
            "reference": "This will be linked to a real reference in the future."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)