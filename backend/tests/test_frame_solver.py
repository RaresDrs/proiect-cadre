# REQ-03-06, REQ-03-07, REQ-03-15
import pytest
# solve_frame will be created in 03-02-PLAN.md
# from app.services.frame_solver import solve_frame
# from app.schemas.frame import FrameInput, FrameNode, FrameBar, NodeLoad, BarLoad


class TestFrameSolverPortal:
    """Portal frame: 2 vertical columns (h=3m) + 1 horizontal beam (L=4m).
    Nodes: n1(0,0,pin) n2(0,3,free) n3(4,3,free) n4(4,0,roller).
    Bars: column left (n1→n2), beam top (n2→n3), column right (n4→n3).
    Load: horizontal point load Fx=10kN at n2."""

    def test_todo_reactions_equilibrium(self):
        pytest.skip("TODO: implement after solve_frame exists")

    def test_todo_max_M_positive(self):
        pytest.skip("TODO: implement after solve_frame exists")

    def test_todo_node_results_count(self):
        pytest.skip("TODO: implement after solve_frame exists")

    def test_todo_bar_diagrams_count(self):
        pytest.skip("TODO: implement after solve_frame exists")


class TestFrameSolverValidation:
    def test_todo_no_nodes_raises(self):
        pytest.skip("TODO: implement after solve_frame exists")

    def test_todo_no_supports_raises(self):
        pytest.skip("TODO: implement after solve_frame exists")
