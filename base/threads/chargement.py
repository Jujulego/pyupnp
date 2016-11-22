# Importations
from base.wrapper import ThreadSafeWrapper

import threading as th
from time import sleep

# Classes
class AnimationChargement(th.Thread):
    # Méthodes spéciales
    def __init__(self, texte):
        self.texte  = texte
        self.fini   = False
        self.erreur = False
        
        super(AnimationChargement, self).__init__()
    
    # Méthodes
    def run(self):
        statut = 0
        avance = True
        animation = [".    ", "..   ", "...  ", " ... ", "  ...", "   ..", "    ."]
        
        print("")
        while not self.fini:
            points = animation[statut]
            
            if avance:
                statut += 1
                
                if statut == len(animation) -1:
                    avance = False
            
            else:
                statut -= 1
                
                if statut == 0:
                    avance = True
            
            print("\033[A\033[K\033[1m{:<50}  [{}]\033[0m".format(self.texte, points))
            
            sleep(0.3)
        
        couleur = "37"
        message = "Ok"
        
        if self.erreur != False:
            couleur = "31"
            message = "Erreur : {!r}".format(self.erreur)
        
        print("\033[A\033[K\033[1;{}m{:<50}  {}\033[0m".format(couleur, self.texte, message))
    
    def arreter(self):
        self.fini = True
        self.join()

class PourcentageChargement(th.Thread):
    # Méthodes spéciales
    def __init__(self, texte):
        self.texte  = texte
        self.fini   = False
        self.erreur = False
        self._etat  = 0
        
        super(PourcentageChargement, self).__init__()
    
    # Méthodes
    def run(self):
        statut = 0
        avance = True
        
        print("")
        while not self.fini:
            print("\033[A\033[K\033[1m{:<50}  {:.2%}\033[0m".format(self.texte, self._etat))
            sleep(0.3)
        
        couleur = "37"
        message = "Ok"
        
        if self.erreur != False:
            couleur = "31"
            message = "Erreur : {!r}".format(self.erreur)
        
        print("\033[A\033[K\033[1;{}m{:<50}  {}\033[0m".format(couleur, self.texte, message))
    
    def arreter(self):
        self.fini = True
        self.join()
    
    # Propriétés
    @property
    def etat(self):
        return self._etat
    
    @etat.setter
    def etat(self, val):
        if (val < 0) or (val > 1):
            self.erreur = "erreur !"
            raise ValueError("Doit être compris entre 0 et 1 !")
        
        self._etat = val

class ChargementThread:
    # Méthodes spéciales
    def __init__(self, target, description):
        self._target = target
        self._description = description
        
        self._retour = ThreadSafeWrapper(None)
    
    # Méthodes privées
    def run(self):
        return self._target()
    
    def _fonction(self):
        try:
            retour = self.run()
            
            with self._retour:
                self._retour.objet = "OK !"
            
            return retour
        
        except Exception as err:
            with self._retour:
                self._retour.objet = "Erreur !\n    " + repr(err)
    
    # Méthodes
    def charger(self):
        # Création des threads
        t  = th.Thread(target=self._fonction)
        ta = AnimationChargement(self._description)
        
        # Lancement
        t.start()
        ta.start()
        
        # Attente
        t.join()
        
        # Fin
        if self._retour.objet.startswith("Erreur"):
            ta.erreur = self._retour.objet
        
        ta.arreter()
