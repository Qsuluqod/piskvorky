from copy import deepcopy
from math import inf


class Node:

    def __init__(self, symbol: str, row: int, col: int, ext: int):
        """
        Vygeneruje nové políčko
        :param symbol: symbol políčka
        :param row: řádek, v němž se políčko nachází
        :param col: sloupec, v němž se políčko nachází
        :param ext: rozměr hrací desky
        """
        self.symbol = symbol
        self.row = row
        self.col = col
        self.diagonal = row + col
        self.rev_diagonal = (ext - row - 1) + col

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.symbol


class Board:

    def __init__(self, game):

        """
        :param game: hra, v jaké se deska nachází
        """
        self.game = game
        self.ext = game.ext
        ext = self.ext
        self.X = game.X
        self.O = game.O
        self.empty = game.empty
        self.win_count = game.win_count

        # volné místo na šachovnici
        self.space = ext ** 2

        # kladné - vyhrává kolečko, záporné - vyhrává křížek
        self.score = 0

        # hrací pole
        self.field = [[Node(self.empty, row, col, ext) for col in range(ext)] for row in range(ext)]
        # relevantní políčka desky (ty v rozumné vzdálenosti od již položených políček)
        self.relevant = set()

        # vytvoření transpozice hracího pole
        self.transposition = [[None for _ in range(ext)] for _ in range(ext)]
        for x in range(ext):
            for y in range(ext):
                self.transposition[x][y] = self.field[y][x]

        # vytvoří diagonálních reprezentací hracího pole
        self.diagonal = [[] for _ in range(ext * 2 - 1)]  # /
        self.rev_diagonal = [[] for _ in range(ext * 2 - 1)]  # \

        for x in range(ext * 2 - 1):
            row = min(x, ext - 1)
            col = max(0, -ext + x + 1)
            rev_row = max(ext - x - 1, 0)
            for y in range(min(x + 1, ext * 2 - 1 - x)):
                self.diagonal[x].append(self.field[row][col])
                self.rev_diagonal[x].append(self.field[rev_row][col])
                row -= 1
                col += 1
                rev_row += 1

        self.fields = [self.field, self.transposition, self.diagonal, self.rev_diagonal]

        # vytvoření horní lišty, pro tisknutí herní desky do konzole
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:ext])
        self.headline = "  |"
        for seq, letter in enumerate(self.alphabet):
            space = "|" if (seq + 1) % 5 == 0 else " "
            self.headline += "{}{}".format(letter, space)
        self.headline = self.headline[:-1]
        self.headline += "|\n"

    def __str__(self):

        out = "\n"
        out += self.headline
        for ind, row in enumerate(self.field):
            space = " " if ind <= 8 else ""
            out += "{}{}|".format(space, ind + 1)
            for seq, symbol in enumerate(row):
                separator = " "
                if seq + 1 == self.ext:
                    separator = "|"
                elif (seq + 1) % 5 == 0:
                    if (ind + 1) % 5 == 0:
                        separator = " "
                    else:
                        separator = " "

                out += "{}{}".format(symbol, separator)

            out += "\n"

        return out

    def __repr__(self):

        return self.field

    def add_symbol(self, row: int, col: int, symbol: str) -> None:

        """
        Přidá na desku symbol
        :param row: řádek, na nějž přidá symbol
        :param col: sloupec, na nějž přidá symbol
        :param symbol: symbol, jenž přidá
        :return:
        """
        if self.field[row][col].symbol != self.empty:
            raise Exception("Symbol má být položen na již obsazené místo")

        self.field[row][col].symbol = symbol
        self.relevant.discard(self.field[row][col])
        add_r = [-1, -1, -1, 0, 0, 1, 1, 1]
        add_c = [-1, 0, 1, -1, 1, -1, 0, 1]
        for i in range(len(add_r)):
            r = row + add_r[i]
            c = col + add_c[i]
            if 0 <= r < self.ext and 0 <= c < self.ext:
                if self.field[r][c].symbol == self.empty:
                    self.relevant.add(self.field[r][c])
        self.space -= 1

    def win_condition_for_one_new(self, node: Node, player: bool, length: int) -> bool:

        """
        Zjistí jestli hráč nevyhrál v okolí jednoho políčka
        :param node: políčko, okolo kterého kontrolujeme
        :param player: hráč, pro kterého zjišťujeme, jestli nevyhrál
        :param length: požadovaná délka výherní řady symbolů
        :return: True nebo False podle toho, jestli hráč vyhrál
        """
        symbol = self.O if player else self.X
        # hledaný řetězec
        wanted = symbol * length
        parts = [self.field[node.row], self.transposition[node.col],
                 self.diagonal[node.diagonal], self.rev_diagonal[node.rev_diagonal]]
        res = False
        for part in parts:
            if wanted in "".join([node.symbol for node in part]):
                res = True

        if res:
            self.score = inf if player else -inf
        return res

    def win_condition(self, player: bool, length: int) -> bool:

        """
        Zjistí jestli jeden z hráču nevyhrál kdekoliv na desce
        :param player: hráč, pro kterého zjišťujeme, jestli nevyhrál
        :param length: požadovaná délka výherní řady symbolů
        :return: True nebo False podle toho, jestli hráč vyhrál
        """
        symbol = self.O if player else self.X
        wanted = symbol * length
        res = False
        for field in self.fields:
            res = res or self.win_condition_in_field(wanted, field)

        if res:
            self.score = inf if player else -inf
        return res

    def calculate_score_for_one_new(self, node: Node) -> float:

        pass

    def calculate_score(self) -> float:

        if self.win_condition(True, self.win_count):
            self.score = inf
            return inf
        if self.win_condition(False, self.win_count):
            self.score = -inf
            return -inf

        self.score += self.calculate_for_player(True)
        self.score -= self.calculate_for_player(False)
        return self.score

    def calculate_for_player(self, player) -> float:

        res = 0
        for field in self.fields:
            res += self.calculate_for_field(field, player)
        return res

    def calculate_for_field(self, field, player) -> float:

        res = 0
        for part in field:
            res += self.calculate_for_part(part, player)
        return res

    def calculate_for_part(self, part, player) -> float:

        cur = self.O if player else self.X
        streak = 0
        offset = 0
        res = 0
        for node in part:
            if node.symbol == cur:
                streak += 1
            elif node.symbol == self.empty:
                offset += 1
            else:
                streak = 0
                offset = 0
            if streak + offset >= self.win_count:
                res += streak
        return res

    def compare(self, board) -> bool:

        """
        porovná hodnoty symbolů všech svých políček se symbolu jejich ekvivalentů na jiné desce
        :param board: deska se kterou se porovnává
        :return: True nebo False podle výsledku
        """
        for x in range(ext):
            for y in range(ext):
                if self.field[x][y].symbol != board.field[x][y].symbol:
                    return False
        return True

    def win_condition_in_field(self, wanted, field) -> bool:

        for part in field:
            symbols = "".join([node.symbol for node in part])
            if wanted in symbols:
                return True
        return False

    def sample_field(self):

        """
        Funkce je určená pouze pro debugování
        :return:
        """
        for i in range(self.ext):
            for j in range(self.ext):
                self.field[i][j].symbol = str(i * 100 + j)


class MiniMax:

    def __init__(self, parent_game, max_depth: int, debug = False):

        self.game = parent_game
        self.ext = self.game.ext
        self.empty = self.game.empty
        self.X = self.game.X
        self.O = self.game.O
        self.win_count = self.game.win_count

        self.board = self.game.board
        self.layers = [[] for _ in range(self.ext ** 2 + 1)]
        self.layers[0].append(Board(self.game))

        # self.spread = spread
        self.max_depth = max_depth
        self.debug = debug

    def choose_option(self, player: bool):

        cur = self.O if player else self.X
        options = list(self.board.relevant)
        if len(options) == 0:
            return self.ext // 2, self.ext // 2

        res = [options[0].row, options[0].col]
        if len(options) == 1:
            return res[0], res[1]

        best_eval = -inf if player else inf
        alpha = -inf
        beta = inf
        for seq, option in enumerate(options):
            new_board = deepcopy(self.board)
            new_board.add_symbol(option.row, option.col, cur)

            if new_board.win_condition_for_one_new(option, cur, self.win_count):
                # self.layers[self.game.depth + 1].append(new_board)
                return option.row, option.col

            outcome = self.proceed_option(1, new_board, player, not player, alpha, beta)

            if player:
                alpha = max(alpha, outcome)
                if best_eval < outcome:
                    res = [option.row, option.col]
            else:
                beta = min(beta, outcome)
                if best_eval > outcome:
                    res = [option.row, option.col]
            if beta <= alpha:
                break

        return res[0], res[1]

    def proceed_option(self, cur_depth: int, board: Board, ref: bool, switch: bool, alpha: int, beta: int) -> float:

        """
        :param cur_depth: aktuální hloubka ponoření minimaxu
        :param board: aktuální deska
        :param ref: hráč (referent) pro kterého kalkulujeme tah (True - kolečeko, False - křížek)
        :param switch: jaký hráč zrovna ve stromu táhne (True - kolečko, False - křížek)
        :param alpha: alfa
        :param beta: beta
        :return: hodnota uzlu
        """
        if cur_depth >= self.max_depth:
            return board.calculate_score()

        relevant = list(board.relevant)
        if len(relevant) == 0:
            return board.calculate_score()

        cur = self.O if switch else self.X
        best_eval = -inf if switch else inf

        for node in relevant:
            new_board = deepcopy(board)
            new_board.add_symbol(node.row, node.col, cur)

            if new_board.win_condition_for_one_new(node, cur, self.win_count):
                return inf if switch else -inf

            outcome = self.proceed_option(cur_depth + 1, new_board, ref, switch, alpha, beta)

            if switch:
                best_eval = max(best_eval, outcome)
                alpha = max(alpha, outcome)
            else:
                best_eval = min(best_eval, outcome)
                beta = min(beta, outcome)
            if beta <= alpha:
                break

        return best_eval

    def choose_option_fully(self, player: bool):

        cur = self.O if player else self.X
        print("STARTED CHOOSING OPTION FOR {}".format(cur))
        options = list(self.board.relevant)
        if len(options) == 0:
            print("ENDED CHOOSING OPTION BY PLACING FIRST SYMBOL")
            return self.ext // 2, self.ext // 2

        res = [options[0].row, options[0].col]
        if len(options) == 1:
            print("ENDED CHOOSING OPTION BY TAKING THE ONLY OPTION")
            return res[0], res[1]

        for seq, option in enumerate(options):
            print("    Testing option number {0} "
                  "on position {2} {1}".format(seq, option.row + 1, self.board.alphabet[option.col]))

            # vytvoří novou desku s nově položeným symbolem
            new_board = deepcopy(self.board)
            new_board.add_symbol(option.row, option.col, cur)

            # zkontroluje, jestli daná deska už nebyla vyřešená
            skip = False
            for layer_board in self.layers[self.game.depth + 1]:
                if new_board.compare(layer_board):
                    skip = True
                    if layer_board.won == cur:
                        print("ENDED BY FINDING WINNING STRATEGY IN HISTORY")
                        return option.row, option.col
            if skip:
                continue

            # zkontroluje, jestli položením už nevyhrála
            if new_board.win_condition_for_one_new(option, cur, self.win_count):
                print("ENDED CHOOSING OPTION BY FINDING INSTANT WIN")
                self.layers[self.game.depth + 1].append(new_board)
                return option.row, option.col

            # spustí minimax
            outcome = self.proceed_option(1, new_board, cur, not player)

            if outcome == 1:
                print("ENDED CHOOSING OPTION BY FINDING BEST LONG TERM STRATEGY")
                return option.row, option.col
            elif outcome == 0:
                res = [option.row, option.col]

        if res[0] == options[0].row and res[1] == options[1].col:
            print("ENDED CHOOSING OPTION BY TAKING THE FIRST POSSIBILITY")
        else:
            print("ENDED CHOOSING OPTION BY TAKING ZERO OPTION")

        return res[0], res[1]

    def proceed_option_fully(self, cur_depth: int, board: Board, ref: str, switch: bool):

        if cur_depth >= self.max_depth:
            return 0

        cur = self.O if switch else self.X
        opp = self.X if switch else self.O

        if self.debug:
            print("    " + "    " * cur_depth + "testing suboption number {} for {}".format(self.game.depth + cur_depth,
                                                                                            cur))
            print(board)

        relevant = list(board.relevant)
        if len(relevant) == 0:
            return 0

        outcomes = []
        for node in relevant:
            # vytvoří novou desku a položí na ní symbol
            new_board = deepcopy(board)
            new_board.add_symbol(node.row, node.col, cur)
            res = 0

            # zkontroluje, jestli deska již nebyla vyřešena
            for layer_board in self.layers[self.game.depth + cur_depth + 1]:
                if new_board.compare(layer_board):
                    if layer_board.won is not None:
                        if layer_board.won == cur:
                            res = 1 if cur == ref else -1
                        elif layer_board.won == opp:
                            res = -1 if cur == ref else 1
                    break

            # zkontroluje, jestli deska nevyhrává
            if res == 0 and new_board.win_condition_for_one_new(node, cur, self.win_count):
                self.layers[self.game.depth + cur_depth + 1].append(new_board)
                res = 1 if cur == ref else - 1

            # rekurzivní zanoření
            if res == 0:
                res = self.proceed_option(cur_depth + 1, new_board, ref, not switch)

            outcomes.append(res)
            if cur == ref and res == 1:
                break
            elif cur != ref and res == -1:
                break

        res = max(outcomes) if cur == ref else min(outcomes)
        if res != 0:
            self.layers[self.game.depth + cur_depth].append(board)
            if res == 1:
                board.won = ref
            else:
                board.won = self.X if ref == self.O else self.O
        return res


class Game:

    def __init__(self, _ext: int, _win_count: int, _minimax_depth: int, _debug: bool):

        # True = O, False = X
        self.switch = True
        self.ext = _ext
        self.win_count = _win_count
        self.depth = 0

        self.X = "X"
        self.O = "O"
        self.empty = " "

        self.debug = debug

        self.board = Board(self)
        self.minimax_depth = _minimax_depth
        self.minimax = MiniMax(self, _minimax_depth, debug = _debug)

    def clean(self):

        self.switch = True
        self.depth = 0
        self.board = Board(self)
        self.minimax = MiniMax(self, self.minimax_depth, debug = debug)

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

        cur = self.O if self.switch else self.X
        if self.board.win_condition(self.switch, self.win_count):
            print(self.board)
            print("Hráč {} vyhrál".format(cur))
            return True
        if self.board.space == 0:
            print(self.board)
            print("Remíza")
            return True
        return False

    def __str__(self):

        return self.board.__str__()


ext = 3
win_count = 3
minimax_depth = 20
debug = False

game = Game(ext, win_count, minimax_depth, debug)
while True:
    game_mode = input("Vyber, jakým způsobem chceš hrát:\n"
                      "1 - hráč proti hráči\n2 - hráč sám se sebou\n"
                      "3 - hráč proti počátači (začíná počítač)\n"
                      "4 - hráč proti počítači (začíná hráč)\n"
                      "5 - počítač proti počítači\n__: ")
    if game_mode == "1":
        game.play()
    elif game_mode == "2":
        game.play_without_switch()
    elif game_mode == "3":
        game.play_with_ai()
    elif game_mode == "4":
        game.play_with_ai(ai_starts = False)
    elif game_mode == "5":
        game.play_ai_vs_ai()
    else:
        print("Zadal si asi něco špatně, zkus to znovu")
    game.clean()
