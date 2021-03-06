import json, requests


def callFGenAPI(idToken, guid, timeStamp, type):
    '''Passes flags into the Proprietary Android Emulator for KeyGen'''

    API_LINK = "https://flapg.com/ika2/api/login?public"

    hash = getElifeAPIHash(idToken, timeStamp)

    apiAppHead = {
			'x-token': idToken,
			'x-time':  str(timeStamp),
			'x-guid':  guid,
			'x-hash':  hash,
			'x-ver':   '3',
			'x-iid':   type
		}

    apiResponse = requests.get(API_LINK, headers=apiAppHead)
    key = json.loads(apiResponse.text)["result"]

    return key


def getElifeAPIHash(idToken, timeStamp):
    '''Fetches an authentication hash used to generate the Bearer Token.'''

    USER_AGENT = "NSO-DI/0.1.0"
    API_LINK = "https://elifessler.com/s2s/api/gen2"

    apiAppHead = { 'User-Agent': USER_AGENT }
    apiBody = { 'naIdToken': idToken, 'timestamp': timeStamp }
    
    apiResponse = requests.post(API_LINK, headers=apiAppHead, data=apiBody)
    
    hash = json.loads(apiResponse.text)["hash"]
    
    return hash