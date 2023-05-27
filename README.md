Market Data Integrity from an API

Market Analysis

This code performs a market analysis of Bitcoin using data from CoinGecko. The analysis includes:

    Calculating the rolling 7-day average for price and volume
    Plotting the spot price, total volume, and z-scores of spot price and total volume
    Performing data tests on the data

To run the code, you will need to install the following dependencies:

    python3
    plotly
    pandas
    pycoingecko

The code will generate two HTML files:

    market_analysis.html - This file contains a plot of the spot price, total volume, and z-scores of spot price and total volume.
    test_results.html - This file contains a table of the results of the data tests.

Data

The code uses data from CoinGecko. To get the latest data, you can use the following command:

python
cg = CoinGeckoAPI()
chart_data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days='max')

The chart_data variable will contain a dictionary of data. The keys of the dictionary are the timestamps, and the values of the dictionary are the prices and total volumes for each timestamp.

Analysis

The code performs the following analysis:

    Calculates the rolling 7-day average for price and volume.
    Plots the spot price, total volume, and z-scores of spot price and total volume.
    Performs data tests on the data.

The rolling 7-day average is calculated by taking the average of the price and volume for the previous 7 days. The z-scores are calculated by subtracting the mean from each value and then dividing by the standard deviation.

The data tests are performed to ensure that the data is valid. The tests include:

    Checking that the data types are correct.
    Checking that the data is within a reasonable range.
    Checking that there are no missing values.
    Checking that the data is consistent.

Note: The data tests are rudimentary and may not catch all errors in the data. Users should add their own tests to ensure the integrity of the data.

Results

The results of the analysis are shown in the market_analysis.html and test_results.html files. The market_analysis.html file shows a plot of the spot price, total volume, and z-scores of spot price and total volume. The test_results.html file shows a table of the results of the data tests.

Conclusion

The code provides a simple way to perform a market analysis of Bitcoin and validate your API market data integrity.
