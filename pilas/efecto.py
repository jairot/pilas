import pilas
import random

class Gota(object):
    "Representa una gota de lluvia."

    def __init__(self, x, y, velocidad=3, velocidad_viento=3):
        self.velocidad = velocidad
        self.x = x
        self.y = y
        self.largo = random.randrange(3,10)
        self.velocidad_viento = velocidad_viento
        self.grosor = random.randint(1,2)

    def actualizar(self):
        self.y += self.velocidad
        self.x += self.velocidad_viento

    def dibujar(self, pizarra):
        pizarra.linea(self.x, self.y, self.x + self.velocidad_viento, self.y - self.largo, grosor=self.grosor,color=pilas.colores.blanco)


class Lluvia(object):

    def __init__(self, velocidad_viento=5):
        self.pizarra = pilas.actores.Pizarra()
        self.gotas = []
        self.velocidad_viento = velocidad_viento
        self.crear_gotas(cantidad=10)

    def crear_gotas(self, cantidad=100):
        for i in range(1,cantidad):
            self.gotas.append(Gota(random.randrange(-320,320),240,velocidad=random.randint(2,3),velocidad_viento=self.velocidad_viento))

    def actualizar(self):
        self.pizarra.limpiar()
        if random.randint(1,6) == 5:
            if len(self.gotas) < 200:
                self.crear_gotas(cantidad=10)

        for gota in self.gotas:
            gota.y -= gota.velocidad
            gota.dibujar(self.pizarra)
            if (gota.y < -200):
                self.gotas.remove(gota)


