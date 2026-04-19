# REQ-03-08, REQ-03-09
import pytest
from fastapi.testclient import TestClient
# frames router will be created in 03-02-PLAN.md
# from app.main import app


PORTAL_PAYLOAD = {
    "nodes": [
        {"id": "n1", "x": 0.0, "y": 0.0, "constraint": "pin"},
        {"id": "n2", "x": 0.0, "y": 3.0, "constraint": "free"},
        {"id": "n3", "x": 4.0, "y": 3.0, "constraint": "free"},
        {"id": "n4", "x": 4.0, "y": 0.0, "constraint": "roller"},
    ],
    "bars": [
        {"id": "b1", "node_i": "n1", "node_j": "n2", "EI": 21000.0, "EA": 2100000.0},
        {"id": "b2", "node_i": "n2", "node_j": "n3", "EI": 21000.0, "EA": 2100000.0},
        {"id": "b3", "node_i": "n4", "node_j": "n3", "EI": 21000.0, "EA": 2100000.0},
    ],
    "node_loads": [{"node_id": "n2", "Fx": 10.0, "Fy": 0.0, "Mz": 0.0}],
    "bar_loads": [],
}


def test_todo_frames_solve_200():
    pytest.skip("TODO: implement after frames router exists")


def test_todo_frames_solve_empty_nodes_422():
    pytest.skip("TODO: implement after frames router exists")


def test_todo_frames_solve_result_shape():
    pytest.skip("TODO: implement after frames router exists")
