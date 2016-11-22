# Importations
from .base.lignecommande import BaseLigneCommande

from helper import Helper

# Variable
helper = Helper()

# Classe
class LigneCommande(BaseLigneCommande):
    # Attributs
    options = {
        "description": "Client pyUPnP (version: {})".format(helper.VERSION),
    }
    
    arguments = (
        {   # La version
            "noms": ["-v", "--version"],
            "action": "version",
            "version": "%(prog)s " + helper.VERSION,
            
            "help": "Donne la version du programme",
        },
    )
    
    # Méthodes
    def executer(self, args):
        if hasattr(args, "fonction"):
            args.fonction(args)
        
        else:
            self.parser.print_help()
