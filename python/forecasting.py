# FILE 2: forecasting.py (UPDATED for Dynamic Bid Price)

import numpy as np

def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    days_remaining: int) -> dict: # <-- NEW ARGUMENT
    """
    Forecasts the demand distribution for the *remaining* booking window.

    Args:
        unconstrained_estimates: List of *total* true demand from historical data.
        external_factors: Causal drivers for the new train.
        demand_factors: Calculated factors from historical data.
        days_remaining: How many days are left in the booking window.

    Returns:
        A forecast dict for *remaining* demand.
    """
    print("Step 2: Forecasting demand for each customer class...")
    
    # Base mu is the average *total* demand from history
    base_mu = np.mean(unconstrained_estimates)
    
    # Base split: 70% Leisure, 30% Urgent
    forecast = {
        'leisure': {'mu': base_mu * 0.7, 'sigma': base_mu * 0.15},
        'urgent':  {'mu': base_mu * 0.3, 'sigma': base_mu * 0.05}
    }
    
    # --- APPLY CALCULATED FACTORS ---
    if external_factors.get('is_holiday'):
        print(f"... applying holiday factor ({demand_factors.get('factor_holiday', 1.0):.2f})")
        forecast['urgent']['mu'] *= demand_factors.get('factor_holiday', 1.0)
        forecast['leisure']['mu'] *= demand_factors.get('factor_holiday', 1.0)
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        print(f"... applying weekend factor ({demand_factors.get('factor_weekend', 1.0):.2f})")
        forecast['urgent']['mu'] *= demand_factors.get('factor_weekend', 1.0)
        forecast['leisure']['mu'] *= demand_factors.get('factor_weekend', 1.0)
    # ---------------------------------

    # --- NEW: SCALE FORECAST BY DAYS REMAINING ---
    # Heuristic: Assume demand is distributed linearly over the 30-day window.
    # A real model would use "pick-up curves," but this is a solid start.
    scaling_factor = days_remaining / 30.0 
    
    # Clean up by converting to integers *after* scaling
    for k in forecast:
        forecast[k]['mu'] = int(forecast[k]['mu'] * scaling_factor)
        forecast[k]['sigma'] = int(forecast[k]['sigma'] * scaling_factor)
        
    print(f"Forecast complete (for {days_remaining} days): {forecast}")
    return forecast