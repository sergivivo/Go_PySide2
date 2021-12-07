import threading
import pickle

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from board import Board
from thread import ThreadPlayer

class BoardView(QGraphicsView):
    giveTurn = Signal()
    def __init__(self, parent=None):
        super(BoardView, self).__init__()

        self.viewSize = 855
        self.setFixedSize(self.viewSize, self.viewSize)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.serverMode = False
        self.sock = None
        self.player = True

    def loadBoard(self, size):
        self.scene = QGraphicsScene()

        # Background
        brush = QBrush(QColor(255,178,102,255))
        self.scene.setBackgroundBrush(brush)
        self.scene.setSceneRect(0,0,self.viewSize,self.viewSize)

        # Lines
        self.hitbox = self.viewSize / size
        half = self.hitbox/2
        for i in range(size):
            self.scene.addLine(i*self.hitbox+half, half, i*self.hitbox+half, self.viewSize-half)
            self.scene.addLine(half, i*self.hitbox+half, self.viewSize-half, i*self.hitbox+half)

        # Doted intersections
        brush = QBrush(QColor(0,0,0,255))
        thirdline = 2*self.hitbox+half
        fourthline = 3*self.hitbox+half
        if size == 19:
            self.scene.addEllipse(fourthline-3, fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-fourthline-3, fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(fourthline-3, self.viewSize-fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-fourthline-3, self.viewSize-fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(fourthline-3, self.viewSize/2-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize/2-3, fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-fourthline-3, self.viewSize/2-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize/2-3, self.viewSize-fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize/2-3, self.viewSize/2-3, 6, 6, brush=brush)
        elif size == 13:
            self.scene.addEllipse(fourthline-3, fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-fourthline-3, fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(fourthline-3, self.viewSize-fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-fourthline-3, self.viewSize-fourthline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize/2-3, self.viewSize/2-3, 6, 6, brush=brush)
        elif size == 9:
            self.scene.addEllipse(thirdline-3, thirdline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-thirdline-3, thirdline-3, 6, 6, brush=brush)
            self.scene.addEllipse(thirdline-3, self.viewSize-thirdline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize-thirdline-3, self.viewSize-thirdline-3, 6, 6, brush=brush)
            self.scene.addEllipse(self.viewSize/2-3, self.viewSize/2-3, 6, 6, brush=brush)


        # Game board initialization
        self.board = Board(size)
        self.board.startGame()

        self.setScene(self.scene)
        self.resetMatrix()

    def mouseReleaseEvent(self, event):
        if not self.serverMode or self.isCurrentPlayer():
            pos = self.mapToScene(event.pos())
            if 0 <= pos.y() < self.viewSize and 0 <= pos.x() < self.viewSize:
                i = int(pos.y()/self.hitbox)
                j = int(pos.x()/self.hitbox)

                # Tries to play the move and test if it is valid
                self.board.gameAction(i,j)
                if self.board.getValidated():
                    self.updateBoardView()

                    # If serverMode, send move to the other player
                    if self.serverMode:
                        self.sock.sendall(pickle.dumps([i,j]))
                        self.giveTurn.emit()

    def updateBoardView(self):
        # New placed stone update
        x = self.board.getLastPlayed()
        player = self.board.getBoard()[x[0]][x[1]]
        if player == 1:
            brush = QBrush(QColor(0,0,0,255))
            self.scene.addEllipse(x[1]*self.hitbox,x[0]*self.hitbox,self.hitbox,self.hitbox, brush=brush)
        elif player == -1:
            brush = QBrush(QColor(255,255,255,255))
            self.scene.addEllipse(x[1]*self.hitbox,x[0]*self.hitbox,self.hitbox,self.hitbox, brush=brush)

        # If any was captured, delete
        stones = self.board.getCaptured()
        for x in stones:
            self.scene.removeItem(self.scene.itemAt(
                        x[1]*self.hitbox+self.hitbox/2,
                        x[0]*self.hitbox+self.hitbox/2,
                        QTransform()))

    def enableServerMode(self, sock, player):
        self.serverMode = True
        self.sock = sock
        self.player = player
        self.createQThread()

    def createQThread(self):
        self.thread = QThread()
        self.tplayer = ThreadPlayer(self.sock)
        self.tplayer.moveToThread(self.thread)

        self.thread.started.connect(self.tplayer.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.tplayer.finished.connect(self.thread.quit)
        self.tplayer.finished.connect(self.tplayer.deleteLater)
        self.tplayer.finished.connect(self.disableServerMode)
        self.tplayer.datasignal.connect(self.getResponse)

        self.giveTurn.connect(self.tplayer.takeTurn)

        self.thread.start()

        if not self.isCurrentPlayer():
            self.giveTurn.emit()

    def disableServerMode(self):
        self.serverMode = False
        self.sock.close()

    @Slot(list)
    def getResponse(self, action):
        self.board.gameAction(action[0], action[1])
        self.updateBoardView()

    def isCurrentPlayer(self):
        return self.board.getCurrentPlayer() == self.player

