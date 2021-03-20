from robot_dlya_antonova.robot import order, cancel_all, authorization
# from tests.utils import call_api
# import tests.utils as test
import unittest
import aiounittest
import json
import yaml
import websockets
import asyncio
# import json

# def test_version():
    # assert __version__ == '0.1.0'
class Tests(aiounittest.AsyncTestCase):


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


	async def test_get_order(self):
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
				info = await order(ws, 'buy', 'BTC-PERPETUAL', 40000, 10, 'limit')
				id = json.loads(info)['result']['order']['order_id']
				status = json.loads(info)['result']['order']['order_state']
				await ws.close()
			self.assertEqual(status, 'open')

	async def test_cancel_all(self):
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
		
				info = await cancel_all(ws)
				result = json.loads(info)['result']
				await ws.close()
			self.assertEqual(result, 1)

# if __name__ == '__main__':
# 	asyncio.get_event_loop().run_until_complete(call_api())
# 	unittest.main()
