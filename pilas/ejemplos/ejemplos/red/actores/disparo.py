# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar
import pilas
from pilas.actores import Actor
import math

class Disparo(Actor):
    "Representa un disparo que avanza."

    def __init__(self, x=0, y=0, rotacion=0, velocidad=5, control=Actor.LOCAL):
        Actor.__init__(self, x=x, y=y, control=control)
        self.velocidad = velocidad
        self.imagen = pilas.imagenes.cargar_imagen("data/disparo.png")
        self.aprender(pilas.habilidades.PuedeExplotar)
        self.radio_de_colision = 4
        self.tiempo_activo = 100
        self.rotacion = rotacion   
        self.listeners = []
        
        self.evento_destruir = pilas.eventos.Evento("Destruir Disparo")   

    def actualizar(self):
        self.avanzar()
        self.tiempo_activo -= 1
        if (self.tiempo_activo < 0):
            self.evento_destruir.emitir(bala=self)
            self.destruir()

    def avanzar(self):
        "Hace avanzar la nave en direccion a su angulo."
        rotacion_en_radianes = math.radians(-self.rotacion + 90)
        dx = math.cos(rotacion_en_radianes) * self.velocidad
        dy = math.sin(rotacion_en_radianes) * self.velocidad
        self.x += dx
        self.y += dy
        
class CrossHair(Actor):
    
    def __init__(self, x=0, y=0):
        Actor.__init__(self, x=x, y=y)
        self.imagen = pilas.imagenes.cargar_imagen("data/crosshair.png")
        
class DisparoTriple(Actor):
    def __init__(self, x=0, y=0, control=Actor.LOCAL):
        Actor.__init__(self, x=x, y=y, control=control)
        self.imagen = pilas.imagenes.cargar_imagen("data/power.png")        