import asyncio
import websockets

class PS2_WebSocket_Listener:
	def __init__(self, uri):
		self.uri = uri
		self.callbacks = []

	def addCallback(self, callback):
		self.callbacks.append(callback)

	async def socketConnect(self, characterIds):
		async with websockets.connect(self.uri) as websocket:
			charArray = '"characters":['
			for id in characterIds:
				charArray = charArray + '"' + id + '"'
			charArray = charArray + "]"
			charArray = charArray.replace('""', '","')

			await websocket.send('{"service":"event","action":"clearSubscribe","all":"true"}')
			# await websocket.send('{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]}')
			await websocket.send('{"service":"event","action":"subscribe",' + charArray + ',"eventNames":["AchievementEarned","BattleRankUp","Death","ItemAdded","SkillAdded","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]}')


			while True:
				payload = await websocket.recv()
				for callback in self.callbacks:
					callback(payload=payload)
				#print(payload)

if __name__ == "__main__":
	uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
	websocket_listener = PS2_WebSocket_Listener(uri)
	asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect())
	