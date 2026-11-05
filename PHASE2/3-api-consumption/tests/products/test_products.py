import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_get_devices():
    response = httpx.get(f"{BASE_URL}/products")
    assert response.status_code == 200


