# Importations
from .base.commande import BaseCommande
from .ligne import LigneCommande

from helper import Helper
from partages.client import Client

from base.utils import recupIp
from gardiens import Gardien

# Variables
helper = Helper()

# Classe
class DecouverteCommande(BaseCommande):
    # Attributs
    nom = "decouverte"
    options = {
        "description": "Permet de lancer une recherche et d'en recuperer le résultat.",
        "help"       : "Permet de lancer une recherche et d'en recuperer le résultat.",
    }
    arguments = (
        {
            "noms": ("st",),
            "action": "store",
            "default": "ssdp:all",
            
            "help": "Texte de la recherche (par défaut : 'ssdp:all').",
        },
        {
            "noms": ("-m", "--max-age"),
            "action": "store",
            "dest": "mx",
            "type": str,
            "default": str(helper.MSEARCH_MAX_AGE),
            
            "help": "Défini le temps de collecte des réponses (par défaut {}).".format(helper.MSEARCH_MAX_AGE),
        },
        {
            "noms": ("-e", "--envois"),
            "action": "store",
            "type": int,
            "default": helper.NB_ENVOI_REQUETES,
            
            "help": "Défini le nombre d'envois de la recherche (par défaut {}).".format(helper.NB_ENVOI_REQUETES),
        },
        {
            "noms": ("-u", "--uuid"),
            "action": "store_true",
            
            "help": "Indique que le texte de la recherche est un UUID de périfériques.",
        },
        {
            "noms": ("-p", "--perif"),
            "action": "store_true",
            
            "help": "Indique que le texte de la recherche est un type de périférique.",
        },
        {
            "noms": ("-s", "--service"),
            "action": "store_true",
            
            "help": "Indique que le texte de la recherche est un type de service.",
        },
        {
            "noms": ("-n", "--nom-domaine"),
            "action": "store",
            "default": "schemas-upnp-org",
            
            "help": "Définition du nom de domaine (par défaut 'schemas-upnp-org')",
        },
        {
            "noms": ("-v", "--version"),
            "action": "store",
            "default": '1',
            
            "help": "Définition de la version du périférique/service recherché (par défaut 1)",
        },
    )
    
    # Méthodes
    def executer(self, args):
        Gardien().lancer(False)
        
        if args.uuid:
            args.st = "uuid:" + args.st
        
        elif args.perif:
            args.st = "urn:" + args.nom_domaine + ":device:" + args.st + ":" + str(args.version)
        
        elif args.service:
            args.st = "urn:" + args.nom_domaine + ":service:" + args.st + ":" + str(args.version)
        
        try:
            client = Client(recupIp())
            client.lancer('decouverte', args)
        
        finally:
            Gardien().arreter(False)

LigneCommande.commandes.append(DecouverteCommande)
