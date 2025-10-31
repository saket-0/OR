# FILE 0: factor_calculator.py (FIXED)

import numpy as np
from unconstraining import unconstrain_demand

def get_unconstrained_demand(historical_data: list, capacity: int) -> list:
    """
    Helper function to run unconstraining on the new detailed data format.
    """
    # Create the simple list format required by the original unconstraining function
    simple_sales_data = [
        {
            'train_id': rec['train_id'], 
            'days_before_departure': rec['days_early'], 
            'total_sold': rec['total_sold']
        }
        for rec in historical_data
    ]
    return unconstrain_demand(simple_sales_data, capacity)


def calculate_demand_factors(historical_data: list, capacity: int) -> dict:
    """
    Calculates demand factors by comparing "normal" days to "special" days.
    
    Returns:
        A dict of multiplicative factors, e.g.:
        {'holiday': 1.45, 'weekend': 1.12, 'base_leisure_split': 0.68}
    """
    print("--- Calculating Demand Factors from Historical Data ---")
    
    # 1. Get true demand for all historical runs
    true_demand_list = get_unconstrained_demand(historical_data, capacity)
    
    # 2. Add the 'true_demand' to our detailed records
    for i, record in enumerate(historical_data):
        record['true_demand'] = true_demand_list[i]

    # --- (FIXED LOGIC) ---
    # 3. Calculate an overall average to use as a safe fallback
    #    (Use 1.0 to avoid division by zero if true_demand_list is empty)
    overall_mu = np.mean(true_demand_list) if true_demand_list else 1.0

    # 4. Calculate Base Demand (non-holiday, weekday)
    normal_demand = [
        rec['true_demand'] for rec in historical_data
        if not rec['is_holiday'] and rec['day_of_week'] not in ['Fri', 'Sun']
    ]
    # Use 'overall_mu' as the fallback instead of 200
    base_mu = np.mean(normal_demand) if normal_demand else overall_mu
    
    # 5. Calculate Holiday Demand
    holiday_demand = [
        rec['true_demand'] for rec in historical_data if rec['is_holiday']
    ]
    # Use 'base_mu' as fallback, so factor defaults to 1.0
    avg_holiday_mu = np.mean(holiday_demand) if holiday_demand else base_mu
    
    # 6. Calculate Weekend Demand
    weekend_demand = [
        rec['true_demand'] for rec in historical_data 
        if rec['day_of_week'] in ['Fri', 'Sun'] and not rec['is_holiday'] # Avoid double-counting
    ]
    avg_weekend_mu = np.mean(weekend_demand) if weekend_demand else base_mu
    # --- (END OF FIX) ---

    # 7. Calculate Factors
    factor_holiday = avg_holiday_mu / base_mu
    factor_weekend = avg_weekend_mu / base_mu
    
    factors = {
        'base_mu': base_mu,
        'factor_holiday': factor_holiday,
        'factor_weekend': factor_weekend
    }
    
    print(f"Factors calculated: {factors}")
    return factors