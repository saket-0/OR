# FILE 5: config.py (NEW)
# This file contains all static configuration and system parameters
# for the Revenue Management engine.

# --- System Parameters ---
TRAVEL_CLASSES = ['1AC', '2AC', '3AC']
BOOKING_WINDOW_DAYS = 120 

# --- Capacity and Price Data ---
CAPACITY = {'1AC': 30, '2AC': 60, '3AC': 110}

PRICES = {
    '1AC': {'general': 7000, 'tatkal': 8500},
    '2AC': {'general': 3000, 'tatkal': 4000},
    '3AC': {'general': 1800, 'tatkal': 2500}
}

# --- Causal Factors for New Train ---
EXTERNAL_FACTORS = {'is_holiday': True, 'day_of_week': 'Fri'}

# --- Historical Data Store ---
# In a real system, this would be loaded from a database.
DETAILED_HISTORICAL_DATA = {
    '1AC': [
        {'train_id': 1, 'total_sold': 28, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 2,  'days_early': 1,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 25, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 30, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
    ],
    '2AC': [
        {'train_id': 1, 'total_sold': 55, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 5,  'days_early': 1,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 58, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 2,  'days_early': 1,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'TQ'},
        {'train_id': 3, 'total_sold': 55, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 50, 'days_early': 10, 'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 10, 'days_early': 1,  'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TQ'},
    ],
    '3AC': [
        {'train_id': 1, 'total_sold': 100, 'days_early': 5, 'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 1, 'total_sold': 10,  'days_early': 1, 'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TQ'},
        {'train_id': 2, 'total_sold': 100, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 95,  'days_early': 0, 'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 90,  'days_early': 10,'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 20,  'days_early': 1, 'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TQ'},
        {'train_id': 5, 'total_sold': 105, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Tue', 'quota': 'GN'},
        {'train_id': 6, 'total_sold': 108, 'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 6, 'total_sold': 2,   'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'TQ'},
    ]
}