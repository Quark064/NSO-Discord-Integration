from discordRP import createRPC, updateLoop

def startLoop():
    '''Call the Infinite Update Loop.'''
    
    rpc = createRPC()
    updateLoop(rpc)

if __name__ == "__main__":
    startLoop()