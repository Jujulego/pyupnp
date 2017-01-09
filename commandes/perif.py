# Importations
from .base.commande import BaseCommande
from .ligne import LigneCommande

from helper import Helper
from partages.client import Client
from partages.namespace import Namespace

from base.utils import recupIp
from gardiens import Gardien

# Variables
helper = Helper()

# Classe
class PerifCommande(BaseCommande):
    # Attributs
    nom = "perif"
    options = {
        "description": "Affiche les infos connues sur le périférique donné.",
        "help":        "Affiche les infos connues sur le périférique donné.",
    }
    arguments = (
        {
            "noms": ["-u", "--uuid"],
            "action": "store_true",
            
            "help": "Indique que l'identifiant est un un UUID.",
        },
        {
            "noms": ["identifiant"],
            "action": "store",
            
            "help": "Identifiant du périférique (visibles dans la liste).",
        },
    )
    
    # Méthodes
    def executer(self, args):
        try:
            c = Client(recupIp(), helper.PORT_PARTAGE)
            c.lancer("perif", args)
            
        except KeyboardInterrupt:
            c.envoyer(b"arret")

LigneCommande.commandes.append(PerifCommande)
