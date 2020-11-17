from cmp.tools.automata import NFA, DFA, nfa_to_dfa
from cmp.tools.automata import automata_union, automata_concatenation, automata_closure, automata_minimization
from cmp.Parser_LL1 import metodo_predictivo_no_recursivo
from cmp.pycompiler import Grammar
from cmp.utils import Token
from cmp.tools.evaluation import evaluate_parse
from cmp.ast import Node, AtomicNode, UnaryNode, BinaryNode


EPSILON = 'ε'


class EpsilonNode(AtomicNode):
    def evaluate(self):
        # Your code here!!!
        return NFA(1,{0},{}, 0)


class SymbolNode(AtomicNode):
    def evaluate(self):
        s = self.lex
        return NFA(2, [1], {(0, s):[1]}, 0)


class ClosureNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_closure(value)


class UnionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_union(lvalue, rvalue)


class ConcatNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        # Your code here!!!
        return automata_concatenation(lvalue, rvalue)


class PlusNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_concatenation(value,automata_closure(value)) 


class QuestionNode(UnaryNode):
    @staticmethod
    def operate(value):
        # Your code here!!!
        return automata_union(value,NFA(1,{0},{}, 0))  #aqui deberia ir 


G = Grammar()

E = G.NonTerminal('E', True)
T, F, A, X, Y, Z= G.NonTerminals('T F A X Y Z')
pipe, star, opar, cpar, symbol, epsilon = G.Terminals('| * ( ) symbol ε')

#E --> T + X
#X --> | + T + X $ epsilon
#T --> A + Y
#Y --> A + Y $ epsilon
#A --> Z + F
#F --> * $ epsilon
#Z --> opar + E + opar $ symbol $ ε

E %= T + X, lambda h, s: s[2], None, lambda h, s: s[1]

X %= pipe + T + X, lambda h, s: s[3], None, None, lambda h, s: UnionNode(h[0], s[2])
X %= G.Epsilon, lambda h, s: h[0]

T %= A + Y, lambda h, s: s[2], None, lambda h, s: s[1]

Y %= A + Y, lambda h, s: s[2], None, lambda h, s: ConcatNode(h[0], s[1])
Y %= G.Epsilon, lambda h, s: h[0]

A %= Z + F, lambda h, s: s[2], None, lambda h, s: s[1]

F %= star + F, lambda h, s: s[2], None, lambda h, s: ClosureNode(h[0])
F %= G.Epsilon, lambda h, s: h[0]

Z %= opar + E + cpar, lambda h, s: s[2], None, None, None
Z %= symbol, lambda h, s: SymbolNode(s[1]), None
Z %= epsilon, lambda h, s: EpsilonNode(s[1]), None


def regex_tokenizer(text, G, skip_whitespaces=True, special_symbol = None):
    tokens = []
    # > fixed_tokens = ???
    fixed_tokens = {
        '|' : Token('|', pipe),
        '*' : Token('*', star),
        '(' : Token('(', opar),
        ')' : Token(')', cpar),
        EPSILON : Token(EPSILON, epsilon)
    }
    # Your code here!!!
    
    special = False
    for char in text:
        if skip_whitespaces and char.isspace():
            continue
        # Your code here!!!
        if special:
            special = False
            tokens.append(Token(char, symbol))
            continue
        if special_symbol and special_symbol == char:
            special = True
            continue
        try:
            tokens.append(fixed_tokens[char])
        except KeyError:
            tokens.append(Token(char, symbol))
            
    tokens.append(Token('$', G.EOF))
    return tokens

def regex_automaton(regex):
    tokens = regex_tokenizer(regex, G,False, '#')
    #print(tokens)
    parser = metodo_predictivo_no_recursivo(G)
    left_parse = parser(tokens)
    ast = evaluate_parse(left_parse, tokens)
    nfa = ast.evaluate() 
    dfa = nfa_to_dfa(nfa)
    mini = automata_minimization(dfa)
    return mini
