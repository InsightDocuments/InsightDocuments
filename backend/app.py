import os
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure upload folder (local storage for temporary file handling)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# AWS clients
textract = boto3.client('textract', region_name='us-east-1')  # Adjust region if needed
s3 = boto3.client('s3', region_name='us-east-1')  # Adjust region if needed

# Set S3 bucket name here (replace 'insightdocuments-pdfs' with your actual bucket name)
S3_BUCKET = 'insightdocuments-pdfs'  # Set this variable on **line 16**

# Test route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to InsightDocuments Backend!"})

# Upload and extract text route
@app.route('/upload', methods=['POST'])
def upload_file():
    print("Request received at /upload endpoint")  # Debugging
    print("Request files:", request.files)  # Debugging

    if 'file' not in request.files:
        print("No file part in the request")  # Debugging
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        print("No file selected")  # Debugging
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.pdf'):
        print("Invalid file type. Only PDF files are allowed")  # Debugging
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Save the file locally
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    print(f"File saved to {filepath}")  # Debugging

    # Upload the file to S3
    try:
        s3.upload_file(filepath, S3_BUCKET, file.filename)
        print(f"File uploaded to S3: {S3_BUCKET}/{file.filename}")  # Debugging
    except Exception as e:
        print("Error during S3 upload:", e)  # Debugging
        return jsonify({"error": "S3 upload failed", "details": str(e)}), 500

    # Call Textract to analyze the document
    try:
        response = textract.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': S3_BUCKET,
                    'Name': file.filename
                }
            }
        )
        job_id = response['JobId']
        print(f"Textract job started with ID: {job_id}")

        # Polling for the job result
        while True:
            result = textract.get_document_text_detection(JobId=job_id)
            if result['JobStatus'] in ['SUCCEEDED', 'FAILED']:
                break

        if result['JobStatus'] == 'FAILED':
            raise Exception("Text detection job failed")

        # Extract raw text
        extracted_text = []
        for block in result['Blocks']:
            if block['BlockType'] == 'LINE':
                extracted_text.append(block['Text'])
        
        return jsonify({
            "message": f"File {file.filename} uploaded and processed successfully",
            "extracted_text": extracted_text
        }), 200
    except Exception as e:
        print("Error during text extraction:", e)  # Debugging
        return jsonify({"error": "Text extraction failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/query', methods=['POST'])
def query_document():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Mock response for now
    response = {
        "answer": f"Mock answer to the question: '{question}'",
        "reference": "Page 1, Section 2"
    }

    return jsonify(response), 200