import json
import argparse


def treelib_to_d3(node):
    """
    Given a dict representing the json dump of a treelib node,
    return a dict of the same node its descendents, formatted
    for d3 consumption, with no data loss.

    treelib.json output:
    {"root":
      {"children":[{"Activity: Build/improve models in response to community demand":
                     {"data": {"node_type": "Activities"}}},
                   {"Priority: Brand Awareness":
                     {"children": [{"Outcome: B-O2: Clarify and strengthen brand arch":
                                     {"children": [{"KD: B-O2-D1: Brand",
                                                   {"data":{"node_type": "Projects"}}}]}}]}}]}}

    d3 hierarchical json (e.g. 'flare.json')

    {"name": "root",
     "children": [{"name": "Activity: Build/improve models in response to community demand",
                   "data": {"node_type": "Activities"},}
                  {"name": "Priority: Brand Awareness",
                   "children": [{"name": "Outcome: B-O2: Clarify and strengthen brand arch",
                                 "children": [{"name": "KD: B-O2-D1: Brand",
                                               "data": {"node_type": "Projects"}}]}]}]}
    """

    # assume there is only one key/value pair in treelib node, and that
    # the key is the node name, and the value is a dict of its contents
    name = next(iter(node))
    new_dict = {'name': name}
    node_value = node[name]

    # assume that the value of the only key of the treelib node as a dict.
    # if it has a 'data' key, move it and its value up to the node-level dict
    data = node_value.get('data')
    if data:
        new_dict['data'] = data

    # if there is a children key, assume its value is a list of nodes,
    # recurse through them, rebuild them as a list, and move the 'children'/list
    # key/value pair up to the node-level dict
    children = node_value.get('children')
    if children:
        child_list = []
        for child in children:
            child_node = treelib_to_d3(child)
            child_list.append(child_node)
        new_dict['children'] = child_list

    return new_dict


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
        output_dict = treelib_to_d3(data)
    file = open(output_filename, 'w')
    file.write(json.dumps(output_dict))


if __name__ == '__main__':

    main()