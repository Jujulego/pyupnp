# Fonctions
def init_ssdp():
    from .serveur import SSDPServeur
    from .handler import SSDPHandler
    
    from gardiens import Gardien
    
    import multiprocessing as mp
    
    def fonc():
        try:
            srv_ssdp = SSDPServeur(('', 1900), SSDPHandler)
            return srv_ssdp.serve_forever()
        
        finally:
            g = Gardien()
            
            if g.status == "actif":
                g.arreter()
    
    p = mp.Process(name="SSDP-Process", target=fonc)
    p.start()
    return p
