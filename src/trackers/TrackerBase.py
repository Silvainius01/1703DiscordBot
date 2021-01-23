
from src.DataFetcher import *

class TrackedEventMetaData:
    def __init__(self):
        self.sundererKills = 0
        self.airVehicleKills = 0
        self.groundVehicleKills = 0
        self.vehicleKills = 0
        return

    def AddEvent(self, event):
        eventName = event.get("event_name")
        self.__GetMetaDataFunc__(event, eventName)
        return
    
    def __GetMetaDataFunc__(self, event, eventName):
        switch = {
            "VehicleKill" : self.__VehicleKill__
        }
        try:
            switch[eventName](event);
        except:
            return
        return
    def __VehicleKill__(self, event):
        vId = event.get("vehicle_id")
        self.vehicleKills += 1

        if VehicleMetaData.GetVehicleName(vId) == "Sunderer":
            self.sundererKills += 1
        if VehicleMetaData.IsGroundVehicle(vId):
            self.groundVehicleKills += 1
        elif VehicleMetaData.IsAirVehicle(vId):
            self.airVehicleKills += 1
        return

class ExpAggregate:
    def __init__(self, expId):
        self.expId = expId
        self.expTotal = 0
        self.expCount = 0
        # create entry for any unknown XP types (fucking Jeff and getting a 395)
        if not ExpMetaData.GetExp(expId):
            ExpMetaData.experienceDict[expId] = { 
                "experience_id": "{0}".format(expId),
                "description":"Unknown Exp Type {0}".format(expId),
                "xp": "0"
               }
        return
    
    def AddTick(self, amt:int):
        self.expTotal += amt
        self.expCount += 1
        return "{0}xp from {1}".format(amt, ExpMetaData.GetDesc(self.expId))
    
    def ToString(self):
        str = "{0} score from {2} counts of {1}".format(self.expTotal, ExpMetaData.GetExpDesc(self.expId), self.expCount)
        return

class TrackedDataBase:
    def __init__(self, id:str, data:dict):
        self.expDict = {}
        self.eventTypeDict = {}
        self.expTotal = 0
        self.id = id
        self.data = data
        self.name = self.__SetName__()
        self.metaData = TrackedEventMetaData()
        return

    def AddEvent(self, event):
        eventName = event.get("event_name")
        if eventName == None:
            return
        if eventName == "GainExperience":
            self.__AddExpTick__(event)
            return
        else:
            if eventName in self.eventTypeDict:
                self.eventTypeDict[eventName].append(event)
            else: self.eventTypeDict[eventName] = [event]
            self.__GeneralEventCallback__(event)
        self.metaData.AddEvent(event)
        return

    def ExpReportStr(self, mode:int):
        switch = {
            0: self.__FullReport__,
            1: self.__KillReport__
        }
        return switch[mode]()

    def __SetName__(self):
        return "No Name Given ({0})".format(self.id)

    def __AddExpTick__(self, event):
        expId = event.get("experience_id");

        if expId == None:
            return
        if not expId in self.expDict:
            self.expDict[expId] = ExpAggregate(expId)

        expAmt = int(event["amount"])
        self.expTotal += expAmt
        self.expDict[expId].AddTick(expAmt)
        self.__ExperienceGainCallback__(event)
        return

    def __FullReport__(self):
        retval = ["{0} earned {1} score from following sources: ".format(self.name, self.expTotal)]
        for exp in self.expDict.values():
            retval.append("\n\t- {0} ({1}%)".format(exp.ToString(), exp.expTotal/self.expTotal))
        return ''.join(retval)
    def __KillReport__(self):
        kills = self.eventTypeDict.get("Kill").count()
        deaths = self.eventTypeDict.get("Death").count()
        kd = "Infinity" if deaths == 0 else kills/deaths
        return "{0} - K: {1}  D: {2}  K/D: {3}".format(self.charName, kills, deaths, kd)

    def __ExperienceGainCallback__(self, event):
        print(event.get("event_name"))
        return
    def __GeneralEventCallback__(self, event):
        print(event.get("event_name"))
        return

class TrackerBase:
    def __init__(self):
        self.flags = { }
        self.defaultTrackedData = TrackedDataBase("-1", "DefaultTrackerIsBeingRun")

        # Reverse event names for easier data management. 
        self.death2kill = {
            "Death":"Kill",
            "VehicleDestroy":"VehicleKill"
        }
        self.death2teamKill = {
            "Death":"TeamKill",
            "VehicleDestroy":"TeamVehicleKill",
            "TeamVehicleKill" : "TeamVehicleKill",
            "TeamKill":"TeamKill"
        }
        self.death2suicide = {
            "Death" : "Suicide",
            "VehicleDestroy":"VehicleSuicide"
        }

        return

    def ProcessEvent(self, event):
        if self.__CanTrackEvent__(event):
            self.__AddEvent__(event)
            return True
        return False
    
    def AddTrackedObject(self, objData):
        if self.__CanTrackObject__(objData):
            self.__TrackObject__(objData)
            return True
        return False

    def GetTrackerData(self):
        return {}

    def GetMetaData(self):
        return {}

    def GetReverseEventName(self, event):
        eventName = event["event_name"] 
        charId = event.get("character_id")
        vfaction = event.get("faction_id")
        attackerId = event.get("attacker_character_id")

         # Suicide
        if attackerId == charId:
            return self.death2suicide.get(eventName, "_Suicide")
        # CharId of zero usually indicate vehicles that are killed with no one inside
        # Leading theory is that it's when a vehicle is destoryed but no one gets kill credit
        if charId == "0" and vfaction != None:
            if CharacterMetaData.GetCharFaction(attackerId) == vfaction:
                return self.death2teamKill.get(eventName, eventName+"_TeamKill")
            return self.death2kill.get(eventName, eventName+"_Kill")
        if CharacterMetaData.CharsOnSameTeam(charId, attackerId):
            return self.death2teamKill.get(eventName, eventName+"_TeamKill")
        return self.death2kill.get(eventName, eventName+"_Kill")

    def __CanTrackObject__(self, objData):
        return True

    def __TrackObject__(self, objData):
        return

    def __CanTrackEvent__(self, event):
        return True

    def __AddEvent__(self, event):
        self.defaultTrackedData.AddEvent(event)
        return