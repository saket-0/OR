# FILE 6: booking_curve_model.py (FIXED)
# This file defines the booking pick-up curve logic.

from config import BOOKING_WINDOW_DAYS

def _generate_pickup_curve(window_days: int) -> dict:
    """
    (Internal) Simulates a non-linear pick-up curve for the General Quota.
    
    Returns:
        A dict where:
        - key = day (e.g., 120, 119, ... 1)
        - value = cumulative % of tickets *sold* by the *start* of that day.
    """
    curve = {}
    
    # The booking window is from day `window_days` down to day 1.
    gn_window_len = float(window_days) # e.g., 120 days
    
    for day in range(window_days, 0, -1):
        # This simulates a "square root" curve.
        # 'day' represents the number of days remaining in the window
        # (e.g., on Day 120, 120 days remain; on Day 1, 1 day remains)
        days_remaining_gn = day
        
        # We use (days_remaining_gn / gn_window_len) ** 0.5
        # This gives % of demand *remaining* to book.
        # So, 1.0 - this = % of demand *sold* so far.
        percent_remaining = (days_remaining_gn / gn_window_len) ** 0.5
        percent_sold = 1.0 - percent_remaining
        
        curve[day] = percent_sold

    # Add the opening day (Day 120)
    # At the start of Day 120, 0% of tickets are sold.
    curve[window_days] = 0.0 
    
    return curve

# --- Initialize the pick-up curve globally ---
# This is pre-calculated once when the module is imported.
PICKUP_CURVE = _generate_pickup_curve(BOOKING_WINDOW_DAYS)