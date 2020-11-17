from cmp.tools.Firsts_and_Follows import compute_firsts, compute_follows


def build_parsing_table(G, firsts, follows):
    # init parsing table
    M = {}

    # P: X -> alpha
    for production in G.Productions:
        X = production.Left
        alpha = production.Right

        # working with symbols on First(alpha) ...
        for symbol in firsts[alpha]:
            try:
                M[X.Name, symbol.Name].append(production)
            except KeyError:
                M[X.Name, symbol.Name] = [production]

        # working with epsilon...
        if firsts[alpha].contains_epsilon:
            for symbol in follows[X]:
                try:
                    M[X.Name, symbol.Name].append(production)
                except KeyError:
                    M[X.Name, symbol.Name] = [production]

    # parsing table is ready!!!
    return M


def metodo_predictivo_no_recursivo(G, M=None, firsts=None, follows=None):
    # checking table...
    if M is None:
        if firsts is None:
            firsts = compute_firsts(G)
        if follows is None:
            follows = compute_follows(G, firsts)
        M = build_parsing_table(G, firsts, follows)

    # parser construction...
    def parser(w):

        # w ends with $ (G.EOF)
        # init:
        stack = [G.startSymbol]
        cursor = 0
        output = []
        ### stack =  ????
        ### cursor = ????
        ### output = ????

        # parsing w...
        while len(stack) > 0 and cursor < len(w):
            top = stack.pop()
            a = w[cursor]
            x = str(a)
            #             print((top, a))
            if top.IsTerminal and x == top.Name:
                cursor += 1
            elif top.IsNonTerminal:#poner un try aqui para coger los errores
                productions = M[top.Name, x]
                output.append(productions[0])
                for prod in productions:
                    for symbol in reversed(prod.Right):
                        stack.append(symbol)
            else:
                return False

        if str(w[cursor]) != '$':
            return False
        # left parse is ready!!!
        return output

    # parser is ready!!!
    return parser


def Is_LL1(M):
    return not any(i for i in M if len(M[i]) > 1)