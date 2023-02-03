from board import Board
from math import inf
from copy import deepcopy


class MiniMax:

    def __init__(self, parent_game, max_depth: int):

        self.game = parent_game
        self.ext = self.game.ext
        self.empty = self.game.empty
        self.X = self.game.X
        self.O = self.game.O
        self.win_count = self.game.win_count

        self.board = self.game.board
        self.layers: [[Board]]
        self.layers = [[] for _ in range(self.ext ** 2 + 1)]
        self.layers[0].append(Board(self.game))

        # self.spread = spread
        self.max_depth = max_depth

    def choose_option(self, player: bool):

        """

        :param player:
        :return:
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
        for seq, option in enumerate(options):
            new_board = deepcopy(self.board)
            new_board.add_symbol(option.row, option.col, cur)

            if abs(new_board.score) == inf:
                return option.row, option.col

            for layer_board in self.layers[self.game.depth + 1]:
                if new_board.compare(layer_board):
                    if layer_board.inherited_score == inf and player or\
                            layer_board.inherited_score == -inf and not player:
                        return option.row, option.col
                    elif abs(layer_board.inherited_score) == inf:
                        new_board = layer_board
                    break

            boards.append((new_board, new_board.score, option))

        boards.sort(key = lambda x: x[1], reverse = player)

        for board, score, option in boards:
            outcome = self.proceed_option(1, board, not player, alpha, beta)

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

        print("nejlepší dosažitelné skóre pro {}: {}".format(cur, best_eval))
        return res[0], res[1]

    def proceed_option(self, cur_depth: int, board: Board, switch: bool, alpha: int, beta: int) -> float:

        """
        :param cur_depth: aktuální hloubka ponoření minimaxu
        :param board: aktuální deska
        :param switch: jaký hráč zrovna ve stromu táhne (True - kolečko, False - křížek)
        :param alpha: alfa
        :param beta: beta
        :return: hodnota uzlu
        """
        # pokud hloubka zanoření minimaxu přetekla
        if cur_depth >= self.max_depth:
            return board.score

        # vybere relevantní políčka z desky
        relevant = list(board.relevant)
        if len(relevant) == 0:
            return board.score

        cur = self.O if switch else self.X
        best_eval = -inf if switch else inf

        # vytvoří všechny desky s variantami, kam může hráč položit políčko
        boards = []
        for node in relevant:
            new_board = deepcopy(board)
            new_board.add_symbol(node.row, node.col, cur)

            # zkontroluje, jestli na desce někdo nevyhrává
            if abs(new_board.score) == inf:
                return new_board.score

            # zkontroulje, jestli deska už nebyla v historii vyřešena
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

        # projede jednotlivé
        for new_board, score in boards:
            outcome = self.proceed_option(cur_depth + 1, new_board, not switch, alpha, beta)

            if switch:
                best_eval = max(best_eval, outcome)
                alpha = max(alpha, outcome)
            else:
                best_eval = min(best_eval, outcome)
                beta = min(beta, outcome)
            if beta <= alpha:
                break

        if abs(best_eval) == inf:
            board.inherited_score = best_eval
            self.layers[self.game.depth + cur_depth].append(board)
        return best_eval
