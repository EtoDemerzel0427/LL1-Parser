import copy
import pandas as pd


class Grammar(object):
    """
    The class for a context-free grammar. Including the operations of get first/follow sets,
    remove left recursions, extract left common factors.
    """
    def __init__(self):
        self.start = ''
        self.productions = dict()
        self.first_dict = dict()
        self.follow_dict = dict()
        self.table = {}
        self.new_table = {}

    def read_grammar(self, filename):
        """
        get the grammar from the file, store the grammar into a dict.
        dict format:
        {('Non',):{('sth1', 'sth2', 'sth3'), ('sth4','sth5')} refers to: Non -> sth1 sth2 sth3 | sth4 sth5
        :param filename: the filename to read
        :return:
        """
        with open(filename, 'r') as fin:
            is_start = True
            for line in fin:
                tokens = line.strip().split()
                left = (tokens[0],)
                right = tokens[2:]

                if is_start:
                    self.start = left[0]
                    is_start = False

                right_set = set()
                product = tuple()
                for token in right:
                    if token != '|':
                        product += (token,)
                    else:
                        right_set.add(product)
                        product = tuple()
                right_set.add(product)
                self.productions[left] = right_set

    def print_grammar(self, filename = 'grammar_no_recur.txt'):
        """
        output the productions to text file from grammar.productions.
        e.g: for grammar.productions = {('E',):('a','b'),('c',)}
        the file should be E -> a b | c
        :return:
        """
        with open(filename, 'w') as fin:
            for key, values in self.productions.items():
                left = ' '.join(key)
                fin.write(left + ' -> ')
                length = len(values)

                num = 1
                for value in values:
                    right = ' '.join(value)
                    fin.write(right)

                    if num < length:
                        fin.write(' | ')
                    else:
                        fin.write('\n')

                    num += 1


        pass

    def reduce_left_recursion(self):
        new_productions = dict()
        recur = False
        for key, values in self.productions.items():
            new_productions[key] = self.productions[key]
            left = key[0]
            for value in values:
                if value[0] == left:
                    recur = True
                    original_set, new_set = self.transform(key)
                    new_productions[key] = original_set
                    new_productions[(key[0] + "'",)] = new_set
                    break
        if recur:
            self.productions = new_productions

    def transform(self, key):
        """
        method:
        key -> key alpha | beta ===> key -> beta new_symbol; new_symbol -> alpha new_symbol | #
        :param key: the symbol that causes left recursion
        :return:
        """
        new_symbol = key[0] + "'"
        new_key = (new_symbol,)
        new_set = {('#',)}
        original_set = set()

        for value in self.productions[key]:
            if value[0] == key[0]:
                new_set.add(value[1:] + new_key)
            else:
                original_set.add(value + new_key)

        return original_set, new_set

    def get_first(self, tokens):
        """
        get the first set for a token string.
        :param tokens: a tuple, each element a symbol
        :return:
        """
        if not isinstance(tokens, tuple):
            raise Exception("Wrong type argument. tuple expected!")

        token = tokens[0]  # the first symbol
        first = set()
        # if non-terminals
        if token[0].isupper():
            for entity in self.productions[(token,)]:
                if entity == ('#',):  # entity is tuple too
                    if len(tokens) == 1:  # a single non-terminal
                        first.add('#')
                    else:
                        first = first.union(self.get_first(tokens[1:]))
                else:
                    first = first.union(self.get_first(entity))
        else:
            first.add(token)

        return first

    def get_first_dict(self):
        """
        get the first sets for all non-terminals.
        the key is a string indicating the non-terminal,
        and the value is a string set of its first set members.
        :return: None
        """
        for left in self.productions:
            self.first_dict[left[0]] = self.get_first(left)

    def get_follow_dict(self):
        for key in self.productions:
            self.follow_dict[key[0]] = set()

        self.follow_dict[self.start] = {'$'}

        while True:
            pre_dict = copy.deepcopy(self.follow_dict)
            for key, values in self.productions.items():
                left = key[0]
                for value in values:  # value is a tuple
                    length = len(value)
                    for i in range(length):
                        if value[i][0].isupper():  # value[i] is a symbol, in string format
                            if i == length - 1:
                                self.follow_dict[value[i]] = self.follow_dict[value[i]].union(self.follow_dict[left])
                            else:
                                next_follow = self.get_first(value[i+1:])
                                self.follow_dict[value[i]] = self.follow_dict[value[i]].union(next_follow)
                                if '#' in next_follow:
                                    self.follow_dict[value[i]] -= {'#'}
                                    self.follow_dict[value[i]] = \
                                        self.follow_dict[value[i]].union(self.follow_dict[left])
            if self.follow_dict == pre_dict:
                break

    def generate_table(self):
        self.table = {}
        for key, values in self.productions.items():
            for value in values:
                first = self.get_first(value)
                for entity in first:
                    if entity != '#':
                        self.table[key[0], entity] = key[0], value
                    if '#' in first:
                        for ent in self.follow_dict[key[0]]:
                            self.table[key[0], ent] = key[0], value

        for key, values in self.follow_dict.items():
            for value in values:
                if (key, value) not in self.table:
                    self.table[key, value] = 'synch'

        # to display in matrix form
        self.new_table = {}
        for pair in self.table:
            self.new_table[pair[1]] = {}

        for pair in self.table:
            if self.table[pair] == 'synch':
                self.new_table[pair[1]][pair[0]] = self.table[pair]
            else:
                self.new_table[pair[1]][pair[0]] = '{}->{}'.format(self.table[pair][0], ' '.join(self.table[pair][1]))

        # print('----------------------------The analyzing table ------------------------------')
        # print(pd.DataFrame(self.new_table).fillna('error'))


if __name__ == '__main__':
    # test
    g = Grammar()
    g.read_grammar('grammar2.txt')
    # print(g.productions)
    g.reduce_left_recursion()
    print(g.productions)
    g.get_first_dict()
    g.get_follow_dict()
    g.generate_table()
    print(g.start)
