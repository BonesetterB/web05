import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import datetime
import aiohttp
import aiofiles
import calendar

logging.basicConfig(level=logging.INFO)

async def take_info(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            return result

async def creater_dict(info):
    dicti={}
    for i in info["exchangeRate"]:
            if i["currency"]=="EUR" or i["currency"]=="USD" or i["currency"]=="GBP":
                dicti[i["currency"]]={'sale':i["saleRateNB"],"purchase":i["purchaseRateNB"]}
    return  dicti

async def from_dilt_str(dikt,day):
    string=f' |||{day}\nВалютний курс||| '
    for key,val in dikt.items():
        string+=f"\n{key}\nПродажа {val['sale']} \nКупівля: {val['purchase']}"
    return string

async def exchange():
    time=datetime.datetime.now()
    url_old="https://api.privatbank.ua/p24api/exchange_rates?json&date="
    str_time=time.strftime("%d.%m.%Y")
    url_new=url_old+str_time
    result = await take_info(url_new)
    dikt=await creater_dict(result)
    result=await from_dilt_str(dikt,str_time)
    async with aiofiles.open('exchange\login.txt', mode='w') as f:
         await f.write(result)
    return result

async def exchange2():
    time=datetime.datetime.now()
    url_old="https://api.privatbank.ua/p24api/exchange_rates?json&date="
    str_time=time.strftime("%d.%m.%Y")
    l=''
    for i in range(2):
        str_time=time.strftime("%d.%m.%Y")
        url_new=url_old+str_time
        result = await take_info(url_new)
        dikt=await creater_dict(result)
        result=await from_dilt_str(dikt,str_time)
        l+=result
        try:
            time=datetime.datetime(time.year, time.month, time.day-1)
        except ValueError:
            ff=calendar.monthrange(time.year, time.month-1)
            time=datetime.datetime(time.year, time.month-1, ff[1])
    async with aiofiles.open('exchange\login.txt', mode='w') as f:
         await f.write(l)
    return l

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
             if message == 'exchange':
                 info =await exchange()
                 await self.send_to_clients(f"{info}")
             elif message == 'exchange 2':
                 info= await exchange2()
                 await self.send_to_clients(f"{info}")
             else:
                 await self.send_to_clients(f"{ws.name}: {message}")
    


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())