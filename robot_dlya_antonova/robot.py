import nest_asyncio
import websockets
import json
import asyncio
import yaml
from mysql.connector import connect
from contextlib import closing
from server import order_to_db



async def authorization(ws, client_id, client_secret):
    msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : client_id,
    "client_secret" : client_secret
  }
}
    login = json.dumps(msg)
    await ws.send(login)
    return await ws.recv()

async def order(websocket, trade, instrument, price, amount, type):
    msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2,
  "method" : "private/"+trade,
  "params" : {
    "instrument_name" : instrument,
    "price" : price,
    "amount" : amount,
    "type" : type,
    "label" : "market0000234"
  }
}
    deal = json.dumps(msg)
    await websocket.send(deal)
    return await websocket.recv()


async def cancel_all(websocket):
    msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2,
  "method" : "private/cancel_all",
}
    deal = json.dumps(msg)
    await websocket.send(deal)
    return await websocket.recv()

async def get_price(websocket, instrument):

    msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2,
  "method" : "public/get_order_book",
  "params" : {
    "instrument_name" : instrument,
    "depth" : 5
  }
}
    deal = json.dumps(msg)
    await websocket.send(deal)
    return await websocket.recv()


async def order_status_by_instrument(websocket, id):

    msg = \
{
  "jsonrpc" : "2.0",
  "id" : 2,
  "method" : "private/get_order_state",
  "params" : {
    "order_id" : id
  }
}
    deal = json.dumps(msg)
    await websocket.send(deal)
    return await websocket.recv()



async def get_order(ws, trade, price, amount):
    info = await order(ws, trade,'BTC-PERPETUAL', price, amount, 'limit')
    id = json.loads(info)['result']['order']['order_id']
    return id
        
async def robot(ws, gap, gap_ignore, amount):

        status = 'open'
        while status == 'open':
            price = await get_price(ws, 'BTC-PERPETUAL')
            current_price = json.loads(price)['result']['mark_price']
            buy_price = current_price - gap * 0.5
            id = await get_order(ws, 'buy', buy_price, amount)
            order_to_db(id, 'BUY', 'BTC-PERPETUAL',buy_price, amount,status)

            while current_price <= buy_price + gap + gap_ignore and status == 'open':
                    status = await order_status_by_instrument(ws, id)
                    status = json.loads(status)['result']['order_state']

                    price = await get_price(ws, 'BTC-PERPETUAL')
                    current_price = json.loads(price)['result']['mark_price']
                    
            if status == 'open':
                response = await cancel_all(ws)
                print('buy order canceled')
            else:
                print([status, buy_price, 'BUY'])
            
        status = 'open'
        while status == 'open':
            price = await get_price(ws, 'BTC-PERPETUAL')
            current_price = json.loads(price)['result']['mark_price']
            sell_price = current_price + gap
            id = await get_order(ws, 'sell', sell_price, amount)
            order_to_db(id, 'SELL', 'BTC-PERPETUAL',buy_price, amount,status)

            while current_price >= sell_price - gap - gap_ignore and status == 'open':
                    status = await order_status_by_instrument(ws, id)
                    status = json.loads(status)['result']['order_state']
                    price = await get_price(ws, 'BTC-PERPETUAL')
                    current_price = json.loads(price)['result']['mark_price']

            if status == 'open':
                response = await cancel_all(ws)
                print('sell order canceled')
            else:
                print([status, sell_price, 'SELL'])
        

async def call_api():
    

    with open('config.yaml') as f:
        template = yaml.safe_load(f)

    client_id = template['client_id']
    client_secret = template['client_secret']
    gap = template['gap']
    gap_ignore = template['gap_ignore']
    amount = template['amount']
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as ws:
        response = await authorization(ws, client_id, client_secret)
        while ws.open:
            await robot(ws, gap, gap_ignore, amount)
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(call_api())