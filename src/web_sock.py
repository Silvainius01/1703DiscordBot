import asyncio
import websockets

class PS2_WebSocket_Listener:
	def __init__(self, uri):
		self.uri = uri

	async def socketConnect(self):
		async with websockets.connect(self.uri) as websocket:
			await websocket.send('{"service":"event","action":"clearSubscribe","all":"true"}')
			await websocket.send('{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]}')

			while True:
				payload = await websocket.recv()
				print(payload)

if __name__ == "__main__":
	uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
	websocket_listener = PS2_WebSocket_Listener(uri)
	asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect())
	