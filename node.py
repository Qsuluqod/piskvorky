class Node:

    """
    Reprezentace políčka.

    :var self.symbol: symbol, jaký políčko má
    :var self.row: v kolikátem řádku se políčko nachází
    :var self.col: v kolikátém sloupci se políčko nachází
    :var self.diagonal: v kolikáté diagonále se políčko nachází
    :var self.rev_diagonal: v kolikáté reverzní diagonále se políčko nachází
    """

    def __init__(self, symbol: str, row: int, col: int, ext: int) -> None:

        """
        Konstruktor políčka.

        :param symbol: symbol políčka
        :param row: řádek, v němž se políčko nachází
        :param col: sloupec, v němž se políčko nachází
        :param ext: rozměr hrací desky, slouží k výpočtu zbylých atributů
        :return: None
        """
        self.symbol = symbol
        self.row = row
        self.col = col
        # na kolikáté diagonále se nechází
        self.diagonal = row + col
        # na kolikáte reverzní diagonále se nachází
        self.rev_diagonal = (ext - row - 1) + col

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.symbol