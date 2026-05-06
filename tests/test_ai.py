import pytest
from ai.engine import scorer

def test_scorer_initialization():
    """Check if the scorer is initialized."""
    assert scorer is not None

def test_mock_prediction():
    """Test the mock prediction logic (used when models are not loaded)."""
    # Test normal traffic
    features = {"Flow_Duration": 1, "Flow_Packets_s": 1, "payload": "hello"}
    result = scorer.analyze_traffic(features)
    assert result["is_anomaly"] is False
    
    # Test SQL Injection heuristic
    features_sqli = {"payload": "SELECT * FROM users"}
    result_sqli = scorer.analyze_traffic(features_sqli)
    assert result_sqli["is_anomaly"] is True
    assert "Web Attack" in result_sqli["label"] or "Web Intrusion" in result_sqli["label"]

def test_analyze_traffic_structure():
    """Verify the output structure of analyze_traffic."""
    features = {"Flow_Duration": 100}
    result = scorer.analyze_traffic(features)
    assert "is_anomaly" in result
    assert "threat_score" in result
    assert "label" in result
    assert "details" in result
