import pandas as pd

# Path to your existing CSV file
csv_path = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv_files\filtered_merged_axaial_series.csv'

# Load the CSV file into a DataFrame
df = pd.read_csv(csv_path)

# Drop duplicate rows based on the 'image_id' column and keep the first occurrence
unique_df = df.drop_duplicates(subset='image_id')

# Path to save the new CSV file with unique entries
output_csv_path = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv_files\unique_image_axaial_images_id.csv'

# Save the DataFrame with unique entries to a new CSV file
unique_df.to_csv(output_csv_path, index=False)

print(f"CSV file with unique image entries has been saved to: {output_csv_path}")
