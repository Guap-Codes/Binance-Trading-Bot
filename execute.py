import json
import os
import binance
import strategy

# Specify the path to the JSON settings file
import_path = "settings.json"

# Function to load project settings from a JSON file
def get_settings(import_path):
    # Check if the JSON settings file exists
    if os.path.exists(import_path):
        # Open and read the settings file
        file = open(import_path, "r")
        # Parse the JSON content into a Python dictionary
        project_settings = json.load(file)
        file.close()
        # Return the loaded project settings
        return project_settings
    else:
        # If the file doesn't exist, return an ImportError
        return ImportError

# Function to execute the trading analysis and trade based on a specified action
def execute_analysis_and_trade(buy_or_sell):
    # Load project settings from the JSON file
    project_settings = get_settings(import_path)

    # Extract API key and secret key from project settings
    api_key = project_settings["BinanceKeys"]["API_KEY"]
    secret_key = project_settings["BinanceKeys"]["SECRET_KEY"]

    # Define specific tokens from the project settings
    SOL = project_settings["Tokens"]["SOL"]
    USDT = project_settings["Tokens"]["USDT"]
    BUSD = project_settings["Tokens"]["BUSD"]

    # Query the Binance account using API credentials
    account = binance_connect.query_account(api_key, secret_key)
    if account["canTrade"]:
        print("Your account is ready to trade")

        # Calculate the reference and current ratios using the trading strategy
        reference_ratio = strategy.check_pair_relation(SOL, USDT, "bsc")
        current_ratio = strategy.check_pair_relation(BUSD, USDT, "bsc")

        # Print the reference and current ratios
        print(f"Reference ratio: {reference_ratio}")
        print(f"Current ratio: {current_ratio}")

        # Calculate the difference between the ratios
        check = strategy.check_ratio_relation(current_ratio, reference_ratio)

        # Query a list of quote assets related to "USDT"
        asset_list = binance_connect.query_quote_asset_list("USDT")
        # Identify a specific trading pair (e.g., SOL/USDT)
        sol_pair = asset_list.loc[asset_list["symbol"] == "SOLUSDT"]
        symbol = sol_pair["symbol"].values[0]

        if check and buy_or_sell == "buy":
            print("Buying Time")
            # Analyze trading symbols for potential buying opportunities
            analysis = strategy.analyze_symbols(sol_pair, "1h", 0.000001, "buy")
            if analysis:
                print("Buying SOL")
                # Calculate buy trade parameters
                params = strategy.calculate_buy_params(symbol, sol_pair, "1h")
                # Execute the buy trade
                response = binance_connect.make_trade_with_params(params, project_settings)
                print(response)
            else:
                print("Not Buying SOL")
                print(f"Reason: The analysis is {analysis}")
        elif buy_or_sell == "sell":
            print("Selling Time")
            # Analyze trading symbols for potential selling opportunities
            analysis = strategy.analyze_symbols(sol_pair, "1h", 0.000001, "sell")
            if analysis:
                print("Selling SOL")
                # Calculate sell trade parameters
                params = strategy.calculate_sell_params(symbol, sol_pair, "1h")
                # Execute the sell trade
                response = binance_connect.make_trade_with_params(params, project_settings)
                print(response)
            else:
                print("Not Selling SOL")
                print(f"Reason: The analysis is {analysis}")

