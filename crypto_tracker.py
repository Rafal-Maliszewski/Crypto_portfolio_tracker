# -- CREATE A LIST PORTFOLIO --
import json 
import requests
from datetime import datetime

# Defining Binance API URL 
key = "https://api.binance.com/api/v3/ticker/price?symbol="

# Making list for multiple crypto's 
currencies = {"BTCUSDT":0.01, #insert {name:quantity}
"ETHUSDT":0.1,
"MATICUSDT":1,
"AVAXUSDT":1,
"ONDOUSDT":100,
"MAVIAUSDT":10,
} 
other_currencies={"MAVIAUSDT":1 #other, not listed on binance ; in progress...
                  }

def get_cryptocurrency_price(symbol):
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        coin_id = None
        for coin in data:
            if coin["symbol"] == symbol:
                coin_id = coin["id"]
                break
        
        if coin_id:
            price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            price_response = requests.get(price_url)
            if price_response.status_code == 200:
                price_data = price_response.json()
                return price_data[coin_id]["usd"]
            else:
                print("Failed to fetch price data")
                return None
        else:
            print("Coin not found")
            return None
    else:
        print("Failed to fetch data")
        return None


filedate= datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename =  "crypto_"+filedate + "_list.txt"
total_value=0
with open(filename, 'w') as file:
    for i in currencies:
        file.write(f"{i}\n")
        print(i)
        # completing API for request
        try: #try Binance API
            url = key+i
            data = requests.get(url) 
            data = data.json()
            price = data['price'] 
            value=round(float(currencies[i])*float(price),2)
            total_value+=value
            print(f"{data['symbol']} price is {price}") 
            print(f"{data['symbol']} value is {value} \n")
            file.write(f"price: {price}\n")
            file.write(f"value: {value}\n\n")
        except KeyError: #if coin not found try Coingecko API
            coin_symbol=(i.split('USDT')[0]).lower()
            price=get_cryptocurrency_price(coin_symbol)
            value=round(float(currencies[i])*float(price),2)
            total_value+=value
            print(f"{coin_symbol} price is {price}") 
            print(f"{coin_symbol} value is {value} \n")
            file.write(f"price: {price}\n")
            file.write(f"value: {value}\n\n")
        except Exception as e:
            file.write(f"Error: {e}\n\n")
    print(round(total_value,2))
    file.write(f"total_value: {round(total_value,2)}")

# -- CREATE A CHART --

import matplotlib.pyplot as plt

def read_data(filename):
    coin_values = {}

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "USD" in line:
                symbol_line=line.split('USD')
                coin_symbol = str(symbol_line[0])
            elif "total_value" in line:
                pass
            elif "value" in line:
                value_line = line.strip(': ')
                value = float(value_line.split(":")[1])
                coin_values[coin_symbol] = value
            else:
                pass     
    
            total_value = float(lines[-1].split(":")[1])
    return coin_values, total_value

def create_wheel_chart(coin_values, total_value):
    sorted_coin_values = dict(sorted(coin_values.items(), key=lambda item: item[1], reverse=True))  
    labels = sorted_coin_values.keys()
    sizes = [(sorted_coin_values[symbol] / total_value) * 100 for symbol in sorted_coin_values]
    
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=100)
    ax.axis('equal') 
    ax.set_title(f'Percentage of Total Value [{int(total_value)}] for Each Coin')
    # Save the plot to a file
    plt.savefig(f'crypto_{filedate}_distribution.png', bbox_inches='tight')
    plt.show()
    plt.close()

coin_values, total_value = read_data(filename)
create_wheel_chart(coin_values, total_value)