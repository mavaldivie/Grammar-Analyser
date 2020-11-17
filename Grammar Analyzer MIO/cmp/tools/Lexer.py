from cmp.automata import State
from cmp.utils import Token
from cmp.tools.my_regex import regex_automaton


class Lexer:
    def __init__(self, table, eof):
        self.eof = eof
        self.regexs = self._build_regexs(table)
        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex) in enumerate(table):
            # Your code here!!!
            # - Remember to tag the final states with the token_type and priority.
            # - <State>.tag might be useful for that purpose ;-)

            # use with my_regex
            auto = regex_automaton(regex)
            auto, states = State.from_nfa(auto, True)
            # other
            # regex = Regex(regex)
            # auto, states = State.from_nfa(regex.automaton, True)

            for st in states:
                if st.final:
                    st.tag = (n, token_type)

            regexs.append(auto)
        return regexs

    def _build_automaton(self):
        start = State('start')

        # Your code here!!!
        for x in self.regexs:
            start.add_epsilon_transition(x)

        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ''

        for symbol in string:
            # Your code here!!!
            if state.has_transition(symbol):
                state = state[symbol][0]
                if state.final:
                    final = state
                    final_lex = lex
            else:
                final_lex = lex
                break
            lex += symbol
        else:
            final_lex = lex

        return final, final_lex

    def _tokenize(self, text):
        # Your code here!!!
        while text:
            stop, lex = self._walk(text)
            if stop and len(lex) > 0:
                st_min = min([st.tag for st in [final for final in stop.state if final.final]])
                yield lex, st_min[1]
            else:
                lex = '1'
                yield 'Unknown', 'Unknown'

            text = text[len(lex):]
        yield '\n', 'endl'
        yield '$', self.eof

    def __call__(self, text):
        return [Token(lex, ttype) for lex, ttype in self._tokenize(text)]