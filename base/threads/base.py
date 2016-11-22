'''
Created on 12 mars 2015

@author: Julien
'''

from threading import Thread
from log.mixin import ThreadLogMixin

class BaseThread(Thread, ThreadLogMixin):
    '''
    Constitue la base d'un Thread
    '''
    
    # Méhtodes spéciales
    def __init__(self, *args, processus=None, **kwargs):
        '''
        Exécute le constructeur du parent.
        Si un argument processus est donné, on ajoute ce Thread au processus concerné.
        '''
        
        super(BaseThread, self).__init__(*args, **kwargs)
        
        self._processus = None
        self.processus = processus
    
    # Méthodes
    def start(self):
        if self.processus:
            if self.processus.etat == "en cours" and self.processus.etape == self._position:
                return super(BaseThread, self).start()
        
            raise RuntimeError("Ce Thread doit être lancé avec le processus associé !")
        
        return super(BaseThread, self).start()
    
    # Propriétés
    @property
    def processus(self):
        return self._processus
    
    @processus.setter
    def processus(self, processus):
        if processus != None:
            self._position = processus.ajouterThread(self)
            self._processus = processus
        
        elif self._processus != None:
            self._processus.enleverThread(self._position)
