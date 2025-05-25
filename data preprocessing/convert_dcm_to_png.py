#convert all acail images to png
import os
import pydicom
import numpy as np
import cv2

# Path to the folder containing DICOM (.dcm) images
dcm_folder = r'D:\dcm_all_axial_images'  # Replace with your DICOM folder path
# Path to the output folder for PNG images
png_folder = r'D:\png_all_axial_images'  # Replace with your PNG folder path

# Create the output folder if it doesn't exist
os.makedirs(png_folder, exist_ok=True)

# Iterate over all DICOM files in the folder
for filename in os.listdir(dcm_folder):
    if filename.lower().endswith('.dcm'):
        # Full path to the DICOM file
        dcm_path = os.path.join(dcm_folder, filename)
        
        # Read the DICOM file
        dcm_image = pydicom.dcmread(dcm_path)
        
        # Convert DICOM pixel array to a numpy array
        image_array = dcm_image.pixel_array
        
        # Normalize the image to 0-255
        image_array = (image_array - np.min(image_array)) / (np.max(image_array) - np.min(image_array)) * 255
        image_array = image_array.astype(np.uint8)
        
        # Save the image as PNG
        png_filename = filename.replace('.dcm', '.png')
        png_path = os.path.join(png_folder, png_filename)
        cv2.imwrite(png_path, image_array)
        print(f"Converted {dcm_path} to {png_path}")

print("Conversion from DICOM to PNG is complete.")
