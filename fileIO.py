import json

PATH = "Persistant/config.json"

def createConfig():
    dict = {
            "userID": 5103427393683456,
            "sessionToken": "",
            "apiToken": "",
            "bearerToken": ""
        }
    
    writeConfig(dict)
    

def writeConfig(dict):
    config = open(PATH, "w")
    config.write(json.dumps(dict, indent=4))
    config.close()


def openConfig():
    try:
        jsonObj = open(PATH, "x")
        jsonObj.close()
        createConfig()
        jsonObj = open(PATH)
    
    except FileExistsError:
        jsonObj = open(PATH)
    
    return json.load(jsonObj)



