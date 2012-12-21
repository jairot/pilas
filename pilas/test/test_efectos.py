# Permite que este ejemplo funcion incluso si no has instalado pilas.
import sys
sys.path.insert(0, "/home/quique/git/pilas/")
import pilas
from pilas.efecto import Lluvia

pilas.iniciar()

class Escena(pilas.escena.Base):

    def __init__(self):
        pilas.escena.Base.__init__(self)
        self.actualizar.conectar(self.actualizar_escena)

    def iniciar(self):
        self.pingu = pilas.actores.Pingu(y=-200)
        self.lluvia = Lluvia(velocidad_viento=0)
        pilas.fondos.Tarde()

    def actualizar_escena(self, evento):
        self.lluvia.actualizar()


pilas.cambiar_escena(Escena())
pilas.ejecutar()
