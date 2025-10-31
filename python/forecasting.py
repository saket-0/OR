# FILE 2: forecasting.py (UPDATED for Pick-up Curves)

import numpy as np

def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    quota_type: str) -> dict: # <-- MODIFIED ARGS (days_remaining removed)
    """
    Forecasts the *total* demand distribution for a specific quota.
    The scaling by day is no longer done here.

    Args:
        unconstrained_estimates: List of *total* true demand from historical data 
                                 (for this specific quota).
        external_factors: Causal drivers for the new train.
        demand_factors: Calculated factors from historical data.
        quota_type: The quota we are forecasting for ('GN' or 'TQ').

    Returns:
        A forecast dict for *total* demand for this quota.
    """
    print(f"Step 2: Forecasting *total* demand for {quota_type} quota...")
    
    # Base mu is the average *total* demand for this quota from history
    base_mu = np.mean(unconstrained_estimates) if unconstrained_estimates else 0
    
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

    # --- SCALING LOGIC REMOVED ---
    # The main_engine will now use a pick-up curve to determine
    # *remaining* demand from this *total* forecast.
        
    forecast['mu'] = int(forecast['mu'])
    forecast['sigma'] = int(forecast['sigma'])
        
    print(f"Total forecast complete for {quota_type}: {forecast}")
    return forecast
