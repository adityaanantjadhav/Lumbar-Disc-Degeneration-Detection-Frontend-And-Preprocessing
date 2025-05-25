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
    if 'image' not in request.files or 'viewType' not in request.form:
        return jsonify({'error': 'Invalid request'}), 400

    file = request.files['image']
    view_type = request.form['viewType']

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

            # Get processed image with bounding boxes
            processed_image = results[0].plot()

            # Save processed image
            unique_filename = f"processed_{uuid.uuid4().hex}.png"
            save_dir = os.path.join("static", "processed_images")
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, unique_filename)
            cv2.imwrite(file_path, processed_image)

            # Extract prediction details using .item() approach
            predictions = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    class_name = result.names[class_id] if result.names else str(class_id)
                    confidence = box.conf.item()
                    predictions.append({
                        'label': str(class_name),
                        'confidence': float(confidence)  # Ensure native float
                    })

            # Debug print to verify predictions
            print("Stored in session:", predictions)

            # Store predictions in session
            session["predictions"] = predictions

            result_url = url_for('result', filename=unique_filename)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({'redirect': result_url})
            else:
                return redirect(result_url)

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
