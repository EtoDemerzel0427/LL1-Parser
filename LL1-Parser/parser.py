import re
from . import Grammar
# import Grammar


class Parser(object):
    def __init__(self, grammar_file, tokens_file, output_file="out.txt"):
        self.grammar_file = grammar_file
        self.tokens_file = tokens_file
        self.output_file = output_file
        self.G = None
        self.tokens = []

    def load_grammar(self):
        self.G = Grammar.Grammar()
        self.G.read_grammar(self.grammar_file)
        self.G.reduce_left_recursion()
        self.G.print_grammar()
        self.G.get_first_dict()
        self.G.get_follow_dict()
        self.G.generate_table()

    def load_tokens(self):
        self.tokens = []
        with open(self.tokens_file, 'r') as fin:
            for line in fin:
                line = line.strip().replace(" ", "")  # remove the white spaces
                token = re.split('([()*+])', line)
                token = list(filter(None, token))
                self.tokens.append(token)

    def parse(self):
        is_start = True
        for token in self.tokens:
            if is_start:
                is_start = False
                fout = open(self.output_file, 'w')
            else:
                fout = open(self.output_file, 'a')
            print('************************Process Begin************************')
            fout.write('************************Process Begin************************\n')
            self.parse_one_line(token, fout)
            print('************************Process End**************************')
            fout.write('************************Process End**************************\n')
            fout.close()

    def parse_one_line(self, token, fout):
        stack = ['$']
        stack.append(self.G.start)

        token.append('$')

        index = 0
        length = len(token)
        accepted_tokens = []

        while len(stack) > 0 and index < length:
            top = stack[-1]
            cur = token[index]
            print('----------------------------------------------------------')
            print('[Stack Top] ', top)
            print('[Current Token] ', cur)
            print('[Stack]', stack)
            print('[Accepted Tokens]', accepted_tokens)

            fout.write('----------------------------------------------------------\n')
            fout.write('[Stack Top] {}\n'.format(top))
            fout.write('[Current Token] {}\n'.format(cur))
            fout.write('[Stack] {}\n'.format(stack))
            fout.write('[Accepted Tokens] {}\n'.format(accepted_tokens))

            # non-terminal on top
            if top[0].isupper():
                key = top, cur

                # if the non-terminal is in the table
                if key in self.G.table:
                    stack.pop()

                    # correct case
                    if self.G.table[key] != 'synch':
                        # put into stack reversely
                        product = self.G.table[key][1]
                        print('[Using production] {} -> {}'.format(self.G.table[key][0],
                                                                   ' '.join(self.G.table[key][1])))
                        fout.write('[Using production] {} -> {}\n'.format(self.G.table[key][0],
                                                                          ' '.join(self.G.table[key][1])))
                        if product != ('#',):
                            for i in reversed(product):
                                stack.append(i)

                    else:
                        print('[Sync Error Here]')
                        fout.write('[Sync Error Here]\n')

                else:
                    index += 1
                    print('[Empty Error Here]   Skip:', cur)
                    fout.write('[Empty Error Here]    skip: {}\n'.format(cur))

            else:
                stack.pop()
                if top == cur:
                    index += 1
                    accepted_tokens.append(cur)
                    if cur == '$':
                        print('[ACCEPT]')
                        break

                    print('[Successful Match] pop symbol: {}'.format(top))
                    fout.write('[Successful Match] pop symbol: {}\n'.format(top))
                else:
                    print('[Incompatible Error Here]')
                    fout.write('[Incompatible Error Here]\n')



if __name__ == '__main__':
    parser = Parser('grammar2.txt', 'tokens.txt')
    parser.load_grammar()
    parser.load_tokens()
    print(parser.tokens)
#    print(parser.G.table['E','('])
    parser.parse()
