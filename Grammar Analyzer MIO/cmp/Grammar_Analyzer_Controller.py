from cmp.Grammar_Formatter import String_to_Grammar
from cmp.tools.Firsts_and_Follows import compute_firsts, compute_follows
from cmp.Parser_LL1 import build_parsing_table, metodo_predictivo_no_recursivo, Is_LL1
from cmp.pycompiler import *
from cmp.Parser_SLR1 import SLR1Parser
from cmp.Parser_LR1 import LR1Parser
from cmp.Parser_LALR import LALRParser
from cmp.automata import State

class GAC(object):
    def __init__(self, grammar):
        self.gram = grammar
        self.Grammar= String_to_Grammar(grammar)
        self.firsts = None
        self.follows = None
        self.table_LL1 = None
    def Get_Firsts(self):
        self.firsts = compute_firsts(self.Grammar)
        return self.firsts
    def Get_Follows(self):
        if self.firsts is None:
            self.Get_Firsts()
        self.follows = compute_follows(self.Grammar, self.firsts)
        return self.follows
    def Table_LL1(self):
        G = self.Grammar.copy()
        if self.Has_Left_Recursion(G):
            GAC.remove_left_recursion(G)
        if self.Has_Common_Preffixes(G):
            GAC.factorize_grammar(G)

        f = compute_firsts(G)
        F = compute_follows(G, f)
        self.table_LL1 = build_parsing_table(G, f, F)
        if self.Is_LL1():
            return self.table_LL1
        return None
    def Is_LL1(self):
        if self.table_LL1 is None:
            self.Table_LL1()
        return Is_LL1(self.table_LL1)
    def Delete_Common_Prefixes(self):
        GAC.factorize_grammar(self.Grammar)
    def Delete_Left_Recursion(self):
        GAC.remove_left_recursion(self.Grammar)
    def Fixed_Grammar(self):
        G = self.Grammar.copy()
        GAC.factorize_grammar(G)
        GAC.remove_left_recursion(G)
        #eliminar producciones innecesarias
        return G
    def Derivation_Tree_LL1(self, w):
        G = self.Grammar.copy()
        if self.Has_Left_Recursion(G):
            GAC.remove_left_recursion(G)
        if self.Has_Common_Preffixes(G):
            GAC.factorize_grammar(G)

        f = compute_firsts(G)
        F = compute_follows(G, f)
        self.table_LL1 = build_parsing_table(G, f, F)
        parser = metodo_predictivo_no_recursivo(G, self.table_LL1, f, F)
        return GAC.Derivation_Tree(parser(w + '$'))
    def Derivation_Tree_SLR1(self, w):
        parser = SLR1Parser(self.Grammar)
        prod = parser(w + '$')
        rprod = [prod[- i - 1] for i in range(len(prod))]
        return GAC.Derivation_Tree(rprod)
    def Derivation_Tree_LR1(self, w):
        parser = LR1Parser(self.Grammar)
        prod = parser(w + '$')
        rprod = [prod[- i - 1] for i in range(len(prod))]
        return GAC.Derivation_Tree(rprod)
    def Derivation_Tree_LALR(self, w):
        parser = LALRParser(self.Grammar)
        prod = parser(w + '$')
        rprod = [prod[- i - 1] for i in range(len(prod))]
        return GAC.Derivation_Tree(rprod)
    def Convert_to_Automaton(self):
        return GAC.from_RegularGrammar_to_Automaton(self.Grammar)
    
    @staticmethod
    def Derivation_Tree(productions):
        if not productions or any(i for i in productions if not isinstance(i, Production)):
            return None
        root = State(productions[0].Left.Name)
        states = {}
        states[productions[0].Left.Name] = [root]

        for prod in productions:
            try:
                state = states[prod.Left.Name].pop()
            except KeyError:
                return None#aqui hubo un error
            if prod.Right.IsEpsilon:
                x = State(prod.Right.Name)
                state.add_transition('', x)
            for i in prod.Right:
                x = State(i.Name)
                state.add_transition('', x)
                if i.IsNonTerminal:
                    try:
                        states[i.Name].append(x)
                    except KeyError:
                        states[i.Name] = [x]
        return root


    @staticmethod
    def Has_Left_Recursion(G:Grammar):
        for prod in G.Productions:
            if prod.Right != G.Epsilon and prod.Right[0] == prod.Left:
                return True
        return False
    
    @staticmethod
    def Has_Common_Preffixes(G:Grammar):
        for nonTerminal in G.nonTerminals:
            visited = []
            for prod in nonTerminal.productions:
                if prod.Right != G.Epsilon and prod.Right[0] in visited:
                    return True
                elif prod.Right != G.Epsilon:
                    visited.append(prod.Right[0])
        return False
    
    @staticmethod
    def remove_left_recursion(G:Grammar):
        """
        Transform G for remove inmediate
        left recursion
        """
        G.Productions = []
        nonTerminals = G.nonTerminals.copy()

        for nonTerminal in nonTerminals:
            for p in nonTerminal.productions:
                if len(p.Right) > 0 and p.Right[0] == nonTerminal:
                    y = p.Right[1:]
                    pass
            recursion = [p.Right[1:] for p in nonTerminal.productions if len(p.Right) > 0 and p.Right[0] == nonTerminal]
            no_recursion = [p.Right for p in nonTerminal.productions if len(p.Right) == 0 or p.Right[0] != nonTerminal]

            if len(recursion) > 0:
                nonTerminal.productions = []
                aux = G.NonTerminal(f'{nonTerminal.Name}\'')

                for p in no_recursion:
                    nonTerminal %= Sentence(*p) + aux

                for p in recursion:
                    aux %= Sentence(*p) + aux

                aux %= G.Epsilon
            else:
                G.Productions.extend(nonTerminal.productions)

    @staticmethod
    def factorize_grammar(G:Grammar):
        """
        Transform G for remove common
        prefixes
        """
        G.Productions = []

        pending = [i for i in G.nonTerminals]

        while pending:
            nonTerminal = pending.pop()

            productions = nonTerminal.productions.copy()
            nonTerminal.productions = []

            visited = set()

            for i, p in enumerate(productions):
                if p not in visited:
                    n = len(p.Right)
                    same_prefix = []

                    for p2 in productions[i:]:
                        m = 0

                        for s1, s2 in zip(p.Right, p2.Right):
                            if s1 == s2:
                                m += 1
                            else:
                                break

                        if m > 0:
                            same_prefix.append(p2)
                            n = min(n, m)

                    if len(same_prefix) > 1:
                        visited.update(same_prefix)
                        aux = G.NonTerminal(f'{nonTerminal.Name}{i + 1}')

                        nonTerminal %= Sentence(*p.Right[:n]) + aux
                        for p2 in same_prefix:
                            if n == len(p2.Right):
                                aux %= G.Epsilon
                            else:
                                aux %= Sentence(*p2.Right[n:])

                        pending.append(aux)
                    else:
                        visited.add(p)
                        temp = Production(nonTerminal, p.Right)
                        if not temp in G.Productions:
                            nonTerminal %= p.Right

    @staticmethod
    def from_RegularGrammar_to_Automaton(G:Grammar):
        flag = True
        for prod in G.Productions:
            ok = (prod.Right == G.Epsilon)
            ok |= (len(prod.Right) == 1 and isinstance(prod.Right[0], Terminal))
            ok |= (len(prod.Right) == 2 and isinstance(prod.Right[0], Terminal) and isinstance(prod.Right[1], NonTerminal))
            flag &= ok

        if not flag:
            return None

        states = {}
        for i in G.nonTerminals:
            states[i] = State(i.Name)

        final = State('f', True)

        for prod in G.Productions:
            l = states[prod.Left]

            if prod.Right == G.Epsilon:
                l.add_epsilon_transition(final)
            elif len(prod.Right) == 1 and isinstance(prod.Right[0], Terminal):
                l.add_transition(prod.Right[0].Name, final)
            else:
                r = states[prod.Right[1]]
                l.add_transition(prod.Right[0].Name, r)

        return states[G.startSymbol]


    #automaton debe poseer un solo nodo final, distinto del inicial
    @staticmethod
    def from_automaton_to_regular_expression(automaton:State):
        index = {}
        n = 0
        for i, j in enumerate(automaton):
            index[j] = i
            n += 1

        transitions = [{} for _ in range(n)]
        backtransitions = [{} for _ in range(n)]

        for state in automaton:
            idx = index[state]
            for i, l in state.transitions.items():
                for j in l:
                    try:
                        transitions[idx][i].append(index[j])
                    except KeyError:
                        transitions[idx][i] = [index[j]]
                    try:
                        backtransitions[index[j]][i].append(idx)
                    except KeyError:
                        backtransitions[index[j]][i] = [idx]
            for i in state.epsilon_transitions:
                try:
                    transitions[idx]['ε'].append(index[i])
                except KeyError:
                    transitions[idx]['ε'] = [index[i]]
                try:
                    backtransitions[index[i]]['ε'].append(idx)
                except KeyError:
                    backtransitions[index[i]]['ε'] = [idx]

        start = index[automaton]
        final = None
        for i in automaton:
            if i.final:
                final = index[i]

        for i in range(n):
            if i not in (start, final):
                loop = ''
                trans = transitions[i].copy()
                for symbol, l in trans.items():
                    for state in l:
                        if state == i:
                            if len(loop) == 0:
                                loop = symbol
                            else:
                                loop += '|' + symbol
                            transitions[i][symbol].remove(state)
                            backtransitions[state][symbol].remove(i)
                if len(loop) > 0 and loop != 'ε':
                    loop = ('(' if len(loop) > 1 else '') + loop + (')' if len(loop) > 1 else '') + '*'

                btrans = backtransitions[i].copy()
                trans = transitions[i].copy()
                for symbolIn, l1 in btrans.items():
                    for state1 in l1:
                        if i == state1:
                            continue

                        try:
                            transitions[state1][symbolIn].remove(i)
                        except:
                            pass

                        for symbolOut, l2 in trans.items():
                            for state2 in l2:
                                if i == state2:
                                    continue

                                try:
                                    backtransitions[state2][symbolOut].remove(i)
                                except:
                                    pass

                                regex = (symbolIn if symbolIn != 'ε' else '') + (loop if loop != 'ε' else '') + (symbolOut if symbolOut != 'ε' else '')
                                if len(regex) == 0:
                                    regex = 'ε'
                                try:
                                    if not state2 in transitions[state1][regex]:
                                        transitions[state1][regex].append(state2)
                                except KeyError:
                                    transitions[state1][regex] = [state2]
                                try:
                                    if not state1 in backtransitions[state2][regex]:
                                        backtransitions[state2][regex].append(state1)
                                except KeyError:
                                    backtransitions[state2][regex] = [state1]

        a, b, c, d = '', '', '', ''
        for i, l in transitions[start].items():
            for j in l:
                if j == start:
                    if len(a) == 0:
                        a = i
                    else:
                        a += '|' + i
                else:
                    if len(b) == 0:
                        b = i
                    else:
                        b += '|' + i
        for i, l in transitions[final].items():
            for j in l:
                if j == final:
                    if len(d) == 0:
                        d = i
                    else:
                        d += '|' + i
                else:
                    if len(c) == 0:
                        c = i
                    else:
                        c += '|' + i

        if len(b) == 0:
            return ''
        left, right = a, None

        if len(c) > 0:
            left += ('|' if len(a) > 0 else '') + b + d + ('*' if len(d) > 0 else '') + c
        if len(left) > 0:
            left = ('(' if len(left) > 1 else '') + left + (')' if len(left) > 1 else '') + '*'
        right = b + d + ('*' if len(d) > 0 else '')
        return left + '(' + right + ')'

