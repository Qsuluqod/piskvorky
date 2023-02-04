from UI import UI

# rozměr pole
ext = 10
# počet políček v řadě nutných k vítězství
win_count = 5
# maximální zanoření minimaxu
minimax_depth = 2

ui = UI(ext, win_count, minimax_depth)
ui.run()
