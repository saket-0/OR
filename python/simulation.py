# FILE 7: simulation.py (UPDATED for Stochastic/Quiet Mode - CORRECTED)

import numpy as np
import config
from engine import get_quota_forecasts 
from allocation_engine import partition_capacity_by_quota, partition_quota_into_buckets
# (NEW) Import both curves
from booking_curve_model import GENERAL_PICKUP_CURVE, LADIES_PICKUP_CURVE

def _get_or_initialize_key(data_dict, key, default_val=0):
    """Helper to safely initialize nested dict keys."""
    if key not in data_dict:
        data_dict[key] = default_val
    return data_dict[key]


def run_dynamic_simulation(stochastic_mode: bool = False, quiet_mode: bool = False): # <-- (NEW)
    """
    (UPDATED) Simulates the 120-day booking window using
    a 2-step static allocation and quota-specific booking curves.
    
    (NEW) Args:
        stochastic_mode: Passed to engine.get_quota_forecasts()
        quiet_mode: Suppresses all print output for fast simulation runs.
    """
    
    # --- 1. OFFLINE PHASE: Run Forecasts ---
    # Pass the stochastic_mode flag to the forecasting engine
    # Note: get_quota_forecasts uses stochastic_mode to set its *own* quiet param
    all_quota_forecasts = get_quota_forecasts(stochastic_mode=stochastic_mode)
    
    # --- 2. OFFLINE PHASE: Run Master Allocation (Quota vs Quota) ---
    master_allocations = {}
    if not quiet_mode:
        print("\n--- RUNNING MASTER ALLOCATION ENGINE (Quota vs. Quota) ---")
    for tc in config.TRAVEL_CLASSES:
        master_allocations[tc] = partition_capacity_by_quota(
            all_quota_forecasts[tc],
            config.CAPACITY[tc],
            tc, # <-- (NEW) Pass travel class for policy constraints
            quiet_mode=quiet_mode # <-- (NEW) Pass quiet_mode
        )
    if not quiet_mode:
        print(f"\n--- MASTER ALLOCATIONS COMPLETE: {master_allocations} ---")
    
    # --- 3. (NEW) OFFLINE PHASE: Run Inner Allocation (Bucket vs Bucket) ---
    final_bucket_allocations = {}
    if not quiet_mode:
        print("\n--- RUNNING INNER ALLOCATION ENGINE (Bucket vs. Bucket) ---")
    for tc in config.TRAVEL_CLASSES:
        final_bucket_allocations[tc] = {}
        for q_code, q_config in config.QUOTA_CONFIG.items():
            
            quota_total_allocation = master_allocations[tc].get(f"{q_code}_Allocation", 0)
            if quota_total_allocation == 0:
                continue # No seats allocated to this quota

            forecast_data = all_quota_forecasts[tc][q_code]
            
            if q_config['type'] == 'FLEXI':
                inner_alloc = partition_quota_into_buckets(
                    forecast_data['independent_bucket_demands'],
                    forecast_data['prices'],
                    quota_total_allocation,
                    q_code,
                    quiet_mode=quiet_mode # <-- (NEW) Pass quiet_mode
                )
                final_bucket_allocations[tc].update(inner_alloc)
            
            elif q_config['type'] == 'FLAT':
                final_bucket_allocations[tc][f"{q_code}_Bucket_0_Allocation"] = quota_total_allocation
    
    # --- THIS WAS THE BUGGY LINE ---
    if not quiet_mode:
    # --- END OF BUG FIX ---
        print(f"\n--- FINAL BUCKET ALLOCATIONS COMPLETE: {final_bucket_allocations} ---")

    
    # --- 4. ONLINE PHASE: Initialize Simulation ---
    if not quiet_mode:
        print(f"\n--- RUNNING *DYNAMIC* ONLINE SIMULATION ({config.BOOKING_WINDOW_DAYS} Days) ---")
    
    total_revenue = 0
    seats_sold = {}
    bookings_accepted = {}
    bookings_rejected = {}
    
    for tc in config.TRAVEL_CLASSES:
        bookings_rejected[tc] = {}
        seats_sold[tc] = {} 
        bookings_accepted[tc] = {} 
        
    # --- 5. Main Simulation Loop (Day 120 down to Day 1) ---
    for day in range(config.BOOKING_WINDOW_DAYS, 0, -1):
        if not quiet_mode:
            print(f"\n================ DAY {day} (Booking Window Open) ================")
        
        for tc in config.TRAVEL_CLASSES:
            class_bucket_allocs = final_bucket_allocations[tc]
            
            for q_code, q_config in config.QUOTA_CONFIG.items():
                
                if day > q_config['booking_window_open']:
                    continue 

                daily_arrivals = 0
                total_demand = all_quota_forecasts[tc][q_code]['total_demand']
                
                # --- (UPDATED) QUOTA-SPECIFIC BOOKING CURVE LOGIC ---
                
                if q_code == 'GN':
                    # Use the main booking curve
                    percent_sold_today = GENERAL_PICKUP_CURVE.get(day, 1.0)
                    percent_sold_tmrw = GENERAL_PICKUP_CURVE.get(day - 1, 1.0)
                    percent_to_book_this_day = percent_sold_tmrw - percent_sold_today
                    avg_arrivals = total_demand * percent_to_book_this_day
                    daily_arrivals = np.random.poisson(avg_arrivals)

                elif q_code == 'LD':
                    # (NEW) Use the Ladies quota booking curve
                    percent_sold_today = LADIES_PICKUP_CURVE.get(day, 1.0)
                    percent_sold_tmrw = LADIES_PICKUP_CURVE.get(day - 1, 1.0)
                    percent_to_book_this_day = percent_sold_tmrw - percent_sold_today
                    avg_arrivals = total_demand * percent_to_book_this_day
                    daily_arrivals = np.random.poisson(avg_arrivals)
                
                elif q_code == 'TK':
                    # Tatkal demand arrives all at once
                    if day == q_config['booking_window_open']:
                        avg_arrivals = total_demand
                        daily_arrivals = np.random.poisson(avg_arrivals)
                
                # --- END OF UPDATED LOGIC ---
                
                if daily_arrivals == 0: continue
                
                if not quiet_mode:
                    print(f"  Simulating {daily_arrivals} arrivals for Class {tc}, Quota {q_code}...")
                _get_or_initialize_key(bookings_rejected[tc], q_code, 0)
                
                price_config = q_config['price_config'][tc]
                
                # --- Handle arrivals for this specific quota ---
                for _ in range(daily_arrivals):
                    sold_ticket = False
                    
                    if q_config['type'] == 'FLEXI':
                        for i, bucket_info in enumerate(price_config):
                            alloc_key = f"{q_code}_Bucket_{i}_Allocation"
                            bucket_limit = class_bucket_allocs.get(alloc_key, 0)
                            
                            sold_key = f"{q_code}_Bucket_{i}"
                            total_bucket_seats_sold = _get_or_initialize_key(seats_sold[tc], sold_key, 0)

                            if total_bucket_seats_sold < bucket_limit:
                                seats_sold[tc][sold_key] += 1
                                total_revenue += bucket_info['price']
                                _get_or_initialize_key(bookings_accepted[tc], sold_key, 0)
                                bookings_accepted[tc][sold_key] += 1
                                sold_ticket = True
                                break 
                    
                    elif q_config['type'] == 'FLAT':
                        alloc_key = f"{q_code}_Bucket_0_Allocation"
                        bucket_limit = class_bucket_allocs.get(alloc_key, 0)
                        
                        sold_key = f"{q_code}_Bucket_0"
                        total_bucket_seats_sold = _get_or_initialize_key(seats_sold[tc], sold_key, 0)

                        if total_bucket_seats_sold < bucket_limit:
                            seats_sold[tc][sold_key] += 1
                            total_revenue += price_config
                            _get_or_initialize_key(bookings_accepted[tc], sold_key, 0)
                            bookings_accepted[tc][sold_key] += 1
                            sold_ticket = True
                    
                    if not sold_ticket:
                        bookings_rejected[tc][q_code] += 1

    if not quiet_mode:
        print("\n================ SIMULATION COMPLETE ================")
        print(f"\nTotal Revenue (All Classes): ₹{total_revenue:,}")
        
        print("\n--- FINAL CLASS BREAKDOWN ---")
        for tc in config.TRAVEL_CLASSES:
            total_sold = sum(seats_sold[tc].values())
            print(f"\nClass: {tc}")
            print(f"  Seats Sold: {total_sold} / {config.CAPACITY[tc]}")
            print(f"  Master Allocation was: {master_allocations[tc]}")

            print("\n  Customer Segment Analysis (by Quota-Bucket):")
            for sold_key, num_accepted in sorted(bookings_accepted[tc].items()):
                if num_accepted > 0:
                    print(f"  {sold_key}: {num_accepted} accepted")
            
            print("\n  Total Rejected (by Quota):")
            for q_code, num_rejected in sorted(bookings_rejected[tc].items()):
                if num_rejected > 0:
                    print(f"  {q_code}: {num_rejected} rejected")
    
    # --- (NEW) Return the final revenue for Monte Carlo analysis ---
    return total_revenue