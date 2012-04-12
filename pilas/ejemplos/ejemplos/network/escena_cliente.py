import pilas
from pilas.escenas import Normal
from pilas.actores import Aceituna
from pilas.net.actor import PilasNetworkObject

# Permite que este ejemplo funcion incluso si no has instalado pilas.
import sys
sys.path.insert(0, "..")

class AceitunaNet(Aceituna, PilasNetworkObject):
    def __init__(self, x=0, y=0):
        Aceituna.__init__(self,x,y)
        PilasNetworkObject.__init__(self)

class Escena_Parametros(Normal):
    
    def __init__(self):
        Normal.__init__(self)
        pilas.fondos.Pasto()
        self.boton_conectar = pilas.interfaz.Boton("Conectar")
        self.boton_conectar.conectar(self.conectar_servidor)
        
    def conectar_servidor(self):
        Escena_Cliente()

class Escena_Cliente(pilas.net.EscenaCliente):
    
    def __init__(self):
        pilas.net.EscenaCliente.__init__(self)
        pilas.avisar("Conectado")
        pilas.eventos.click_de_mouse.conectar(self.crear_actor)

    def crear_actor(self, event):
        actor = AceitunaNet()
        actor.x = event.x
        actor.y = event.y
        
    def actualizar(self, evento):
        pilas.net.EscenaCliente.actualizar(self, evento)

pilas.iniciar()

Escena_Parametros()

pilas.ejecutar()
