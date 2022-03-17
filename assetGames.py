import requests
import json
from output import log

GAME_JSON_LINK = "https://api.npoint.io/cb0cfc91e62a756f6a75"

FALLBACK_DICT = {
    "splatoon 2": "splatoon2",
    "mario kart 8 deluxe": "mk8d",
    "fortnite": "fortnite",
    "animal crossing new horizions": "acnh",
    "luigis mansion 3": "lm3",
    "super mario maker 2": "smm2",
    "super mario odyssey": "smo",
    "super smash bros ultimate": "ssbu",
    "the legend of zelda breath of the wild": "botw",
    "youtube": "youtube",
    "paper mario the origami king": "pmtko"
}

def getAssetDict():
    '''Returns the asset dictionary.'''
    
    try:
        gameDict = requests.get(GAME_JSON_LINK)
        return json.loads(gameDict.text)
    except Exception:
        log("Failed to pull updated game list from the server! Using fallback list...", "warning")
        return FALLBACK_DICT