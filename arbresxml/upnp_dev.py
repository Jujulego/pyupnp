# Importations
from .base import XMLInterrupt
from .upnp import UPnPBaseXMLParser

import re

# Classe
class UPnPDeviceXMLParser(UPnPBaseXMLParser):
    # Attributs
    namespace  = "upnp_dev"
    devTypeRe  = re.compile(r"urn:(?P<namespace>.+):device:(?P<type>.+):(?P<version>[0-9]+)")
    servTypeRe = re.compile(r"urn:(?P<namespaceType>[^#]+):service:(?P<type>[^#]+):(?P<version>[0-9.]+)")
    servIdRe   = re.compile(r"urn:(?P<namespaceId>.+):serviceId:(?P<identifiant>.+)")
    
    # Méthodes
    def _analyse_device(self, dev, parent, uuid_parent):
        # UDN + parenté
        uuid = self.find(dev, "UDN", True).text[5:]
        self.donnees[uuid] = {
            "uuid": uuid,
            "parent": uuid_parent,
            "spec_version": self.spec_version,
        }
        
        # deviceType
        dev_type = self.devTypeRe.match(self.find(dev, "deviceType", True).text)
        if not dev_type:
            raise XMLInterrupt("Valeur de deviceType invalide : {}".format(self.find(dev, "deviceType", True).text), "warning")
        
        self.donnees[uuid].update(dev_type.groupdict())
        
        # Obligatoire
        for nom, tag in (("nom simple", "friendlyName"), ("créateur", "manufacturer"), ("nom", "modelName")):
            if "URL" in tag:
                self.donnees[uuid][nom] = self._join_url(self.find(dev, tag, True).text)
            
            else:
                self.donnees[uuid][nom] = self.find(dev, tag, True).text
        
        # Recommandé / Optionnel
        for nom, tag in (("site créateur", "manufacturerURL"), ("description", "modelDescription"), ("numero modèle", "modelNumber"), ("site modèle", "modelURL"), ("numéro de série", "serialNumber"), ("UPC", "UPC")):
            elem = self.find(dev, tag, False)
            
            if elem:
                if "URL" in tag:
                    self.donnees[uuid][nom] = self._join_url(elem.text)
                
                else:
                    self.donnees[uuid][nom] = elem.text
        
        # Icones:
        self.donnees[uuid]["icones"] = []
        icones_liste = self.find(dev, "iconList", False)
        
        if icones_liste:
            for icone in self.findall(icones_liste, "icon"):
                di = {}
                
                for nom, tag in (("mime type", "mimetype"), ("largeur", "width"), ("hauteur", "height"), ("bits / pixel", "depth"), ("url", "url")):
                    di[nom] = self.find(icone, tag, True).text
                
                di["url"] = self._join_url(di["url"])
                self.donnees[uuid]["icones"].append(di)
            
            self.donnees[uuid]["icones"] = tuple(self.donnees[uuid]["icones"])
        
        # Services
        self.donnees[uuid]["services"] = {}
        services_liste = self.find(dev, "serviceList", False)
        
        if services_liste:
            for service in self.findall(services_liste, "service"):
                ds = {}
                
                # serviceType
                serv_type = self.servTypeRe.match(self.find(service, "serviceType").text)
                if not serv_type:
                    raise XMLInterrupt("Valeur de serviceType invalide : {}".format(self.find(service, "serviceType").text), "warning")
                
                ds.update(serv_type.groupdict())
                
                # serviceId
                serv_id = self.servIdRe.match(self.find(service, "serviceId").text)
                if not serv_id:
                    raise XMLInterrupt("Valeur de serviceId invalide : {}".format(self.find(service, "serviceId").text), "warning")
                
                ds.update(serv_id.groupdict())
                
                # Infos :
                for nom, tag in (("description", "SCPDURL"), ("controle", "controlURL"), ("evenements", "eventSubURL")):
                    ds[nom] = self._join_url(self.find(service, tag).text)
                
                self.donnees[uuid]["services"][ds["identifiant"]] = ds
        
        # Périfériques inclus
        self.donnees[uuid]["perifs inclus"] = []
        devices_liste = self.find(dev, "deviceList", False)
        
        if devices_liste:
            for device in self.findall(devices_liste, "device"):
                self.donnees[uuid]["perifs inclus"].append(self._analyse_device(device, dev, uuid))
        
        return uuid
    
    def _analyser(self):
        self.check_specVersion()
        self.donnees = {}
        elem = self.find(self.racine, "URLBase", False)
        
        if elem:
            self._base_url = elem.text
        
        self._analyse_device(self.find(self.racine, "device", True), None, None)
        
        from periferiques.perif_distant import PeriferiqueDistant
        
        for uuid, infos in self.donnees.items():
            PeriferiqueDistant(uuid).ajouter_xml(infos)
