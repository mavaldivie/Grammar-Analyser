from cmp.Parser_LR1 import *

def have_same_core(a, b):
    a, b = a.state, b.state

    equal = True
    for i in a:
        equal &= any(j for j in b if i.Center() == j.Center())
    for i in b:
        equal &= any(j for j in a if i.Center() == j.Center())

    return equal

#merge a to b
def merge_nodes(a, b):
    for i in a.state:
        item = None
        for j in b.state:
            if i.Center() == j.Center():
                item = j
                break
        item.lookaheads |= i.lookaheads

def build_LALR_automaton(automaton):
    root = automaton
    notckecked = [i for i in automaton]
    notckecked.reverse()
    truenodes = []

    while notckecked:
        i = notckecked.pop()
        merged = False
        for j in truenodes:
            merged |= have_same_core(i, j)
            if merged:
                merge_nodes(i, j)
                for node in (notckecked + truenodes):
                    for symbol, states in node.transitions.items():
                        for state in states:
                            if state == i:
                                node.add_transition(symbol, j)
                for symbol, states in i.transitions.items():
                    for state in states:
                        if state in (truenodes + notckecked):
                            j.add_transition(symbol, state)
                break
        if not merged:
            truenodes.append(i)
    return root

class LALRParser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)

        automaton = build_LALR_automaton(automaton)

        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for item in node.state:
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    if item.production.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF.Name), (self.OK, None))
                    else:
                        for c in item.lookaheads:
                            self._register(self.action, (idx, c.Name), (self.REDUCE, item.production))
                else:
                    next_symbol = item.NextSymbol
                    try:
                        next_state = node[next_symbol.Name][0]
                        if next_symbol.IsNonTerminal:
                            self._register(self.goto, (idx, next_symbol.Name), next_state.idx)
                        else:
                            self._register(self.action, (idx, next_symbol.Name), (self.SHIFT, next_state.idx))
                    except KeyError:
                        print(f'Node: {node} without transition with symbol {next_symbol}')
                        return

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value