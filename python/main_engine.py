# FILE 4: main_engine.py

import numpy as np
from unconstraining import unconstrain_demand
from forecasting import forecast_demand
from optimization import calculate_bid_price

# --- 1. DEFINE SYSTEM PARAMETERS ---

# Our inventory
CAPACITY = 200

# Our fare classes
PRICES = {
    'urgent': 6000,
    'leisure': 3000
}

# Causal factors for the train we are pricing
EXTERNAL_FACTORS = {
    'is_holiday': True,
    'day_of_week': 'Fri'
}

# Dummy historical data (from past train runs)
# 3 trains: 1 sold out 5 days early, 1 sold out 2 days early, 1 didn't sell out
HISTORICAL_SALES_DATA = [
    {'train_id': 1, 'days_before_departure': 5, 'total_sold': 200},
    {'train_id': 2, 'days_before_departure': 2, 'total_sold': 200},
    {'train_id': 3, 'days_before_departure': 0, 'total_sold': 185}
]


# --- 2. THE "GATEKEEPER" (Inventory Control Logic) ---
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
    estimates = unconstrain_demand(HISTORICAL_SALES_DATA, CAPACITY)
    forecast = forecast_demand(estimates, EXTERNAL_FACTORS)
    bid_price = calculate_bid_price(forecast, PRICES, CAPACITY)
    print("--- OFFLINE ENGINE RUN COMPLETE ---")
    return bid_price


# --- 4. RUN THE ONLINE SIMULATION (Simulates the booking window) ---
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