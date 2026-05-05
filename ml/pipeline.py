import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, f1_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets"
MODELS_DIR = BASE_DIR.parent / "backend" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def generate_network_data():
    """Generates synthetic network data for the Random Forest model if a real dataset isn't present."""
    logger.info("Generating synthetic network dataset...")
    np.random.seed(42)
    n_samples = 1000
    
    # Features: Flow_Duration, Flow_Packets_s, Total_Length_Fwd, Total_Length_Bwd
    # Label: 0 (Normal), 1 (DoS), 2 (PortScan)
    
    data = {
        'Flow_Duration': np.random.randint(10, 10000, n_samples),
        'Flow_Packets_s': np.random.uniform(0.1, 1000, n_samples),
        'Total_Length_Fwd': np.random.randint(40, 5000, n_samples),
        'Total_Length_Bwd': np.random.randint(0, 10000, n_samples),
        'Label': np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1], size=n_samples)
    }
    
    # Make anomalies statistically distinct
    data['Flow_Duration'] = np.where(data['Label'] == 1, data['Flow_Duration'] * 10, data['Flow_Duration'])
    data['Flow_Packets_s'] = np.where(data['Label'] == 1, data['Flow_Packets_s'] * 50, data['Flow_Packets_s'])
    
    df = pd.DataFrame(data)
    return df

def train_network_model():
    """Trains and fine-tunes a Random Forest model on network data."""
    logger.info("--- Training Network Anomaly Model ---")
    df = generate_network_data()
    X = df.drop('Label', axis=1)
    y = df['Label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Fine-tuning using GridSearchCV
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [None, 10, 20]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='f1_macro')
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    logger.info(f"Best parameters for Network Model: {grid_search.best_params_}")
    
    # Evaluation
    y_pred = best_model.predict(X_test)
    logger.info("\nNetwork Model Evaluation Metrics:")
    logger.info(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    logger.info(f"F1-Score (macro): {f1_score(y_test, y_pred, average='macro'):.4f}")
    logger.info("\n" + classification_report(y_test, y_pred))
    
    # Save model
    model_path = MODELS_DIR / "rf_model.pkl"
    joblib.dump(best_model, model_path)
    logger.info(f"Saved Network Model to {model_path}")

def train_web_attack_model():
    """Trains a pipeline (TF-IDF + Logistic Regression) for SQLi/XSS detection."""
    logger.info("--- Training Web Attack Model ---")
    dataset_path = DATA_DIR / "web_attacks.csv"
    
    if not dataset_path.exists():
        logger.error(f"Web attack dataset not found at {dataset_path}")
        return
        
    df = pd.read_csv(dataset_path)
    X = df['payload']
    y = df['label']
    
    # Train-test split (Note: very small dataset, just for demonstration)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 3), analyzer='char_wb')),
        ('clf', LogisticRegression(random_state=42, class_weight='balanced'))
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluation
    y_pred = pipeline.predict(X_test)
    logger.info("\nWeb Attack Model Evaluation Metrics:")
    logger.info(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    logger.info(f"F1-Score: {f1_score(y_test, y_pred):.4f}")
    logger.info("\n" + classification_report(y_test, y_pred))
    
    # Save model
    model_path = MODELS_DIR / "web_model.pkl"
    joblib.dump(pipeline, model_path)
    logger.info(f"Saved Web Attack Model to {model_path}")

def run_pipeline():
    logger.info("Starting ML Pipeline...")
    train_network_model()
    train_web_attack_model()
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
