from cmp.tools.Lexer import Lexer
from cmp.pycompiler import Grammar, Production, Symbol, Sentence, SentenceList
from cmp.ast import AtomicNode, BinaryNode
from cmp.tools.evaluation import evaluate_parse
from cmp.Parser_LL1 import metodo_predictivo_no_recursivo


may = '|'.join(chr(n) for n in range(ord('A'),ord('Z')+1))
minu = '|'.join(chr(n) for n in range(ord('a'),ord('z')+1))
esp = '!|@|$|%|##|^|&|#*|#(|#)|_|+|-|=|{|}|[|]|<|>|,|.|/|?'

#hacer q los tokens terminen en endl
lexer = Lexer([
    ('epsilon', 'epsilon'),
    ('arrow', '-->'),
    ('space', '  *'),
    ('endl', '\n'),
    ('pipe', '#|'),
    ('may', f'({may})'),
    ('sym', f'({minu}|{esp})')
], '$') # $ para que coincida con la gramatica


class GrammarNode(BinaryNode):
    def evaluate(self):
        rvalue = self.right.evaluate()
        return self.operate(rvalue)

    def operate(self, rvalue):
        raise NotImplementedError()
class TerminalNode(AtomicNode):
    def __init__(self, grammar, lex):
        super().__init__(lex)
        self.grammar = grammar

    def evaluate(self):
        try:
            symbol = self.grammar.symbDict[self.lex]
        except KeyError:
            symbol = self.grammar.Terminal(self.lex)
        return symbol
class NonTerminalNode(AtomicNode):
    def __init__(self, grammar, lex):
        super().__init__(lex)
        self.grammar = grammar

    def evaluate(self):
        try:
            symbol = self.grammar.symbDict[self.lex]
        except KeyError:
            symbol = self.grammar.NonTerminal(self.lex)
        return symbol
class SentenceNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        if lvalue is None:
            return rvalue
        if rvalue is None:
            return Sentence(lvalue)
        return lvalue + rvalue
class SentenceListNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        if lvalue is None:
            return rvalue
        if rvalue is None:
            return SentenceList(lvalue)
        return lvalue | rvalue
class ProductionNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        if lvalue is None or rvalue is None:
            return None
        if isinstance(rvalue, Sentence):
            return [Production(lvalue, rvalue)]
        else:
            return [Production(lvalue, i) for i in rvalue]

class ProductionListNode(BinaryNode):
    @staticmethod
    def operate(lvalue, rvalue):
        if lvalue is None:
            return rvalue
        if rvalue is None:
            return lvalue
        return lvalue + rvalue
class ReturnNode(GrammarNode):
    def operate(self, rvalue):
        if self.left is None or rvalue is None:
            return None
        self.left.startSymbol = rvalue[0].Left
        for i in rvalue:
            self.left.Add_Production(i)
        return self.left
class EpsilonNode(AtomicNode):
    def evaluate(self):
        return self.lex.Epsilon


G = Grammar()

E = G.NonTerminal('E', True)
X, T, F, Y, P, Q = G.NonTerminals('X T F Y P Q')
may, sym, pipe, arrow, endl, epsilon = G.Terminals('may sym pipe arrow endl epsilon')

#Tengo q heredar la gramatica y poner el epsilon node
E %= T + X, lambda h, s: ReturnNode(h[0], ProductionListNode(s[1], s[2])), lambda h, s: h[0], lambda h, s: h[0]
X %= T + X, lambda h, s: ProductionListNode(s[1], s[2]), lambda h, s: h[0], lambda h, s: h[0]
X %= G.Epsilon, lambda h, s: None
T %= may + arrow + F + endl, lambda h, s: ProductionNode(NonTerminalNode(h[0], s[1]), s[3]), None, None, lambda h, s: h[0], None
F %= P + Y, lambda h, s: SentenceListNode(s[1], s[2]), lambda h, s: h[0], lambda h, s: h[0]
Y %= pipe + P + Y, lambda h, s: SentenceListNode(s[2], s[3]), None, lambda h, s: h[0], lambda h, s: h[0]
Y %= G.Epsilon, lambda h, s: None
P %= may + Q, lambda h, s: SentenceNode(NonTerminalNode(h[0], s[1]), s[2]), None, lambda h, s: h[0]
P %= sym + Q, lambda h, s: SentenceNode(TerminalNode(h[0], s[1]), s[2]), None, lambda h, s: h[0]
P %= epsilon, lambda h, s: EpsilonNode(h[0]), None
Q %= sym + Q, lambda h, s: SentenceNode(TerminalNode(h[0], s[1]), s[2]), None, lambda h, s: h[0]
Q %= may + Q, lambda h, s: SentenceNode(NonTerminalNode(h[0], s[1]), s[2]), None, lambda h, s: h[0]
Q %= G.Epsilon, lambda h, s: None

parser = metodo_predictivo_no_recursivo(G)

#Todas las mayusculas son no terminales
#El simbolo inicial es el simbolo cabecera de la primera produccion
#El simbolo distinguido de la gramatica se debe indicar mediante la palabra 'epsilon'
def String_to_Grammar(text):
    tokens = lexer(text)
    tokens = [i for i in tokens if i.token_type != 'space']

    left_parse = parser(tokens)
    ast = evaluate_parse(left_parse, tokens, Grammar())
    return ast.evaluate()
