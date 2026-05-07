import os
import json
import joblib
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc, 
    precision_recall_curve, average_precision_score, f1_score, accuracy_score
)
from sklearn.preprocessing import label_binarize
from torch.utils.data import DataLoader, TensorDataset
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset as TorchDataset

# Setup Paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "evaluation_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set style for "Scientific Paper" look
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.5)
# Custom color palette
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

# -------------------------
# DL Architecture (Must match pipeline.py)
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
# NLP Dataset (Must match pipeline.py)
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
# Helper Functions
# -------------------------
def save_plot(filename):
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")

def plot_confusion_matrix(y_true, y_pred, classes, title, filename):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title(title, fontsize=18, pad=20)
    plt.ylabel('Actual Label', fontsize=14)
    plt.xlabel('Predicted Label', fontsize=14)
    save_plot(filename)

def plot_roc_curves(y_true, y_score, classes, title, filename):
    plt.figure(figsize=(10, 8))
    
    # Binarize labels for multi-class ROC
    n_classes = len(classes)
    if n_classes > 2:
        y_true_bin = label_binarize(y_true, classes=range(n_classes))
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_score[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, lw=2, label=f'Class {classes[i]} (AUC = {roc_auc:.2f})')
    else:
        fpr, tpr, _ = roc_curve(y_true, y_score[:, 1])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, color='darkorange', label=f'ROC curve (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=14)
    plt.ylabel('True Positive Rate', fontsize=14)
    plt.title(title, fontsize=18, pad=20)
    plt.legend(loc="lower right")
    save_plot(filename)

def plot_feature_importance(model, feature_names, filename):
    importances = model.feature_importances_
    indices = np.argsort(importances)[-15:] # Top 15
    
    plt.figure(figsize=(12, 8))
    plt.title('Top 15 Feature Importances (Random Forest)', fontsize=18, pad=20)
    plt.barh(range(len(indices)), importances[indices], color='#3498db', align='center')
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Relative Importance', fontsize=14)
    save_plot(filename)

# -------------------------
# Evaluation logic
# -------------------------
def main():
    print("Starting evaluation and visualization...")
    
    # 1. Load Data
    data_path = DATA_DIR / "network_traffic.parquet"
    if not data_path.exists():
        print("Data not found, cannot proceed.")
        return

    df = pd.read_parquet(data_path)
    if 'attack_label' in df.columns:
        df.rename(columns={'attack_label': 'Label'}, inplace=True)
    
    # Sample for evaluation (consistent with training)
    df = df.sample(n=10000, random_state=42)
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    
    X = df.drop('Label', axis=1)
    X = X.select_dtypes(include=[np.number])
    y = df['Label']
    
    # Load Preprocessing Artifacts
    le = joblib.load(MODELS_DIR / "label_encoder.pkl")
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    with open(MODELS_DIR / "network_features.json", "r") as f:
        feature_names = json.load(f)

    # Align features
    X = X[feature_names]
    X_scaled = scaler.transform(X)
    y_enc = le.transform(y)
    
    # 2. Random Forest Evaluation
    print("Evaluating Random Forest...")
    rf = joblib.load(MODELS_DIR / "rf_baseline.pkl")
    rf_preds = rf.predict(X_scaled)
    rf_probs = rf.predict_proba(X_scaled)
    
    plot_confusion_matrix(y_enc, rf_preds, le.classes_, "Random Forest Confusion Matrix", "rf_cm.png")
    plot_roc_curves(y_enc, rf_probs, le.classes_, "Random Forest ROC Curves", "rf_roc.png")
    plot_feature_importance(rf, feature_names, "rf_feature_importance.png")

    # 3. CNN-LSTM Evaluation
    print("Evaluating CNN-LSTM...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dl_model = Hybrid_CNN_LSTM(input_features=len(feature_names), num_classes=len(le.classes_))
    dl_model.load_state_dict(torch.load(MODELS_DIR / "cnn_lstm_model.pth", map_location=device))
    dl_model.to(device)
    dl_model.eval()
    
    X_t = torch.FloatTensor(X_scaled).unsqueeze(1).to(device)
    with torch.no_grad():
        logits = dl_model(X_t)
        dl_probs = torch.softmax(logits, dim=1).cpu().numpy()
        dl_preds = np.argmax(dl_probs, axis=1)
    
    plot_confusion_matrix(y_enc, dl_preds, le.classes_, "Hybrid CNN-LSTM Confusion Matrix", "cnn_lstm_cm.png")
    plot_roc_curves(y_enc, dl_probs, le.classes_, "Hybrid CNN-LSTM ROC Curves", "cnn_lstm_roc.png")

    # 4. Isolation Forest Evaluation
    print("Evaluating Isolation Forest...")
    iso = joblib.load(MODELS_DIR / "iso_forest.pkl")
    scores = iso.decision_function(X_scaled)
    
    plt.figure(figsize=(10, 6))
    plt.hist(scores[y == 'BENIGN'], bins=50, alpha=0.5, label='Normal', color='blue', density=True)
    plt.hist(scores[y != 'BENIGN'], bins=50, alpha=0.5, label='Attack', color='red', density=True)
    plt.title("Anomaly Score Distribution (Isolation Forest)", fontsize=18, pad=20)
    plt.xlabel("Score (Lower = More Anomalous)", fontsize=14)
    plt.legend()
    save_plot("iso_forest_dist.png")

    # 5. DistilBERT Web Attack Evaluation
    print("Evaluating DistilBERT...")
    web_attacks_path = DATA_DIR / "web_attacks.csv"
    if web_attacks_path.exists():
        web_df = pd.read_csv(web_attacks_path).sample(min(1000, len(pd.read_csv(web_attacks_path))), random_state=42)
        model_path = MODELS_DIR / "distilbert_web_attack"
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        web_model = AutoModelForSequenceClassification.from_pretrained(model_path)
        web_model.to(device)
        web_model.eval()
        
        inputs = tokenizer(web_df['payload'].tolist(), truncation=True, padding=True, max_length=128, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = web_model(**inputs)
            web_probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()
            web_preds = np.argmax(web_probs, axis=1)
            
        plot_confusion_matrix(web_df['label'], web_preds, ["Benign", "Attack"], "DistilBERT Confusion Matrix", "distilbert_cm.png")
        plot_roc_curves(web_df['label'], web_probs, ["Benign", "Attack"], "DistilBERT ROC Curve", "distilbert_roc.png")
    
    # 6. Comparative Bar Chart (Accuracy/F1)
    print("Generating performance summary...")
    metrics = {
        "Model": ["Random Forest", "CNN-LSTM"],
        "Accuracy": [
            accuracy_score(y_enc, rf_preds),
            accuracy_score(y_enc, dl_preds)
        ],
        "F1-Score": [
            f1_score(y_enc, rf_preds, average='weighted'),
            f1_score(y_enc, dl_preds, average='weighted')
        ]
    }
    m_df = pd.DataFrame(metrics)
    m_df_melted = m_df.melt(id_vars="Model", var_name="Metric", value_name="Score")
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=m_df_melted, x="Model", y="Score", hue="Metric", palette="viridis")
    plt.ylim(0, 1.1)
    plt.title("Performance Comparison: RF vs CNN-LSTM", fontsize=18, pad=20)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    save_plot("model_comparison.png")

    print("\n--- All visualizations generated in 'ai/evaluation_results' ---")

if __name__ == "__main__":
    main()
