# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2010 - hugo ruscitti
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar
import socket
from escenas import ServidorPilas
from escenas import EscenaRed

def obteber_ip_local():
    return socket.gethostbyname(socket.gethostname())