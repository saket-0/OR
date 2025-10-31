# FILE 2: forecasting.py (UPDATED for Flexi-Fare)

import numpy as np
import config

def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    quota_type: str) -> dict:
    """
    Forecasts the *total* demand distribution for a specific quota.
    (This function is unchanged)
    """
    print(f"Step 2: Forecasting *total* demand for {quota_type} quota...")
    
    # Base mu is the average *total* demand for this quota from history
    base_mu = np.mean(unconstrained_estimates) if unconstrained_estimates else 0
    
    forecast = {
        'mu': base_mu, 
        'sigma': base_mu * 0.15 # Std dev can be tuned
    }
    
    # --- APPLY CALCULATED FACTORS ---
    if external_factors.get('is_holiday'):
        print(f"... applying holiday factor ({demand_factors.get('factor_holiday', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_holiday', 1.0)
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        print(f"... applying weekend factor ({demand_factors.get('factor_weekend', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_weekend', 1.0)
    
    forecast['mu'] = int(forecast['mu'])
    forecast['sigma'] = int(forecast['sigma'])
        
    print(f"Total forecast complete for {quota_type}: {forecast}")
    return forecast


def get_price_elastic_demand_forecast(total_demand_mu: int, 
                                      price_buckets: list) -> list:
    """
    (MOCK FUNCTION)
    Simulates a price-elastic demand forecast.
    
    In a real system, this would be a complex model. Here, we just
    split the total demand across the buckets using a predefined ratio.
    
    Args:
        total_demand_mu: The total forecasted demand (e.g., 150).
        price_buckets: The list of bucket dicts from config.
        
    Returns:
        A list of demand forecasts, one for each bucket.
        e.g., [100, 30, 20]
    """
    num_buckets = len(price_buckets)
    
    # --- Mock Ratios ---
    # We assume more demand for cheaper buckets.
    # These ratios are arbitrary and should be data-driven.
    if num_buckets == 3:
        ratios = [0.60, 0.30, 0.10] # 60% of demand for B1, 30% for B2, etc.
    elif num_buckets == 4:
        ratios = [0.50, 0.25, 0.15, 0.10]
    elif num_buckets == 5:
        ratios = [0.40, 0.25, 0.15, 0.10, 0.10]
    else:
        ratios = [1.0 / num_buckets] * num_buckets # Fallback
    
    # This is "independent" demand: the demand for *each* bucket
    # as if it were the only one offered.
    # For the LP, we need *cumulative* demand, but this is a common
    # simplification (D_b1 = demand willing to pay P_b1).
    demand_per_bucket = [int(total_demand_mu * r) for r in ratios]
    
    print(f"... MOCK price-elastic demand: {demand_per_bucket}")
    return demand_per_bucket