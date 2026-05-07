import os
import time
import json
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Classical ML & Preprocessing
import joblib
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE

# Deep Learning
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Transformers (Web Attacks)
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset as TorchDataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# DL Architecture
# -------------------------
class Hybrid_CNN_LSTM(nn.Module):
    def __init__(self, input_features, num_classes):
        super(Hybrid_CNN_LSTM, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=2, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        self.lstm = nn.LSTM(input_size=16, hidden_size=32, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        out = self.cnn(x)
        out = out.permute(0, 2, 1)
        out, _ = self.lstm(out)
        out = out[:, -1, :]
        out = self.fc(out)
        return out

# -------------------------
# NLP Dataset
# -------------------------
class WebAttackDataset(TorchDataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(texts.tolist(), truncation=True, padding=True, max_length=max_length)
        self.labels = labels.tolist()

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

# -------------------------
# Training Functions
# -------------------------
def train_network_models():
    """Trains RF Baseline, Isolation Forest, and CNN-LSTM on Flow Data."""
    logger.info("--- Starting Network Traffic Model Training ---")
    
    data_path_csv = DATA_DIR / "network_traffic.csv"
    data_path_parquet = DATA_DIR / "network_traffic.parquet"
    
    if data_path_parquet.exists():
        logger.info("Loading real network data from Parquet file...")
        df = pd.read_parquet(data_path_parquet)
        if 'attack_label' in df.columns:
            df.rename(columns={'attack_label': 'Label'}, inplace=True)
            # The CIC-IDS dataset has many columns. We'll sample it to avoid memory issues during training.
            if len(df) > 50000:
                logger.info("Dataset is very large. Sampling 50,000 rows for faster training...")
                df = df.sample(n=50000, random_state=42)
    elif data_path_csv.exists():
        logger.info("Loading real network data from CSV file...")
        df = pd.read_csv(data_path_csv)
    else:
        logger.warning("No real network data found. Generating synthetic dummy data.")
        np.random.seed(42)
        n_samples = 5000
        df = pd.DataFrame({
            'Flow_Duration': np.random.randint(10, 10000, n_samples),
            'Total_Fwd_Packets': np.random.randint(1, 100, n_samples),
            'Total_Length_Fwd': np.random.randint(40, 5000, n_samples),
            'Total_Length_Bwd': np.random.randint(0, 10000, n_samples),
            'Flow_Packets_s': np.random.uniform(0.1, 1000, n_samples),
            'Label': np.random.choice(['BENIGN', 'DoS', 'PortScan', 'BruteForce'], p=[0.7, 0.15, 0.1, 0.05], size=n_samples)
        })

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
        
    X = df.drop('Label', axis=1)
    # Ensure all features are numeric
    X = X.select_dtypes(include=[np.number])
    y = df['Label']

    # Filter out classes with too few samples for SMOTE (minimum 6 samples needed for default k_neighbors=5)
    counts = y.value_counts()
    keep_classes = counts[counts >= 6].index
    if len(keep_classes) < len(counts):
        logger.info(f"Removing classes with < 6 samples: {list(set(counts.index) - set(keep_classes))}")
        mask = y.isin(keep_classes)
        X = X[mask]
        y = y[mask]
    
    # 1. Preprocessing
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X_scaled, y_enc)
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42)
    
    # 2. RF Baseline
    logger.info("Training Random Forest Classifier...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    logger.info(f"RF Accuracy: {rf_acc:.4f}")
    
    # 3. Isolation Forest (Anomaly)
    logger.info("Training Isolation Forest (Unsupervised)...")
    iso = IsolationForest(contamination=0.05, random_state=42)
    # Train only on NORMAL data
    X_normal = X_scaled[y_enc == le.transform(['BENIGN'])[0]]
    iso.fit(X_normal)
    
    # 4. DL CNN-LSTM
    logger.info("Training Hybrid CNN-LSTM Model...")
    X_train_t = torch.FloatTensor(X_train).unsqueeze(1)
    X_test_t = torch.FloatTensor(X_test).unsqueeze(1)
    y_train_t = torch.LongTensor(y_train)
    
    train_loader = DataLoader(TensorDataset(X_train_t, y_train_t), batch_size=64, shuffle=True)
    dl_model = Hybrid_CNN_LSTM(input_features=X.shape[1], num_classes=len(le.classes_))
    optimizer = optim.Adam(dl_model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    dl_model.train()
    for epoch in range(3): # Short epoch for demo/speed
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            out = dl_model(batch_x)
            loss = criterion(out, batch_y)
            loss.backward()
            optimizer.step()
    logger.info("CNN-LSTM Training Complete.")
    
    # Save all network models
    joblib.dump(rf, MODELS_DIR / "rf_baseline.pkl")
    joblib.dump(iso, MODELS_DIR / "iso_forest.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    joblib.dump(le, MODELS_DIR / "label_encoder.pkl")
    torch.save(dl_model.state_dict(), MODELS_DIR / "cnn_lstm_model.pth")
    # Also save the feature columns order so the backend knows what to expect
    with open(MODELS_DIR / "network_features.json", "w") as f:
        json.dump(list(X.columns), f)
        
    logger.info("All Network Flow models saved successfully.")

def train_web_model():
    """Trains DistilBERT on Web Attacks dataset."""
    logger.info("--- Starting DistilBERT Fine-tuning for Web Attacks ---")
    
    web_attacks_path = DATA_DIR / "web_attacks.csv"
    if not web_attacks_path.exists():
        logger.warning(f"Web attacks dataset not found. Mocking data for demonstration.")
        df = pd.DataFrame({
            "payload": ["SELECT * FROM users", "hello world", "<script>alert(1)</script>", "good morning"], 
            "label": [1, 0, 1, 0]
        })
    else:
        df = pd.read_csv(web_attacks_path)
        
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    X = df['payload']
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_dataset = WebAttackDataset(X_train, y_train, tokenizer)
    val_dataset = WebAttackDataset(X_test, y_test, tokenizer)
    
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
    
    # Supress massive huggingface logs
    logging.getLogger("transformers").setLevel(logging.ERROR)
    
    training_args = TrainingArguments(
        output_dir=str(MODELS_DIR / 'results'),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir=str(MODELS_DIR / 'logs'),
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        disable_tqdm=False
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )
    
    logger.info("Fine-tuning DistilBERT...")
    trainer.train()
    
    save_path = MODELS_DIR / "distilbert_web_attack"
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    logger.info(f"DistilBERT web attack model saved to {save_path}.")

def run_pipeline():
    start_time = time.time()
    logger.info("=== IDRS Full Training Pipeline Started ===")
    train_network_models()
    train_web_model()
    logger.info(f"=== IDRS Pipeline Completed in {(time.time() - start_time):.2f}s ===")

if __name__ == "__main__":
    run_pipeline()
