import os
import websockets
import datetime
import time

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\testdata"
saveDirectoryWebsocket = saveDirectory + "\\websocket"

def saveDataToDiskAppend(data:str, filePath:str, fileName:str):
	if not os.path.exists(filePath):
		os.makedirs(filePath)
	dump_file = open("{0}\\{1}".format(filePath, fileName), "a")
	dump_file.write("\n\n{0}\n{1}".format(datetime.datetime.now(), data))
	dump_file.close()
	return

def StartLoop(loop):
	asyncio.set_event_loop(loop)
	loop.run_forever()
	return

class PsEventGatherer:
	def __init__(self):
		self.uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
		self.callbacks = []
		self.charIds = []
		self.eventNames = []
		self.worlds = []
		self.maxRetry = 3
		self.eventBuffers = { }
		self.currBuffer = 0

	def addCallback(self, callback):
		self.callbacks.append(callback)
		return

	def setCharIds(self, charIds:list):
		self.charIds = charIds if charIds != None and (isinstance(charIds,list)) else []
		return
	def setEventNames(self, events:list):
		self.eventNames = events if events != None and (isinstance(events,list)) else []
		return
	def setWorlds(self, worlds:list):
		self.worlds = worlds if worlds != None and (isinstance(worlds,list)) else []
		return

	def __charArg__(self):
		"""
			Creates the character listener argument for the websocket. If nothing is provided, will listen to all chars.
		"""
		if self.charIds != None and self.charIds.__len__() > 0:
			charList = []
			for id in self.charIds:
				charList.append('"{0}"'.format(id))
			charList = ",".join(charList)
			return '"characters":[{0}]'.format(charList)
		return '"characters":["all"]'

	def __eventArg__(self):
		if self.eventNames != None and self.eventNames.__len__() > 0:
			eventList = []
			for id in self.eventNames:
				eventList.append('"{0}"'.format(id))
			eventList = ",".join(eventList)
			return '"eventNames":[{0}]'.format(eventList)
		return '"eventNames":["all"]'
	
	def __worldArg__(self):
		arg = '"worlds":["all"]'
		if self.worlds != None and self.worlds.__len__() > 0:
			worldList = []
			for id in self.worlds:
				worldList.append('"{0}"'.format(id))
			worldList = ",".join(worldList)
			arg = '"worlds":[{0}]'.format(worldList)
		return '{0},"logicalAndCharactersWithWorlds":true'.format(arg)

	async def socketConnect(self):
		i = 0
		currBuffer = 0
		print("Establishing connections...")
		while i < self.maxRetry:
			try:
				async with websockets.connect(self.uri) as websocket:
					i = 0
					print("Connected.")
					msg  = '{{"service":"event","action":"subscribe",{0},{1},{2} }}'.format(self.__charArg__(), self.__eventArg__(), self.__worldArg__())
			
					await websocket.send(msg)

					receivePackets = True
					while receivePackets:
						payload = await websocket.recv()
						self.SendPayloadToBuffer(payload)
					await websocket.send('{"service":"event","action":"clearSubscribe","all":"true"}')
			except websockets.exceptions.ConnectionClosedError as exc:
				saveDataToDiskAppend(exc, saveDirectoryWebsocket, "log.txt")
				print("Connection Failed. Retrying ({0}/{1})...".format(i+1, self.maxRetry))
			except ConnectionResetError as exc:
				saveDataToDiskAppend(exc, saveDirectoryWebsocket, "log.txt")
				print("Connection Reset. Retrying ({0}/{1})...".format(i+1, self.maxRetry))
			i += 1
		return

	def RunEventLog(self, file):
		for line in file.readlines():
			payload = "{{ \"payload\": {0} }}".format(line.strip())
			self.SendPayloadToBuffer(payload)
		return

	def SendPayloadToBuffer(self, payload):
		bufferId = self.currBuffer
		self.eventBuffers[bufferId].append(payload)
		self.currBuffer = (bufferId+1)%len(self.eventBuffers)
		return

	def ProcessBuffer(self):
		bufferId = len(self.eventBuffers)
		if self.eventBuffers.get(bufferId) == None:
			self.eventBuffers[bufferId] = []
		while True:
			if len(self.eventBuffers[bufferId]) > 0:
				payload = self.eventBuffers[bufferId].pop(0)
				for callback in self.callbacks:
					callback(rawResponse=payload)
			else: time.sleep(1)
		return

	def MonitorBuffers(self, threadStartFunc):
		eventCount = 0
		for buffer in self.eventBuffers:
			eventCount += len(buffer)
		eventCount // 1000
		for i in range(1000, eventCount, 1000):
			threadStartFunc()
		time.sleep(60)


if __name__ == "__main__":
	uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
	websocket_listener = PsEventGatherer(uri)
	asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect())
	