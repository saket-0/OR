# FILE 1: unconstraining.py (REFINED HEURISTIC)

import pandas as pd

# --- REFINED MODEL PARAMETER ---
# This is our configurable assumption for the "daily spill factor".
# 8% is a more aggressive (and likely realistic) assumption
# for compounded unconstrained demand.
DAILY_SPILL_FACTOR = 0.08 

def unconstrain_demand(historical_sales: list, capacity: int) -> list:
    """
    Estimates true (unconstrained) demand from historical sales data.

    This *refined* heuristic uses an exponential compounding factor,
    assuming that demand "spills" and compounds each day.

    Args:
        historical_sales: A list of dicts, e.g., 
                          [{'train_id': 1, 'days_before_departure': 3, 'total_sold': 200},
                           {'train_id': 2, 'days_before_departure': 0, 'total_sold': 180}]
        capacity: The total seat capacity (e.g., 200).

    Returns:
        A list of unconstrained demand estimates.
    """
    print("Step 1: Unconstraining historical data (Refined)...")
    unconstrained_estimates = []
    
    for record in historical_sales:
        sold = record['total_sold']
        days_early = record['days_before_departure']
        
        if sold < capacity:
            # Train did not sell out. Sales = True Demand.
            unconstrained_estimates.append(sold)
        else:
            # --- REFINED HEURISTIC ---
            # Train sold out. Apply an exponential heuristic.
            # Old linear: (1.0 + (days_early * 0.10))
            # New exponential: (1.0 + DAILY_SPILL_FACTOR) ** days_early
            early_booking_factor = (1.0 + DAILY_SPILL_FACTOR) ** days_early
            estimated_demand = int(sold * early_booking_factor)
            unconstrained_estimates.append(estimated_demand)
            # -------------------------
            
    print(f"Unconstrained estimates: {unconstrained_estimates}")
    return unconstrained_estimates