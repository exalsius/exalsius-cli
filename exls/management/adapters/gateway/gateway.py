from exls.management.core.ports.ports import ManagementRepository


# The gateway acts as the adapter here since there is no
# complex adapter logic needed.
class ManagementGateway(ManagementRepository):
    pass
