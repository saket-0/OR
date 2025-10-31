# FILE 4: main_engine.py (UPDATED)

import numpy as np
from unconstraining import unconstrain_demand
from forecasting import forecast_demand
from optimization import calculate_bid_price
from factor_calculator import calculate_demand_factors # <-- IMPORT NEW MODULE

# --- 1. DEFINE SYSTEM PARAMETERS ---

# Our inventory
CAPACITY = 200

# Our fare classes
PRICES = {
    'urgent': 6000,
    'leisure': 3000
}

# Causal factors for the *new* train we are pricing
EXTERNAL_FACTORS = {
    'is_holiday': True,
    'day_of_week': 'Fri'
}

# --- UPDATED HISTORICAL DATA ---
# This data is now more detailed, with tags for holidays/weekends
# This is the data we learn from.
DETAILED_HISTORICAL_DATA = [
    {'train_id': 1, 'total_sold': 200, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri'},
    {'train_id': 2, 'total_sold': 200, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed'},
    {'train_id': 3, 'total_sold': 185, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon'},
    {'train_id': 4, 'total_sold': 200, 'days_early': 10, 'is_holiday': True,  'day_of_week': 'Sun'},
    {'train_id': 5, 'total_sold': 190, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Tue'},
    {'train_id': 6, 'total_sold': 200, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri'},
]


# --- 2. THE "GATEKEEPER" (Inventory Control Logic) ---
# (This function is unchanged)
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
    Runs the full RM process to generate the optimal bid price.
    In reality, this runs once per day to update the price.
    """
    print("--- RUNNING OFFLINE ENGINE ---")
    
    # --- NEW STEP: Calculate factors from all past data ---
    demand_factors = calculate_demand_factors(DETAILED_HISTORICAL_DATA, CAPACITY)
    
    # Step 1: Unconstrain *just* the most recent data to get a baseline
    # (Note: The factor calculator already ran this, but we run it
    # again on all data to get the most up-to-date average)
    #
    unconstrained_estimates = [rec['true_demand'] for rec in DETAILED_HISTORICAL_DATA]

    # Step 2: Forecast demand using the *new factors*
    #
    forecast = forecast_demand(
        unconstrained_estimates, 
        EXTERNAL_FACTORS, 
        demand_factors # <-- PASS THE FACTORS
    ) 
    
    # Step 3: Optimize
    #
    bid_price = calculate_bid_price(forecast, PRICES, CAPACITY)
    
    print("--- OFFLINE ENGINE RUN COMPLETE ---")
    return bid_price


# --- 4. RUN THE ONLINE SIMULATION (Simulates the booking window) ---
# (This function is unchanged)
def run_online_simulation(bid_price: float):
    """
    Simulates the 30-day booking window using the Bid-Price Gatekeeper.
    """
    print("\n--- RUNNING ONLINE SIMULATION ---")
    
    revenue = 0
    seats_sold = 0
    bookings_accepted = {'leisure': 0, 'urgent': 0}
    bookings_rejected = {'leisure': 0, 'urgent': 0}

    for day in range(30, 0, -1): # Loop from Day 30 down to Day 1
        
        # Simulate customer arrivals (Poisson distribution)
        # Leisure: High arrivals early, low arrivals late
        leisure_lambda = 10 if day > 3 else 2
        # Urgent: Low arrivals early, high arrivals late
        urgent_lambda = 2 if day > 3 else 20
        
        leisure_arrivals = np.random.poisson(leisure_lambda)
        urgent_arrivals = np.random.poisson(urgent_lambda)

        # Process Leisure Customers
        for _ in range(leisure_arrivals):
            if should_accept_booking(PRICES['leisure'], bid_price, CAPACITY - seats_sold):
                seats_sold += 1
                revenue += PRICES['leisure']
                bookings_accepted['leisure'] += 1
            else:
                bookings_rejected['leisure'] += 1
                
        # Process Urgent Customers
        for _ in range(urgent_arrivals):
            if should_accept_booking(PRICES['urgent'], bid_price, CAPACITY - seats_sold):
                seats_sold += 1
                revenue += PRICES['urgent']
                bookings_accepted['urgent'] += 1
            else:
                bookings_rejected['urgent'] += 1

    print("--- SIMULATION COMPLETE ---")
    print(f"\nTotal Seats Sold: {seats_sold} / {CAPACITY}")
    print(f"Total Revenue: ₹{revenue:,}")
    print("\nBOOKING BREAKDOWN:")
    print(f"  Leisure: {bookings_accepted['leisure']} accepted, {bookings_rejected['leisure']} rejected")
    print(f"  Urgent:  {bookings_accepted['urgent']} accepted, {bookings_rejected['urgent']} rejected")
    
    if bid_price > PRICES['leisure']:
        print(f"\nANALYSIS: The bid price (₹{bid_price:.0f}) was higher than the leisure fare (₹{PRICES['leisure']}).")
        print("This means the model *intentionally* rejected leisure customers to save seats for urgent ones.")
    else:
        print(f"\nANALYSIS: The bid price (₹{bid_price:.0f}) was at or below the leisure fare (₹{PRICES['leisure']}).")
        print("This means the model predicted low demand and accepted all customer types ('first come, first served').")

# --- RUN THE MODEL ---
if __name__ == "__main__":
    optimal_bid_price = run_offline_engine()
    run_online_simulation(optimal_bid_price)