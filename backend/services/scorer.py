import os
import joblib
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
NETWORK_MODEL_PATH = MODELS_DIR / "rf_model.pkl"
WEB_MODEL_PATH = MODELS_DIR / "web_model.pkl"

class TrafficScorer:
    def __init__(self):
        self.network_model = None
        self.web_model = None
        self._load_models()
        
    def _load_models(self):
        if NETWORK_MODEL_PATH.exists():
            try:
                self.network_model = joblib.load(NETWORK_MODEL_PATH)
                logger.info(f"Loaded network model from {NETWORK_MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load network model: {e}")
        else:
            logger.warning("No trained network model found.")
            
        if WEB_MODEL_PATH.exists():
            try:
                self.web_model = joblib.load(WEB_MODEL_PATH)
                logger.info(f"Loaded web attack model from {WEB_MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load web attack model: {e}")
        else:
            logger.warning("No trained web attack model found.")
            
    def analyze_traffic(self, features: dict) -> dict:
        """
        Analyze network packet/flow features and HTTP payloads for threats.
        """
        result = {
            "is_anomaly": False,
            "threat_score": 0.0,
            "label": "Normal",
            "details": "Traffic appears normal."
        }
        
        # 1. Web Attack Detection (SQLi, XSS)
        payload = features.get("payload", "")
        if payload and self.web_model:
            try:
                pred = self.web_model.predict([payload])[0]
                proba = self.web_model.predict_proba([payload])[0]
                
                if pred == 1:
                    result["is_anomaly"] = True
                    result["threat_score"] = float(proba[1])
                    result["label"] = "Web Attack (SQLi/XSS)"
                    result["details"] = f"Malicious payload detected: '{payload[:30]}...'"
                    return result  # Priority return for web attacks
            except Exception as e:
                logger.error(f"Error in web attack detection: {e}")
                
        # 2. Network Anomaly Detection
        if self.network_model:
            try:
                # Expecting: Flow_Duration, Flow_Packets_s, Total_Length_Fwd, Total_Length_Bwd
                # Map incoming generic features to what model expects
                model_features = {
                    "Flow_Duration": features.get("Flow_Duration", 1000),
                    "Flow_Packets_s": features.get("Flow_Packets_s", 10),
                    "Total_Length_Fwd": features.get("Total_Length_Fwd", 100),
                    "Total_Length_Bwd": features.get("Total_Length_Bwd", 100)
                }
                df = pd.DataFrame([model_features])
                
                prediction = self.network_model.predict(df)[0]
                proba = self.network_model.predict_proba(df)[0]
                
                if prediction != 0:
                    result["is_anomaly"] = True
                    result["threat_score"] = float(max(proba))
                    label_map = {1: "DoS", 2: "PortScan"}
                    result["label"] = label_map.get(prediction, f"Anomaly Type {prediction}")
                    result["details"] = f"Network anomaly detected with confidence {result['threat_score']:.2f}"
            except Exception as e:
                logger.error(f"Error in network anomaly detection: {e}")
                
        # 3. Fallback logic if models fail or aren't loaded and basic heuristics trigger
        if not result["is_anomaly"] and (not self.network_model or not self.web_model):
            return self._mock_predict(features)
            
        return result
            
    def _mock_predict(self, features: dict) -> dict:
        """Fallback mock prediction logic for development."""
        duration = features.get("Flow_Duration", 0)
        packets = features.get("Flow_Packets_s", 0)
        payload = features.get("payload", "")
        
        if "SELECT" in payload.upper() or "<script>" in payload.lower():
            return {
                "is_anomaly": True,
                "threat_score": 0.95,
                "label": "Web Attack (Heuristic)",
                "details": "Heuristic triggered for SQLi/XSS"
            }
            
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
