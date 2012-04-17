import random

import pilas
from pilas.escenas import Normal
from pilas.actores import *
from pilas.net import *

import actores
from actores.tanque import Tanque
from actores.disparo import Disparo
from actores.disparo import DisparoTriple

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
    
    def crear_power_up(self):
        rand_x = random.randint(-320,320)
        rand_y = random.randint(-240,240)
        disparo_triple = DisparoTriple(x=rand_x, y=rand_y)
        self.agregar_actor_local(disparo_triple)
    
    def colision_con_actores_remotos(self, actor_local, actor_remoto):
        if (isinstance(actor_remoto, Disparo) and isinstance(actor_local, Tanque)):
            self.mi_tanque.quitar_vida()
            self.enviar_a_propietario_actor_puntos(actor_remoto, 5)           
            self.eliminar_actor_remoto(actor_remoto)
        elif (isinstance(actor_local, Tanque) and isinstance(actor_remoto, DisparoTriple)):
            self.eliminar_actor_remoto(actor_remoto)
            self.mi_tanque.disparo_triple = True   
                                           
    def colision_con_actores_locales(self, actor_local1, actor_local2):
        if (isinstance(actor_local1, Tanque) and isinstance(actor_local2, DisparoTriple)):
            self.eliminar_actor_local(actor_local2)
            self.mi_tanque.disparo_triple = True   
    
    def actualizar(self, evento):
        if (self.mi_tanque.disparo):
            if (self.mi_tanque.disparo_triple): 
                self.agregar_actor_local(self.mi_tanque.disparos[-1])
                self.mi_tanque.disparos[-1].evento_destruir.conectar(self.eliminar_bala)
                self.agregar_actor_local(self.mi_tanque.disparos[-2])
                self.mi_tanque.disparos[-2].evento_destruir.conectar(self.eliminar_bala)
                self.agregar_actor_local(self.mi_tanque.disparos[-3])
                self.mi_tanque.disparos[-3].evento_destruir.conectar(self.eliminar_bala)
                
            else:
                self.agregar_actor_local(self.mi_tanque.disparos[-1])
                self.mi_tanque.disparos[-1].evento_destruir.conectar(self.eliminar_bala)
                
            self.mi_tanque.disparo = False
        
        if (self.mi_tanque.get_vida() <= 0):
            self.eliminar_actor_local(self.mi_tanque)
            # Creamos uno nuevo
            self.crear_tanque()
    
        if not(self.soy_cliente()):
            aleatorio = random.randint(0,300)
            if (aleatorio == 50):
                self.crear_power_up()
        
        self.puntaje.texto = str(self.puntos)
        if (self.puntaje.texto == "20"):
            self.escena_ganador()
        
        EscenaNetwork.actualizar(self, evento)
    
    def eliminar_bala(self, datos_evento):       
        self.destruir_actor_local(datos_evento['bala'])
                
        


pilas.iniciar(titulo="Tanques Net")

Escena_Parametros()

pilas.ejecutar()
