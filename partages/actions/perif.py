# Importations
from .base import BaseAction

from base.utils import genererTableau
from periferiques import PeriferiqueDistant

from datetime import datetime

# Clase
class PerifAction(BaseAction):
    # Attributs
    nom = "perif"
    
    # Méthodes
    def executer(self):
        # Chargement
        self.afficher("Chargement des données ...")
        
        try:
            if not self.args.uuid:
            	perif = PeriferiqueDistant(int(self.args.identifiant))
            
            else:
                perif = PeriferiqueDistant(self.args.identifiant)
            
            infos = perif.infos
            servs = perif.services
        
        except IndexError:
            self.afficher("Le périférique {} est inconnu.".format(str(self.args.identifiant)))
            return
        
        self.afficher("\033[A\033[KChargement des données OK")
        
        # Informations
        taille_nom = max([len(n) for n in infos])
        
        self.afficher("Périférique {} :".format(infos.get("nom simple", str(infos["uuid"]))))
        self.afficher("  Informations :")
        
        for n, v in infos.items():
            if not n in ("perifs inclus", "services", "icones"):
                self.afficher(("  │ {:<" + str(taille_nom) + "} : {}").format(n, v))
        
        self.afficher("")
        
        # Services
        self.afficher("  Services : ")
        if len(servs) != 0:
        	tab = genererTableau(
        		[s.infos for s in servs],
        		["identifiant", "type", "version", "namespaceId", "namespaceType"]
        	)
        	
        	for l in tab.splitlines():
        		self.afficher("    " + l)
        
        else:
            self.afficher("    aucuns !")
        
        self.afficher("")
        
        # Sous-périfériques
        self.afficher("  Périfériques inclus :")
        
        if len(infos.get("perifs inclus", [])) != 0:
            for p in infos.get("perifs inclus", []):
                self.afficher("  - {}".format(p))
        
        else:
            self.afficher("    aucuns !")
