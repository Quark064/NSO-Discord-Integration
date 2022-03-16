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

TIMEOUT_WAIT = 20

def createRPC():
    rpc = Presence(CLIENT_KEY, pipe=0)
    rpc.connect()
    
    return rpc


def rpcManageChange(rpc, newState):
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

    config = openConfig()
    lastState = processResponse(config["userID"])

    while True:
        newState = processResponse(config["userID"])

        if lastState != newState:  
            rpcManageChange(rpc, newState)
        
        lastState = newState
        sleep(TIMEOUT_WAIT)


def findUserID(dict, ID):
        for num, entry in enumerate(dict['result']['friends']):
            if entry['id'] == ID:
                return num
        return -1


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
    stateMessage = ''


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

    if gameName in assetDict:
        gameID = assetDict[gameName]

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