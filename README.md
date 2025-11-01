# Advanced Railway Revenue Management System

This project is an advanced simulation of an end-to-end Revenue Management (RM) system for a railway, built with Python, Operations Research (OR) principles, and an interactive Streamlit frontend.

The system moves beyond a simple "first-come, first-served" model. It uses historical data, demand forecasting, and Linear Programming (LP) to create an optimal seat allocation plan that maximizes revenue. The final model is then stress-tested using a Monte Carlo simulation and presented in an interactive dashboard.

## Key Features

  * **Multi-Quota Demand Modeling:** Simulates distinct customer segments (e.g., General 'GN', Tatkal 'TK', and Ladies 'LD') with different booking behaviors and price sensitivities.
  * **Two-Step LP Optimization:** Uses a two-stage Linear Programming model to first allocate seats *between* quotas (Master LP) and then *within* each quota's price buckets (Inner LP).
  * **Demand Unconstraining:** Employs a refined heuristic to estimate true, unconstrained demand from censored historical sales data (i.e., sales that were "capped" by capacity).
  * **Quota-Specific Booking Curves:** Models different arrival patterns. For example, 'GN' quota demand follows a standard "square root" curve, while 'LD' quota follows a bimodal "U-shaped" curve (early and late bookings).
  * **Policy Constraints:** The optimization model includes real-world business rules, such as guaranteeing a minimum number of seats for the 'LD' quota, even if it is not revenue-optimal.
  * **Monte Carlo Robustness Testing:** The main application runs the entire simulation 100+ times, sampling from a stochastic demand forecast to test the robustness of the static plan.
  * **Interactive Web Dashboard:** A Streamlit-based frontend (`app.py`) provides a user-friendly interface to run the simulation and visualize the results, including key metrics and a revenue distribution histogram.

## How it Works: The Model Logic

The system is split into two phases: an "Offline" planning phase and an "Online" simulation phase.

### Phase 1: Offline Planning & Optimization

Before the booking window opens, the system runs a multi-step process to create its master allocation plan.

1.  **Unconstrain Data:** The system analyzes `DETAILED_HISTORICAL_DATA`. For any train that sold out, `unconstraining.py` estimates what the *true* demand might have been.
2.  **Calculate Factors:** `factor_calculator.py` uses this unconstrained data to find demand multipliers (e.g., `factor_holiday = 1.45`, `factor_weekend = 1.12`).
3.  **Forecast Demand:** `engine.py` generates a total market forecast for *each* quota, applying the relevant factors. `forecasting.py` then translates this total demand into price-elastic demand for 'FLEXI' quotas and flat demand for 'FLAT' quotas.
4.  **Run Master LP:** `allocation_engine.py` runs the "Master" LP. It decides how to partition the total train capacity (e.g., 110 3AC seats) between the competing quotas (GN, TK, LD) based on their total forecasted demand and average revenue-per-seat.
5.  **Run Inner LPs:** The system then runs an "Inner" LP for each 'FLEXI' quota. For example, if 'GN' was given 80 seats by the Master LP, this step partitions those 80 seats optimally among its own price buckets.

### Phase 2: Online Simulation

The system simulates the 120-day booking window.

1.  `simulation.py` loops from Day 120 down to Day 1.
2.  On each day, it simulates customer arrivals for each quota. The number of arrivals is determined by the quota's specific booking curve (e.g., `GENERAL_PICKUP_CURVE` or `LADIES_PICKUP_CURVE`).
3.  When a customer "arrives," the system attempts to sell them a ticket based on the static allocation plan from Phase 1.
4.  If a bucket is full, the 'FLEXI' quota customer is "spilled" up to the next available, more expensive bucket. If all buckets for that quota are full, the booking is rejected.
5.  This continues until Day 0, and the final revenue is calculated.

## How to Run the Web Application

This project is run through an interactive Streamlit web application.

### 1\. Install Dependencies

You will need the `numpy`, `pulp`, `streamlit`, and `matplotlib` libraries. They are listed in `requirements.txt`.

```bash
# Navigate to the project folder (OR/)
pip install -r requirements.txt
```

### 2\. Run the Streamlit App

The main entry point is `app.py`.

```bash
# From the OR/ folder
streamlit run app.py
```

This command will start the web server and open the application in your default web browser.

### 3\. Run the Simulation

Once the app is open in your browser:

1.  Click the **"🚀 Run Full Monte Carlo Simulation"** button.
2.  Wait for the simulation to complete (it may take 20-30 seconds).
3.  The app will update to show the full analysis.

## Interpreting the Dashboard

The application will present the results in three main sections:

1.  **Summary Metrics:** A set of cards on the left showing:

      * **Baseline (Deterministic) Revenue:** The revenue from a single, "perfect world" run.
      * **Average (Mean) Revenue:** The more realistic expected revenue from all 100 stochastic runs.
      * **Standard Deviation:** Measures the volatility/risk.
      * **Min/Max Revenue:** The "worst-case" and "best-case" scenarios from the simulation.

2.  **Revenue Distribution (Histogram):** A bar chart on the right showing the frequency of different revenue outcomes. This helps visualize the risk.

      * The **green line** shows the *Mean Revenue*.
      * The **red dashed line** shows the *Baseline Revenue*.

3.  **Detailed Log:** An expandable section at the bottom that contains the full, detailed terminal output from the *Baseline (Deterministic)* run, allowing you to audit the system's decisions (e.g., why some customers were rejected).

## Module Breakdown

  * `app.py`: The main Streamlit web application frontend. Handles the UI and user interaction.
  * `python/main.py`: The main backend entry point, *called by app.py*. Orchestrates the Monte Carlo simulation and returns the final analysis.
  * `python/config.py`: Contains all static configuration: train capacity, quota definitions, price structures, and historical data.
  * `python/simulation.py`: The "Online" module. Runs the 120-day dynamic simulation of the booking window.
  * `python/engine.py`: The main "Offline" module. Orchestrates the forecasting process for all quotas.
  * `python/allocation_engine.py`: Solves the two-step (Master and Inner) Linear Programming problems to create the optimal allocation plan.
  * `python/forecasting.py`: Contains the logic to model price-elastic demand (for 'FLEXI' quotas) and flat-price demand (for 'FLAT' quotas).
  * `python/factor_calculator.py`: Uses historical data to calculate demand multipliers for holidays and weekends.
  * `python/unconstraining.py`: Estimates true, unconstrained demand from "sold-out" (censored) historical sales data.
  * `python/booking_curve_model.py`: Defines the different customer arrival patterns (pickup curves) for different quotas.
  * `requirements.txt`: A list of all Python dependencies.