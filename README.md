# HEAVY WIP
This program aims to automate adding your Switch Online Presence to the Discord GameSDK automatically, allowing all of your Discord friends to see you online on your Switch.

## CURRENT STATUS:
* Found work-around to allow for your own online presence to be shown in the NSO application. ✅
* Repurposed the `splatnet2statink` repository to fetch your current online status in a JSON format. ✅
* Working PoC using `pypresence`! ✅

## TO-DO
* Figure out Python threading so the update loop can run independently from the (eventual) GUI.
* Error Checking.
* GUI
* Get permission to actually be using some of the API's and do proper crediting!!
* MAYBE'S (IDK IF THESE ARE POSSIBLE WITH PYTHON AND DEFINITLY WON'T WORK CROSS PLATFORM)
  * Tray Icon
  * Enable `npf71b963c1b7b6d119` redirection to avoid awkward copy-pasting of session keys.

## CREDITS
[eli](https://github.com/frozenpandaman): Wrote the `splatnet2statink` repo, which I unceremoniously stole and repurposed code from for authentication purposes; along with their hashing API.

[qwertyquerty](https://github.com/qwertyquerty): For the `pypresence` library that greatly simplified getting the PoC working.

# SETUP
*This is still in Alpha so the instructions are going to be pretty bare, and you will probably encounter a lot of fun crashes. I will be creating executables for more polished versions (unless I get help porting it to Electron or something) in the future.*

Due to the structure of the program, a secondary Nintendo Account is required. This allows for both detection of your online presence and ban protection (highly unlikely) against your main account.
* Create a new user account on your Switch.
* Create and link a Nintendo Account to it.
* Go to the Friend Settings of the new user and add your main account as a friend (via your Friend Code).

Requirements:
* Python >= 3.10
* Discord installed on your machine.
* Additional libraries:
  * `pip install bs4`
  * `pip install pypresence`

Setting Up
* Clone or download the repo.
* Run the `main.py` file and follow the directions to link the new Nintendo Account you created to the program.
  * Generated keys are stored in the `config.json` file and are only sent to Nintendo.
* Success!! If all went well, as long as you keep the program running, your Discord status will now reflect your Switch Online status. 
