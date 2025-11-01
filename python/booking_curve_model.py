# FILE 6: booking_curve_model.py (FIXED & UPDATED)
# This file defines the booking pick-up curve logic for different quotas.

import numpy as np
from config import BOOKING_WINDOW_DAYS

def _generate_general_pickup_curve(window_days: int) -> dict:
    """
    (Internal) Simulates a non-linear "square root" pick-up curve
    for the General Quota (GN).
    
    Returns:
        A dict where:
        - key = day (e.g., 120, 119, ... 1)
        - value = cumulative % of tickets *sold* by the *start* of that day.
    """

    curve = {}
    gn_window_len = float(window_days)
    
    for day in range(window_days, 0, -1):
        days_remaining_gn = day
        percent_remaining = (days_remaining_gn / gn_window_len) ** 0.5
        percent_sold = 1.0 - percent_remaining
        curve[day] = percent_sold

    curve[window_days] = 0.0 
    return curve

def _generate_ladies_pickup_curve(window_days: int) -> dict:
    """
    Simulates a "bimodal" (U-shaped) pick-up curve
    for the Ladies Quota (LD).
    
    Assumes:
    - 50% of demand books in the first 30 days (Days 120-91)
    - 50% of demand books in the last 15 days (Days 15-1)
    """
    curve = {}
    
    # Define booking periods
    EARLY_PERIOD_DAYS = 30  # Days 120 down to 91
    LATE_PERIOD_DAYS = 15   # Days 15 down to 1
    
    total_early_sold = 0.50
    total_late_sold = 0.50

    for day in range(window_days, 0, -1):
        percent_sold = 0.0
        
        if day > (window_days - EARLY_PERIOD_DAYS):
            # --- Early Period (e.g., Day 120 to 91) ---
            # Linear ramp-up during this period
            days_into_window = window_days - day
            percent_sold = (days_into_window / EARLY_PERIOD_DAYS) * total_early_sold
        
        elif day <= LATE_PERIOD_DAYS:
            # --- Late Period (e.g., Day 15 to 1) ---
            # We already sold 50% (total_early_sold)
            # Now, sell the remaining 50%
            days_remaining = day
            # We use (LATE_PERIOD_DAYS - days_remaining) to get days *into* the late period
            days_into_late_period = LATE_PERIOD_DAYS - days_remaining
            percent_sold_in_late_period = (days_into_late_period / LATE_PERIOD_DAYS) * total_late_sold
            percent_sold = total_early_sold + percent_sold_in_late_period
        
        else:
            # --- Middle Period (e.g., Day 90 to 16) ---
            # No new bookings, hold at 50%
            percent_sold = total_early_sold

        curve[day] = percent_sold

    # At the start of Day 120, 0% are sold.
    curve[window_days] = 0.0
    
    # At the start of Day 0 (end of Day 1), 100% are sold.
    curve[0] = 1.0 
    
    return curve

# --- Initialize the pick-up curves globally ---
GENERAL_PICKUP_CURVE = _generate_general_pickup_curve(BOOKING_WINDOW_DAYS)
LADIES_PICKUP_CURVE = _generate_ladies_pickup_curve(BOOKING_WINDOW_DAYS)