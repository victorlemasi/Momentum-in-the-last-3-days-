import yfinance as yf
import MetaTrader5 as mt5
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Broker login details
BROKER_LOGIN = int(os.getenv("BROKER_LOGIN", "0"))
BROKER_PASSWORD = os.getenv("BROKER_PASSWORD", "")
BROKER_SERVER = os.getenv("BROKER_SERVER", "")

# Function to calculate momentum
def calculate_momentum(symbol):
    # Fetch historical data for the last 3 days
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=7)
    
    data = yf.download(symbol, start=start_date, end=end_date, interval="1d")
    
    if len(data) < 3:
        print("Not enough data to calculate momentum.")
        return None

    # Calculate momentum as the difference between the last closing price and the price 3 days ago
    momentum = data['Close'][-1] - data['Close'][-4]
    return momentum

# Function to connect to MetaTrader 5
def connect_to_mt5():
    if not mt5.initialize():
        print(f"MetaTrader5 initialization failed. Error: {mt5.last_error()}")
        return False

    # Log in to the broker
    login_status = mt5.login(BROKER_LOGIN, password=BROKER_PASSWORD, server=BROKER_SERVER)
    if not login_status:
        print(f"Login failed. Error: {mt5.last_error()}")
        mt5.shutdown()
        return False

    print(f"Logged in successfully to {BROKER_SERVER} with account {BROKER_LOGIN}.")
    return True

# Function to place a buy or sell order in MT5
def place_order(symbol, action, volume=0.1):
    # Define the order type
    order_type = mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL

    # Get the current symbol price
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        print(f"Symbol {symbol} not found.")
        return False

    price = symbol_info.ask if action == "buy" else symbol_info.bid

    # Create the order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": f"{action.capitalize()} order by Python",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send the order
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed. Error: {result.comment}")
        return False

    print(f"{action.capitalize()} order placed successfully.")
    return True

# Main function
def main():
    symbol = input("Enter the stock or forex symbol (e.g., EURUSD, AAPL): ").upper()
    if not connect_to_mt5():
        return

    momentum = calculate_momentum(symbol)
    if momentum is None:
        return

    print(f"Momentum for {symbol}: {momentum}")
    
    # Decide whether to buy or sell based on momentum
    if momentum > 0:
        print("Momentum is positive. Placing a buy order...")
        place_order(symbol, "buy")
    elif momentum < 0:
        print("Momentum is negative. Placing a sell order...")
        place_order(symbol, "sell")
    else:
        print("Momentum is neutral. No action taken.")

    # Shutdown MT5 connection
    mt5.shutdown()

if __name__ == "__main__":
    main()
