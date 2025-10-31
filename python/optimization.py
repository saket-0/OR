# FILE 3: optimization.py (UPDATED for Quota Allocation)

import pulp

def calculate_quota_allocation(forecast_general: dict, 
                               forecast_tatkal: dict, 
                               prices: dict, 
                               capacity: int) -> dict:
    """
    Calculates the optimal allocation of seats between General and Tatkal quotas
    using a Deterministic Linear Program (DLP).

    Args:
        forecast_general: The demand forecast for the General quota.
        forecast_tatkal: The demand forecast for the Tatkal quota.
        prices: The price for each quota, e.g., {'general': 3000, 'tatkal': 4000}
        capacity: Total *remaining* number of seats.

    Returns:
        A dict with protection levels, e.g.,
        {'general_booking_limit': 90, 'tatkal_protection_level': 20}
    """
    print("Step 3: Optimizing to find optimal quota allocation (using PuLP)...")
    
    # --- 1. Get Forecasts and Prices ---
    D_general = forecast_general['mu']
    D_tatkal = forecast_tatkal['mu']
    
    P_general = prices['general']
    P_tatkal = prices['tatkal']

    # --- 2. Create the LP Problem ---
    # We want to MAXIMIZE revenue
    prob = pulp.LpProblem("Quota_Allocation_Problem", pulp.LpMaximize)

    # --- 3. Define Decision Variables ---
    # How many of each ticket *type* to sell?
    x_general = pulp.LpVariable("General_Tickets", lowBound=0, cat='Continuous')
    x_tatkal = pulp.LpVariable("Tatkal_Tickets", lowBound=0, cat='Continuous')

    # --- 4. Define Objective Function ---
    # Maximize (P_general * x_general) + (P_tatkal * x_tatkal)
    prob += (P_general * x_general) + (P_tatkal * x_tatkal), "Total_Revenue"

    # --- 5. Define Constraints ---
    # We can't sell more than our *remaining* capacity
    prob += (x_general + x_tatkal <= capacity, "Capacity_Constraint")
    
    # We can't sell more tickets than we have demand for
    prob += (x_general <= D_general, "General_Demand_Constraint")
    prob += (x_tatkal <= D_tatkal, "Tatkal_Demand_Constraint")

    # --- 6. Solve the LP ---
    prob.solve()

    # Check if the solution is optimal
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception(f"LP solver failed to find an optimal solution. Status: {pulp.LpStatus[prob.status]}")

    # --- 7. Get the Optimal Allocation ---
    # The "protection level" is the number of Tatkal tickets the LP wants to sell.
    # We must round it to a whole number.
    tatkal_protection = int(x_tatkal.varValue)
    
    # The General quota gets what's left over. This is a common
    # industry practice: protect the high-value quota first.
    general_booking_limit = capacity - tatkal_protection

    result = {
        'general_booking_limit': general_booking_limit,
        'tatkal_protection_level': tatkal_protection
    }
    
    print(f"Optimization complete. Result: {result}")
    return result
