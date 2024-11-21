# -- CREATE A LIST PORTFOLIO --
import json 
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import time
import os
import sys

def read_currencies_from_file(filename):
    currencies = {}
    current_folder = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_folder, f'{filename}')
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip():  # Check if the line is not empty
                name, quantity = line.strip().split(":")
                currencies[name] = float(quantity)
    folder_path= os.path.join(current_folder, 'Wallet history')
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return currencies, folder_path


def get_cryptocurrency_price_coingecko(symbol, response, loop):
    excluded_coins=["agility","artificial-general-intelligence"]
    if response.status_code == 200:
        data = response.json()
        #with open('coins_list.json', 'w') as json_file:
        #    json.dump(data, json_file, indent=4)
        coin_id = None
        for coin in data:
            if coin["symbol"] == symbol and coin['id'] not in excluded_coins:
                if coin["symbol"]=="agi" and coin["id"]!="delysium":
                    #print(coin["id"]+" rejected")
                    pass
                else:
                    coin_id = coin["id"]
                    break
        if coin_id:
            price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            price_response = requests.get(price_url)
            code = price_response.status_code
            if code == 429:
                if loop==False:
                    return 429
                elif loop==True:
                    while code==429:
                        retry_after = price_response.headers.get('Retry-After')
                        print ("Too many request to serwer. Retrying after: " + str(retry_after) + " sec")
                        for remaining in range(int(retry_after), 0, -10):
                            print(f"{remaining}...")
                            time.sleep(10) 
                        price_response = requests.get(price_url)
                        code = price_response.status_code
            if  code == 200:
                price_data = price_response.json()
                return price_data[coin_id]["usd"]
            else:
                print("Failed to fetch price data "+str(price_url)+'  '+str(price_response))
                return None
        else:
            print("Coin id error")
            return None
    else:
        print("Coingecko bad response: "+str(response.status_code))
        return None

def get_cryptocurrency_price_paprika(symbol):
    url = "https://api.coinpaprika.com/v1/tickers"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for currency in data:
            if currency['symbol'] == symbol:
                price = currency['quotes']['USD']['price']
                return price
        #print(f"Cryptocurrency with symbol {symbol} not found")
        return None
    else:
        print("Failed to fetch data")
        return None

def get_price(folder_path):
    print("Collecting data...")
    currencies_count=len(currencies)
    key = "https://api.binance.com/api/v3/ticker/price?symbol="     # Defining Binance API URL
    filedate= datetime.now().strftime("%d.%m.%Y %H%M%S")
    filename = folder_path+"/crypto list "+filedate + ".txt"
    total_value=0
    url_gecko = "https://api.coingecko.com/api/v3/coins/list"
    response_gecko = requests.get(url_gecko)
    currencies_fetched=0
    exec_list=[]
    def exec_info(currencies_fetched,exec_list,currencies_count):
        exec_proc= currencies_fetched/currencies_count
        if (not (0.23 < exec_proc < 0.27) and not (0.48 < exec_proc < 0.52) and not (0.73 < exec_proc < 0.77) and exec_proc != 1):
            pass
        else:
            exec_print=str((round(exec_proc*100/5))*5)+'%'#print only 25,50,75,100 % values
            if exec_print not in exec_list: #do not print twice 
                print (exec_print)
                return exec_print

    with open(filename, 'w') as file:
        for i in currencies:
            file.write(f"{i}\n")
            # completing API for request
            try: #try Binance API
                url = key+i
                response = requests.get(url)
                data = response.json()
                price = data['price']
                value=round(float(currencies[i])*float(price),2)
                total_value+=value
                file.write(f"quantity: {currencies[i]}\n")
                file.write(f"price: {price}\n")
                file.write(f"value: {value}\n\n")
                currencies_fetched+=1
                unique=exec_info(currencies_fetched,exec_list,currencies_count)
                if unique!=None:
                    exec_list.append(unique)

            except KeyError: #if coin not found try Coingecko API
                coin_symbol=(i.split('USDT')[0]).lower()
                coin_symbol_pap=coin_symbol.upper()
                price=get_cryptocurrency_price_paprika(coin_symbol_pap)
                if price==None:#if coin not found try BINANCE API
                    price=get_cryptocurrency_price_coingecko(coin_symbol,response_gecko,True)
                if price not in [None,429]:
                    value=round(float(currencies[i])*float(price),2)
                    total_value+=value
                file.write(f"quantity: {currencies[i]}\n")
                file.write(f"price: {price}\n")
                file.write(f"value: {value}\n\n")
                currencies_fetched+=1
                unique=exec_info(currencies_fetched,exec_list,currencies_count)
                if unique!=None:
                    exec_list.append(unique)
            except Exception as e:
                file.write(f"Error: {e}\n\n")
        file.write(f"total_value: {round(total_value,2)}")
        return filedate, filename

# -- CREATE A CHART --

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
                try:
                    value = float(value_line.split(":")[1])
                except ValueError:
                    value = 0
                coin_values[coin_symbol] = value
            else:
                pass        
            total_value = float(lines[-1].split(":")[1])
    return coin_values, total_value

def create_wheel_chart(coin_values, total_value, filedate, folder_path):
    sorted_coin_values = dict(sorted(coin_values.items(), key=lambda item: item[1], reverse=True))  
    labels = sorted_coin_values.keys()
    sizes = [(sorted_coin_values[symbol] / total_value) * 100 for symbol in sorted_coin_values]
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=100)
    ax.axis('equal') 
    ax.set_title(f'Percentage of Total Value [{int(total_value)}] for Each Coin')
    # Save the plot to a file
    plt.savefig(folder_path+f'/crypto distribution {filedate}.png', bbox_inches='tight')
    print("Data saved to the files")
    plt.show()
    plt.close()

if __name__=="__main__":
    wallet_filename = "currencies.txt"
    currencies, folder_path = read_currencies_from_file(wallet_filename)
    try:
        filedate, values_filename = get_price(folder_path)
    except requests.exceptions.ConnectionError as e:
        print("ERROR: No internet connection!")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print("HTTP ERROR: Server returned error!")
        sys.exit(1)
    coin_values, total_value = read_data(values_filename)
    create_wheel_chart(coin_values, total_value, filedate, folder_path)