from game import Game


extent = 5
win_count = 4
minimax_depth = 5

game = Game(extent, win_count, minimax_depth)
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
