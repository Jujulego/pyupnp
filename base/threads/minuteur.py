'''
Created on 22 avr. 2015

@author: julien
'''

from datetime import datetime, timedelta
from threading import RLock, Timer

class Minuteur():
    '''
    Exécute "action" dans le temps donné.
    '''
    
    # Attributs
    _lock_liste = RLock()
    _minuteurs = []
    
    # Méthodes spéciales
    def __init__(self, action, *args, **kwargs):
        """
        Stocke l'action dans self.action, et lance un thread.Timer.
        """
        
        self.action = action
        self.args = args
        self.kwargs = kwargs
        
        self._etat = "terminé"
    
    def __repr__(self):
        texte = ""
        
        if self.etat == "en cours":
            texte = " ({})".format(str(self.timedelta))
        
        return "<Minuteur, {}{}>".format(self.etat, texte)
    
    # Méthodes
    def lancer(self, duree):
        if self.etat == "terminé":
            self._date_fin = datetime.now() + timedelta(seconds=duree)
            self._etat = "en cours"
            
            def action(*args, **kwargs):
                try:
                    resultat = self.action(*args, **kwargs)
                
                finally:
                    self._etat = "terminé"
                    self.__class__._minuteurs.remove(self)
                
                return resultat
            
            self._timer = Timer(self.duree, action, self.args, self.kwargs)
            self._timer.start()
            
            with self.__class__._lock_liste:
                self.__class__._minuteurs.append(self)
    
    def annuler(self):
        self._etat = "terminé"
        self.__class__._minuteurs.remove(self)
        
        return self._timer.cancel()
    
    # Méthodes de classe
    @classmethod
    def arreterMinuteurs(cls):
        """
        Execute annuler sur tout les minuteurs
        """
        
        while len(cls._minuteurs) > 0:
            for m in cls._minuteurs:
                m.annuler()
                del m
    
    # Propriétés
    @property
    def timedelta(self):
        return self._date_fin - datetime.now()
    
    @property
    def duree(self):
        return self.timedelta.total_seconds()
    
    @duree.setter
    def duree(self, nouv_duree):
        if self.etat == "en cours":
            self.annuler()
            
            self.lancer(nouv_duree)
    
    @property
    def etat(self):
        return self._etat