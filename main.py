import requests
import json
import tkinter as tk
from tkinter import ttk
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

load_dotenv()
API_KEY = os.getenv('COINMARKETCAP_API_KEY')
print(f"API_KEY: {API_KEY}")  # Debugging line to check if the API key is read correctly
BASE_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

def get_crypto_data():
    if not API_KEY:
        print("Error: API key not found. Please set the COINMARKETCAP_API_KEY environment variable.")
        return None

    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }
    print("Fetching data from CoinMarketCap API...")
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code == 200:
        print("Data fetched successfully.")
        return response.json()
    else:
        print(f"Error: Failed to fetch data. Status code: {response.status_code}")
        return None

def get_global_metrics():
    url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Global metrics data fetched successfully.")
        return response.json()
    else:
        print(f"Error: Failed to fetch global metrics. Status code: {response.status_code}")
        return None

def display_global_metrics():
    global_data = get_global_metrics()
    if global_data:
        total_market_cap = global_data['data']['quote']['USD']['total_market_cap']
        btc_dominance = global_data['data']['btc_dominance']
        global_metrics_label.config(text=f"Total Market Cap: ${total_market_cap:,.2f}\nBTC Dominance: {btc_dominance:.2f}%")
    else:
        global_metrics_label.config(text="Failed to fetch global metrics.")

def convert_currency(amount, symbol_from, symbol_to):
    url = 'https://pro-api.coinmarketcap.com/v1/tools/price-conversion'
    params = {
        'amount': amount,
        'symbol': symbol_from,
        'convert': symbol_to
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    print(f"Converting {amount} {symbol_from} to {symbol_to}...")
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Currency conversion successful.")
        return response.json()
    else:
        print(f"Error: Failed to convert currency. Status code: {response.status_code}")
        return None

def display_currency_conversion():
    try:
        amount = float(amount_entry.get())
        symbol_from = from_currency_entry.get().upper()
        symbol_to = to_currency_entry.get().upper()
        conversion_data = convert_currency(amount, symbol_from, symbol_to)
        if conversion_data:
            converted_amount = conversion_data['data']['quote'][symbol_to]['price']
            conversion_label.config(text=f"{amount} {symbol_from} = {converted_amount:.2f} {symbol_to}")
        else:
            conversion_label.config(text="Failed to convert currency.")
    except ValueError:
        conversion_label.config(text="Invalid input. Please enter a valid amount.")

def get_crypto_info(crypto_symbol):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
    params = {'symbol': crypto_symbol}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        print("Cryptocurrency info fetched successfully.")
        return response.json()
    else:
        print(f"Error: Failed to fetch cryptocurrency info. Status code: {response.status_code}")
        return None

def display_crypto_info():
    crypto_symbol = crypto_info_entry.get().upper()
    info_data = get_crypto_info(crypto_symbol)
    if info_data:
        info = info_data['data'][crypto_symbol]
        info_label.config(text=f"Name: {info['name']}\nSymbol: {info['symbol']}\nCategory: {info['category']}")
    else:
        info_label.config(text="Failed to fetch cryptocurrency info.")

def analyze_data(data):
    if data:
        top_10 = data['data'][:10]
        return [(crypto['name'], crypto['symbol'], crypto['quote']['USD']['market_cap'], crypto['quote']['USD']['price']) for crypto in top_10]
    else:
        return []

def plot_data(analyzed_data):
    names = [item[0] for item in analyzed_data]
    market_caps = [item[2] for item in analyzed_data]

    fig, ax = plt.subplots()
    ax.barh(names, market_caps, color='skyblue')
    ax.set_xlabel('Market Cap (USD)')
    ax.set_title('Top 10 Cryptocurrencies by Market Cap')

    return fig

def display_data():
    print("Displaying data...")
    data = get_crypto_data()
    if data is None:
        print("No data to display.")
        return

    analyzed_data = analyze_data(data)
    
    for item in tree.get_children():
        tree.delete(item)
    
    for item in analyzed_data:
        tree.insert('', tk.END, values=(item[0], item[1], item[2], item[3]))
    print("Data displayed.")

    fig = plot_data(analyzed_data)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def refresh_data():
    print("Refreshing data...")
    display_data()
    root.after(60000, refresh_data)  # Refresh data every 60 seconds

def on_closing():
    plt.close('all')
    root.destroy()

root = tk.Tk()
root.title("Cryptocurrency Analyzer")

# Treeview for displaying cryptocurrency data
tree = ttk.Treeview(root, columns=('Name', 'Symbol', 'Market Cap', 'Price'), show='headings')
tree.heading('Name', text='Name')
tree.heading('Symbol', text='Symbol')
tree.heading('Market Cap', text='Market Cap')
tree.heading('Price', text='Price')
tree.pack(expand=True, fill='both')

# Button to refresh data
refresh_button = tk.Button(root, text="Refresh", command=display_data)
refresh_button.pack()

# Section for displaying global metrics
global_metrics_label = tk.Label(root, text="")
global_metrics_label.pack()
global_metrics_button = tk.Button(root, text="Display Global Metrics", command=display_global_metrics)
global_metrics_button.pack()

# Section for currency conversion
tk.Label(root, text="Amount").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()
tk.Label(root, text="From Currency").pack()
from_currency_entry = tk.Entry(root)
from_currency_entry.pack()
tk.Label(root, text="To Currency").pack()
to_currency_entry = tk.Entry(root)
to_currency_entry.pack()
conversion_button = tk.Button(root, text="Convert Currency", command=display_currency_conversion)
conversion_button.pack()
conversion_label = tk.Label(root, text="")
conversion_label.pack()

# Section for displaying cryptocurrency info
tk.Label(root, text="Crypto Symbol").pack()
crypto_info_entry = tk.Entry(root)
crypto_info_entry.pack()
crypto_info_button = tk.Button(root, text="Get Crypto Info", command=display_crypto_info)
crypto_info_button.pack()
info_label = tk.Label(root, text="")
info_label.pack()

root.protocol("WM_DELETE_WINDOW", on_closing)

display_data()
root.after(60000, refresh_data)  # Start the periodic refresh

root.mainloop()