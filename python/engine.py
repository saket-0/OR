# FILE 4: engine.py (UPDATED for Stochastic Mode)
# This file's job is *only* to forecast total demand.

import numpy as np # <-- For stochastic sampling
from forecasting import (
    forecast_demand, 
    forecast_demand_by_price_point,
    get_flat_price_demand_forecast
)
from factor_calculator import calculate_demand_factors

import config
import pulp

def _convert_cumulative_to_independent_demand(cumulative_demand: list) -> list:
    """Helper to convert cumulative [100, 70, 30] to independent [30, 40, 30]."""
    independent_demand = []
    for i in range(len(cumulative_demand)):
        if i == len(cumulative_demand) - 1:
            independent_demand.append(cumulative_demand[i])
        else:
            demand_at_this_price_only = cumulative_demand[i] - cumulative_demand[i+1]
            independent_demand.append(demand_at_this_price_only)
    return independent_demand


def get_quota_forecasts(stochastic_mode: bool = False): # <-- For stochastic sampling
    """
    Runs "End-of-Horizon" forecasts for ALL quotas to get
    their total demand and expected revenue potential.
    
    This is the main "offline" process.
    
    Args:
        stochastic_mode: If True, samples demand from a normal distribution
                         instead of using the fixed mean (mu).
    """
    if not stochastic_mode:
        print("--- RUNNING 'END-OF-HORIZON' FORECASTING ENGINE (Deterministic Mode) ---")
    
    all_quota_forecasts = {}
    
    for tc in config.TRAVEL_CLASSES:
        if not stochastic_mode:
            print(f"\n================ Processing Class: {tc} ================")
        all_quota_forecasts[tc] = {}
        total_class_capacity = config.CAPACITY[tc]

        for q_code, q_config in config.QUOTA_CONFIG.items():
            if not stochastic_mode:
                print(f"\n--- Forecasting TOTAL demand for Quota: {q_code} ---")

            class_historical_data = [
                r for r in config.DETAILED_HISTORICAL_DATA[tc] 
                if r['quota'] == q_code
            ]

            forecast_total = {'mu': 0, 'sigma': 0}
            if class_historical_data:
                factors = calculate_demand_factors(class_historical_data, total_class_capacity, quiet=stochastic_mode)
                unconstrained = [rec['true_demand'] for rec in class_historical_data]
                forecast_total = forecast_demand(
                    unconstrained, config.EXTERNAL_FACTORS, factors, q_code, quiet=stochastic_mode
                )
            
            total_market_mu = forecast_total['mu']
            total_market_sigma = forecast_total['sigma'] # Get sigma
            
            if total_market_mu == 0 and not class_historical_data:
                 if not stochastic_mode:
                    print("... No historical data, using fallback demand 10.")
                 total_market_mu = 10 
                 total_market_sigma = total_market_mu * 0.15 # Assign a sigma

            # --- STOCHASTIC MODE LOGIC ---
            if stochastic_mode:
                # Sample the total market demand from its distribution
                sampled_mu = np.random.normal(total_market_mu, total_market_sigma)
                # Ensure demand is non-negative
                total_market_mu = max(0, int(sampled_mu))
            # --- (END) ---

            cumulative_demand_total = []
            prices = []
            
            if q_config['type'] == 'FLEXI':
                price_buckets = q_config['price_config'][tc]
                (cumulative_demand_total, prices) = forecast_demand_by_price_point(
                    total_market_mu, price_buckets, quiet=stochastic_mode
                )
            elif q_config['type'] == 'FLAT':
                price = q_config['price_config'][tc]
                (cumulative_demand_total, prices) = get_flat_price_demand_forecast(
                    total_market_mu, price, quiet=stochastic_mode
                )

            independent_demand_total = _convert_cumulative_to_independent_demand(
                cumulative_demand_total
            )
            
            # Calculate total demand and avg revenue for the master allocator
            total_demand = sum(independent_demand_total)
            max_revenue = sum(
                independent_demand_total[i] * prices[i] for i in range(len(prices))
            )
            avg_revenue = (max_revenue / total_demand) if total_demand > 0 else 0
            
            if not stochastic_mode:
                print(f"TOTAL Independent demand for {q_code}: {independent_demand_total}")
                print(f"Max Revenue: {max_revenue}, Total Demand: {total_demand}, Avg Revenue: {avg_revenue:.2f}")

            # Store the data for the allocators
            all_quota_forecasts[tc][q_code] = {
                'total_demand': total_demand,
                'avg_revenue_per_seat': avg_revenue,
                'independent_bucket_demands': independent_demand_total,
                'prices': prices
            }
    
    if not stochastic_mode:
        print("\n--- FORECASTING ENGINE COMPLETE ---")
    return all_quota_forecasts