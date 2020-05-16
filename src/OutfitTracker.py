
from TrackerBase import *
from CharacterTracker import *
from DataFetcher import *

class TrackedOutfitData(TrackedDataBase):
    def __init__(self, id, data):
        self.tag = data.get("alias")
        self.charTracker = CharacterTracker(False)
        return super().__init__(id, data)

    def __SetName__(self):
        return self.data.get("name")

    def AddEvent(self, event):
        self.charTracker.ProcessEvent(event)
        super().AddEvent(event)
        return

    def ContainsChar(self, charId):
        return self.charTracker.trackedChars.get(charId) != None

    def BasicTeamStats(self):
        stats = {
            "tag": self.tag,
            "name": self.name,
            "kills": len(self.eventTypeDict.get("Kill", {})),
            "deaths": 0,
            "revives": self.__GetExpCount__("7"),
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
        self.characterToOutfit = {}
        self.untrackedChars = {}
        return super().__init__()

    def GetBasicTeamStats(self):
        statsList = []
        for id in self.trackedOutfits:
            outfit = self.trackedOutfits[id]
            statsList.append(outfit.BasicTeamStats())
        return statsList;

    def GetTrackerData(self):
        return self.GetBasicTeamStats()

    def __CanTrackObject__(self, objData):
        return objData.get("outfit_id") != None

    def __TrackObject__(self, objData):
        outfitId = objData.get("outfit_id")
        self.trackedOutfits[outfitId] = TrackedOutfitData(outfitId, objData)
        for member in objData.get("members"):
            charId = member.get("character_id")
            self.trackedOutfits[outfitId].charTracker.AddTrackedObject(member)
            self.characterToOutfit[charId] = outfitId
        return

    def __CanTrackEvent__(self, event):
        charId = event.get("character_id")
        if charId == None:
            return False

        outfitId = self.characterToOutfit.get(charId)
        attackerId = event.get("attacker_character_id")
        attackerOutfitId = self.characterToOutfit.get(attackerId) if attackerId != None else None
        if outfitId == None and attackerOutfitId == None:
            return False
        return True

    def __AddEvent__(self, event):
        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")
        outfitId = self.characterToOutfit.get(charId)

        if outfitId != None:
            self.trackedOutfits[outfitId].AddEvent(event)
        if attackerId != None and attackerId != charId:
            attackerOutfitId = self.characterToOutfit.get(attackerId)
            if attackerOutfitId != None:
                self.trackedOutfits[attackerOutfitId].AddEvent(event)
        return