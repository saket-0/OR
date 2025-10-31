Here is a comprehensive README file for your project, reflecting all the advanced features you have implemented.

-----

# Advanced Railway Revenue Management System

This project is an advanced simulation of an end-to-end Revenue Management (RM) system for a railway, built with Python and Operations Research (OR) principles.

The system moves beyond a simple "first-come, first-served" model. It uses historical data, demand forecasting, and Linear Programming (LP) to create an optimal seat allocation plan that maximizes revenue. The final model is then stress-tested using a Monte Carlo simulation to evaluate its performance under real-world uncertainty.

## Key Features

  * **Multi-Quota Demand Modeling:** Simulates distinct customer segments (e.g., General 'GN', Tatkal 'TK', and Ladies 'LD') with different booking behaviors and price sensitivities.
  * **Two-Step LP Optimization:** Uses a two-stage Linear Programming model to first allocate seats *between* quotas (Master LP) and then *within* each quota's price buckets (Inner LP).
  * **Demand Unconstraining:** Employs a refined heuristic to estimate true, unconstrained demand from censored historical sales data (i.e., sales that were "capped" by capacity).
  * **Quota-Specific Booking Curves:** Models different arrival patterns. For example, 'GN' quota demand follows a standard "square root" curve, while 'LD' quota follows a bimodal "U-shaped" curve (early and late bookings).
  * **Policy Constraints:** The optimization model includes real-world business rules, such as guaranteeing a minimum number of seats for the 'LD' quota, even if it is not revenue-optimal.
  * **Monte Carlo Robustness Testing:** The main application runs the entire simulation 100+ times, sampling from a stochastic demand forecast to test the robustness of the static plan. This provides an average revenue, worst-case, and best-case scenario.

## How it Works: The Model Logic

The system is split into two phases: an "Offline" planning phase and an "Online" simulation phase.

### Phase 1: Offline Planning & Optimization

Before the booking window opens, the system runs a multi-step process to create its master allocation plan.

1.  **Unconstrain Data:** The system analyzes `DETAILED_HISTORICAL_DATA`. For any train that sold out, `unconstraining.py` estimates what the *true* demand might have been.
2.  **Calculate Factors:** `factor_calculator.py` uses this unconstrained data to find demand multipliers (e.g., `factor_holiday = 1.45`, `factor_weekend = 1.12`).
3.  **Forecast Demand:** `engine.py` generates a total market forecast for *each* quota, applying the relevant factors. `forecasting.py` then translates this total demand into price-elastic demand for 'FLEXI' quotas and flat demand for 'FLAT' quotas.
4.  **Run Master LP:** `allocation_engine.py` runs the "Master" LP. It decides how to partition the total train capacity (e.g., 110 3AC seats) between the competing quotas (GN, TK, LD) based on their total forecasted demand and average revenue-per-seat.
5.  **Run Inner LPs:** The system then runs an "Inner" LP for each 'FLEXI' quota. For example, if 'GN' was given 80 seats by the Master LP, this step partitions those 80 seats optimally among its own price buckets (e.g., 10 for Bucket 1, 15 for Bucket 2, etc.).

### Phase 2: Online Simulation

The system simulates the 120-day booking window.

1.  `simulation.py` loops from Day 120 down to Day 1.
2.  On each day, it simulates customer arrivals for each quota. The number of arrivals is determined by the quota's specific booking curve (e.g., `GENERAL_PICKUP_CURVE` or `LADIES_PICKUP_CURVE`).
3.  When a customer "arrives," the system attempts to sell them a ticket based on the static allocation plan from Phase 1.
4.  If a bucket is full, the 'FLEXI' quota customer is "spilled" up to the next available, more expensive bucket. If all buckets for that quota are full, the booking is rejected.
5.  This continues until Day 0, and the final revenue is calculated.

## How to Run the Project

This project includes a Monte Carlo runner that analyzes the model's robustness.

### 1\. Install Dependencies

You will need the `numpy` and `pulp` libraries. They are listed in `requirements.txt`.

```bash
# Navigate to the project folder
pip install -r requirements.txt
```

### 2\. Run the Simulation

The main entry point is `main.py`. This script will first run the simulation *once* in deterministic mode (printing all logs) and then run it 99 more times in stochastic "quiet" mode to build the final analysis.

```bash
python python/main.py
```

### 3\. Interpreting the Output

The final output will look something like this:

```
--- RUN 1: DETERMINISTIC (Baseline) ---
(Detailed simulation log for the single deterministic run)
...
--- DETERMINISTIC Baseline Revenue: ₹705,240 ---

--- RUNNING 99 STOCHASTIC SIMULATIONS ---
  Simulation 99/99 complete. Revenue: ₹620,000

--- MONTE CARLO ANALYSIS COMPLETE ---

Baseline (Deterministic) Revenue: ₹705,240.00
Average (Mean) Revenue:         ₹662,052.60
Standard Deviation:             ₹33,421.78
Min Revenue (Worst Case):       ₹554,580.00
Max Revenue (Best Case):        ₹724,440.00
```

  * **Baseline (Deterministic) Revenue:** The revenue from the single, "perfect world" plan where forecasts are assumed to be 100% accurate.
  * **Average (Mean) Revenue:** The average revenue from the 99 stochastic runs. This is the **more realistic** expected revenue, as it accounts for real-world demand uncertainty.
  * **Standard Deviation:** Measures the volatility of the revenue. A high number means the plan is high-risk.
  * **Min/Max Revenue:** The 5th and 95th percentile (or absolute min/max) showing the "worst-case" and "best-case" scenarios.

## Module Breakdown

  * `main.py`: Main entry point. Runs the Monte Carlo simulation and prints the final analysis.
  * `config.py`: Contains all static configuration: train capacity, quota definitions, price structures, and historical data.
  * `simulation.py`: The "Online" module. Runs the 120-day dynamic simulation of the booking window.
  * `engine.py`: The main "Offline" module. Orchestrates the forecasting process for all quotas.
  * `allocation_engine.py`: Solves the two-step (Master and Inner) Linear Programming problems to create the optimal allocation plan.
  * `forecasting.py`: Contains the logic to model price-elastic demand (for 'FLEXI' quotas) and flat-price demand (for 'FLAT' quotas).
  * `factor_calculator.py`: Uses historical data to calculate demand multipliers for holidays and weekends.
  * `unconstraining.py`: Estimates true, unconstrained demand from "sold-out" (censored) historical sales data.
  * `booking_curve_model.py`: Defines the different customer arrival patterns (pickup curves) for different quotas.
  * `requirements.txt`: A list of all Python dependencies (e.g., `pulp`, `numpy`).