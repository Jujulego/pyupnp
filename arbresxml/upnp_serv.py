# Importations
from .base import XMLInterrupt
from .upnp import UPnPBaseXMLParser

from services.actions import Argument, Action
from services.variables import creer_var_xml

import re

# Classe
class UPnPServiceXMLParser(UPnPBaseXMLParser):
    # Attributs
    namespace = "upnp_serv"
    
    # Méthodes
    def check_nom(self, nom, state_var=False):
        if len(nom) > 32:
            raise XMLInterrupt("Nom invalide '{}'".format(nom), "warning")
        
        if nom.startswith("A_"):
            if nom.startswith("A_ARG_TYPE_") and state_var:
                pass
            
            else:
                raise XMLInterrupt("Nom invalide '{}'".format(nom), "warning")
        
        for c in nom.encode("utf-8"):
            if ((c == 0x2e) and (nom.encode("utf-8").index(c) > 0)) or \
               ((c >= 0x30) and (c <= 0x39)) or \
               ((c >= 0x41) and (c <= 0x5a)) or \
               (c == 0x5f) or \
               ((c >= 0x61) and (c <= 0x7a)) or \
               (c >= 0x7f):
                continue
            
            raise XMLInterrupt("Nom invalide '{}'".format(nom), "warning")
    
    def analyse_state_var(self, state_var):
        # Nom
        nom = self.find(state_var, "name", False).text
        self.check_nom(nom, True)
        
        # Type
        dataType = self.find(state_var, "dataType", False).text
        
        # Events
        events = (state_var.attrib.get("sendEvents", "yes") == "yes")
        
        # Rassemblement !
        variable = {
            "nom"   : nom,
            "type"  : dataType,
            "events": events,
        }
        
        # Valeur par defaut
        defaut = self.find(state_var, "defaultValue")
        
        if defaut != None:
            defaut = defaut.text
            
            variable["defaut"] = defaut
        
        # Limite (valeurs numeriques)
        range = self.find(state_var, "allowedValueRange")
        
        if range != None:
            max  = self.find(range, "maximum", False).text
            min  = self.find(range, "minimum", False).text
            step = self.find(range, "step")
            if step != None:
                step = step.text
            
            variable.update({
                "max" : max,
                "min" : min,
                "step": step,
            })
        
        # Choix (valeurs textuelles)
        liste_elem = self.find(state_var, "allowedValueList")
        liste = []
        
        if liste_elem != None:
            for v in self.findall(liste_elem, "allowedValue"):
                liste.append(v.text)
            
            variable["liste"] = liste
        
        return variable["nom"], creer_var_xml(**variable)
    
    def analyse_action(self, action):
        donnees = {}
        
        # Nom
        nom = self.find(action, "name").text
        self.check_nom(nom)
        
        donnees["nom"] = nom
        donnees["standard"] = not nom.startswith("X_")
        
        # Arguments
        args_liste = self.find(action, "argumentList", False)
        args = {}
        
        if args_liste:
            for arg in self.findall(args_liste, "argument"):
                # Nom
                nom = self.find(arg, "name", False).text
                self.check_nom(nom)
                
                # Direction (input / output)
                direction = self.find(arg, "direction", False).text
                if direction.lower() not in ["in", "out"]:
                    raise XMLInterrupt("Mauvaise direction {}".format(direction))
                
                # Variable liée
                var_liee = self.find(arg, "relatedStateVariable", False).text
                args[nom] = Argument(nom, self.variables[var_liee], direction)
        
        donnees["arguments"] = args
        
        return Action(**donnees)
    
    def _analyser(self):
        self.check_specVersion()
        
        url_base = self.find(self.racine, "URLBase", False)
        if url_base:
            self._base_url = url_base.text
        
        try:
            self.variables = {}
            self.actions = {}
            
            for state_var in self.findall(self.find(self.racine, "serviceStateTable"), "stateVariable"):
                nom, donnees = self.analyse_state_var(state_var)
                self.variables[nom] = donnees
            
            actionList = self.find(self.racine, "actionList", False)
            if actionList:
                for action in self.findall(actionList, "action"):
                    a = self.analyse_action(action)
                    self.actions[a.nom] = a
        
        except XMLInterrupt:
            pass
        
        except Exception as err:
            raise XMLInterrupt("Erreur lors de l'analyse : {!r}".format(err), "warning")
