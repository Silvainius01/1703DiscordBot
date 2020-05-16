
from TrackerBase import *
from DataFetcher import *

class TrackedCharacterData(TrackedDataBase):
    def __init__(self, id, data, allowPrinting = True):
        self.allowPrinting = allowPrinting
        return super().__init__(id, data)

    def __SetName__(self):
        return self.data.get("name", {}).get("first", "!!NO NAME FOUND!!")

    def GetOutfitData(self):
        return charData.get("outfit")

    def GetFaction(self):
        return self.data.get("faction_id")

    def __ExperienceGainCallback__(self, event):
        if self.allowPrinting:
            expId = event["experience_id"]
            print("{0} gained {1} score from {2}".format(self.name,event["amount"],ExpAggregate.GetExpDesc(expId)))
        return
    def __GeneralEventCallback__(self, event):
        if self.allowPrinting:
            print("{0} event: {1}".format(self.name, event["event_name"]))
        return

class CharacterTracker(TrackerBase):
    charFactionMap = {
        "0" : "-1"
    }

    def __init__(self, allowPrinting = True):
        self.allowPrinting = allowPrinting
        self.targetChars = { }
        self.trackedChars = { }
        # Dict for hashes of events where two tracked chars interacted with each other. Involved in duplicate event prevention.
        self.multiCharEvents = { }
        # Reversal names for easier data management. 
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
        return super().__init__()

    def ProcessCharacterEvent(self, event):
        """
            Processes an event about a character. Will ignore events about non-target characters, and automatically handles tracking and untracking players.
        """
        charId = event["character_id"]
        eventName = event["event_name"]

        if self.IsTargetCharacter(charId):
            self.__StartTrackingCharacter__(charId)

        # If this is a kill event, determine if a tracked character was killed.
        if event.get("attacker_character_id"):
            vfaction = event.get("faction_id")
            attackerId = event["attacker_character_id"]

            # If it's a suicide
            if attackerId == charId:
                event["event_name"] = self.death2suicide.get(eventName, "_Suicide")
            # If the killed player is not tracked, flip name of event accordingly
            elif not self.IsTargetCharacter(charId):
                # If it a vehicle is killed and no one was in it
                if charId == "0" and vfaction != None:
                    if self.GetCharIdFaction(attackerId) == vfaction:
                        event["event_name"] = self.death2teamKill.get(eventName, eventName+"_TeamKill")
                    else: event["event_name"] = self.death2kill.get(eventName, eventName+"_Kill")
                elif self.CharsOnSameTeam(charId, attackerId):
                    event["event_name"] = self.death2teamKill.get(eventName, eventName+"_TeamKill")
                else: event["event_name"] = self.death2kill.get(eventName, eventName+"_Kill")
                charId = attackerId
            # If this is a multi-char event, process accordingly.
            elif self.IsTargetCharacter(attackerId):
                self.__StartTrackingCharacter__(attackerId)
                self.ProcessMultiCharEvent(event)
                return

        if not self.IsTrackedCharacter(charId):
            return # If the character is not a target char, ignore event.
        self.trackedChars[charId].AddEvent(event)
        return

    def ProcessMultiCharEvent(self, event):
        """
            Processes an event in which two tracked chars interact with other
        """
        charId = event["character_id"]
        attackerId = event["attacker_character_id"]
        eventName = event["event_name"]

        # Add event for defender as normal
        self.trackedChars[charId].AddEvent(event)

        # Reverse event name for attacker, then add
        if self.CharsOnSameTeam(charId, attackerId):
            event["event_name"] = self.death2teamKill.get(eventName, eventName+"_TeamKill")
        else: event["event_name"] = self.death2kill.get(eventName, eventName+"_Kill")
        self.trackedChars[attackerId].AddEvent(event)
        return

    def __AddTargetCharacter__(self, objData):
        """
            Tells the Manager to keep a look out for events from these characters.
        """
        charId = objData.get("character_id")
        charName = objData.get("name", {}).get("first", "!!NO NAME FOUND!!")
        self.targetChars[charId] = charName
        print("Added target char {0} with id {1}".format(charId, charName))
        return

    def __StartTrackingCharacter__(self, charId):
        if self.IsTrackedCharacter(charId):
            return False
        charName = self.targetChars.pop(charId)
        charData = DataFetcher.fetchCharacterId(charId, False)
        if(charData.get("status") == False):
           return False
        charData = charData.get("charData")
        self.trackedChars[charId] = TrackedCharacterData(charId, charData, self.allowPrinting)
        CharacterTracker.charFactionMap[charId] = self.GetCharIdFaction(charId)
        print("Began tracking {0}".format(charName))
        return True

    def CharsOnSameTeam(self, char1Id, char2Id):
        return self.GetCharIdFaction(char1Id) == self.GetCharIdFaction(char2Id)
    def GetCharIdFaction(self, id):
        if self.IsTrackedCharacter(id):
            return self.trackedChars[id].GetFaction()

        factionId = CharacterTracker.charFactionMap.get(id)
        if factionId == None:
            # Register character faction if not found
            factionId = DataFetcher.fetchCharacterIdFaction(id)
            if factionId.get("status"):
                factionId = factionId.get("faction_id")
                CharacterTracker.charFactionMap[id] = factionId
            return "-1";
        return factionId

    def IsTrackedCharacter(self, characterId):
        return self.trackedChars.get(characterId) != None
    def IsTargetCharacter(self, characterId):
        return self.targetChars.get(characterId) != None or self.IsTrackedCharacter(characterId)

    def __CanTrackObject__(self, objData):
        return objData.get("character_id") != None

    def __TrackObject__(self, objData):
        self.__AddTargetCharacter__(objData)
        return

    def __CanTrackEvent__(self, event):
        return event.get("character_id") != None

    def __AddEvent__(self, event):
        self.ProcessCharacterEvent(event)
        return