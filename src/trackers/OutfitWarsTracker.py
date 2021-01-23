

from src.DataFetcher import *
from src.PsEventManager import *
from src.EventFilter import *
from src.trackers.OutfitTracker import *

baseBracketDict = {
    "id": -1,
    "name": "Invalid Bracket",
    "outfits": {}, #"id": {"id": "0", "tag": "", "name":"NO NAME", "faction":"0"}
    "characters": {}, #"id": {"id": "0", "name":"NO NAME", "outfit": "", "faction":"0"}
    "desolationInstance": "0"
}

def KeyInDict(key, dict):
    try: 
        dict[key]
        return True
    except: 
        return False
    return False

class OutfitWarsTrackedData(TrackedDataBase):
    def __init__(self, bracketId, bracketName):
        data = {
            "bracketId": bracketId,
            "bracketName": bracketName,
            "outfits": {},
            "characters": {},
            "desolationInstance": "0"
        }
        return super().__init__(bracketId, data)

    def AddOutfit(self, outfitData):
        outfitId = outfitData["outfit_id"]
        self.data["outfits"][outfitId] = OutfitWarsTrackedData.__CreateOutfitData__(outfitData)
        return

    def AddCharacter(self, charId):
        data = OutfitWarsTrackedData.__CreateCharacterData__(charId)
        if data != None:
            self.data["characters"][charId] = data
        return

    def SetDesolationId(self, desoId):
        self.data["desolationInstance"] = desoId
        return

    def __CreateOutfitData__(outfit):
        data = {
            "id": outfit.get("outfit_id"), 
            "tag": outfit.get("alias"), 
            "name":outfit.get("name"), 
            "faction": OutfitMetaData.GetOutfitFaction(outfit["outfit_id"])
        }
        return data
    def __CreateCharacterData__(id):
        char = CharacterMetaData.GetChar(id)

        if char.get("character_id") == None:
            return None

        data = {
            "id": char["character_id"],
            "name":char["name"]["first"],
            "faction": char["faction_id"]
        }
        return data

class OutfitWarsTracker(OutfitTracker):
    def __init__(self):
        self.testMode = True
        self.desolationFilter = None
        self.outfitBracketMap = { }
        self.bracketOutfitMap = { }
        self.zoneToBracket = { }

        self.trackedData = [OutfitWarsTrackedData(0, "Gold"), OutfitWarsTrackedData(1, "Silver"), OutfitWarsTrackedData(2, "Bronze")]

        for f in EventManagerPS2.instance.filters:
            if type(f) is DesolationZoneFilter:
                self.desolationFilter = f
                self.testMode = False
                break

        if self.testMode:
            self.desolationFilter = DesolationZoneFilter()

        return super().__init__()

    def __CanTrackEvent__(self, event):
        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")
        faction = event.get("faction_id")

        # Observer cams are in the NS faction, so any event with an NS char is invalid
        if faction == '4':
            return False
        if charId != None and charId != '0' and CharacterMetaData.GetCharFaction(charId) == '4':
            return False
        if attackerId != None and attackerId != '0' and CharacterMetaData.GetCharFaction(attackerId) == '4':
            return False
        return super().__CanTrackEvent__(event)

    def __AddEvent__(self, event):
        # Add zone to the correct bracket
        zoneId = event.get("zone_id")
        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")

        bracket = self.zoneToBracket.get(zoneId)
        if bracket == None:
            outfit = CharacterMetaData.GetCharOutfitId(charId)
            attackerOutfit = CharacterMetaData.GetCharOutfitId(attackerId)
            bracket = self.outfitBracketMap.get(outfit, self.outfitBracketMap.get(attackerOutfit))
            if bracket != None:
                if not self.testMode:
                    self.zoneToBracket[zoneId] = bracket
            else: return

        charId = event.get("character_id")
        attackerId = event.get("attacker_character_id")
        bracketData = self.trackedData[bracket]
        
        if charId != None:
            try: self.trackedData[bracket]["characters"][charId]
            except: self.trackedData[bracket].AddCharacter(charId)
        if attackerId != None:
            try: self.trackedData[bracket]["characters"][attackerId]
            except: self.trackedData[bracket].AddCharacter(attackerId)

        return super().__AddEvent__(event)

    def __TrackObject__(self, objData):
        super().__TrackObject__(objData)
        outfitId = objData["outfit_id"]
        bracket = (len(self.trackedOutfits) - 1) // 3 
        self.outfitBracketMap[outfitId] = bracket

        if self.bracketOutfitMap.get(bracket) == None:
            self.bracketOutfitMap[bracket] = [outfitId]
        else: self.bracketOutfitMap.get(bracket).append(outfitId)

        bracketData = self.trackedData[bracket]
        bracketData.AddOutfit(objData)
        return

    def GetOutfitBracket(self, outfitId):
        return self.outfitBracketMap.get(outfitId, 3)

    def GetMetaData(self):
        arr = []
        for b in self.trackedData:
            arr.append(b.data)
        return arr

# Only able to reconstruct accurately if:
#   - Events from same server (world_id)
#   - Event logs are from only desolation
#   - Matches were staggered Gold -> Silver -> Bronze
#   - Events from the three deso instances appear in correct order
class RetroactiveOutfitWarsTracker(OutfitWarsTracker):
    def __init__(self):
        self.desoBrackets = {}
        self.factionOverride = {}
        self.currEvent = None
        self.retryEvents = []
        return super().__init__()

    def GetCharacterOutfit(self, charId):
        event = self.currEvent
        eventZone = self.currEvent.get("zone_id")
        bracket = self.zoneToBracket.get(eventZone, 0)
        faction = self.factionOverride.get(charId, CharacterMetaData.GetCharFaction(charId))

        if event["event_name"] == "VehicleDestroy" and charId != '0' and charId == event["character_id"]:
            # This should handle deleted or invalid characters.
            # Sadly, only way to get this info is from vkill events.
            if faction == '0' or faction == None:
                self.factionOverride[charId] = faction
            faction = event["faction_id"]

        for outfit in self.bracketOutfitMap.get(bracket, []):
            if OutfitMetaData.GetOutfitFaction(outfit) == faction:
                return outfit
        return super().GetCharacterOutfit(charId)

    def __CanTrackEvent__(self, event):
        charId = event.get("character_id")
        faction = event.get("faction_id")
        if charId == None:
            return False
        # Filter out OBS cams!
        if faction == '4' or CharacterMetaData.GetCharFaction(charId) == '4':
            return False
        return True

    def __AddEvent__(self, event):
        desoId = event.get("zone_id")
        count = len(self.bracketOutfitMap)
        if count < 3:
            self.bracketOutfitMap[desoId] = count
        self.currEvent = event
        return super().__AddEvent__(event)
