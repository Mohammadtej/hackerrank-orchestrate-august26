# Google Colab Setup Cell (Copy-paste this into your first cell in Google Colab):
# !pip install -U -q setfit transformers==4.40.0 datasets
# IMPORTANT: After running the install cell, go to Colab menu: Runtime -> Restart session (or Ctrl+M .) to load the downgraded transformers library!

import os
import json
import pandas as pd
from datasets import Dataset
from setfit import SetFitModel, Trainer, TrainingArguments

# 1. Define paths assuming files are in Google Colab's base folder (/content/)
SAMPLE_CSV = "/content/sample_messages.csv"
AUDIO_JSON = "/content/audio_to_text.json"
IMAGE_JSON = "/content/image_to_text.json"
MODEL_OUTPUT_DIR = "setfit_model"

print(f"Using paths:\n  Sample CSV: {SAMPLE_CSV}\n  Audio JSON: {AUDIO_JSON}\n  Image JSON: {IMAGE_JSON}")

# 2. Load processed audio and image descriptions
with open(AUDIO_JSON, "r") as f:
    audio_to_text = json.load(f)

with open(IMAGE_JSON, "r") as f:
    image_to_text = json.load(f)

# 3. Read sample messages
df = pd.read_csv(SAMPLE_CSV)
print(f"Loaded {len(df)} sample messages.")

# 4. Enrich message text with transcripts/descriptions
def get_enriched_text(row):
    text = str(row["message_text"]) if not pd.isna(row["message_text"]) else ""
    
    # Append visual context for images
    if row["media_type"] == "image":
        media_id = row["media_id"]
        if media_id in image_to_text:
            text += " [Image Context: " + image_to_text[media_id] + "]"
            
    # Append audio transcript for voice notes
    elif row["media_type"] == "voice":
        media_id = row["media_id"]
        audio_key = f"{media_id}.mp3"
        if audio_key in audio_to_text:
            text += " [Audio Transcript: " + audio_to_text[audio_key] + "]"
            
    return text.strip()

df["text"] = df.apply(get_enriched_text, axis=1)

# 5. Map message_type string labels to integer classes
ALLOWED_TYPES = [
    "personal", "urgent", "event", "payment", "business_update",
    "promotion", "greeting", "forward", "spam", "scam", "unknown"
]

label2id = {label: idx for idx, label in enumerate(ALLOWED_TYPES)}
id2label = {idx: label for idx, label in enumerate(ALLOWED_TYPES)}

# Ensure all labels in samples are within ALLOWED_TYPES
df["label"] = df["message_type"].map(label2id)
missing_labels = df[df["label"].isna()]["message_type"].unique()
if len(missing_labels) > 0:
    raise ValueError(f"Found unexpected labels in sample_messages.csv: {missing_labels}")

# 6. Convert to HuggingFace Dataset
train_df = df[["text", "label"]].copy()
dataset = Dataset.from_pandas(train_df)

print("\nSample training data:")
for i in range(min(5, len(dataset))):
    print(f"Text: {dataset[i]['text'][:120]}... -> Label: {id2label[dataset[i]['label']]}")

# 7. Load pre-trained Sentence Transformer model for SetFit
print("\nInitializing SetFit model...")
model = SetFitModel.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2",
    labels=ALLOWED_TYPES
)

# 8. Configure training arguments
training_args = TrainingArguments(
    batch_size=16,
    num_epochs=10, 
    num_iterations=20, 
    use_amp=True
)

# 9. Create Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    metric="accuracy"
)

# 10. Run Training
print("\nStarting SetFit training...")
trainer.train()

# 11. Evaluate on the training set as a sanity check
metrics = trainer.evaluate(dataset)
print(f"\nTraining set self-evaluation metrics: {metrics}")

# 12. Save model weights and class mapping
print(f"\nSaving model to: {MODEL_OUTPUT_DIR}")
trainer.model.save_pretrained(MODEL_OUTPUT_DIR)

# Save the label mapping JSON inside the model directory for easy local loading during inference
mapping_path = os.path.join(MODEL_OUTPUT_DIR, "label_mapping.json")
with open(mapping_path, "w") as f:
    json.dump({"label2id": label2id, "id2label": id2label}, f, indent=2)

print(f"Saved label mappings to: {mapping_path}")
print("Training complete! Zip the 'setfit_model' directory, download it, and extract it here.")

# To easily download from Colab, run this:
# !zip -r setfit_model.zip setfit_model
# from google.colab import files
# files.download('setfit_model.zip')
