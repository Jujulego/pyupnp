# Importations
from .base.commande import BaseCommande
from .ligne import LigneCommande

from base.utils import recupIp
from partages.client import Client

from gardiens import Gardien

# Classes
class ListeCommande(BaseCommande):
    '''
    Affiche la liste des périfériques présents sur le réseau.
    '''
    
    # Attributs
    nom = "liste"
    options = {
        "description": "Affiche une liste des périfériques connus, ainsi que de quelques informations les concernant.",
        "help":        "Affiche une liste des périfériques connus, ainsi que de quelques informations les concernant.",
    }
    arguments = (
        {
            "noms": ["-a", "--all",],
            "action": "store_true",
            
            "help": "Affiche tous les périfériques connus.",
        },
        {
            "noms": ["-c", "--couleur",],
            "action": "store_true",
            
            "help": "Provoque un affichage coloré",
        },
        {
            "noms": ["-u", "--uuid",],
            "action": "store_true",
            
            "help": "Affiche les UUID au lieu des nom",
        },
        {
            "noms": ["-t", "--tri",],
            "action": "store",
            "default": "id",
            "choices": ("id", "nom", "uuid", "nom dns", "port", "présent", "valide"),
            
            "help": "Modifie le tri du tableau (défaut: 'id')",
        },
        {
            "noms": ["-i", "--inverse",],
            "action": "store_true",
            
            "help": "Inverse le tri en cours.",
        },
        {
            "noms": ["-s", "--serveur",],
            "action": "store",
            "default": "",
            
            "help": "Indique l'adresse du serveur",
        },
    )
    
    # Méthodes
    def executer(self, args):
        Gardien().lancer(False)
        
        try:
             if args.serveur != "":
                 client = Client(args.serveur)
             else:
                 client = Client(recupIp())
             
             client.lancer('liste', args)
                
        finally:
            Gardien().arreter(False)

LigneCommande.commandes.append(ListeCommande)
