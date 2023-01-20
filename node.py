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