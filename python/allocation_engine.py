# FILE 3: allocation_engine.py (UPDATED with Policy Constraint & Quiet Mode)
# This module solves the "Master" LP (between quotas)
# and the "Inner" LP (between buckets).

import pulp # Function to solve the LLP problems

# ===================================================================
# --- MASTER ALLOCATION LP BETWEEN QUOTAS ---
def partition_capacity_by_quota(quota_forecasts: dict, 
                                total_capacity: int,
                                tc: str,
                                quiet_mode: bool = False) -> dict: # <-- (NEW) Added quiet_mode
    """
    Solves the "Master Allocation" problem.
    
    Decides how many seats to protect for each quota based on
    its total demand and average revenue per seat.
    """
    if not quiet_mode: 
        print(f"--- Solving Master LP for {tc} to partition {total_capacity} seats ---")
    
    prob = pulp.LpProblem(f"Master_Quota_Allocation_{tc}", pulp.LpMaximize)
    
    q_codes = list(quota_forecasts.keys())
    



    # --- 1. Defining Decision Variables ---
    # x_q = How many seats to allocate to Quota q
    x_vars = pulp.LpVariable.dicts(
        "Allocation", q_codes, lowBound=0, cat='Continuous'
    )

    # --- 2. Defining Objective Function ---
    # Maximize (AvgRev_GN * Alloc_GN) + (AvgRev_TK * Alloc_TK) + ...
    prob += pulp.lpSum(
        [quota_forecasts[q]['avg_revenue_per_seat'] * x_vars[q] for q in q_codes]
    ), "Total_Expected_Revenue"



    # --- 3. Defining Constraints ---
    
    # 1. Capacity Constraint: We can't allocate more than our total capacity
    prob += pulp.lpSum(x_vars) <= total_capacity, "Capacity_Constraint"
    
    # 2. Demand Constraints: We can't allocate more seats to a quota
    #    than it has demand for.
    for q in q_codes:
        prob += (
            x_vars[q] <= quota_forecasts[q]['total_demand'], 
            f"Demand_Constraint_{q}"
        )

    # --- 3b. POLICY CONSTRAINT ---
    # Enforce a minimum allocation for social/policy quotas,
    # even if it's not revenue-optimal.
    if 'LD' in q_codes and tc == '3AC':
        if not quiet_mode: 
            print("... Applying 'LD' Policy Constraint for 3AC (min 2 seats)")
        prob += x_vars['LD'] >= 2, "Policy_Constraint_LD_3AC_Min"



    # --- 4. Solve the LP ---
    # Suppress solver console output
    prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] != 'Optimal':
        # Don't raise an exception, just warn, as it might be an "empty problem"
        if not quiet_mode: 
            print(f"WARNING: Master Allocation for {tc} LP status: {pulp.LpStatus[prob.status]}")
        if pulp.LpStatus[prob.status] == 'Infeasible':
             raise Exception(f"Master Allocation LP for {tc} is INFEASIBLE.")


    # --- 5. Get the Final Allocation ---
    result = {}
    for q in q_codes:
        result[f"{q}_Allocation"] = int(x_vars[q].varValue)
    
    if not quiet_mode: 
        print(f"Master Allocation complete. Result: {result}")
    return result

# ===================================================================

# ===================================================================
# --- INNER ALLOCATION LP BETWEEN BUCKETS OF A QUOTA ---
def partition_quota_into_buckets(independent_demands: list,
                                 prices: list,
                                 quota_allocation: int,
                                 q_code: str,
                                 quiet_mode: bool = False) -> dict: # <-- (NEW) Added quiet_mode
    """
    Solves the "Inner Allocation" problem for a single FLEXI quota.
    
    Takes the total seats allocated to a quota (e.g., 84 for GN) and
    partitions them optimally among its own price buckets.
    """
    # (Benign) If total demand is <= allocation, no LP is needed.
    if sum(independent_demands) <= quota_allocation:
        if not quiet_mode: 
            print(f"--- Skipping Inner LP for {q_code} (Demand <= Allocation) ---")
        result = {}
        for i in range(len(independent_demands)):
             result[f"{q_code}_Bucket_{i}_Allocation"] = independent_demands[i]
        return result

    if not quiet_mode: 
        print(f"--- Solving Inner LP for {q_code} to partition {quota_allocation} seats ---")
    
    num_buckets = len(independent_demands)
    prob = pulp.LpProblem(f"Inner_Allocation_{q_code}", pulp.LpMaximize)
    
    # --- 1. Define Decision Variables ---
    # x_i = How many tickets to sell in Bucket i
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
    prob.solve(pulp.PULP_CBC_CMD(msg=False)) # Suppress solver console output
    if pulp.LpStatus[prob.status] != 'Optimal':
        if not quiet_mode: 
            print(f"WARNING: Inner LP for {q_code} failed. Allocating 0 seats.")
        return {}



    # --- 5. Get the Final Allocation ---
    result = {}
    for i in range(num_buckets):
        result[f"{q_code}_Bucket_{i}_Allocation"] = int(x_vars[i].varValue)

    if not quiet_mode: 
        print(f"Inner Allocation complete. Result: {result}")
    return result

# ===================================================================