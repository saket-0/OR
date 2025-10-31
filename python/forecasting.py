# FILE 2: forecasting.py (UPDATED with Price-Elasticity Model)

import numpy as np
import config

# --- NEW: Elasticity Parameters ---
# This controls how sensitive demand is to price changes.
# E > 1.0 = Elastic (demand changes a lot with price)
# E < 1.0 = Inelastic (demand changes little with price)
PRICE_ELASTICITY_COEFFICIENT = 1.5 


def forecast_demand(unconstrained_estimates: list, 
                    external_factors: dict, 
                    demand_factors: dict,
                    quota_type: str) -> dict:
    """
    Forecasts the *total potential market* for a specific quota.
    (This function is unchanged)
    """
    print(f"Step 2: Forecasting *total potential market* for {quota_type} quota...")
    
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
        
    print(f"Total potential market forecast for {quota_type}: {forecast}")
    return forecast


def forecast_demand_by_price_point(total_market_mu: int, 
                                   price_buckets: list) -> list:
    """
    (NEW) Simulates a price-elastic demand forecast.
    
    This model calculates an *independent* demand forecast for each
    price point, assuming demand decreases as price increases.
    
    Args:
        total_market_mu: The total forecasted demand (e.g., 150),
                         treated as the demand for the *base price*.
        price_buckets: The list of bucket dicts from config.
        
    Returns:
        A list of demand forecasts, one for each bucket.
        e.g., [150, 85, 60]
    """
    print(f"... simulating price-elastic demand from market size {total_market_mu}")
    
    if not price_buckets:
        return []

    # 1. Get the base price (lowest price, e.g., 1.0x)
    base_price_bucket = price_buckets[0]
    base_price = base_price_bucket['price']
    
    # 2. Assume the total market mu is the demand at the base price
    # This is a key assumption: D(base_price) = total_market_mu
    base_demand = total_market_mu
    
    demand_per_bucket = []
    
    for bucket in price_buckets:
        current_price = bucket['price']
        
        if current_price == base_price:
            # Demand for the base bucket is the total market
            demand_per_bucket.append(int(base_demand))
        else:
            # 3. Apply a price elasticity formula for higher prices
            # Formula: Demand(P) = Base_Demand * (Base_Price / P)^E
            # This is a "constant elasticity" model.
            price_ratio = base_price / current_price
            demand = base_demand * (price_ratio ** PRICE_ELASTICITY_COEFFICIENT)
            demand_per_bucket.append(int(demand))

    print(f"... Price-elastic demand forecast: {demand_per_bucket}")
    return demand_per_bucket