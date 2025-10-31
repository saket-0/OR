# FILE 4: engine.py (MODIFIED for Price-Elasticity)
# This file contains the "offline" engine logic.

from forecasting import forecast_demand, forecast_demand_by_price_point # <-- UPDATED IMPORT
from optimization import calculate_flexi_fare_allocation 
from factor_calculator import calculate_demand_factors

import config
from booking_curve_model import PICKUP_CURVE


def run_offline_engine(remaining_capacity_map: dict, days_remaining: int):
    """
    Runs the full RM process based on the *current* system state.
    Calculates the optimal *bucket allocations* for the remaining days.
    """
    print("--- RUNNING DAILY OFLINE ENGINE ---")
    
    optimal_allocations = {}
    
    for tc in config.TRAVEL_CLASSES:
        print(f"\n--- Processing Class: {tc} ---")
        
        class_capacity_remaining = remaining_capacity_map[tc]
        total_class_capacity = config.CAPACITY[tc]
        class_historical_data = config.DETAILED_HISTORICAL_DATA[tc]
        class_flexi_structure = config.FLEXI_FARE_STRUCTURE[tc]
        class_prices = [b['price'] for b in class_flexi_structure]

        # --- 3a. Forecast TOTAL General Demand (Potential Market) ---
        hist_data_gn = [r for r in class_historical_data if r['quota'] == 'GN']
        forecast_gn_total = {'mu': 0, 'sigma': 0}
        if hist_data_gn:
            factors_gn = calculate_demand_factors(hist_data_gn, total_class_capacity)
            unconstrained_gn = [rec['true_demand'] for rec in hist_data_gn]
            forecast_gn_total = forecast_demand(
                unconstrained_gn, config.EXTERNAL_FACTORS, factors_gn, 'GN'
            ) 
        
        # --- 3b. (NEW) Get Price-Elastic Demand Forecast ---
        # This function now splits demand based on a realistic elasticity model
        demand_by_bucket_total = forecast_demand_by_price_point( # <-- UPDATED FUNCTION CALL
            forecast_gn_total['mu'],
            class_flexi_structure
        )

        # --- 4. APPLY PICK-UP CURVE ---
        percent_sold_by_today = PICKUP_CURVE.get(days_remaining, 1.0)
        percent_still_to_come_gn = 1.0 - percent_sold_by_today
        
        # Apply the pick-up curve to *each bucket's* demand forecast
        forecast_gn_remaining_by_bucket = [
            int(d * percent_still_to_come_gn) for d in demand_by_bucket_total
        ]
        
        print(f"Total GN Market {forecast_gn_total['mu']}, Percent to come: {percent_still_to_come_gn:.2f}")
        print(f"Remaining forecast by bucket: {forecast_gn_remaining_by_bucket}")
        
        # --- 5. Optimize ---
        if class_capacity_remaining > 0:
            allocation = calculate_flexi_fare_allocation(
                forecast_gn_remaining_by_bucket, 
                class_prices, 
                class_capacity_remaining 
            )
        else:
            # Create an empty allocation if no seats are left
            allocation = {f'Bucket_{i}_Allocation': 0 for i in range(len(class_prices))}
        
        optimal_allocations[tc] = allocation

    print("--- DAILY OFFLINE RUN COMPLETE ---")
    return optimal_allocations