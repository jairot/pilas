import pilas
from pilas.escenas import Normal
from pilas.actores import *


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
        actor = Aceituna()
        actor.x = event.x
        actor.y = event.y
        actor.aprender(pilas.habilidades.MoverseConElTeclado)
        self.agregarActorObservado(actor)
        
    def actualizar(self, evento):
        pilas.net.EscenaCliente.actualizar(self, evento)

pilas.iniciar()

Escena_Parametros()

pilas.ejecutar()
