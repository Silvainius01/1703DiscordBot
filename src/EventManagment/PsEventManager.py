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
        eventPayload = json.loads(json).get("payload")
        if "character_id" in  eventPayload:
            EventManagerPS2.AddEventToCharacter(payload)
        else:
            eventTypeDict[eventPayload.get("event_name")].append(realEvent)
        return

    def AddEventToCharacter(event):
        charId = event["character_id"]
        if not charId in characterDict:
            characterDict[charId] = CharacterData(charId)
        characterDict[charId].AddEvent(event)
        return