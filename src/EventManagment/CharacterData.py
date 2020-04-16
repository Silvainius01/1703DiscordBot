from PsPlayerEvents import *

class ExpAggregate:
    expName = "none"
    expTotal = 0
    expCount = 0

    def __init__(self, name:str):
        expName = name
        expTotal = 0
        expCount = 0
        return
    def AddTick(self, amt:int):
        expTotal += amt
        expCount += 1
        return

class CharacterData:
    expDict = {}
    charId = ""
    charName = ""
    eventTypeDict = {
        "AchievementEarned": [],
        "BattleRankUp": [],
        "Death": [],
        "GainExperience": [],
        "ItemAdded":[],
        "PlayerFacilityCapture": [],
        "PlayerFacilityDefend": [],
        "PlayerLogin": [],
        "PlayerLogout": [],
        "SkillAdded": [],
        "VehicleDestroy": [],
    }

    def __init__(self, id:str):
        self.charId = id
        self.charName = name
        #init all known experience types
        self.expDict["7"] = ExpAggregate("revive")
        return

    def AddExpTick(self, event:ExperienceGainEvent):
        if not event.experience_id in self.expDict:
            self.expDict[event.experience_id] = ExpAggregate(event.experience_id)
        self.expDict[event.experience_id].AddTick(event.amount)

    def AddEvent(self, event):
        if event.event_name == "GainExperience":
            self.AddExpTick(event)
        if event.event_name in self.eventTypeDict:
            self.eventTypeDict[event.event_name].append(event)
        else: print("Attemtped to add untracked event type: " + event.event_name)