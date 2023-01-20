from node import Node
from math import inf


class Board:

    def __init__(self, parent_game):

        """
        :param parent_game: hra, v jaké se deska nachází
        """
        self.game = parent_game
        self.ext = parent_game.ext
        self.X = parent_game.X
        self.O = parent_game.O
        self.empty = parent_game.empty
        self.win_count = parent_game.win_count

        # volné místo na šachovnici
        self.space = self.ext ** 2

        # kladné - vyhrává kolečko, záporné - vyhrává křížek
        self.score = 0.0

        # hrací pole
        self.field = [[Node(self.empty, row, col, self.ext) for col in range(self.ext)] for row in range(self.ext)]
        # relevantní políčka desky (ty v rozumné vzdálenosti od již položených políček)
        self.relevant = set()

        # vytvoření transpozice hracího pole
        self.transposition = [[None for _ in range(self.ext)] for _ in range(self.ext)]
        for x in range(self.ext):
            for y in range(self.ext):
                self.transposition[x][y] = self.field[y][x]

        # vytvoří diagonálních reprezentací hracího pole
        self.diagonal = [[] for _ in range(self.ext * 2 - 1)]  # /
        self.rev_diagonal = [[] for _ in range(self.ext * 2 - 1)]  # \

        for x in range(self.ext * 2 - 1):
            row = min(x, self.ext - 1)
            col = max(0, -self.ext + x + 1)
            rev_row = max(self.ext - x - 1, 0)
            for y in range(min(x + 1, self.ext * 2 - 1 - x)):
                self.diagonal[x].append(self.field[row][col])
                self.rev_diagonal[x].append(self.field[rev_row][col])
                row -= 1
                col += 1
                rev_row += 1

        self.fields = [self.field, self.transposition, self.diagonal, self.rev_diagonal]

        # na skore
        self.field_score = [0 for _ in range(self.ext)]
        self.transposition_score = [0 for _ in range(self.ext)]
        self.diagonal_score = [0 for _ in range(2 * self.ext - 1)]
        self.rev_diagonal_score = [0 for _ in range(2 * self.ext - 1)]
        self.field_score = [self.field_score, self.transposition_score, self.diagonal_score, self.rev_diagonal_score]

        # vytvoření horní lišty, pro tisknutí herní desky do konzole
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:self.ext])
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
        self.manage_score_for_node(self.field[row][col])

    def manage_score_for_node(self, node: Node):

        if node.symbol == self.O:
            if self.win_condition_for_one_new(node, True):
                return
        else:
            if self.win_condition_for_one_new(node, False):
                return

        if self.space == 0:
            self.score = 0
            return

        parts = [self.field[node.row], self.transposition[node.col],
                 self.diagonal[node.diagonal], self.rev_diagonal[node.rev_diagonal]]
        indexes = (node.row, node.col, node.diagonal, node.rev_diagonal)

        for seq, part in enumerate(parts):
            index = indexes[seq]
            self.score -= self.field_score[seq][index]
            self.field_score[seq][index] = self.calculate_score_for_part(part, True)
            self.field_score[seq][index] -= self.calculate_score_for_part(part, False)
            self.score += self.field_score[seq][index]

    def win_condition_for_one_new(self, node: Node, player: bool) -> bool:

        """
        Zjistí jestli hráč nevyhrál v okolí jednoho políčka
        :param node: políčko, okolo kterého kontrolujeme
        :param player: hráč, pro kterého zjišťujeme, jestli nevyhrál
        :param length: požadovaná délka výherní řady symbolů
        :return: True nebo False podle toho, jestli hráč vyhrál
        """
        symbol = self.O if player else self.X
        # hledaný řetězec
        wanted = symbol * self.win_count
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

    def calculate_score_for_node(self, node: Node) -> float:

        parts = [self.field[node.row], self.transposition[node.col],
                 self.diagonal[node.diagonal], self.rev_diagonal[node.rev_diagonal]]
        score = 0
        for seq, part in enumerate(parts):
            score += self.calculate_score_for_part(part, True)
            score -= self.calculate_score_for_part(part, False)
        return score

    def calculate_score(self) -> float:

        if self.space == 0:
            return 0

        self.score += self.calculate_score_for_player(True)
        self.score -= self.calculate_score_for_player(False)
        return self.score

    def calculate_score_for_player(self, player: bool) -> float:

        res = 0
        for field in self.fields:
            for part in field:
                res += self.calculate_score_for_part(part, player)
        return res

    def calculate_score_for_part(self, part, player: bool) -> float:

        res = self.calculate_score_for_part_one_direction(part, player)
        res += self.calculate_score_for_part_one_direction(reversed(part), player)
        return res

    def calculate_score_for_part_one_direction(self, part, player: bool) -> float:

        cur = self.O if player else self.X
        streak = 0
        offset = 0
        res = 0
        for node in part:
            if node.symbol == cur:
                streak += 1
                offset = min(offset, 1)
            elif node.symbol == self.empty:
                offset += 1
                streak = min(streak, 5 - offset)
            else:
                streak = 0
                offset = 0
            if streak + offset >= self.win_count:
                res += streak**2
        return res

    def compare(self, board) -> bool:

        """
        porovná hodnoty symbolů všech svých políček se symbolu jejich ekvivalentů na jiné desce
        :param board: deska se kterou se porovnává
        :return: True nebo False podle výsledku
        """
        for x in range(self.ext):
            for y in range(self.ext):
                if self.field[x][y].symbol != board.field[x][y].symbol:
                    return False
        return True

    def win_condition_in_field(self, wanted: str, field) -> bool:

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