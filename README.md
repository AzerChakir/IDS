# AI-based Intrusion Detection and Automated Response System (IDRS)

## 🛡️ Project Overview
This project implements a production-grade **Intrusion Detection and Automated Response System (IDRS)** specifically designed to protect educational web platforms. Leveraging a multi-layered AI architecture, the system detects network-level anomalies and sophisticated web attacks in real-time, providing automated mitigation through an LLM-powered response engine.

## 🚀 Key Features
- **Multi-Model Network Defense**: 
    - **Classical ML Baseline**: Random Forest classifier for high-speed traffic profiling.
    - **Deep Learning Core**: Hybrid **CNN-LSTM** architecture for sequential pattern recognition in network flows.
    - **Anomaly Detection**: Isolation Forest for detecting zero-day threats and unknown traffic patterns.
- **Advanced Web Attack Detection**: 
    - **DistilBERT Transformers**: Fine-tuned NLP model for identifying SQL Injection, XSS, and malicious payloads with high precision.
- **Intelligent Response Engine (RAG + LLM)**: 
    - Integrates **Google Gemini 1.5 Flash** with a **Retrieval-Augmented Generation (RAG)** system to generate context-aware remediation strategies based on security playbooks.
- **Automated Dataset Management**: 
    - Built-in integration with **Hugging Face** to automatically download and process research datasets like **CIC-IDS2017** and **UNSW-NB15**.
- **Real-time Dashboard**: 
    - Modern React-based UI and FastAPI backend for live threat monitoring and statistics.

## 📂 Project Structure
```bash
├── ai/
│   ├── datasets/         # Automated dataset storage (Parquet/CSV)
│   ├── models/           # Trained model artifacts (Weights, Pickles)
│   ├── engine.py         # Real-time inference engine
│   └── pipeline.py       # Full training & fine-tuning pipeline
├── backend/
│   ├── routes/           # API endpoints (FastAPI)
│   └── services/         # Core business logic (DB, RAG, Dashboard)
├── frontend/             # React-based monitoring dashboard
├── tests/                # Automated test suite (PyTest)
├── dataset.py            # Hugging Face dataset utility
└── requirements.txt      # Project dependencies
```

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PCD_IDS
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY="your_google_gemini_key_here"
   ```

## 📈 Usage

### 1. Prepare Data & Train
You can automatically download research data and train all models in one go:
```bash
# 1. Download datasets (CIC-IDS2017)
python download_datasets.py
python download_web_attacks.py

# 2. Run the training pipeline
python ai/pipeline.py
```

### 2. Launch the System
Start the backend API:
```bash
uvicorn backend.main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

Start the Frontend:
```bash
cd frontend
npm run dev
```

## 🧪 Testing
Run the automated test suite to verify the system integrity:
```bash
pytest
```

## 🛡️ Built With
- **FastAPI** - High-performance backend
- **PyTorch** - Deep Learning (CNN-LSTM)
- **Transformers (Hugging Face)** - NLP (DistilBERT)
- **Scikit-Learn** - Classical Machine Learning
- **Google Generative AI** - LLM & RAG Engine
- **React** - Frontend Dashboard
