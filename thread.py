from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import pickle
import socket

class ThreadPlayer(QObject):
    datasignal = Signal(list)
    finished = Signal()

    def __init__(self, sock):
        super(ThreadPlayer, self).__init__()
        self.eventLoop = QEventLoop(self)
        self.sock = sock

    def takeTurn(self):
        self.eventLoop.exit()

    def run(self):
        while True:
            self.eventLoop.exec_() # Wait turn
            msg = self.sock.recv(1024)
            if not msg:
                break
            else:
                x = pickle.loads(msg)
                self.datasignal.emit(x)
        self.finished.emit()

