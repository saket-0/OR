# FILE 4: main_engine.py (UPDATED for Quota-Based Segmentation)

import numpy as np
from typing import Union 
from unconstraining import unconstrain_demand
from forecasting import forecast_demand
# Import the new optimization function
from optimization import calculate_quota_allocation 
from factor_calculator import calculate_demand_factors

# --- 1. DEFINE SYSTEM PARAMETERS ---

TRAVEL_CLASSES = ['1AC', '2AC', '3AC']
BOOKING_WINDOW_DAYS = 120 # Use the realistic 120-day window

CAPACITY = {'1AC': 30, '2AC': 60, '3AC': 110}

# FARE_BUCKETS are no longer used in this model, as we have fixed quota prices
# FARE_BUCKETS = { ... } 

# Prices are now per-quota, not per-intent
PRICES = {
    '1AC': {'general': 7000, 'tatkal': 8500},
    '2AC': {'general': 3000, 'tatkal': 4000},
    '3AC': {'general': 1800, 'tatkal': 2500}
}
EXTERNAL_FACTORS = {'is_holiday': True, 'day_of_week': 'Fri'}

# Historical data MUST now include the 'quota'
DETAILED_HISTORICAL_DATA = {
    '1AC': [
        {'train_id': 1, 'total_sold': 28, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 2,  'days_early': 1,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 25, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 30, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
    ],
    '2AC': [
        {'train_id': 1, 'total_sold': 55, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 5,  'days_early': 1,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 58, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 2,  'days_early': 1,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'TQ'},
        {'train_id': 3, 'total_sold': 55, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 50, 'days_early': 10, 'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 10, 'days_early': 1,  'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TQ'},
    ],
    '3AC': [
        {'train_id': 1, 'total_sold': 100, 'days_early': 5, 'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 10,  'days_early': 1, 'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 100, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 95,  'days_early': 0, 'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 90,  'days_early': 10,'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 20,  'days_early': 1, 'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TQ'},
        {'train_id': 5, 'total_sold': 105, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Tue', 'quota': 'GN'},
        {'train_id': 6, 'total_sold': 108, 'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 6, 'total_sold': 2,   'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'TQ'},
    ]
}


# --- 2. THE "GATEKEEPER" (PRICE QUOTER) ---
# (This function is no longer needed, as we have fixed quota prices)
# def get_offered_price(...)


# --- 3. RUN THE OFFLINE ENGINE (UPDATED) ---
def run_offline_engine(remaining_capacity_map: dict, days_remaining: int):
    """
    Runs the full RM process based on the *current* system state.
    Calculates the optimal *quota allocation* for the remaining days.
    """
    print("--- RUNNING DAILY OFFLINE ENGINE ---")
    
    optimal_allocations = {}
    
    for tc in TRAVEL_CLASSES:
        print(f"\n--- Processing Class: {tc} ---")
        
        # 1. Get *remaining* capacity for optimization
        class_capacity_remaining = remaining_capacity_map[tc]
        
        # 2. Get *total* capacity for unconstraining
        total_class_capacity = CAPACITY[tc]
        class_prices = PRICES[tc] 
        class_historical_data = DETAILED_HISTORICAL_DATA[tc]

        # --- 3. Run for GENERAL Quota ---
        hist_data_gn = [r for r in class_historical_data if r['quota'] == 'GN']
        # Only run if we have data
        if hist_data_gn:
            factors_gn = calculate_demand_factors(hist_data_gn, total_class_capacity)
            unconstrained_gn = [rec['true_demand'] for rec in hist_data_gn]
            forecast_gn = forecast_demand(
                unconstrained_gn, EXTERNAL_FACTORS, factors_gn, days_remaining, 'GN'
            )
        else:
            forecast_gn = {'mu': 0, 'sigma': 0} # No forecast if no data

        # --- 4. Run for TATKAL Quota ---
        hist_data_tq = [r for r in class_historical_data if r['quota'] == 'TQ']
        if hist_data_tq:
            factors_tq = calculate_demand_factors(hist_data_tq, total_class_capacity)
            unconstrained_tq = [rec['true_demand'] for rec in hist_data_tq]
            forecast_tq = forecast_demand(
                unconstrained_tq, EXTERNAL_FACTORS, factors_tq, days_remaining, 'TQ'
            )
        else:
            forecast_tq = {'mu': 0, 'sigma': 0} # No forecast if no data

        # --- 5. Optimize ---
        # Get the optimal quota allocation based on *remaining* capacity
        if class_capacity_remaining > 0:
            allocation = calculate_quota_allocation(
                forecast_gn, 
                forecast_tq, 
                class_prices, 
                class_capacity_remaining 
            )
        else:
            # If no seats are left, no allocation needed
            allocation = {'general_booking_limit': 0, 'tatkal_protection_level': 0}
        
        optimal_allocations[tc] = allocation

    print("--- DAILY OFFLINE RUN COMPLETE ---")
    return optimal_allocations


# --- 4. RUN THE DYNAMIC SIMULATION ---
def run_dynamic_simulation():
    """
    Simulates the 120-day booking window, re-calculating the
    quota allocations every single day.
    """
    print(f"\n--- RUNNING *DYNAMIC* ONLINE SIMULATION ({BOOKING_WINDOW_DAYS} Days) ---")
    
    # --- Initialize Simulation State ---
    total_revenue = 0
    # Track seats sold by quota
    seats_sold = {tc: {'GN': 0, 'TQ': 0} for tc in TRAVEL_CLASSES}
    bookings_accepted = {tc: {'GN': 0, 'TQ': 0} for tc in TRAVEL_CLASSES}
    bookings_rejected = {tc: {'GN': 0, 'TQ': 0} for tc in TRAVEL_CLASSES}
    
    current_allocations = {}

    # --- Main Simulation Loop (Day 120 down to Day 1) ---
    for day in range(BOOKING_WINDOW_DAYS, 0, -1):
        print(f"\n================ DAY {day} (Booking Window Open) ================")
        
        # 1. Get current total remaining capacity
        remaining_capacity = {}
        for tc in TRAVEL_CLASSES:
            total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
            remaining_capacity[tc] = CAPACITY[tc] - total_sold_for_class
        
        # 2. Re-run the offline engine to get new allocations for *today*
        current_allocations = run_offline_engine(remaining_capacity, day)
        print(f"Updated Allocations for Day {day}: {current_allocations}")

        # 3. Simulate customer arrivals for *this day*
        
        # --- GENERAL QUOTA WINDOW (Day 120 down to 2) ---
        if day > 1:
            for tc in TRAVEL_CLASSES:
                # Get the booking limit calculated by the optimizer
                gn_booking_limit = current_allocations[tc]['general_booking_limit']
                
                # Simulate arrivals for General quota
                # (Simple simulation: 5 arrivals per day)
                general_arrivals = np.random.poisson(5) 
                price_gn = PRICES[tc]['general']

                for _ in range(general_arrivals):
                    # --- NEW GATEKEEPER LOGIC ---
                    # We check two things:
                    # 1. Have we sold more than our 'GN' limit?
                    # 2. Is the class *actually* full?
                    total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
                    
                    if seats_sold[tc]['GN'] < gn_booking_limit and \
                       total_sold_for_class < CAPACITY[tc]:
                        
                        seats_sold[tc]['GN'] += 1
                        total_revenue += price_gn
                        bookings_accepted[tc]['GN'] += 1
                    else:
                        # Reject booking to *protect* seats for Tatkal or because full
                        bookings_rejected[tc]['GN'] += 1

        # --- TATKAL QUOTA WINDOW (Day 1) ---
        if day == 1:
            print("\n!!! TATKAL WINDOW OPEN !!!")
            for tc in TRAVEL_CLASSES:
                # Simulate a spike in Tatkal arrivals
                tatkal_arrivals = np.random.poisson(15) # High demand spike
                price_tq = PRICES[tc]['tatkal']

                for _ in range(tatkal_arrivals):
                    # --- NEW GATEKEEPER LOGIC ---
                    # Simple check: is there *any* seat left?
                    total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
                    
                    if total_sold_for_class < CAPACITY[tc]:
                        seats_sold[tc]['TQ'] += 1
                        total_revenue += price_tq
                        bookings_accepted[tc]['TQ'] += 1
                    else:
                        bookings_rejected[tc]['TQ'] += 1 # Sold out

    print("\n================ SIMULATION COMPLETE ================")
    print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
    
    print("\n--- FINAL CLASS BREAKDOWN ---")
    for tc in TRAVEL_CLASSES:
        total_sold = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
        
        print(f"\nClass: {tc}")
        print(f"  Seats Sold: {total_sold} / {CAPACITY[tc]}")
        print(f"  General Sold: {seats_sold[tc]['GN']}")
        print(f"  Tatkal Sold:  {seats_sold[tc]['TQ']}")

        print("\n  Customer Segment Analysis:")
        gn_fare = PRICES[tc]['general']
        tq_fare = PRICES[tc]['tatkal']
        print(f"  General (Fare: ₹{gn_fare}): {bookings_accepted[tc]['GN']} accepted, {bookings_rejected[tc]['GN']} rejected")
        print(f"  Tatkal  (Fare: ₹{tq_fare}):  {bookings_accepted[tc]['TQ']} accepted, {bookings_rejected[tc]['TQ']} rejected")

# --- RUN THE MODEL ---
if __name__ == "__main__":
    run_dynamic_simulation()