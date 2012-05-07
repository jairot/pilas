# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

import pilas
from pilas.escenas import Normal
from pilas.actores import Actor

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel
from PodSixNet.Connection import connection, ConnectionListener

from weakref import WeakKeyDictionary

import uuid    

class CanalCliente(Channel):
    """
    Esta es la representación de canal de comunicación con el Cliente.
    Aquí estan las posibles llamadas que hacen los Clientes al servidor.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
            
    def Network_crear_actor(self, data):
        """ Envia al resto de Clientes la creación de un Actor """
        # Enviamos el comando al resto de clientes.
        self._server.enviar_al_resto(data, self)
        # El servidor se guarda la referencia del ID del Actor y que Cliente 
        # lo ha creado.
        self._server.actores.append({"id" : data['id'], "cliente" : self})

    def Network_mover_actor(self, data):
        """ Envia la acción de mover un actor en el resto de Clientes """
        self._server.enviar_al_resto(data, self)

    def Network_crear_actor_en_cliente(self, data):
        """ Envia a un Cliente en concreto la creación de un Actor """
        data['action'] = 'crear_actor'
        # Enviamos el comando al resto de clientes.
        self._server.enviar_a_cliente(data)

    def Network_eliminar_actor(self, data):
        """ Elimina un actor del resto de clientes. """
        self._server.enviar_al_resto(data, self)
    
    def Network_enviar_a_propietario_actor_puntos(self, data):
        """ Envia a un cliente los puntos para que se los sume """
        self._server.enviar_a_propietario_actor_puntos(data)
        
    def Network_notificar_perdedores(self, data):
        """ Notifica al resto de clientes que son los perdedores """
        self._server.enviar_al_resto(data, self)
    
    def Close(self):
        """ Cierra la conexion con el servidor """
        self._server.eliminar_cliente(self)


class ServidorPilas(Server):
    """
    Clase que controla el flujo de las conexiones con los 
    distintos clientes 
    """

    channelClass = CanalCliente
    
    def __init__(self, puerto_servidor=31425):
        Server.__init__(self, localaddr=(pilas.red.obteber_ip_local(), puerto_servidor))
        #print "Servidor iniciado en el pueto :" , puerto_servidor
        self._clientes = WeakKeyDictionary()
        self.actores = []

    def actualizar(self):
        self.Pump()
        
    def Connected(self, channel, addr):
        #print "Cliente agregado"
        self.agregar_Cliente(channel)
            
    def agregar_Cliente(self, cliente):
        #print "Nuevo Cliente " + str(cliente.addr)
        self._clientes[cliente] = True
        self.enviar_actores_a_cliente(cliente)
    
    def eliminar_cliente(self, cliente):
        #print "Eliminando Cliente " + str(cliente.addr)
        for actor in self.actores:
            if (actor['cliente'].addr == cliente.addr):
                self.enviar_al_resto({"action" : "eliminar_actor", 
                                      "id" : actor['id'],
                                      "control" : Actor.REMOTO,
                                      "destruir" : False}, cliente)
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
    
    def enviar_a_propietario_actor_puntos(self, data):
        for actor in self.actores:            
            if (actor['id'] == data['id']):
                actor['cliente'].Send(data)
                break
        
class ActorObserver():
    def cambioEnActor(self, event):
        raise NotImplementedError("Debe implementar el metodo cambioEnActor " +
                                  "para Observar los cambios de los actores.")

class EscucharServidor(ConnectionListener):
    """ 
    Clase que implementa las peticiones que le llegan desde el servidor.    
    """
    def Network(self, data):
        pass #print 'network data:', data
            
    def Network_connected(self, data):
        pilas.avisar("Conectado al servidor")
        
    def Network_disconnected(self, data):        
        pilas.avisar("Desconectado del servidor")    
        
    def Network_error(self, data):
        pilas.avisar(data['error'][1])

    def Network_crear_actor(self, data):
        """ Crea un actor de otro Cliente """
        exec("from  " + data['modulo'] + " import " + data['clase'])
        clase_actor = eval(data['clase'])
        actor = clase_actor(control=Actor.REMOTO)
        actor.id = data['id']
        actor.x = data['x']
        actor.y = data['y']
        actor.escala_x = data['escala_x']
        actor.escala_y = data['escala_y']
        actor.rotacion = data['rotacion']
        self.agregar_actor_remoto(actor)
    
    def Network_mover_actor(self, data):
        """ Mueve un actor de otro cliente """
        for actor in self._actores_remotos:
            if (isinstance(actor, Actor) and actor.id == data['id']):
                actor.x = data['x'] 
                actor.y = data['y']
                actor.escala_x = data['escala_x']
                actor.escala_y = data['escala_y']
                actor.rotacion = data['rotacion']
                break
            
    def Network_enviar_actores_a_cliente(self, data):
        """ Envia todos sus actores a otro Cliente """
        for actor in self._actores_locales:
            if (isinstance(actor, Actor)):
                connection.Send({"action" : "crear_actor_en_cliente",
                                 "cliente" : data['cliente'],
                                 "modulo" : actor.__class__.__module__ ,
                                 "clase" : actor.__class__.__name__ , 
                                 "id" : actor.id,
                                 "x" : actor.x,
                                 "y" : actor.y,
                                 "escala_x" : actor.escala_x,
                                 "escala_y" : actor.escala_y,
                                 "rotacion" : actor.rotacion})

    def Network_eliminar_actor(self, data):
        """ Elimina un actor ya sea local o remoto """
        if (data['control'] == Actor.LOCAL):
            for actor in self._actores_remotos:
                if (isinstance(actor, Actor) and actor.id == data['id']):
                    actor = self._actores_remotos.pop(self._actores_remotos.index(actor))
                    if (data['destruir'] == 'True'):
                        actor.destruir()
                    else:
                        actor.eliminar()
                    break
        if (data['control'] == Actor.REMOTO):                
            for actor in self._actores_locales:
                if (isinstance(actor, Actor) and actor.id == data['id']):
                    actor = self._actores_locales.pop(self._actores_locales.index(actor))
                    if (data['destruir'] == 'True'):
                        actor.destruir()
                    else:
                        actor.eliminar()
                    break


    def Network_enviar_a_propietario_actor_puntos(self, data):
        """ Recibe los puntos que le hayan enviado y los suma a los que
        ya tiene """
        self.puntos += int(data['puntos'])
        
    def Network_notificar_perdedores(self, data):
        """ Muestra la escena por haber perdido """
        self.escena_perdedor()

class EscenaRed(Normal, EscucharServidor, ActorObserver):
    """ Clase para crear una escena que permite jugar en red.
    Se debe indicar si se quiere ser cliente o servidor mediante el parametro
    "rol" que se pasa al constructor.
    
    SERVIDOR
    EscenaRed.__init__(self,'servidor', ip_servidor=192.168.0.30)
    
    CLIENTE
    EscenaRed.__init__(self,'cliente', ip_servidor=192.168.0.30)
    
    También se puede establecer el puerto donde escuchará el servidor y por el
    que deberá conectar el cliente mediante el parametro "puerto_servidor".
    
    Podemos obtener la ip local mediante:
    pilas.net.obteber_ip_local()
    
    """    
    
    def __init__(self, rol='cliente', ip_servidor='127.0.0.1', 
                 puerto_servidor=31425):
        
        Normal.__init__(self)
        
        # Crea un conector para actualizar la escena
        pilas.eventos.actualizar.conectar(self.actualizar)
        
        # Lista para guardar los actores locales
        self._actores_locales = []
        
        # Lista para guardar los actores remotos
        self._actores_remotos = []
        
        # Variable para guardar los puntos de una partida si es necesario.
        self.puntos = 0
        
        # Agregamos la colisiones de los actores locales con los remotos.
        pilas.mundo.colisiones.agregar(self._actores_locales, 
                                       self._actores_remotos, 
                                       self.colision_con_actores_remotos)
        
        # Agregamos la colisiones de los actores locales con los propios
        # locales.
        pilas.mundo.colisiones.agregar(self._actores_locales, 
                                       self._actores_locales, 
                                       self.colision_con_actores_locales)

                
        self.servidor = None
        # Si la escena es un servidor, lo creamos.
        if (rol == 'servidor'):
            self.servidor = ServidorPilas(puerto_servidor=31425)

        # Conectamos con el servidor.
        self.Connect((ip_servidor, puerto_servidor))
        
    def aumentar_puntos(self, cantidad):
        """ Aumenta los puntos del jugador """
        self.puntos += cantidad
    
    def soy_cliente(self):
        """ Comprueba si es cliente o servidor """
        if (self.servidor == None):
            return True
        else:
            return False 
    
    def escena_ganador(self):
        """ Muestra la escena del ganador y notifica a los perdedores. """
        for actor in self._actores_locales:
            actor.destruir()
        for actor in self._actores_remotos:
            actor.destruir()

        
        connection.Send({"action" : "notificar_perdedores"})
        
        connection.Pump()
        self.Pump()
        
        Escena_Ganador()
    
    def escena_perdedor(self):
        """ Muestra la escena del pededor """
        for actor in self._actores_locales:
            actor.destruir()
        for actor in self._actores_remotos:
            actor.destruir()
            
        Escena_Perdedor()

    def enviar_a_propietario_actor_puntos(self, actor, puntos=1):
        """ 
        Envia al propietario de un actor un número de puntos especificos 
        """
        connection.Send({"action" : "enviar_a_propietario_actor_puntos",
                                 "id" : actor.id,
                                 "puntos" : puntos})
        
    def colision_con_actores_remotos(self, acto_local, actor_remoto):
        """ Metodo que se debe sobreescribir para controlar las colisiones """
        raise NotImplementedError("colision_con_actores_remotos(self, acto_local, actor_remoto): No implementado.")
    
    def colision_con_actores_locales(self, acto_local1, actor_local2):
        """ Metodo que se debe sobreescribir para controlar las colisiones """
        raise NotImplementedError("colision_con_actores_locales(self, acto_local1, actor_local2): No implementado.")

    def agregar_actor_local(self, actor, notificar=True):
        """ 
        Agrega un actor local.
        - notificar : Si se establece a True notifica al resto de clientes
        para que creen dicho actor en su Escena
        """
        if not isinstance(actor, list):
            actor = [actor]
        
        for a in actor:
            if (isinstance(a, Actor)):
                a.conectarObservador(self)            
                a.id = str(uuid.uuid4())
                self._actores_locales.append(a)
                if (notificar):
                    connection.Send({"action" : "crear_actor",
                                 "modulo" : a.__class__.__module__,
                                 "clase" : a.__class__.__name__ , 
                                 "id" : a.id,
                                 "x" : a.x,
                                 "y" : a.y,
                                 "escala_x" : a.escala_x,
                                 "escala_y" : a.escala_y,
                                 "rotacion" : a.rotacion})

    def eliminar_actor_local(self, actor, notificar=True, destruir=False):
        """
        Elimina un actor local.
        - notificar : Si se establece a True notifica al resto de clientes
        para que creen dicho actor en su Escena
        - destruir : Si se establece a True el actor se elimina mediante
        actor.destruir(). Si se establece a False se ejecuta actor.eliminar()
        """
        
        id = actor.id
        actor.desconectarObservador(self)
        actor = self._actores_locales.pop(self._actores_locales.index(actor))
        if (destruir):
            actor.destruir()                        
        else:
            actor.eliminar()
            
        if (notificar):
            data = {"action" : "eliminar_actor",
                             "id" : id,
                             "control" :  actor.control,
                             "destruir" : destruir}
            connection.Send(data)

    
    def agregar_actor_remoto(self, actor):
        """ Agrega un actor a la lista de actores remotos """
        self._actores_remotos.append(actor)
    
    def eliminar_actor_remoto(self, actor_remoto, notificar=True, 
                              destruir=False):
        """
        Elimina un actor local.
        - notificar : Si se establece a True notifica al resto de clientes
        para que creen dicho actor en su Escena
        - destruir : Si se establece a True el actor se elimina mediante
        actor.destruir(). Si se establece a False se ejecuta actor.eliminar()
        """
        
        id = actor_remoto.id
        actor_remoto = self._actores_remotos.pop(self._actores_remotos.index(actor_remoto))
        if not(destruir):
            actor_remoto.eliminar()
        else:
            actor_remoto.destruir()
        if (notificar):
            connection.Send({"action" : "eliminar_actor",
                             "id" : id,
                             "control" :  actor_remoto.control,
                             "destruir" : destruir})

    def cambioEnActor(self, data):
        """ Si han habido cambios en un actor local lo notifica a los clientes
        para que efectuen la actualizacion """
        accion = {"action": "mover_actor"}
        connection.Send (dict(accion.items() + data.items()))
             
    def actualizar(self, evento):
        # Actualizamos el servidor si existe.
        if (self.servidor != None):
            self.servidor.actualizar()
        
        connection.Pump()
        self.Pump()
        
        
class Escena_Ganador(Normal):
    def __init__(self):
        Normal.__init__(self)
        texto = pilas.actores.Texto("HAS GANADO")
        texto.color = pilas.colores.negro

class Escena_Perdedor(Normal):
    def __init__(self):
        Normal.__init__(self)
        texto = pilas.actores.Texto("HAS PERDIDO")
        texto.color = pilas.colores.negro
        
        