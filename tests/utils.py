import yaml
import websockets
import asyncio
import json

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

async def call_api():
#    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
#        await websocket.send(msg)
    with open('config.yaml') as f:
        template = yaml.safe_load(f)

    client_id = template['client_id']
    client_secret = template['client_secret']
    gap = template['gap']
    gap_ignore = template['gap_ignore']
    amount = template['amount']
    print(1)
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as ws:
        response = await authorization(ws, client_id, client_secret)
        print(ws)
        return ws


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(call_api())