import os

# Path to your folder containing the .mid files
folder_path = os.path.join('MIDIs')

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith("-.mid"):
        # Create the new filename by removing the dash before ".mid"
        new_filename = filename.replace("-.mid", ".mid")
        
        # Full paths
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)
        
        # Rename the file
        os.rename(old_path, new_path)
        print(f'Renamed: {filename} → {new_filename}')

print("Renaming complete.")
