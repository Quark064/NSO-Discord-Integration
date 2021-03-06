# Credit to Eli Fessler for base code.

import os, time
import requests, json, re
import base64, hashlib, uuid
from bs4 import BeautifulSoup

from apiFunc import callFGenAPI
from fileIO import openConfig, writeConfig
from output import log

session = requests.Session()

DEFAULT_NSO_VER = '2.0.0'

BLANK = ""

# FLOW PATH: Nintendo Session Code -> Nintendo Session Token ->
#            Web Service Token -> Bearer Token

def getNSOVersion():
    '''Fetches the current Nintendo Switch Online app version from the Google Play Store.'''
    
    PLAY_STORE_LISTING = "https://play.google.com/store/apps/details?id=com.nintendo.znca&hl=en"

    try:
        page = requests.get(PLAY_STORE_LISTING)
        soup = BeautifulSoup(page.text, 'html.parser')
        elts = soup.find_all("span", {"class": "htlgb"})
        ver = elts[7].get_text().strip()
        return ver
    except Exception:
        return DEFAULT_NSO_VER
   

def getNintendoSessionToken(nsoVersion):
    '''Gets a Nintendo Session Token.'''

    URL = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
    
    authState = base64.urlsafe_b64encode(os.urandom(36))

    authCodeVerifier = base64.urlsafe_b64encode(os.urandom(32)).replace(b"=", b"")
    authCVHash = hashlib.sha256()
    authCVHash.update(authCodeVerifier.replace(b"=", b""))
    authCodeChallenge = base64.urlsafe_b64encode(authCVHash.digest()).replace(b"=", b"")

    appHead = {
		'Host':                      'accounts.nintendo.com',
		'Connection':                'keep-alive',
		'Cache-Control':             'max-age=0',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent':                'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
		'Accept':                    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8n',
		'DNT':                       '1',
		'Accept-Encoding':           'gzip,deflate,br',
	}

    body = {
		'state':                                authState,
		'redirect_uri':                        'npf71b963c1b7b6d119://auth',
		'client_id':                           '71b963c1b7b6d119',
		'scope':                               'openid user user.birthday user.mii user.screenName',
		'response_type':                       'session_token_code',
		'session_token_code_challenge':         authCodeChallenge,
		'session_token_code_challenge_method': 'S256',
		'theme':                               'login_form'
	}

    response = session.get(URL, headers=appHead, params=body)
    specialLoginURL = response.history[0].url

    log("Copy/Paste this URL and sign in with your Alt Nintendo Account:\n")
    print(specialLoginURL)
    print("\n")
    
    log("Right-click the 'Select this account' button, copy the link, and paste it here.")
    
    while True:
        log("Please enter the right-clicked URL:\n", "question")
        userAccountURL = input()
        userAccountURL = userAccountURL.strip()
        print()
        if userAccountURL.startswith("npf71b963c1b7b6d119://auth#session_state="):
            break
        log("That doesn't appear to be a valid URL, please try again...", "warning")

    ninSessionCode = re.search('de=(.*)&', userAccountURL).group(1)
    ninServiceToken = ninSessionCodeToToken(nsoVersion, ninSessionCode, authCodeVerifier)
    
    return ninServiceToken


def ninSessionCodeToToken(nsoVersion, ninSessionCode, authCodeVerifier):
    '''Get the Web Service Token from the Nintendo Session Token'''

    URL = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
    
    appHead = {
		'User-Agent':      'OnlineLounge/{} NASDKAPI Android'.format(nsoVersion),
		'Accept-Language': 'en-US',
		'Accept':          'application/json',
		'Content-Type':    'application/x-www-form-urlencoded',
		'Content-Length':  '540',
		'Host':            'accounts.nintendo.com',
		'Connection':      'Keep-Alive',
		'Accept-Encoding': 'gzip'
	}

    body = {
		'client_id':                   '71b963c1b7b6d119',
		'session_token_code':           ninSessionCode,
		'session_token_code_verifier':  authCodeVerifier
	}

    response = session.post(URL, headers=appHead, data=body)
    ninSessionToken = json.loads(response.text)["session_token"]

    return ninSessionToken


def getAPIToken(nsoVersion, ninSessionToken, userLang):
    '''Takes a Session Token and generates an API token.'''

    URL = "https://accounts.nintendo.com/connect/1.0.0/api/token"

    appHead = {
		'Host':            'accounts.nintendo.com',
		'Accept-Encoding': 'gzip',
		'Content-Type':    'application/json; charset=utf-8',
		'Accept-Language':  userLang,
		'Content-Length':  '439',
		'Accept':          'application/json',
		'Connection':      'Keep-Alive',
		'User-Agent':      'OnlineLounge/{} NASDKAPI Android'.format(nsoVersion)
	}

    body = {
		'client_id':     '71b963c1b7b6d119', # Splatoon 2 Service
		'session_token':  ninSessionToken,
		'grant_type':    'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token'
	}

    request = requests.post(URL, headers=appHead, json=body)
    token = json.loads(request.text)
    
    return token["access_token"]


def getUserInfo(nsoVersion, apiToken, userLang):
    '''Takes an API Token and gathers user information for Bearer Token Generation.'''

    URL = "https://api.accounts.nintendo.com/2.0.0/users/me"

    appHead = {
			'User-Agent':      'OnlineLounge/{} NASDKAPI Android'.format(nsoVersion),
			'Accept-Language':  userLang,
			'Accept':          'application/json',
			'Authorization':   'Bearer {}'.format(apiToken),
			'Host':            'api.accounts.nintendo.com',
			'Connection':      'Keep-Alive',
			'Accept-Encoding': 'gzip'
		}
    
    response = requests.get(URL, headers=appHead)
    userInfo = json.loads(response.text)

    return userInfo


def getUserLogin(nsoVersion, apiToken, userInfo, userLang):
    '''Takes user information and an API token and uses external API's 
       to generate a Bearer Token to use to get Online Status.'''

    URL = "https://api-lp1.znc.srv.nintendo.net/v1/Account/Login"
    
    timeStamp = int(time.time())
    guid = str(uuid.uuid4())

    appHead = {
		'Host':             'api-lp1.znc.srv.nintendo.net',
		'Accept-Language':   userLang,
		'User-Agent':       'com.nintendo.znca/{} (Android/7.1.2)'.format(nsoVersion),
		'Accept':           'application/json',
		'X-ProductVersion':  nsoVersion,
		'Content-Type':     'application/json; charset=utf-8',
		'Connection':       'Keep-Alive',
		'Authorization':    'Bearer',
		'X-Platform':       'Android',
		'Accept-Encoding':  'gzip'
	}

    FGen = callFGenAPI(apiToken, guid, timeStamp, "nso")
    parameter = {
			'f':          FGen["f"],
			'naIdToken':  FGen["p1"],
			'timestamp':  FGen["p2"],
			'requestId':  FGen["p3"],
			'naCountry':  userInfo["country"],
			'naBirthday': userInfo["birthday"],
			'language':   userInfo["language"]
		}
    
    body = {"parameter": parameter}

    response = requests.post(URL, headers=appHead, json=body)
    bearerToken = json.loads(response.text)["result"]["webApiServerCredential"]["accessToken"]

    return bearerToken


def friendListRequest(nsoVersion, userLoginToken):
    '''Takes a Bearer Token and retrives the raw Friend List JSON.'''
     
    URL = "https://api-lp1.znc.srv.nintendo.net/v3/Friend/List"
     
    appHead = {
			'Host':             'api-lp1.znc.srv.nintendo.net',
			'User-Agent':       'com.nintendo.znca/{} (Android/7.1.2)'.format(nsoVersion),
			'Accept':           'application/json',
			'X-ProductVersion':  nsoVersion,
			'Content-Type':     'application/json; charset=utf-8',
			'Connection':       'Keep-Alive',
			'Authorization':    'Bearer {}'.format(userLoginToken),
			'Content-Length':   '37',
			'X-Platform':       'Android',
			'Accept-Encoding':  'gzip'
		}
    
    body = {"parameter": {}}

    response = requests.post(URL, headers=appHead, json=body)
    responseJSON = json.loads(response.text)

    if responseJSON['status'] != 0:
        raise Exception("Recieved an error from the Friend API!")

    return responseJSON

def genCycle(depth, nsoVersion, userLang):
    '''
    Manages Tokens and calls all of the other coreAuth methods to
    properly generate and replace expired keys.

    DEPTH 3 -> Regen all Tokens
    DEPTH 2 -> Regen API Token
    DEPTH 1 -> Regen Bearer Tokens

    '''
    
    config = openConfig()

    ninSessionToken = config["sessionToken"]
    apiToken = config["apiToken"]
    userLoginToken = config["bearerToken"]

    TOKEN_LIST = [ninSessionToken, apiToken, userLoginToken]

    for token in TOKEN_LIST:    # If one of the tokens is blank, regen all of them.
        if token == BLANK:
            depth = 3

    if depth >= 3:
        ninSessionToken = getNintendoSessionToken(nsoVersion)
        config["sessionToken"] = ninSessionToken
        log("Refreshed Session Token!")

    if depth >= 2:
        apiToken = getAPIToken(nsoVersion, ninSessionToken, userLang)
        config["apiToken"] = apiToken
        log("Refreshed API Token!")
    
    if depth >= 1:
        userInfo = getUserInfo(nsoVersion, apiToken, userLang)
        userLoginToken = getUserLogin(nsoVersion, apiToken, userInfo, userLang)
        config["bearerToken"] = userLoginToken
        log("Refreshed Bearer Token!")
    
    if depth >= 0:
        writeConfig(config)
        friendListJSON = friendListRequest(nsoVersion, userLoginToken)

    return friendListJSON


def getFriendJSON(nsoVersion, userLang):
    '''Handles API errors and calls 'genCycle()' with the right depth.'''

    try:                                                     # Recycle bearerToken
       return genCycle(0, nsoVersion, userLang)
    except Exception:
        try:                                                 # Recycle apiToken
            return genCycle(1, nsoVersion, userLang)
        except Exception:
            try:                                             # Recycle sessionToken
                return genCycle(2, nsoVersion, userLang)
            except Exception:
                try:                                         # Regen all tokens
                    return genCycle(3, nsoVersion, userLang)
                except Exception:
                    print("Couldn't refresh tokens!")