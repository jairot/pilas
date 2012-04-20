# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

import pilas
from pilas.actores import Actor

class Velocidad(Actor):
    def __init__(self, x=0, y=0, control=Actor.LOCAL):
        Actor.__init__(self, x=x, y=y, control=control)
        self.imagen = pilas.imagenes.cargar_imagen("data/bota.png")  