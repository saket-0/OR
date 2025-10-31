# FILE 4: engine.py (MODIFIED from main_engine.py)
# This file contains the "offline" engine logic.
# Its only job is to run the analysis and optimization.

from forecasting import forecast_demand
from optimization import calculate_quota_allocation 
from factor_calculator import calculate_demand_factors

# Import models and config data from other files
import config
from booking_curve_model import PICKUP_CURVE


def run_offline_engine(remaining_capacity_map: dict, days_remaining: int):
    """
    Runs the full RM process based on the *current* system state.
    Calculates the optimal *quota allocation* for the remaining days.
    """
    print("--- RUNNING DAILY OFFLINE ENGINE ---")
    
    optimal_allocations = {}
    
    for tc in config.TRAVEL_CLASSES:
        print(f"\n--- Processing Class: {tc} ---")
        
        class_capacity_remaining = remaining_capacity_map[tc]
        total_class_capacity = config.CAPACITY[tc]
        class_prices = config.PRICES[tc] 
        class_historical_data = config.DETAILED_HISTORICAL_DATA[tc]

        # --- 3a. Forecast TOTAL General Demand ---
        hist_data_gn = [r for r in class_historical_data if r['quota'] == 'GN']
        forecast_gn_total = {'mu': 0, 'sigma': 0}
        if hist_data_gn:
            factors_gn = calculate_demand_factors(hist_data_gn, total_class_capacity)
            unconstrained_gn = [rec['true_demand'] for rec in hist_data_gn]
            forecast_gn_total = forecast_demand(
                unconstrained_gn, config.EXTERNAL_FACTORS, factors_gn, 'GN'
            ) 
        
        # --- 3b. Forecast TOTAL Tatkal Demand ---
        hist_data_tq = [r for r in class_historical_data if r['quota'] == 'TQ']
        forecast_tq_total = {'mu': 0, 'sigma': 0}
        if hist_data_tq:
            factors_tq = calculate_demand_factors(hist_data_tq, total_class_capacity)
            unconstrained_tq = [rec['true_demand'] for rec in hist_data_tq]
            forecast_tq_total = forecast_demand(
                unconstrained_tq, config.EXTERNAL_FACTORS, factors_tq, 'TQ'
            )

        # --- 4. APPLY PICK-UP CURVE ---
        percent_sold_by_today = PICKUP_CURVE.get(days_remaining, 1.0)
        percent_still_to_come_gn = 1.0 - percent_sold_by_today
        
        forecast_gn_remaining = {
            'mu': int(forecast_gn_total['mu'] * percent_still_to_come_gn),
            'sigma': int(forecast_gn_total['sigma'] * percent_still_to_come_gn)
        }
        
        if days_remaining == 1:
            forecast_tq_remaining = forecast_tq_total
        else:
            forecast_tq_remaining = {'mu': 0, 'sigma': 0}
        
        print(f"Total GN forecast {forecast_gn_total}, Percent to come: {percent_still_to_come_gn:.2f}, Remaining GN forecast {forecast_gn_remaining}")
        print(f"Total TQ forecast {forecast_tq_total}, Remaining TQ forecast {forecast_tq_remaining}")
        
        # --- 5. Optimize ---
        if class_capacity_remaining > 0:
            allocation = calculate_quota_allocation(
                forecast_gn_remaining, 
                forecast_tq_remaining, 
                class_prices, 
                class_capacity_remaining 
            )
        else:
            allocation = {'general_booking_limit': 0, 'tatkal_protection_level': 0}
        
        optimal_allocations[tc] = allocation

    print("--- DAILY OFFLINE RUN COMPLETE ---")
    return optimal_allocations