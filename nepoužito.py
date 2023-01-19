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