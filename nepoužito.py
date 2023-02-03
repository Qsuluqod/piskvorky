# V self.board:
def find_relevant(self, spread):
    relevant = []
    relevant += self.find_relevant_in_field(spread, self.field)
    relevant += self.find_relevant_in_field(spread, self.transposition)
    return relevant


def find_relevant_in_field(self, spread, field):
    relevant = []
    for part in field:
        relevant += self.find_relevant_in_part(spread, part)
        relevant += self.find_relevant_in_part(spread, reversed(part))
    return relevant


def find_relevant_in_part(self, spread, part):
    relevant = []
    reach = 0
    for node in part:
        if node.symbol != self.empty:
            reach = spread
        elif node.symbol == self.empty and reach > 0:
            relevant.append(node)
            reach -= 1
    return relevant

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