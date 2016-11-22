'''
Created on 18 juin 2015

@author: julien
'''

from datetime import datetime
import multiprocessing as mp
import multiprocessing.connection  # @UnusedImport
import pickle

from base.serveurs.exceptions import VideErreur, MessageErreur

class BaseServeur():
    '''
    Base des serveurs
    '''
    
    # Méthodes
    def envoi(self, conn, message, niveau="I"):
        """
        Envoie un message dans la connection conn.
        Le message doit être picklable.
        
        Définition des niveaux:
         - D : données
         - E : erreur
         - I : info
        """
        
        assert niveau.upper() in ["D", "E", "I"], "Le niveau doit être parmis D, E et I"
        message = (niveau + ":").encode("utf-8") + pickle.dumps(message)
        
        if isinstance(conn, mp.connection.Connection):
            conn.send_bytes(message)
        
        else:
            conn.send(message)
    
    def recevoir(self, conn, timeout=0.0, erreurs=True):
        """
        Reçoit et analyse le message.
        """
        
        if isinstance(conn, mp.connection.Connection):
            if conn.poll(timeout):
                message = conn.recv_bytes()
            
            else:
                raise VideErreur("Il n'y a rien à lire !")
        
        else:
            debut = datetime.now()
            un_tour = True # Force à entrer la boucle au moins une fois.
            
            while (datetime.now() - debut).total_seconds() <= timeout or un_tour:
                un_tour = False
                message = conn.recv()
            
            if len(message) == 0:
                raise VideErreur("Il n'y a rien à lire !")
            
        niveau = message[0].decode("utf-8")
        message = pickle.loads(message[2:])
        
        if niveau == "E" and erreurs:
            raise MessageErreur("Erreur dans le traitement de la requête") from message
        
        return niveau, message