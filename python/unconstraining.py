# FILE 1: unconstraining.py

import pandas as pd

def unconstrain_demand(historical_sales: list, capacity: int) -> list:
    """
    Estimates true (unconstrained) demand from historical sales data.

    This basic heuristic assumes that if a train sold out early,
    the true demand was higher.

    Args:
        historical_sales: A list of dicts, e.g., 
                          [{'train_id': 1, 'days_before_departure': 3, 'total_sold': 200},
                           {'train_id': 2, 'days_before_departure': 0, 'total_sold': 180}]
        capacity: The total seat capacity (e.g., 200).

    Returns:
        A list of unconstrained demand estimates.
    """
    print("Step 1: Unconstraining historical data...")
    unconstrained_estimates = []
    
    for record in historical_sales:
        sold = record['total_sold']
        days_early = record['days_before_departure']
        
        if sold < capacity:
            # Train did not sell out. Sales = True Demand.
            unconstrained_estimates.append(sold)
        else:
            # Train sold out. Apply heuristic.
            # Heuristic: 10% more demand for each day it sold out early.
            # (A real EM algorithm would be much more complex)
            early_booking_factor = 1.0 + (days_early * 0.10)
            estimated_demand = int(sold * early_booking_factor)
            unconstrained_estimates.append(estimated_demand)
            
    print(f"Unconstrained estimates: {unconstrained_estimates}")
    return unconstrained_estimates