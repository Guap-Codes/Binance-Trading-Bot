# Import necessary libraries
import pandas
import numpy
import binance_connect
import time
import requests

# Function to convert Binance candlestick data to a Pandas DataFrame
def get_and_transform_data(symbol, timeframe, number_of_candles):
    """
    Retrieve and transform candlestick data from Binance into a DataFrame.

    Args:
        symbol (str): The trading symbol (e.g., 'SOLUSDT').
        timeframe (str): The timeframe for the candlestick data (e.g., '1h', '1d').
        number_of_candles (int): The number of candles to retrieve.

    Returns:
        pandas.DataFrame: Transformed candlestick data with added columns.
    """
    # Retrieve raw candlestick data from Binance
    raw_data = binance_connect.get_candlestick_data(symbol, timeframe, number_of_candles)

    # Transform the raw data into a DataFrame
    df = pandas.DataFrame(raw_data)

    # Convert timestamp columns to datetime format
    df["time"] = pandas.to_datetime(df["time"], unit="ms")
    df["close_time"] = pandas.to_datetime(df["close_time"], unit="ms")

    # Add a column to classify candlestick color as 'Green' or 'Red'
    df["RedOrGreen"] = numpy.where((df["open"] < df["close"]), "Green", "Red")

    return df

# Function to get the price of a token based on its address and blockchain chain
def get_token_price(address, chain):
    """
    Get the price of a token based on its address and blockchain chain.

    Args:
        address (str): The token's address.
        chain (str): The blockchain chain (e.g., 'Ethereum', 'Binance Smart Chain').

    Returns:
        float: The price of the token in USD.
    """
    # Make an API request to retrieve token price data
    url = f"http://localhost:5002/getPrice?address={address}&chain={chain}"
    response = requests.get(url)
    data = response.json()

    # Extract the USD price from the response
    usd_price = data["usdPrice"]

    return usd_price

# Function to check the pair relation
def check_pair_relation(address1, address2, chain):
    """
    Check the ratio of two token prices based on their addresses and blockchain chain.

    Args:
        address1 (str): The address of the first token.
        address2 (str): The address of the second token.
        chain (str): The blockchain chain (e.g., 'Ethereum', 'Binance Smart Chain').

    Returns:
        float: The ratio of the prices of the two tokens.
    """
    price1 = get_token_price(address1, chain)
    price2 = get_token_price(address2, chain)

    ratio = price1 / price2

    return ratio

# Function to check the current ratio relative to a reference ratio
def check_ratio_relation(current_ratio, reference_ratio):
    """
    Compare the current ratio to a reference ratio to make trading decisions.

    Args:
        current_ratio (float): The current ratio to be compared.
        reference_ratio (float): The reference ratio for comparison.

    Returns:
        bool: True if the current ratio is less than the reference ratio, otherwise False.
    """
    if current_ratio > reference_ratio:
        return False
    elif current_ratio < reference_ratio:
        return True

# Function to check for consecutive price increases or decreases
def determine_trade_event(symbol, timeframe, percentage_change, candle_color):
    """
    Check for consecutive candlesticks with the same color and percentage changes to trigger trades.

    Args:
        symbol (str): The trading symbol (e.g., 'SOLUSDT').
        timeframe (str): The timeframe for candlestick data (e.g., '1h', '1d').
        percentage_change (float): The minimum percentage change required to trigger a trade.
        candle_color (str): The color of candlesticks to be considered ('Green' or 'Red').

    Returns:
        bool: True if trading conditions are met, otherwise False.
    """
    candlestick_data = get_and_transform_data(symbol, timeframe, 3)

    if (
        candlestick_data.loc[0, "RedOrGreen"] == candle_color
        and candlestick_data.loc[1, "RedOrGreen"] == candle_color
        and candlestick_data.loc[2, "RedOrGreen"] == candle_color
    ):
        change_one = determine_percentage_change(
            candlestick_data.loc[0, "open"], candlestick_data.loc[0, "close"]
        )
        change_two = determine_percentage_change(
            candlestick_data.loc[1, "open"], candlestick_data.loc[1, "close"]
        )
        change_three = determine_percentage_change(
            candlestick_data.loc[2, "open"], candlestick_data.loc[2, "close"]
        )

        if candle_color == "Red":
            print(f'First Drop: {change_one}')
            print(f'Second Drop: {change_two}')
            print(f'Third Drop: {change_three}')
        elif candle_color == "Green":
            print(f'First Increase: {change_one}')
            print(f'Second Increase: {change_two}')
            print(f'Third Increase: {change_three}')

        if (
            change_one >= percentage_change
            and change_two >= percentage_change
            and change_three >= percentage_change
        ):
            return True
        else:
            return False
    else:
        return False

# Function to calculate percentage change between two prices
def determine_percentage_change(close_previous, close_current):
    """
    Calculate the percentage change between two closing prices.

    Args:
        close_previous (float): The previous closing price.
        close_current (float): The current closing price.

    Returns:
        float: The percentage change between the two prices.
    """
    return (close_current - close_previous) / close_previous

# Function to analyze symbols based on specified trading conditions
def analyze_symbols(symbol_dataframe, timeframe, percentage, type):
    """
    Analyze trading symbols based on specific trading conditions.

    Args:
        symbol_dataframe (pandas.DataFrame): DataFrame containing trading symbols and their details.
        timeframe (str): The timeframe for candlestick data (e.g., '1h', '1d').
        percentage (float): The minimum percentage change for triggering a trade.
        type (str): The type of trade analysis ('buy' or 'sell').

    Returns:
        bool: True if trading conditions are met for at least one symbol, otherwise False.
    """
    for index in symbol_dataframe.index:
        if type == "buy":
            analysis = determine_trade_event(
                symbol_dataframe.loc[index],
                timeframe,
                percentage,
                "Green",
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive rises')
            else:
                print(
                    f'{symbol_dataframe["symbol"][index]} does not have 3 consecutive rises'
                )
            time.sleep(1)
            return analysis
        elif type == "sell":
            analysis = determine_trade_event(
                symbol_dataframe["symbol"][index],
                timeframe=timeframe,
                percentage_change=percentage,
                candle_color="Red",
            )
            if analysis:
                print(f'{symbol_dataframe["symbol"][index]} has 3 consecutive drops')
            else:
                print(
                    f'{symbol_dataframe["symbol"][index]} does not have 3 consecutive drops'
                )
            time.sleep(1)
            return analysis

# Function to calculate buying parameters for a symbol
def calculate_buy_params(symbol, pair, timeframe):
    """
    Calculate trading parameters for a buy trade.

    Args:
        symbol (str): The trading symbol (e.g., 'SOLUSDT').
        pair (pandas.DataFrame): DataFrame containing trading pair details.
        timeframe (str): The timeframe for candlestick data (e.g., '1h', '1d').

    Returns:
        dict: Parameters for a buy trade.
    """
    raw_data = binance_connect.get_candlestick_data(symbol, timeframe, 1)

    precision = pair.iloc[0]["baseAssetPrecision"]
    filters = pair.iloc[0]["filters"]
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            step_size = float(f["stepSize"])
            min_qty = float(f["minQty"])
        elif f["filterType"] == "PRICE_FILTER":
            tick_size = float(f["tickSize"])

    close_price = raw_data[0]["close"]
    buy_stop = close_price * 1.01
    buy_stop = round(buy_stop / tick_size) * tick_size
    raw_quantity = 0.1 / buy_stop
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": buy_stop,
        "trailingDelta": 100,
    }
    return params

# Function to calculate selling parameters for a symbol
def calculate_sell_params(symbol, pair, timeframe):
    """
    Calculate trading parameters for a sell trade.

    Args:
        symbol (str): The trading symbol (e.g., 'SOLUSDT').
        pair (pandas.DataFrame): DataFrame containing trading pair details.
        timeframe (str): The timeframe for candlestick data

    Returns:
        dict: Parameters for a sell trade.
    """
    raw_data = binance_connect.get_candlestick_data(symbol=symbol, timeframe=timeframe, number_of_candles=1)

    precision = pair.iloc[0]["baseAssetPrecision"]
    filters = pair.iloc[0]["filters"]
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            min_qty = float(f["minQty"])
            step_size = float(f["stepSize"])
            break

    close_price = raw_data[0]["close"]
    sell_stop = close_price * 0.99
    raw_quantity = 0.1 / sell_stop
    quantity = max(min_qty, round(raw_quantity - (raw_quantity % step_size), precision))
    params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "STOP_LOSS_LIMIT",
        "timeInForce": "GTC",
        "quantity": quantity,
        "price": close_price,
        "trailingDelta": 100,
    }
    return params
