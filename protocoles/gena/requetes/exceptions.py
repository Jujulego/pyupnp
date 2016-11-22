# Exceptions
class GENAErreur(Exception):
    # Méthodes spéciales
    def __init__(self, message, requete):
        self.message = message
        self.requete = requete
        
        self.args = (message,)
