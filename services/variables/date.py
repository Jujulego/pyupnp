# Importations
from .base import BaseVariable
from .exceptions import ValeurIllegale

from datetime import date, datetime, time

# Temps
class VariableTemps(BaseVariable):
    # Attributs
    temps_format = None
    
    # Méthodes privées
    def _check_valeur(self, valeur):
        pass
    
    @classmethod
    def _pythoniser(cls, valeur):
        return datetime.strptime(valeur, cls.temps_format)
    
    def _xmliser(self):
        return self.valeur.isoformat() # ISO 8601

class Date(VariableTemps):
    # Attributs
    identifiant  = "date"
    python_type  = date
    temps_format = "%Y-%m-%d"
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        return super(Date, cls)._pythoniser(valeur).date()

class DateTime(VariableTemps):
    # Attributs
    identifiant  = "dateTime"
    python_type  = datetime
    temps_format = "%Y-%m-%dT%H:%M:%S"

class DateTimeTz(VariableTemps):
    # Attributs
    identifiant  = "dateTime.tz"
    python_type  = datetime
    temps_format = "%Y-%m-%dT%H:%M:%S%z"
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        valeur = ':'.join(valeur.split(':')[:-1]) + valeur.split(':')[-1]
        return datetime.strptime(valeur, cls.temps_format)

class Time(VariableTemps):
    # Attributs
    identifiant  = "time"
    python_type  = time
    temps_format = "%H:%M:%S"
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        return super(Time, cls)._pythoniser(valeur).time()

class TimeTz(VariableTemps):
    # Attributs
    identifiant  = "time.tz"
    python_type  = time
    temps_format = "%H:%M:%S%z"
    
    # Méthodes privées
    @classmethod
    def _pythoniser(cls, valeur):
        valeur = ':'.join(valeur.split(':')[:-1]) + valeur.split(':')[-1]
        return datetime.strptime(valeur, cls.temps_format).timetz()
