
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

    def __ExperienceGainCallback__(self, event):
        expId = event["experience_id"]
        desc = ExpAggregate.experienceDict[expId].get("description", "Unknown Experience Type "+ expId)
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
        if charId == None or self.untrackedChars.get(charId):
            return False
        outfitId = self.characterToOutfit.get(charId)
        if outfitId == None:
            return False
        return True

    def __AddEvent__(self, event):
        charId = event.get("character_id")
        outfitId = self.characterToOutfit.get(charId)
        self.trackedOutfits[outfitId].AddEvent(event)
        return