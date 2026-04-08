import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_beam_simply_supported_uniform_load():
    """Grinda simplu rezemata cu sarcina uniforma q=10 kN/m, L=6m"""
    payload = {
        "length": 6.0,
        "angle_deg": 0.0,
        "supports": [
            {"x": 0.0, "type": 1},
            {"x": 6.0, "type": 2}
        ],
        "point_loads": [],
        "distributed_load": 10.0,
        "q_start": 0.0,
        "q_end": 6.0,
        "EI": 21000.0,
        "EA": 2100000.0
    }
    response = client.post("/api/v1/beams/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Reactiuni: fiecare reazem = q*L/2 = 30 kN
    reactions = data["reactions"]
    fy_sum = sum(v for k, v in reactions.items() if "_Fy" in k)
    # anastruct returneaza reactiuni ca forte de reazem (pozitive = in sus)
    # suma verticala trebuie sa echilibreze sarcina totala q*L = 10*6 = 60 kN
    assert abs(abs(fy_sum) - 60.0) < 0.5, f"Suma reactiuni Fy = {fy_sum}, asteptat ~60"
    # Moment maxim: q*L^2/8 = 10*36/8 = 45 kNm
    assert abs(data["max_M"] - 45.0) < 1.0, f"max_M = {data['max_M']}, asteptat ~45"


def test_beam_invalid_length():
    payload = {"length": -1.0, "supports": [], "EI": 21000.0, "EA": 2100000.0}
    response = client.post("/api/v1/beams/solve", json=payload)
    assert response.status_code == 422


def test_beam_result_has_diagrams():
    payload = {
        "length": 4.0,
        "supports": [{"x": 0.0, "type": 1}, {"x": 4.0, "type": 2}],
        "point_loads": [{"x": 2.0, "fx": 0.0, "fy": -20.0}],
        "distributed_load": 0.0,
        "q_start": 0.0,
        "EI": 21000.0,
        "EA": 2100000.0
    }
    response = client.post("/api/v1/beams/solve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["diagrams"]) > 0
    assert all("x" in d and "N" in d and "V" in d and "M" in d for d in data["diagrams"])
