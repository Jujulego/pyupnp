# Importations
from .base.commande import BaseCommande
from .ligne import LigneCommande

from helper import Helper
from partages.client import Client
from partages.namespace import Namespace

from base.utils import recupIp
from gardiens import Gardien

# Variables
helper = Helper()

# Classe
class MatrixCommande(BaseCommande):
    # Attributs
    nom = "matrix"
    options = {
        "description": "Affiche la matrice",
        "help":        "Affiche la matrice des locks contenu (développement)",
    }
    arguments = (
        {
            "noms": ["-c", "--couleur"],
            "action": "store_true",
            
            "help": "Affiche les nombres colorés.",
        },
        {
            "noms": ["-f", "--frequence"],
            "action": "store",
            "default": 10,
            "type": int,
            
            "help": "Réglage du nombre de mise à jour par secondes (défaut: 10)",
        },
    )
    
    # Méthodes
    def executer(self, args):
        c = Client(recupIp(), helper.PORT_PARTAGE)
        c.lancer("matrix", args)

LigneCommande.commandes.append(MatrixCommande)
