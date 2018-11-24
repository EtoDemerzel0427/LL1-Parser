from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import pandas as pd
from . import parser


def add_args():
    """
    add command-line arguments
    :return: args
    """
    arg_parser = ArgumentParser("LL1-Parser",
                                formatter_class=ArgumentDefaultsHelpFormatter,
                                conflict_handler="resolve")

    arg_parser.add_argument("--grammar", dest="grammar", required=True,
                            help="The filename of the grammar")

    arg_parser.add_argument("--tokens", dest="tokens", required=True,
                            help="The token stream to analyze")

    arg_parser.add_argument("--output", dest="output", default="process.txt",
                            required=False, help="The output filename")

    args = arg_parser.parse_args()

    return args


def save_to_file(filename):
    print(filename)


if __name__ == "__main__":
    args = add_args()
    parser = parser.Parser(grammar_file=args.grammar, tokens_file=args.tokens, output_file=args.output)
    parser.load_grammar()

    # save the analyzing table first
    df = pd.DataFrame(parser.G.new_table).fillna('error')
    df.to_csv("out.csv", mode='w')

    # start analyzing
    parser.load_tokens()
    parser.parse()
