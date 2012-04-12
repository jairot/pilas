import pilas
from pilas.escenas import Normal

class Escena_1(Normal):

   def __init__(self):
       Normal.__init__(self)
       pilas.actores.Aceituna()
       pilas.actores.Aceituna()
       pilas.actores.Aceituna()

       # al pulsar la tecla, tiene que haber 4 actores (tres aceitunas y el fondo)
       #pilas.eventos.click_de_mouse.conectar(self.conectar_servidor)
       pilas.eventos.pulsa_tecla.conectar(self.mostrar_actores)
       self.boton_conectar = pilas.interfaz.Boton("Conectar")
       self.boton_conectar.conectar(self.conectar_servidor)

   def conectar_servidor(self, evento):
       Escena_2()

   def mostrar_actores(self, evento):
       print "hay", len(pilas.actores.todos)
       print pilas.actores.todos

class Escena_2(Normal):

   def __init__(self):
       Normal.__init__(self)
       pilas.avisar("Pruebas")

       # al pulsar la tecla, tiene que haber 3 actores (el fondo, el texto, y
       # la sombra)
       pilas.eventos.pulsa_tecla.conectar(self.mostrar_actores)

       # luego de unos segundos, tiene que haber un solo actor.


   def mostrar_actores(self, evento):
       print "hay", len(pilas.actores.todos)
       print pilas.actores.todos

pilas.iniciar()
Escena_1()
pilas.ejecutar()