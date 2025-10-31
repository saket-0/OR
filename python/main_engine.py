# FILE 4: main_engine.py (UPDATED for Multi-Class)

import numpy as np
from unconstraining import unconstrain_demand
from forecasting import forecast_demand
from optimization import calculate_bid_price
from factor_calculator import calculate_demand_factors

# --- 1. DEFINE SYSTEM PARAMETERS (Now by Class) ---

# Define the classes we are managing
TRAVEL_CLASSES = ['1AC', '2AC', '3AC']

# Inventory for each class
CAPACITY = {
    '1AC': 30,
    '2AC': 60,
    '3AC': 110
    # Total = 200
}

# Fare classes (leisure/urgent) *within* each travel class
PRICES = {
    '1AC': {'urgent': 10000, 'leisure': 7000},
    '2AC': {'urgent': 6000,  'leisure': 3000},
    '3AC': {'urgent': 3500,  'leisure': 1800}
}

# Causal factors for the *new* train we are pricing
# (These are train-level, so they apply to all classes)
EXTERNAL_FACTORS = {
    'is_holiday': True,
    'day_of_week': 'Fri'
}

# --- Detailed Historical Data (Now broken down by class) ---
# In a real system, this would come from a database query
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


# --- 2. THE "GATEKEEPER" (Inventory Control Logic) ---
# (This function is unchanged, it is generic)
def should_accept_booking(fare: float, bid_price: float, seats_available: int) -> bool:
    """
    The real-time Bid-Price Control logic.
    Accepts a booking if the fare is >= the opportunity cost (bid price)
    and a seat is available.
    """
    if seats_available <= 0:
        return False
    
    # This is the core rule!
    return fare >= bid_price


# --- 3. RUN THE OFFLINE ENGINE (Once per day) ---
def run_offline_engine():
    """
    Runs the full RM process *for each travel class* to generate
    a dictionary of optimal bid prices.
    """
    print("--- RUNNING OFFLINE ENGINE FOR ALL CLASSES ---")
    
    optimal_bid_prices = {}
    
    for tc in TRAVEL_CLASSES:
        print(f"\n--- Processing Class: {tc} ---")
        
        # 1. Get data for *this class only*
        class_capacity = CAPACITY[tc]
        class_historical_data = DETAILED_HISTORICAL_DATA[tc]
        class_prices = PRICES[tc]

        # 2. Calculate factors from this class's data
        #
        demand_factors = calculate_demand_factors(class_historical_data, class_capacity)
        
        # 3. Get unconstrained estimates for this class
        #
        unconstrained_estimates = [rec['true_demand'] for rec in class_historical_data]

        # 4. Forecast demand for this class
        #
        forecast = forecast_demand(
            unconstrained_estimates, 
            EXTERNAL_FACTORS, 
            demand_factors
        ) 
        
        # 5. Optimize to find the bid price for this class
        #
        bid_price = calculate_bid_price(forecast, class_prices, class_capacity)
        
        # 6. Store the result
        optimal_bid_prices[tc] = bid_price

    print("\n--- OFFLINE ENGINE RUN COMPLETE ---")
    print(f"Final Bid Prices: {optimal_bid_prices}")
    return optimal_bid_prices


# --- 4. RUN THE ONLINE SIMULATION (Simulates the booking window) ---
def run_online_simulation(bid_prices: dict):
    """
    Simulates the 30-day booking window using the Bid-Price Gatekeeper
    for each separate travel class.
    
    Args:
        bid_prices: A dict of bid prices, e.g.,
                    {'1AC': 7500.0, '2AC': 3100.0, '3AC': 1900.0}
    """
    print("\n--- RUNNING ONLINE SIMULATION (ALL CLASSES) ---")
    
    # --- Simulation State (Track everything by class) ---
    total_revenue = 0
    seats_sold = {tc: 0 for tc in TRAVEL_CLASSES}
    
    bookings_accepted = {
        tc: {'leisure': 0, 'urgent': 0} for tc in TRAVEL_CLASSES
    }
    bookings_rejected = {
        tc: {'leisure': 0, 'urgent': 0} for tc in TRAVEL_CLASSES
    }
    # ----------------------------------------------------

    for day in range(30, 0, -1): # Loop from Day 30 down to Day 1
        
        # --- Simulate Customer Arrivals for *EACH CLASS* ---
        for tc in TRAVEL_CLASSES:
            
            # Get class-specific info
            class_bid_price = bid_prices[tc]
            class_prices = PRICES[tc]
            class_capacity = CAPACITY[tc]
            
            # Simulate different arrival patterns for each class
            # (e.g., 3AC books earlier, 1AC books later)
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

            # --- Process Leisure Customers for this class ---
            for _ in range(leisure_arrivals):
                fare = class_prices['leisure']
                seats_available = class_capacity - seats_sold[tc]
                
                if should_accept_booking(fare, class_bid_price, seats_available):
                    seats_sold[tc] += 1
                    total_revenue += fare
                    bookings_accepted[tc]['leisure'] += 1
                else:
                    bookings_rejected[tc]['leisure'] += 1
                    
            # --- Process Urgent Customers for this class ---
            for _ in range(urgent_arrivals):
                fare = class_prices['urgent']
                seats_available = class_capacity - seats_sold[tc]
                
                if should_accept_booking(fare, class_bid_price, seats_available):
                    seats_sold[tc] += 1
                    total_revenue += fare
                    bookings_accepted[tc]['urgent'] += 1
                else:
                    bookings_rejected[tc]['urgent'] += 1

    print("--- SIMULATION COMPLETE ---")
    print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
    
    print("\n--- CLASS BREAKDOWN ---")
    for tc in TRAVEL_CLASSES:
        print(f"\nClass: {tc}")
        print(f"  Seats Sold: {seats_sold[tc]} / {CAPACITY[tc]}")
        print(f"  Bid Price:  ₹{bid_prices[tc]:.0f}")
        print(f"  Leisure:  {bookings_accepted[tc]['leisure']} accepted, {bookings_rejected[tc]['leisure']} rejected (Fare: ₹{PRICES[tc]['leisure']})")
        print(f"  Urgent:   {bookings_accepted[tc]['urgent']} accepted, {bookings_rejected[tc]['urgent']} rejected (Fare: ₹{PRICES[tc]['urgent']})")

        if bid_prices[tc] > PRICES[tc]['leisure']:
            print("  ANALYSIS: Bid price was > leisure fare. Model *intentionally* saved seats.")
        else:
            print("  ANALYSIS: Bid price was <= leisure fare. Model accepted 'first come, first served'.")

# --- RUN THE MODEL ---
if __name__ == "__main__":
    all_class_bid_prices = run_offline_engine()
    run_online_simulation(all_class_bid_prices)