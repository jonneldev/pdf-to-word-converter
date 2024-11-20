from flask import Flask, request, jsonify, send_file
import logging
import os
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Helper function to check if a file is a valid PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Convert PDF to DOCX using pdf2docx
def convert_pdf_to_docx(pdf_path, output_name):
    try:
        # Generate the output DOCX file path
        docx_output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{output_name}.docx")
        logging.info(f"Starting PDF to DOCX conversion for {pdf_path}...")

        # Initialize pdf2docx converter and convert
        cv = Converter(pdf_path)
        cv.convert(docx_output_path, start=0, end=None)  # Convert entire PDF
        cv.close()

        logging.info(f"PDF to DOCX conversion successful. Output saved at {docx_output_path}")
        return docx_output_path
    except Exception as e:
        logging.error(f"Error during PDF to DOCX conversion for {pdf_path}: {e}")
        return None

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        logging.warning("No file part in the request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.warning("No file selected by the user.")
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            # Secure the filename and save the uploaded file
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            logging.info(f"File uploaded successfully: {pdf_path}")

            # Get the base name of the file (without extension) for output
            base_name = os.path.splitext(filename)[0]

            # Convert PDF to DOCX
            docx_file = convert_pdf_to_docx(pdf_path, base_name)

            if docx_file:
                logging.info(f"File conversion completed successfully. Sending {docx_file} to client.")
                # Return the DOCX file as an attachment
                logging.info(f"Sending file from path: {docx_file}")
                return send_file(
                    docx_file,
                    as_attachment=True,
                    download_name=f"{base_name}.docx",
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
                

            else:
                logging.error("File conversion failed.")
                return jsonify({"error": "Failed to convert file"}), 500

        except Exception as e:
            logging.error(f"Unexpected error during file conversion: {e}")
            return jsonify({"error": str(e)}), 500

    else:
        logging.warning(f"Invalid file type attempted: {file.filename}")
        return jsonify({"error": "Invalid file type. Only PDF is allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000)
