import pilas
from pilas.escenas import Normal
from pilas.actores import *


class Escena_Parametros(Normal):
    
    def __init__(self):
        Normal.__init__(self)
        pilas.fondos.Pasto()
        self.boton_servidor = pilas.interfaz.Boton("Servidor")
        self.boton_servidor.y = 100
        self.boton_servidor.conectar(self.conectar_servidor)
        
        self.texto_ip_servidor = pilas.interfaz.IngresoDeTexto(pilas.net.obteber_ip_local())
        
        self.boton_cliente = pilas.interfaz.Boton("Cliente")
        self.boton_cliente.y = -50
        self.boton_cliente.conectar(self.conectar_cliente)
        
    def conectar_servidor(self):
        MiEscena('servidor')
        
    def conectar_cliente(self):
        MiEscena('cliente', ip_servidor=self.texto_ip_servidor.texto)

class MiEscena(pilas.net.EscenaNetwork):
    
    def __init__(self, rol, ip_servidor=pilas.net.obteber_ip_local()):
        pilas.net.EscenaNetwork.__init__(self,rol,ip_servidor=ip_servidor)
        pilas.fondos.Tarde()
        pilas.avisar("Conectado")
        pilas.eventos.click_de_mouse.conectar(self.crear_actor)
        

    def colision_con_ajenos(self, actor_compartido, actor_ajeno):
        self.eliminar_Actor_Observado(actor_compartido)
    
    def crear_actor(self, event):
        actor = Aceituna()
        actor.x = event.x
        actor.y = event.y
        actor.aprender(pilas.habilidades.MoverseConElTeclado)
        actor.aprender(pilas.habilidades.AumentarConRueda)
        actor.aprender(pilas.habilidades.PuedeExplotar)
        self.agregar_Actor_Observado(actor)
        
    def actualizar(self, evento):
        pilas.net.EscenaNetwork.actualizar(self, evento)

pilas.iniciar()

Escena_Parametros()

pilas.ejecutar()
