# -- CREATE A LIST PORTFOLIO --
import json 
import requests
from datetime import datetime

# Defining Binance API URL 
key = "https://api.binance.com/api/v3/ticker/price?symbol="

# Making list for multiple crypto's 
currencies = {"BTCUSDT":1, #insert {name:quantity}
"ETHUSDT":1,
"MATICUSDT":1,
"AVAXUSDT":1,
"SOLUSDT":1,
"DOTUSDT":1,
"ATOMUSDT":3,
"IOTAUSDT":4,
"XRPUSDT":4,
"ADAUSDT":1,
"DOGEUSDT":2,
} 
other_currencies={"MAVIAUSDT":1 #other, not listed on binance ; in progress...
                  }
filedate= datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename =  "crypto_"+filedate + "_list.txt"
total_value=0
with open(filename, 'w') as file:
    for i in currencies:
        file.write(f"{i}\n")
        print(i)
        # completing API for request 
        url = key+i
        data = requests.get(url) 
        data = data.json()
        price = data['price'] 
        value=float(currencies[i])*float(price)
        total_value+=value
        print(f"{data['symbol']} price is {price}") 
        print(f"{data['symbol']} value is {value} \n")
        try:
            price = data['price'] 
            value = float(currencies[i]) * float(price)
            file.write(f"price: {price}\n") 
            file.write(f"value: {value}\n\n")
        except KeyError:
            file.write(f"Error: No price data found for {i}\n\n")
        except Exception as e:
            file.write(f"Error: {e}\n\n")
    print(total_value)
    file.write(f"total_value: {total_value}")

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