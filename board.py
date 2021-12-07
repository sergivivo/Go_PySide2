class Board():

    LEGEND = {0: " ", 1: "X", -1: "O"}

    def __init__(self, size):
        self.size = size
        self.board = [[0 for i in range(size)] for i in range(size)]

    def startGame(self, komi=6.5):
        self.ko = None
        self.move = 0
        self.komi = komi
        self.history = []

    def gameAction(self, i, j):
        player = self.move % 2 == 0
        userinput = [i,j]
        action = [player, userinput]
        self.validated, msg = self._validateMove(action)
        if self.validated:
            self.history.append(action)
            self.move += 1

    def _validateMove(self, action):
        player = 1 if action[0] else -1
        row = action[1][0]
        column = action[1][1]
        position = self.board[row][column]

        # Check if already occupied
        if position != 0:
            return False, "Position already occupied"

        # Check Ko
        if self.ko:
            if player == self.ko[0] and row == self.ko[1] and column == self.ko[2]:
                return False, "Can't play Ko until next turn"

        # Place the stone
        self.board[row][column] = player

        # Capturing before suicide
        adjacent = self._getAdjacent(row,column)
        self.captured = []
        for x in adjacent:
            if self.board[x[0]][x[1]] != player:
                stones, liberties = self._getStonesAndLiberties(x[0],x[1])
                if stones and liberties == 0:
                    self.captured += stones
                    for y in stones:
                        self.board[y[0]][y[1]] = 0

        # Check suicide
        stones, liberties = self._getStonesAndLiberties(row, column)
        if liberties == 0:
            self.board[row][column] = 0
            return False, "That move is suicide"

        # Update Ko
        if len(self.captured) == 1 and len(stones) == 1 and liberties == 1:
            oponent = -1 if player == 1 else 1
            self.ko = [oponent, self.captured[0][0], self.captured[0][1]]
        else:
            self.ko = None

        self.lastplayed = [row,column]
        return True, ""

    def _getAdjacent(self, row, column):
        block = [[i,j] for i in range(max(row-1   , 0), min(row+2   , self.size))
                       for j in range(max(column-1, 0), min(column+2, self.size))]

        adjacent = []
        for x in block:
            parity = (row+column)%2
            if (x[0]+x[1])%2 != parity:
                adjacent.append(x)

        return adjacent

    def _getStonesAndLiberties(self, row, column):
        player = self.board[row][column]
        if player == 0:
            return None, None

        # Will store adjacent connected stones
        tocheck = [[row,column]]
        checked = []

        # Will store liberties
        liberties = []

        while len(tocheck) > 0:
            checking = tocheck.pop()

            adjacent = self._getAdjacent(checking[0],checking[1])

            # Add adjacent stones that are not already in list
            samecolor = [x for x in adjacent if self.board[x[0]][x[1]] == player]
            tocheck += [x for x in samecolor if x not in checked+tocheck]

            # Add liberties that are not already in list
            locallib = [x for x in adjacent if self.board[x[0]][x[1]] == 0]
            liberties += [x for x in locallib if x not in liberties]

            checked.append(checking)

        return checked, len(liberties)

    def getLastPlayed(self):
        return self.lastplayed

    def getCaptured(self):
        return self.captured

    def getBoard(self):
        return self.board

    def getValidated(self):
        return self.validated

    def getCurrentPlayer(self):
        return self.move % 2 == 0

    def __str__(self):
        """Print whole board"""
        s = "   # "
        for j in range(self.size):
            s += chr(ord('a') + j) + " "
        s += "#\n#####"
        for j in range(self.size):
            s += "##"
        s += "#\n"

        for i in range(self.size):
            s += str(self.size - i).rjust(2, ' ') + " # "
            for j in range(self.size):
                s += Board.LEGEND[self.board[i][j]] + " "
            s += "#\n"

        s += "#####"
        for j in range(self.size):
            s += "##"
        s += "#"

        return s

