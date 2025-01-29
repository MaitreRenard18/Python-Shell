from colorama import Style


def frame_text(*args, title: str = None, color: str = None):
    if not args:
        args = ("")
    
    max_length = max(len(line) for line in args)
    
    if title:
        titre_length = len(title) + 2
        max_length = max(max_length, titre_length)
    
    if title:
        espace_gauche = (max_length - len(title)) // 2
        espace_droite = max_length - len(title) - espace_gauche
        
        bordure_haut = f"╭{'─' * espace_gauche} {title} {'─' * espace_droite}╮"
    else:
        bordure_haut = f"╭{'─' * (max_length + 2)}╮"
    
    if color:
        print(color + bordure_haut + Style.RESET_ALL)
    else:
        print(bordure_haut)
    
    for line in args:
        padded_line = line.ljust(max_length)
        if color:
            print(color + "│ " + Style.RESET_ALL + padded_line + color + " │" + Style.RESET_ALL)
        else:
            print(f"│ {padded_line} │")
    
    if color:
        print(color + f"╰{'─' * (max_length + 2)}╯" + Style.RESET_ALL)
    else:
        print(f"╰{'─' * (max_length + 2)}╯")