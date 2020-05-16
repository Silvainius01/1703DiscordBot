import json
import sys
import time
import tkinter
import os
import datetime

from collections import namedtuple
from DataFetcher import *
from web_sock import *
from EventFilter import *
from TrackerBase import *

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open(filePath+"\\"+fileName, "w")
    dump_file.write(response_serialized)
    dump_file.close()
    return

class EventManagerPS2:
    def __init__(self):
        self.eventTypeDict = {
        "ContinentLock": [],
        "ContinentUnlock": [],
        "FacilityControl": [],
        "Metagame": [],
        }

        self.filters = {
            "ex" : [],
            "in" : []
        }

        self.tracker = TrackerBase()
        self.writeEnabled = True
        self.writeToDiskInterval = 50
        self.eventSinceWrite = 0
        self.writePath = "{0}\\tracker_sessions".format(os.path.dirname(os.path.abspath(__file__)))
        self.sessionFileName = "session_{0}.json".format(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
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
        if self.tracker.ProcessEvent(eventPayload):
            if self.writeEnabled:
                if self.eventSinceWrite > self.writeToDiskInterval:
                    print("")
                    data = self.tracker.GetTrackerData()
                    saveDataToDisk(data, self.writePath, self.sessionFileName)
                    self.eventSinceWrite = 0
                self.eventSinceWrite += 1
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