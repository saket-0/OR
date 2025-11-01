# This is your new frontend file: OR/app.py

import streamlit as st
import matplotlib.pyplot as plt
import sys
import os

# Add the 'python' subdirectory to the system path
# This allows the app to import your backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

# Now we can import the modified main.py
try:
    from main import run_analysis
except ImportError as e:
    st.error(f"Error importing backend: {e}\n"
             "Make sure app.py is in the 'OR' folder, "
             "and your modules are in 'OR/python/'.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(
    page_title="Railway Revenue Management Simulation",
    page_icon="🚂",
    layout="wide"
)

st.title("🚂 Advanced Railway Revenue Management")
st.markdown("Monte Carlo Simulation & Optimization Engine")

# --- Initialize Session State ---
# This holds variables so they don't reset
if 'results' not in st.session_state:
    st.session_state.results = None
if 'running' not in st.session_state:
    st.session_state.running = False

# --- Main App Logic ---
if st.button("🚀 Run Full Monte Carlo Simulation", 
             disabled=st.session_state.running):
    
    st.session_state.running = True
    st.session_state.results = None
    
    # Create a progress bar and a status text element
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    final_results = None
    
    # Use st.spinner to show a global "running" message
    with st.spinner("Initializing Simulation... This may take a minute."):
        
        # Call the generator function from main.py
        n_sims = 1 # Start at 1
        for i, status in enumerate(run_analysis()):
            
            # Check if it's the final results dictionary
            if isinstance(status, dict):
                final_results = status
                n_sims = final_results.get('n_simulations', 100)
                break
            
            # Update progress
            status_text.text(status)
            # Estimate progress
            progress = (i + 1) / (3 + (100 // 10)) # 3 setup steps + 10 progress updates
            progress_bar.progress(min(1.0, progress))

    st.session_state.running = False
    progress_bar.progress(1.0)
    status_text.success("✅ Analysis Complete!")
    st.session_state.results = final_results

# --- Display Results ---
if st.session_state.results:
    st.balloons()
    
    results = st.session_state.results
    n_sims = results['n_simulations']
    
    st.header(f"Monte Carlo Analysis ({n_sims} Runs)")
    st.markdown("---")

    # --- 1. Key Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Baseline (Deterministic) Revenue", 
                f"₹{results['baseline_revenue']:,.2f}",
                help="Revenue from a single run assuming perfect forecasts.")
    
    col2.metric("Average (Mean) Revenue", 
                f"₹{results['mean_revenue']:,.2f}",
                help="The most realistic expected revenue from all stochastic runs.")
    
    col3.metric("Standard Deviation", 
                f"₹{results['std_dev']:,.2f}",
                help="Measures the volatility/risk. Higher is riskier.")
    
    col4, col5 = st.columns(2)
    col4.metric("Min Revenue (Worst Case)", 
                f"₹{results['min_revenue']:,.2f}")
    col5.metric("Max Revenue (Best Case)", 
                f"₹{results['max_revenue']:,.2f}")

    # --- 2. Revenue Distribution Chart ---
    st.subheader("Revenue Distribution (Histogram)")
    
    # Create a histogram using Matplotlib
    fig, ax = plt.subplots()
    ax.hist(results['all_revenues'], bins=30, edgecolor='black', alpha=0.7)
    
    # Add vertical lines for key metrics
    ax.axvline(results['baseline_revenue'], color='red', linestyle='--', linewidth=2, 
                label=f'Baseline (₹{results["baseline_revenue"]:,.0f})')
    ax.axvline(results['mean_revenue'], color='green', linestyle='-', linewidth=2, 
                label=f'Mean (₹{results["mean_revenue"]:,.0f})')
    
    ax.set_title(f'Distribution of Revenue over {n_sims} Simulations')
    ax.set_xlabel('Total Revenue (₹)')
    ax.set_ylabel('Frequency')
    ax.legend()
    
    # Display the chart in Streamlit
    st.pyplot(fig)
    
    # --- 3. Detailed Log from Baseline Run ---
    st.subheader("Detailed Log (from Deterministic Baseline Run)")
    with st.expander("Click to view the full simulation log"):
        # Display the captured print output in a code block
        st.code(results['deterministic_log'], language='text')

elif not st.session_state.running:
    st.info("Click the 'Run' button to start the analysis. This will take a moment.")