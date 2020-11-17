from cmp.tools.Firsts_and_Follows import compute_follows
from cmp.automata import State, lr0_formatter
from cmp.pycompiler import Item
from cmp.utils import ContainerSet
from cmp.tools.Firsts_and_Follows import compute_firsts, compute_local_first
from cmp.tools.parsing import ShiftReduceParser

def build_LR0_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0)

    automaton = State(start_item, True)

    pending = [start_item]
    visited = {start_item: automaton}

    while pending:
        current_item = pending.pop()
        if current_item.IsReduceItem:
            continue

        # Your code here!!! (Decide which transitions to add)
        # Your code here!!! (Add the decided transitions)
        current_state = visited[current_item]
        next_item = current_item.NextItem()
        next_symbol = current_item.NextSymbol

        try:
            next_state = visited[next_item]
        except KeyError:
            next_state = State(next_item, True)
            visited[next_item] = next_state
            pending.append(next_item)

        current_state.add_transition(next_symbol.Name, next_state)
        if next_symbol in G.nonTerminals:
            for prod in next_symbol.productions:
                item = Item(prod, 0)
                try:
                    next_state = visited[item]
                except KeyError:
                    next_state = State(item, True)
                    visited[item] = next_state
                    pending.append(item)
                current_state.add_epsilon_transition(next_state)

    return automaton

class SLR1Parser(ShiftReduceParser):

    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)
        firsts = compute_firsts(G)
        follows = compute_follows(G, firsts)

        automaton = build_LR0_automaton(G).to_deterministic()
        for i, node in enumerate(automaton):
            if self.verbose: print(i, '\t', '\n\t '.join(str(x) for x in node.state), '\n')
            node.idx = i

        for node in automaton:
            idx = node.idx
            for state in node.state:
                item = state.state
                # Your code here!!!
                # - Fill `self.Action` and `self.Goto` according to `item`)
                # - Feel free to use `self._register(...)`)
                if item.IsReduceItem:
                    if item.production.Left == G.startSymbol:
                        self._register(self.action, (idx, G.EOF.Name), (self.OK, None))
                    else:
                        for f in follows[item.production.Left]:
                            self._register(self.action, (idx, f.Name), (self.REDUCE, item.production))

                else:
                    if item.NextSymbol.IsTerminal:
                        self._register(self.action, (idx, item.NextSymbol.Name),
                                       (self.SHIFT, node[item.NextSymbol.Name][0].idx))
                    else:
                        self._register(self.goto, (idx, item.NextSymbol.Name), (node[item.NextSymbol.Name][0].idx))

    @staticmethod
    def _register(table, key, value):
        assert key not in table or table[key] == value, 'Shift-Reduce or Reduce-Reduce conflict!!!'
        table[key] = value

