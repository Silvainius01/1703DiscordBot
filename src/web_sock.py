import asyncio
import os
import websockets
import datetime

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\testdata"
saveDirectoryWebsocket = saveDirectory + "\\websocket"

def saveDataToDiskAppend(data:str, filePath:str, fileName:str):
	if not os.path.exists(filePath):
		os.makedirs(filePath)
	dump_file = open("{0}\\{1}".format(filePath, fileName), "a")
	dump_file.write("\n\n{0}\n{1}".format(datetime.datetime.now(), data))
	dump_file.close()
	return

class PS2_WebSocket_Listener:
	def __init__(self, callbacks:list = []):
		self.uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
		self.callbacks = callbacks
		self.charIds = []
		self.eventNames = []
		self.worlds = []
		self.maxRetry = 3

	def addCallback(self, callback):
		self.callbacks.append(callback)

	def startListener(self):
		asyncio.get_event_loop().run_until_complete(self.socketConnect())
		print("after")
		return

	def setCharIds(self, charIds:list):
		self.charIds = charIds if charIds != None and (charIds is list) else []
		return
	def setEventNames(self, events:list):
		self.eventNames = events if events != None and (events is list) else []
		return
	def setWorlds(self, worlds:list):
		self.worlds = worlds if worlds != None and (worlds is list) else []
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
		if self.worlds != None and self.worlds.__len__() > 0:
			worldList = []
			for id in self.worlds:
				worldList.append('"{0}"'.format(id))
			worldList = ",".join(worldList)
			return '"worlds":[{0}]'.format(worldList)
		return '"worlds":["all"]'

	async def socketConnect(self):
		i = 0
		print("Establishing connections...")
		while i < self.maxRetry:
			try:
				async with websockets.connect(self.uri) as websocket:
					i = 0
					print("Connected.")
					msg  = '{{"service":"event","action":"subscribe",{0},{1},{2} }}'.format(self.__charArg__(), self.__eventArg__(), self.__worldArg__())
			
					await websocket.send('{"service":"event","action":"clearSubscribe","all":"true"}')
					await websocket.send(msg)

					while True:
						payload = await websocket.recv()
						for callback in self.callbacks:
							callback(payload=payload)
			except websockets.exceptions.ConnectionClosedError as exc:
				saveDataToDiskAppend(exc, saveDirectoryWebsocket, "log.txt")
				print("Connection Failed. Retrying ({0}/{1})...".format(i+1, self.maxRetry))
			except ConnectionResetError as exc:
				saveDataToDiskAppend(exc, saveDirectoryWebsocket, "log.txt")
				print("Connection Reset. Retrying ({0}/{1})...".format(i+1, self.maxRetry))
			i += 1
		return

if __name__ == "__main__":
	uri = "wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270"
	websocket_listener = PS2_WebSocket_Listener(uri)
	asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect())
	