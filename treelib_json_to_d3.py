import json
import argparse


def main():
    """
    Convert a treelib json file from extract.py to a d3 hierarchy-style json file.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('input_filename',
                        type=str,
                        help='What is the input filename?')

    parser.add_argument('output_filename',
                        type=str,
                        help='What is the output filename?')

    args = vars(parser.parse_args())

    input_filename = args.get('input_filename')
    output_filename = args.get('output_filename')

    with open(input_filename, 'r') as input_file:
        data = json.load(input_file)

    breakpoint()
    


if __name__ == '__main__':

    main()
