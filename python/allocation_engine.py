# FILE 3: allocation_engine.py (UPDATED with 2 LPs)
# This module solves the "Master" LP (between quotas)
# and the "Inner" LP (between buckets).

import pulp

def partition_capacity_by_quota(quota_forecasts: dict, 
                                total_capacity: int) -> dict:
    """
    (NEW) Solves the "Master Allocation" problem.
    
    Decides how many seats to *protect* for each quota based on
    its total demand and average revenue per seat.
    """
    print(f"--- Solving Master LP to partition {total_capacity} seats ---")
    
    prob = pulp.LpProblem("Master_Quota_Allocation", pulp.LpMaximize)
    
    q_codes = list(quota_forecasts.keys())
    
    # --- 1. Define Decision Variables ---
    # x_q = How many seats to allocate to Quota q
    x_vars = pulp.LpVariable.dicts(
        "Allocation", q_codes, lowBound=0, cat='Continuous'
    )

    # --- 2. Define Objective Function ---
    # Maximize (AvgRev_GN * Alloc_GN) + (AvgRev_TK * Alloc_TK) + ...
    prob += pulp.lpSum(
        [quota_forecasts[q]['avg_revenue_per_seat'] * x_vars[q] for q in q_codes]
    ), "Total_Expected_Revenue"

    # --- 3. Define Constraints ---
    
    # 1. Capacity Constraint: We can't allocate more than our total capacity
    prob += pulp.lpSum(x_vars) <= total_capacity, "Capacity_Constraint"
    
    # 2. Demand Constraints: We can't allocate more seats to a quota
    #    than it has demand for.
    for q in q_codes:
        prob += (
            x_vars[q] <= quota_forecasts[q]['total_demand'], 
            f"Demand_Constraint_{q}"
        )

    # --- 4. Solve the LP ---
    prob.solve()

    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception("Master Allocation LP failed to find a solution.")

    # --- 5. Get the Final Allocation ---
    result = {}
    for q in q_codes:
        result[f"{q}_Allocation"] = int(x_vars[q].varValue)

    print(f"Master Allocation complete. Result: {result}")
    return result


def partition_quota_into_buckets(independent_demands: list,
                                 prices: list,
                                 quota_allocation: int,
                                 q_code: str) -> dict:
    """
    (NEW) Solves the "Inner Allocation" problem for a single FLEXI quota.
    
    Takes the total seats allocated to a quota (e.g., 84 for GN) and
    partitions them optimally among its own price buckets.
    """
    print(f"--- Solving Inner LP for {q_code} to partition {quota_allocation} seats ---")
    
    num_buckets = len(independent_demands)
    prob = pulp.LpProblem(f"Inner_Allocation_{q_code}", pulp.LpMaximize)
    
    # --- 1. Define Decision Variables ---
    # x_i = How many tickets to *sell* in Bucket i
    x_vars = [
        pulp.LpVariable(f"{q_code}_Bucket_{i}", lowBound=0, cat='Continuous')
        for i in range(num_buckets)
    ]

    # --- 2. Define Objective Function ---
    # Maximize (P_b1 * x_b1) + (P_b2 * x_b2) + ...
    prob += pulp.lpSum(
        [prices[i] * x_vars[i] for i in range(num_buckets)]
    ), "Total_Revenue"

    # --- 3. Define Constraints ---
    
    # 1. Capacity Constraint: Can't sell more than this quota's
    #    master allocation (e.g., 84 seats)
    prob += pulp.lpSum(x_vars) <= quota_allocation, "Quota_Capacity_Constraint"
    
    # 2. Demand Constraints: Can't sell more in a bucket
    #    than its independent demand.
    for i in range(num_buckets):
        prob += (
            x_vars[i] <= independent_demands[i], 
            f"Demand_Constraint_B{i}"
        )
    
    # --- 4. Solve the LP ---
    prob.solve()
    if pulp.LpStatus[prob.status] != 'Optimal':
        print(f"WARNING: Inner LP for {q_code} failed. Allocating 0 seats.")
        return {}

    # --- 5. Get the Final Allocation ---
    result = {}
    for i in range(num_buckets):
        result[f"{q_code}_Bucket_{i}_Allocation"] = int(x_vars[i].varValue)

    print(f"Inner Allocation complete. Result: {result}")
    return result