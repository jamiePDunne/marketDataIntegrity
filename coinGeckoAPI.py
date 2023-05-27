import datetime
import plotly.graph_objects as go
import pandas as pd
from pycoingecko import CoinGeckoAPI
from plotly.subplots import make_subplots
import dateutil.relativedelta as relativedelta
import scipy.stats as stats
import plotly.offline as offline


def range_validation(data, column, min_value, max_value):
    return (data[column] >= min_value) & (data[column] <= max_value)


def perform_data_tests(data):
    tests = {
        'Data Type Validation - Spot Price': lambda x: 'Pass' if pd.api.types.is_numeric_dtype(x['Price']) else 'Fail',
        'Data Type Validation - Total Volume': lambda x: 'Pass' if pd.api.types.is_numeric_dtype(x['Volume']) else 'Fail',
        'Range Validation - Spot Price': lambda x: 'Pass' if range_validation(x, 'Price', 0, float('inf')).all() else 'Fail',
        'Range Validation - Total Volume': lambda x: 'Pass' if range_validation(x, 'Volume', 0, float('inf')).all() else 'Fail',
        'Null Value Validation - Spot Price': lambda x: 'Pass' if not x['Price'].isnull().any() else 'Fail',
        'Null Value Validation - Total Volume': lambda x: 'Pass' if not x['Volume'].isnull().any() else 'Fail',
        'Duplicate Value Validation - Spot Price': lambda x: 'Pass' if not x.duplicated(subset='Price').any() else 'Fail',
        'Duplicate Value Validation - Total Volume': lambda x: 'Pass' if not x.duplicated(subset='Volume').any() else 'Fail',
        'Consistency Validation - Spot Price': lambda x: 'Pass' if not x['Price'].isnull().any() else 'Fail',
        'Consistency Validation - Total Volume': lambda x: 'Pass' if not x['Volume'].isnull().any() else 'Fail',
    }

    test_results = {test_name: {col: test_func(data) for col in ['Price', 'Volume']} for test_name, test_func in tests.items()}

    return test_results


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

# Perform data tests
test_results = perform_data_tests(rolling_average)

# Create subplots
fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=("Spot Price", "Total Volume", "Z-Scores"))

# Add traces for spot price, total volume
fig.add_trace(go.Scatter(x=rolling_average.index, y=rolling_average['Price'], name='Spot Price'), row=1, col=1)
fig.add_trace(go.Scatter(x=rolling_average.index, y=rolling_average['Volume'], name='Total Volume'), row=2, col=1)

# Add horizontal line at the latest value of total volume
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

# Add traces for z-score of spot price and total volume
spot_price_zscore = stats.zscore(rolling_average['Price'])
volume_zscore = stats.zscore(rolling_average['Volume'])

fig.add_trace(go.Scatter(x=rolling_average.index, y=spot_price_zscore, name='Spot Price Z-score'), row=3, col=1)
fig.add_trace(go.Scatter(x=rolling_average.index, y=volume_zscore, name='Total Volume Z-score'), row=3, col=1)

# Add horizontal lines for Z-score plot
fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=-2,
    x1=rolling_average.index[-1],
    y1=-2,
    line=dict(color='blue', width=1, dash='dash'),
    row=3,
    col=1
)

fig.add_shape(
    type="line",
    x0=rolling_average.index[0],
    y0=2,
    x1=rolling_average.index[-1],
    y1=2,
    line=dict(color='blue', width=1, dash='dash'),
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

# Create the table trace
test_table = go.Table(
    header=dict(values=['Test', 'Spot Price', 'Total Volume']),
    cells=dict(values=[list(test_results.keys()), [result['Price'] for result in test_results.values()], [result['Volume'] for result in test_results.values()]]),
)

# Create the figure for the table
table_fig = go.Figure(data=[test_table])

# Configure the layout for the table figure
table_fig.update_layout(
    title="Test Results",
)

# Save the figures as HTML
offline.plot(fig, filename='market_analysis.html', auto_open=True)
offline.plot(table_fig, filename='test_results.html', auto_open=True)
