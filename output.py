def log(msg, icon="deafult"):
    match icon:
        case "warning":
            icon = "!"
        case "question":
            icon = "?"
        case _:
            icon = "•"
        
    print(f"[{icon}] {msg}")