
from .TrackerBase import *
from .CharacterTracker import *
from .OutfitTracker import *
from .DataFetcher import *
from .PsEventManager import *
from .EventFilter import *

class OutfitWarsTrackedData(TrackedDataBase):
    def __init__(self, id, data):
        return super().__init__(id, data)

class OutfitWarsTracker(OutfitTracker):
    def __init__(self):
        self.desolationFilter = DesolationZoneFilter()
        self.outfitZoneMap = { }
        self.outfitBracketMap = { }

        for f in EventManagerPS2.instance.filters:
            if type(f) is DesolationZoneFilter:
                self.desolationFilter = f
                break

        return super().__init__()

    def __TrackObject__(self, objData):
        super().__TrackObject__(objData)
        bracket = (len(self.trackedOutfits) - 1) // 3 
        self.outfitBracketMap[objData["outfit_id"]] = bracket

    def GetOutfitBracket(self, outfitId):
        return self.outfitBracketMap.get(outfitId, 3)

    def ReconstructOutfit(self, charId, zoneId):
        factionId = CharacterMetaData.GetCharIdFaction(id)
        if factionId == "-1": return None

        return

