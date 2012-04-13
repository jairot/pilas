# Permite que este ejemplo funcion incluso si no has instalado pilas.
import sys
sys.path.insert(0, "..")

import pilas
from pilas.escenas import Normal




class Escena_Servidor(pilas.net.EscenaServidor):
    
    def __init__(self):
        pilas.net.EscenaServidor.__init__(self)

    def actualizar(self, evento):
        pilas.net.EscenaServidor.actualizar(self, evento)
        

pilas.iniciar()

Escena_Servidor()

pilas.ejecutar()
