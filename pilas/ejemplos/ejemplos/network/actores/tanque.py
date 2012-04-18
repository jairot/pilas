# -*- encoding: utf-8 -*-

import pilas
from pilas.actores import Actor

import math

import disparo
import humo

class Tanque(Actor):
    
    VELOCIDAD_RECARGA = 1

    def __init__(self, x=0, y=0,id='', control=Actor.LOCAL):
        Actor.__init__(self, x=x, y=y, control=control)
        self.id = id
        
        self.velocidad = 2
        self.imagen = pilas.imagenes.cargar_imagen("data/tanque.png")
        self.aprender(pilas.habilidades.PuedeExplotar)
        
        self.radio_de_colision = 15
        
        self.disparo_triple = False
        self.contador_frecuencia_disparo = 0
                
        
        self.disparos = []
        self.evento_disparar = pilas.eventos.Evento("Disparo Tanque")

        if (self.control == Actor.LOCAL):
            self.barra_recarga = pilas.actores.Energia(self.x, self.y + 22, progreso=100, ancho=50, alto = 6, con_brillo=False, con_sombra=False)
            self.barra_vida = pilas.actores.Energia(self.x, self.y + 30 , progreso=100, ancho=50, alto = 6, color_relleno=pilas.colores.rojo, con_brillo=False, con_sombra=False)
            self.anexar(self.barra_recarga)
            self.anexar(self.barra_vida)
    
    def set_id(self, id):
        self.id = id
    
    def actualizar(self):
        if (self.control == Actor.LOCAL):
            if self.barra_recarga.progreso < 100:
                self.barra_recarga.progreso += self.VELOCIDAD_RECARGA

            if pilas.mundo.control.izquierda:
                self.rotacion -= self.velocidad
            elif pilas.mundo.control.derecha:
                self.rotacion += self.velocidad
                
            if pilas.mundo.control.arriba:
                self.avanzar()
                self.actualizar_posicion_barras()
            elif pilas.mundo.control.abajo:
                self.retroceder()
                self.actualizar_posicion_barras()
            
            if pilas.mundo.control.boton:
                if self.barra_recarga.progreso >= 100:
                    self.barra_recarga.progreso = 0
                    if self.disparo_triple:
                        self.disparar_triple()
                        self.evento_disparar.emitir(tipo="triple")
                        self.disparo_triple = False
                    else:
                        self.disparar()
                        self.evento_disparar.emitir(tipo="simple")
            
    def actualizar_posicion_barras(self):
            self.barra_recarga.set_x(self.x)
            self.barra_recarga.set_y(self.y + 22)
            self.barra_vida.set_y(self.y + 30)
            self.barra_vida.set_x(self.x)

        #self.eliminar_disparos_innecesarios()
        
    def _crear_humo(self):
        humos = humo.Humo()
        rotacion_en_radianes = math.radians(-self.rotacion + 90)
        dx = math.cos(rotacion_en_radianes) * 25
        dy = math.sin(rotacion_en_radianes) * 25
        humos.x = self.x + dx
        humos.y = self.y + dy
    
    def avanzar(self):
        rotacion_en_radianes = math.radians(-self.rotacion + 90)
        dx = math.cos(rotacion_en_radianes) * self.velocidad
        dy = math.sin(rotacion_en_radianes) * self.velocidad
        self.x += dx
        self.y += dy
        
    def retroceder(self):
        rotacion_en_radianes = math.radians(-self.rotacion + 90)
        dx = math.cos(rotacion_en_radianes) * self.velocidad
        dy = math.sin(rotacion_en_radianes) * self.velocidad
        self.x -= dx
        self.y -= dy
    
    def quitar_vida(self, cantidad=50):
        self.barra_vida.progreso -= cantidad        
                
    def get_vida(self):
        return self.barra_vida.progreso
    
    def disparar(self):
        self._crear_humo()
        disparo_nuevo = disparo.Disparo(self.x, self.y, self.rotacion, 4)
        self.disparos.append(disparo_nuevo)                
        self.disparo = True
        self.disparo_triple = False
        
    def disparar_triple(self):
        self._crear_humo()
        disparo_nuevo_1 = disparo.Disparo(self.x, self.y, self.rotacion-5, 4)
        disparo_nuevo_2 = disparo.Disparo(self.x, self.y, self.rotacion, 4)
        disparo_nuevo_3 = disparo.Disparo(self.x, self.y, self.rotacion+5, 4)
        self.disparos.append(disparo_nuevo_1)                        
        self.disparos.append(disparo_nuevo_2)
        self.disparos.append(disparo_nuevo_3)
        self.disparo = True