import io
import os
import uuid
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from ultralytics import YOLO
import pydicom  # For DICOM handling

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for sessions
CORS(app, supports_credentials=True)

# Load YOLO models for sagittal and axial views
sagittal_model = YOLO(r"E:\New project final year\Newest Models\sagittal\weights\best.pt")
axial_model = YOLO(r"E:\New project final year\Newest Models\axial\weights\best.pt")

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'dcm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def dicom_to_image(file_stream):
    """
    If the uploaded file is DICOM, convert to a numpy image (BGR) for processing.
    """
    print("Dicom conversion start")
    ds = pydicom.dcmread(io.BytesIO(file_stream))
    arr = ds.pixel_array
    arr = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    image = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
    print("Dicom conversion end")
    return image


def apply_clahe(image):
    """
    Apply CLAHE to the image for better contrast.
    Works on color images: converts to LAB, applies CLAHE on L-channel.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    final = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return final

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files or 'viewType' not in request.form or 'userId' not in request.form:
        return jsonify({'error': 'Invalid request'}), 400

    file = request.files['image']
    view_type = request.form['viewType']
    user_id = request.form['userId']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            image_bytes = file.read()
            ext = file.filename.rsplit('.',1)[1].lower()
            if ext == 'dcm':
                image = dicom_to_image(image_bytes)
                extension = 'png'
            else:
                arr = np.asarray(bytearray(image_bytes), dtype=np.uint8)
                image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                extension = ext

            if image is None:
                raise ValueError("Failed to read the image. The file may not be valid.")

            # Apply CLAHE
            image = apply_clahe(image)

            model = sagittal_model if view_type == 'sagittal' else axial_model
            results = model(image)
            processed_image = results[0].plot()

            save_dir = os.path.join("static", "processed_images")
            os.makedirs(save_dir, exist_ok=True)

            existing_files = [f for f in os.listdir(save_dir)
                              if f.startswith(f"{user_id}_") and f.endswith(f".{extension}")]
            existing_counts = [int(f.split('_')[1].split('.')[0]) 
                               for f in existing_files if '_' in f and f.split('_')[1].split('.')[0].isdigit()]
            next_count = max(existing_counts) + 1 if existing_counts else 1

            filename = f"{user_id}_{next_count}.{extension}"
            file_path = os.path.join(save_dir, filename)
            cv2.imwrite(file_path, processed_image)

            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    class_name = result.names[class_id] if result.names else str(class_id)
                    confidence = box.conf.item()
                    predictions.append({'label': class_name, 'confidence': confidence})

            return jsonify({'imageName': filename, 'predictions': predictions})

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed to process the image.'}), 500
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@app.route('/result')
def result():
    filename = request.args.get('filename')
    if not filename:
        return "No image to display", 400
    image_url = url_for('static', filename='processed_images/' + filename)
    predictions = session.get("predictions", [])
    return render_template('result.html', image_url=image_url, predictions=predictions)

if __name__ == "__main__":
    app.run(debug=True)
