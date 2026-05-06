import os
import joblib
import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent / "models"

# Define the CNN-LSTM Architecture for inference
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

class TrafficScorer:
    def __init__(self):
        self.rf_model = None
        self.iso_forest = None
        self.scaler = None
        self.label_encoder = None
        self.dl_model = None
        self.web_tokenizer = None
        self.web_model = None
        self.feature_columns = None
        
        self._load_models()
        
    def _load_models(self):
        try:
            # Network Classical Models
            if (MODELS_DIR / "rf_baseline.pkl").exists():
                self.rf_model = joblib.load(MODELS_DIR / "rf_baseline.pkl")
                self.iso_forest = joblib.load(MODELS_DIR / "iso_forest.pkl")
                self.scaler = joblib.load(MODELS_DIR / "scaler.pkl")
                self.label_encoder = joblib.load(MODELS_DIR / "label_encoder.pkl")
                
                # Load feature layout
                if (MODELS_DIR / "network_features.json").exists():
                    with open(MODELS_DIR / "network_features.json", "r") as f:
                        self.feature_columns = json.load(f)
                
                # Deep Learning Model
                if (MODELS_DIR / "cnn_lstm_model.pth").exists():
                    num_classes = len(self.label_encoder.classes_)
                    input_features = len(self.feature_columns) if self.feature_columns else 5
                    self.dl_model = Hybrid_CNN_LSTM(input_features, num_classes)
                    self.dl_model.load_state_dict(torch.load(MODELS_DIR / "cnn_lstm_model.pth", map_location=torch.device('cpu')))
                    self.dl_model.eval()
                
                logger.info("Successfully loaded network flow models (RF, DL, ISO, Scalers).")
        except Exception as e:
            logger.error(f"Failed to load network models: {e}")

        try:
            # Web NLP Model (DistilBERT)
            web_path = MODELS_DIR / "distilbert_web_attack"
            if web_path.exists():
                self.web_tokenizer = AutoTokenizer.from_pretrained(web_path)
                self.web_model = AutoModelForSequenceClassification.from_pretrained(web_path)
                self.web_model.eval()
                logger.info("Successfully loaded DistilBERT Web Attack model.")
        except Exception as e:
            logger.error(f"Failed to load web NLP model: {e}")

    def analyze_traffic(self, features: dict) -> dict:
        """
        Analyze network packet/flow features and HTTP payloads for threats
        using the advanced multi-model ensemble (IDRS Architecture).
        """
        result = {
            "is_anomaly": False,
            "threat_score": 0.0,
            "label": "Normal",
            "details": "Traffic appears normal."
        }
        
        composite_score = 0.0
        ml_prob = 0.0
        dl_prob = 0.0
        is_anomaly_flow = False
        web_threat_status = "Benign"
        
        # 1. Web Attack Detection (DistilBERT)
        payload = features.get("payload", "")
        if payload and payload != "N/A" and self.web_model and self.web_tokenizer:
            try:
                inputs = self.web_tokenizer(payload, return_tensors="pt", truncation=True, padding=True)
                with torch.no_grad():
                    logits = self.web_model(**inputs).logits
                pred = torch.argmax(logits, dim=1).item()
                
                if pred == 1:
                    web_threat_status = "Malicious"
                    # Web attacks bypass flow scores - direct critical alert
                    result["is_anomaly"] = True
                    result["threat_score"] = 0.95
                    result["label"] = "Web Intrusion (SQLi/XSS)"
                    result["details"] = f"Malicious web payload detected by DistilBERT: '{payload[:30]}...'"
                    return result
            except Exception as e:
                logger.error(f"Error in DistilBERT web attack detection: {e}")

        # 2. Network Flow Detection Ensemble
        if self.rf_model and self.scaler:
            try:
                # Map incoming features to the exact columns the model expects
                model_features = {}
                if self.feature_columns:
                    for col in self.feature_columns:
                        model_features[col] = features.get(col, 0)
                else:
                    # Fallback default feature match
                    model_features = {
                        "Flow_Duration": features.get("Flow_Duration", 1000),
                        "Total_Fwd_Packets": features.get("Total_Fwd_Packets", 10),
                        "Total_Length_Fwd": features.get("Total_Length_Fwd", 100),
                        "Total_Length_Bwd": features.get("Total_Length_Bwd", 100),
                        "Flow_Packets_s": features.get("Flow_Packets_s", 10)
                    }
                    
                df = pd.DataFrame([model_features])
                X_scaled = self.scaler.transform(df)
                
                # Classical ML Prediction
                ml_pred_idx = self.rf_model.predict(X_scaled)[0]
                ml_prob = np.max(self.rf_model.predict_proba(X_scaled)[0])
                threat_label = self.label_encoder.inverse_transform([ml_pred_idx])[0]
                
                # Isolation Forest Anomaly
                is_anomaly_flow = (self.iso_forest.predict(X_scaled)[0] == -1)
                
                # Deep Learning Prediction
                if self.dl_model:
                    with torch.no_grad():
                        X_t = torch.FloatTensor(X_scaled).unsqueeze(1)
                        dl_out = self.dl_model(X_t)
                        dl_prob = torch.softmax(dl_out, dim=1).max().item()
                
                # Composite Scoring
                composite_score = (ml_prob * 0.4) + (dl_prob * 0.4) + (float(is_anomaly_flow) * 0.2)
                
                if composite_score > 0.7 or threat_label != "BENIGN":
                    result["is_anomaly"] = True
                    result["threat_score"] = float(composite_score)
                    result["label"] = threat_label if threat_label != "BENIGN" else "Unknown Anomaly"
                    result["details"] = f"Network flow ensemble flagged with {composite_score*100:.1f}% severity."
                    
            except Exception as e:
                logger.error(f"Error in network anomaly detection ensemble: {e}")
                
        # 3. Fallback mock if nothing is loaded
        if not result["is_anomaly"] and not self.rf_model and not self.web_model:
            return self._mock_predict(features)
            
        return result
            
    def _mock_predict(self, features: dict) -> dict:
        """Fallback mock prediction logic for development."""
        duration = features.get("Flow_Duration", 0)
        packets = features.get("Flow_Packets_s", 0)
        payload = features.get("payload", "")
        
        if "SELECT" in payload.upper() or "<script>" in payload.lower():
            return {"is_anomaly": True, "threat_score": 0.95, "label": "Web Attack (Mock)", "details": "Heuristic triggered"}
            
        score = min((duration / 100) + (packets / 50), 1.0)
        is_anomaly = score > 0.8
        
        return {
            "is_anomaly": is_anomaly,
            "threat_score": score,
            "label": "DOS" if is_anomaly else "Normal",
            "details": "Mock heuristic triggered" if is_anomaly else "Traffic appears normal"
        }

# Singleton instance
scorer = TrafficScorer()
