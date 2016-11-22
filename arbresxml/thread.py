# Importations
from protocoles.http import ClientHTTP

from base.wrapper import ThreadSafeWrapper
from log.mixin import ThreadLogMixin

import re
import threading as th

# Classe
class XMLThread(ThreadLogMixin, th.Thread):
    # Attributs
    nom_log = "upnp"
    etudes_en_cours = ThreadSafeWrapper({})
    
    # Méthodes spéciales
    def __init__(self, location, parser):
        if not location.startswith("http://"):
            location = "http://" + location;
        
        self.location   = location
        self.parser_cls = parser
        
        super(XMLThread, self).__init__()
    
    # Méthodes
    def recup_arbre(self):
        reponse, ok = ClientHTTP.depuisAdresse(self.location)
        
        if ok:
            self.debug("{} : arbre reçu.".format(self.location))
            return reponse.read().decode("utf-8")
        
        return None
    
    def run(self):
        with self.etudes_en_cours:
            if self.location in self.etudes_en_cours.objet.get(self.parser_cls, []):
                return
            
            else:
                if self.parser_cls not in self.etudes_en_cours.objet:
                    self.etudes_en_cours.objet[self.parser_cls] = []
                
                self.etudes_en_cours.objet[self.parser_cls].append(self.location)
        
        self.info("Analyse de l'arbre {}".format(self.location))
        
        arbre = self.recup_arbre()
        
        if arbre == None:
            return
        
        self.parser = self.parser_cls(arbre)
        m = re.match(r"http://((([0-9]{1,3}\.?){4}(:[0-9]{1,5})?)|([a-zA-Z\.0-9-_=+?]+))/", self.location)
        self.parser._base_url = self.location[m.start():m.end()]
        self.parser.analyser()
        
        with self.etudes_en_cours:
            self.etudes_en_cours.objet[self.parser_cls].remove(self.location)
        
        self.info("Arbre {} analysé !".format(self.location))
