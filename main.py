import platform
import asyncio
import aiohttp
import datetime
import calendar
from time import  time

async def main(days, list):
    time=datetime.datetime.now()
    url_old="https://api.privatbank.ua/p24api/exchange_rates?json&date="
    l=[]
    for i in range(days):
        str_time=time.strftime("%d.%m.%Y")
        url_new=url_old+str_time
        result = await take_info(url_new)
        dikt=await creater_dict(result,list)
        l.append(dikt)
        try:
            time=datetime.datetime(time.year, time.month, time.day-1)
        except ValueError:
            ff=calendar.monthrange(time.year, time.month-1)
            time=datetime.datetime(time.year, time.month-1, ff[1])
    return l
        

async def creater_dict(info, list):
    dicti={}
    dicti[info["date"]]={}  
    for i in info["exchangeRate"]:
        for c in list:
            if i["currency"]==c.upper():
                dicti[info["date"]][i["currency"]]={'sale':i["saleRateNB"],"purchase":i["purchaseRateNB"]}
    return  dicti


async def take_info(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            return result

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    x=input('Оберить кількість днів та валюта котра потрібна ')
    request= x.split(' ')
    try:
        num_days=int(request[0])
    except TypeError or ValueError:
        num_days=int(input('Ввeдіть число '))
    if num_days>10:
        num_days=int(input("Не більше 10 днів "))
    request.pop(0)
    start = time()
    r= asyncio.run(main(num_days,request))
    print(r)
    print(time() - start)
