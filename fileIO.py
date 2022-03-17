import json

PATH = "Persistant/config.json"

def createConfig():
    '''Creates a default, blank configuration file.'''

    dict = {
            "userID": 0,
            "sessionToken": "",
            "apiToken": "",
            "bearerToken": ""
        }
    
    writeConfig(dict)
    

def writeConfig(dict):
    '''Takes a dictionary and writes it to the configuration file.'''

    config = open(PATH, "w")
    config.write(json.dumps(dict, indent=4))
    config.close()


def openConfig():
    '''Opens the configuration file, creates one if it does not exist.'''
    
    try:
        jsonObj = open(PATH, "x")
        jsonObj.close()
        createConfig()
        jsonObj = open(PATH)
    
    except FileExistsError:
        jsonObj = open(PATH)
    
    return json.load(jsonObj)



