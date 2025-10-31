# FILE 6: booking_curve_model.py (NEW)
# This file defines the booking pick-up curve logic.

from config import BOOKING_WINDOW_DAYS

def _generate_pickup_curve(window_days: int) -> dict:
    """
    (Internal) Simulates a non-linear pick-up curve for the General Quota.
    
    Returns:
        A dict where:
        - key = day (e.g., 120, 119, ... 2)
        - value = cumulative % of tickets *sold* by that day.
    """
    curve = {}
    # The General Quota window is from day `window_days` down to day 2.
    # Day 1 is TQ only.
    gn_window_len = float(window_days - 1) # e.g., 119 days
    
    for day in range(window_days, 0, -1):
        if day == 1:
            # By Day 1 (TQ window), 100% of GN bookings are complete.
            curve[day] = 1.0 
            continue
            
        # This simulates a "square root" curve.
        days_remaining_gn = day - 1
        
        # We use (days_remaining_gn / gn_window_len) ** 0.5
        # This gives % of demand *remaining*.
        # So, 1.0 - this = % of demand *sold*.
        percent_remaining = (days_remaining_gn / gn_window_len) ** 0.5
        percent_sold = 1.0 - percent_remaining
        
        curve[day] = percent_sold

    # Add the opening day
    curve[window_days] = 0.0 # 0% sold when window opens
    return curve

# --- Initialize the pick-up curve globally ---
# This is pre-calculated once when the module is imported.
PICKUP_CURVE = _generate_pickup_curve(BOOKING_WINDOW_DAYS)