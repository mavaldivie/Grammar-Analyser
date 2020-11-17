from cmp.utils import ContainerSet
from cmp.utils import DisjointSet


class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard('')

    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()

    def _repr_svg_(self):
        try:
            return self.graph().create_svg().decode('utf8')
        except:
            pass


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def _move(self, symbol):
        # Your code here
        try:
            self.current = self.transitions[self.current][symbol][0]
        except KeyError:
            raise KeyError("Transition does not exists")

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        # Your code here
        try:
            for symbol in string:
                self._move(symbol)
            flag = self.current in self.finals
        except KeyError:
            flag = False
        self._reset()
        return flag


def move(automaton, states, symbol):
    moves = set()
    for state in states:
        # Your code here
        if symbol in automaton.transitions[state]:
            moves.update(automaton.transitions[state][symbol])
    return moves


def epsilon_closure(automaton, states):
    pending = [s for s in states]  # equivalente a list(states) pero me gusta así :p
    closure = {s for s in states}  # equivalente a  set(states) pero me gusta así :p

    while pending:
        state = pending.pop()
        # Your code here
        for symbol in automaton.epsilon_transitions(state):
            if not symbol in closure:
                closure.add(symbol)
                pending.append(symbol)

    return ContainerSet(*closure)


def nfa_to_dfa(automaton):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    count = 1;

    pending = [start]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:
            nx = epsilon_closure(automaton, move(automaton, state, symbol))
            if not nx:
                continue

            if nx not in states:
                nx.id = count
                count += 1

                nx.is_final = any(s in automaton.finals for s in nx)
                states.append(nx)
                pending.append(nx)
            else:
                nx = states[states.index(nx)]

            try:
                transitions[state.id, symbol]
                assert False, 'Invalid DFA!!!'
            except KeyError:
                transitions[state.id, symbol] = nx.id

    finals = [state.id for state in states if state.is_final]
    dfa = DFA(len(states), finals, transitions)
    return dfa


def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[origin + d2, symbol] = [state + d2 for state in destinations]

    ## Add transitions from start state ...
    # Your code here
    transitions[start, ''] = [a1.start + d1, a2.start + d2]

    ## Add transitions to final state ...
    # Your code here
    for state in a1.finals:
        transitions[state + d1, ''] = [final]
    for state in a2.finals:
        transitions[state + d2, ''] = [final]

    states = a1.states + a2.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}

    start = a1.start  # esto lo cambie yo
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate a1 transitions ...
        # Your code here
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    for (origin, symbol), destinations in a2.map.items():
        ## Relocate a2 transitions ...
        # Your code here
        transitions[origin + d2, symbol] = [state + d2 for state in destinations]

    ## Add transitions to final state ...
    # Your code here
    for state in a1.finals:
        try:  # esto lo cambie yo
            transitions[state + d1, ''].append(a2.start + d2)
        except KeyError:
            transitions[state + d1, ''] = [a2.start + d2]
    for state in a2.finals:
        try:  # esto lo cambie yo
            transitions[state + d2, ''].append(final)
        except KeyError:
            transitions[state + d2, ''] = [final]

    states = a1.states + a2.states + 1
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}

    start = 0
    d1 = 1
    final = a1.states + d1

    for (origin, symbol), destinations in a1.map.items():
        ## Relocate automaton transitions ...
        # Your code here
        transitions[origin + d1, symbol] = [state + d1 for state in destinations]

    ## Add transitions from start state ...
    # Your code here
    transitions[start, ''] = [a1.start + d1, final]  # no creo q este final vaya aqui

    ## Add transitions to final state and to start state ...
    # Your code here
    for state in a1.finals:
        try:  # lo annadi yo
            transitions[state + d1, ''].append(final)
        except KeyError:
            transitions[state + d1, ''] = [final]

    transitions[final, ''] = [start]

    states = a1.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


def distinguish_states(group, automaton, partition):
    split = {}
    vocabulary = tuple(automaton.vocabulary)

    for member in group:
        # Your code here
        for state in split.keys():
            for symbol in vocabulary:
                try:
                    m_pos = automaton.transitions[member.value][symbol][0]
                    m_pos = partition[m_pos].representative

                except KeyError:
                    m_pos = -1

                try:
                    s_pos = automaton.transitions[state][symbol][0]
                    s_pos = partition[s_pos].representative
                except KeyError:
                    s_pos = -1

                if not m_pos == s_pos:
                    break
            else:
                split[state].append(member.value)
                break;
        else:
            split[member.value] = [member.value]

    return [group for group in split.values()]


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    ## partition = { NON-FINALS | FINALS }
    # Your code here
    partition.merge(automaton.finals)
    non_finals = [state for state in range(automaton.states) if not state in automaton.finals]
    partition.merge(non_finals)

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        ## Split each group if needed (use distinguish_states(group, automaton, partition))
        # Your code here
        for group in partition.groups:
            new_groups = distinguish_states(group, automaton, partition)
            # print(group, new_groups)
            for g in new_groups:
                new_partition.merge(g)

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        ## origin = ???
        origin = state.value
        # Your code here
        for symbol, destinations in automaton.transitions[origin].items():
            # Your code here
            new_destination = states.index(partition[destinations[0]].representative)

            try:
                transitions[i, symbol]
                assert False
            except KeyError:
                # Your code here
                transitions[i, symbol] = new_destination  # el dfa es sin []
                pass

    ## finals = ???          #cambie esto un poco
    finals = {states.index(partition[i].representative) for i in automaton.finals}
    ## start  = ???
    start = states.index(partition[automaton.start].representative)
    # Your code here

    return DFA(len(states), finals, transitions, start)

