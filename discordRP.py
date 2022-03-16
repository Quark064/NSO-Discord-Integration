from time import sleep
from pypresence import Presence
from coreAuth import getNSOVersion, getFriendJSON
from assetGames import getAssetDict
from fileIO import openConfig
import os

CLIENT_KEY = 953323389844615208

NSO_VERSION = getNSOVersion()
USER_LANG = "en-US"

TIMEOUT_WAIT = 300

def createRPC():
    rpc = Presence(CLIENT_KEY, pipe=0)
    rpc.connect()
    
    return rpc


def updateLoop(rpc):

    config = openConfig()
    assetDict = getAssetDict()

    while True:
        
        valid, online, onlineState, onlineSince, gameName = processResponse(config["userID"])

        if not online:
            rpc.clear(pid=os.getpid())

        gameID = ''
        if gameName in assetDict:
            gameID = assetDict[gameName]
        else:
            gameID = 'default'
        
        if valid and online:
            rpc.update(
                    details = gameName,
                    state = onlineState,
                    start = onlineSince,
                    large_image = gameID,
                    large_text = gameName,
                    small_image = 'default',
                    small_text = 'NSO-DI'
                )

        sleep(TIMEOUT_WAIT)

def processResponse(ID):
    '''Process a raw JSON response and returns a Tuple with the values.'''

    dict = getFriendJSON(NSO_VERSION, USER_LANG)

    onlineState = ''
    onlineSince = 0
    gameName = ''
    totalPlayTime = 0
    sysDesc = ''

    stateMessage = ''

    def findUserID(dict, ID):
        for num, entry in enumerate(dict['result']['friends']):
            if entry['id'] == ID:
                return num
        
        return -1

    userNum = findUserID(dict, ID)

    if userNum < 0:
        return False, False, stateMessage, onlineSince, gameName

    try:
        onlineState = dict['result']['friends'][userNum]['presence']['state']
    except KeyError:
        pass

    try:
        onlineSince = dict['result']['friends'][userNum]['presence']['updatedAt']
    except KeyError:
       pass
    
    try:
        gameName = dict['result']['friends'][userNum]['presence']['game']['name']
    except KeyError:
        pass

    try:
        totalPlayTime = dict['result']['friends'][userNum]['presence']['game']['totalPlayTime']
    except KeyError:
        pass

    try:
        sysDesc = dict['result']['friends'][userNum]['presence']['game']['sysDescription']
    except KeyError:
        pass

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
        return False, True, stateMessage, onlineSince, gameName 


    return True, True, stateMessage, onlineSince, gameName