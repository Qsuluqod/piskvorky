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
        self.space = ext**2

        # kladné - vyhrává kolečko, záporné - vyhrává křížek
        self.score = None

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
