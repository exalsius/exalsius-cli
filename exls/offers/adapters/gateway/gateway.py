from exls.offers.core.ports.repository import OffersRepository


# The gateway acts as the adapter here since there is no
# complex adapter logic needed.
class OffersGateway(OffersRepository):
    pass
