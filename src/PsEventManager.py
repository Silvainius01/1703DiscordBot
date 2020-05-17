import json
import sys
import time
import tkinter
import os
import datetime
import hashlib

from collections import namedtuple
from DataFetcher import *
from web_sock import *
from EventFilter import *
from TrackerBase import *

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open("{0}\\{1}".format(filePath, fileName), "w")
    dump_file.write(response_serialized)
    dump_file.close()
    return
def saveDataToDiskAppend(data:str, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open("{0}\\{1}".format(filePath, fileName), "a")
    dump_file.write("{0}\n".format(response_serialized))
    dump_file.close()
    return

class EventManagerPS2:
    instance = None

    def __init__(self):
        self.eventTypeDict = {
        "ContinentLock": [],
        "ContinentUnlock": [],
        "FacilityControl": [],
        "MetagameEvent": [],
        }

        self.allUnfilteredEvents = []

        self.filters = {
            "ex" : [],
            "in" : []
        }

        self.eventHashes = { }

        basePath = "{0}\\testdata".format(os.path.dirname(os.path.abspath(__file__)))
        timestr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        self.tracker = TrackerBase()
        self.writeEnabled = True
        self.writeLogEnabled = True
        self.writeToDiskInterval = 50
        self.eventSinceWrite = self.writeToDiskInterval
        self.writePath = "{0}\\tracker_sessions".format(basePath)
        self.sessionFileName = "session_{0}.json".format(timestr)
        self.eventLogName = "session_{0}_eventlog.txt".format(timestr)
        EventManagerPS2.instance = self
        return

    def SetTracker(self, tracker:TrackerBase):
        self.tracker = tracker
        return

    def ReceiveEvent(self, payload:str):
        """
            Entry point for all events received from websocket.
        """
        eventPayload = json.loads(payload).get("payload")

        # If no payload or event doesnt pass filters
        if eventPayload == None or self.FilterEvent(eventPayload):
            return

        # Protection against duplicate events
        hash = EventManagerPS2.__GenerateEventHash__(eventPayload)
        try: 
            if self.eventHashes[hash]:
                return
        except KeyError:
            self.eventHashes[hash] = True

        if self.writeLogEnabled:
            saveDataToDiskAppend(eventPayload, self.writePath, self.eventLogName)

        if self.tracker.ProcessEvent(eventPayload):
            if self.writeEnabled:
                if self.eventSinceWrite > self.writeToDiskInterval:
                    self.WriteTrackerData()
                    self.eventSinceWrite = 0
                self.eventSinceWrite += 1
        return

    def WriteTrackerData(self):
        print("")
        saveDataToDisk(self.tracker.GetTrackerData(), self.writePath, self.sessionFileName)
        return

    def FilterEvent(self, event):
        # Exclusive filters drop an event if triggered
        for eventFilter in self.filters["ex"]:
            if (eventFilter.FilterEvent(event)):
                return True
        
        # Event must pass at least one inclusive filter if present
        if len(self.filters["in"]) > 0:
            for eventFilter in self.filters["in"]:
                if(eventFilter.FilterEvent(event)):
                    return False
            return True
        # Event passes if no inclusive filters are present
        return False

    def SetFilter(self, filterName, filterValue, filterMode):
        if self.filters.get(filterMode) == None:
            print("ERROR: invalid filter mode {0}".format(filterMode))
        self.filters[filterMode].append(EventFilter(filterName, filterValue))
        return
    def SetInverseFilter(self, filterName, filterValue, filterMode):
        if self.filters.get(filterMode) == None:
            print("ERROR: invalid filter mode {0}".format(filterMode))
            return
        self.filters[filterMode].append(InverseEventFilter(filterName, filterValue))
        return
    def SetOutfitWarsFilter(self):
        self.filters["ex"].append(DesolationZoneFilter())
        return
    def SetExpDescFilter(self, desc, filterMode):
        if filterMode == "in":
            self.filters["in"].append(InclusiveExperienceDescFilter(desc))
        else: self.filters["ex"].append(ExclusiveExperienceDescFilter(desc))
        return
    def SetExpIdFilter(self, id, filterMode):
        if filterMode == "in":
            self.filters["in"].append(InclusiveExperienceIdFilter(id))
        else: self.filters["ex"].append(ExclusiveExperienceIdFilter(id))
        return

    def __GenerateEventHash__(event):
        eventName = event["event_name"]
        timestamp = event["timestamp"]
        world_id = event.get("world_id")
        zone_id = event.get("zone_id")
        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")
        return "{0}{1}{2}{3}{4}{5}".format(eventName, timestamp, world_id, zone_id, charId, attackerId)


if __name__ == "__main__":
    # init manager
    manager = EventManagerPS2()
    members = DataFetcher.fetchOutfitMemberList("1703", True)
    for member in members:
        manager.AddTargetCharacter(member.get("id"), member.get("name"))
    manager.AddTargetCharacter("5428985062301712145", "deThreeVS")
    manager.AddTargetCharacter("5428977504197397649", "TaterKnight")

    # init websocket
    websocket_listener = PS2_WebSocket_Listener([manager.ReceiveEvent])
    websocket_listener.startListener(list(manager.targetChars.keys()), ["AchievementEarned","BattleRankUp","Death","ItemAdded","SkillAdded","VehicleDestroy","GainExperience","PlayerFacilityCapture","PlayerFacilityDefend"])