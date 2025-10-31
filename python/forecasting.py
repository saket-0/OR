# FILE 2: forecasting.py (UPDATED)

import numpy as np

def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict) -> dict: # <-- ACCEPT NEW ARGUMENT
    """
    Forecasts the demand distribution (mean & std dev) for each fare class.

    This *updated* model applies statistically-derived factors.

    Args:
        unconstrained_estimates: List of true demand estimates.
        external_factors: A dict of causal drivers for the *new* train.
        demand_factors: A dict of calculated factors from historical data.

    Returns:
        A forecast dict: {'leisure': {'mu': 150, 'sigma': 30}, 
                          'urgent': {'mu': 70, 'sigma': 20}}
    """
    print("Step 2: Forecasting demand for each customer class...")
    
    # Base mu is the average of our historical true demand
    base_mu = np.mean(unconstrained_estimates)
    
    # Base split: 70% Leisure, 30% Urgent (this could also be in demand_factors)
    forecast = {
        'leisure': {'mu': base_mu * 0.7, 'sigma': base_mu * 0.15},
        'urgent':  {'mu': base_mu * 0.3, 'sigma': base_mu * 0.05}
    }
    
    # --- APPLY CALCULATED FACTORS ---
    # Apply factors based on the *new train's* external_factors
    if external_factors.get('is_holiday'):
        print("... applying holiday factor")
        # Apply the *calculated* holiday factor
        forecast['urgent']['mu'] *= demand_factors.get('factor_holiday', 1.0)
        forecast['leisure']['mu'] *= demand_factors.get('factor_holiday', 1.0)
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        print("... applying weekend factor")
        # Apply the *calculated* weekend factor
        forecast['urgent']['mu'] *= demand_factors.get('factor_weekend', 1.0)
        forecast['leisure']['mu'] *= demand_factors.get('factor_weekend', 1.0)
    # ---------------------------------

    # Clean up by converting to integers
    for k in forecast:
        forecast[k]['mu'] = int(forecast[k]['mu'])
        forecast[k]['sigma'] = int(forecast[k]['sigma'])
        
    print(f"Forecast complete: {forecast}")
    return forecast
