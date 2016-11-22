#
# Paramètres de PyUPnP
#

# Importations
from base.table import Table

from os import path
import socket

# Paramètres généraux
BASE_DIR  = path.dirname(__file__)
HOST_NAME = socket.gethostname()
VERSION   = "1.0.1"

RESEAU = "maison"

# Paramètres SSDP
NB_ENVOI_REQUETES = 3
TTL_REQUETES      = 4
MSEARCH_MAX_AGE   = 5
NOTIFY_MAX_AGE    = 1800

# Paramètres des serveurs externes
PORT_PARTAGE      = 19000

# Paramètres des serveurs internes
PORT_RECHERCHES   = 19100
PORT_PERIFERIQUES = 19101

# Paramètres de l'analyse XML
XML_NAMESPACES = {
    # UPnP
    "upnp_dev" : "urn:schemas-upnp-org:device-1-0",
    "upnp_serv": "urn:schemas-upnp-org:service-1-0",
    
    # EMC
    "emc": "urn:schemas-emc-com:device-1-0",
}

# Stockage
DOSSIER_RACINE = path.join(BASE_DIR, "donnees")
ARBRE_STOCKAGE = {
    "racine": DOSSIER_RACINE,
    
    "contenu": {
        RESEAU: {
            "type": "stock",
            
            "contenu": {
                "periferiques": {
                    "type": "stock",
                    
                    "contenu": {
                        "liste": {
                            "type": "coffre",
                            
                            "contenu": Table(("id", "uuid")),
                        },
                    },
                },
                
                "recherches": {
                    "type": "stock",
                    
                    "contenu": {
                    },
                },
            },
        },
    },
}

# Définition de la journalisation
LOG_DIR = path.join(BASE_DIR, "logs")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    
    "formatters": {
        "console": {
            '()': "log.formatters.ConsoleFormatter",
        },
        
        "debug": {
            'format': "%(name)s %(levelname)s: %(threadName)s (%(asctime)s)\nFonction : %(module)s.%(funcName)s, %(filename)s ligne %(lineno)d\n%(message)s",
        },
    },
    
    "filters": {
    },
    
    "handlers": {
        "null": {
            'class': "logging.NullHandler",
        },
        
        "console": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            
            'formatter': "console",
        },
        
        "console_err": {
            'level': "ERROR",
            'class': "logging.StreamHandler",
            
            'formatter': "console",
        },
        
        "log_upnp": {
            'level': "DEBUG",
            'class': "logging.handlers.TimedRotatingFileHandler",
            
            'formatter': "debug",
            
            'filename': path.join(LOG_DIR, "upnp.log"),
            'when': 'd',
            'backupCount': 30,
        },
        
        "log_ssdp": {
            'level': "DEBUG",
            'class': "logging.handlers.TimedRotatingFileHandler",
            
            'formatter': "debug",
            
            'filename': path.join(LOG_DIR, "ssdp.log"),
            'when': 'd',
            'backupCount': 30,
        },
        
        "log_part": {
            'level': "DEBUG",
            'class': "logging.handlers.TimedRotatingFileHandler",
            
            'formatter': "debug",
            
            'filename': path.join(LOG_DIR, "partage.log"),
            'when': 'd',
            'backupCount': 30,
        },
    },
    
    "loggers": {
        "gardien": {
            'handlers': ('console',),
            'propagate': False,
        },
        
        "upnp": {
            'handlers': ('console',),
            'propagate': False,
        },
        
        "upnp.log": {
            'handlers': ('log_upnp',),
        },
        
        "upnp.ssdp": {
            'handlers': ('log_ssdp',),
        },
        
        "upnp.partages": {
            'handlers': ('log_part',),
        },
        
        "upnp.periferiques": {
        },
        
        "upnp.recherches": {
        },
    },
}
