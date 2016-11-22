# Importations
import errno

# Exceptions
class FileOpenError(OSError):
    """
    Envoyée si le fichier demandé est ouvert
    """
    
    def __init__(self, message):
        super(FileOpenError, self).__init__(errno.EBADFD, message)

class FileCloseError(OSError):
    """
    Envoyée si le fichier demandé est fermé
    """
    
    def __init__(self, message):
        super(FileCloseError, self).__init__(errno.EBADFD, message)
