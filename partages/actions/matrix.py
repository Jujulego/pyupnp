# Importations
from .base import BaseAction

from gardiens.matrix import MatrixClient

import multiprocessing as mp
from select import select
from time import sleep

# Classes
class MatrixAction(BaseAction):
    # Attributs
    nom = "matrix"
    
    # Méthodes
    def executer(self):
        mc = MatrixClient(mp.current_process().matrix_addr)
        mc.connecter()
        
        while True:
            couleurs = ["32", "33", "31", "35", "36", "34", "37", "38"]
            statuts  = ""
            somme    = 0
            
            for s in mc.recup_statuts():
                if s == 0:
                    statuts += ' '
                
                elif (s <= 8) and self.args.couleur:
                    statuts += "\033[{}m{:d}\033[0m".format(couleurs[s-1], s)
                
                else:
                    statuts += str(s)
                
                somme += s
            
            self.afficher(statuts + '│ ' + str(somme))
            rliste, _, _ = select([self.stdout], [], [], 1/self.args.frequence)
            
            if self.stdout in rliste:
                message = self.stdout.read()
                
                if message == b"arret":
                    break
        
        mc.deconnecter()
