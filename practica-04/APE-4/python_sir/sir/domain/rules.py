def infection_probability(beta: float, infected: int, population: int) -> float:
    """Probabilidad de infección por susceptible en un paso."""
    return 1 - (1 - beta / population) ** infected
