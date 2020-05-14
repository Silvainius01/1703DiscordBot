import asyncio

import websockets

class PS2_WebSocket_Listener:
	def __init__(self, callbacks:list = []):
		self.uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
		self.callbacks = callbacks

	def addCallback(self, callback):
		self.callbacks.append(callback)

	def startListener(self, characterIds:list, eventNames:list):
		characterIds = self.createCharListenerArg(characterIds)
		eventNames = self.createEventListenerArg(eventNames)
		asyncio.get_event_loop().run_until_complete(self.socketConnect(characterIds, eventNames))
		print("after")
		return

	def createCharListenerArg(self, characterIds:list):
		"""
			Creates the character listener argument for the websocket. If nothing is provided, will listen to all chars.
		"""
		if characterIds != None and characterIds.__len__() > 0:
			charList = []
			for id in characterIds:
				charList.append('"{0}"'.format(id))
			charList = ",".join(charList)
			return '"characters":[{0}]'.format(charList);
		return '"characters":["all"]'

	def createEventListenerArg(self, eventNames:list):
		if eventNames != None and eventNames.__len__() > 0:
			eventList = []
			for id in eventNames:
				eventList.append('"{0}"'.format(id))
			eventList = ",".join(eventList)
			return '"eventNames":[{0}]'.format(eventList);
		return '"eventNames":["all"]'

	async def socketConnect(self, charArgument, eventArgument):
		async with websockets.connect(self.uri) as websocket:
			#msg = '{"service":"event","action":"subscribe","characters":["all"],"eventNames":["Death","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]}'
			msg = '{"service":"event","action":"subscribe",' + charArgument + ',"eventNames":["AchievementEarned","BattleRankUp","Death","ItemAdded","SkillAdded","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"]}'
			#msg  = '{"service":"event","action":"subscribe",{0},{1}}'.format(charArgument, eventArgument)
			await websocket.send('{"service":"event","action":"clearSubscribe","all":"true"}')
			await websocket.send(msg)

			while True:
				payload = await websocket.recv()
				for callback in self.callbacks:
					callback(payload=payload)
				#print(payload)

if __name__ == "__main__":
	uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
	websocket_listener = PS2_WebSocket_Listener(uri)
	asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect())
	