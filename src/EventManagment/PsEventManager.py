import json
import sys
from collections import namedtuple
from CharacterData import *
   

class EventManagerPS2:
    eventFuncDict = {
        "ContinentLock": [],
        "ContinentUnlock": [],
        "FacilityControl": [],
        "Metagame": [],
    }
    characterDict = {
    }
    
    def __init__(self):
        return

    def ReceiveEvent(json: str):
        baseEvent = json.loads(json, object_hook=BaseEventDecoder)
        realEvent = EventDecoder(baseEvent.payload)
        eventTypeDict[realEvent.event_name].append(realEvent)
        return

    def BaseEventDecoder(eventDict):
       return namedtuple('BasePsEvent', eventDict.keys())(*eventDict.values)

    def EventDecoder(payload):
        name = payload.event_name + "Event"
        return namedtuple(name, payload.keys())(*payload.values())

    def AddEventToCharacter(event):
        if not event.character_id in characterDict:
            characterDict[event.character_id] = CharacterData(event.character_id)
        characterDict[event.character_id].AddEvent(event)
        return