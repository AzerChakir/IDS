import os
import logging
import sys
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging to stdout so messages show in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Mock playbooks (Knowledge Base for RAG)
PLAYBOOKS = [
    {
        "topic": "SQL Injection (SQLi)",
        "content": "SQL Injection is a code injection technique that might destroy your database. "
                   "Mitigation: Use prepared statements and parameterized queries. Implement input validation and least privilege."
    },
    {
        "topic": "Cross-Site Scripting (XSS)",
        "content": "XSS attacks enable attackers to inject client-side scripts into web pages viewed by other users. "
                   "Mitigation: Use Content Security Policy (CSP), encode data on output, and sanitize user input."
    },
    {
        "topic": "Denial of Service (DoS)",
        "content": "A DoS attack is meant to shut down a machine or network, making it inaccessible to its intended users. "
                   "Mitigation: Implement rate limiting, block malicious IPs, and use Web Application Firewalls (WAF)."
    },
    {
        "topic": "Port Scanning",
        "content": "Port scanning is a method to determine which ports on a network are open and could be receiving or sending data. "
                   "Mitigation: Close unused ports, use an IDS/IPS to detect and block scanning IPs."
    }
]

class LLMRagService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        # Create embeddings for our Knowledge Base
        self.kb_texts = [p["topic"] + " " + p["content"] for p in PLAYBOOKS]
        self.kb_embeddings = self.vectorizer.fit_transform(self.kb_texts)

        self.use_llm = False
        self.llm_type = None
        self.model = None

        # Try Hugging Face (free tier)
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        print(f"[DEBUG] HF Token loaded: {hf_token[:10] if hf_token else 'None'}...")
        if hf_token and hf_token != "your_huggingface_token_here":
            try:
                self.hf_token = hf_token
                # Models with verified Inference API support
                models_to_try = [
                    "facebook/opt-125m",
                    "gpt2",
                    "bigscience/bloom-560m"
                ]

                for model_name in models_to_try:
                    try:
                        print(f"[DEBUG] Trying model: {model_name}")
                        self.hf_model_url = f"https://api-inference.huggingface.co/models/{model_name}"
                        test_response = requests.post(
                            self.hf_model_url,
                            headers={"Authorization": f"Bearer {self.hf_token}"},
                            json={"inputs": "Hello"},
                            timeout=15
                        )
                        print(f"[DEBUG] Response status: {test_response.status_code}")
                        if test_response.status_code != 200:
                            print(f"[DEBUG] Response body: {test_response.text[:200]}")
                        if test_response.status_code == 200:
                            self.model = model_name
                            self.use_llm = True
                            self.llm_type = "huggingface"
                            print(f"[SUCCESS] LLM initialized: {model_name}")
                            break
                    except Exception as e:
                        print(f"[DEBUG] Error with {model_name}: {e}")
                        continue
            except Exception as e:
                print(f"[ERROR] Failed to initialize Hugging Face LLM: {e}")

        # Final status message
        if self.use_llm:
            print(f"\n{'='*50}")
            print(f"✓ LLM INITIALIZED SUCCESSFULLY")
            print(f"  Model: {self.model}")
            print(f"  Type: {self.llm_type}")
            print(f"{'='*50}\n")
        else:
            print(f"\n{'='*50}")
            print(f"✗ LLM INITIALIZATION FAILED")
            print(f"  Reason: No valid HuggingFace API key or all models failed")
            print(f"  Will use mock responses instead")
            print(f"{'='*50}\n")
                
    def retrieve_context(self, query: str) -> str:
        """Retrieve the most relevant playbook based on the query."""
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.kb_embeddings).flatten()
        best_match_idx = similarities.argmax()
        
        if similarities[best_match_idx] > 0.1:
            return PLAYBOOKS[best_match_idx]["content"]
        return "General Security Best Practices: Keep systems updated and monitor logs."

    def analyze_alert(self, alert_label: str, alert_details: str) -> dict:
        """
        Uses RAG to analyze an alert and provide an automated response plan.
        """
        query = f"{alert_label} {alert_details}"
        context = self.retrieve_context(query)

        prompt = (
            f"You are an expert AI Cybersecurity Analyst for an educational platform.\n"
            f"An alert was triggered: '{alert_label}' with details: '{alert_details}'.\n"
            f"Based on the following knowledge base context: '{context}'\n\n"
            f"Provide a structured analysis containing:\n"
            f"1. Threat Explanation\n"
            f"2. Immediate Automated Action (e.g., Block IP)\n"
            f"3. Long-term Remediation Strategy\n"
            f"Be concise and professional."
        )

        if self.use_llm and self.llm_type == "huggingface":
            try:
                # Use Hugging Face Inference API
                headers = {"Authorization": f"Bearer {self.hf_token}"}

                # Adjust prompt format for chat models
                if "TinyLlama" in self.model or "gemma" in self.model:
                    payload = {
                        "inputs": prompt,
                        "parameters": {"max_new_tokens": 256, "temperature": 0.3}
                    }
                else:
                    payload = {
                        "inputs": prompt,
                        "parameters": {"max_new_tokens": 256, "temperature": 0.3}
                    }

                response = requests.post(
                    self.hf_model_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        analysis = result[0].get("generated_text", "")
                    else:
                        analysis = str(result)
                    logger.info(f"LLM response received: {analysis[:100]}...")
                else:
                    logger.error(f"HF API error: {response.status_code} - {response.text}")
                    analysis = self._mock_generation(alert_label, context)
            except Exception as e:
                logger.error(f"LLM Generation failed: {e}")
                analysis = self._mock_generation(alert_label, context)
        else:
            analysis = self._mock_generation(alert_label, context)
            
        return {
            "alert": alert_label,
            "retrieved_context": context,
            "llm_analysis": analysis
        }
        
    def _mock_generation(self, label: str, context: str) -> str:
        return (
            f"**Threat Explanation:** The system detected a potential {label} attack.\n"
            f"**Immediate Action:** The source IP has been temporarily blocked to prevent further exploitation.\n"
            f"**Long-term Remediation:** {context}\n"
            f"(Note: This is a simulated LLM response because no API key is configured.)"
        )

llm_rag_service = LLMRagService()
