import json

PATH = "Persistant/config.json"

def createConfig():
    dict = {
            "userID": 0,
            "apiToken": ""
        }
    
    writeConfig(dict)
    

def writeConfig(dict):
    config = open(PATH, "w")
    config.write(json.dumps(dict))
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



