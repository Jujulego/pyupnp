# Importations
from .base.commande import BaseCommande
from .ligne import LigneCommande

from starter import Starter

from helper import Helper

# Variables
helper = Helper()

# Classe
class ServeurCommande(BaseCommande):
    '''
    Commande lançant une instance du serveur
    '''
    
    # Attributs
    nom = "serveur"
    options = {
        "description": "Lance une instance du serveur. Les logs sont alors affichés à l'écran",
        "help":        "Lance une instance du serveur. Les logs sont alors affichés à l'écran",
    }
    arguments = (
        {
            "noms": ["-r", "--reseau"],
            "action": "store",
            "default": helper.RESEAU,
            
            "help": "Indique le réseau actuel.",
        },
        {
            "noms": ["--gardien-verbose"],
            "action": "store_true",
            "default": False,
            
            "help": "Autorise l'affichage des logs de Gardien.",
        },
    )
    
    # Méthodes
    def executer(self, args):
        print('''Serveur PyUPnP ({})
'''.format(helper.VERSION))
        
        s = Starter()
        
        s.parametrer(**vars(args))
        s.executer()

LigneCommande.commandes.append(ServeurCommande)
