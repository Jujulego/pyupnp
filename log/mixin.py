'''
Created on 4 févr. 2015

@author: julien
'''

# Importations
import logging
from threading import Thread
import traceback
import sys

# Classe LogMixin
class LogMixin:
    '''
    Donne un accès à un log directement depuis l'objet.
    '''
    
    # Attributs
    nom_log = None
    
    # Méthode
    def log(self, niveau, message, *args, **kwargs):
        '''
        Envoie un message du niveau indiqué.
        '''
        
        return self.logger.log(niveau, message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        '''
        Envoie un message de niveau DEBUG (10)
        '''
        
        return self.log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        '''
        Envoie un message de niveau INFO (20)
        '''
        
        return self.log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        '''
        Envoie un message de niveau WARNING (30)
        '''
        
        return self.log(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        '''
        Envoie un message de niveau ERROR (40)
        '''
        
        return self.log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        '''
        Envoie un message de niveau CRITICAL (50)
        '''
        
        return self.log(logging.CRITICAL, message, *args, **kwargs)
    
    # Propriété
    @property
    def logger(self):
        return logging.getLogger(self.nom_log)

# Log Thread
class LogThread(Thread):
    '''
    Thread envoyant un log.
    '''
    
    # Méthodes spéciales
    def __init__(self, logger, niveau, message, *args, **kwargs):
        '''
        Initialise le Thread et stock les information sur le log.
        '''
        super(LogThread, self).__init__()
        
        self.logger = logger
        self.niveau = niveau
        self.message = message
        
        self.args = args
        self.kwargs = kwargs
        
        self.name = "LogThread-{}-{}".format(self.niveau, self.name.split('-')[-1])
    
    # Méthodes
    def run(self):
        self.logger.log(self.niveau, self.message, *self.args, **self.kwargs)

class ThreadLogMixin(LogMixin):
    '''
    Comme LogMixin mais les logs sont envoyés dans des Threads
    '''
    
    # Méthodes
    def log(self, niveau, message, *args, **kwargs):
        '''
        Envoie le log, dans un thread parallèle
        '''
        
        t = LogThread(self.logger, niveau, message, *args, **kwargs)
        t.daemon = True
        t.start()

# Pour les serveurs de 'socketserver'
class ServerLogMixin(LogMixin):
    # Méthodes
    def handle_error(self, requete, client_address):
        tb = ''.join(traceback.format_exception(*sys.exc_info()))[:-1]
        self.error("Exception happened during processing of request from {addr}\n\n{erreur}".format(addr=str(client_address), erreur=tb))

class ServerThreadLogMixin(ThreadLogMixin, ServerLogMixin):
    pass
