from cmp.pycompiler import Grammar, Item
from cmp.utils import ContainerSet
from cmp.tools.Firsts_and_Follows import compute_firsts, compute_local_first
from cmp.automata import State, multiline_formatter
from cmp.tools.parsing import ShiftReduceParser


def expand(item, firsts):
    next_symbol = item.NextSymbol
    if next_symbol is None or not next_symbol.IsNonTerminal:
        return []

    lookaheads = ContainerSet()
    # Your code here!!! (Compute lookahead for child items)
    for prev in item.Preview():
        lookaheads.update(compute_local_first(firsts, prev))

    assert not lookaheads.contains_epsilon
    # Your code here!!! (Build and return child items)
    return [Item(x, 0, lookaheads) for x in next_symbol.productions]

def compress(items):
    centers = {}

    for item in items:
        center = item.Center()
        try:
            lookaheads = centers[center]
        except KeyError:
            centers[center] = lookaheads = set()
        lookaheads.update(item.lookaheads)

    return {Item(x.production, x.pos, set(lookahead)) for x, lookahead in centers.items()}


def closure_lr1(items, firsts):
    closure = ContainerSet(*items)

    changed = True
    while changed:
        changed = False

        new_items = ContainerSet()
        for item in closure:
            new_items.extend(expand(item, firsts))

        changed = closure.update(new_items)

    return compress(closure)


def goto_lr1(items, symbol, firsts=None, just_kernel=False):
    assert just_kernel or firsts is not None, '`firsts` must be provided if `just_kernel=False`'
    items = frozenset(item.NextItem() for item in items if item.NextSymbol == symbol)
    return items if just_kernel else closure_lr1(items, firsts)


def build_LR1_automaton(G):
    assert len(G.startSymbol.productions) == 1, 'Grammar must be augmented'

    firsts = compute_firsts(G)
    firsts[G.EOF] = ContainerSet(G.EOF)

    start_production = G.startSymbol.productions[0]
    start_item = Item(start_production, 0, lookaheads=(G.EOF,))
    start = frozenset([start_item])

    closure = closure_lr1(start, firsts)
    automaton = State(frozenset(closure), True)

    pending = [start]
    visited = {start: automaton}

    while pending:
        current = pending.pop()
        current_state = visited[current]

        for symbol in G.terminals + G.nonTerminals:
            # Your code here!!! (Get/Build `next_state`)
            next_state_key = goto_lr1(current_state.state, symbol, just_kernel=True)

            if not next_state_key:
                continue
            try:
                next_state = visited[next_state_key]
            except KeyError:
                next_state_items = goto_lr1(current_state.state, symbol, firsts)
                next_state = State(frozenset(next_state_items), True)
                pending.append(next_state_key)
                visited[next_state_key] = next_state

            current_state.add_transition(symbol.Name, next_state)

    automaton.set_formatter(multiline_formatter)
    return automaton


class LR1Parser(ShiftReduceParser):
    def _build_parsing_table(self):
        G = self.G.AugmentedGrammar(True)

        automaton = build_LR1_automaton(G)
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
                        self._register(self.action, (idx, G.EOF.Name), (self.OK, None))#tengo que ponerlo asi '$'
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

