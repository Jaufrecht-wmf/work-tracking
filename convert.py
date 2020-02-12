import argparse
import pickle
import treelib
import sys


class RootedTree(treelib.Tree):
    """
    This is the starting point for all tree data representation.
    Use a dummy root node so that, if a child node is added that has a
    parent not in the tree, or no parent, it can still be added without
    breaking the DAGness of the tree.
    """

    ROOT_ID = -1

    def __init__(self):
        super(RootedTree, self).__init__()
        self.create_node('root', identifier=RootedTree.ROOT_ID)


def main():
    """
    Load a pickled Treelib file and output it in any of several forms: JSON,
    csv, text, or Graphviz dot.
    """
    ######################################################################
    # Initialize
    ######################################################################

    parser = argparse.ArgumentParser()

    parser.add_argument('input_file',
                        type=str,
                        nargs='+',
                        help="""Name of serialized treelib json file.""")

    parser.add_argument('--output_type',
                        choices=['text', 'json', 'csv', 'graphviz'],
                        default='json',
                        help="""Output format; pipe to file to
                        save. Text is an ascii-art representation of a
                        tree.  JSON is a complete data dump in
                        hierarchical JSON, including all node data.
                        csv is a flattened dump of all nodes, i.e.,
                        with parent node for each row.  Graphviz is the
                        dot file format.""")

    args = vars(parser.parse_args())
    input_file = args.get('input_file')[0]
    output_type = args.get('output_type', 'text')

    ######################################################################
    # Load data from file
    ######################################################################

    if not input_file:
        raise Exception(
            'Specify an input file.'
        )

    with open(input_file, 'r') as file:
        result_tree = pickle.load(open(input_file, 'rb'))

    breakpoint()
    if not result_tree:
        raise Exception(f'Could not load anything from {file}')

    if output_type == 'json':
        print(result_tree.to_json(with_data=True))
    elif output_type == 'csv':
        import csv
        nodes = result_tree.nodes
        writer = csv.writer(sys.stdout)
        writer.writerow(['id', 'name', 'node_type', 'parent_id', 'owner', 'start', 'end'])
        for key in nodes.keys():
            node = nodes[key]
            id = node.identifier
            name = node.tag
            if id != -1:
                parent_id = result_tree.parent(id).identifier
            else:
                parent_id = None
            node_type = None
            owner = None
            start = None
            end = None
            if node.data:
                node_type = node.data.get('node_type')
                owner = node.data.get('owner')
                start = node.data.get('start')
                end = node.data.get('end')
            row = [id, name, node_type, parent_id, owner, start, end]
            writer.writerow(row)
    elif output_type == 'graphviz':
        result_tree.to_graphviz(shape=u'box')
    else:
        result_tree.show()


if __name__ == '__main__':
    main()
