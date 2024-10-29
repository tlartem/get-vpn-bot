from asyncxui.methods.base import Base
from asyncxui.methods.clients import Clients
from asyncxui.methods.inbounds import Inbounds
from asyncxui.methods.login import Login


class Methods(Base, Login, Inbounds, Clients):
    pass
