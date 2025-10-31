def should_accept_booking(customer_class, seats_sold, capacity, protection_level_urgent):
    
    # How many seats are physically left?
    seats_available = capacity - seats_sold

    if customer_class == "Urgent":
        # Class 1 (Highest Fare)
        # We only care if there is *any* seat left.
        if seats_available > 0:
            return True
        else:
            return False

    elif customer_class == "Leisure":
        # Class 2 (Lower Fare)
        # We must check if this booking would "eat into" the protected seats.
        # We accept only if the number of available seats is
        # strictly GREATER than the number we are protecting.
        
        if seats_available > protection_level_urgent:
            return True
        else:
            # Not enough non-protected seats left. REJECT.
            return False