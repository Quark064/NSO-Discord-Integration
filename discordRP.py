from time import sleep
from pypresence import Presence
from coreAuth import getNSOVersion, getFriendJSON
from assetGames import getAssetDict
from fileIO import openConfig
from output import log
from sys import exit

CLIENT_KEY = 953323389844615208

NSO_VERSION = getNSOVersion()
USER_LANG = "en-US"

TIMEOUT_WAIT = 15   # Online presence is checked every 'TIMEOUT_WAIT' seconds

def createRPC():
    '''Creates and returns a RPC Presence class to update status.'''
    
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

    config = openConfig()
    lastState = ()

    while True:
        newState = processResponse(config["userID"])

        if lastState != newState:  
            rpcManageChange(rpc, newState)
        
        lastState = newState
        sleep(TIMEOUT_WAIT)


def findUserID(dict, ID):
    '''Takes the userID and finds their position in the Friend JSON.'''
    
    if ID == "":            # Temp solution, won't work if Nintendo Account has >1 friend.
        return 0
    
    for num, entry in enumerate(dict['result']['friends']):
        if entry['id'] == ID:
            return num
    return -1

def gameNameFormatter(name):
    '''Sanitizes game name strings for naming simplicity.'''
    TO_REMOVE = list(",.':")
    
    for char in TO_REMOVE:
        name = name.replace(char, "")
    return name.lower()

def processResponse(ID):
    '''Process a raw JSON response and returns a Tuple with the values.'''

    dict = getFriendJSON(NSO_VERSION, USER_LANG)
    assetDict = getAssetDict()
    userNum = findUserID(dict, ID)

    onlineState = None
    onlineSince = 0
    gameName = None
    totalPlayTime = 0
    sysDesc = None
    
    gameID = 'default'
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
        if cleanGameName in assetDict:
            gameID = assetDict[cleanGameName]

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