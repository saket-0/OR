# FILE 4: main_engine.py (UPDATED for Dynamic Bid Price)

import numpy as np
from typing import Union 
from unconstraining import unconstrain_demand
from forecasting import forecast_demand
from optimization import calculate_bid_price
from factor_calculator import calculate_demand_factors

# --- 1. DEFINE SYSTEM PARAMETERS ---
# (This section is unchanged)

TRAVEL_CLASSES = ['1AC', '2AC', '3AC']
CAPACITY = {'1AC': 30, '2AC': 60, '3AC': 110}
FARE_BUCKETS = {
    '1AC': [7000, 8500, 10000, 12000],
    '2AC': [3000, 4000, 5000, 6000],
    '3AC': [1800, 2500, 3500, 4500] 
}
PRICES = {
    '1AC': {'urgent': 10000, 'leisure': 7000},
    '2AC': {'urgent': 6000,  'leisure': 3000},
    '3AC': {'urgent': 3500,  'leisure': 1800}
}
EXTERNAL_FACTORS = {'is_holiday': True, 'day_of_week': 'Fri'}
DETAILED_HISTORICAL_DATA = {
    '1AC': [
        {'train_id': 1, 'total_sold': 30, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri'},
        {'train_id': 2, 'total_sold': 25, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed'},
        {'train_id': 3, 'total_sold': 30, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri'},
    ],
    '2AC': [
        {'train_id': 1, 'total_sold': 60, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri'},
        {'train_id': 2, 'total_sold': 60, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed'},
        {'train_id': 3, 'total_sold': 55, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon'},
        {'train_id': 4, 'total_sold': 60, 'days_early': 10, 'is_holiday': True,  'day_of_week': 'Sun'},
    ],
    '3AC': [
        {'train_id': 1, 'total_sold': 110, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri'},
        {'train_id': 2, 'total_sold': 100, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Wed'},
        {'train_id': 3, 'total_sold': 95,  'days_early': 0, 'is_holiday': False, 'day_of_week': 'Mon'},
        {'train_id': 4, 'total_sold': 110, 'days_early': 10,'is_holiday': True,  'day_of_week': 'Sun'},
        {'train_id': 5, 'total_sold': 105, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Tue'},
        {'train_id': 6, 'total_sold': 110, 'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri'},
    ]
}


# --- 2. THE "GATEKEEPER" (PRICE QUOTER) ---
# (This function is unchanged and correct)
def get_offered_price(travel_class: str, bid_price: float, seats_available: int) -> Union[float, None]:
    if seats_available <= 0:
        return None
    available_buckets = FARE_BUCKETS[travel_class]
    for fare in available_buckets:
        if fare >= bid_price:
            return fare
    return None


# --- 3. RUN THE OFFLINE ENGINE (UPDATED) ---
def run_offline_engine(remaining_capacity_map: dict, days_remaining: int):
    """
    Runs the full RM process based on the *current* system state.
    
    Args:
        remaining_capacity_map: A dict of *remaining* seats for each class.
        days_remaining: How many days are left to sell.
    """
    print("--- RUNNING DAILY OFFLINE ENGINE ---")
    
    optimal_bid_prices = {}
    
    for tc in TRAVEL_CLASSES:
        print(f"\n--- Processing Class: {tc} ---")
        
        # --- KEY CHANGES HERE ---
        # 1. Use *remaining* capacity for optimization
        class_capacity_remaining = remaining_capacity_map[tc]
        
        # 2. Use *full* historical data for learning
        class_historical_data = DETAILED_HISTORICAL_DATA[tc]
        class_prices = PRICES[tc] 
        
        # We must get the *total* capacity for this class to unconstrain properly
        total_class_capacity = CAPACITY[tc]

        # Calculate factors (learning from history)
        demand_factors = calculate_demand_factors(class_historical_data, total_class_capacity)
        
        # Get unconstrained estimates (learning from history)
        unconstrained_estimates = [rec['true_demand'] for rec in class_historical_data]

        # Forecast *remaining* demand (using days_remaining)
        forecast = forecast_demand(
            unconstrained_estimates, 
            EXTERNAL_FACTORS, 
            demand_factors,
            days_remaining  # <-- Pass in remaining days
        ) 
        
        # Optimize based on *remaining* capacity
        bid_price = calculate_bid_price(
            forecast, 
            class_prices, 
            class_capacity_remaining # <-- Pass in remaining seats
        )
        
        optimal_bid_prices[tc] = bid_price

    print("--- DAILY OFFLINE RUN COMPLETE ---")
    return optimal_bid_prices


# --- 4. RUN THE DYNAMIC SIMULATION ---
def run_dynamic_simulation():
    """
    Simulates the 30-day booking window, re-calculating the
    bid price every single day.
    """
    print("\n--- RUNNING *DYNAMIC* ONLINE SIMULATION (30 Days) ---")
    
    # --- Initialize Simulation State ---
    total_revenue = 0
    seats_sold = {tc: 0 for tc in TRAVEL_CLASSES}
    bookings_accepted = {tc: {'leisure': 0, 'urgent': 0} for tc in TRAVEL_CLASSES}
    bookings_rejected = {tc: {'leisure': 0, 'urgent': 0} for tc in TRAVEL_CLASSES}
    
    # This will be updated every day
    current_bid_prices = {}

    # --- Main Simulation Loop (Day 30 down to Day 1) ---
    for day in range(30, 0, -1):
        print(f"\n================ DAY {day} (Booking Window Open) ================")
        
        # 1. Get current remaining capacity
        remaining_capacity = {tc: CAPACITY[tc] - seats_sold[tc] for tc in TRAVEL_CLASSES}
        
        # 2. Re-run the offline engine to get new bid prices for *today*
        current_bid_prices = run_offline_engine(remaining_capacity, day)
        print(f"Updated Bid Prices for Day {day}: {current_bid_prices}")

        # 3. Simulate customer arrivals for *this day*
        for tc in TRAVEL_CLASSES:
            
            class_bid_price = current_bid_prices[tc]
            class_capacity_total = CAPACITY[tc] # Total capacity
            
            # --- Customer Arrival Logic (unchanged) ---
            if tc == '3AC':
                leisure_lambda = 10 if day > 3 else 2
                urgent_lambda = 2 if day > 3 else 10
            elif tc == '2AC':
                leisure_lambda = 6 if day > 3 else 2
                urgent_lambda = 2 if day > 3 else 15
            else: # 1AC
                leisure_lambda = 2 if day > 3 else 1
                urgent_lambda = 1 if day > 3 else 5
            
            leisure_arrivals = np.random.poisson(leisure_lambda)
            urgent_arrivals = np.random.poisson(urgent_lambda)

            # --- Process Leisure Customers (with bug fix) ---
            leisure_wtp = PRICES[tc]['leisure']
            for _ in range(leisure_arrivals):
                seats_available = class_capacity_total - seats_sold[tc]
                offered_price = get_offered_price(tc, class_bid_price, seats_available)

                if offered_price is not None and leisure_wtp >= offered_price:
                    seats_sold[tc] += 1
                    total_revenue += offered_price 
                    bookings_accepted[tc]['leisure'] += 1
                else:
                    bookings_rejected[tc]['leisure'] += 1
                    
            # --- Process Urgent Customers (with bug fix) ---
            urgent_wtp = PRICES[tc]['urgent']
            for _ in range(urgent_arrivals):
                seats_available = class_capacity_total - seats_sold[tc]
                offered_price = get_offered_price(tc, class_bid_price, seats_available)

                if offered_price is not None and urgent_wtp >= offered_price:
                    seats_sold[tc] += 1
                    total_revenue += offered_price
                    bookings_accepted[tc]['urgent'] += 1
                else:
                    bookings_rejected[tc]['urgent'] += 1

    print("\n================ SIMULATION COMPLETE ================")
    print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
    
    print("\n--- FINAL CLASS BREAKDOWN ---")
    for tc in TRAVEL_CLASSES:
        # Get the very last bid price from Day 1
        final_bid_price = current_bid_prices.get(tc, 0)
        final_offered_price = get_offered_price(tc, final_bid_price, 1) 
        
        print(f"\nClass: {tc}")
        print(f"  Seats Sold: {seats_sold[tc]} / {CAPACITY[tc]}")
        print(f"  Final Bid Price (Day 1): ₹{final_bid_price:.0f}")
        print(f"  Final Offered Price:   ₹{final_offered_price if final_offered_price else 'SOLD OUT'}")
        
        print("\n  Customer Segment Analysis:")
        leisure_fare = PRICES[tc]['leisure']
        urgent_fare = PRICES[tc]['urgent']
        print(f"  Leisure (WTP: ₹{leisure_fare}): {bookings_accepted[tc]['leisure']} accepted, {bookings_rejected[tc]['leisure']} rejected")
        print(f"  Urgent  (WTP: ₹{urgent_fare}):  {bookings_accepted[tc]['urgent']} accepted, {bookings_rejected[tc]['urgent']} rejected")

# --- RUN THE MODEL ---
if __name__ == "__main__":
    run_dynamic_simulation() # <-- This is the new main call