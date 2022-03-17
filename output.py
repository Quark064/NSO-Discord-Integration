def log(msg, icon="default", indent=0):
    '''Logs a user message in a formatted manner.'''
    
    match icon:
        case "warning":
            icon = "!"
        case "question":
            icon = "?"
        case _:
            icon = "•"
    
    message = []

    for _ in range(0, indent):
        message.append("    ")
    
    message.append(f"[{icon}] {msg}")
        
    print("".join(message))