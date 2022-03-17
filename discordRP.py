from time import sleep
from unidecode import unidecode
from pypresence import Presence
from coreAuth import getNSOVersion, getFriendJSON
from assetGames import getAssetDict
from fileIO import openConfig, writeConfig
from output import log
from sys import exit

CLIENT_KEY = 953323389844615208

NSO_VERSION = getNSOVersion()
USER_LANG = "en-US"
GAME_ASSET_DICT = getAssetDict()

TIMEOUT_WAIT = 16   # Online presence is checked every 'TIMEOUT_WAIT' seconds
                    # Discord only allows for RPC updates every 15 seconds.

def createRPC():
    '''Creates and returns a RPC Presence Class to update status.'''
    
    rpc = Presence(CLIENT_KEY, pipe=0)
    rpc.connect()
    
    return rpc


def rpcManageChange(rpc, newState):
    '''Updates the Discord Status when a change in online presence is detected.'''

    online, onlineState, onlineSince, gameName, gameID = newState
    
    if not online:
        rpc.clear()
        return
    
    rpc.update(
                details = gameName,
                state = onlineState,
                start = onlineSince,
                large_image = gameID,
                large_text = gameName,
                small_image = 'default',
                small_text = 'NSO-DI'
                )


def updateLoop(rpc):
    '''Loop that checks on the users online status every 'TIMEOUT_WAIT' seconds.'''

    lastState = ()
    log("Starting loop cycle!")

    while True:
        config = openConfig()
        newState = processResponse(config["userID"])

        if lastState != newState:
            rpcManageChange(rpc, newState)
        
        lastState = newState
        sleep(TIMEOUT_WAIT)


def findUserID(dict, ID):
    '''Takes the userID and finds their position in the Friend JSON.'''
    
    if ID == 0:     # If userID has not been configured yet.
        config = openConfig()
        max = 0
        log("No userID was found in the log file! Please enter the number next your your account below.", "warning")
        
        for num, entry in enumerate(dict['result']['friends']):
            log(f"{num+1}: {entry['name']}", indent=1)
            max += 1
        
        if max == 0:
            log("No friends were found linked to this Nintendo Account!", "warning")
            log("Add your main account as a friend and try again.")
            exit(1)
        else:
            print()
            log("If your name is not present, you have not friended your main account with your alt account yet.")
            log("If this is the case, please close the program and try again.\n")
        
        while True:
            ID = input("[?] Enter the number next to your account: ")
            if ID.isdigit():
                ID = int(ID)-1
                if ID >= 0 and ID < max:
                    break
            log("That was not a valid option! Try again...\n", "warning")
        
        ID = dict['result']['friends'][ID]['id']
        config['userID'] = ID
        writeConfig(config)
    
    for num, entry in enumerate(dict['result']['friends']):
        if entry['id'] == ID:
            return num
    return -1

def gameNameFormatter(name):
    '''Sanitizes game name strings for naming simplicity.'''
    TO_REMOVE = list(",.':")
    
    for char in TO_REMOVE:
        name = name.replace(char, "")
    return unidecode(name.lower())

def processResponse(ID):
    '''Process a raw JSON response and returns a Tuple with the values.'''

    dict = getFriendJSON(NSO_VERSION, USER_LANG)
    userNum = findUserID(dict, ID)

    onlineState = None
    onlineSince = 0
    gameName = None
    totalPlayTime = 0
    sysDesc = None
    
    gameID = 'unknown'
    stateMessage = None


    if userNum < 0:
        log("UserID is not valid!", "warning")
        exit(1)

    try:
        onlineState = dict['result']['friends'][userNum]['presence']['state']
        onlineSince = dict['result']['friends'][userNum]['presence']['updatedAt']
        gameName = dict['result']['friends'][userNum]['presence']['game']['name']
        totalPlayTime = dict['result']['friends'][userNum]['presence']['game']['totalPlayTime']
        sysDesc = dict['result']['friends'][userNum]['presence']['game']['sysDescription']
    except KeyError:
        pass
    
    if gameName != None:
        cleanGameName = gameNameFormatter(gameName)
        if cleanGameName in GAME_ASSET_DICT:
            gameID = GAME_ASSET_DICT[cleanGameName]

    if onlineState == 'ONLINE':
        if totalPlayTime != 0:
            stateMessage = "Played for {:,} hours".format(int(totalPlayTime/60))
        else:
            stateMessage = "Playing"
    
    elif onlineState == "PLAYING":
        if sysDesc != '':
            stateMessage = sysDesc
        else:
            stateMessage = "Playing"
    
    else:
        return False, stateMessage, onlineSince, gameName, gameID

    return True, stateMessage, onlineSince, gameName, gameID