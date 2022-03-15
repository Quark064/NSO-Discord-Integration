# import threading
from discordRP import createRPC, updateLoop

def rpcThread():
    rpc = createRPC()
    updateLoop(rpc)

# rpcThreadObj = threading.Thread(target=rpcThread, name="RPC Update Loop")
# 
# rpcThreadObj.start()
# 
# print("Started the NSO-DI Service!")

rpcThread()