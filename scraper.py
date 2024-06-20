from bs4 import BeautifulSoup
import requests
import re
import schedule
import time
from datetime import datetime, timedelta

def find_stocks():
    sym = ['●','\u20b9']
    rep = ['','INR ']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    url = requests.get("https://www.5paisa.com/share-market-today/stocks-to-buy-or-sell-today",headers=headers)

    if url.status_code == 200:
        soup = BeautifulSoup(url.text,'lxml')

        market = soup.find('section',class_ = 'faq-mainwrapper block block-block-content block-block-content61a7b17c-4717-4781-abf7-0ee6e4c144d0 clearfix')
        stocks = market.find_all('h2')
        details = market.find_all('h4')
        date = stocks[0].text.split('on ')[1].strip()
        datas = []
        for i in range(1,6):
            stock = stocks[i].text.strip()
            detail_array = []
            for detail in details[(i-1)*6:i*6]:
                text = detail.text
                for j in range(len(sym)):
                    text = text.replace(sym[j],rep[j])
                detail_array.append(text.strip())
            datas.append([stock,detail_array])

        def clean_and_convert(value):
            clean_value = re.sub(r'[^0-9.]', '', value)
            return float(clean_value)

        price = {}
        target1 = {}
        target2 = {}
        profit = {}
        for data in datas:
            stock_name = data[0].split(':')[0]
            price[stock_name] =   clean_and_convert(data[1][2].split('INR ')[1])
            target1[stock_name] = clean_and_convert(data[1][3].split('INR ')[1])
            target2[stock_name] = clean_and_convert(data[1][4].split('INR ')[1])
            profit[stock_name] = ((target1[stock_name] - price[stock_name]) / target1[stock_name])*100
            
            results = []
            if price[stock_name] < 2500 and profit[stock_name] > 2:
                result = f"{stock_name}\n"
                if profit[stock_name] >= 0:
                    result += f"BUY at: "
                else:
                    result += f"SELL at: "
                result += f"{price[stock_name]}\n"
                result += f"Target: {target1[stock_name]} - {target2[stock_name]}\n"
                result += f"Profit: {abs(profit[stock_name])}% \n\n\n"
                results.append(result)

                with open(f'{date}.txt', 'a') as file:
                    for result in results:
                        file.write(result)
                
    else:
        print(f'failed to retrieve the page. status code: {url.status_code}')

if __name__ == '__main__':
    schedule.every().day.at("04:00").do(find_stocks)  # 9:30 AM IST is 4:00 AM UTC
    while True:
        schedule.run_pending()
        time.sleep(60)
       