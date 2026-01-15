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

# Mapping broker symbols to Yahoo Finance tickers
YAHOO_MAPPING = {
    'XAUUSD': 'GC=F',
    'GOLD': 'GC=F',
    'BTCUSD': 'BTC-USD',
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    'USDJPY': 'JPY=X',
}

# Function to calculate momentum
def calculate_momentum(symbol, period_days):
    # Fetch historical data - add extra days to account for weekends and holidays
    end_date = datetime.datetime.now()
    # Multiply by 1.5 to ensure we have enough data even with weekends
    start_date = end_date - datetime.timedelta(days=int(period_days * 1.5) + 5)
    
    # Determine the ticker to use for Yahoo Finance
    yahoo_ticker = YAHOO_MAPPING.get(symbol, symbol)
    
    print(f"--- Fetching Data for {symbol} (Yahoo Ticker: {yahoo_ticker}) ---")
    data = yf.download(yahoo_ticker, start=start_date, end=end_date, interval="1d")
    
    # Check if data is empty, it might be a forex pair requiring "=X" for yfinance
    if len(data) == 0 and symbol not in YAHOO_MAPPING:
        # Try appending "=X" which is common for forex pairs on Yahoo Finance
        print(f"No data found for {yahoo_ticker}, trying {symbol}=X...")
        data = yf.download(f"{symbol}=X", start=start_date, end=end_date, interval="1d")

    # Check if we have enough data for the requested period
    required_data_points = period_days + 1
    if len(data) < required_data_points:
        print(f"Not enough data to calculate momentum. Need at least {required_data_points} data points, but only have {len(data)}.")
        return None

    # Calculate momentum as the difference between the last closing price and the price N days ago
    # We need at least period_days + 1 data points to calculate momentum
    try:
        current_close = data['Close'].iloc[-1]
        # Use -(period_days + 1) to get the price from N days ago
        past_close = data['Close'].iloc[-(period_days + 1)]
        
         # Handle case where yfinance returns a DataFrame for Close (multi-ticker behavior edge case)
        if hasattr(current_close, 'iloc'): 
             current_close = current_close.iloc[0]
        if hasattr(past_close, 'iloc'):
             past_close = past_close.iloc[0]
             
        momentum = current_close - past_close
        print(f"Price {period_days} days ago: {past_close:.5f}, Current price: {current_close:.5f}")
        return momentum
    except Exception as e:
        print(f"Error calculating momentum: {e}")
        return None

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

    # Check if symbol is visible in Market Watch, if not, enable it
    if not symbol_info.visible:
        print(f"Symbol {symbol} is not visible, attempting to select it...")
        if not mt5.symbol_select(symbol, True):
            print(f"symbol_select({symbol}) failed, error code =", mt5.last_error())
            return False
            
    # Refresh symbol info after selection
    symbol_info = mt5.symbol_info(symbol)

    price = symbol_info.ask if action == "buy" else symbol_info.bid
    digits = symbol_info.digits
    
    # Determine filling mode
    filling_type = mt5.ORDER_FILLING_FOK
    filling_type = mt5.ORDER_FILLING_FOK
    
    # Symbol filling flags (missing in mt5 module, defining manually)
    SYMBOL_FILLING_FOK = 1
    SYMBOL_FILLING_IOC = 2
    
    if symbol_info.filling_mode & SYMBOL_FILLING_IOC:
        filling_type = mt5.ORDER_FILLING_IOC
    elif symbol_info.filling_mode & SYMBOL_FILLING_FOK:
        filling_type = mt5.ORDER_FILLING_FOK

    # Create the order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": f"{action.capitalize()} order by Python",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_type,
    }

    # Send the order
    print(f"Sending order: {request}...")
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed. Error: {result.comment} (Retcode: {result.retcode})")
        return False

    print(f"{action.capitalize()} order placed successfully. Ticket: {result.order}")
    return True

# Main function
def main():
    if not connect_to_mt5():
        return
        
    symbol_input = input("Enter the stock or forex symbols (comma-separated, e.g., EURUSD, AAPL, XAUUSD): ").upper()
    symbols = [s.strip() for s in symbol_input.split(',') if s.strip()]
    
    try:
        lot_input = input("Enter lot size (default 0.1): ")
        volume = float(lot_input) if lot_input.strip() else 0.1
    except ValueError:
        print("Invalid input. Using default lot size: 0.1")
        volume = 0.1
    
    # Get momentum period from user
    try:
        period_input = input("Enter momentum period in days (e.g., 3 for 3-day momentum, default 3): ")
        period_days = int(period_input) if period_input.strip() else 3
        if period_days < 1:
            print("Period must be at least 1 day. Using default: 3")
            period_days = 3
    except ValueError:
        print("Invalid input. Using default period: 3 days")
        period_days = 3
    
    print(f"\nCalculating {period_days}-day momentum...\n")

    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        momentum = calculate_momentum(symbol, period_days)
        if momentum is None:
            continue

        print(f"{period_days}-day Momentum for {symbol}: {momentum:.5f}")
        
        # Decide whether to buy or sell based on momentum
        if momentum > 0:
            print(f"Momentum is positive. Placing a buy order (Volume: {volume})...")
            place_order(symbol, "buy", volume)
        elif momentum < 0:
            print(f"Momentum is negative. Placing a sell order (Volume: {volume})...")
            place_order(symbol, "sell", volume)
        else:
            print("Momentum is neutral. No action taken.")

    # Shutdown MT5 connection
    mt5.shutdown()

if __name__ == "__main__":
    main()
