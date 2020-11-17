class ShiftReduceParser:
    SHIFT = 'SHIFT'
    REDUCE = 'REDUCE'
    OK = 'OK'

    def __init__(self, G, verbose=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}
        self._build_parsing_table()

    def _build_parsing_table(self):
        raise NotImplementedError()

    def __call__(self, w):
        stack = [0]
        cursor = 0
        output = []

        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose: print(stack, '<---||--->', w[cursor:])

            # Your code here!!! (Detect error)
            try:
                action, tag = self.action[state, lookahead]
            except:
                raise Exception('Aborting Parsing, Invalid Symbol. :-(')

            # Your code here!!! (Shift case)
            if action == self.SHIFT:
                stack.append(lookahead)
                stack.append(tag)
                cursor += 1
            # Your code here!!! (Reduce case)
            elif action == self.REDUCE:
                output.append(tag)
                for i in range(len(tag.Right)):
                    stack.pop()
                    assert stack[-1] == tag.Right[-i - 1].Name, 'Symbol does not match'
                    stack.pop()
                index = self.goto[stack[-1], tag.Left.Name]
                stack.append(tag.Left.Name)
                stack.append(index)
            # Your code here!!! (OK case)
            elif action == self.OK:
                return output
            # Your code here!!! (Invalid case)
            else:
                raise Exception('Aborting Parsing, Invalid Symbol. :-(')
                return None