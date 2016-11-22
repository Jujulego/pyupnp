# Exceptions :
class SSDPErreur(Exception):
    """
        Classe mère des exceptions autour du SSDP.
    """
    
    # Méthodes spéciales
    def __init__(self, message, requete):
        """
            Le paramètre message est passé au constructeur de Exception.
            Le paramètre requete est la requête qui pose problème.
        """
        self.requete = requete
        super(SSDPErreur, self).__init__(message)

class SSDPTypeErreur(SSDPErreur):
    """
        Pour les erreurs de types de requêtes SSDP.
    """
    pass
