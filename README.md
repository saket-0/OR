## Modules

1.  **`unconstraining.py`**: Estimates true demand from censored historical sales data.
2.  **`forecasting.py`**: Forecasts demand for "Urgent" and "Leisure" customer classes based on unconstrained data and external factors.
3.  **`optimization.py`**: Uses Linear Programming (LP) to calculate the optimal "bid price" (opportunity cost) of a single seat.
4.  **`main_engine.py`**: The main controller.
    * **Offline:** Runs modules 1-3 to get the bid price.
    * **Online:** Runs a 30-day simulation of the booking window, using the bid price as the "gatekeeper" to accept or reject new booking requests.

## How to Run

1.  **Install dependencies:**
    ```bash
    pip install numpy scipy
    ```
    (Or `pip install -r requirements.txt`)

2.  **Run the engine:**
    ```bash
    python main_engine.py
    ```

## Example Output

When you run `main_engine.py`, it will first run the offline model and then the online simulation. The output will look like this: