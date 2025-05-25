import os
import pandas as pd
from PIL import Image

# Load your CSV file
csv_path =r"C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv\filtered_merged_sagittal_series.csv"  # Replace with your actual CSV file path
images_folder =r'D:\all_sagitial_png_images'  # Folder where images are stored

# Load the CSV into a DataFrame
df = pd.read_csv(csv_path)

# Initialize new columns for height and width
df['image_height'] = None
df['image_width'] = None

# Iterate over each row in the DataFrame
for idx in range(len(df)):
    image_id = df.loc[idx, 'image_id']
    image_path = os.path.join(images_folder, f"{image_id}.png")  # Adjust extension if necessary

    # Check if the image ID is the same as the previous row to avoid recalculating dimensions
    if idx > 0 and df.loc[idx, 'image_id'] == df.loc[idx - 1, 'image_id']:
        # Copy dimensions from the previous row
        df.loc[idx, 'image_height'] = df.loc[idx - 1, 'image_height']
        df.loc[idx, 'image_width'] = df.loc[idx - 1, 'image_width']
    else:
        # If the image exists, open it and calculate dimensions
        if os.path.exists(image_path):
            try:
                # Open the image and get dimensions
                with Image.open(image_path) as img:
                    width, height = img.size
                    # Update DataFrame for the current row
                    df.loc[idx, 'image_height'] = height
                    df.loc[idx, 'image_width'] = width
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        else:
            print(f"Image not found: {image_path}")

# Save the updated DataFrame to a new CSV file
output_csv_path = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv\height_width_png_img.csv'  # Specify where you want to save the updated CSV
df.to_csv(output_csv_path, index=False)
print("Updated CSV saved successfully.")