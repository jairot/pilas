# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

import pilas
from pilas.escenas import Normal
from pilas.actores.actor import Actor

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from PodSixNet.Connection import connection, ConnectionListener

from weakref import WeakKeyDictionary

import random

from pilas.actores import *
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
        self._server.actores.append({"clase" : data['clase'], "id" : data['id'], "cliente" : self.addr})

    def Network_mover_actor(self, data):
        self._server.enviar_al_resto(data, self)

    def Close(self):
        pass
    

class EscucharServidor(ConnectionListener):
    def __init__(self):
        pass
    
    def Network_crear_actor(self, data):
        clase_actor = eval(data['clase'])
        actor = clase_actor()
        actor.id = data['id']
        actor.x = random.randint(-320,320)
        actor.y = random.randint(-240,240)
        actor.decir(data['id'])
    
    def Network_mover_actor(self, data):
        print data

class EscenaServidor(Normal, Server):

    channelClass = ClientChannel
    
    def __init__(self, puerto_servidor=31425):
        Normal.__init__(self)
        Server.__init__(self, localaddr=("127.0.0.1", puerto_servidor))
        print "Servidor iniciado en el pueto :" , puerto_servidor
        self._clientes = WeakKeyDictionary()
        pilas.eventos.actualizar.conectar(self.actualizar)
        self.actores = []

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
        for actor in self.actores:
            #print actor
            channel.Send({"action": "crear_actor", "clase" : actor['clase'], "id" : actor['id']})
    
    def agregar_Cliente(self, cliente):
        print "Nuevo Cliente " + str(cliente.addr)
        self._clientes[cliente] = True
        #self.SendPlayers()
        #print "clientes", [p for p in self._clientes]        
    
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
        self._actores_compartidos = []
        
    def agregarActorObservado(self, actor):
        actor.conectarObservador(self)
        self._actores_compartidos.append(actor)
        
    def cambioEnActor(self, event):
        connection.Send({"action": "mover_actor", "x" : event['x'] , "id" : event['id']})
             
    def actualizar(self, evento):
        if (len(self._actores_compartidos) > 0):
            for actor in self._actores_compartidos:
                if (isinstance(actor, Actor) and actor.id == ""):
                    actor.id = str(uuid.uuid4())
                    print actor.id
                    connection.Send({"action": "crear_actor", "clase" : actor.__class__.__name__ , "id" : actor.id})
        connection.Pump()
        self.Pump()
        