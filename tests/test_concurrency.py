from concurrent.futures import ThreadPoolExecutor


def test_concurrent_ingestion_streams(client):
    def send_log(index: int) -> int:
        response = client.post(
            "/api/v1/logs",
            json={"source_ip": f"10.0.0.{(index % 200) + 1}", "event_type": "data_access", "payload": {"stream": index}},
            headers={"X-API-Key": "test-key"},
        )
        return response.status_code

    with ThreadPoolExecutor(max_workers=8) as executor:
        statuses = list(executor.map(send_log, range(24)))

    assert statuses == [201] * 24