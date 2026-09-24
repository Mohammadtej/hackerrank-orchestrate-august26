import pandas as pd
import os

# Create dataset_processed if it doesn't exist
os.makedirs("dataset_processed", exist_ok=True)

# Load group members
df = pd.read_csv("dataset/group_members.csv")

# Filter where role is 'admin'
admins = df[df["role"] == "admin"]

# Save to dataset_processed/group_admins.csv
output_path = "dataset_processed/group_admins.csv"
admins.to_csv(output_path, index=False)

print(f"Successfully separated {len(admins)} group admin entries.")
print(f"Saved to: {output_path}")
print(admins.head())
