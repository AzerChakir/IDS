import os
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai

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
        
        # Configure Gemini if API key is present
        api_key = os.getenv("GEMINI_API_KEY")
        self.use_llm = False
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Use a standard recommended model
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_llm = True
                logger.info("LLM initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                
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
        
        if self.use_llm:
            try:
                response = self.model.generate_content(prompt)
                analysis = response.text
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
            f"(Note: This is a simulated LLM response because GEMINI_API_KEY is not set.)"
        )

llm_rag_service = LLMRagService()
