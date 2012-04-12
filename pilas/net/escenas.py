import pilas
from pilas.escenas import Normal
from pilas.net.actor import PilasNetworkObject

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from PodSixNet.Connection import connection, ConnectionListener

from weakref import WeakKeyDictionary

import uuid

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
    
    #def Network(data):
    #    print data
            
    def Network_crear_actor(self, data):
        self._server.enviar_al_resto(data, self)

    def Close(self):
        pass
    

class EscucharServidor(ConnectionListener):
    def __init__(self):
        pass
    
    def Network_crear_actor(self, data):
        pilas.net.actor.ActorNet()
    

class EscenaServidor(Normal, Server):

    channelClass = ClientChannel
    
    def __init__(self, puerto_servidor=31425):
        Normal.__init__(self)
        Server.__init__(self, localaddr=("127.0.0.1", puerto_servidor))
        print "Servidor iniciado en el pueto :" , puerto_servidor
        self._clientes = WeakKeyDictionary()
        pilas.eventos.actualizar.conectar(self.actualizar)

    def iniciar(self):
        pass

    def terminar(self):
        pass
    
    def actualizar(self, evento):
        self.Pump()
        
    # ####################################################
    # Network Events
    # #################################################### 
           
    def Connected(self, channel, addr):
        print "Cliente agregado"
        self.agregar_Cliente(channel)
    
    def agregar_Cliente(self, cliente):
        print "Nuevo Cliente " + str(cliente.addr)
        self._clientes[cliente] = True
        #self.SendPlayers()
        print "clientes", [p for p in self._clientes]        
    
    def eliminar_Cliente(self, cliente):
        print "Eliminando Cliente " + str(cliente.addr)
        del self._clientes[cliente]
        #self.SendPlayers()
    
    #def SendPlayers(self):
    #    self.SendToAll({"action": "players", "players": [p.nickname for p in self.players]})
    def enviar_al_resto(self, data, cliente_excepcion):
        for c in self._clientes:
            if (c != cliente_excepcion):
                c.Send(data)
        
    
    def enviar_a_todos(self, data):
        [c.Send(data) for c in self._clientes]
    
class EscenaCliente(Normal, EscucharServidor):
    
    def __init__(self, ip_servidor='127.0.0.1', puerto_servidor=31425):
        Normal.__init__(self)
        self.Connect((ip_servidor, puerto_servidor))
        pilas.eventos.actualizar.conectar(self.actualizar)
    
    def actualizar(self, evento):
        if (len(pilas.actores.todos) > 0):
            for actor in pilas.actores.todos:
                if (isinstance(actor, PilasNetworkObject) and actor.id == ""):
                    actor.id = '0'
                    connection.Send({"action": "crear_actor", "data" : actor.__class__.__name__})
        connection.Pump()
        self.Pump()                 