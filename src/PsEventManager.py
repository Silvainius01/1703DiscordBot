import json
import sys
import time
import tkinter
from collections import namedtuple
from CharacterData import *
from DataFetcher import *
from web_sock import *

class EventManagerPS2:
    def __init__(self):
        self.eventTypeDict = {
        "ContinentLock": [],
        "ContinentUnlock": [],
        "FacilityControl": [],
        "Metagame": [],
        }
        # Character data currently being updated
        self.trackedChars = {
        }
        # Character data that is currently cached in memory, and not being actively updated. Examples being logged out chars
        self.untrackedChars = {
        }
        # Characters that we want data for, but have not logged in or proc'd an event.
        self.targetChars = {
        }
        # Dict for hashes of events where two tracked chars interacted with each other. Involved in duplicate event prevention.
        self.multiCharEvents = {
        }
        # Reversal names for easier data management. 
        self.death2kill = {
            "Death":"Kill",
            "VehicleDestroy":"VehicleKill"
        }
        return

    def ReceiveEvent(self, payload:str):
        """
            Entry point for all events received from websocket.
        """
        eventPayload = json.loads(payload).get("payload")
        if eventPayload == None:
            return
        if eventPayload.get("character_id"):
            self.ProcessCharacterEvent(eventPayload)
        else:
            self.eventTypeDict[eventPayload.get("event_name")].append(eventPayload)
        return

    def ProcessCharacterEvent(self, event):
        """
            Processes an event about a character. Will ignore events about non-target characters, and automatically handles tracking and untracking players.
        """
        charId = event["character_id"]
        eventName = event["event_name"]

        # If this is a kill event, determine if a tracked character was killed.
        if event.get("attacker_character_id"):
            attackerId = event["attacker_character_id"]
            if not self.IsTargetCharacter(charId):
                charId = attackerId # If the killed player is not tracked, set next candidate to be the killer
                event["event_name"] = self.death2kill.get(eventName, eventName+"_Kill")
            # If this is a multi-char event, process accordingly.
            elif self.IsTargetCharacter(attackerId):
                self.ProcessMultiCharEvent(event)
                return

        if not self.IsTrackedCharacter(charId):
            if not self.IsTargetCharacter(charId):
                return # If the character is not a target char, ignore event.
            self.StartTrackingCharacter(charId) # Start tracking this character if it is a target.
        self.trackedChars[charId].AddEvent(event)
        return

    def ProcessMultiCharEvent(self, event):
        """
            Processes an event in which two tracked chars interact with other
        """
        charId = event["character_id"]
        attackerId = event["attacker_character_id"]
        eventName = event["event_name"]

        # Make sure to track chars involved.
        self.StartTrackingCharacter(charId)
        self.StartTrackingCharacter(attackerId)

        # Add event for defender as normal
        self.trackedChars[charId].AddEvent(event)

        # Reverse event name for attacker, then add
        event["event_name"] = self.death2kill.get(eventName, eventName+"_Kill")
        self.trackedChars[attackerId].AddEvent(event)
        return

    def AddTargetCharacter(self, characterId:str, characterName:str):
        """
            Tells the Manager to keep a look out for events from these characters.
        """
        if self.IsTrackedCharacter(characterId):
            return
        self.targetChars[characterId] = characterName
        print("Added target character " + characterName + " with id " + characterId)

    def StartTrackingCharacter(self, characterId:str):
        """
           Generates a CharacterData object for the Id provided. Will fail if Id is not a target character. 
        """
        if self.targetChars.get(characterId):
            charName = self.targetChars.pop(characterId)
            self.trackedChars[characterId] = CharacterData(characterId, charName)
            print("Began tracking "+charName)
        if self.untrackedChars.get(characterId):
            self.trackedChars[characterId] = self.untrackedChars.pop(characterId)
        return

    def StopTrackingCharacter(self, characterId:str):
        """
            Cahces a tracked characters data, currently unused.
        """
        if not self.trackedChars.get(characterId):
            return
        charData = self.trackedChars.pop(characterId)
        self.untrackedChars[characterId] = charData
        return

    def IsTargetCharacter(self, characterId:str):
        return (self.targetChars.get(characterId) != None or
                self.trackedChars.get(characterId) != None or
                self.untrackedChars.get(characterId) !=  None)

    def IsTrackedCharacter(self, characterId):
        return self.trackedChars.get(characterId) != None

    def IsUntrackedCharacter(self, characterId):
        return self.untrackedChars.get(characterId) != None



if __name__ == "__main__":
    # init manager
    manager = EventManagerPS2()
    members = DataFetcher.fetchOutfitMemberList("1703", True)
    for member in members:
        manager.AddTargetCharacter(member.get("id"), member.get("name"))
    manager.AddTargetCharacter("5428985062301712145", "deThreeVS")
    manager.AddTargetCharacter("5428977504197397649", "TaterKnight")

    # init websocket
    websocket_listener = PS2_WebSocket_Listener("wss://push.planetside2.com/streaming?environment=ps2&service-id=s:17034223270")
    websocket_listener.addCallback(manager.ReceiveEvent)
    asyncio.get_event_loop().run_until_complete(websocket_listener.socketConnect(manager.targetChars.keys()))