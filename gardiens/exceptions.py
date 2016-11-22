# Classes
class RequeteInvalide(Exception):
    # Méthodes spéciales
    def __init__(self, requete):
        self.args = (str(requete),)

class PasDeReponse(Exception):
    pass

class TropDeReponses(Exception):
    # Méthodes spéciales
    def __init__(self, nombre):
        self.args = ("Reçu {} requête{}".format(nombre, "s" if nombre > 1 else ""),)

class AdresseInvalideErreur(Exception):
    pass

class ErreurDistante(Exception):
    # Méthodes spéciales
    def __init__(self, message):
        self.message = message
