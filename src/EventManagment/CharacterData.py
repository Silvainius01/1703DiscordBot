
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

    def AddExpTick(self, event):
        expId = event.get("experience_id");
        if expId == None:
            return

        if not expId in self.expDict:
            self.expDict[expId] = ExpAggregate(event.experience_id)
        self.expDict[expId].AddTick(event.amount)

    def AddEvent(self, event):
        eventName = event.get("event_name")
        if eventName == None:
            return
        if eventName == "GainExperience":
            self.AddExpTick(event)
        if eventName in self.eventTypeDict:
            self.eventTypeDict[eventName].append(event)
        else: print("Attemtped to add untracked event type: " + event.event_name)