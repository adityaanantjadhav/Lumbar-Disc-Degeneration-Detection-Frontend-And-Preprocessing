import io
import os
import uuid
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from ultralytics import YOLO

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for sessions
CORS(app, supports_credentials=True)

# Load YOLO models for sagittal and axial views
sagittal_model = YOLO(r"E:\New project final year\Newest Models\sagittal\weights\best.pt")
axial_model = YOLO(r"E:\New project final year\Newest Models\axial\weights\best.pt")

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            # Read and decode image
            image_bytes = file.read()
            image = np.asarray(bytearray(image_bytes), dtype=np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Failed to read the image. The file may not be a valid image.")

            # Select model based on view type
            model = sagittal_model if view_type == 'sagittal' else axial_model

            # Run detection
            results = model(image)

            # Get processed image
            processed_image = results[0].plot()

            # Get original file extension
            extension = file.filename.rsplit('.', 1)[1].lower()

            # Save processed image with unique userId_count.ext format
            save_dir = os.path.join("static", "processed_images")
            os.makedirs(save_dir, exist_ok=True)

            # Find next available counter for this user
            existing_files = [f for f in os.listdir(save_dir) if f.startswith(f"{user_id}_") and f.endswith(f".{extension}")]
            existing_counts = [int(f.split('_')[1].split('.')[0]) for f in existing_files if '_' in f and f.split('_')[1].split('.')[0].isdigit()]
            next_count = max(existing_counts) + 1 if existing_counts else 1

            filename = f"{user_id}_{next_count}.{extension}"
            file_path = os.path.join(save_dir, filename)

            cv2.imwrite(file_path, processed_image)

            # Extract predictions
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    class_name = result.names[class_id] if result.names else str(class_id)
                    confidence = box.conf.item()
                    predictions.append({
                        'label': str(class_name),
                        'confidence': float(confidence)
                    })

            return jsonify({
                'imageName': filename,
                'predictions': predictions
            })

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed to process the image. Please try again later.'}), 500
    else:
        return jsonify({'error': 'Invalid file format'}), 400


@app.route('/result')
def result():
    filename = request.args.get('filename')
    if not filename:
        return "No image to display", 400
    # Generate the image URL using Flask's url_for function
    image_url = url_for('static', filename='processed_images/' + filename)
    # Retrieve the prediction details from the session
    predictions = session.get("predictions", [])
    return render_template('result.html', image_url=image_url, predictions=predictions)

if __name__ == "__main__":
    app.run(debug=True)
