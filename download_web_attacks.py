import pandas as pd
from datasets import load_dataset
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def download_web_attacks():
    logger.info("Downloading Web Attacks dataset (SQLi, XSS, Normal) from Hugging Face...")
    ds = load_dataset("shengqin/web-attacks", split="train")
    
    # Convert to pandas dataframe
    df = ds.to_pandas()
    
    # We want to map it to binary classification: 0 for normal, 1 for attack
    # 'text_label' contains 'normal', 'XSS', 'SQLi'
    df['label'] = df['text_label'].apply(lambda x: 0 if x == 'normal' else 1)
    
    # Rename 'Payload' to 'payload' to match pipeline.py
    df.rename(columns={'Payload': 'payload'}, inplace=True)
    
    # Keep only payload and label
    df_final = df[['payload', 'label']]
    
    # Save to ai/datasets/web_attacks.csv
    dest_dir = Path("ai/datasets")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "web_attacks.csv"
    
    logger.info(f"Saving dataset with {len(df_final)} records to {dest_file}...")
    df_final.to_csv(dest_file, index=False)
    logger.info("Web Attacks dataset successfully downloaded and formatted for pipeline.py!")

if __name__ == "__main__":
    download_web_attacks()
