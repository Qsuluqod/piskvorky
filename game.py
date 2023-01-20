from board import Board
from minimax import MiniMax


class Game:

    def __init__(self, ext: int, win_count: int, minimax_depth: int):

        # True = O, False = X
        self.switch = True
        self.ext = ext
        self.win_count = win_count
        self.depth = 0

        self.X = "X"
        self.O = "O"
        self.empty = " "

        self.board = Board(self)
        self.minimax_depth = minimax_depth
        self.minimax = MiniMax(self, minimax_depth)

    def clean(self):

        self.switch = True
        self.depth = 0
        self.board = Board(self)
        self.minimax = MiniMax(self, self.minimax_depth)

    def player_turn(self, symbol: str):

        row = self.ext + 1
        col = self.ext

        while row == self.ext or col == self.ext:
            row = self.ext + 1
            col = self.ext
            coors = input("Zadej, kam chceš položit {}: ".format(symbol))
            for coor in coors:
                try:
                    num = int(coor)
                    row %= (self.ext + 1)
                    row *= 10
                    row += num
                except ValueError:
                    try:
                        col = self.board.alphabet.index(coor.upper())
                    except ValueError:
                        col = self.ext

            row -= 1
            if row >= self.ext or col >= self.ext:
                continue
            if self.board.field[row][col].symbol != self.empty:
                print("Toto pole už je zabrané!")

        return row, col

    def play(self):

        self.switch = True
        while True:
            print(self.board)
            cur = self.O if self.switch else self.X
            row, col = self.player_turn(cur)
            self.board.add_symbol(row, col, cur)
            if self.check_end():
                break
            self.end_turn()

    def play_ai_vs_ai(self):

        self.switch = True
        while True:
            print(self.board)
            cur = self.O if self.switch else self.X
            row, col = self.minimax.choose_option(self.switch)
            self.board.add_symbol(row, col, cur)
            if self.check_end():
                break
            self.end_turn()

    def play_with_ai(self, ai_starts = True):

        self.switch = True
        while True:
            print(self.board)

            cur = self.O if self.switch else self.X
            if ai_starts:
                if self.switch:
                    row, col = self.minimax.choose_option(True)
                else:
                    row, col = self.player_turn(cur)
            else:
                if self.switch:
                    row, col = self.player_turn(cur)
                else:
                    row, col = self.minimax.choose_option(False)

            self.board.add_symbol(row, col, cur)

            if self.check_end():
                break
            self.end_turn()

    def play_without_switch(self):

        self.switch = True
        while True:
            print(self.board)
            row, col = self.player_turn(self.O)
            self.board.add_symbol(row, col, self.O)
            if self.check_end():
                break
            self.depth += 1

    def end_turn(self):

        self.switch = not self.switch
        self.depth += 1

    def check_end(self):

        if self.board.win_condition(self.switch, self.win_count):
            cur = self.O if self.switch else self.X
            print(self.board)
            print("Hráč {} vyhrál\n".format(cur))
            return True
        if self.board.space == 0:
            print(self.board)
            print("Remíza\n")
            return True
        return False

    def __str__(self):

        return self.board.__str__()
