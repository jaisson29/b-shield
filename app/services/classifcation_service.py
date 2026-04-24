def calculate_irc_level(irc: float) -> str:
    if irc >= 8.5:
        return "Critico"
    if irc >= 6.5:
        return "Alto"
    if irc >= 4.0:
        return "Medio"
    return "Bajo"
