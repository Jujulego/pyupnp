# Exceptions:
# Communication
class CommunicationErreur(Exception):
    pass

class ErreurDistante(CommunicationErreur):
    pass

class MD5CheckErreur(CommunicationErreur):
    pass

class RequeteInvalide(Exception):
    def __init__(self, requete, opts, notps):
        self.requete = requete
        self.opts    = opts
        self.nopts   = nopts

# Locks
class AntiDeadLock(Exception):
    pass

class VerrouilleErreur(Exception):
    pass
