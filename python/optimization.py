# FILE 3: optimization.py

from scipy.optimize import linprog

def calculate_bid_price(forecast: dict, prices: dict, capacity: int) -> float:
    """
    Calculates the optimal bid price using a Deterministic Linear Program (DLP).

    The bid price is the shadow price (dual variable) of the capacity constraint.

    Args:
        forecast: The demand forecast from the forecasting module.
        prices: The price for each fare class, e.g., {'urgent': 6000, 'leisure': 3000}
        capacity: Total number of seats.

    Returns:
        The single optimal bid price (float).
    """
    print("Step 3: Optimizing to find bid price...")
    
    # We have 2 decision variables: x_urgent, x_leisure
    # We use the demand means (mu) from the forecast
    D_urgent = forecast['urgent']['mu']
    D_leisure = forecast['leisure']['mu']
    
    P_urgent = prices['urgent']
    P_leisure = prices['leisure']

    # --- LP Formulation ---
    # Objective: Maximize (P_urgent * x_urgent) + (P_leisure * x_leisure)
    # scipy.optimize.linprog minimizes, so we flip the signs.
    c = [-P_urgent, -P_leisure]

    # Constraints (A_ub * x <= b_ub):
    # 1. x_urgent + x_leisure <= capacity
    # 2. x_urgent             <= D_urgent
    # 3.           x_leisure  <= D_leisure
    
    A_ub = [
        [1, 1],  # Capacity constraint
        [1, 0],  # Urgent demand constraint
        [0, 1]   # Leisure demand constraint
    ]
    
    b_ub = [capacity, D_urgent, D_leisure]
    
    # Bounds (x >= 0)
    bounds = [(0, None), (0, None)]

    # --- THIS IS THE FIX ---
    # Solve the LP using the 'interior-point' method, which is highly stable
    # and reliably returns dual variables.
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='interior-point')

    if not result.success:
        raise Exception(f"Linear Programming optimization failed: {result.message}")

    # The bid price is the shadow price (dual) of the *first* constraint (capacity).
    # For 'interior-point', this is stored in 'result.ineqlin'
    # We take its absolute value as linprog's duals for '<=' constraints are negative.
    
    # Add a check in case ineqlin is missing, though it shouldn't be.
    if not hasattr(result, 'ineqlin') or len(result.ineqlin) == 0:
        print("Warning: Solver did not return dual variables. Defaulting bid price to 0.")
        print(f"Full solver result: {result}")
        return 0.0

    bid_price = abs(result.ineqlin[0])
    
    print(f"Optimization complete. Optimal Bid Price: ₹{bid_price:.2f}")
    return bid_price