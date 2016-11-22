# Importations
from base.communication import PickleMixin, BaseClient

# Mixins
class CommunicationClientMixin(PickleMixin, BaseClient):
    pass
