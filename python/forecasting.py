# FILE 2: forecasting.py

import numpy as np

def forecast_demand(unconstrained_estimates: list, external_factors: dict) -> dict:
    """
    Forecasts the demand distribution (mean & std dev) for each fare class.

    This basic model splits the average unconstrained demand and applies
    external factors (like holidays).

    Args:
        unconstrained_estimates: List of true demand estimates from the unconstraining module.
        external_factors: A dict of causal drivers, e.g.,
                          {'is_holiday': True, 'day_of_week': 'Fri'}

    Returns:
        A forecast dict: {'leisure': {'mu': 150, 'sigma': 30}, 
                          'urgent': {'mu': 70, 'sigma': 20}}
    """
    print("Step 2: Forecasting demand for each customer class...")
    
    # Base mu is the average of our historical true demand
    base_mu = np.mean(unconstrained_estimates)
    
    # Base split: 70% Leisure, 30% Urgent
    forecast = {
        'leisure': {'mu': base_mu * 0.7, 'sigma': base_mu * 0.15},
        'urgent':  {'mu': base_mu * 0.3, 'sigma': base_mu * 0.05}
    }
    
    # Apply simple causal rules
    if external_factors.get('is_holiday'):
        # Holidays increase urgent demand
        forecast['urgent']['mu'] *= 1.5
        forecast['leisure']['mu'] *= 0.8 # Decrease leisure
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        # Weekends increase both
        forecast['urgent']['mu'] *= 1.2
        forecast['leisure']['mu'] *= 1.1

    # Clean up by converting to integers
    for k in forecast:
        forecast[k]['mu'] = int(forecast[k]['mu'])
        forecast[k]['sigma'] = int(forecast[k]['sigma'])
        
    print(f"Forecast complete: {forecast}")
    return forecast