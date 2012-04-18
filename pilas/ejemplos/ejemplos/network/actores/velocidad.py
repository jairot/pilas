# -*- encoding: utf-8 -*-

import pilas
from pilas.actores import Actor

class Velocidad(Actor):
    def __init__(self, x=0, y=0, control=Actor.LOCAL):
        Actor.__init__(self, x=x, y=y, control=control)
        self.imagen = pilas.imagenes.cargar_imagen("data/bota.png")  