# FILE 8: main.py (UPDATED for Monte Carlo Simulation)
# This is the main entry point for the application.
# It now runs the simulation multiple times to test robustness.

import numpy as np
from simulation import run_dynamic_simulation

# --- (NEW) Monte Carlo Parameters ---
N_SIMULATIONS = 100 # Number of times to run the simulation
all_revenues = []
# ---

if __name__ == "__main__":
    print("--- RUNNING MONTE CARLO SIMULATION ---")
    print(f"--- (Running {N_SIMULATIONS} simulations to test plan robustness) ---")
    
    # --- (NEW) Run one deterministic simulation first ---
    print("\n--- RUN 1: DETERMINISTIC (Baseline) ---")
    baseline_revenue = run_dynamic_simulation(
        stochastic_mode=False, 
        quiet_mode=False
    )
    print(f"\n--- DETERMINISTIC Baseline Revenue: ₹{baseline_revenue:,} ---")
    
    # --- (NEW) Run N-1 stochastic simulations ---
    print(f"\n--- RUNNING {N_SIMULATIONS-1} STOCHASTIC SIMULATIONS ---")
    all_revenues.append(baseline_revenue) # Add baseline as first run
    
    for i in range(N_SIMULATIONS - 1):
        # Run in stochastic mode (samples forecasts) and quiet mode (no print)
        revenue = run_dynamic_simulation(
            stochastic_mode=True, 
            quiet_mode=True
        )
        all_revenues.append(revenue)
        # Use end='\r' to print on the same line for a cleaner look
        print(f"  Simulation {i+1}/{N_SIMULATIONS-1} complete. Revenue: ₹{revenue:,}   ", end='\r')

    print("\n\n--- MONTE CARLO ANALYSIS COMPLETE ---")
    mean_revenue = np.mean(all_revenues)
    std_dev = np.std(all_revenues)
    min_revenue = np.min(all_revenues)
    max_revenue = np.max(all_revenues)
    
    print(f"\nBaseline (Deterministic) Revenue: ₹{baseline_revenue:,.2f}")
    print(f"Average (Mean) Revenue:         ₹{mean_revenue:,.2f}")
    print(f"Standard Deviation:             ₹{std_dev:,.2f}")
    print(f"Min Revenue (Worst Case):       ₹{min_revenue:,.2f}")
    print(f"Max Revenue (Best Case):        ₹{max_revenue:,.2f}")