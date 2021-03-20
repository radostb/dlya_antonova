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

# async def order_status(websocket):

#     msg = \
# {
#   "jsonrpc" : "2.0",
#   "id" : 2,
#   "method" : "private/get_open_orders_by_currency",
#   "params" : {
#     "currency" : "BTC"
#   }
# }
#     deal = json.dumps(msg)
#     await websocket.send(deal)
#     return await websocket.recv()

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
        # response = await cancel_all(ws)
        
#         buy_info = await buy(ws, 'BTC-PERPETUAL', buy_price, amount, 'limit')
#         id = json.loads(buy_info)['result']['order']['order_id']
        
#         status = await order_status_by_instrument(ws, id)
#         status = json.loads(status)['result']['order_state']
        status = 'open'
        while status == 'open':
            price = await get_price(ws, 'BTC-PERPETUAL')
            current_price = json.loads(price)['result']['mark_price']
            buy_price = current_price - gap * 0.5
            id = await get_order(ws, 'buy', buy_price, amount)
            order_to_db(id, 'BUY', 'BTC-PERPETUAL',buy_price, amount,status)
            # query = """INSERT INTO orders (id, buy_or_sell, currency, price, volume, order_status) VALUES (%s, %s, %s, %s, %s, %s)"""
            # cursor.execute(query, order_to_db)
        
            # db.commit()
#      
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
            # query = """INSERT INTO orders (id, buy_or_sell, currency, price, volume, order_status) VALUES (%s, %s, %s, %s, %s, %s)"""
            # cursor.execute(query, order_to_db)
            # db.commit()
            while current_price >= sell_price - gap - gap_ignore and status == 'open':
                    status = await order_status_by_instrument(ws, id)
                    status = json.loads(status)['result']['order_state']
                    price = await get_price(ws, 'BTC-PERPETUAL')
                    current_price = json.loads(price)['result']['mark_price']
#                     print([status, current_price, sell_price, 'SELL'])
            if status == 'open':
                response = await cancel_all(ws)
                print('sell order canceled')
            else:
                print([status, sell_price, 'SELL'])
        
#         price = await get_price(ws, 'BTC-PERPETUAL')
#         current_price = json.loads(price)['result']['mark_price']
#         sell_price = current_price + gap
#         sell_info = await sell(ws, 'BTC-PERPETUAL', sell_price, amount, 'limit')
#         id = json.loads(sell_info)['result']['order']['order_id']
#         status = await order_status_by_instrument(ws, id)
#         status = json.loads(status)['result']['order_state']
#         while status == 'open':
            
#             if current_price < sell_price - gap - gap_ignore:
#                 response = await cancel_all(ws)
#                 print('sell order canceled')
#                 break
#             id = json.loads(sell_info)['result']['order']['order_id']
#             status = await order_status_by_instrument(ws, id)
#             status = json.loads(status)['result']['order_state']
#             price = await get_price(ws, 'BTC-PERPETUAL')
#             current_price = json.loads(price)['result']['mark_price']
#             print([status, current_price, 'SELL'])


async def call_api():
#    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
#        await websocket.send(msg)
#     ordersdb = connect(
#         host="localhost",
#         user='root',
#         password='EZsh4tgC',
#         db='world'
# )
    

    with open('config.yaml') as f:
        template = yaml.safe_load(f)

    client_id = template['client_id']
    client_secret = template['client_secret']
    gap = template['gap']
    gap_ignore = template['gap_ignore']
    amount = template['amount']
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as ws:
        response = await authorization(ws, client_id, client_secret)
#         data = json.loads(response)
#         print(data['result']['access_token'])
       ###############
       # Before sending message, make sure that your connection
       # is authenticated (use public/auth call before) 
       ###############
#        await websocket.send(msg2)
#     while websocket.open:
#            response = await websocket.recv()
#            print(response)
#            await websocket.send(msg2)
#         with ws.open:
        while ws.open:
            await robot(ws, gap, gap_ignore, amount)
#             response = await get_price(ws, 'BTC-PERPETUAL')
#             price = json.loads(response)['result']['mark_price']
#             break
#             print(price)
#             response = await buy(ws, 'BTC-PERPETUAL', 1488, 10, 'limit')
#             print(response)
#             response = await sell(ws, 'BTC-PERPETUAL', 133769, 10, 'limit')
#             print(response)
#             response = await cancel_all(ws, 'BTC-PERPETUAL')
#             print(response)
#
#         finally:
#             await close_ws(ws)
#            response = await websocket.recv()
#            print(response)
#            response2 = await websocket.recv()
           # do something with the response...
#            print(response2)

# nest_asyncio.apply()
if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(call_api())