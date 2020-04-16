import json
from collections import namedtuple

class BasePsEvent:
    payload = ""
    service = ""
    type = ""

class EventManagerPS2:
    i = 0
    
    def BaseEventDecoder(eventDict):
       return namedtuple('BasePsEvent', eventDict.keys())(*eventDict.values)