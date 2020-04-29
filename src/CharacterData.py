
from DataFetcher import *

class ExpAggregate:
    experienceDict = DataFetcher.fetchExperienceDataDict(False)

    def __init__(self, expId):
        self.expId = expId
        self.expTotal = 0
        self.expCount = 0
        # create entry for any unknown XP types (fucking Jeff and getting a 395)
        if not experienceDict.get(expId):
            ExpAggregate.experienceDict[expId] = { 
                "experience_id": "{0}".format(expId),
                "description":"Unknown Exp Type {0}".format(expId),
                "xp": "0"
               }
        return
    
    def GetDescription(self):
        return ExpAggregate.experienceDict[self.expId]["description"]
    
    def AddTick(self, amt:int):
        self.expTotal += amt
        self.expCount += 1
        return "{0}xp from {1}".format(amt, self.GetDescription())
    
    def ToString(self):
        str = "{0} score from {2} counts of {1}".format(self.expTotal, self.GetDescription(), self.expCount)
        return

class CharacterData:
    def __init__(self, id:str, name:str):
        self.charId = id
        self.charName = name
        self.expDict = {}
        self.eventTypeDict = {}
        self.expTotal = 0
        return

    def AddExpTick(self, event):
        expId = event.get("experience_id");

        if expId == None:
            return
        if not expId in self.expDict:
            self.expDict[expId] = ExpAggregate(expId)

        expAmt = int(event["amount"])
        self.expTotal += expAmt
        self.expDict[expId].AddTick(expAmt)
        print("{0} gained {1}xp from {2}".format(self.charName,event["amount"],ExpAggregate.experienceDict[expId].get("description", "Unknown Experience Type "+ expId))
        return

    def AddEvent(self, event):
        eventName = event.get("event_name")
        if eventName == None:
            return
        if eventName == "GainExperience":
            self.AddExpTick(event)
            return
        elif eventName in self.eventTypeDict:
            self.eventTypeDict[eventName].append(event)
        else:
           self.eventTypeDict[eventName] = [event]
        print("{0} event: {1}".format(self.charName, eventName))
        return

    def ToString(self, mode:int):
        switch = {
            0: 0
        }
        return

    def __FullReport__(self):
        retval = ["{0} earned {1} score from following sources: ".format(self.charName, self.expTotal)]
        for exp in self.expDict.values():
            retval.append("\n\t- {0} ({1}%)".format(exp.ToString(), exp.expTotal/self.expTotal))
        return ''.join(retval)
    def __KillReport__(self):
        kills = self.eventTypeDict.get("Kill").count()
        deaths = self.eventTypeDict.get("Death").count()
        kd = "Infinity" if deaths == 0 else kills/deaths
        return "{0} - K: {1}  D: {2}  K/D: {3}".format(self.charName, kills, deaths, kd)