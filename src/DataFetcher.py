import asyncio
import requests
import json
import os

saveDirectory = os.path.dirname(os.path.abspath(__file__)) + "\\testdata"
saveDirectoryOutfit = saveDirectory + "\\outfit"
saveDirectoryPlayer = saveDirectory + "\\player"

baseRequestUrl = "https://census.daybreakgames.com/s:17034223270/get/ps2:v2"

def saveDataToDisk(data, filePath:str, fileName:str):
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    response_serialized = json.dumps(data)
    dump_file = open(filePath+"\\"+fileName, "w")
    dump_file.write(response_serialized)
    dump_file.close()

class DataFetcher:
    def fetchOutfitData(outfitTag:str, saveToDisk:bool):
        url = baseRequestUrl+"/outfit?alias="+outfitTag+"&c:resolve=member_character_name&c:resolve=member_online_status"
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
        url = baseRequestUrl + "/character/?character_id=" + characterId
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                charData = json.loads(response_text)
                if(saveToDisk):
                    charName = charData.get("character_list")[0].get("name").get("first")
                    saveDataToDisk(outfitData, saveDirectoryPlayer, "{0}_{1}.json".format(charName, characterId))
                return {"status": True, "charData": charData.get("character_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
        return {"status":False}

    def fetchCharacterName(characterName:str, saveToDisk:bool):
        url = baseRequestUrl + "/character/?name.first=" + characterName
        response = requests.get(url)
        try:
            if(response.status_code == 200):
                response_text = response.text
                charData = json.loads(response_text)
                if(saveToDisk):
                    charId = charData.get("character_list")[0].get("character_id")
                    saveDataToDisk(charData, saveDirectoryPlayer, "{0}_{1}.json".format(characterName, charId))
                return {"status": True, "charData": charData.get("character_list")[0] }
            else:
                raise Exception("Bad status code from request!")
        except Exception as exc:
            return {"status": False, "print": True, "exception": exc}
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

