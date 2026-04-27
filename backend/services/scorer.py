import os
import joblib
import pandas as pd
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "rf_model.pkl"

class TrafficScorer:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Loaded model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning("No trained model found. Running in mock mode.")
            
    def analyze_traffic(self, features: dict) -> dict:
        """
        Analyze network packet/flow features and return threat score/label.
        """
        # If no model is loaded, we fallback to a mock heuristic
        if self.model is None:
            return self._mock_predict(features)
            
        try:
            # Prepare data
            df = pd.DataFrame([features])
            
            # Predict
            prediction = self.model.predict(df)[0]
            # Since model outputs integer classes, mapping back might be required
            proba = self.model.predict_proba(df)[0]
            
            # Assuming class 0 is BENIGN and class 1+ are Anomalies
            is_anomaly = (prediction != 0)
            threat_score = float(max(proba)) if is_anomaly else (1 - float(proba[0]))
            
            return {
                "is_anomaly": is_anomaly,
                "threat_score": threat_score,
                "label": "ANOMALY" if is_anomaly else "Normal",
                "details": f"Model identified cluster {prediction}"
            }
        except Exception as e:
            logger.error(f"Error analyzing traffic: {e}")
            return self._mock_predict(features)
            
    def _mock_predict(self, features: dict) -> dict:
        """Fallback mock prediction logic for development."""
        # Simple heuristic on mock data
        duration = features.get("Flow_Duration", 0)
        packets = features.get("Flow_Packets_s", 0)
        
        # Fake a threat score
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
