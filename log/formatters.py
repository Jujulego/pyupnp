'''
Created on 6 févr. 2015

@author: julien
'''

# Importations
import logging

# Classes
class ConsoleFormatter(logging.Formatter):
    """
    Mise en forme de la sortie console.
    """
    
    # Méthodes
    def format(self, record):
        record.message = record.getMessage()
        
        if record.levelno == logging.DEBUG:
            return logging.Formatter("\033[34m%(name)-20s %(levelname)s: %(message)s\033[0m").format(record)
        
        elif record.levelno == logging.INFO:
            return logging.Formatter("%(name)-20s %(levelname)s: %(message)s").format(record)
        
        elif record.levelno == logging.WARNING:
            return logging.Formatter("\033[33m%(name)-20s %(levelname)s: %(message)s\033[0m").format(record)
        
        else:
            return logging.Formatter("\033[31m----------------------------------------\n%(name)-15s %(levelname)s dans %(threadName)s, depuis %(module)s.%(funcName)s (%(asctime)s)\n%(message)s\n----------------------------------------\033[0m").format(record)
