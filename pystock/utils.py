# Importations
from gardiens.utils import identifiant_processus

import threading as th

# Fonctions
def thread_identifiant():
    t = th.current_thread()
    
    if not hasattr(t, "cle"):
        t.cle = "{}-{:x}".format(identifiant_processus(), t.ident)
    
    return t.cle
