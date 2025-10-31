# FILE 5: config.py (UPDATED for Flexi-Fare)
# This file contains all static configuration and system parameters
# for the Revenue Management engine.

# --- System Parameters ---
TRAVEL_CLASSES = ['1AC', '2AC', '3AC']
BOOKING_WINDOW_DAYS = 120 

# --- Capacity Data ---
CAPACITY = {'1AC': 30, '2AC': 60, '3AC': 110}

# --- NEW: Flexi-Fare Price Structure ---
# Defines the price buckets for the General quota.
# Prices are absolute (can be derived from a base + multiplier).
FLEXI_FARE_STRUCTURE = {
    '1AC': [
        {'name': 'Bucket_1 (1.0x)', 'price': 7000},
        {'name': 'Bucket_2 (1.1x)', 'price': 7700},
        {'name': 'Bucket_3 (1.2x)', 'price': 8400},
    ],
    '2AC': [
        {'name': 'Bucket_1 (1.0x)', 'price': 3000},
        {'name': 'Bucket_2 (1.1x)', 'price': 3300},
        {'name': 'Bucket_3 (1.2x)', 'price': 3600},
        {'name': 'Bucket_4 (1.3x)', 'price': 3900},
    ],
    '3AC': [
        {'name': 'Bucket_1 (1.0x)', 'price': 1800},
        {'name': 'Bucket_2 (1.1x)', 'price': 1980},
        {'name': 'Bucket_3 (1.2x)', 'price': 2160},
        {'name': 'Bucket_4 (1.3x)', 'price': 2340},
        {'name': 'Bucket_5 (1.4x)', 'price': 2500}, # Capped price
    ]
}

# --- Causal Factors for New Train ---
EXTERNAL_FACTORS = {'is_holiday': True, 'day_of_week': 'Fri'}

# --- Historical Data Store ---
# (Simplified: In this model, we are only forecasting/pricing the General Quota)
DETAILED_HISTORICAL_DATA = {
    '1AC': [
        {'train_id': 1, 'total_sold': 28, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 25, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 30, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
    ],
    '2AC': [
        {'train_id': 1, 'total_sold': 55, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 58, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 55, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 50, 'days_early': 10, 'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
    ],
    '3AC': [
        {'train_id': 1, 'total_sold': 100, 'days_early': 5, 'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 100, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 95,  'days_early': 0, 'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 90,  'days_early': 10,'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'GN'},
        {'train_id': 5, 'total_sold': 105, 'days_early': 0, 'is_holiday': False, 'day_of_week': 'Tue', 'quota': 'GN'},
        {'train_id': 6, 'total_sold': 108, 'days_early': 1, 'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
    ]
}