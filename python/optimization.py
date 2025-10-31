# FILE 3: optimization.py (UPDATED for Flexi-Fare)

import pulp

def calculate_flexi_fare_allocation(demand_forecast_by_bucket: list, 
                                    prices_by_bucket: list, 
                                    capacity: int) -> dict:
    """
    Calculates the optimal allocation of seats across multiple
    price buckets (Flexi-Fare) using a Deterministic Linear Program (DLP).

    Args:
        demand_forecast_by_bucket: A list of *remaining* demand forecasts,
                                     e.g., [D_b1, D_b2, D_b3]
        prices_by_bucket: A list of prices for each bucket,
                          e.g., [P_b1, P_b2, P_b3]
        capacity: Total *remaining* number of seats.

    Returns:
        A dict with optimal allocation sizes, e.g.,
        {'Bucket_0_Allocation': 50, 'Bucket_1_Allocation': 30, ...}
    """
    print("Step 3: Optimizing to find optimal Flexi-Fare bucket sizes (using PuLP)...")
    
    num_buckets = len(prices_by_bucket)
    
    # --- 2. Create the LP Problem ---
    prob = pulp.LpProblem("Flexi_Fare_Allocation_Problem", pulp.LpMaximize)

    # --- 3. Define Decision Variables ---
    # x_i = How many tickets to *sell* in Bucket i
    x_buckets = [
        pulp.LpVariable(f"Bucket_{i}", lowBound=0, cat='Continuous')
        for i in range(num_buckets)
    ]

    # --- 4. Define Objective Function ---
    # Maximize (P_b1 * x_b1) + (P_b2 * x_b2) + ...
    prob += pulp.lpSum(
        [prices_by_bucket[i] * x_buckets[i] for i in range(num_buckets)]
    ), "Total_Revenue"

    # --- 5. Define Constraints ---
    
    # We can't sell more than our *remaining* capacity
    prob += pulp.lpSum(x_buckets) <= capacity, "Capacity_Constraint"
    
    # We can't sell more tickets in a bucket than we have demand for it
    # This assumes "independent" demand forecasts.
    for i in range(num_buckets):
        prob += (
            x_buckets[i] <= demand_forecast_by_bucket[i], 
            f"Demand_Constraint_B{i}"
        )

    # --- 6. Solve the LP ---
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception(f"LP solver failed to find an optimal solution. Status: {pulp.LpStatus[prob.status]}")

    # --- 7. Get the Optimal Allocation ---
    result = {}
    for i in range(num_buckets):
        # We round to whole numbers for ticket allocations
        result[f'Bucket_{i}_Allocation'] = int(x_buckets[i].varValue)

    print(f"Optimization complete. Result: {result}")
    return result