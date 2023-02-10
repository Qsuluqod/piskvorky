from game import Game


class UI:

    """
    Třída, která řeší komunikaci s uživatelem. Obsahuje iniciační funkci run.

    :var self.ext: rozměr hrací desky
    :var self.win_count: počet políček nutných k vítězství
    :var self.minimax_depth: maximální zanoření minimaxu
    """

    def __init__(self, ext: int, win_count: int, minimax_depth: int) -> None:

        self.ext = ext
        self.win_count = win_count
        self.minimax_depth = minimax_depth

    def run(self) -> None:

        """
        Iniciační funkce programu. Zeptá se uživatele, jaký chce hrát herní režim, načež ho spustí.

        :return: None
        """
        game = Game(self.ext, self.win_count, self.minimax_depth)
        while True:
            # nechá uživatele vybrat herní režim
            game_mode = input("Vyber, jakým způsobem chceš hrát:\n"
                              "1 - hráč proti hráči\n"
                              "2 - hráč sám se sebou\n"
                              "3 - hráč proti počítači (začíná počítač)\n"
                              "4 - hráč proti počítači (začíná hráč)\n"
                              "5 - počítač proti počítači\n"
                              "6 - ukončit program\n"
                              "__: ")
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
            elif game_mode == "6":
                print("Nashledanou")
                break
            else:
                print("Zadal jsi asi něco špatně, zkus to znovu")
            game.clean()
