from flask import Flask, request
from moralis import evm_api
from dotenv import load_dotenv
import execute
import datetime
import locale
import os
import json

# Load environment variables from a .env file
load_dotenv()

# Retrieve the Moralis API key from environment variables
api_key = os.getenv("MORALIS_API_KEY")

# Set the locale to en_US.UTF-8
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

# Create a Flask web application instance
app = Flask(__name__)

# Define a route for the "/getPrice" endpoint with the HTTP method "GET"
@app.route("/getPrice", methods=["GET"])
def prices():
    # Extract the "address" and "chain" parameters from the query string
    address = request.args.get("address")
    chain = request.args.get("chain")

    # Construct a dictionary of parameters
    params = {
        "chain": chain,
        "exchange": "pancakeswap-v2",
        "address": address,
    }

    # Call the Moralis API to get token price information
    result = evm_api.token.get_token_price(api_key=api_key, params=params)

    # Return the result as the response
    return result

# Define a route for the "webhook" endpoint with the HTTP method "POST"
@app.route("/webhook", methods=["POST"])
def webhook():
    # Receive the webhook data as a UTF-8 encoded string
    webhook = request.data.decode("utf-8")

    # Parse the JSON data into a Python dictionary
    json_object = json.loads(webhook)

    # Access the list of transactions from the JSON payload
    txs = json_object["txs"]

    for tx in txs:
        from_address = tx["fromAddress"]
        to_address = tx["toAddress"]

        # Define a specific "whale" address for comparison
        whale = "0xcA3B6f18Ebc4E7C66885eaAde4C2FF3Edcf48d02"
        whale = whale.lower()

        if from_address == whale:
            # If the "from_address" matches the "whale" address, execute a "sell" action
            print("sell")
            execute.execute_analysis_and_trade("sell")
        elif to_address == whale:
            # If the "to_address" matches the "whale" address, execute a "buy" action
            print("buy")
            execute.execute_analysis_and_trade("buy")
        else:
            # If neither condition is met, print "no whale"
            print("no whale")

    # Return "ok" as the response
    return "ok"

# Start the Flask web application
if __name__ == "__main__":
    app.run(port=5002, debug=True)
