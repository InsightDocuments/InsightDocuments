from openai import OpenAI
from dotenv import load_dotenv
import os
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load environment variables from the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import os
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# OpenAI API Configuration

# Test route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to InsightDocuments Backend!"})

# File upload route
@app.route("/upload", methods=["POST"])
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        # Debug: Print the files sent in the request
        print("Request files:", request.files)

        # Ensure the request contains a file
        if "file" not in request.files:
            print("No file part in the request")  # Debugging log
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files["file"]

        if file.filename == "":
            print("No file selected")  # Debugging log
            return jsonify({"error": "No file selected"}), 400

        # Save the file locally
        filepath = os.path.join(app.config.get("UPLOAD_FOLDER", "./uploads"), file.filename)
        file.save(filepath)

        return jsonify({"message": "File uploaded successfully!", "filename": file.filename}), 200

    except Exception as e:
        print("Error:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500
    
# Query route to handle NLP-based questions
@app.route('/query', methods=['POST'])
def query_document():
    try:
        # Get the question from the request
        data = request.json
        question = data.get("question", "")

        # Call OpenAI ChatCompletion API
        response = client.chat.completions.create(model="gpt-4",  # Use the latest model
        messages=[
            {"role": "system", "content": "You are an assistant providing answers about documents."},
            {"role": "user", "content": question}
        ],
        max_tokens=150,
        temperature=0.7)

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