# FILE 5: config.py (UPDATED for Multi-Quota Logic)
# This file contains all static configuration and system parameters
# for the Revenue Management engine.

# --- System Parameters ---
TRAVEL_CLASSES = ['1AC', '2AC', '3AC']
BOOKING_WINDOW_DAYS = 120 

# --- Capacity Data ---
CAPACITY = {'1AC': 30, '2AC': 60, '3AC': 110}

# --- 1. Flexi-Fare Price Structure (for 'GN' Quota) ---
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
        {'name': 'Bucket_5 (1.4x)', 'price': 2500}, # Capped price for 3AC
    ]
}

# --- 2. (NEW) Quota Configuration ---
# Defines all quotas, their price model, and booking window.
QUOTA_CONFIG = {
    'GN': {
        'type': 'FLEXI',
        'price_config': FLEXI_FARE_STRUCTURE, # Links to the structure above
        'booking_window_open': 120 # Opens 120 days out
    },
    'TK': {
        'type': 'FLAT',
        'price_config': {'1AC': 8500, '2AC': 4000, '3AC': 2600}, # Fixed Tatkal prices
        'booking_window_open': 1 # Opens 1 day before departure
    },
    'LD': {
        'type': 'FLAT',
        'price_config': {'1AC': 7000, '2AC': 3000, '3AC': 1800}, # Fixed "Ladies" prices (at base rate)
        'booking_window_open': 120 # Opens 120 days out
    }
    # Add other quotas like 'PT' (Premium Tatkal) here,
    # which would be a 'FLEXI' type but with a different booking window and price list.
}


# --- Causal Factors for New Train ---
EXTERNAL_FACTORS = {'is_holiday': True, 'day_of_week': 'Fri'}

# --- (UPDATED) Historical Data Store ---
# Now includes data for 'TK' (Tatkal) and 'LD' (Ladies) quotas
DETAILED_HISTORICAL_DATA = {
    '1AC': [
        {'train_id': 1, 'total_sold': 20, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 18, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 22, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 5,  'days_early': 1,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'TK'},
        {'train_id': 5, 'total_sold': 2,  'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'LD'},
    ],
    '2AC': [
        {'train_id': 1, 'total_sold': 40, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 35, 'days_early': 2,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 30, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 10, 'days_early': 1,  'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TK'},
        {'train_id': 5, 'total_sold': 8,  'days_early': 1,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'TK'},
        {'train_id': 6, 'total_sold': 5,  'days_early': 10, 'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'LD'},
    ],
    '3AC': [
        {'train_id': 1, 'total_sold': 80, 'days_early': 5,  'is_holiday': True,  'day_of_week': 'Fri', 'quota': 'GN'},
        {'train_id': 2, 'total_sold': 70, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Wed', 'quota': 'GN'},
        {'train_id': 3, 'total_sold': 65, 'days_early': 0,  'is_holiday': False, 'day_of_week': 'Mon', 'quota': 'GN'},
        {'train_id': 4, 'total_sold': 20, 'days_early': 1,  'is_holiday': True,  'day_of_week': 'Sun', 'quota': 'TK'},
        {'train_id': 5, 'total_sold': 15, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Tue', 'quota': 'TK'},
        {'train_id': 6, 'total_sold': 10, 'days_early': 1,  'is_holiday': False, 'day_of_week': 'Fri', 'quota': 'LD'},
    ]
}