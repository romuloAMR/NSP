from nsp_solver import NurseScheduling
import time
import sys
import io

test_cases = {
    1: ("small_feasible", {
        "nurses": ["N1", "N2", "N3"],
        "shifts": ["S1", "S2"],
        "edges": [("N1", "S1"), ("N2", "S1"), ("N2", "S2"), ("N3", "S2")],
        "nurse_limits": [(1, 1), (1, 2), (1, 1)],
        "shift_limits": [(2, 2), (1, 2)]
    }),
    2: ("small_infeasible", {
        "nurses": ["N1", "N2"],
        "shifts": ["S1", "S2"],
        "edges": [("N1", "S1"), ("N2", "S2")],
        "nurse_limits": [(1, 1), (1, 1)],
        "shift_limits": [(2, 2), (1, 1)] 
    }),
    3: ("medium_complex", {
        "nurses": ["N1", "N2", "N3", "N4", "N5"],
        "shifts": ["S1", "S2", "S3", "S4"],
        "edges": [
            ("N1", "S1"), ("N1", "S2"), 
            ("N2", "S1"), ("N2", "S3"),
            ("N3", "S2"), ("N3", "S3"), ("N3", "S4"),
            ("N4", "S4"), ("N4", "S1"),
            ("N5", "S2"), ("N5", "S4")
        ],
        "nurse_limits": [(1, 2), (1, 2), (2, 3), (1, 2), (1, 2)],
        "shift_limits": [(2, 3), (2, 3), (1, 2), (2, 3)]
    }),
    4: ("large_infeasible", {
        "nurses": ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"],
        "shifts": ["S1", "S2", "S3", "S4", "S5"],
        "edges": [
            ("N1", "S1"), ("N2", "S1"), ("N3", "S1"), 
            ("N4", "S2"), ("N5", "S2"),
            ("N6", "S3"), ("N7", "S4"), ("N8", "S5")
        ],
        "nurse_limits": [(0, 1) for _ in range(8)],
        "shift_limits": [(4, 5), (3, 4), (1, 2), (1, 2), (1, 2)]
    }),
    5: ("large_feasible", {
        "nurses": ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"],
        "shifts": ["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
        "edges": [
            ("N1", "S1"), ("N1", "S2"), ("N2", "S1"), ("N2", "S3"),
            ("N3", "S2"), ("N3", "S4"), ("N4", "S3"), ("N4", "S5"),
            ("N5", "S4"), ("N5", "S6"), ("N6", "S5"), ("N6", "S7"),
            ("N7", "S6"), ("N7", "S1"), ("N8", "S2"), ("N8", "S4"),
            ("N9", "S3"), ("N9", "S5"), ("N9", "S7"), ("N10", "S1"),
            ("N10", "S6"), ("N10", "S7")
        ],
        "nurse_limits": [(1, 3) for _ in range(10)],
        "shift_limits": [(1, 2), (1, 3), (1, 2), (2, 3), (1, 2), (1, 3), (2, 3)]
    })
}

def run_experiment(test_id, test_data):
    print(f"Running test: {test_id}")
    
    nurses = test_data['nurses']
    shifts = test_data['shifts']
    edges = test_data['edges']
    nurse_limits = test_data['nurse_limits']
    shift_limits = test_data['shift_limits']
    
    stdout_original = sys.stdout
    sys.stdout = buffer_output = io.StringIO()
    
    start_time = time.perf_counter()
    
    scheduler = NurseScheduling(
        nurses=nurses,
        shifts=shifts,
        edges=edges,
        nurse_limits=nurse_limits,
        shift_limits=shift_limits
    )
    result = scheduler.run()
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    sys.stdout = stdout_original
    log_text = buffer_output.getvalue()
    
    status = "infeasible" if result is None else "feasible"
    total_assigned = result['total_alocated'] if status == "feasible" else 0

    return [test_id, len(nurses), len(shifts), len(edges), status, total_assigned, elapsed_time], log_text
