# Importations
from .upnp import UPnPDeviceXMLParser

# Classe
class EMCXMLParser(UPnPDeviceXMLParser):
    # Attributs
    namespace = "emc"
