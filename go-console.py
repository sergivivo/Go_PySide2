import random as rand

class Tablero():

    LEGEND = {0: " ", 1: "X", -1: "O"}

    def __init__(self, size):
        self.size = size
        self.tablero = [[0 for i in range(size)] for i in range(size)]
        self.ko = None

    def _startGame(self, komi=6.5):
        move = 0
        end  = 0
        giveup = False
        self.history = []
        while not giveup and end < 2:
            validate = False
            while not validate:
                print(self)
                print("Actions: letter+number | giveup | pass | end")

                # Checking user input format
                strturn = "Black" if move % 2 == 0 else "White"
                userinput = input("{}'s turn: ".format(strturn))
                validAction, msg = self._validateInput(move % 2 == 0, userinput)
                if not validAction:
                    print("    " + msg)
                    print("    Example of valid input -> {}{}".format(
                        chr(ord('a') + rand.randrange(self.size)),
                        rand.randrange(self.size)))
                else:
                    if validAction[1] not in [-1,0,1]:
                        # Checking if the move is valid
                        validMove, msg = self._validateMove(validAction)
                        if not validMove:
                            print("    " + msg)
                            print("    Try another position to play!")
                        else:
                            validate = True
                        end = 0
                    else:
                        validate = True
                        if validAction[1] == -1:
                            giveup = True
                        elif validAction[1] == 1:
                            end += 1

            self.history.append(validAction)
            move += 1

    def _validateInput(self, player, userinput):
        if userinput == "giveup":
            return [player, -1], ""
        elif userinput == "pass":
            return [player, 0], ""
        elif userinput == "end":
            return [player, 1], ""
        else:
            try:
                letter = userinput[0]
                number = userinput[1:]

                row = self.size - int(number)
                column = ord(letter) - ord('a')

                if row not in range(self.size):
                    return None, "Number out of the bounds of the board"
                if column not in range(self.size):
                    return None, "Letter out of the bounds of the board"

                return [player, [row, column]], ""

            except ValueError:
                return None, "Only a number must follow after a single letter"
            except:
                return None, "Unrecognizable input"

    def _validateMove(self, action):
        player = 1 if action[0] else -1
        row = action[1][0]
        column = action[1][1]
        position = self.tablero[row][column]

        # Check if already occupied
        if position != 0:
            return False, "Position already occupied"

        # Check Ko
        if self.ko:
            if player == self.ko[0] and row == self.ko[1] and column == self.ko[2]:
                return False, "Can't play Ko until next turn"

        # Place the stone
        self.tablero[row][column] = player

        # Capturing before suicide
        adjacent = self._getAdjacent(row,column)
        captured = []
        for x in adjacent:
            if self.tablero[x[0]][x[1]] != player:
                stones, liberties = self._getStonesAndLiberties(x[0],x[1])
                if stones and liberties == 0:
                    captured += stones
                    for y in stones:
                        self.tablero[y[0]][y[1]] = 0

        # Check suicide
        stones, liberties = self._getStonesAndLiberties(row, column)
        if liberties == 0:
            self.tablero[row][column] = 0
            return False, "That move is suicide"

        # Update Ko
        if len(captured) == 1 and len(stones) == 1 and liberties == 1:
            oponent = -1 if player == 1 else 1
            self.ko = [oponent, captured[0][0], captured[0][1]]
        else:
            self.ko = None

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
        player = self.tablero[row][column]
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
            samecolor = [x for x in adjacent if self.tablero[x[0]][x[1]] == player]
            tocheck += [x for x in samecolor if x not in checked+tocheck]

            # Add liberties that are not already in list
            locallib = [x for x in adjacent if self.tablero[x[0]][x[1]] == 0]
            liberties += [x for x in locallib if x not in liberties]

            checked.append(checking)

        return checked, len(liberties)

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
                s += Tablero.LEGEND[self.tablero[i][j]] + " "
            s += "#\n"

        s += "#####"
        for j in range(self.size):
            s += "##"
        s += "#"

        return s

if __name__ == "__main__":
    tablero = Tablero(19)
    tablero._startGame(6.5)
    print(tablero)
