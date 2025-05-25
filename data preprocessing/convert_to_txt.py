import pandas as pd
import os

# Constants
OD_INPUT_SIZE = 384  # Example value, replace with your actual OD_INPUT_SIZE
STD_BOX_SIZE = 20  # Example value, replace with your actual STD_BOX_SIZE

# Paths
csv_file_path = r"C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv\height_width_png_img.csv"  # Path to the CSV file
output_folder = r"D:\yolo_model\labels"  # Folder to save the text files

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Read the CSV file
data = pd.read_csv(csv_file_path)

# Iterate over the rows grouped by image_id
for image_id, group in data.groupby('image_id'):
    lines = []
    for _, row in group.iterrows():
        # Extract values
        condition_id = row['class_id_numerical']  # Assuming 'condition' column already contains the numeric condition ID
        image_height = row['image_height']
        image_width = row['image_width']
        x = row['x']
        y = row['y']

        # Perform calculations
        normalized_x = x / image_width
        normalized_y = y / image_height
        new_width = (image_width / OD_INPUT_SIZE) * (STD_BOX_SIZE / image_width)
        new_height = (image_height / OD_INPUT_SIZE) * (STD_BOX_SIZE / image_height)

        # Add line to the text file
        lines.append(f"{condition_id} {normalized_x:.6f} {normalized_y:.6f} {new_width:.6f} {new_height:.6f}")

    # Write to a text file named after the image_id
    txt_file_path = os.path.join(output_folder, f"{image_id}.txt")
    with open(txt_file_path, 'w') as txt_file:
        txt_file.write("\n".join(lines))

    print(f"Created file: {txt_file_path}")

print("Processing complete.")
