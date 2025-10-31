# FILE 3: optimization.py (NEW - using PuLP)

import pulp

def calculate_bid_price(forecast: dict, prices: dict, capacity: int) -> float:
    """
    Calculates the optimal bid price using a Deterministic Linear Program (DLP).

    The bid price is the shadow price (dual variable) of the capacity constraint.
    This version uses the PuLP library for stability.

    Args:
        forecast: The demand forecast from the forecasting module.
        prices: The price for each fare class, e.g., {'urgent': 6000, 'leisure': 3000}
        capacity: Total number of seats.

    Returns:
        The single optimal bid price (float).
    """
    print("Step 3: Optimizing to find bid price (using PuLP)...")
    
    # --- 1. Get Forecasts and Prices ---
    D_urgent = forecast['urgent']['mu']
    D_leisure = forecast['leisure']['mu']
    
    P_urgent = prices['urgent']
    P_leisure = prices['leisure']

    # --- 2. Create the LP Problem ---
    # We want to MAXIMIZE revenue
    prob = pulp.LpProblem("Bid_Price_Problem", pulp.LpMaximize)

    # --- 3. Define Decision Variables ---
    # How many of each ticket to sell?
    x_urgent = pulp.LpVariable("Urgent_Tickets", lowBound=0, cat='Continuous')
    x_leisure = pulp.LpVariable("Leisure_Tickets", lowBound=0, cat='Continuous')

    # --- 4. Define Objective Function ---
    # Maximize (P_urgent * x_urgent) + (P_leisure * x_leisure)
    prob += (P_urgent * x_urgent) + (P_leisure * x_leisure), "Total_Revenue"

    # --- 5. Define Constraints ---
    # We must give the capacity constraint a name to get its dual price
    prob += (x_urgent + x_leisure <= capacity, "Capacity_Constraint")
    prob += (x_urgent <= D_urgent, "Urgent_Demand_Constraint")
    prob += (x_leisure <= D_leisure, "Leisure_Demand_Constraint")

    # --- 6. Solve the LP ---
    # The default CBC solver is excellent
    prob.solve()

    # Check if the solution is optimal
    if pulp.LpStatus[prob.status] != 'Optimal':
        raise Exception(f"LP solver failed to find an optimal solution. Status: {pulp.LpStatus[prob.status]}")

    # --- 7. Get the Bid Price (The Dual Variable) ---
    # This is the most stable way:
    # 1. Create a dictionary of all constraints
    constraints = prob.constraints
    
    # 2. Get the dual value (pi) from the constraint we named
    bid_price = constraints["Capacity_Constraint"].pi

    # In PuLP, duals from a maximization problem with a '<=' constraint
    # are negative, so we must take the absolute value.
    bid_price = abs(bid_price)
    
    print(f"Optimization complete. Optimal Bid Price: ₹{bid_price:.2f}")
    return bid_price