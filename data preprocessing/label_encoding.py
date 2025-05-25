import pandas as pd

# Define the mapping of disease names to class IDs
disease_mapping = {
    'Spinal Canal Stenosis': 0,
    'Right Neural Foraminal Narrowing': 1,
    'Left Neural Foraminal Narrowing': 2,
}

# Path to the existing CSV file
csv_path = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv\height_width_png_img.csv'  # Path to your CSV file

# Read the existing CSV file into a pandas DataFrame
df = pd.read_csv(csv_path)

# Add the 'class_id_numerical' column based on the 'class_id' (disease name)
df['class_id_numerical'] = df['condition'].map(disease_mapping)

# Save the updated DataFrame back to the same CSV file, overwriting the old one
df.to_csv(csv_path, index=False)

print(f"Updated CSV file saved to {csv_path}")
