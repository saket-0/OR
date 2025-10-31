# FILE 3: optimization.py (UPDATED for Cumulative Demand)

import pulp

def calculate_flexi_fare_allocation(demand_forecast_by_bucket: list, 
                                    prices_by_bucket: list, 
                                    capacity: int) -> dict:
    """
    Calculates the optimal allocation of seats across multiple
    price buckets (Flexi-Fare) using a Deterministic Linear Program (DLP)
    based on a CUMULATIVE demand forecast.

    Args:
        demand_forecast_by_bucket: A list of *cumulative* remaining demand forecasts,
                                     e.g., [D_b1, D_b2, D_b3]
                                     where D_b1 >= D_b2 >= D_b3.
        prices_by_bucket: A list of prices for each bucket (must be sorted
                          from lowest to highest), e.g., [P_b1, P_b2, P_b3].
        capacity: Total *remaining* number of seats.

    Returns:
        A dict with optimal allocation sizes, e.g.,
        {'Bucket_0_Allocation': 50, 'Bucket_1_Allocation': 30, ...}
    """
    print("Step 3: Optimizing (Cumulative Demand LP) for optimal Flexi-Fare buckets...")
    
    num_buckets = len(prices_by_bucket)
    
    # --- 2. Create the LP Problem ---
    prob = pulp.LpProblem("Flexi_Fare_Allocation_Problem", pulp.LpMaximize)

    # --- 3. Define Decision Variables ---
    # x_i = How many tickets to *sell* in Bucket i (at Price i)
    x_buckets = [
        pulp.LpVariable(f"Bucket_{i}", lowBound=0, cat='Continuous')
        for i in range(num_buckets)
    ]

    # --- 4. Define Objective Function ---
    # Maximize (P_b1 * x_b1) + (P_b2 * x_b2) + ...
    # (This is unchanged)
    prob += pulp.lpSum(
        [prices_by_bucket[i] * x_buckets[i] for i in range(num_buckets)]
    ), "Total_Revenue"

    # --- 5. Define Constraints ---
    
    # Capacity Constraint: We can't sell more than our *remaining* capacity
    # (This is unchanged)
    prob += pulp.lpSum(x_buckets) <= capacity, "Capacity_Constraint"
    
    # --- (NEW) CUMULATIVE Demand Constraints ---
    # This is the key change. We now model "nested" demand.
    #
    # Example for 3 buckets:
    # 1. Sales(B3) <= Demand(B3)
    #    x_buckets[2] <= demand_forecast[2]
    #
    # 2. Sales(B2) + Sales(B3) <= Demand(B2)
    #    x_buckets[1] + x_buckets[2] <= demand_forecast[1]
    #
    # 3. Sales(B1) + Sales(B2) + Sales(B3) <= Demand(B1)
    #    x_buckets[0] + x_buckets[1] + x_buckets[2] <= demand_forecast[0]
    
    for i in range(num_buckets):
        # Sum of sales from this bucket 'i' up to the highest-priced bucket
        cumulative_sales_from_i_onward = pulp.lpSum(
            x_buckets[j] for j in range(i, num_buckets)
        )
        
        # This sum must be less than or equal to the cumulative demand
        # for this bucket's price point 'i' or higher.
        prob += (
            cumulative_sales_from_i_onward <= demand_forecast_by_bucket[i], 
            f"Cumulative_Demand_Constraint_B{i}"
        )
    # --- End of NEW Constraints ---

    # --- 6. Solve the LP ---
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception(f"LP solver failed to find an optimal solution. Status: {pulp.LpStatus[prob.status]}")

    # --- 7. Get the Optimal Allocation ---
    # (This is unchanged)
    result = {}
    for i in range(num_buckets):
        # We round to whole numbers for ticket allocations
        result[f'Bucket_{i}_Allocation'] = int(x_buckets[i].varValue)

    print(f"Optimization complete. Result: {result}")
    return result