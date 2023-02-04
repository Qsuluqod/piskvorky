from board import Board
from math import inf
from copy import deepcopy


class MiniMax:

    """
    Strktura, která za pomocí algoritmu minimax vrací tahy, které jsou pro hráče nejvýhodnější. Používá alfa beta
    prořezávání.

    V self.layers se ukrývá něco jako historie průchodů, pokud nějaká deska nevyhnutelně vede k vítězství jedné
    nebo druhé strany, uloží se do příslušné vrstvy, tyto vrsty se pak porovnávají při průchodu minimaxem, aby minimax
    zbytečně nemusel nějaké desky vyhodnocovat vícekrát. Každé pole v self.layer odpovídá jedné vrstvě hry, takže
    na první pozici jsou desky, kde je právě zaplněno právě jedno pole, na druhé vrstvě jsou uloženy desky, kde jsou
    zaplněna právě dvě pole atd.

    :var self.game: instance hry, ve které bude minimax operovat
    :var self.layers: Pole polí, kam se ukládají jednotlivé desky, jež už byly vyřešeny.
    """

    def __init__(self, parent_game, max_depth: int) -> None:

        """
        Konstruktor minimaxu.

        :param parent_game: hra, ve které bude minimax operovat
        :param max_depth: maximální zanoření minimaxové funkce
        :return: None
        """

        self.game = parent_game
        self.ext = self.game.ext
        self.empty = self.game.empty
        self.X = self.game.X
        self.O = self.game.O
        self.win_count = self.game.win_count

        self.board = self.game.board

        # historie průchodů minimaxu
        self.layers = [[] for _ in range(self.ext ** 2 + 1)]
        self.layers[0].append(Board(self.game))

        # maximální zanoření
        self.max_depth = max_depth

    def choose_option(self, player: bool) -> (int, int):

        """
        Funkce, která ze všech relevantních políček desky, vybere tu nejlepší pro zadaného hráče podle minimaxového
        algoritmu. Používá alfa beta prořezávání.

        Nejdříve vygeneruje všechny možné tahy podle výběru relevantních políček z dané desky. Následně je seřadí
        dle jejich statického ohodnocení a v tomto pořadí na ně volá obdobnou rekurzivní funkci self.proceed_option.

        :param player: hráč, pro jakého generujeme tah
        :return: souřadnice, které minimax vyhodnotil jako nejlepší
        """
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
        boards = []

        # vygeneruje všechny možnosti, kam může být položeno políčko
        for seq, option in enumerate(options):
            # vytvoří novou desku
            new_board = deepcopy(self.board)
            # přidá na ní políčko
            new_board.add_symbol(option.row, option.col, cur)

            # pokud ne desce hráč vyhrává, rovnou vrátí danou možnost
            if abs(new_board.score) == inf:
                return option.row, option.col

            # pro desku zkontroluje, jestli už nebyla vyřešena v minulosti
            for layer_board in self.layers[self.game.depth + 1]:
                if new_board.compare(layer_board):
                    if layer_board.inherited_score == inf and player or\
                            layer_board.inherited_score == -inf and not player:
                        return option.row, option.col
                    elif abs(layer_board.inherited_score) == inf:
                        new_board = layer_board
                    break

            # přidá desku do seznamu
            boards.append((new_board, new_board.score, option))

        # seřadí desky podle skóre
        boards.sort(key=lambda x: x[1], reverse=player)

        # projede všechny možnosti, kam může položit políčko
        for board, score, option in boards:
            # zavolání rekurzivní funkce
            outcome = self.proceed_option(1, board, not player, alpha, beta)

            # alfa beta prořezávání
            if player:
                alpha = max(alpha, outcome)
                if best_eval < outcome:
                    best_eval = outcome
                    res = [option.row, option.col]
            else:
                beta = min(beta, outcome)
                if best_eval > outcome:
                    best_eval = outcome
                    res = [option.row, option.col]
            if beta <= alpha:
                break

        return res[0], res[1]

    def proceed_option(self, cur_depth: int, board: Board, switch: bool, alpha: int, beta: int) -> float:

        """
        Rekurzivní funkce, která vyhodnocuje nejlepší možnost pro danou desku. Používá se alfa beta prořezávání.

        Pokud dosáhla funkce svého maximálního zanoření, vrátí statické ohodnocení dané desky, jinak nejdříve vybere
        všechny relevantní možnosti, kam může táhnout z desky, poté je seřadí podle statického ohodnocení desek a
        rekurzivně zavolá tuto funkci na každou možnost v pořadí, v jakém je seřadila, hodnoty která získá z jejich
        volání si ukládá. Zároveň pro každou desku, kterou vytvoří kontroluje, jestli už daná deska nebyla vyřešena v
        historii.

        Až bude mít ohodnocení všech desek, vrátí minimální nebo maximální hodnotu (dle toho, jaký hráč je na tahu)
        z desek, na něž může táhnout.

        :param cur_depth: aktuální hloubka ponoření minimaxu
        :param board: aktuální deska, pro kterou vybíráme možnost
        :param switch: jaký hráč zrovna ve stromu táhne (True - kolečko, False - křížek)
        :param alpha: alfa, slouží pro alfa beta prořezávání
        :param beta: beta, slouží pro alfa beta prořezávání
        :return: nejlepší dosažitelná minimaxová hodnoty zadané desky
        """
        # pokud hloubka zanoření minimaxu přetekla, vrátíme statické ohodnocení desky
        if cur_depth >= self.max_depth:
            return board.score

        # vybere relevantní políčka z desky
        relevant = list(board.relevant)
        if len(relevant) == 0:
            return board.score

        # vybere symbol hráče na tahu
        cur = self.O if switch else self.X
        # zavede nejlepší možný výsledek
        best_eval = -inf if switch else inf

        # vytvoří všechny desky s variantami, kam může hráč položit políčko
        boards = []
        for node in relevant:
            new_board = deepcopy(board)
            new_board.add_symbol(node.row, node.col, cur)

            # zkontroluje, jestli na desce někdo nevyhrává
            if abs(new_board.score) == inf:
                return new_board.score

            # zkontroluje, jestli deska už nebyla v historii vyřešena
            for layer_board in self.layers[self.game.depth + cur_depth + 1]:
                if new_board.compare(layer_board):
                    if abs(layer_board.inherited_score) == inf:
                        if layer_board.inherited_score == inf and switch:
                            return inf
                        elif layer_board.inherited_score == -inf and not switch:
                            return -inf
                    new_board = layer_board
                    break

            boards.append((new_board, new_board.score))

        # seřadí desky podle pravděpodobnosti výběru
        boards.sort(key=lambda x: x[1], reverse=switch)

        # projede jednotlivé možnosti
        for new_board, score in boards:
            # zanoření minimaxu
            outcome = self.proceed_option(cur_depth + 1, new_board, not switch, alpha, beta)

            # alfa beta prořezávání
            if switch:
                best_eval = max(best_eval, outcome)
                alpha = max(alpha, outcome)
            else:
                best_eval = min(best_eval, outcome)
                beta = min(beta, outcome)
            if beta <= alpha:
                break

        # pokud na desce někdo vyhrál, přidá desku do historie
        if abs(best_eval) == inf:
            board.inherited_score = best_eval
            self.layers[self.game.depth + cur_depth].append(board)
        return best_eval
