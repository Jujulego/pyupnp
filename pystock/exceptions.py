# Classes
class ExisteDejaErreur(Exception):
    pass

class CoffreExisteErreur(FileExistsError, ExisteDejaErreur):
    pass

class CoffreIntrouvableErreur(FileNotFoundError):
    pass

class StockExisteErreur(FileExistsError, ExisteDejaErreur):
    pass

class StockIntrouvableErreur(FileNotFoundError):
    pass
