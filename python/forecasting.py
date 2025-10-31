# FILE 2: forecasting.py (UPDATED for Quota-Based Segmentation)

import numpy as np

def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    days_remaining: int,
                    quota_type: str) -> dict: # <-- MODIFIED ARGS
    """
    Forecasts the demand distribution for the *remaining* booking window
    for a *specific quota*.

    Args:
        unconstrained_estimates: List of *total* true demand from historical data 
                                 (for this specific quota).
        external_factors: Causal drivers for the new train.
        demand_factors: Calculated factors from historical data.
        days_remaining: How many days are left in the booking window.
        quota_type: The quota we are forecasting for ('GN' or 'TQ').

    Returns:
        A forecast dict for *remaining* demand for this quota.
    """
    print(f"Step 2: Forecasting demand for {quota_type} quota...")
    
    # Base mu is the average *total* demand for this quota from history
    base_mu = np.mean(unconstrained_estimates)
    
    # Forecast is now a single object, not nested
    forecast = {
        'mu': base_mu, 
        'sigma': base_mu * 0.15 # Std dev can be tuned
    }
    
    # --- APPLY CALCULATED FACTORS ---
    # (This logic is unchanged)
    if external_factors.get('is_holiday'):
        print(f"... applying holiday factor ({demand_factors.get('factor_holiday', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_holiday', 1.0)
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        print(f"... applying weekend factor ({demand_factors.get('factor_weekend', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_weekend', 1.0)
    # ---------------------------------

    # --- NEW: QUOTA-BASED SCALING ---
    # Scale forecast based on the rules for this quota
    scaling_factor = 0.0
    
    if quota_type == 'GN':
        # General quota sells from Day 120 down to Day 2.
        # We use (days_remaining - 1) because Day 1 is TQ-only.
        # Assumes a 120-day booking window.
        scaling_factor = max(0, days_remaining - 1) / 120.0 
    
    elif quota_type == 'TQ':
        # Tatkal quota sells *only* on Day 1.
        if days_remaining == 1:
            scaling_factor = 1.0
        else:
            scaling_factor = 0.0 # No Tatkal demand expected on other days
        
    # Clean up by converting to integers *after* scaling
    forecast['mu'] = int(forecast['mu'] * scaling_factor)
    forecast['sigma'] = int(forecast['sigma'] * scaling_factor)
        
    print(f"Forecast complete (for {days_remaining} days, {quota_type}): {forecast}")
    return forecast