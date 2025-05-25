import pandas as pd

# Paths to your CSV files
train_coordinates_csv = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv_files\final_train_label_coordinates.csv'
train_description_csv = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv_files\train_series_descriptions.csv'
output_csv = r'C:\Users\Admin\Documents\FINAL_YEAR_PROJECT\csv_files\filtered_merged_axaial_series.csv'

# Read the CSV files
coordinates_df = pd.read_csv(train_coordinates_csv)
description_df = pd.read_csv(train_description_csv)

# Merge the dataframes on 'study_id' and 'series_id'
merged_df = pd.merge(coordinates_df, description_df, on=['study_id', 'series_id'], how='inner')

# Filter rows where 'series_description' contains 'Axial'
axial_df = merged_df[merged_df['series_description'].str.contains('Axial', case=False, na=False)]

# Save the filtered DataFrame to a new CSV file
axial_df.to_csv(output_csv, index=False)

print("Filtered axial series CSV file created successfully.")
