# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

# Permite que este ejemplo funcion incluso si no has instalado pilas.

import sys

sys.path.insert(0, "../../../..")

import random

import pilas
from pilas.escenas import Normal
from pilas.actores import *
from pilas.red import *

import actores


class Escena_Parametros(Normal):
    
    def __init__(self):
        Normal.__init__(self)
        pilas.fondos.Selva()
        
        # Titulo
        self.titulo = pilas.actores.Texto("Comer Bananas")
        self.titulo.color = pilas.colores.negro
        self.titulo.y = 180

        self.boton_servidor = pilas.interfaz.Boton("Servidor")
        self.boton_servidor.conectar(self.conectar_servidor)
        
        self.texto_ip_servidor = pilas.interfaz.IngresoDeTexto(obteber_ip_local(), ancho=200)
        self.texto_ip_servidor.y = -110                
        
        self.boton_cliente = pilas.interfaz.Boton("Cliente")
        self.boton_cliente.y = -80
        self.boton_cliente.conectar(self.conectar_cliente)
        
    def conectar_servidor(self):
        ComerBananas(pilas.red.SERVIDOR)
        
    def conectar_cliente(self):
        ComerBananas(pilas.red.CLIENTE, ip_servidor=self.texto_ip_servidor.texto)


class ComerBananas(EscenaRed):
    
    def __init__(self, rol, ip_servidor=obteber_ip_local()):
        EscenaRed.__init__(self,rol,ip_servidor=ip_servidor)
        
        pilas.fondos.Selva()
        
        self.crear_mono()
        
        self.puntaje = pilas.actores.Puntaje(x=-300,y=220)
        
    def crear_mono(self):
        
        rand_x = random.randint(-320,320)
        rand_y = -210
        self.mi_mono = pilas.actores.Mono(rand_x, rand_y)
        self.agregar_actor_local(self.mi_mono)
        self.mi_mono.aprender(pilas.habilidades.MoverseConElTeclado)
        self.mi_mono.aprender(pilas.habilidades.SeMantieneEnPantalla)
        self.mi_mono.escala = 0.5
    
    def crear_banana(self):
        x = random.randint(-320,320)
        y = 220
        banana = pilas.actores.Banana(x, y)
        banana.aprender(pilas.habilidades.RebotarComoPelota)
        self.agregar_actor_local(banana)
        
    
    def colision_con_actores_remotos(self, actor_local, actor_remoto):
        if (isinstance(actor_local, pilas.actores.Mono) and isinstance(actor_remoto, pilas.actores.Banana)):
            self.mi_mono.sonreir()
            self.puntos += 1           
            self.eliminar_actor_remoto(actor_remoto, notificar=False)
        elif (isinstance(actor_local, pilas.actores.Banana) and isinstance(actor_remoto, pilas.actores.Mono)):
            self.eliminar_actor_local(actor_local, notificar=False)
            actor_remoto.sonreir()
                                           
    def colision_con_actores_locales(self, actor_local1, actor_local2):
        if (isinstance(actor_local1, pilas.actores.Mono) and isinstance(actor_local2, pilas.actores.Banana)):
            self.eliminar_actor_local(actor_local2)
            self.puntos += 1
            actor_local1.sonreir()
    
    def actualizar(self, evento):

        if (self.mi_mono.y >= -100):
            self.mi_mono.y = -100
    
        if not(self.soy_cliente()):
            aleatorio = random.randint(0,100)
            if (aleatorio == 50 ):
                self.crear_banana()
        
        self.puntaje.texto = "Puntos:" + str(self.puntos)
        if (self.puntos == 10):
            self.escena_ganador()
        
        EscenaRed.actualizar(self, evento)
    
pilas.iniciar(titulo="Comer Bananas")

Escena_Parametros()

pilas.ejecutar()
