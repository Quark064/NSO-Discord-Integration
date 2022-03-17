# import threading
from discordRP import createRPC, updateLoop

def rpcThread():
    '''Call the Infinite Update loop to run in it's own thread.'''
    
    rpc = createRPC()
    updateLoop(rpc)

# rpcThreadObj = threading.Thread(target=rpcThread, name="RPC Update Loop")
# 
# rpcThreadObj.start()
# 
# print("Started the NSO-DI Service!")

if __name__ == "__main__":  # Threading to be implimented.
    rpcThread()