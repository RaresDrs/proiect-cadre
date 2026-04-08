import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rectangle_section():
    """Dreptunghi b=20cm, h=40cm"""
    payload = {"shape": "rectangle", "b": 20.0, "h": 40.0}
    response = client.post("/api/v1/sections/properties", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert abs(data["A"] - 800.0) < 0.01, f"A = {data['A']}, asteptat 800"
    assert abs(data["Ix"] - 106666.67) < 1.0, f"Ix = {data['Ix']}, asteptat 106666.67"
    assert abs(data["Wx"] - 5333.33) < 1.0, f"Wx = {data['Wx']}, asteptat 5333.33"
    assert abs(data["ix"] - 11.547) < 0.01, f"ix = {data['ix']}, asteptat 11.547"


def test_circle_section():
    """Cerc d=30cm"""
    import math
    payload = {"shape": "circle", "d": 30.0}
    response = client.post("/api/v1/sections/properties", json=payload)
    assert response.status_code == 200
    data = response.json()
    expected_A = math.pi * 15**2
    assert abs(data["A"] - expected_A) < 0.01
    assert data["Ip"] is not None


def test_invalid_shape():
    payload = {"shape": "triangle", "b": 10.0}
    response = client.post("/api/v1/sections/properties", json=payload)
    assert response.status_code == 422
