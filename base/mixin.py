"""
Created on 31 juillet 2015

@author: julien
"""

import multiprocessing as mp
import socketserver
import threading as th

# Mixins
class SingletonMixin:
    # Attributs
    __instance__ = None
    __pid_instance__ = None
    
    # Méthodes spéciales
    def __new__(cls, *args, **kwargs):
        if not cls.__instance__ or (cls.__pid_instance__ != mp.current_process().pid):
            cls.__instance__ = super(SingletonMixin, cls).__new__(cls, *args, **kwargs)
            cls.__pid_instance__ = mp.current_process().pid
            cls.__instance__._creer = True
        
        return cls.__instance__

class ThreadingServerMixin(socketserver.ThreadingMixIn):
    # Méthodes
    def process_request(self, request, client_address):
        t = th.Thread(target=self.process_request_thread, args=(request, client_address))
        
        if not hasattr(self, "threads"):
            self.threads = []
        
        self.threads.append(t)
        t.daemon = self.daemon_threads
        t.start()
