from nsp_solver import NurseScheduling
import time
import sys
import io

test_cases = {
    1: ("small_feasible", {
        "nurses": ["N1", "N2", "N3"],
        "shifts": ["S1", "S2", "S3"],
        "edges": [("N1", "S1"), ("N2", "S1"), ("N2", "S2"), ("N3", "S3")],
        "nurse_limits": [(1, 1), (1, 2), (1, 1)],
        "shift_limits": [(2, 2), (1, 2), (1, 1)]
    }),
    2: ("small_infeasible", {
        "nurses": ["N1", "N2"],
        "shifts": ["S1", "S2", "S3"],
        "edges": [("N1", "S1"), ("N2", "S2")],
        "nurse_limits": [(1, 1), (1, 1)],
        "shift_limits": [(2, 2), (1, 1), (1, 1)]
    }),
    3: ("medium_complex", {
        "nurses": ["N1", "N2", "N3", "N4", "N5"],
        "shifts": ["S1", "S2", "S3"],
        "edges": [
            ("N1", "S1"), ("N1", "S2"),
            ("N2", "S1"), ("N2", "S3"),
            ("N3", "S2"), ("N3", "S3"),
            ("N4", "S1"), ("N4", "S3"),
            ("N5", "S2")
        ],
        "nurse_limits": [(1, 2), (1, 2), (2, 3), (1, 2), (1, 2)],
        "shift_limits": [(3, 3), (2, 3), (2, 3)]
    }),
    4: ("large_infeasible", {
        "nurses": ["N1", "N2", "N3", "N4", "N5", "N6"],
        "shifts": ["S1", "S2", "S3"],
        "edges": [
            ("N1", "S1"), ("N2", "S1"),
            ("N3", "S2"), ("N4", "S2"),
            ("N5", "S3"), ("N6", "S3")
        ],
        "nurse_limits": [(0, 1) for _ in range(6)],
        "shift_limits": [(3, 3), (3, 3), (3, 3)]
    }),
    5: ("large_feasible", {
        "nurses": [f"N{i+1}" for i in range(10)],
        "shifts": ["S1", "S2", "S3"],
        "edges": [
            ("N1", "S1"), ("N1", "S2"),
            ("N2", "S1"), ("N2", "S3"),
            ("N3", "S2"), ("N3", "S3"),
            ("N4", "S1"), ("N4", "S2"),
            ("N5", "S2"), ("N5", "S3"),
            ("N6", "S1"), ("N6", "S3"),
            ("N7", "S1"), ("N8", "S2"),
            ("N9", "S2"), ("N10", "S3")
        ],
        "nurse_limits": [(1, 3) for _ in range(10)],
        "shift_limits": [(4, 5), (4, 5), (3, 4)]
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
