import httpx

BASE_URL = "http://localhost:8000"

def test_get_clients():
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.get("/api/v1/clients")
        assert response.status_code == 200
