def test_rejects_invalid_api_key(client):
    response = client.post("/api/v1/logs", json={"source_ip": "192.168.1.10", "event_type": "auth_failure"}, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_ingests_valid_log_and_binds_timestamp(client):
    response = client.post("/api/v1/logs", json={"source_ip": "192.168.1.10", "event_type": "auth_failure", "payload": {"attempt": 1}}, headers={"X-API-Key": "test-key"})
    assert response.status_code == 201
    body = response.json()
    assert body["source_ip"] == "192.168.1.10"
    assert body["timestamp"]


def test_rejects_malformed_log(client):
    response = client.post("/api/v1/logs", json={"source_ip": "not-an-ip", "event_type": "unknown"}, headers={"X-API-Key": "test-key"})
    assert response.status_code == 422