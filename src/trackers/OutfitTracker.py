
from src.DataFetcher import *
from src.PsEventManager import *
from src.EventFilter import *
from src.trackers.TrackerBase import *
from src.trackers.CharacterTracker import *

class TrackedOutfitData(TrackedDataBase):
    def __init__(self, id, data):
        self.tag = data.get("alias")
        return super().__init__(id, data)

    def __SetName__(self):
        return self.data.get("name")

    def AddEvent(self, event):
        super().AddEvent(event)
        return

    def BasicTeamStats(self):
        stats = {
            "tag": self.tag,
            "name": self.name,
            "kills": len(self.eventTypeDict.get("Kill", {})),
            "deaths": 0,
            "revives": self.__GetExpCount__("7") + self.__GetExpCount__("53"),
            "airkills": self.metaData.airVehicleKills,
            "sundykills": self.metaData.sundererKills,
            "vehiclekills": self.metaData.groundVehicleKills - self.metaData.sundererKills,
            "cortiumharvest": self.__GetExpCount__("674"),
            "repair": 0
        }

        count = len(self.eventTypeDict.get("Death", {})) + len(self.eventTypeDict.get("Suicide", {})) + len(self.eventTypeDict.get("TeamKill", {}))
        stats["deaths"] = count

        for expId in ExpMetaData.experienceTypes["AllRepairs"]:
            stats["repair"] += self.__GetExpCount__(expId)
        return stats

    def __GetExpCount__(self, expId):
        temp = self.expDict.get(expId)
        return temp.expCount if temp != None else 0

    def __ExperienceGainCallback__(self, event):
        expId = event["experience_id"]
        desc = ExpMetaData.GetDesc(expId)
        print("[{0}] {2}: {1} score generated".format(self.tag,event["amount"],desc))
        return
    def __GeneralEventCallback__(self, event):
        print("[{0}] event: {1}".format(self.tag, event["event_name"]))
        return

class OutfitTracker(TrackerBase):
    def __init__(self):
        self.trackedOutfits = {}
        self.untrackedChars = {}
        self.char2outfit = {}
        self.charTracker = CharacterTracker(False)
        return super().__init__()

    def GetBasicTeamStats(self):
        statsList = []
        for id in self.trackedOutfits:
            outfit = self.trackedOutfits[id]
            statsList.append(outfit.BasicTeamStats())
        return statsList;

    def GetTrackerData(self):
        return self.GetBasicTeamStats()

    def GetCharacterOutfit(self, charId):
        return CharacterMetaData.GetCharOutfitId(charId)

    def __CanTrackObject__(self, objData):
        try:
            objData["outfit_id"]
            objData["members"]
            return True
        except KeyError:
            return False

    def __TrackObject__(self, objData):
        outfitId = objData.get("outfit_id")
        
        if self.IsTrackedOutfit(outfitId):
            return

        self.trackedOutfits[outfitId] = TrackedOutfitData(outfitId, objData)
        for member in objData.get("members"):
            charId = member.get("character_id")
            self.charTracker.AddTrackedObject(member)
            self.char2outfit[charId] = outfitId
        return

    def __CanTrackEvent__(self, event):
        charId = event.get("character_id")
        if charId == None:
            return False

        outfitId = self.GetCharacterOutfit(charId)
        attackerId = event.get("attacker_character_id")
        attackerOutfitId = self.GetCharacterOutfit(attackerId) if attackerId != None else None
        return self.IsTrackedOutfit(outfitId) or self.IsTrackedOutfit(attackerOutfitId)

    def IsTrackedOutfit(self, id):
        try:
            self.trackedOutfits[id]
            return True
        except KeyError:
            return False

    def __AddEvent__(self, event_real):
        event = event_real.copy()
        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")
        outfitId = self.GetCharacterOutfit(charId)

        # Add event for chars
        self.charTracker.ProcessEvent(event_real)

        # Add event to defender/main char's outfit
        if self.IsTrackedOutfit(outfitId):
            self.trackedOutfits[outfitId].AddEvent(event)
        # add event to attacker's outfit, if it is tracked
        if attackerId != None and attackerId != charId:
            attackerOutfitId = self.GetCharacterOutfit(attackerId)
            if self.IsTrackedOutfit(attackerOutfitId):
                event["event_name"] = self.GetReverseEventName(event)
                self.trackedOutfits[attackerOutfitId].AddEvent(event)
        return