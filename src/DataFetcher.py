import asyncio
import requests
import json
import os

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\testdata"
saveDirectoryOutfit = saveDirectory + "\\outfit"
saveDirectoryPlayer = saveDirectory + "\\player"
saveDirectoryDyZone = saveDirectory + "\\DynamicZone"

baseRequestUrl = "https://census.daybreakgames.com/s:17034223270/get/ps2:v2"

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open(filePath+"\\"+fileName, "w")
    dump_file.write(response_serialized)
    dump_file.close()
    return
def CharacterNameOrIdUrl(nameOrId:str, ext:str):
    try:
        int(nameOrId)
        return "{0}/character/?character_id={1}{2}".format(baseRequestUrl, nameOrId, ext)
    except ValueError:
        return "{0}/character/?name.first={1}{2}".format(baseRequestUrl, nameOrId, ext)

class DataFetcher:
    def fetchOutfitData(outfitTag:str, saveToDisk:bool):
        url = "{0}/outfit?alias={1}&c:resolve=member_character_name&c:resolve=member_online_status".format(baseRequestUrl, outfitTag)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                outfitData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(outfitData, saveDirectoryOutfit, outfitTag+".json")
                return {"status": True, "outfitData": outfitData.get("outfit_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchOutfitMemberList(outfitTag:str, saveToDisk:bool):
        response = DataFetcher.fetchOutfitData(outfitTag, False)
        if response.get("status") == True:
            memberList = []
            members = response.get("outfitData").get("members")
            for member in members:
                memberList.append({ "name": member["name"]["first"], "id" : member["character_id"] })
            if(saveToDisk):
                saveDataToDisk(memberList, saveDirectoryOutfit, outfitTag+"_members.json")
            return memberList
        else:
            print("Error fetching outift data: ")
            print(response.get("exception"))
        return response
            
    def fetchCharacterId(characterId:str, saveToDisk:bool):
        url = "{0}/character/?character_id={1}&c:resolve=outfit".format(baseRequestUrl, characterId)
        return DataFetcher.__fetchCharacter__(url, saveToDisk)
    def fetchCharacterName(characterName:str, saveToDisk:bool):
        url = "{0}/character/?name.first={1}&c:resolve=outfit".format(baseRequestUrl, characterName)
        return DataFetcher.__fetchCharacter__(url, saveToDisk)
    def __fetchCharacter__(url, saveToDisk:bool):
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                charData = json.loads(response_text).get("character_list")[0]
                if(saveToDisk):
                    charId = charData.get("character_id")
                    charName = charData.get("name").get("first")
                    saveDataToDisk(charData, saveDirectoryPlayer, "{0}_{1}.json".format(charName, charId))
                return {"status": True, "charData": charData }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchCharacterIdFaction(id:str):
        url = "{0}/character/?character_id={1}&c:show=faction_id".format(baseRequestUrl, id)
        return DataFetcher.__fetchCharacterFaction__(url)
    def fetchCharacterNameFaction(name:str):
        url = "{0}/character/?name.first={1}&c:show=faction_id".format(baseRequestUrl, nameOrId)
        return DataFetcher.__fetchCharacterFaction__(url)
    def __fetchCharacterFaction__(url):
        response = requests.get(url)
        if(response.status_code == 200):
            response_text = response.text
            factionId = json.loads(response_text).get("character_list")[0].get("faction_id")
            return {"status": True, "faction_id": factionId }
        return {"status":False}
    
    def fetchExperienceDataList(saveToDisk:bool):
        url = baseRequestUrl+"/experience?c:limit=999999"
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                expTypeData = json.loads(response_text)
                if(saveToDisk):
                    saveDataToDisk(outfitData, saveDirectory, "ExpTypes.json")
                return {"status": True, "experience_list": expTypeData.get("experience_list") }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}
    
    def fetchExperienceDataDict(saveToDisk:bool):
        expList = DataFetcher.fetchExperienceDataList(saveToDisk)
        if expList.get("status") == False:
            return expList
        expDict = {}
        expList = expList.get("experience_list")
        for expType in expList:
            expDict[expType.get("experience_id")] = expType
        return expDict

    def fetchDynamicZoneData(worldId:str, zoneId:str, saveToDisk:bool):
        url = "{0}/map/?world_id={1}&zone_ids={2}".format(baseRequestUrl, worldId, zoneId)
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                zoneData = json.loads(response_text)
                if zoneData.get("map_list").__len__() == 0:
                    return {"status":False}
                if(saveToDisk):
                    saveData = zoneData.get("map_list")[0]
                    saveDataToDisk(saveData, saveDirectory, "world{0}_{1}.json".format(worldId, zoneId))
                return {"status": True, "zoneData": zoneData.get("map_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def isDynamicZoneKoltyr(worldId:str, zoneId:str):
        zoneData = DataFetcher.fetchDynamicZoneData(worldId, zoneId, False)
        if zoneData.get("status") == True:
            isKoltyr = len(zoneData.get("zoneData").get("Regions").get("Row")) == 9
            return {"status":True, "isKoltyr":isKoltyr}
        return {"status":False}