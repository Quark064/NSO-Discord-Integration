def log(msg, icon="default"):
    '''Logs a user message in a formatted manner.'''
    
    match icon:
        case "warning":
            icon = "!"
        case "question":
            icon = "?"
        case _:
            icon = "•"
        
    print(f"[{icon}] {msg}")