import random

import pilas
from pilas.escenas import Normal
from pilas.actores import *
from pilas.net import *

import actores
from actores.tanque import Tanque
from actores.disparo import Disparo

class Escena_Parametros(Normal):
    
    def __init__(self):
        Normal.__init__(self)
        pilas.fondos.Pasto()
        self.boton_servidor = pilas.interfaz.Boton("Servidor")
        self.boton_servidor.y = 100
        self.boton_servidor.conectar(self.conectar_servidor)
        
        self.texto_ip_servidor = pilas.interfaz.IngresoDeTexto(obteber_ip_local())
        
        self.boton_cliente = pilas.interfaz.Boton("Cliente")
        self.boton_cliente.y = -50
        self.boton_cliente.conectar(self.conectar_cliente)
        
    def conectar_servidor(self):
        MiEscena('servidor')
        
    def conectar_cliente(self):
        MiEscena('cliente', ip_servidor=self.texto_ip_servidor.texto)

class MiEscena(EscenaNetwork):
    
    def __init__(self, rol, ip_servidor=obteber_ip_local()):
        EscenaNetwork.__init__(self,rol,ip_servidor=ip_servidor)
        pilas.fondos.Pasto()
        
        self.crear_tanque()
        
        self.puntaje = pilas.actores.Puntaje(x=-300,y=220)
        
    def crear_tanque(self):
        rand_x = random.randint(-320,320)
        rand_y = random.randint(-240,240)
        self.mi_tanque = actores.tanque.Tanque(x=rand_x, y=rand_y)
        self.agregar_actor_local(self.mi_tanque)
    
    def colision_con_actores_remotos(self, actor_local, actor_remoto):
        if (isinstance(actor_remoto, Disparo)):
            self.mi_tanque.quitar_vida()            
            self.eliminar_actor_remoto(actor_remoto)
                                           
    
    def actualizar(self, evento):
        if (self.mi_tanque.disparo):
            self.agregar_actor_local(self.mi_tanque.disparos)
            self.mi_tanque.disparo = False
        
        if (self.mi_tanque.get_vida() <= 0):
            self.eliminar_actor_local(self.mi_tanque)
            # Creamos uno nuevo
            self.crear_tanque()
            
            
        EscenaNetwork.actualizar(self, evento)

pilas.iniciar()

Escena_Parametros()

pilas.ejecutar()
