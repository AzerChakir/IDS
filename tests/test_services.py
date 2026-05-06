import pytest
from backend.services.llm_rag import llm_rag_service

def test_rag_context_retrieval():
    """Test if RAG can retrieve context for a known attack."""
    context = llm_rag_service.retrieve_context("SQL Injection")
    assert "SQL Injection" in context or "prepared statements" in context

def test_analyze_alert_structure():
    """Test the structure of the LLM analysis output."""
    result = llm_rag_service.analyze_alert("SQL Injection", "Detected 'OR 1=1'")
    assert "alert" in result
    assert "llm_analysis" in result
    assert "retrieved_context" in result
