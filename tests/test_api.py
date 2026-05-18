from fastapi.testclient import TestClient
from app.main import app
from tests.utils import generate_valid_payload
import time
import copy


client = TestClient(app=app)
data = generate_valid_payload()

def test_predict_contract():
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    body = response.json()
    assert "salePrice" in body
    assert isinstance(body["salePrice"], float)

def test_invalid_input_type():
    invalid_data = copy.deepcopy(data)
    invalid_data['ms_zoning'] = 'abcdefgh'
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422

def test_edge_case():
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_latency():
    start = time.time()
    response = client.post("/predict", json=data)
    end = time.time()
    assert response.status_code == 200
    assert (end - start) < 2.0