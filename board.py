from node import Node
from math import inf


class Board:

    """
    Reprezentace herní desky.

    Jednotlivá políčka jsou uložena v atributu self.field, kde jsou uložena, tak jak se tisknou (v seznamu řádků), dále
    jsou ještě tatáž políčka uložena v atributech self.transposition, self.diagonal a self.rev_diagonal,
    v těchto strukturách jsou seřezana políčka po sloupcích, po diagonále z levého dolního rohu do pravého horního rohu
    a po diagonále z levého horního rohu do pravého dolního rohu. Takto jsou ta samá políčka uložená ve vícero
    strukturách, aby se lépe kontrolovalo, jestli nějaký hráč už třeba nedal dostatek symbolů dohromady, a tudíž
    nevyhrál.

    Další důležitá struktura je self.relevant, tam jsou uložena políčka, která jsou v bezprostřední blízkosti již
    položených políček, tato struktura slouží k tomu, aby minimax nemusel zkoušet všechna políčka, ale pouze ta v
    bezprostřední blízkosti již položených políček. self.relevant je množina a ne seznam, což zaručuje, že minimax,
    pracující s toutu strukturou, nebude deterministický, jelikož si tuto množinu převádí na seznam, což není
    deterministické. Pokaždé když je přidáno nové políčko na desku, zavolá se funkce, která přehodnotí množinu
    relevantních políček self.relevant.

    Poslední důležitá struktura je skóre. Skóre má kladnou hodnotu pokud je deska výhodnější pro hráče O a zápornou,
    pokud je deska výhodnější pro hráče X. Pokud jeden hráč dosáhl absolutního vítězství na desce, je skóre desky
    plus nebo mínus nekončeno. Skóre se počítá pro každý sloupec, řádek, diagonálu a obrácenou diagonálu zvlášť (viz
    pole self.scores), po tom, co se přidá nové políčko, je zavolána funkce, která z celkového skóre odečte předešlé
    hodnoty skóre v polích, kde se nově přidavší políčko vyskytuje (řádku, sloupci, diagonále a obrácené diagonále),
    vypočítá nové hodnoty skóre v těch samých polích, načež je přičte k celkovému skóre.

    Jedna z nejzásadnějších funkcí je self.calculate_score_for_part_one_direction, kde se vyhodnocuje skóre jednoho
    pole z jednoho směru, doporučuji přečíst si hlavně její popis.

    :var self.game: hra, v níž se deska nachází
    :var self.space: počet volných míst na desce
    :var self.score: skóre desky, když je záporné, deska je spíše nakloněná pro hráče X, pokud je kladné, deska je spíše nakloněna hráči O. Pokud je plus, nebo mínus nekonečno, jeden z hráčů vyhrál
    :var self.inherited_score: pokud deska nevynutelně vede k vítězství jednoho z hráčů, tato proměnná bude zastávat hodnotu plus, nebo minus nekonečna, podle toho, jaký hráč na téhle desce vyhraje (počítá s tím, že oba hráči budou volit své nejlepší tahy)
    :var self.field: reprezentace desky, pole jednotlivých řádků
    :var self.relevant: množina relevantních políček
    :var self.transposition: transpozice herní desky, pole jednotlivých sloupců
    :var self.diagonal: reprezentace diagonál desky (vedoucích z levého dolního rohu do pravého horního rohu)
    :var self.rev_diagonal: reprezentace reverzních diagonál desky (vedoucích z levého horního rohu do pravého dolního rohu)
    :var self.field_score: hodnoty dílčích skóre jednotlivých řádků
    :var self.transposition_score: hodnoty dílčích skóre jednotlivých sloupců
    :var self.diagonal_score: hodnoty dílčích skóre jednotlivých diagonál
    :var self.rev_diagonal_score: hodnoty dílčích skóre jednotlivých reverzních diagonál
    """

    def __init__(self, parent_game) -> None:

        """
        Konstruktor nové desky.

        :param parent_game: hra, v níž se deska nachází
        :return: None
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
        self.inherited_score = 0.0

        # hrací pole
        self.field = [[Node(self.empty, row, col, self.ext) for col in range(self.ext)] for row in range(self.ext)]
        # relevantní políčka desky (ty v rozumné vzdálenosti od již položených políček)
        self.relevant = set()

        # vytvoření transpozice hracího pole
        self.transposition = [[None for _ in range(self.ext)] for _ in range(self.ext)]
        for x in range(self.ext):
            for y in range(self.ext):
                self.transposition[x][y] = self.field[y][x]

        # vytvoří diagonální reprezentace hracího pole
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

        # vytvoří pole, kam se bude ukládat skóre jednotlivých
        self.field_score = [0 for _ in range(self.ext)]
        self.transposition_score = [0 for _ in range(self.ext)]
        self.diagonal_score = [0 for _ in range(2 * self.ext - 1)]
        self.rev_diagonal_score = [0 for _ in range(2 * self.ext - 1)]
        self.scores = [self.field_score, self.transposition_score, self.diagonal_score, self.rev_diagonal_score]

        # vytvoření horní lišty, pro tisknutí herní desky do konzole
        self.alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:self.ext])
        self.headline = "  |"
        for seq, letter in enumerate(self.alphabet):
            space = "|" if (seq + 1) % 5 == 0 else " "
            self.headline += "{}{}".format(letter, space)
        self.headline = self.headline[:-1]
        self.headline += "|\n"

    def __str__(self) -> str:

        """
        Vytiskne desku do konzole.

        :return: textovou reprezentaci desky
        """
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
        Přidá na desku nový symbol.

        :param row: řádek, na nějž přidá symbol
        :param col: sloupec, na nějž přidá symbol
        :param symbol: symbol, jenž přidá
        :return: None
        """
        if self.field[row][col].symbol != self.empty:
            raise Exception("Symbol má být položen na již obsazené místo")

        # přepíše symbol políčka
        self.field[row][col].symbol = symbol
        # zmenší zbývající políčka na desce o jedna
        self.space -= 1
        # přehodnotí relevantní políčka
        self.manage_relevant(row, col)
        # přehodnotí skóre
        self.manage_score(self.field[row][col])

    def manage_relevant(self, row: int, col: int) -> None:

        """
        Volá se výhradně po přidání nového políčka, přehodnotí jaká políčka jsou relevantní pro minimax (jaká políčka
        se nacházejí v bezprostřední blízkosti již položených políček).

        :param row: řádek, kam se přidalo nové políčko
        :param col: sloupec, kam se přidalo nové políčko
        :return: None
        """
        self.relevant.discard(self.field[row][col])

        add_r = [-1, -1, -1, 0, 0, 1, 1, 1]
        add_c = [-1, 0, 1, -1, 1, -1, 0, 1]
        for i in range(len(add_r)):
            r = row + add_r[i]
            c = col + add_c[i]
            if 0 <= r < self.ext and 0 <= c < self.ext:
                if self.field[r][c].symbol == self.empty:
                    self.relevant.add(self.field[r][c])

    def manage_score(self, node: Node) -> None:

        """
        Volá se výhradně po přidání nového políčka, přepočítá skóre desky, popřípadě, jestli na desce někdo nevyhrává.

        :param node: políčko, které bylo přidáno
        :return: None
        """
        # zkontroluje, jestli hráč, co byl na tahu, nevyhrál
        if node.symbol == self.O:
            if self.win_condition_for_one_new(node, True):
                return
        else:
            if self.win_condition_for_one_new(node, False):
                return

        # zkontroluje, jestli je na desce ještě volné místo
        if self.space == 0:
            self.score = 0
            return

        # přepočítá hodnotu skóre
        parts = [self.field[node.row], self.transposition[node.col],
                 self.diagonal[node.diagonal], self.rev_diagonal[node.rev_diagonal]]
        indexes = (node.row, node.col, node.diagonal, node.rev_diagonal)

        for seq, part in enumerate(parts):
            index = indexes[seq]
            self.score -= self.scores[seq][index]

            self.scores[seq][index] = self.calculate_score_for_part(part, True)
            self.scores[seq][index] -= self.calculate_score_for_part(part, False)

            self.score += self.scores[seq][index]

    def win_condition_for_one_new(self, node: Node, player: bool) -> bool:

        """
        Zjistí, jestli hráč nevyhrál v okolí jednoho políčka.

        :param node: políčko, okolo kterého se kontroluje
        :param player: hráč, pro kterého se zjišťuje, jestli nevyhrál
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
        Zjistí, jestli jeden z hráču nevyhrál kdekoliv na desce.

        :param player: hráč pro kterého se zjišťuje, jestli nevyhrál
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

    def calculate_score(self) -> float:

        """
        Vypočítá skóre pro celou desku.

        :return: skóre celé desky
        """
        if self.space == 0:
            return 0

        self.score += self.calculate_score_for_player(True)
        self.score -= self.calculate_score_for_player(False)
        return self.score

    def calculate_score_for_player(self, player: bool) -> float:

        """
        Vypočítá hodnotu skóre na celé desce pro jednoho hráče.

        :param player: pro jekého hráče skóre počítáme
        :return: celkové skóre zadaného hráče
        """
        res = 0
        for field in self.fields:
            for part in field:
                res += self.calculate_score_for_part(part, player)
        return res

    def calculate_score_for_part(self, part, player: bool) -> float:

        """
        Vypočítá hodnotu skóre v jednom poli.

        :param part: pole, kde se vypočítá skóre
        :param player: pro jakého hráče skóre počítame
        :return: skóre zadaného pole
        """
        res = self.calculate_score_for_part_one_direction(part, player)
        res += self.calculate_score_for_part_one_direction(reversed(part), player)
        return res

    def calculate_score_for_part_one_direction(self, part, player: bool) -> float:

        """
        Vypočítá hodnotu skóre v jednom poli v jednom směru, proto se tato funkce na jedno konkrétní pole volá dvakrát,
        jednou s jeho normální reprezentací a podruhé s jeho převrácenou reprezentací. Jedna z nejzásadnějších funkcí.

        Za každou sekvenci prázdných míst a hledaných symbolů, která;

        1) může obsahovat jedno prázdné místo na začátku, nebo uprostřed řetězce hledaných znaků

        2) může obsahovat až čtyři prázdná místa na konci řetězce

        3) má dohromady délku, jako požadovaná délka vítězného řetězce

        přičte druhou mocninu počtu hledaných znaků v sekvenci ke skóre. Řetězce, které by se přičetli pak jsou tedy
        například: .OO.., O...., O.O.., OO.OO, OOO..

        Důsledky tohoto algoritmu jsou:

        1) ježto se přičítá druhá mocnina počtu hledaných znaků v sekvenci, bude minimax preferovat vytváření méňe delších řetězců, na úkor mnoha kratších

        2) minimax bude preferovat vytváření oboustraně otevřených pozic, jelikož se přičtou do skóre dvakrát.

        3) pozice uzavřené z obou stran (XOOOX) se nepřičtou vůbec

        :param part: pole, kde se vypočítá skóre.
        :param player: pro jakého hráče skóre počítáme.
        :return: skóre jednoho pole z jednoho směru
        """
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
        Porovná hodnoty symbolů všech svých políček se symboly jejich ekvivalentů na jiné desce.

        :param board: deska se kterou se porovnává
        :return: True nebo False podle výsledku
        """
        for x in range(self.ext):
            for y in range(self.ext):
                if self.field[x][y].symbol != board.field[x][y].symbol:
                    return False
        return True

    def win_condition_in_field(self, wanted: str, field) -> bool:

        """
        Zjistí, jestli se výherní kombinace nenachází v jednom poli.

        :param wanted: hledaný řetězec
        :param field: pole, ve kterém hledáme
        :return: True nebo False podle toho, jestli hráč vyhrál
        """
        for part in field:
            symbols = "".join([node.symbol for node in part])
            if wanted in symbols:
                return True
        return False

    def sample_field(self) -> None:

        """
        Funkce je určená pouze pro debugování. Zaplní všechna políčka odlišnými čísly.

        :return: None
        """
        for i in range(self.ext):
            for j in range(self.ext):
                self.field[i][j].symbol = str(i * 100 + j)