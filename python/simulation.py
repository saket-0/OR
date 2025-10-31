# FILE 7: simulation.py (NEW)
# This file contains the "online" simulation logic.
# It simulates the 120-day booking window.

import numpy as np

# Import the config data
import config
# Import the offline engine to be run daily
from engine import run_offline_engine


def run_dynamic_simulation():
    """
    Simulates the 120-day booking window, re-calculating the
    quota allocations every single day.
    """
    print(f"\n--- RUNNING *DYNAMIC* ONLINE SIMULATION ({config.BOOKING_WINDOW_DAYS} Days) ---")
    
    # --- Initialize Simulation State ---
    total_revenue = 0
    seats_sold = {tc: {'GN': 0, 'TQ': 0} for tc in config.TRAVEL_CLASSES}
    bookings_accepted = {tc: {'GN': 0, 'TQ': 0} for tc in config.TRAVEL_CLASSES}
    bookings_rejected = {tc: {'GN': 0, 'TQ': 0} for tc in config.TRAVEL_CLASSES}
    
    current_allocations = {}

    # --- Main Simulation Loop (Day 120 down to Day 1) ---
    for day in range(config.BOOKING_WINDOW_DAYS, 0, -1):
        print(f"\n================ DAY {day} (Booking Window Open) ================")
        
        # 1. Get current total remaining capacity
        remaining_capacity = {}
        for tc in config.TRAVEL_CLASSES:
            total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
            remaining_capacity[tc] = config.CAPACITY[tc] - total_sold_for_class
        
        # 2. Re-run the offline engine to get new allocations for *today*
        current_allocations = run_offline_engine(remaining_capacity, day)
        print(f"Updated Allocations for Day {day}: {current_allocations}")

        # 3. Simulate customer arrivals for *this day*
        
        # --- GENERAL QUOTA WINDOW (Day 120 down to 2) ---
        if day > 1:
            for tc in config.TRAVEL_CLASSES:
                gn_booking_limit = current_allocations[tc]['general_booking_limit']
                
                general_arrivals = np.random.poisson(5) 
                price_gn = config.PRICES[tc]['general']

                for _ in range(general_arrivals):
                    total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
                    
                    if seats_sold[tc]['GN'] < gn_booking_limit and \
                       total_sold_for_class < config.CAPACITY[tc]:
                        
                        seats_sold[tc]['GN'] += 1
                        total_revenue += price_gn
                        bookings_accepted[tc]['GN'] += 1
                    else:
                        bookings_rejected[tc]['GN'] += 1

        # --- TATKAL QUOTA WINDOW (Day 1) ---
        if day == 1:
            print("\n!!! TATKAL WINDOW OPEN !!!")
            for tc in config.TRAVEL_CLASSES:
                tatkal_arrivals = np.random.poisson(15) 
                price_tq = config.PRICES[tc]['tatkal']

                for _ in range(tatkal_arrivals):
                    total_sold_for_class = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
                    
                    if total_sold_for_class < config.CAPACITY[tc]:
                        seats_sold[tc]['TQ'] += 1
                        total_revenue += price_tq
                        bookings_accepted[tc]['TQ'] += 1
                    else:
                        bookings_rejected[tc]['TQ'] += 1 

    print("\n================ SIMULATION COMPLETE ================")
    print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
    
    print("\n--- FINAL CLASS BREAKDOWN ---")
    for tc in config.TRAVEL_CLASSES:
        total_sold = seats_sold[tc]['GN'] + seats_sold[tc]['TQ']
        
        print(f"\nClass: {tc}")
        print(f"  Seats Sold: {total_sold} / {config.CAPACITY[tc]}")
        print(f"  General Sold: {seats_sold[tc]['GN']}")
        print(f"  Tatkal Sold:  {seats_sold[tc]['TQ']}")

        print("\n  Customer Segment Analysis:")
        gn_fare = config.PRICES[tc]['general']
        tq_fare = config.PRICES[tc]['tatkal']
        print(f"  General (Fare: ₹{gn_fare}): {bookings_accepted[tc]['GN']} accepted, {bookings_rejected[tc]['GN']} rejected")
        print(f"  Tatkal  (Fare: ₹{tq_fare}):  {bookings_accepted[tc]['TQ']} accepted, {bookings_rejected[tc]['TQ']} rejected")