# AI-based Intrusion Detection and Automated Response System (IDRS)

## Overview
This project proposes the design and implementation of an AI-based Intrusion Detection and Automated Response System (IDRS) specifically tailored for educational web platforms. Educational institutions have increasingly become targets of cyberattacks (data breaches, DoS, SQL injections, XSS). Traditional signature-based systems are no longer sufficient. 

This IDRS uses a dual-model approach and Large Language Models (LLMs) to provide real-time threat detection, automated mitigation, and enhanced system resilience.

## Features
- **Network Anomaly Detection:** Utilizes a fine-tuned Random Forest model to detect network-level attacks such as Denial of Service (DoS) and Port Scanning based on flow features.
- **Web Application Attack Detection:** Employs a TF-IDF and Logistic Regression pipeline trained on malicious web payloads to specifically block SQL Injections (SQLi) and Cross-Site Scripting (XSS).
- **Intelligent Incident Response (RAG + LLM):** Integrates Google's Gemini LLM with a Retrieval-Augmented Generation (RAG) system. When an alert triggers, the system queries its cybersecurity knowledge base for mitigation playbooks and uses the LLM to generate clear threat explanations and automated remediation strategies.
- **Dashboard API:** FastAPI-powered backend with endpoints for traffic analysis, alert management, and real-time statistics.

## Project Structure
- `backend/`: FastAPI application containing routes, models, and services (including the LLM RAG service and Traffic Scorer).
- `ml/`: Machine Learning pipeline, model training scripts, and datasets.
- `data/`: Raw and processed data.
- `frontend/`: Dashboard UI (to be implemented).

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd PCD_IDS
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your environment variables (create a `.env` file or export them):
   ```bash
   # Required for the Intelligent Response system
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

### 1. Train the ML Models
If the models are not present in `backend/models`, you can train them by running the pipeline:
```bash
python -m ml.pipeline
```
This will train both the Network Anomaly Model and the Web Attack Model and evaluate them.

### 2. Run the API Server
Start the FastAPI backend:
```bash
uvicorn backend.main:app --reload
```
The API will be available at `http://localhost:8000`. 
Check the interactive API documentation at `http://localhost:8000/docs`.

### Key Endpoints
- `POST /api/analyze`: Submit traffic features/payloads for anomaly scoring.
- `GET /api/alert/{alert_id}/analyze`: Trigger the LLM RAG engine to retrieve a mitigation playbook and analyze a specific alert.
- `GET /api/dashboard/stats`: Retrieve high-level dashboard statistics.

## Built With
- **FastAPI** - Backend Framework
- **Scikit-Learn** - Machine Learning Models (Random Forest, Logistic Regression, TF-IDF)
- **Google Generative AI (Gemini)** - LLM for Incident Response (RAG)
- **Pandas & NumPy** - Data Processing
