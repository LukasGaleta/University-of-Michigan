import yfinance as yf

import streamlit as st
import pandas as pd
import numpy as np
import datetime

import matplotlib.pyplot as plt
import seaborn as sns

#-----------------------------------------------------------------------------------------------------------------------



def Create_trajectory(monthly_data, monhly_invest):
  avg_ret = pd.DataFrame()
  avg_ret['avg_ret'] = monthly_data2['avg_ret'].sample(n=240, replace=True)+1
  avg_ret['avg_ret_cumprod'] = avg_ret['avg_ret'].cumprod()-1

  avg_ret['invested'] = monhly_invest
  avg_ret['invested'] = avg_ret['invested'].cumsum()

  avg_ret['stock_value'] = 100 * (avg_ret['avg_ret_cumprod']+1)

  avg_ret['stock_vol_bought'] = monhly_invest/avg_ret['stock_value']

  avg_ret['stock_tot'] = avg_ret['stock_vol_bought'].cumsum()


  avg_ret['portfolio_value'] = avg_ret['stock_value'] * avg_ret['stock_tot']


  return avg_ret


#-----------------------------------------------------------------------------------------------------------------------

# Title of the app
st.title("Portfolio Value Estimation")
st.write("""
**SI 106 Project** 

**Lukas Galeta** 

The motivation behind this project is to develop a simple tool that can estimate potential past returns based on monthly investments from a specific date in selected assets.

More importantly, this project aims to fill the gap in tools available for estimating long-term savings, specifically projecting future portfolio values over a 20-year horizon. By leveraging the power of Monte Carlo simulations, it offers a comprehensive approach to forecasting portfolio growth, addressing the current lack of such tools in the market.
""")
#-----------------------------------------------------------------------------------------------------------------------
# Sidebar inputs
st.sidebar.header("How much do you invest monthly?")
monthly_invest = st.sidebar.slider("Amont in USD", min_value=10, max_value=500, value=100)

#-----------------------------------------------------------------------------------------------------------------------
#Start date of simulation
start_date = st.sidebar.date_input(
    "When did you start?",
    value=datetime.date(2024, 1, 1),  # Default value is today's date
    min_value=datetime.date(2015, 1, 1),  # Minimum selectable date
    max_value=datetime.date(2024, 12, 2)  # Maximum selectable date
)

#-----------------------------------------------------------------------------------------------------------------------
#Tickers
ticker_mapping = {
    "S&P 500 (SPY)": "SPY",
    "JPMorgan Chase (JPM)": "JPM",
    "Exxon Mobil (XOM)": "XOM",
    "iShares 20+ Year Treasury Bond ETF (TLT)": "TLT",
    "Apple (AAPL)": "AAPL",
    "Google (GOOG)": "GOOG",
    "Microsoft (MSFT)": "MSFT",
    "Amazon (AMZN)": "AMZN",
    "Tesla (TSLA)": "TSLA",
    "Meta Platforms (META)": "META",
    "Berkshire Hathaway (BRK.B)": "BRK-B",
    "NVIDIA (NVDA)": "NVDA",
    "Johnson & Johnson (JNJ)": "JNJ",
    "Procter & Gamble (PG)": "PG",
    "Pfizer (PFE)": "PFE",
}

# Sidebar multiselect for company names
selected_companies = st.sidebar.multiselect(
    "Select 5 companies (stocks/ETFs):",
    options=list(ticker_mapping.keys()),
    default=["S&P 500 (SPY)", "JPMorgan Chase (JPM)", "Exxon Mobil (XOM)", "iShares 20+ Year Treasury Bond ETF (TLT)", "Apple (AAPL)"]
)

# Validate selection
if len(selected_companies) != 5:
    st.sidebar.error("Please select exactly 5 companies.")
else:
    # Map company names to tickers
    tickers = [ticker_mapping[company] for company in selected_companies]



#-----------------------------------------------------------------------------------------------------------------------

#3if 'message' not in st.session_state:
#    st.session_state.message = "Hello, Streamlit!"


if st.sidebar.button("Run Simulations"):

    data = yf.download(tickers, start=start_date, end="2024-12-31",  interval='1mo')

    data = data[["Close", "Adj Close"]]

    

    # monthly_data = data.resample('ME').last()


    monthly_data = data.copy()

  
    monthly_data.head(5)

    monthly_data['s0'] = monthly_invest / monthly_data['Adj Close'][tickers[0]] / 5
    monthly_data['s1'] = monthly_invest / monthly_data['Adj Close'][tickers[1]] / 5
    monthly_data['s2'] = monthly_invest / monthly_data['Adj Close'][tickers[2]] / 5
    monthly_data['s3'] = monthly_invest / monthly_data['Adj Close'][tickers[3]] / 5
    monthly_data['s4'] = monthly_invest / monthly_data['Adj Close'][tickers[4]] / 5

    monthly_data['s0'] = monthly_data['s0'].cumsum()
    monthly_data['s1'] = monthly_data['s1'].cumsum()
    monthly_data['s2'] = monthly_data['s2'].cumsum()
    monthly_data['s3'] = monthly_data['s3'].cumsum()
    monthly_data['s4'] = monthly_data['s4'].cumsum()

    monthly_data['portfolio_value'] = 0

    for x in range(5):
        monthly_data['portfolio_value'] = monthly_data['portfolio_value'] + monthly_data['s' + str(x)] * \
                                          monthly_data['Adj Close'][tickers[x]]

    monthly_data.head(5)

    monthly_data['invested'] = monthly_invest
    monthly_data['invested'] = monthly_data['invested'].cumsum()


# ----------------------------------------------------------------------------------------------------------------------


    # Plot Results
    st.subheader("Strategy Backtest")
    st.write("Backtesting is the process of testing a trading strategy or investment model using historical data to evaluate its performance and effectiveness. It allows traders and investors to assess how their strategies would have performed in the past before applying them in real-time markets.")

    fig, ax = plt.subplots(figsize=(12, 7))

    if not monthly_data['invested'].empty and not monthly_data['portfolio_value'].empty:
        # Plotting the data
        ax.plot(monthly_data.index, monthly_data['invested'], label='Invested Amount', color='blue', linestyle='--', linewidth=2)
        ax.plot(monthly_data.index, monthly_data['portfolio_value'], label='Portfolio Value', color='green', linestyle='-', linewidth=2)
        ax.fill_between(monthly_data.index, monthly_data['invested'], monthly_data['portfolio_value'], color='gray', alpha=0.2, label='Difference')
    else:
        st.write("Data is missing for invested or portfolio value.")

    # Labels and Title
    ax.set_title('Invested vs Portfolio Value Over Time', fontsize=14)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value (USD)', fontsize=12)
    ax.legend(fontsize=10, loc='upper left')

    # Adjusting ticks and grid
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.grid(True, which='both', linestyle='--', alpha=0.5)

    # Show plot in Streamlit
    st.pyplot(fig)


    st.write("""
    Blue line represents invested money. Green line represents portfolio value. Gray area is market gain. Strategy invests equal ammount of money in to each asset, It is simple, but effective.
    """)

# ----------------------------------------------------------------------------------------------------------------------
# MC SIMULATION

    # Download data from Yahoo Finance
    data2 = yf.download(tickers, start="2010-01-01", end="2024-12-31", interval='1mo')

    # Filter only 'Adj Close'
    data2 = data2[["Adj Close"]]

    # monthly_data2 = data2.resample('ME').last()
    monthly_data2 = data2.copy()
  
    # Calculate monthly returns
    monthly_data2pct = monthly_data2.pct_change()

    # Calculate average price and return
    monthly_data2['avg_price'] = monthly_data2.sum(axis=1) / len(tickers)
    monthly_data2['sum_ret'] = monthly_data2pct.sum(axis=1)
    monthly_data2['avg_ret'] = monthly_data2['sum_ret'] / len(tickers)
  
    monthly_data3 = monthly_data2.copy()


  


    st.subheader("Monte Carlo Simulation")

    st.write("""
    Monte Carlo simulation is a powerful tool for predicting portfolio outcomes. However, using biased stock selection can lead to unrealistic results. In this project, we simulate different portfolio paths by randomly sampling from historical portfolio returns.
    """)


# Histogram SIMULATION

    st.write("""
    Histograms below shows sampling distribution. Portfolio returns are skewed and portfolio value is rising.
    """)
    # Display the first few rows of the data in the app
    #st.write("### First 5 rows of the monthly data:", monthly_data2.head())

    # Create and show the histogram for average monthly returns
    plt.figure(figsize=(12, 6))

    plt.hist(
        monthly_data3['avg_ret'] * 100,  # Convert to percentage
        bins=20,
        edgecolor='black',
        color='skyblue',
        alpha=0.8
    )

    # Title and labels for the plot
    plt.title('Distribution of Average Monthly Returns', fontsize=14)
    plt.xlabel('Average Monthly Return (%)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)

    # Customize ticks and grid
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adjust layout
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(plt)


    






    st.write("""
    **Note 1**  
    A proper Monte Carlo simulation should sample from an estimated return distribution, not just past returns. This approach doesn't fully capture the randomness and variability of future market conditions.

    **Note 2**  
    This simulation uses only 100 trajectories, which is limited by speed and memory constraints. Ideally, a more accurate simulation would involve around 100,000 trajectories to better capture the range of potential outcomes.
    """)



#----------------------


    trajectories_list = []

    for x in range(100):
      simulation = Create_trajectory(monthly_data2, monthly_invest)
      trajectory = simulation.portfolio_value
      trajectory = trajectory.reset_index(drop=True)
      trajectories_list.append(trajectory)

    df_trajectories = pd.DataFrame(trajectories_list).T
    df_trajectories.columns = [f"Trajectory_{i + 1}" for i in range(df_trajectories.shape[1])]

    df_invested = df_trajectories.copy()
    df_invested['invested'] = monthly_invest
    df_invested['invested_cumsum'] = df_invested['invested'].cumsum()


    date_range = pd.date_range(start='2025-01-01', end='2044-12-31', freq='M')
    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 7))

    # Plotting each trajectory (gray dashed lines)
    for column in df_trajectories.columns:
        ax.plot(date_range, df_trajectories[column], color='gray', linestyle='--', alpha=0.3)

    # Plotting the average trajectory (red solid line)
    average_trajectory = df_trajectories.mean(axis=1)
    ax.plot(date_range, average_trajectory, label='Average Trajectory', color='red', linewidth=2)

    # Plotting the invested money (green line)
    ax.plot(date_range, df_invested['invested_cumsum'], label='Invested Money', color='green', linewidth=2)

    # Plotting the 95% confidence interval (blue shaded area)
    lower_bound = df_trajectories.quantile(0.025, axis=1)
    upper_bound = df_trajectories.quantile(0.975, axis=1)
    ax.fill_between(date_range, lower_bound, upper_bound, color='blue', alpha=0.2, label='95% Confidence Interval')

    # Adding title and labels
    ax.set_title('Portfolio Value Trajectories with Confidence Intervals (2025-2044)', fontsize=14)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Portfolio Value (USD)', fontsize=12)

    # Formatting ticks and grid
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Displaying the legend
    ax.legend(loc='upper left', fontsize=12)

    # Adjusting layout to make it look good
    plt.tight_layout()

    # Show the plot in Streamlit
    st.pyplot(fig)

    #-----------------------

    st.write("""
    The graph shows different hypothetical portfolio values. The confidential interval is really wide since the simulation estimates return in 2045 based on 2024 data.
    """)

    #-----------------------------------------------------------------------------------------------------
