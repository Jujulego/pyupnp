'''
Created on 11 mars 2015

@author: Julien
'''

class Processus():
    '''
    Enregistre une suite de Threads, à executer dans un ordre précis.
    '''
    
    # Méthodes spéciales
    def __init__(self, nom, sync=True, daemon=False):
        '''
        Défini les options, et construit la base de l'objet.
        
        L'option sync, signifie que les threads seront lancés les uns après les autres si mise à True, sinon, ils seront lancés simultanément.
        '''
        
        self._etat = "non lancé"
        self._etape = 0
        self._threads = []
        
        self._nom = nom
        self._daemon = daemon
        self._sync = sync
    
    def __repr__(self):
        return "<Processus {} {} (étape {:d}/{:d})>".format(self.nom, self.etat, self.etape, len(self._threads))
    
    # Méthodes
    # Gestion des Threads
    def ajouterThread(self, thread, position=-1):
        """
        Ajoute un Thread dans la liste, à une position donnée.
        Par défaut, l'ajoute à la fin de la liste.
        """
        
        thread.name += " (Processus {})".format(self.nom)
        thread._processus = self
        
        if position == -1:
            self._threads.append(thread)
            thread._position = len(self._threads)
            return len(self.threads)-1
        
        self._threads.insert(position, thread)
        thread._position = position+1
        return position
    
    def recupererThread(self, position):
        """
        Renvoie le Thread de la position donnée
        """
        
        return self._threads[position]
    
    def enleverThread(self, position):
        """
        Enlève le Thread, à la position donnée
        """
        
        thread = self._threads.pop(position)
        thread._processus = None
    
    # Gestion du processus
    def lancer(self):
        """
        Lance le processus
        """
        
        self._etat = "en cours"
        self._etape = 0
        
        for t in self._threads:
            self._etape += 1
            t.start()
            
            if self.sync or self.etape == len(self._threads):
                t.join()
        
        self._etat = "terminé"
    
    # Propriétés
    # Etat :
    @property
    def etat(self):
        return self._etat
    
    # Etape :
    @property
    def etape(self):
        return self._etape
    
    # Threads :
    @property
    def threads(self):
        return self._threads
    
    # Nom :
    @property
    def nom(self):
        return self._nom
    
    @nom.setter
    def nom(self, nom):
        if not self.etat == "non lancé":
            self._nom = nom
    
    # Daemon
    @property
    def daemon(self):
        return self._daemon
    
    @daemon.setter
    def daemon(self, daemon):
        if not self.etat == "non lancé":
            self._daemon = daemon
    
    # Daemon
    @property
    def sync(self):
        return self._sync
    
    @sync.setter
    def sync(self, sync):
        if not self.etat == "non lancé":
            self._sync = sync
