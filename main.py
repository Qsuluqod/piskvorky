from UI import UI

# rozměr pole
ext = 5
# počet políček v řadě nutných k vítězství
win_count = 4
# maximální zanoření minimaxu
minimax_depth = 5

ui = UI(ext, win_count, minimax_depth)
ui.run()
