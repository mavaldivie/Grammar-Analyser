def evaluate_parse(left_parse, tokens, inherited_value = None):
    if not left_parse or not tokens:
        return

    left_parse = iter(left_parse)
    tokens = iter(tokens)
    result = evaluate(next(left_parse), left_parse, tokens, inherited_value)

    return result


def evaluate(production, left_parse, tokens, inherited_value=None):
    head, body = production
    attributes = production.attributes

    # Insert your code here ...
    synteticed = [None for _ in attributes]
    inherited = [None for _ in attributes]
    # > synteticed = ...
    # > inherited = ...
    # Anything to do with inherited_value?
    inherited[0] = inherited_value

    for i, symbol in enumerate(body, 1):
        if symbol.IsTerminal:
            assert inherited[i] is None
            # Insert your code here ...
            synteticed[i] = next(tokens).lex
        else:
            next_production = next(left_parse)
            assert symbol == next_production.Left
            # Insert your code here ...
            if attributes[i] is not None:
                inherited[i] = attributes[i](inherited, synteticed)
            synteticed[i] = evaluate(next_production, left_parse, tokens, inherited[i])

    # Insert your code here ...
    synteticed[0] = attributes[0](inherited, synteticed)
    # > return ...
    return synteticed[0]

