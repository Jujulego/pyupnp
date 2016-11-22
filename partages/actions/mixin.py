# Importations
from base.objets import FStr
from base.utils import genererTableau
from pystock.exceptions import CoffreIntrouvableErreur

from datetime import datetime

# Classe
class ListeMixin():
    # Méthodes
    def _recup_donnees(self, p):
        try:
            perif = {}
            
            infos = p.infos
            
            perif["nom dns"], perif["port"] = infos.get("adresse", ('-------', '----'))
            perif["id"]      = infos.get("id", "--")
            perif["uuid"]    = infos.get("uuid", "-------- ---- ---- ---- ------------")
            perif["nom"]     = infos.get("nom simple", perif["uuid"])
            perif["présent"] = infos.get("present", FStr("-----"))
            
            if "fin_validite" in infos:
                perif["valide"] = (datetime.now() < infos["fin_validite"])
            
            else:
                perif["valide"] = FStr("-----")
            
            if perif["valide"] or vars(self.args).get("all", True) or not perif["présent"]:
                self.perifs.append(perif)
            
            else:
                self.non_affiches += 1
        
        except KeyError:
            self.non_affiches += 1
        
        except CoffreIntrouvableErreur:
            self.non_affiches += 1
    
    def generer_liste(self, liste):
        self.perifs       = []
        self.non_affiches = 0
        
        self.afficher("Chargement des données: 0%")
        for p in liste:
            self._recup_donnees(p)
            self.afficher("\033[A\033[KChargement des données: {:.2%}".format((len(self.perifs) + self.non_affiches) / len(liste)))
        
        self.afficher("\033[A\033[KChargement des données: Ok !")
        
        perifs = self.perifs
        
        if len(perifs) > 1:
           operifs = perifs
           perifs  = [operifs[0]]
           
           for p in operifs[1:]:
               for i in range(len(perifs)):
                   try:
                       if perifs[i][vars(self.args).get("tri", "id")] > p[vars(self.args).get("tri", "id")]:
                           perifs.insert(i, p)
                           break
                   
                   except TypeError:
                       pass
               
               if not p in perifs:
                   perifs.append(p)
        
        if vars(self.args).get("inverse", False):
            perifs.reverse()
        
        affichage = ["id", "uuid" if vars(self.args).get("uuid", False) else "nom", "nom dns", "port", "présent"]
        
        if vars(self.args).get("all", True):
            affichage.insert(5, "valide")
        
        return ("{}\n{} périfériques" + (" (+{} non affichés)" if self.non_affiches > 0 else "")).format(
            genererTableau(perifs, affichage,
                couleur = lambda d: ((("32" if d["valide"] else "31") if d["présent"] else "34") if vars(self.args).get("couleur", False) else "0"),
            ),
            len(perifs),
            self.non_affiches
        )
