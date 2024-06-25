from binance.spot import Spot
import pandas

# Function to query the Binance system status
def query_binance_status():
    """
    Queries the system status of Binance.

    Returns:
        bool: True if the system is operational, raises ConnectionError otherwise.
    """
    status = Spot().system_status()
    if status['status'] == 0:
        return True
    else:
        raise ConnectionError

# Function to query account information
def query_account(api_key, secret_key):
    """
    Queries the account information associated with the provided API key and secret key.

    Args:
        api_key (str): The Binance API key.
        secret_key (str): The corresponding secret key.

    Returns:
        dict: Account information.
    """
    return Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url='https://testnet.binance.vision'
    ).account()

# Function to query the Binance testnet server time
def query_testnet():
    """
    Connects to the Binance testnet and prints the server time.
    """
    client = Spot(base_url="https://testnet.binance.vision")
    print(client.time())

# Function to query historical candlestick data
def get_candlestick_data(symbol, timeframe, qty):
    """
    Queries historical candlestick data for a trading pair.

    Args:
        symbol (str): The trading pair symbol.
        timeframe (str): The candlestick timeframe (e.g., '1h', '1d').
        qty (int): The number of candlesticks to retrieve.

    Returns:
        list: List of dictionaries containing candlestick data.
    """
    raw_data = Spot().klines(symbol=symbol, interval=timeframe, limit=qty)
    converted_data = []

    for candle in raw_data:
        # Convert raw data to a dictionary for readability
        converted_candle = {
            "time": candle[0],
            "open": float(candle[1]),
            "high": float(candle[2]),
            "low": float(candle[3]),
            "close": float(candle[4]),
            "volume": float(candle[5]),
            "close_time": candle[6],
            "quote_asset_volume": float(candle[7]),
            "number_of_trades": int(candle[8]),
            "taker_buy_base_asset_volume": float(candle[9]),
            "taker_buy_quote_asset_volume": float(candle[10]),
        }
        converted_data.append(converted_candle)

    return converted_data

# Function to query trading pairs with a specific quote asset
def query_quote_asset_list(quote_asset_symbol):
    """
    Queries trading pairs with the specified quote asset and filters for those in 'TRADING' status.

    Args:
        quote_asset_symbol (str): The quote asset symbol (e.g., 'SOL').

    Returns:
        pandas.DataFrame: DataFrame containing trading pairs with the quote asset.
    """
    symbol_dictionary = Spot().exchange_info()
    symbol_dataframe = pandas.DataFrame(symbol_dictionary["symbols"])
    quote_symbol_dataframe = symbol_dataframe.loc[
        (symbol_dataframe["quoteAsset"] == quote_asset_symbol) & (symbol_dataframe["status"] == "TRADING")
    ]
    return quote_symbol_dataframe

# Function to place a trade with given parameters
def make_trade_with_params(params, project_settings):
    """
    Places a trade using the provided parameters.

    Args:
        params (dict): Dictionary containing trade parameters.
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response from the trade execution.
    """
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["SECRET_KEY"]
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    try:
        response = client.new_order(**params)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to query open trades
def query_open_trades(project_settings):
    """
    Queries open trades associated with the provided API key and secret key.

    Args:
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response containing open trade orders.
    """
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    try:
        response = client.get_open_orders()
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to cancel an open trade by symbol
def cancel_order_by_symbol(symbol, project_settings):
    """
    Cancels open trade orders for the specified trading pair (symbol).

    Args:
        symbol (str): The trading pair symbol.
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response from the order cancellation.
    """
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    client = Spot(
        api_key=api_key,
        api_secret=secret_key,
        base_url="https://testnet.binance.vision",
    )
    try:
        response = client.cancel_open_orders(symbol=symbol)
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to place a limit order for a symbol
def place_limit_order(symbol, side, quantity, price, project_settings):
    """
    Places a limit order for a specified trading pair.

    Args:
        symbol (str): The trading pair symbol.
        side (str): The order side ('BUY' or 'SELL').
        quantity (float): The order quantity.
        price (float): The order price.
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response from the order placement.
    """
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            price=price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to place a stop loss order for a symbol
def place_stop_loss_order(symbol, side, quantity, stop_price, limit_price, project_settings):
    """
    Places a stop loss order for a specified trading pair.

    Args:
        symbol (str): The trading pair symbol.
        side (str): The order side ('BUY' or 'SELL').
        quantity (float): The order quantity.
        stop_price (float): The stop price.
        limit_price (float): The limit price.
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response from the order placement.
    """
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="STOP_LOSS_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")

# Function to place a take profit order for a symbol
def place_take_profit_order(symbol, side, quantity, stop_price, limit_price, project_settings):
    """
    Places a take profit order for a specified trading pair.

    Args:
        symbol (str): The trading pair symbol.
        side (str): The order side ('BUY' or 'SELL').
        quantity (float): The order quantity.
        stop_price (float): The stop price.
        limit_price (float): The limit price.
        project_settings (dict): Project-specific settings.

    Returns:
        dict: Response from the order placement.
    """
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    client = Spot(
        key=api_key, secret=secret_key, base_url="https://testnet.binance.vision"
    )
    try:
        response = client.new_order(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT_LIMIT",
            timeInForce="GTC",
            quantity=quantity,
            stopPrice=stop_price,
            price=limit_price,
        )
        return response
    except ConnectionRefusedError as error:
        print(f"Error: {error}")
