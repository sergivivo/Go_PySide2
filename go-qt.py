#!/usr/bin/env python

import threading
import socket
import sys

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from boardview import BoardView

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()

        # Initiate the board
        self.board = BoardView(self)
        self.board.loadBoard(19)

        # Menu
        self.menu = self.menuBar()

        difi = self.menu.addMenu("Board")
        prin = QAction( "9x9" ,self)
        avan = QAction("13x13",self)
        expe = QAction("19x19",self)
        prin.triggered.connect(lambda: self.board.loadBoard( 9))
        avan.triggered.connect(lambda: self.board.loadBoard(13))
        expe.triggered.connect(lambda: self.board.loadBoard(19))
        difi.addAction(prin)
        difi.addAction(avan)
        difi.addAction(expe)

        server = self.menu.addMenu("Server")
        servstart = QAction("Start server", self)
        servconnect = QAction("Connect to server", self)
        servstart.triggered.connect(self.startServer)
        servconnect.triggered.connect(self.connectServer)
        server.addAction(servstart)
        server.addAction(servconnect)

        # Vertical box layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.board)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def createThread(self,target):
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    def startServer(self):
        HOST = socket.gethostbyname(socket.gethostname())
        PORT = 65432
        self.conn, addr = None, None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST,PORT))
        self.sock.listen()

        print("Server listening at {}".format((HOST,PORT)))
        self.createThread(self.serverWait)

    def serverWait(self):
        self.conn, addr = self.sock.accept()
        print("Client at {} connected successfully".format(addr))
        self.board.enableServerMode(self.conn, True)

    def connectServer(self):
        HOST = "192.168.0.16"
        PORT = 65432

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST,PORT))
        self.board.enableServerMode(self.sock, False)

if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
