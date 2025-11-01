# FILE 8: main.py (MODIFIED for Streamlit - CORRECTED)
# This file can now be run directly OR imported by app.py --> NICE 

import numpy as np
from simulation import run_dynamic_simulation
import io
import contextlib

# --- Monte Carlo Parameters ---
N_SIMULATIONS = 100 # Number of times to run the simulation

def run_analysis():
    """
    Runs the full Monte Carlo analysis and returns the results.
    This function yields progress updates for the Streamlit UI.
    """
    all_revenues = []
    
    # --- Run 1: DETERMINISTIC (Baseline) ---
    yield "Running Deterministic (Baseline) Simulation..."
    
    # We must capture the standard output from the detailed run
    log_stream = io.StringIO()
    with contextlib.redirect_stdout(log_stream):
        baseline_revenue = run_dynamic_simulation(
            stochastic_mode=False, 
            quiet_mode=False
        )
    deterministic_log = log_stream.getvalue()
    all_revenues.append(baseline_revenue)
    
    yield "Deterministic run complete. Running stochastic simulations..."

    # --- Run N-1 stochastic simulations ---
    for i in range(N_SIMULATIONS - 1):
        revenue = run_dynamic_simulation(
            stochastic_mode=True, 
            quiet_mode=True
        )
        all_revenues.append(revenue)
        
        # Yield progress updates to the UI
        current_sim_num = i + 2
        if (current_sim_num % 10 == 0) or (current_sim_num == N_SIMULATIONS):
             yield f"  Simulation {current_sim_num}/{N_SIMULATIONS} complete."

    yield "All simulations complete. Analyzing results..."

    # --- Final Analysis ---
    mean_revenue = np.mean(all_revenues)
    std_dev = np.std(all_revenues)
    min_revenue = np.min(all_revenues)
    max_revenue = np.max(all_revenues)
    
    # Return all results in a single dictionary
    results = {
        "baseline_revenue": baseline_revenue,
        "mean_revenue": mean_revenue,
        "std_dev": std_dev,
        "min_revenue": min_revenue,
        "max_revenue": max_revenue,
        "all_revenues": all_revenues,
        "deterministic_log": deterministic_log,
        "n_simulations": N_SIMULATIONS
    }
    
    # --- THIS IS THE FIX ---
    # Was: return results
    yield results
    # -----------------------

# This block lets you still run this file from the command line if you want
if __name__ == "__main__":
    print("--- RUNNING MONTE CARLO SIMULATION (from command line) ---")
    
    final_results = None
    
    # Consume the generator to run the analysis
    for status in run_analysis():
        print(status)
        # The last item yielded is the results dictionary
        if isinstance(status, dict):
            final_results = status

    if final_results:
        print("\n\n--- MONTE CARLO ANALYSIS COMPLETE ---")
        print(f"\nBaseline (Deterministic) Revenue: ₹{final_results['baseline_revenue']:,.2f}")
        print(f"Average (Mean) Revenue:         ₹{final_results['mean_revenue']:,.2f}")
        print(f"Standard Deviation:             ₹{final_results['std_dev']:,.2f}")
        print(f"Min Revenue (Worst Case):       ₹{final_results['min_revenue']:,.2f}")
        print(f"Max Revenue (Best Case):        ₹{final_results['max_revenue']:,.2f}")