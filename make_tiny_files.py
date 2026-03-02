# As the raw data for regular_alt_battery is too large, we have to make it lightweight for documenting 
# So this is taking every 100th row 

import pandas as pd
import os

input_folder = 'regular_alt_batteries' 
# This is the new folder we will create for GitHub
output_folder = 'processed_data' 

# We take every 100th row to make the file size ~100x smaller
n = 100 

# Create the processed_data folder if it doesn't exist yet
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created folder: {output_folder}")

# 2. THE LOOP: PROCESS ALL 15 FILES
print("Starting the slimming process...")

for filename in os.listdir(input_folder):
    # Only look for CSV files
    if filename.endswith(".csv"):
        print(f"Reading {filename}...")
        
        # Load the large file
        path = os.path.join(input_folder, filename)
        df = pd.read_csv(path)
        
        # Downsample: Keep every 100th row
        # This keeps the data shape but removes the bulk
        df_tiny = df[::n].copy()
        
        # Save to the new 'processed_data' folder
        output_path = os.path.join(output_folder, filename)
        df_tiny.to_csv(output_path, index=False)
        
        print(f"Success! {filename} is now tiny.")

print("\nFinished! You can now use the files in 'processed_data' for GitHub.")