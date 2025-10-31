# FILE 2: forecasting.py (UPDATED for Multi-Quota)

import numpy as np
import config

# --- Elasticity Parameters ---
PRICE_ELASTICITY_COEFFICIENT = 1.5 


def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    quota_type: str) -> dict:
    """
    Forecasts the *total potential market* for a specific quota.
    (This function is unchanged)
    """
    print(f"\nStep 2: Forecasting *total potential market* for {quota_type} quota...")
    
    base_mu = np.mean(unconstrained_estimates) if unconstrained_estimates else 0
    forecast = {'mu': base_mu, 'sigma': base_mu * 0.15}
    
    if external_factors.get('is_holiday'):
        print(f"... applying holiday factor ({demand_factors.get('factor_holiday', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_holiday', 1.0)
        
    if external_factors.get('day_of_week') in ['Fri', 'Sun']:
        print(f"... applying weekend factor ({demand_factors.get('factor_weekend', 1.0):.2f})")
        forecast['mu'] *= demand_factors.get('factor_weekend', 1.0)
    
    forecast['mu'] = int(forecast['mu'])
    forecast['sigma'] = int(forecast['sigma'])
        
    print(f"Total potential market forecast for {quota_type}: {forecast}")
    return forecast


def forecast_demand_by_price_point(total_market_mu: int, 
                                   price_buckets: list) -> (list, list):
    """
    (UPDATED) Simulates a price-elastic CUMULATIVE demand forecast for FLEXI quotas.
    
    Returns:
        A tuple of (cumulative_demand_list, price_list)
        e.g., ([150, 85, 60], [1800, 1980, 2160])
    """
    print(f"... simulating price-elastic demand from market size {total_market_mu}")
    prices = [b['price'] for b in price_buckets]
    
    if not price_buckets:
        return ([], [])

    base_price = price_buckets[0]['price']
    base_demand = total_market_mu
    cumulative_demand_per_bucket = []
    
    for bucket in price_buckets:
        current_price = bucket['price']
        if current_price == base_price:
            cumulative_demand_per_bucket.append(int(base_demand))
        else:
            price_ratio = base_price / current_price
            demand = base_demand * (price_ratio ** PRICE_ELASTICITY_COEFFICIENT)
            cumulative_demand_per_bucket.append(int(demand))

    print(f"... CUMULATIVE price-elastic demand: {cumulative_demand_per_bucket}")
    return (cumulative_demand_per_bucket, prices)


def get_flat_price_demand_forecast(total_market_mu: int, 
                                   price: int) -> (list, list):
    """
    (NEW) Formats the demand for a FLAT price quota.
    
    Returns:
        A tuple of (cumulative_demand_list, price_list)
        e.g., ([20], [2600])
    """
    print(f"... formatting FLAT price demand for market size {total_market_mu}")
    
    # For a flat price, the "cumulative" demand is just the total market
    # forecast, and there is only one price.
    cumulative_demand = [int(total_market_mu)]
    prices = [price]
    
    print(f"... FLAT price demand: {cumulative_demand} at {prices}")
    return (cumulative_demand, prices)