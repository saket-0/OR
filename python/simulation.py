# FILE 7: simulation.py (FIXED for Flexi-Fare)
# This file contains the "online" simulation logic.

import numpy as np
import config
from engine import run_offline_engine


def run_dynamic_simulation():
    """
    Simulates the 120-day booking window, re-calculating the
    Flexi-Fare bucket allocations every single day.
    """
    print(f"\n--- RUNNING *DYNAMIC* ONLINE SIMULATION ({config.BOOKING_WINDOW_DAYS} Days) ---")
    
    # --- Initialize Simulation State ---
    total_revenue = 0
    
    # Track seats sold *per bucket* (Total)
    seats_sold = {}
    bookings_accepted = {}
    bookings_rejected = {}
    for tc in config.TRAVEL_CLASSES:
        num_buckets = len(config.FLEXI_FARE_STRUCTURE[tc])
        seats_sold[tc] = {f'Bucket_{i}': 0 for i in range(num_buckets)}
        bookings_accepted[tc] = {f'Bucket_{i}': 0 for i in range(num_buckets)}
        bookings_rejected[tc] = {'total': 0} 
    
    current_allocations = {}

    # --- Main Simulation Loop (Day 120 down to Day 1) ---
    for day in range(config.BOOKING_WINDOW_DAYS, 0, -1):
        print(f"\n================ DAY {day} (Booking Window Open) ================")
        
        # 1. Get current total remaining capacity
        remaining_capacity = {}
        for tc in config.TRAVEL_CLASSES:
            total_sold_for_class = sum(seats_sold[tc].values())
            remaining_capacity[tc] = config.CAPACITY[tc] - total_sold_for_class
        
        # 2. Re-run the offline engine to get new *bucket allocations*
        #    This allocation is the optimal number of *additional* seats
        #    to sell from *this day forward*.
        current_allocations = run_offline_engine(remaining_capacity, day)
        print(f"Updated Allocations for Day {day}: {current_allocations}")

        # (NEW) We must track sales *for this day* against the new limit
        seats_sold_today = {}
        for tc in config.TRAVEL_CLASSES:
            num_buckets = len(config.FLEXI_FARE_STRUCTURE[tc])
            seats_sold_today[tc] = {f'Bucket_{i}': 0 for i in range(num_buckets)}

        # 3. Simulate customer arrivals for *this day*
        for tc in config.TRAVEL_CLASSES:
            class_buckets = config.FLEXI_FARE_STRUCTURE[tc]
            
            daily_arrivals = np.random.poisson(7) 

            for _ in range(daily_arrivals):
                total_sold_for_class = sum(seats_sold[tc].values())
                
                # Check overall capacity
                if total_sold_for_class >= config.CAPACITY[tc]:
                    bookings_rejected[tc]['total'] += 1
                    continue # Train is full

                # --- Flexi-Fare "Bid Price" Logic ---
                sold_ticket = False
                for i, bucket in enumerate(class_buckets):
                    bucket_alloc_key = f'Bucket_{i}_Allocation'
                    bucket_sold_key = f'Bucket_{i}'
                    
                    # Get the *new* limit for *additional* sales
                    bucket_limit_for_today = current_allocations[tc].get(bucket_alloc_key, 0)
                    # Get the number of sales *today*
                    num_sold_in_bucket_today = seats_sold_today[tc].get(bucket_sold_key, 0)
                    
                    # Check if we are still under *today's* limit
                    if num_sold_in_bucket_today < bucket_limit_for_today:
                        # Found an open bucket! Sell the ticket.
                        
                        # Increment *today's* sales tracker
                        seats_sold_today[tc][bucket_sold_key] += 1
                        # Increment *total* sales tracker
                        seats_sold[tc][bucket_sold_key] += 1
                        
                        total_revenue += bucket['price']
                        bookings_accepted[tc][bucket_sold_key] += 1
                        sold_ticket = True
                        break # Move to next customer
                
                if not sold_ticket:
                    # All buckets optimized for today are full
                    bookings_rejected[tc]['total'] += 1

    print("\n================ SIMULATION COMPLETE ================")
    print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
    
    print("\n--- FINAL CLASS BREAKDOWN ---")
    for tc in config.TRAVEL_CLASSES:
        total_sold = sum(seats_sold[tc].values())
        print(f"\nClass: {tc}")
        print(f"  Seats Sold: {total_sold} / {config.CAPACITY[tc]}")

        print("\n  Customer Segment Analysis:")
        for i, bucket in enumerate(config.FLEXI_FARE_STRUCTURE[tc]):
            bucket_sold_key = f'Bucket_{i}'
            num_accepted = bookings_accepted[tc][bucket_sold_key]
            price = bucket['price']
            print(f"  {bucket['name']} (Fare: ₹{price:,}): {num_accepted} accepted")
        
        print(f"  Total Rejected: {bookings_rejected[tc]['total']}")