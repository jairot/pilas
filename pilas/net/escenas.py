# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

import pilas
from pilas.escenas import Normal

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from PodSixNet.Connection import connection, ConnectionListener

from weakref import WeakKeyDictionary

import random

from pilas.actores import *
import uuid    

class CanalCliente(Channel):
    """
    Esta es la representación de canal de comunicación con el Cliente.
    Aquí estan las posibles llamadas que hacen los Clientes al servidor.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
    
    def Network_crear_actor(self, data):
        """ Manda al resto de Clientes la creación de un Actor """
        # Enviamos el comando al resto de clientes.
        self._server.enviar_al_resto(data, self)
        # El servidor se guarda la referencia del ID del Actor y que Cliente lo ha creado.
        self._server.actores.append({"id" : data['id'], "cliente" : self.addr})

    def Network_mover_actor(self, data):
        """ Manda la acción de mover un actor en el resto de Clientes """
        self._server.enviar_al_resto(data, self)

    def Network_crear_actor_en_cliente(self, data):
        """ Manda a un Cliente en concreto la creación de un Actor """
        data['action'] = 'crear_actor'
        # Enviamos el comando al resto de clientes.
        self._server.enviar_a_cliente(data)

    def Network_eliminar_actor(self, data):
        """ Manda la acción de eliminar un actor en el resto de Clientes """
        self._server.enviar_al_resto(data, self)
        
    def Close(self):
        pass

# ---------------------------------
# SERVIDOR
# ---------------------------------

class ServidorPilas(Server):

    channelClass = CanalCliente
    
    def __init__(self, puerto_servidor=31425):
        Server.__init__(self, localaddr=(pilas.net.obteber_ip_local(), puerto_servidor))
        print "Servidor iniciado en el pueto :" , puerto_servidor
        self._clientes = WeakKeyDictionary()
        self.actores = []

    def actualizar(self):
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
        self.enviar_actores_a_cliente(cliente)
    
    def eliminar_Cliente(self, cliente):
        print "Eliminando Cliente " + str(cliente.addr)
        del self._clientes[cliente]

    def enviar_actores_a_cliente(self, cliente):
        for c in self._clientes:
            if (c != cliente):
                c.Send({"action" : "enviar_actores_a_cliente",
                        "cliente" : cliente.addr})
        
    
    def enviar_al_resto(self, data, cliente_excepcion):
        for c in self._clientes:
            if (c != cliente_excepcion):
                c.Send(data)
        
    def enviar_a_todos(self, data):
        [c.Send(data) for c in self._clientes]
        
    def enviar_a_cliente(self, data):
        for c in self._clientes:
            if (c.addr == data['cliente']):
                c.Send(data)
        

# ---------------------------------
# CLIENTE
# ---------------------------------

class ActorObserver():
    def cambioEnActor(self, event):
        print "Debe implementar el metodo cambioEnActor para Observar los cambios de los actores."    

class EscucharServidor(ConnectionListener):
    """ 
    Clase que implementa las peticiones que le llegan desde el servidor.    
    """
        
    def Network_crear_actor(self, data):
        """ Crea un actor de otro Cliente """
        clase_actor = eval(data['clase'])
        actor = clase_actor()
        actor.id = data['id']
        actor.x = data['x']
        actor.y = data['y']
        actor.escala_x = data['escala_x']
        actor.escala_y = data['escala_y']
        actor.rotacion = data['rotacion']
        self._actores_ajenos.append(actor)
    
    def Network_mover_actor(self, data):
        """ Mueve un actor de otro cliente """
        for actor in self._actores_ajenos:
            if (isinstance(actor, Actor) and actor.id == data['id']):
                actor.x = data['x'] 
                actor.y = data['y']
                actor.escala_x = data['escala_x']
                actor.escala_y = data['escala_y']
                actor.rotacion = data['rotacion']
                break
            
    def Network_enviar_actores_a_cliente(self, data):
        """ Envia todos sus actores a otro Cliente """
        for actor in self._actores_compartidos:
            if (isinstance(actor, Actor)):
                connection.Send({"action" : "crear_actor_en_cliente",
                                 "cliente" : data['cliente'],
                                 "clase" : actor.__class__.__name__ , 
                                 "id" : actor.id,
                                 "x" : actor.x,
                                 "y" : actor.y,
                                 "escala_x" : actor.escala_x,
                                 "escala_y" : actor.escala_y,
                                 "rotacion" : actor.rotacion})

    def Network_eliminar_actor(self, data):
        for actor in self._actores_ajenos:
            if (isinstance(actor, Actor) and actor.id == data['id']):
                actor.eliminar()
                self._actores_ajenos.remove(actor)
                break

class EscenaNetwork(Normal, EscucharServidor, ActorObserver):
    
    def __init__(self, rol='cliente', ip_servidor='127.0.0.1', puerto_servidor=31425):
        Normal.__init__(self)
        self.Connect((ip_servidor, puerto_servidor))
        pilas.eventos.actualizar.conectar(self.actualizar)
        self._actores_compartidos = []
        self._actores_ajenos = []
        
        pilas.mundo.colisiones.agregar(self._actores_compartidos, self._actores_ajenos, self.colision_con_ajenos)
        
        self.servidor = None
        if (rol == 'servidor'):
            self.servidor = ServidorPilas(puerto_servidor=31425)
    
    def colision_con_ajenos(self, acto_compartido, actor_ajeno):
        print "colision_con_ajenos(self, acto_compartido, actor_ajeno): No implementado."
    
    def agregar_Actor_Observado(self, actor):
        actor.conectarObservador(self)
        self._actores_compartidos.append(actor)

    def eliminar_Actor_Observado(self, actor):
        id = actor.id
        actor.desconectarObservador(self)
        actor.eliminar()
        self._actores_compartidos.remove(actor)
        connection.Send({"action" : "eliminar_actor",
                                 "id" : id})
        
    def cambioEnActor(self, data):
        connection.Send(data)
             
    def actualizar(self, evento):
        # Actualizamos el servidor si existe.
        if (self.servidor != None):
            self.servidor.actualizar()
        
        if (len(self._actores_compartidos) > 0):
            for actor in self._actores_compartidos:
                if (isinstance(actor, Actor) and actor.id == ""):
                    actor.id = str(uuid.uuid4())
                    connection.Send({"action" : "crear_actor",
                                 "clase" : actor.__class__.__name__ , 
                                 "id" : actor.id,
                                 "x" : actor.x,
                                 "y" : actor.y,
                                 "escala_x" : actor.escala_x,
                                 "escala_y" : actor.escala_y,
                                 "rotacion" : actor.rotacion})
        connection.Pump()
        self.Pump()
        