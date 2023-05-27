import datetime
import plotly.graph_objects as go
import pandas as pd
from pycoingecko import CoinGeckoAPI
from plotly.subplots import make_subplots
import dateutil.relativedelta as relativedelta
import numpy as np
from scipy.stats import zscore

# Specify the start date variable in months
months_ago = 75  # Specify the number of months ago

# Initialize CoinGeckoAPI
cg = CoinGeckoAPI()

# Get the market chart data for BTC-USD
chart_data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days='max')

# Extract the timestamps, prices, and total volumes from the chart data
timestamps = [datetime.datetime.fromtimestamp(timestamp[0] / 1000) for timestamp in chart_data['prices']]
prices = [float(price[1]) for price in chart_data['prices']]
volumes = [float(volume[1]) for volume in chart_data['total_volumes']]

# Create a DataFrame with timestamps, prices, and volumes
data = pd.DataFrame({'Timestamp': timestamps, 'Price': prices, 'Volume': volumes})

# Set the Timestamp column as the index
data.set_index('Timestamp', inplace=True)

# Calculate the rolling 7-day average for price and volume
rolling_average = data.rolling('7D').mean()

# Calculate the start date by subtracting the specified number of months from the current date
start_date = datetime.datetime.now() - relativedelta.relativedelta(months=months_ago)

# Filter the data for the desired date range
rolling_average = rolling_average.loc[start_date:]

# Calculate Z-scores for spot price and total volume
spot_price_zscore = zscore(rolling_average['Price'])
total_volume_zscore = zscore(rolling_average['Volume'])

# Create subplots
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1)

# Add trace for spot price
fig.add_trace(go.Scatter(x=rolling_average.index, y=rolling_average['Price'], name='Spot Price'), row=1, col=1)

# Add trace for total volume
fig.add_trace(go.Scatter(x=rolling_average.index, y=rolling_average['Volume'], name='Total Volume'), row=2, col=1)

# Add horizontal line at the most recent value of Total Volume
latest_volume = rolling_average['Volume'].iloc[-1]
fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=latest_volume,
    x1=rolling_average.index[-1],
    y1=latest_volume,
    line=dict(color='red', width=1, dash='dash'),
    row=2,
    col=1
)

# Add trace for spot price z-score
fig.add_trace(go.Scatter(x=rolling_average.index, y=spot_price_zscore, name='Spot Price Z-score'), row=3, col=1)

# Add trace for total volume z-score
fig.add_trace(go.Scatter(x=rolling_average.index, y=total_volume_zscore, name='Total Volume Z-score'), row=3, col=1)

# Add horizontal lines for z-score plot
fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=2,
    x1=rolling_average.index[-1],
    y1=2,
    line=dict(color='black', width=1, dash='dash'),
    row=3,
    col=1
)
fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=-2,
    x1=rolling_average.index[-1],
    y1=-2,
    line=dict(color='black', width=1, dash='dash'),
    row=3,
    col=1
)
fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=0,
    x1=rolling_average.index[-1],
    y1=0,
    line=dict(color='black', width=1),
    row=3,
    col=1
)

# Update y-axis labels
fig.update_yaxes(title_text='Spot Price', row=1, col=1)
fig.update_yaxes(title_text='Total Volume', row=2, col=1)
fig.update_yaxes(title_text='Z-score', row=3, col=1)

# Add layout for the plot
fig.update_layout(
    title="Bitcoin Market Data (7 day moving averages)- Spot Price, Total Volume, and Z-scores",
    xaxis_rangeslider_visible=False
)

# Show the plot
fig.show()
